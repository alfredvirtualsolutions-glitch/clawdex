"""External provider integrations — the real seams behind the agents.

Each client reads its key from the environment (never hard-coded) and calls the
provider's real API. When a key is absent the client reports itself unconfigured
so the orchestrator falls back to local simulation. Keys are loaded from a
gitignored ``.env`` (see ``.env.example``) — nothing here embeds a secret.

Provider → agent mapping:
  Exa            → Nova / Echo   (signal & public research)
  Firecrawl      → Delta / Forge (verify + scrape public pages)
  Apollo         → Scout         (professional enrichment)
  Clearout       → Verity        (mailbox validation)
  MX (DNS)       → MX Guardian    (domain receiving gate)  [dnspython, no key]
  Warmy          → deliverability / inbox warmup
  Composio       → tool gateway   (connect additional actions)
"""

from __future__ import annotations

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

TIMEOUT = 25.0


class ProviderError(RuntimeError):
    pass


class ProviderUnavailable(ProviderError):
    """Raised when a provider's key is not configured."""


def _key(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise ProviderUnavailable(f"{name} is not set. Add it to your .env file.")
    return v


def _client() -> "httpx.Client":
    if httpx is None:
        raise ProviderError("httpx is not installed (pip install httpx).")
    return httpx.Client(timeout=TIMEOUT)


# --------------------------------------------------------------------------- #
# Exa — neural/keyword web search  (Nova, Echo)
# --------------------------------------------------------------------------- #
def exa_search(query: str, num_results: int = 5, *, use_autoprompt: bool = True) -> list[dict[str, Any]]:
    key = _key("EXA_API_KEY")
    with _client() as c:
        r = c.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": key, "content-type": "application/json"},
            json={"query": query, "numResults": num_results, "useAutoprompt": use_autoprompt,
                  "contents": {"text": {"maxCharacters": 600}}},
        )
        r.raise_for_status()
        data = r.json()
    return [
        {"title": x.get("title"), "url": x.get("url"), "published": x.get("publishedDate"),
         "snippet": (x.get("text") or "")[:400], "provider": "exa"}
        for x in data.get("results", [])
    ]


# --------------------------------------------------------------------------- #
# Firecrawl — scrape + search  (Delta verify, Forge crawl)
# --------------------------------------------------------------------------- #
def firecrawl_scrape(url: str) -> dict[str, Any]:
    key = _key("FIRECRAWL_API_KEY")
    with _client() as c:
        r = c.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
            json={"url": url, "formats": ["markdown"], "onlyMainContent": True},
        )
        r.raise_for_status()
        data = r.json().get("data", {})
    md = data.get("markdown", "") or ""
    return {"url": url, "markdown": md, "title": (data.get("metadata") or {}).get("title"),
            "length": len(md), "provider": "firecrawl"}


def firecrawl_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    key = _key("FIRECRAWL_API_KEY")
    with _client() as c:
        r = c.post(
            "https://api.firecrawl.dev/v1/search",
            headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
            json={"query": query, "limit": limit},
        )
        r.raise_for_status()
        data = r.json()
    return [{"title": x.get("title"), "url": x.get("url"), "snippet": x.get("description"),
             "provider": "firecrawl"} for x in data.get("data", [])]


# --------------------------------------------------------------------------- #
# Apollo — professional enrichment  (Scout)
# --------------------------------------------------------------------------- #
def apollo_enrich(*, first_name: str | None = None, last_name: str | None = None,
                  organization_name: str | None = None, domain: str | None = None,
                  email: str | None = None) -> dict[str, Any]:
    key = _key("APOLLO_API_KEY")
    payload: dict[str, Any] = {k: v for k, v in {
        "first_name": first_name, "last_name": last_name,
        "organization_name": organization_name, "domain": domain, "email": email,
    }.items() if v}
    with _client() as c:
        r = c.post(
            "https://api.apollo.io/v1/people/match",
            headers={"X-Api-Key": key, "content-type": "application/json",
                     "Cache-Control": "no-cache"},
            json=payload,
        )
        r.raise_for_status()
        person = r.json().get("person") or {}
    return {
        "full_name": person.get("name"),
        "title": person.get("title"),
        "email": person.get("email"),
        "linkedin_url": person.get("linkedin_url"),
        "organization": (person.get("organization") or {}).get("name"),
        "domain": (person.get("organization") or {}).get("primary_domain"),
        "provider": "apollo",
    }


# --------------------------------------------------------------------------- #
# Clearout — mailbox validation  (Verity)
# --------------------------------------------------------------------------- #
def clearout_verify(email: str) -> dict[str, Any]:
    token = _key("CLEAROUT_API_KEY")
    with _client() as c:
        r = c.post(
            "https://api.clearout.io/v2/email_verify/instant",
            headers={"Authorization": f"Bearer:{token}", "content-type": "application/json"},
            json={"email": email},
        )
        r.raise_for_status()
        d = r.json().get("data", {})
    return {"email": email, "status": d.get("status"), "sub_status": d.get("sub_status"),
            "disposable": (d.get("disposable") or {}).get("value"),
            "role": (d.get("role") or {}).get("value"),
            "catch_all": (d.get("catch_all") or {}).get("value"),
            "safe_to_send": d.get("safe_to_send"), "provider": "clearout"}


# --------------------------------------------------------------------------- #
# MX Guardian — DNS receiving gate  (dnspython, no key)
# --------------------------------------------------------------------------- #
def mx_lookup(domain: str) -> dict[str, Any]:
    try:
        import dns.resolver  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise ProviderError("dnspython not installed (pip install dnspython).") from exc
    domain = domain.strip().lower().lstrip("@")
    try:
        answers = dns.resolver.resolve(domain, "MX")
        hosts = sorted((int(a.preference), str(a.exchange).rstrip(".")) for a in answers)
        if len(hosts) == 1 and hosts[0][1] in ("", "."):
            return {"domain": domain, "status": "invalid", "reason": "null_mx", "mx": [], "provider": "dns"}
        return {"domain": domain, "status": "valid", "mx": [h for _, h in hosts], "provider": "dns"}
    except dns.resolver.NXDOMAIN:
        return {"domain": domain, "status": "invalid", "reason": "nxdomain", "mx": [], "provider": "dns"}
    except dns.resolver.NoAnswer:
        return {"domain": domain, "status": "risky", "reason": "no_mx", "mx": [], "provider": "dns"}
    except Exception as exc:  # noqa: BLE001
        return {"domain": domain, "status": "unknown", "reason": str(exc), "mx": [], "provider": "dns"}


# --------------------------------------------------------------------------- #
# Warmy — inbox deliverability / warmup  (health probe; endpoints vary by plan)
# --------------------------------------------------------------------------- #
def warmy_status() -> dict[str, Any]:
    key = _key("WARMY_API_KEY")
    with _client() as c:
        r = c.get("https://backend.warmy.io/api/v1/deliverability",
                  headers={"Authorization": f"Bearer {key}"})
        r.raise_for_status()
        return {"provider": "warmy", "data": r.json()}


# --------------------------------------------------------------------------- #
# Composio — tool gateway (connected actions)
# --------------------------------------------------------------------------- #
def composio_apps() -> dict[str, Any]:
    key = _key("COMPOSIO_API_KEY")
    with _client() as c:
        r = c.get("https://backend.composio.dev/api/v1/apps", headers={"x-api-key": key})
        r.raise_for_status()
        return {"provider": "composio", "apps": r.json()}


# --------------------------------------------------------------------------- #
# Registry / status  (never exposes the key value)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ProviderInfo:
    name: str
    env: str
    agent: str
    purpose: str


REGISTRY = [
    ProviderInfo("exa", "EXA_API_KEY", "Nova / Echo", "Signal & public research"),
    ProviderInfo("firecrawl", "FIRECRAWL_API_KEY", "Delta / Forge", "Verify + scrape public pages"),
    ProviderInfo("apollo", "APOLLO_API_KEY", "Scout", "Professional enrichment"),
    ProviderInfo("clearout", "CLEAROUT_API_KEY", "Verity", "Mailbox validation"),
    ProviderInfo("dns", "", "MX Guardian", "DNS receiving gate (no key)"),
    ProviderInfo("warmy", "WARMY_API_KEY", "Deliverability", "Inbox warmup / deliverability"),
    ProviderInfo("composio", "COMPOSIO_API_KEY", "Tool Gateway", "Connected external actions"),
]


def status() -> list[dict[str, Any]]:
    out = []
    for p in REGISTRY:
        configured = True if not p.env else bool(os.environ.get(p.env, "").strip())
        out.append({"name": p.name, "agent": p.agent, "purpose": p.purpose,
                    "env": p.env, "configured": configured})
    return out
