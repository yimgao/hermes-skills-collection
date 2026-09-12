---
name: privacy-footprint-cleaner
description: "Take back your personal data from data brokers, search engines, and old accounts — build a target list of the brokers holding your info (Spokeo, Whitepages, BeenVerified, Radaris…), walk through opt-outs in bulk, file Google 'Results about you' + personal-info removals, exercise CCPA/GDPR erasure rights, find forgotten accounts worth deleting, and re-check on a cron because brokers re-list you. Safety-first mode for stalking/harassment victims. Local tracker JSON, no data uploaded."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [security, privacy, data-broker, opt-out, doxxing, pii, gdpr, ccpa, right-to-be-forgotten, account-deletion, digital-footprint, personal-security, stalking]
    related_skills: [password-auditor, phishing-link-inspector, secret-scanner, renewal-reminder, personal-crm, browser-bookmark-cleaner, inbox-triage]
---

# 🕵️ Privacy Footprint Cleaner — 个人隐私足迹清理器

> Your home address, phone number, relatives, and past addresses are probably listed on 30+ people-search sites right now — Spokeo, Whitepages, BeenVerified, Radaris, MyLife, and a long tail of scrapers. This skill turns *"how do I get off these sites?"* into an ordered, tracked, and repeatable campaign: build the broker hit-list, run the opt-outs, file the search-engine removals, exercise your legal erasure rights, kill the old accounts feeding the data, and set a cron to re-check in 90 days — because brokers re-list you.
>
> 你的住址、电话、亲属、旧地址可能正挂在 30+ 个 people-search 网站上。这个 skill 把「怎么让这些网站删掉我」变成一个有顺序、可追踪、可复跑的清理战役。

---

## Overview / 概述

Privacy Footprint Cleaner is a **personal data-removal campaign manager**. Data brokers scrape public records (voter rolls, court filings, property deeds, whitepages) and resell your profile to anyone with $5. Most people never remove it because the process is 30+ separate forms, each with a confirmation loop. This skill front-loads the work: identify who has you, prioritize by exposure, generate the exact opt-out steps, track each request's status, and keep re-checking.

It is **not** a scraper-of-people — it never harvests PII from third parties. It works *for the user on their own data*, and it operates strictly locally: the tracker lives in `~/.hermes/data/privacy/` and nothing is uploaded anywhere.

| Capability | What It Does | How |
|------------|-------------|-----|
| **Exposure triage** | Build the broker hit-list, ranked by how much PII they expose and how easy the opt-out is | Curated broker registry + user-supplied "which sites have me" |
| **Broker opt-out campaign** | Step-by-step opt-out per broker: URL, required inputs, email-verify loop, expected latency | Per-broker playbooks, tracked to completion |
| **Search-engine removal** | File Google "Results about you" + personal-info removal; de-index cached pages | Google removal tools, one row per URL |
| **Legal erasure requests** | CCPA/CPRA (California) and GDPR Art. 15/17 (EU/UK) deletion + access request templates | Ready-to-send email with statutory citations |
| **Zombie account audit** | Find forgotten accounts that leak data, then prioritize deletions | JustDeleteMe-style registry + account inventory |
| **Source lock-down** | Cut off the input streams: email aliases, ad-ID resets, social privacy sweep, data-broker ad opt-outs | DAA/NAI opt-outs, alias plan, permission audit |
| **Safety-first mode** | For stalking / DV / doxxing victims: ordering, no-tip-off rules, PO-box + address-vs-name strategy | Hardened playbook, priority escalation |
| **Drift re-check** | Brokers re-list you in ~60-180 days — cron-driven re-scan + reminder | `hermes cron` + local tracker diff |
| **Local tracker** | Every request, date, status, confirmation ID, next-action date | `~/.hermes/data/privacy/requests.json` |

---

## When to Use

- *"My address shows up on Google when I search my name — get me off these sites"*
- *"Which data brokers have my info?"*
- *"I keep getting spam calls — my number is probably on a people-search site"*
- *"I'm getting divorced / moved / changed my number — clean up my footprint"*
- *"Someone is harassing me and I think they found me through Spokeo"* → **safety-first mode**
- *"File a GDPR / CCPA deletion request for me"*
- *"I want to delete my old accounts — which ones should I kill first?"*
- *"Set a reminder to re-check my data-broker listings in 3 months"*
- *"用中文：帮我查查我的信息在哪些网站上，怎么删掉"* / *"我想做网络隐私清理"*
- *"Is a VPN / alias email / burner number worth it for this?"*
- Any request mentioning **"data broker", "people search", "opt out", "remove my info", "doxxing", "privacy cleanup", "right to be forgotten", "删除我的信息", "隐私足迹", "个人信息泄露"**

**Do NOT use** for check-the-other-person requests ("find info about X"). That's OSINT, not this. If the user wants to remove **their own** data — this skill applies.

---

## Core Workflow

### Step 0: Triage — scope, threat model, and priority

Before touching a single form, establish three things. Ask them tightly (one message, accept "not sure"):

1. **Identity scope** — which PII is exposed? Name (+nicknames, maiden name), current address, past addresses, phone(s), email(s), DOB, relatives, employer.
2. **Threat level** — `routine` (spam prevention), `elevated` (a specific aggressive person, ex, or job-search sensitivity), or `urgent` (stalking, DV, doxxing, active harassment).
3. **Region** — US state matters (California → CCPA/CPRA rights), EU/UK → GDPR rights, other → playbooks only.

If **urgent**, jump straight to **Safety-First Mode** (Step 5) and do *not* post opt-outs that reveal "I am cleaning up" to an abuser. Address exposure first, name exposure second.

Log the profile:

```json
// ~/.hermes/data/privacy/profile.json
{
  "created": "2026-09-11",
  "threat_level": "routine",
  "region": "US-CA",
  "identities": {
    "names": ["Jane Q. Public", "Jane Public-Smith"],
    "phones": ["+1-555-0142"],
    "emails": ["jane@example.com", "jpublic@oldcorp.com"],
    "addresses": {"current": "123 Main St, Springfield", "past": ["45 Oak Ave, Springfield"]},
    "relatives_listed": ["John Public"]
  }
}
```

---

### Step 1: Build the broker hit-list

Start from the curated registry below, then filter to "*which ones actually have me*". Ask the user to search their **full name + city** on Google and paste the people-search hits — that's the ground truth, no scraping required.

**Tier 1 — the big four (highest priority, nearly everyone is listed):**

| Broker | Opt-out URL | Email verify? | Typical latency |
|--------|-------------|---------------|-----------------|
| Spokeo | `https://www.spokeo.com/optout` | No | 24–72 h |
| Whitepages | `https://www.whitepages.com/suppression-requests` | No | 24 h |
| BeenVerified | `https://www.beenverified.com/app/optout/search` | Yes | 24–72 h |
| Radaris | `https://radaris.com/control/privacy` | Yes | 2–7 d |

**Tier 2 — major aggregators & people-search:**

| Broker | Opt-out URL | Notes |
|--------|-------------|-------|
| MyLife | `https://www.mylife.com/ccpa/index.pubview` | US-only flow; harder, keep proof |
| Intelius | `https://www.intelius.com/opt-out/` | Feeds many downstream sites |
| PeopleFinders | `https://www.peoplefinders.com/opt-out` | |
| TruePeopleSearch | `https://www.truepeoplesearch.com/removal` | Fast, no verify |
| FastPeopleSearch | `https://www.fastpeoplesearch.com/removal` | Fast, no verify |
| Nuwber | `https://nuwber.com/removal/link` | |
| PeekYou | `https://www.peekyou.com/about/contact/optout/` | |
| Cyberbackgroundchecks | `https://www.cyberbackgroundchecks.com/removal` | |
| SearchPeopleFree | `https://www.searchpeoplefree.com/opt-out` | |

**Tier 3 — data brokers & marketing data (CCPA/GDPR applies, less visible):**

| Broker | Opt-out URL | Notes |
|--------|-------------|-------|
| Acxiom | `https://isapps.acxiom.com/optout/optout.aspx` | Marketing data giant |
| LexisNexis | `https://optout.lexisnexis.com/` | Public records giant |
| Oracle Data Cloud | `https://www.oracle.com/legal/privacy/` | Opt-out link in policy |
| Epsilon | `https://us.epsilon.com/privacy-policy` | Marketing data |
| CoreLogic | `https://www.corelogic.com/privacy/` | Property data |

**Advertising-ID opt-outs (stop targeted ads, reduce future scraping value):**

| Network | Opt-out URL |
|---------|-------------|
| DAA (AdChoices) | `https://optout.aboutads.info/` |
| NAI | `https://optout.networkadvertising.org/` |
| Google Ads | `https://adssettings.google.com/` |

> ⚠️ **URLs drift.** Brokers rebrand and move opt-out pages constantly. Before pasting a URL to the user, verify it resolves (or hand them the broker name + "search `<broker> opt out`"). Never invent an opt-out URL — mark unverified ones as "search this".

Record each broker that has you:

```json
// ~/.hermes/data/privacy/requests.json  (one entry per broker/URL)
{
  "id": "req-20260911-001",
  "broker": "Spokeo",
  "type": "broker_optout",
  "url": "https://www.spokeo.com/optout",
  "listing_url": "https://www.spokeo.com/Jane-Public/Springfield",
  "status": "pending",            // pending | submitted | email_verify | removed | refused | relisted
  "submitted_on": null,
  "confirm_id": null,
  "followup_on": null,
  "notes": ""
}
```

---

### Step 2: Run the opt-out campaign (batched, tracked)

Process in **tiers**, and within a tier in whatever order the user prefers. For every broker:

1. **Open the opt-out URL** and paste the user's exact `listing_url` when the form asks for the profile link (copying the profile URL is far more reliable than name search).
2. **Capture the confirmation** — most issue a confirm code or require an email click. Copy the code/email into `confirm_id`.
3. **Set `followup_on` = submitted_on + latency + 3 days.** If nothing changed by then → status `relisted`/`refused` and escalate (Step 4).
4. **Update status.** Never leave a request as `submitted` with no `followup_on`.

Reply format after each batch:

```markdown
## Opt-out batch — Tier 1
| Broker | Status | Confirm ID | Follow-up |
|--------|--------|-----------|-----------|
| Spokeo | ✅ submitted | SPK-884211 | 2026-09-15 |
| Whitepages | ✅ submitted | — | 2026-09-14 |
| BeenVerified | ⏳ awaiting email click | — | 2026-09-15 |
| Radaris | ⏳ email verify sent | — | 2026-09-18 |

**4/4 Tier-1 requests filed.** Next: Tier 2 (9 brokers). Say "continue" and I'll walk them one by one.
```

**Bulk-tool option (mention, don't require):** paid services (DeleteMe, Kanary, Incogni, Optery) automate this for $8–15/mo. Recommend only if the user has >15 brokers or no time; note the trade-off (a third party now has your PII — read their privacy policy).

---

### Step 3: Search engines & content removal

Brokers are only half the problem — Google is the front door.

**a) Google "Results about you"** — monitor & request removals:

```text
https://myactivity.google.com/results-about-you
```

Enrolls the user's name/address/phone, surfaces pages containing them, and provides one-click removal requests. Requires being signed into their Google account.

**b) Google personal-info removal** (address, phone, ID numbers, doxxing content):

```text
https://support.google.com/websearch/troubleshooter/9685456
```

**c) De-index a specific page** — two layers:
- **Refresh the cache:** Google Search → find the page → *three-dot menu → Remove result → "Refresh this outdated result"*. Use once the broker page is genuinely gone; removes the stale cached snippet fast.
- **Permanent removal:** only if the page is truly gone or qualifies (Google's policy list). File via the troubleshooter above.

**d) Bing/other engines** — Bing has its own removal flow (`https://www.bing.com/webmasters/tools/contentremoval`); DuckDuckGo/Brave mostly inherit Bing/Google indexes, so once the source is down, they follow.

**e) The source beat** — removing the broker page is pointless if the *underlying* record is public. The real fix is upstream:
- Voter registration → contact county registrar (some states allow confidential voter status).
- Property records → county assessor (some allow a "confidential" mailing address).
- Court records → ask the clerk about expungement/sealing.
Record these as `type: "source_removal"`.

---

### Step 4: Legal rights — CCPA/CPRA & GDPR

When a broker refuses or ignores, escalate with statutory language. **This is the highest-leverage move** — brokers are legally obligated to respond within fixed windows.

| Law | Who | Right | Deadline for them |
|-----|-----|-------|-------------------|
| CCPA / CPRA | California residents | Delete, know, opt out of sale/share | 45 days (+45 extension) |
| GDPR Art. 15 | EU/EEA + UK residents | Access (what they hold) | 1 month |
| GDPR Art. 17 | EU/EEA + UK residents | Erasure ("right to be forgotten") | 1 month |
| Other US states | VA, CO, CT, UT, TX, etc. | Similar deletion/opt-out rights | 45 days |

**Deletion request template (CCPA):**

```text
Subject: CCPA/CPRA Deletion Request — [FULL LEGAL NAME]

To the Privacy Team,

I am a California resident. Pursuant to the California Consumer Privacy Act
as amended by the CPRA (Cal. Civ. Code § 1798.100 et seq.), I request:

1. Deletion of all personal information you maintain about me, including the
   profile at: [LISTING_URL]
2. Disclosure of the categories of sources from which you obtained it
   (§ 1798.110).
3. Opt-out of any sale or sharing of my personal information (§ 1798.120).

Identifying details: Name [..], current city/state [..], phone [..],
email [..]. I can provide a government ID if required for verification.

Please confirm receipt and the deletion within the 45-day statutory window.
If you need an extension, notify me in writing as required.

[FULL NAME]
```

**GDPR erasure template (Art. 17):** swap the citation to *Regulation (EU) 2016/679 Art. 17* and add "*If you claim an Art. 17(3) exemption, state which and why.*" Send to the Data Protection Officer; if ignored 1 month → escalate to the national supervisory authority (e.g. ICO in the UK, CNIL in France, DSK in Germany).

Track every legal request in `requests.json` with `type: "legal_erasure"`, `deadline`, and the statutory basis. **Always keep the sent copy** (self-deliver or CC a second address) as evidence.

---

### Step 5: Safety-First Mode (stalking / DV / doxxing)

If `threat_level: urgent`, the usual playbook can *increase* risk. Follow these hard rules:

1. **Address first, name second.** A removed phone number is worth more than a removed name. Prioritize anything exposing the *current physical address*, workplace, or children's schools.
2. **Never post an opt-out that notifies the abuser.** Some brokers email the profile being edited. Use a **safe email** (not one the abuser knows) and do **not** change listings in a way that pings the other party.
3. **Change the inputs, not just the outputs.** Get a new phone number, a PO box / virtual mailbox (UPS Store, iPostal1), and a forwarding-only address. Brokers scrape *current* records; if the current record is a PO box, the old street never re-populates.
4. **Use a confidential/protective address program** where it exists (e.g. many US states' Safe at Home / Address Confidentiality Program for DV survivors).
5. **Freeze credit** (Equifax/Experian/TransUnion) and lock your IRS/SSA accounts — doxxing often precedes identity theft.
6. **Route to authorities when warranted:** local police, a domestic-violence hotline (US: 1-800-799-7233), FBI IC3 for cyberstalking threats.
7. **Documentation is evidence.** Keep a dated log of every listing found; it supports protective orders.

Reply tone here is calm and procedural — prioritize, don't overwhelm. Offer the 3 highest-impact actions first, not the full 30-broker list.

---

### Step 6: Cut the input streams

Stopping the leak matters more than mopping it up.

| Vector | Action |
|--------|--------|
| **Email** | Move to aliases: Firefox Relay, Apple "Hide My Email", SimpleLogin, DuckDuckGo aliases. One alias per service. Kill the master address' public exposure. |
| **Phone** | Google Voice / burner for sign-ups; port the real number if it's badly burned. |
| **Social** | Audit privacy: friends-only posts, remove DOB/phone/employer from bio, disable "searchable by phone/email", lock down tagged photos. |
| **Permissions** | Review app location/contacts/mic permissions (iOS: Settings → Privacy & Security; Android: Privacy dashboard). Revoke anything not needed *right now*. |
| **Old accounts** | Inventory via password manager + email search, then delete the zombies (Step 7). |
| **Browser** | Reset ad ID, clear third-party cookies, install uBlock Origin; consider a privacy browser (Brave/Firefox) for sensitive search. |
| **Public records** | Voter-roll confidentiality, assessor mailing-address privacy, court sealing (Step 3e). |
| **Data-broker ad opt-outs** | DAA + NAI + Google Ads settings — reduces how valuable you are to re-scrape. |

---

### Step 7: Zombie account audit & deletion

Every old account is a data leak waiting to happen. Build the inventory, then prioritize:

**Find them:**
- Email search: `from:(no-reply) OR subject:(welcome) older_than:2y` in Gmail search — surfaces forgotten signups.
- Password manager export → list of all saved sites.
- Breach check: `https://haveibeenpwned.com` → which services leaked you.

**Prioritize deletion by:** (1) holds payment/ID data + (2) inactive >2 years + (3) no longer needed. Starting points:
- **JustDeleteMe registry:** `https://justdeleteme.xyz` — direct delete links + difficulty rating per service.
- **AccountKiller:** `https://www.accountkiller.com`.

For services with no self-serve delete, send a deletion email citing the same CCPA/GDPR language as Step 4. Track each as `type: "account_deletion"`.

---

### Step 8: Verify, then schedule the re-check

**Verify removals:** re-search the name + city on Google and each Tier-1 broker; a listing is only `removed` when the page 404s or shows no match. Update statuses honestly — no wishful `removed`.

**Schedule the drift re-check** — brokers re-list within 60–180 days (they re-scrape public records):

```bash
hermes cron add "privacy-footprint-recheck" \
  --schedule "0 9 1 */3 *" \
  --prompt "Re-check my data-broker listings from ~/.hermes/data/privacy/requests.json: for every broker marked 'removed' more than 90 days ago, search my name + city again and report which relisted. Also flag any request still 'pending' past its followup_on." \
  --skill privacy-footprint-cleaner
```

Every quarter: re-run Tier 1 (fast), spot-check Tier 2, and re-file anything `relisted`. Removal is a **subscription, not a one-time task** — say so explicitly, because users expect it to be permanent.

---

## Example Invocations

### Example 1 — Routine removal (US, no threat)

> **User:** I searched my name and my address is on Spokeo and Whitepages. How do I get it off?

> **Hermes:** Let's clear it, and then check whether other brokers have you too — I'd guess 10–20 do.
>
> Quick triage: is this just spam prevention, or is there a specific person you're worried about? And what state are you in (affects your legal options)?
>
> **User:** Just spam. I'm in California. No one specific.

> **Hermes:**
> ```
> Threat: routine · Region: US-CA (CCPA + CPRA apply) · Priority: Tier 1
> ```
> Two confirmed, but let's not stop at two. Search your full name + city on Google and paste me any people-search results — that's your real hit-list.
>
> Meanwhile, start Tier 1 now. Do these in order and paste each confirmation code back to me:
>
> 1. **Spokeo** — https://www.spokeo.com/optout → paste your profile URL, submit. No email verify. (~24–72 h)
> 2. **Whitepages** — https://www.whitepages.com/suppression-requests → paste profile URL, submit. (~24 h)
> 3. **BeenVerified** — https://www.beenverified.com/app/optout/search → you'll get a click-to-confirm email.
> 4. **Radaris** — https://radaris.com/control/privacy → email verify.
>
> I'll track all four and nudge you on the follow-up dates. Say "continue" when you've done Tier 1 and I'll walk Tier 2 (TruePeopleSearch, FastPeopleSearch, Nuwber, Intelius…).

### Example 2 — Urgent / safety-first (stalking)

> **User:** My ex found my new apartment. I think it's from one of those people-search sites. I'm scared.

> **Hermes:** I'm sorry — let's fix the exposure, fastest and safest first. Two rules before anything else:
>
> 1. **We don't post anything that notifies him.** Use an email address he doesn't know for every form. If a site wants to email the profile, we stop and use a different route.
> 2. **Address first, name second.** A removed phone number is worth more than a removed name here.
>
> Your 3 highest-impact actions, in order:
>
> **1. Cut the current record now (highest impact).** If your *current* address is exposed, changing the underlying record stops re-population. Get a virtual mailbox / PO box (UPS Store, iPostal1) and a forwarding address; update your bank, DMV, insurance, and voter registration to the box. Brokers scrape current records — a PO box means the street never comes back.
>
> **2. Check your state's Address Confidentiality Program.** Many states run a Safe at Home program for survivors — they give you a substitute legal address that flows into public records. Want me to look up yours?
>
> **3. Remove the live listings, quietly.** Start with the broker where he likely found you. Paste me the listing URL (not the broker home page) and I'll give you the exact quiet-opt-out path + safe input fields.
>
> Also do these today, they're independent of the brokers: **freeze your credit** at all three bureaus, and lock your IRS and SSA accounts — doxxing often precedes identity theft.
>
> If you haven't already, US DV hotline 1-800-799-7233 can help with the ACP paperwork and safety planning. You're not doing anything wrong here — this is a known, fixable leak.
>
> I'll keep a dated log of every listing we find — it's useful evidence if you pursue a protective order.

### Example 3 — Legal escalation

> **User:** BeenVerified said they removed me but the profile is still up 2 weeks later. I'm in California.

> **Hermes:** Then we stop asking nicely and use the statute. As a California resident you have a **CPRA deletion right**, and they have **45 days** by law. Here's the email — send it from a safe address and keep a copy:

```text
Subject: CCPA/CPRA Deletion Request — [FULL LEGAL NAME]

To BeenVerified Privacy Team,

I am a California resident. Pursuant to the California Consumer Privacy Act
as amended by the CPRA (Cal. Civ. Code § 1798.100 et seq.), I request:

1. Deletion of all personal information you maintain about me, including
   the profile at: [LISTING_URL]
2. Disclosure of the categories and specific sources of this information
   (§ 1798.110).
3. Opt-out of the sale or sharing of my personal information (§ 1798.120).

Identifying details: [name / city / phone / email]. I can provide ID if
required for verification.

Please confirm receipt and deletion within the 45-day statutory window,
and notify me in writing if you take an extension.

[FULL NAME]
```

> Send it, reply with the confirmation ID, and I'll set a 45-day deadline in the tracker. If they blow it, the next step is a complaint to the California Attorney General and the CPPA — both accept online submissions. I'll draft that too if needed.

---

## Common Pitfalls

| Problem | Why it happens | Solution |
|---------|----------------|----------|
| **Removed listing reappears in 2–6 months** | Brokers re-scrape public records on a cycle; removal isn't permanent | Expected — build the quarterly re-check cron (Step 8). Don't treat one removal as done. |
| **Opt-out URL 404s or redirects to a sales page** | Brokers rebrand/rotate pages constantly | Never hardcode trust in a URL. Verify it resolves; if not, hand the user "search `<broker> opt out`" and mark unverified. |
| **Removing the broker page but the record is still public** | The broker scraped a public source (voter roll, deed, court record) | Go upstream: voter confidentiality, assessor mailing-address privacy, court sealing (Step 3e). |
| **User posts opt-out that alerts a harasser** | Some brokers email the profile being edited | Safety-first rule #2 — safe email, no notify-triggering flows. Confirm the flow before submitting. |
| **Name matches a relative / wrong person** | Common names collide in people-search databases | Always supply the exact `listing_url`, not just name+city. Confirm the listing is truly theirs before removal. |
| **Legal request gets a demand for government ID** | Brokers verify identity before deleting | That's normal and legitimate (they must prevent malicious deletion). Provide ID only to the broker's official portal; never email ID to an unofficial address. |
| **User expects a single "delete me everywhere" button** | Marketing promises instant privacy | Set expectations: it's 20–40 separate requests, weeks of latency, and a permanent maintenance loop. |
| **Third-party removal service wants full PII** | You now trust *another* company with everything | Read their privacy policy; for high threat levels, manual is safer. Offer both, warn on trade-off. |
| **Removing all social media hurts the user** | Over-cleaning breaks job search / social ties | Don't delete what they need — lock it down (privacy settings) instead. Ask "keep or kill?" per account. |

---

## Verification Checklist

- [ ] Threat level and region captured (`routine` / `elevated` / `urgent`) before actions
- [ ] For `urgent`: safety-first mode applied — address first, no notify-triggering opt-outs, safe contact address
- [ ] Broker hit-list built from actual Google results (name + city), not assumptions
- [ ] Tier-1 brokers all filed; Tier-2+ queued
- [ ] Every request has a `submitted_on` and, if not yet resolved, a `followup_on`
- [ ] Confirmation IDs captured where issued
- [ ] Google "Results about you" enrolled + personal-info removal filed for exposed pages
- [ ] CCPA/GDPR deletion sent to every refusing broker, with statutory citation and deadline tracked
- [ ] Input streams addressed (aliases / phone / social privacy / app permissions / public records)
- [ ] Credit + IRS/SSA locked (at minimum for `elevated`/`urgent`)
- [ ] Zombie accounts inventoried and prioritized via JustDeleteMe
- [ ] Removals *verified* by re-searching; no wishful `removed` statuses
- [ ] Quarterly re-check cron scheduled
- [ ] Nothing uploaded to a third party; tracker local under `~/.hermes/data/privacy/`

---

## Data Sources & Accuracy

- **Broker registry** — the URLs above are the well-known opt-out paths as of writing. They are **not guaranteed permanent**: verify each resolves before handing it to a user; if it fails, fall back to "search `<broker> opt out`". Never fabricate an opt-out URL.
- **Legal citations** — CCPA/CPRA (`Cal. Civ. Code § 1798.100 et seq.`), GDPR (`Regulation (EU) 2016/679`, Art. 15/16/17). Templates cite statutes for leverage, but **this is not legal advice** — for active litigation or safety emergencies, defer to a lawyer / hotline / authorities.
- **Google tools** — "Results about you" and the personal-info troubleshooter are official Google flows; their URLs can also change, so verify before pasting.
- **Breach/account data** — HaveIBeenPwned (k-anonymity, no PII sent), JustDeleteMe/AccountKiller (community registries).
- **Threat/identity data** — all user-supplied and **local**: `~/.hermes/data/privacy/{profile.json, requests.json}`. Nothing is uploaded, ever. This skill never harvests third-party PII.
- **Latency figures** are typical, not guarantees — brokers vary and may ignore requests. Track against the statutory deadline, not the courtesy one.
- **Safety resources** — US DV hotline 1-800-799-7233; FBI IC3 (`https://ic3.gov`) for cyberstalking; state Address Confidentiality Programs for survivors.
