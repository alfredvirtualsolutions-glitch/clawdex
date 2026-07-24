"""The Juan OS command hierarchy: 26 agents across 6 divisions.

Encoded directly from the operating spec. This is the single source of truth for
the agent registry the frontend renders (Agent Builder, Workflow Canvas) and the
orchestrator routes work through. Nothing here performs external work — it
describes *who* does *what*, at which authority level, and how records flow.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


# --------------------------------------------------------------------------- #
# Authority levels (who may do what)
# --------------------------------------------------------------------------- #
AUTHORITY_LEVELS = {
    1: {"name": "Research Authority", "can": "Discover information; cannot approve a lead or message."},
    2: {"name": "Evidence Authority", "can": "Verify and classify data; cannot authorize outreach."},
    3: {"name": "Decision Authority", "can": "Approve, reject, pause, or escalate records."},
    4: {"name": "Execution Authority", "can": "Execute approved actions within strict campaign rules."},
    5: {"name": "Command Authority", "can": "Manage campaigns and resolve conflicts; cannot override suppression, compliance, or mandatory human financial review."},
}

DIVISIONS = {
    "command": {"name": "Command", "color": "#1d4ed8"},
    "signal": {"name": "Signal Intelligence", "color": "#0ea5e9"},
    "extraction": {"name": "URL & Extraction", "color": "#6366f1"},
    "data": {"name": "Data Trust", "color": "#14b8a6"},
    "qualification": {"name": "Qualification & Compliance", "color": "#f59e0b"},
    "outreach": {"name": "Outreach", "color": "#a855f7"},
    "operations": {"name": "Conversion & Operations", "color": "#10b981"},
}


@dataclass(frozen=True)
class Agent:
    key: str
    name: str
    role: str
    division: str
    authority: int
    summary: str
    tasks: list[str] = field(default_factory=list)
    guardrails: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["division_name"] = DIVISIONS[self.division]["name"]
        d["division_color"] = DIVISIONS[self.division]["color"]
        d["authority_name"] = AUTHORITY_LEVELS[self.authority]["name"]
        return d


AGENTS: list[Agent] = [
    # ---------------- Command ----------------
    Agent(
        "retirement_specialist", "Retirement Specialist", "Main Orchestrator & Campaign Director",
        "command", 5,
        "Senior operating intelligence: plans the mission, delegates jobs, monitors quality, resolves conflicts, and decides whether a signal or lead may advance.",
        ["Create and activate retirement campaigns", "Assign state/profession/system/advisor/signal priorities",
         "Start daily search cycles and delegate to specialist agents", "Monitor queues, failures, retries, costs, provider health",
         "Enforce human review for high-risk/high-value decisions", "Approve Hot leads before outreach",
         "Stop campaigns on compliance/deliverability/source-quality problems", "Produce the daily operating decision"],
        ["Never declare an annuity suitable", "Never auto-recommend a financial product",
         "Never approve outreach without verified evidence", "Never permit guessed contact info",
         "Never ignore suppression/opt-out", "Never manufacture urgency", "Never allow scrape-to-send"],
    ),
    # ---------------- Signal Intelligence ----------------
    Agent("nova", "Nova", "Daily Signal Research Agent", "signal", 1,
          "Opportunity finder. Searches for current retirement-related developments, deadlines, employer events, and account questions.",
          ["Run morning/midday/evening signal searches", "Generate state-specific queries",
           "Search official sites, news, public posts, retirement systems, directories",
           "Record candidate URLs with publication/event dates", "Separate individual vs organization signals",
           "Create daily signal-search reports"],
          ["Never treat a search snippet as verified evidence"]),
    Agent("atlas", "Atlas", "State Retirement Intelligence Agent", "signal", 1,
          "Specialist in state retirement systems, pension terminology, benefit rules, deadlines, and legislation.",
          ["Maintain retirement intelligence library per state", "Monitor official retirement-system sites",
           "Track rule/eligibility/deadline/board/legislation changes", "Distinguish publication vs effective dates",
           "Provide approved state terminology to Scribe", "Flag material updates to Retirement Specialist"]),
    Agent("echo", "Echo", "Social & Public Conversation Agent", "signal", 1,
          "Monitors publicly accessible conversations revealing retirement questions and transitions.",
          ["Search public posts across LinkedIn/Facebook pages/X/Reddit/forums", "Detect retirement & transition language",
           "Route anonymous discussions to market research, not lead extraction", "Recommend content topics & outreach angles",
           "Route possible signals to Delta"],
          ["Never identify anonymous users", "Never access private profiles", "Never bypass logins",
           "Never infer age/health/assets/family"]),
    Agent("delta", "Delta", "Signal Verification Agent", "signal", 2,
          "Evidence inspector. Proves a discovered signal is real, current, relevant, correctly dated, and connected to the named person/org.",
          ["Open every candidate source and confirm the claim appears", "Verify person/employer/org/state/dates",
           "Capture a factual excerpt", "Reject inaccessible/outdated/duplicate/fabricated/irrelevant signals",
           "Calculate source reliability & verification confidence"],
          ["Only verified signals may enter Pathfinder"]),
    # ---------------- URL & Extraction ----------------
    Agent("pathfinder", "Pathfinder", "URL Intelligence Agent", "extraction", 1,
          "Turns one verified signal into a map of useful public URLs (staff, bio, contact, benefits, directory, news).",
          ["Canonicalize the primary signal URL", "Discover the official organization domain",
           "Search sitemaps & relevant internal links", "Classify & rank URLs by extraction value", "Create crawler jobs"]),
    Agent("forge", "Forge", "Crawler Fleet Commander", "extraction", 1,
          "Manages a fleet of specialized crawlers, routing each page to the right extraction method.",
          ["Route static HTML / JS / directory / PDF / contact pages to the right worker",
           "Control request rates and retries", "Respect robots & public-access boundaries", "Record failures & snapshots"],
          ["Never bypass CAPTCHAs/logins/access controls", "Never scrape private profiles", "Never guess email patterns"]),
    Agent("lens", "Lens", "Structured Data Extraction Agent", "extraction", 2,
          "Converts public page content into structured records, extracting only visibly supported information.",
          ["Extract names/titles/orgs/visible emails/phones/LinkedIn/locations/bios/events/dates",
           "Associate each field with its exact source URL", "Normalize names/phones/state codes/URLs",
           "Assign field confidence; store raw extraction evidence"],
          ["No field without value+source_url+provider+confidence+validation_status+timestamp"]),
    Agent("anchor", "Anchor", "Identity Resolution Agent", "extraction", 2,
          "Determines whether the person in the signal is the same person in a directory/profile/enrichment record.",
          ["Match name/title/org/location/profile URL/domain", "Resolve spelling & legitimate name variations",
           "Detect conflicting identities", "Send uncertain matches to human review", "Build an identity evidence chain"]),
    # ---------------- Data Trust ----------------
    Agent("ledger", "Ledger", "Neon Database Steward", "data", 2,
          "Official record keeper. Every agent writes evidence, status, timestamps, and audit info through Ledger.",
          ["Manage DB writes & state transitions", "Store raw signals/leads before promotion",
           "Prevent direct writes into validated tables", "Maintain field-level provenance & immutable audit logs",
           "Control promotion from raw to validated data"]),
    Agent("merge", "Merge", "Deduplication & Consolidation Agent", "data", 2,
          "Prevents paying to enrich or contacting the same prospect through duplicate records.",
          ["Normalize emails/names/phones/domains/URLs", "Detect exact & probable duplicates; merge evidence",
           "Preserve newer signals as separate events", "Maintain master-person & master-organization IDs"]),
    Agent("scout", "Scout", "Public Data Enrichment Agent", "data", 2,
          "Fills missing professional info from supporting public/approved sources without silently replacing first-party data.",
          ["Find official sites, bios, domains, titles, phones, LinkedIn", "Use Firecrawl/Exa/Apollo (approved providers)",
           "Compare enriched values with source records", "Write conflicts to an enrichment-change log", "Assign provider & match confidence"]),
    Agent("mx_guardian", "MX Guardian", "DNS Email Receiving Agent", "data", 2,
          "Determines whether an email domain is technically configured to receive mail before validating the mailbox.",
          ["Normalize domain; check existence (NS/SOA/A/AAAA)", "Check MX; reject Null MX; resolve MX hosts",
           "Test SMTP availability without sending", "Classify domain valid/risky/invalid/unknown"],
          ["DNS receiving gate runs before mailbox validation"]),
    Agent("verity", "Verity", "Mailbox Validation Agent", "data", 2,
          "Checks whether the specific professional email is safe enough to enter outreach qualification.",
          ["Validate syntax; run Clearout/approved validator", "Detect invalid/disposable/catch-all/role/unknown/risky",
           "Reject invalid mailboxes; send catch-all/unknown to review", "Revalidate replaced emails"],
          ["Only 'valid' emails automatically continue"]),
    # ---------------- Qualification & Compliance ----------------
    Agent("compass", "Compass", "Public Signal & Lead Scoring Agent", "qualification", 3,
          "Scores observable retirement intent — never private facts the prospect hasn't voluntarily provided.",
          ["Score signal strength/timing/recency/source/identity/contact", "Classify Hot/Moderate/Nurture/Reject",
           "Recalculate scores when signals change", "Explain every score"]),
    Agent("sentinel", "Sentinel", "Outreach Eligibility Gate Agent", "qualification", 3,
          "Decides whether a validated lead should be contacted for a specific campaign.",
          ["Confirm source/identity/state/advisor-licensing alignment", "Check email validity & catch-all",
           "Check suppression/opt-out & prior contact", "Require human review for Hot leads", "Approve/pause/reject/suppress"]),
    Agent("counsel", "Counsel", "Compliance & Audit Agent", "qualification", 3,
          "Watches for unsupported claims, missing evidence, improper outreach, invented urgency, and licensing conflicts.",
          ["Validate personalization is evidence-backed", "Confirm sender details/postal/opt-out/calendar",
           "Confirm advisor-state alignment; audit agent decisions", "Flag financial-product claims for human review",
           "Freeze campaigns on serious compliance failures"]),
    # ---------------- Outreach ----------------
    Agent("scribe", "Scribe", "Signal-Based Personalization Agent", "outreach", 3,
          "Converts verified signals into short, natural, educational outreach. Clarity, not pressure.",
          ["Reference the exact verified signal", "Explain why it may be worth reviewing",
           "Use only evidence-supported urgency", "Insert advisor name/calendar/unsubscribe", "Produce variations without changing facts"],
          ["Never invent age/income/balance/net worth/retirement date/tax bracket/losses/family/hardship/annuity interest"]),
    Agent("critic", "Critic", "Message Quality & Evidence Agent", "outreach", 3,
          "Reviews every personalized message before it enters the sending queue.",
          ["Compare message against source evidence", "Detect hallucinated facts & fake urgency",
           "Check tone/readability/length/CTA/footer", "Approve/revise/reject; escalate sensitive messages"]),
    Agent("courier", "Courier", "Outreach Queue & Provider Routing Agent", "outreach", 4,
          "Schedules approved messages and routes them to the correct sending provider. Never sends immediately.",
          ["Create queue records & schedule approved messages", "Select AutoSend/Resend/AgentMail/SMTP",
           "Generate idempotency keys; enforce send limits & pacing", "Cancel queued messages when suppression changes"]),
    Agent("relay", "Relay", "Delivery Webhook & Event Agent", "outreach", 4,
          "Receives provider events and updates the true status of every outreach message.",
          ["Process sent/delivered/bounced/opened/clicked/unsubscribed/complaint events", "Authenticate & de-duplicate webhooks",
           "Trigger suppression after hard bounces/complaints/unsubscribes", "Track provider performance"],
          ["An open is not proof of interest; a reply or booked meeting is stronger"]),
    # ---------------- Conversion & Operations ----------------
    Agent("pulse", "Pulse", "Reply Intelligence Agent", "operations", 4,
          "Reads incoming replies, classifies intent, and routes the conversation to the correct next action.",
          ["Classify replies (interest/info/meeting/objection/OOO/wrong-person/opt-out/complaint)",
           "Draft simple operational replies", "Escalate financial questions to the advisor"]),
    Agent("closer", "Closer", "Appointment & Advisor Routing Agent", "operations", 4,
          "Converts genuine interest into a clean advisor handoff. No pressure, no financial advice.",
          ["Send correct advisor calendar; confirm state/campaign ownership", "Create appointment records; prevent double booking",
           "Pass verified signal + conversation summary to advisor", "Track booked/attended/rescheduled/cancelled/no-show"]),
    Agent("keeper", "Keeper", "Suppression & Consent Agent", "operations", 4,
          "Protects every person's communication preference across all providers, campaigns, and agents.",
          ["Maintain global suppression list; process unsubscribes/complaints", "Record channel-specific consent",
           "Cancel pending messages; stop active sequences; sync across providers", "Prevent enrichment from recreating opted-out contacts"],
          ["Suppression overrides campaign priorities, scores, enrichment, and orchestrator preferences"]),
    Agent("beacon", "Beacon", "Advisor & Operations Notification Agent", "operations", 4,
          "Alerts the right human on important signals, qualified responses, appointments, compliance risks, or failures.",
          ["Notify advisors of Hot leads & positive replies", "Alert on booked meetings & provider failures",
           "Alert Counsel on compliance concerns", "Avoid duplicate alerts for the same event"]),
    Agent("oracle", "Oracle", "Analytics & Daily Reporting Agent", "operations", 4,
          "Measures whether Juan OS produces real business results rather than vanity metrics.",
          ["Generate daily/weekly/campaign reports", "Track verified-signal/useful-URL/extraction/validation rates",
           "Track delivery/bounce/reply/booking/attendance", "Identify bottlenecks & recommend adjustments"]),
]

AGENTS_BY_KEY = {a.key: a for a in AGENTS}


# --------------------------------------------------------------------------- #
# Status flows (the state machines records move through)
# --------------------------------------------------------------------------- #
SIGNAL_FLOW = ["discovered", "pending_verification", "verified", "url_intelligence_ready",
               "extraction_ready", "extraction_complete"]
LEAD_FLOW = ["raw", "deduplicated", "identity_verified", "enrichment_complete", "domain_validated",
             "email_validated", "scored", "outreach_review", "outreach_ready"]
OUTREACH_FLOW = ["ready", "personalized", "quality_checked", "human_reviewed", "approved",
                 "queued", "scheduled", "sent", "delivered", "replied", "meeting_booked"]
FAILURE_STATES = ["source_unavailable", "signal_rejected", "identity_conflict", "duplicate",
                  "invalid_domain", "invalid_email", "catch_all", "manual_review", "suppressed",
                  "opted_out", "provider_failed", "message_rejected"]

# The handoff pipeline — which agent owns each transition (source -> destination).
PIPELINE = [
    ("nova", "delta", "candidate signal -> verification"),
    ("atlas", "delta", "state intelligence -> verification"),
    ("echo", "delta", "social signal -> verification"),
    ("delta", "pathfinder", "verified signal -> URL intelligence"),
    ("pathfinder", "forge", "URL map -> crawl jobs"),
    ("forge", "lens", "crawl results -> extraction"),
    ("lens", "anchor", "extracted record -> identity resolution"),
    ("anchor", "ledger", "identity -> persisted raw lead"),
    ("ledger", "merge", "raw lead -> deduplication"),
    ("merge", "scout", "deduplicated -> enrichment"),
    ("scout", "mx_guardian", "enriched -> DNS receiving gate"),
    ("mx_guardian", "verity", "valid domain -> mailbox validation"),
    ("verity", "compass", "valid email -> scoring"),
    ("compass", "sentinel", "scored -> eligibility gate"),
    ("sentinel", "counsel", "eligible -> compliance audit"),
    ("counsel", "scribe", "approved -> personalization"),
    ("scribe", "critic", "message -> quality check"),
    ("critic", "courier", "approved message -> queue"),
    ("courier", "relay", "sent -> delivery events"),
    ("relay", "pulse", "reply -> reply intelligence"),
    ("pulse", "closer", "genuine interest -> appointment routing"),
    ("closer", "beacon", "booked -> advisor notification"),
]

HANDOFF_CONTRACT_FIELDS = [
    "job_id", "campaign_id", "record_id", "source_agent", "destination_agent", "input_status",
    "required_evidence", "task_instruction", "priority", "attempt_count", "created_at", "deadline",
    "completion_status", "output_reference", "error_reason",
]

OPERATING_PRINCIPLES = [
    "Signal-first", "Evidence-backed", "State-specific", "Public-data only", "No guessed emails",
    "No guessed wealth", "No manufactured urgency", "No scrape-to-send",
    "No automatic financial recommendation", "Fully auditable", "Human-controlled at critical decisions",
]


def catalog_dict() -> dict:
    return {
        "divisions": DIVISIONS,
        "authority_levels": AUTHORITY_LEVELS,
        "agents": [a.to_dict() for a in AGENTS],
        "signal_flow": SIGNAL_FLOW,
        "lead_flow": LEAD_FLOW,
        "outreach_flow": OUTREACH_FLOW,
        "failure_states": FAILURE_STATES,
        "pipeline": [{"source": s, "destination": d, "label": l} for s, d, l in PIPELINE],
        "handoff_contract": HANDOFF_CONTRACT_FIELDS,
        "operating_principles": OPERATING_PRINCIPLES,
    }
