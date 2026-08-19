# Daily Task Workflow — Juan Cabezas Campaign

> One repeatable daily run. Designed to be executed by **one local agent** with
> minimal supervision. The only human touch points are the **Hot-lead approval**
> and the **advisor discovery call**. Everything else runs unattended.

**Phase-1 states:** FL, TX, CA · **Tracks:** Annuity/Income (A) + Long-Term Care (B)

## Daily targets & safety limits (per state, tune later)

| Limit | Default | Why |
| --- | --- | --- |
| Signal searches / day | 60 (20 per state) | Bounded discovery cost |
| New verified signals / day | ≤ 40 | Quality over volume |
| New leads promoted / day | ≤ 15 | Keeps human review sane |
| Outreach sends / day | ≤ 25 | Deliverability + compliance |
| Hot leads | **100% human-reviewed before send** | Suitability + licensing |
| Recency window | last 90 days (dynamic `after:` filter) | Freshness |

## The daily cycle (runs morning · midday · evening)

Each cycle walks the full pipeline for one state/track slice, then rolls up a report.

```
1. PLAN      Retirement Specialist picks today's state + track focus, builds the
             query set from the knowledgebase (intent × location × recency × negatives).

2. SEARCH    Nova/Atlas/Echo run the approved queries (Exa/Firecrawl/Brave) across
             search, public professional posts, news, company announcements, public
             forums, and first-party form submissions. Record candidate URLs + dates.

3. VERIFY    Delta opens each source, confirms the statement is actually present,
             checks person/employer/state/date, captures a factual excerpt.
             Weak/unverifiable → Rejected (no assumptions).

4. MAP+CRAWL Pathfinder finds the useful public URLs (staff/contact/announcement);
             Forge crawls them with the right method; Lens extracts only visibly
             supported fields (name, org, publicly displayed business contact, date).

5. IDENTITY  Anchor confirms the person in the signal matches the public record.
             Uncertain → human review, never a guess.

6. STORE     Ledger persists the raw signal/lead with full provenance; Merge
             de-duplicates; Scout enriches ONLY from approved public/consented
             sources (Apollo/Firecrawl) — never fabricates contact info.

7. VALIDATE  MX Guardian checks the domain can receive mail (DNS/MX); Verity
             validates the specific mailbox (Clearout). Invalid → drop; catch-all → review.

8. SCORE     Compass computes the PUBLIC signal score (0–60) only. No age/asset/
             risk points until the prospect voluntarily supplies them.

9. GATE      Sentinel checks: source verified · identity verified · email valid ·
             not suppressed/opted-out · state ∈ {FL,TX,CA} · Juan licensed there ·
             signal fresh & above threshold. Counsel audits compliance (no product
             claims, required disclosures, consent for channel). Hot → HUMAN REVIEW.

10. DRAFT    Scribe writes a short, educational, evidence-backed message that
             references the exact public event/question and offers a Clarity Review
             or the matching lead magnet (income-gap estimate / LTC cost guide).
             Critic checks it against the source (no hallucinated facts, no fake
             urgency, required footer + opt-out).

11. QUEUE    Courier schedules ONLY approved messages within send limits/windows.
             Relay records delivery events; hard bounce/complaint → suppress.

12. CONVERT  Pulse classifies replies; genuine interest → Closer routes to Juan's
             calendar with the verified signal + conversation summary. Keeper honors
             every opt-out across channels. Beacon alerts Juan on Hot leads/bookings.

13. REPORT   Oracle writes the daily report: per state/track — searches run,
             verified signals, useful-URL rate, leads promoted, Hot/Moderate/Nurture,
             valid-email rate, sends, replies, bookings, cost per validated lead.
```

## Daily human checklist (≈10 min)
1. Open **Approvals** → review each **Hot** lead (evidence + draft) → Approve/Reject.
2. Skim **Run History** for any `manual_review` / `identity_conflict` flags.
3. Check **Command Center** KPIs + Oracle's daily report.
4. Take booked **discovery calls**; complete the voluntary qualification + suitability review.

## What the agent must NEVER do unattended
- Send to a **Hot** lead without human approval.
- Contact a prospect outside FL/TX/CA (phase 1) or one who opted out.
- Populate estimated age/assets/health, or invent an email/phone.
- Claim an annuity or LTC policy is suitable, risk-free, or guaranteed.

## Scheduling
Run the cycle 3×/day (e.g., 08:00 / 12:30 / 17:00 local). Options:
- **In-app:** click **Run cycle** (Workflow Canvas), or
- **Headless/cron:** `POST /api/orchestrator/run-cycle {"campaign_id": "<state campaign>"}` on a schedule (see the local-agent recommendation).
