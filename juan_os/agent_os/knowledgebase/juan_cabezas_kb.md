# Knowledgebase — Juan Cabezas Campaign (SignalBase)

> **Advisor:** Juan Cabezas — licensed financial professional, multiple states.
> **Launch states (phase 1):** **Florida (FL), Texas (TX), California (CA).**
> **Model:** find *public intent signals* → confirm facts through *voluntary,
> consent-based qualification* → route interested prospects to a *licensed human
> advisor* for discovery and suitability. **Never** guess age, assets, health, or
> suitability. This is an intent-detection engine, not a wealth-guessing scraper.

This knowledgebase drives two product tracks under one advisor:

| Track | Focus | Source doc |
| --- | --- | --- |
| **A · Annuity / Retirement-Income** | Retirement income, principal protection, rollovers, pension & CD decisions, business-owner retirement | jUAN_iNTENT |
| **B · Long-Term Care (LTC)** | LTC cost planning, traditional vs. hybrid coverage, protecting retirement from care costs | LTCI brief |

---

## 0. Hard compliance guardrails (apply to BOTH tracks, always)

These are non-negotiable and enforced by the Counsel/Sentinel gates before any outreach.

1. **Public sources only.** Every signal must carry an active `source_url` and a real publication/event date.
2. **Quote only what the source states.** No paraphrase that adds facts.
3. **Never infer** age, income, assets, net worth, account balance, health, marital status, tax bracket, or suitability. Job title / ZIP / home value / employer are **clues, not proof**.
4. **Never identify anonymous forum users.** Use forums for market/content research only.
5. **No invented contact info / no guessed email patterns.** Capture contact details only when *publicly displayed for legitimate business communication*, or when the prospect voluntarily submits a form.
6. **Licensing gate:** Juan must be appropriately licensed in the prospect's state. Phase 1 = FL, TX, CA only.
7. **Channel & consent:** honor opt-out and suppression lists; email must have accurate sender info + working unsubscribe; SMS/automated calls require the required prior consent (FCC/TCPA).
8. **No product claims:** never call an annuity or LTC policy risk-free, guaranteed by the government, universally appropriate, or already suitable. State that guarantees depend on the **issuing insurer** and contract terms (caps, participation rates, fees, riders, surrender/elimination periods, underwriting).
9. **Human-in-the-loop:** a licensed advisor makes every suitability/recommendation decision. The agent routes; it does not recommend.
10. **Audit everything:** why the lead was selected, the evidence, consent, outreach copy, and disposition.

---

## 1. Ideal Prospect Profile (verify by consent, never assume)

**Track A (Annuity/Income):** age ~55–75 or retired; retiring now or within ~10 yrs; low-to-moderate risk tolerance; concern = protecting assets / dependable income; accounts = IRA, 401(k), 403(b), 457(b), SEP/SIMPLE IRA, pension, existing annuity, CDs, brokerage, lump-sum pension.

**Track B (LTC):** ages ~45–65 planning ahead (and adult children of aging parents); concern = cost of care / protecting retirement from a long care event; evaluating traditional vs. hybrid coverage; affluent households, business owners, pre-retirees.

> These attributes are confirmed via the **voluntary qualification form / discovery call**, not scraped.

---

## 2. Signal taxonomy

### Track A — four intent layers (annuity/income)
- **Layer 1 — Direct intent:** actively asking about retirement income, annuities, rollovers, market protection, pension choices ("should I buy an annuity", "what should I do with my 401k when I retire", "fixed annuity vs CD", "pension lump sum or monthly payments").
- **Layer 2 — Problem-aware:** describing a problem annuity planning may address — market-loss fear, income gap ("Social Security is not enough"), maturing CD, "safe place for retirement money".
- **Layer 3 — Life events:** retirement announcements, pension/lump-sum decisions, early-retirement packages, "leaving my employer what happens to 401k", self-disclosed inheritance/business sale.
- **Layer 4 — Small-business owner:** SEP/SIMPLE/solo-401k retirement, "selling my business and retiring", succession announcements.

### Track B — three intent tiers (LTC)
- **High-intent:** `long term care insurance quote [state]`, `long term care insurance advisor near me`, `long term care insurance cost by age`, `compare long term care insurance policies`, `hybrid life insurance long term care quote`.
- **Buyer-research:** `is long term care insurance worth it`, `how much long term care insurance do I need`, `when should I buy long term care insurance`, `long term care insurance vs self funding`, `traditional vs hybrid long term care`.
- **Audience/caregiver context:** `long term care planning before retirement`, `how to pay for elderly parent care`, `asset protection long term care insurance`, `long term care insurance for business owners`, `assisted living cost [city]`, `nursing home cost [state]`.

### Signal categories (output taxonomy)
`retirement_timing · rollover · pension · market_risk · income_gap · cd_maturity · business_transition · tax_concern · ltc_cost · ltc_coverage_compare · caregiver_planning · asset_protection`

---

## 3. Per-state query packs (FL / TX / CA)

Each query = **intent phrase + location + recency + negative keywords**. The date filter is generated dynamically from the campaign window (e.g. `after:<today-90d>`). Retirement-system names are strong local pension-decision signals.

### Shared location + recency templates
```
("planning to retire" OR "retiring this year") "<STATE>"
("pension lump sum" OR "retirement package") "<STATE>"
("protect my retirement savings") "<STATE>"
("long term care insurance cost" OR "long term care planning") "<STATE>"
after:<DATE> ("retiring soon" OR "retirement announced") "<STATE>"
after:<DATE> ("pension buyout" OR "pension lump sum") "<STATE>"
```

### Florida (FL)
- **Retirement systems / pension angles:** **FRS** (Florida Retirement System), **DROP** (Deferred Retirement Option Program — participants near DROP end = strong timing signal).
- **State color:** large retiree/snowbird population, no state income tax, many small-business owners.
- Representative queries:
  - `("FRS retirement" OR "DROP program ends") Florida` · `("pension lump sum" OR "DROP payout") Florida`
  - `("small business owner retiring") Florida` · `("selling my business and retiring") Florida`
  - `long term care insurance cost Florida` · `assisted living cost [Miami|Tampa|Orlando|Jacksonville]`
  - `site:reddit.com "retiring in Florida" ("IRA" OR "401k")`

### Texas (TX)
- **Retirement systems:** **TRS of Texas** (teachers), **ERS of Texas** (state employees).
- **State color:** no state income tax, energy/manufacturing, strong business-owner base.
- Representative queries:
  - `("TRS Texas" OR "teacher retirement Texas") ("lump sum" OR "annuity option")`
  - `("403b rollover" OR "teacher retirement") Texas` · `("owner retiring" OR "business succession") Texas`
  - `long term care insurance cost Texas` · `nursing home cost Texas`
  - `site:reddit.com "pension lump sum or monthly" Texas`

### California (CA)
- **Retirement systems:** **CalSTRS** (teachers), **CalPERS** (public employees).
- **State color:** high cost of living, large public-sector workforce, pension election decisions.
- Representative queries:
  - `("CalSTRS" OR "CalPERS") ("retirement election" OR "lump sum" OR "pension option")`
  - `("pension lump sum" OR "retirement package") California` · `("403b rollover" OR "teacher retirement") California`
  - `long term care insurance California` · `long term care planning high net worth California`
  - `site:reddit.com "retiring soon" "IRA" California`

---

## 4. Negative keywords

Applied to reduce waste; tune weekly from the actual search-term report.

**Universal:** `-jobs -hiring -careers -salary -internship -recruiter -obituary -death -funeral -sports -athlete -pet -software -calculator -definition -wikipedia -student -homework -research-paper -crypto -day-trading -lottery -coupon -"promo code"`

**LTC-specific:** block claims/servicing/free-aid/unrelated insurance — `claim, "claim status", "claims department", login, "my account", "customer service", "phone number", "medicaid application", "medicare login", "auto insurance", "home insurance", "pet insurance", "dental insurance", "workers compensation", doctor, hospital, "provider network", prescription`.

**Consumer-only (use selectively):** `-advisor -agent -insurance` — but **do NOT** apply these when researching competitors, referral partners, or educational content.

**Do NOT auto-exclude (often high value):** `affordable, cost, price, rates, quote, comparison, "worth it", best, medicare, medicaid, "assisted living", "nursing home", "home care", caregiver`. (E.g. "long term care insurance cost at 55" is a strong lead; "Medicaid application" is not.)

---

## 5. Classification

| Class | Meaning | Recommended action |
| --- | --- | --- |
| **Hot** | Recent, direct statement implying an immediate decision (retiring ≤12 mo, pension lump-sum offer, CD maturing soon, "what do I do with my 401k", asked for annuity/LTC comparison, business sale announced). | Verify currency → personalized *educational* message → invite discovery call. **Never lead with a product.** Requires human review before send. |
| **Moderate** | Relevant concern, no deadline (retiring 1–5 yrs, SS income-gap talk, researching safer investments, comparing traditional vs hybrid LTC). | Educational nurture sequence; monitor for stronger intent. |
| **Nurture** | General interest, no clear need (shared an article, attended a seminar, follows retirement content). | Add only with lawful permission; light educational content. |
| **Cold / Rejected** | Outdated, anonymous, no contact path, no relevance, competitor content, clearly below target stage, signal depends on guessed age/assets, duplicate, no `source_url`, or fabricated/AI-generated source. | Suppress. |

---

## 6. Lead scoring model

**Public Signal Score (0–60)** — computed from observable intent only:
- Retirement/LTC timing 0–15 · Financial-decision signal 0–15 · Pain/need 0–15 · Recency 0–10 · Source reliability 0–5.

**Qualification Score (0–40)** — **only** from voluntary answers:
- Age/retirement stage 0–10 · Investable assets (or LTC funding capacity) 0–15 · Risk/protection need 0–5 · Income/care need 0–5 · Timeline 0–5.

**Final bands:** 80–100 Qualified priority · 65–79 Strong discovery candidate · 50–64 Nurture & qualify · 35–49 Low-priority nurture · <35 Do not pursue.

> A high public-signal score does **not** prove suitability. Qualification points are added **only** after the prospect voluntarily supplies them.

---

## 7. Voluntary qualification form (neutral wording)

Age range · expected retirement timing · accounts/assets being reviewed · approximate amount considered for income/protection planning · biggest concern (market loss / running out of money / dependable income / low returns / taxes / inflation / legacy / pension options / consolidation) · importance of access to funds · currently working with a professional? · would you like a licensed professional to review your options?

**LTC add-ons (non-sensitive only):** age range · state · intended retirement age · preferred care setting · whether family caregiving support exists · "what are you exploring?" (retirement / care-cost / family caregiving / coverage comparison).

**Discovery framing (balanced, not sales-heavy):** "If the market declined near/during retirement, how would that affect your plans?" · "How important is it that part of your income continues regardless of how long you live?" · "Are taxes on your retirement savings an important concern?" · (LTC) "How would a multi-year care need affect your retirement income and your family?"

> Never request detailed medical history, SSN, account numbers, or full asset detail on a landing form. Reserve health/underwriting and deep financials for a secure, consent-based conversation.

---

## 8. Search-agent output schema (per signal)

```json
{
  "signal_id": "uuid",
  "track": "annuity | ltc",
  "discovered_at": "ISO-8601", "signal_date": "ISO-8601",
  "signal_category": "retirement_timing|rollover|pension|market_risk|income_gap|cd_maturity|business_transition|tax_concern|ltc_cost|ltc_coverage_compare|caregiver_planning|asset_protection",
  "signal_strength": "hot|moderate|nurture|rejected",
  "person_name": null, "business_name": null, "job_title": null, "location": null,
  "source_platform": "google|linkedin|news|company_site|public_forum|first_party_form",
  "source_url": "https://...", "source_title": "string", "source_excerpt": "short factual excerpt",
  "intent_summary": "why this indicates potential planning intent",
  "public_signal_score": 0, "qualification_score": null, "total_score": null,
  "contact_email": null, "contact_phone": null, "contact_source_url": null,
  "contact_permission": "unknown|email_allowed|call_allowed|sms_allowed|opted_out",
  "advisor_state_license_required": "FL|TX|CA",
  "deduplication_key": "normalized identifier",
  "validation_status": "pending|verified|rejected", "rejection_reason": null,
  "next_action": "research|educational_outreach|nurture|advisor_review|suppress"
}
```
**Never** populate estimated age, net worth, account balance, or health.

---

## 9. Lead magnets & next-step offers (route "hot" intent here)

Instead of pitching, route interested prospects to an education-first, consent-based offer:

| Track | Offer | CTA |
| --- | --- | --- |
| A | "What Does Retirement Income Look Like in `<STATE>`?" income-gap estimate | "Estimate your monthly retirement income gap" |
| A | Pension lump-sum vs. monthly decision checklist | "Get the pension decision checklist" |
| B | "What Could Long-Term Care Cost in `<STATE>`?" local cost guide | "Download the `<STATE>` Care Cost Guide" |
| B | "Traditional vs. Hybrid LTC: 12 Questions to Compare" (product-neutral) | "Get the comparison checklist" |
| B | "Could You Self-Fund Care?" worksheet (non-sensitive inputs only) | "Request a 20-minute funding review" |

Landing pages: single purpose, headline matches the ad/query, ≤5 benefit bullets, short form (first name · email · state · optional "what are you exploring?" · explicit consent checkbox), advisor credibility block, and readable privacy + required insurance/advisory disclosures. Submit ad + page + form + thank-you + follow-up emails together for compliance approval.

---

## 10. Agent system prompt (operating instructions)

> You are Juan Cabezas's **Retirement & Care Intent Signal Agent**. Identify recent, verifiable **public** signals that a person or business may need retirement-income, retirement-account, pension, market-risk, tax-deferral, principal-preservation, or **long-term-care** education. Identify *intent* — never declare a product suitable.
>
> Rules: public sources only; every signal has an active `source_url` + date; quote only what the source states; never guess age/income/assets/health/risk/tax; never identify anonymous users; never invent contact info; capture contact info only when publicly displayed for legitimate business use; reject unverifiable/duplicate/outdated/misleading records; classify Hot/Moderate/Nurture/Rejected; score public intent separately from voluntary qualification; never describe an annuity or LTC policy as risk-free, universally appropriate, or government-guaranteed; state guarantees depend on the issuing insurer and contract terms; route recommendations to a licensed human advisor; respect opt-outs, consent, suppression, and per-state licensing (FL/TX/CA in phase 1); keep a complete audit trail. When evidence is weak, mark **Rejected** rather than filling gaps with assumptions.

---

## 11. Regulatory notes
- **FINRA** applies best-interest obligations to variable and registered index-linked annuity recommendations; **Rule 2330** sets standards for deferred variable-annuity recommendations.
- **FCC/TCPA:** automated calls and commercial texts require proper consent; commercial email must avoid deceptive headers/subjects and provide opt-out (CAN-SPAM).
- **State insurance advertising rules + Google Ads** restrict health/insurance advertising to certified advertisers — confirm certification, disclosures, and landing-page compliance before running paid campaigns.
- Have all consumer-facing materials reviewed under carrier, agency, and state insurance-advertising requirements before publishing.
