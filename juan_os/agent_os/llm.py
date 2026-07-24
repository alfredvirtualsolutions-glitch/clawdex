"""Pluggable LLM / model-runtime layer — the swappable brain behind the agents.

The architecture's "Model Runtime" (Ollama in the diagram) is intentionally not
hard-wired to one provider. Set ``LLM_BACKEND`` to pick which LLM the reasoning
agents (Scribe, Pulse, Compass) call — swap it with one env var, no code change:

    LLM_BACKEND=ollama      # local-first, default (http://localhost:11434)
    LLM_BACKEND=openai      # any OpenAI-compatible API (OpenAI, Groq, Together,
                            # OpenRouter, LM Studio, vLLM) via OPENAI_BASE_URL
    LLM_BACKEND=anthropic   # Claude via the official Anthropic SDK

Keys/URLs come from the environment (.env). When the selected backend isn't
configured, ``available()`` is False and callers fall back to local heuristics.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # noqa: BLE001
    pass

try:
    import httpx
except Exception:  # noqa: BLE001
    httpx = None  # type: ignore

DEFAULT_BACKEND = "ollama"
TIMEOUT = 60.0


class LLMError(RuntimeError):
    pass


class LLMUnavailable(LLMError):
    """Raised when the selected backend isn't configured/reachable."""


def backend() -> str:
    return (os.environ.get("LLM_BACKEND") or DEFAULT_BACKEND).strip().lower()


def model_name() -> str:
    b = backend()
    if b == "ollama":
        return os.environ.get("OLLAMA_MODEL", "llama3.1")
    if b == "openai":
        return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    if b == "anthropic":
        # Default to the latest, most capable Claude model; override via env.
        return os.environ.get("ANTHROPIC_MODEL", "claude-opus-5")
    return "unknown"


def available() -> bool:
    b = backend()
    if b == "ollama":
        return bool(os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"))
    if b == "openai":
        return bool(os.environ.get("OPENAI_API_KEY", "").strip())
    if b == "anthropic":
        return bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())
    return False


def status() -> dict[str, Any]:
    return {"backend": backend(), "model": model_name(), "configured": available()}


# --------------------------------------------------------------------------- #
# Unified chat entrypoint
# --------------------------------------------------------------------------- #
def chat(prompt: str, *, system: str | None = None, max_tokens: int = 800,
         temperature: float | None = None) -> str:
    """Send one turn to the configured backend and return the text reply."""
    b = backend()
    if b == "ollama":
        return _ollama(prompt, system, max_tokens, temperature)
    if b == "openai":
        return _openai(prompt, system, max_tokens, temperature)
    if b == "anthropic":
        return _anthropic(prompt, system, max_tokens)
    raise LLMUnavailable(f"Unknown LLM_BACKEND '{b}'. Use ollama | openai | anthropic.")


# --------------------------------------------------------------------------- #
# Ollama (local) — POST /api/chat
# --------------------------------------------------------------------------- #
def _ollama(prompt: str, system: str | None, max_tokens: int, temperature: float | None) -> str:
    if httpx is None:
        raise LLMError("httpx not installed.")
    base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
    options: dict[str, Any] = {"num_predict": max_tokens}
    if temperature is not None:
        options["temperature"] = temperature
    try:
        with httpx.Client(timeout=TIMEOUT) as c:
            r = c.post(f"{base}/api/chat",
                       json={"model": model_name(), "messages": messages,
                             "stream": False, "options": options})
            r.raise_for_status()
            return (r.json().get("message") or {}).get("content", "").strip()
    except httpx.HTTPError as exc:
        raise LLMUnavailable(f"Ollama not reachable at {base}: {exc}") from exc


# --------------------------------------------------------------------------- #
# OpenAI-compatible — POST {base}/chat/completions
# --------------------------------------------------------------------------- #
def _openai(prompt: str, system: str | None, max_tokens: int, temperature: float | None) -> str:
    if httpx is None:
        raise LLMError("httpx not installed.")
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise LLMUnavailable("OPENAI_API_KEY not set.")
    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": prompt}]
    body: dict[str, Any] = {"model": model_name(), "messages": messages, "max_tokens": max_tokens}
    if temperature is not None:
        body["temperature"] = temperature
    try:
        with httpx.Client(timeout=TIMEOUT) as c:
            r = c.post(f"{base}/chat/completions",
                       headers={"Authorization": f"Bearer {key}"}, json=body)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"].strip()
    except httpx.HTTPError as exc:
        raise LLMError(f"OpenAI-compatible request failed: {exc}") from exc


# --------------------------------------------------------------------------- #
# Anthropic (Claude) — official SDK
# --------------------------------------------------------------------------- #
def _anthropic(prompt: str, system: str | None, max_tokens: int) -> str:
    if not os.environ.get("ANTHROPIC_API_KEY", "").strip():
        raise LLMUnavailable("ANTHROPIC_API_KEY not set.")
    try:
        import anthropic
    except Exception as exc:  # noqa: BLE001
        raise LLMError("anthropic SDK not installed (pip install anthropic).") from exc
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model_name(),
        max_tokens=max_tokens,
        system=system or anthropic.NOT_GIVEN,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()


# --------------------------------------------------------------------------- #
# Agent helpers — LLM-backed when available, deterministic fallback otherwise
# --------------------------------------------------------------------------- #
SCRIBE_SYSTEM = (
    "You are Scribe, a compliant outreach writer for a retirement advisor. Write a short, "
    "natural, educational email referencing ONLY the provided verified public signal. Offer "
    "clarity, not pressure. Never invent age, income, assets, net worth, retirement date, or "
    "financial hardship. Urgency may come only from the stated event/deadline. End with a soft "
    "'Clarity Review' call to action and a reply-INFO option. Keep it under 120 words."
)


def scribe_draft(signal_title: str, signal_summary: str, advisor_name: str) -> dict[str, Any]:
    prompt = (f"Verified signal: {signal_title}\nDetail: {signal_summary}\n"
              f"Advisor: {advisor_name}\n\nWrite the subject line and body.")
    if available():
        try:
            text = chat(prompt, system=SCRIBE_SYSTEM, max_tokens=400)
            return {"generated": True, "backend": backend(), "model": model_name(), "message": text}
        except LLMError as exc:
            return {"generated": False, "error": str(exc), "message": _scribe_fallback(signal_title, advisor_name)}
    return {"generated": False, "backend": backend(), "message": _scribe_fallback(signal_title, advisor_name)}


def _scribe_fallback(signal_title: str, advisor_name: str) -> str:
    return (f"Subject: A quick note about {signal_title}\n\n"
            f"Hi — I noticed the recent public update regarding \"{signal_title}\". It can be a "
            f"useful moment to review your options with no pressure. If a short Clarity Review "
            f"would help, reply and I'll share times. Reply INFO for a one-pager.\n\n— {advisor_name}")


PULSE_CLASSES = ["positive_interest", "request_information", "meeting_request", "question",
                 "not_now", "not_interested", "already_has_advisor", "wrong_person",
                 "unsubscribe", "complaint", "out_of_office"]


def pulse_classify(reply_text: str) -> dict[str, Any]:
    if available():
        prompt = (f"Classify this email reply into exactly one label from {PULSE_CLASSES}. "
                  f"Return only the label.\n\nReply:\n{reply_text}")
        try:
            raw = chat(prompt, system="You are Pulse, a precise reply classifier.", max_tokens=20).lower()
            label = next((c for c in PULSE_CLASSES if c in raw), "question")
            return {"generated": True, "backend": backend(), "label": label}
        except LLMError as exc:
            return {"generated": False, "error": str(exc), "label": _pulse_fallback(reply_text)}
    return {"generated": False, "backend": backend(), "label": _pulse_fallback(reply_text)}


def _pulse_fallback(reply_text: str) -> str:
    t = reply_text.lower()
    if any(w in t for w in ("unsubscribe", "remove me", "stop")):
        return "unsubscribe"
    if any(w in t for w in ("meeting", "call", "schedule", "calendar", "book")):
        return "meeting_request"
    if any(w in t for w in ("info", "more information", "learn more", "send")):
        return "request_information"
    if any(w in t for w in ("not interested", "no thanks", "no thank")):
        return "not_interested"
    if "out of office" in t or "ooo" in t:
        return "out_of_office"
    return "question"
