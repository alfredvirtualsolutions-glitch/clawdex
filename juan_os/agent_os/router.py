"""Task Router + Validation gate — the spine of Juan Cabezas OS.

One architectural rule replaces the overlapping reasoning agents:

    Pokee discovers / reasons.   Gemini processes.   Code decides.
    Human advisor approves.      Neon remembers.

    TASK ROUTER
         │  complexity?
    ┌────┴────┐
    ▼         ▼
 COMPLEX    SIMPLE
 Pokee      Gemini            (each falls back to the other, then to
    └────┬────┘                deterministic code, so the OS always answers)
         ▼
     VALIDATION                 ← Code decides: the 9-check compliance gate.
         │  Pokee/Gemini only *suggest*; only these checks let a record pass.
    ┌────┴─────────┐
    ▼              ▼
  approved   human approval     ← Human advisor approves anything the gate flags.
    ▼
   NEON                         ← Neon remembers.

The models never decide compliance. They produce an *inference* ("Evidence
suggests pension-decision intent"); `validate()` — plain deterministic Python —
is the only thing that can clear a record for the database or route it to a
human. Keys/models come from the environment; when neither model is configured
the router still returns a deterministic result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from . import llm

# --------------------------------------------------------------------------- #
# Tiers
# --------------------------------------------------------------------------- #
COMPLEX = "complex"   # reasoning, research, analysis, personalization → Pokee
SIMPLE = "simple"     # classification, extraction, short summaries    → Gemini

RESEARCH_SYSTEM = (
    "You are the research intelligence layer for Juan OS. Analyze the verified public "
    "retirement signal you are given and state, in one or two sentences, what decision "
    "intent the PUBLIC evidence supports (e.g. pension-election window, plan rollover, "
    "retirement-date filing). Cite only the provided facts. Never infer age, income, "
    "assets, net worth, or hardship. If the evidence is thin, say so."
)


@dataclass
class Inference:
    """What a model *suggests* — never a compliance decision."""
    text: str
    tier: str                       # "pokee" | "gemini" | "deterministic"
    task_kind: str                  # COMPLEX | SIMPLE
    tried: list[str] = field(default_factory=list)
    generated: bool = False         # True if a live model produced it


# --------------------------------------------------------------------------- #
# TASK ROUTER — complexity-based, with graceful fallback
# --------------------------------------------------------------------------- #
def route(prompt: str, *, system: str | None = None, task: str = COMPLEX,
          max_tokens: int = 400, deterministic: str | None = None) -> Inference:
    """Route by complexity: COMPLEX→Pokee first, SIMPLE→Gemini first.

    Falls through to the other model, then to a deterministic string, so a
    caller always gets an ``Inference``.
    """
    order = (["pokee", "gemini"] if task == COMPLEX else ["gemini", "pokee"])
    tried: list[str] = []
    for tier in order:
        try:
            if tier == "pokee" and llm.pokee_available():
                tried.append("pokee")
                text = llm.pokee_chat(prompt, system=system, max_tokens=max_tokens)
                if text:
                    return Inference(text, "pokee", task, tried, generated=True)
            elif tier == "gemini" and llm.gemini_available():
                tried.append("gemini")
                text = llm.gemini_chat(prompt, system=system, max_tokens=max_tokens)
                if text:
                    return Inference(text, "gemini", task, tried, generated=True)
        except llm.LLMError:
            continue
    floor = deterministic if deterministic is not None else \
        "No model configured — deterministic path only; evidence recorded verbatim."
    return Inference(floor, "deterministic", task, tried, generated=False)


# --------------------------------------------------------------------------- #
# POKEE — discovers / reasons (complex)
# --------------------------------------------------------------------------- #
def analyze_signal(signal: dict[str, Any]) -> Inference:
    """Primary research-intelligence pass over a verified public signal."""
    prompt = (f"Signal type: {signal.get('signal_type','')}\n"
              f"Title: {signal.get('title','')}\n"
              f"Summary: {signal.get('summary','')}\n"
              f"State: {signal.get('state','')}\n"
              f"Source: {signal.get('source_url','')}\n"
              f"Date: {signal.get('signal_date','')}\n\n"
              "What decision intent does this public evidence support?")
    det = f"Evidence recorded: {signal.get('title','(untitled signal)')} — deterministic pass, no inference."
    return route(prompt, system=RESEARCH_SYSTEM, task=COMPLEX, max_tokens=200, deterministic=det)


# --------------------------------------------------------------------------- #
# GEMINI — processes (simple / high-volume)
# --------------------------------------------------------------------------- #
def classify(text: str, labels: list[str]) -> Inference:
    """High-volume content classification (Gemini-first)."""
    prompt = (f"Classify the text into exactly one label from {labels}. Return only the label.\n\n{text}")
    det = next((l for l in labels if l.lower() in text.lower()), labels[0] if labels else "")
    inf = route(prompt, system="You are a precise classifier.", task=SIMPLE, max_tokens=12,
                deterministic=det)
    # Normalise a model answer down to one known label.
    inf.text = next((l for l in labels if l.lower() in inf.text.lower()),
                    det if det else inf.text)
    return inf


def summarize(text: str, *, words: int = 40) -> Inference:
    """Short summary (Gemini-first, high-volume)."""
    prompt = f"Summarize in under {words} words, plain and factual:\n\n{text}"
    det = (text[:200] + "…") if len(text) > 200 else text
    return route(prompt, system="You write short, factual summaries.", task=SIMPLE,
                 max_tokens=max(60, words * 2), deterministic=det)


# --------------------------------------------------------------------------- #
# CODE DECIDES — the deterministic validation gate (9 checks)
# --------------------------------------------------------------------------- #
_SUPPRESS_STATUSES = {"suppressed", "unsubscribed", "complaint", "do_not_contact"}


@dataclass
class ValidationResult:
    passed: bool
    needs_human: bool
    checks: dict[str, bool]
    reasons: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "needs_human": self.needs_human,
                "checks": self.checks, "reasons": self.reasons}


def validate(signal: dict[str, Any], campaign: dict[str, Any], *,
             known_source_urls: set[str] | None = None) -> ValidationResult:
    """Deterministic compliance gate — the ONLY thing that clears a record.

    Mirrors the architecture's checklist exactly:
      URL present · source verified · date valid · not duplicate · state
      supported · contact permission · not suppressed · advisor licensed ·
      human approval required?
    """
    known = known_source_urls or set()
    url = (signal.get("source_url") or "").strip()
    state = (signal.get("state") or "").strip().upper()
    lic = {s.strip().upper() for s in (campaign.get("advisor_license_states") or "").split(",") if s.strip()}
    target_state = (campaign.get("target_state") or "").strip().upper()
    status = (signal.get("status") or "").strip().lower()

    checks = {
        "url_present": bool(url),
        "source_verified": url.startswith(("http://", "https://")),
        "date_valid": bool((signal.get("signal_date") or "").strip()),
        "not_duplicate": url not in known,
        "state_supported": bool(target_state) and state == target_state,
        "contact_permission": signal.get("signal_type") in ("first_party_form", "inbound", "consented"),
        "not_suppressed": status not in _SUPPRESS_STATUSES,
        "advisor_licensed": bool(state) and state in lic,
    }
    reasons = [k for k, ok in checks.items() if not ok]

    # Hard gates: any of these failing means the record cannot proceed at all.
    hard = ["url_present", "source_verified", "date_valid", "not_duplicate",
            "state_supported", "not_suppressed", "advisor_licensed"]
    passed = all(checks[k] for k in hard)

    # Human approval required whenever we lack explicit contact permission
    # (public-signal path) even if every hard gate passed — a licensed human
    # must approve first-touch outreach to a non-consented prospect.
    needs_human = passed and not checks["contact_permission"]
    checks["human_approval_required"] = needs_human
    return ValidationResult(passed=passed, needs_human=needs_human, checks=checks, reasons=reasons)


# --------------------------------------------------------------------------- #
# Full pipeline: reason → decide → (persist | route to human)
# --------------------------------------------------------------------------- #
def process_signal(signal: dict[str, Any], campaign: dict[str, Any], *,
                   known_source_urls: set[str] | None = None,
                   persist: bool = False) -> dict[str, Any]:
    """One signal end-to-end: Pokee reasons, code decides, human/Neon follows."""
    inference = analyze_signal(signal)
    decision = validate(signal, campaign, known_source_urls=known_source_urls)

    outcome = ("blocked" if not decision.passed
               else "human_approval" if decision.needs_human else "approved")

    result = {
        "signal_id": signal.get("id"),
        "inference": {"text": inference.text, "tier": inference.tier,
                      "generated": inference.generated, "task": inference.task_kind},
        "validation": decision.as_dict(),
        "outcome": outcome,
    }

    if persist and signal.get("campaign_id"):
        from . import store
        if outcome == "human_approval":
            store.add_approval(signal["campaign_id"], "signal", signal.get("id", ""),
                               signal.get("title", ""),
                               f"Public-signal first touch — {inference.text}", "router")
        store.add_run(signal["campaign_id"], "compass", "route", "signal",
                      signal.get("id", ""),
                      f"[{inference.tier}] {outcome}: {inference.text[:140]}")
    return result
