---
name: personal-crm
description: "Track the people in your life — contacts, meetings, follow-ups, relationship health. Add a contact after meeting someone, log interactions, get reminded to follow up. All data local in JSON, zero cloud dependency."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, crm, networking, relationships, contacts, follow-up, productivity, personal-knowledge]
    related_skills: [habit-tracker, personal-expense-tracker, meeting-minutes-generator, contact-book]
---

# 🤝 Personal CRM — 人脉关系管理

> Track the people who matter. Add a contact after a coffee chat, log what you talked about, get reminded to follow up — all in a private local JSON file. 记录你认识的人，回忆每次对话，及时跟进维系关系。零云端依赖，数据完全本地。

---

## Overview

Most people forget 80% of the people they meet within a week. A Personal CRM fixes this: it turns Hermes into a private relationship manager that remembers names, context, last touchpoint, and next action for every contact in your network — whether it's a founder you met at a meetup, a recruiter from last year, or a college friend you keep losing touch with.

Unlike enterprise CRMs (Salesforce, HubSpot), this skill is **personal, private, and local**. No accounts, no cloud sync, no telemetry. Your network is yours.

| Capability | Description |
|------------|-------------|
| **Add contact** | Capture name, role, company, channels (email/phone/WeChat/LinkedIn) |
| **Log interaction** | Record meeting/call/message with date, summary, sentiment |
| **Schedule follow-up** | Set a "remind me in N days" reminder; Hermes surfaces it on demand |
| **Relationship health** | Score each contact by recency, frequency, and depth |
| **Search & filter** | Find by name, company, tag, last-touched-date |
| **Today's follow-ups** | Quick list of who you should ping today |
| **Network statistics** | Total contacts, contacts added this month, dormant relationships |
| **Export** | Dump to CSV/Markdown for backup or migration |
| **Local-only storage** | All data in `~/.hermes/personal-crm/contacts.json` |

---

## When to Use

- *"I just met a VC at a meetup — add her to my CRM"*
- *"I had coffee with Alex yesterday, we talked about his new startup"*
- *"Who in my network works at Stripe?"*
- *"Who haven't I contacted in over 6 months?"*
- *"Show me my follow-ups for today"*
- *"I need to reach out to 3 people this week — pick the most important ones"*
- *"Export my contacts to CSV"*
- *"Set a reminder to ping Jordan in 2 weeks"*
- *"Mark the relationship with Mom as 'family' — don't suggest her in follow-up lists"*
- *"How many new contacts did I add this month?"*

---

## Core Workflow

### Step 1: Initialize the Local Database

The first time the user mentions a CRM/contact/relationship, ensure the data directory and file exist:

```bash
mkdir -p ~/.hermes/personal-crm
```

**`contacts.json` schema:**

```json
{
  "contacts": [
    {
      "id": "ct_001",
      "name": "Alex Chen",
      "aliases": ["Alex", "陈昊"],
      "role": "Founder & CEO",
      "company": "Acme AI",
      "tags": ["founder", "AI", "investor-warm"],
      "channels": {
        "email": "alex@acme.ai",
        "phone": "+1-555-0100",
        "wechat": "alex_chen_88",
        "linkedin": "linkedin.com/in/alexchen",
        "twitter": "@alexchen"
      },
      "how_we_met": "Met at the AI Founders meetup, July 2026",
      "interactions": [
        {
          "id": "int_001",
          "date": "2026-07-07",
          "type": "in-person",
          "summary": "30 min coffee at Blue Bottle. He just closed seed round. Looking for design partners in fintech. Asked me to intro if I know anyone.",
          "action_items": [
            {"text": "Intro Alex to my friend at Plaid", "due": "2026-07-14", "done": false}
          ],
          "sentiment": "warm"
        }
      ],
      "follow_up": {
        "next_date": "2026-07-21",
        "cadence_days": 30,
        "note": "Follow up after intro to Plaid friend"
      },
      "relationship": "professional",
      "tier": "A",
      "created_at": "2026-07-07T15:30:00Z",
      "updated_at": "2026-07-07T16:00:00Z"
    }
  ],
  "metadata": {
    "version": 1,
    "created_at": "2026-07-07T15:00:00Z",
    "total_contacts": 1
  }
}
```

**Field guide:**

| Field | Purpose | Example |
|-------|---------|---------|
| `tier` | A (close/important) / B (regular) / C (acquaintance) | `"A"` |
| `relationship` | `professional` / `personal` / `family` / `mentor` / `investor` | `"professional"` |
| `tags` | Free-form labels for filtering | `["recruiter", "AI", "warm"]` |
| `interactions[].type` | `in-person` / `call` / `message` / `email` / `event` | `"call"` |
| `interactions[].sentiment` | `warm` / `neutral` / `cold` | `"warm"` |
| `follow_up.cadence_days` | How often to stay in touch (days) | `30` |
| `aliases` | Other names/nicknames for search | `["陈昊", "AC"]` |

### Step 2: Add a New Contact

Parse the user's natural language into a structured contact. Always confirm ambiguous fields.

**User says:** *"I just met Sarah Wong, she's a PM at Notion. We chatted at a conference. Her email is sarah.wong@notion.so"*

**Agent does:**

```python
import json, uuid
from datetime import datetime, timezone
from pathlib import Path

DB = Path.home() / ".hermes/personal-crm/contacts.json"

def load():
    if not DB.exists():
        return {"contacts": [], "metadata": {"version": 1, "created_at": datetime.now(timezone.utc).isoformat(), "total_contacts": 0}}
    return json.loads(DB.read_text())

def save(data):
    data["metadata"]["total_contacts"] = len(data["contacts"])
    data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
    DB.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def add_contact(name, role=None, company=None, channels=None, how_we_met=None,
                tags=None, relationship="professional", tier="B", cadence_days=90):
    data = load()
    contact = {
        "id": f"ct_{uuid.uuid4().hex[:8]}",
        "name": name,
        "aliases": [],
        "role": role,
        "company": company,
        "tags": tags or [],
        "channels": channels or {},
        "how_we_met": how_we_met,
        "interactions": [],
        "follow_up": {
            "next_date": datetime.now(timezone.utc).date().isoformat(),
            "cadence_days": cadence_days,
            "note": ""
        },
        "relationship": relationship,
        "tier": tier,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    data["contacts"].append(contact)
    save(data)
    return contact["id"]

# Example call:
# add_contact(
#     name="Sarah Wong",
#     role="PM",
#     company="Notion",
#     channels={"email": "sarah.wong@notion.so"},
#     how_we_met="Chatted at the Config conference, July 2026",
#     tags=["PM", "AI-tools"],
#     tier="A",
#     cadence_days=60
# )
```

**Confirmation pattern:** Always echo back the parsed contact and ask the user to confirm before saving — names, emails, and company names are easy to mis-hear.

```
[DRAFT] New contact — please confirm:
  Name:     Sarah Wong
  Role:     PM
  Company:  Notion
  Email:    sarah.wong@notion.so
  Met at:   Config conference, July 2026
  Tags:     PM, AI-tools
  Tier:     A
Save? (y/n)
```

### Step 3: Log an Interaction

Whenever the user describes meeting/calling/messaging a contact, append an `interactions` entry.

**User says:** *"I had a 30-min coffee with Alex Chen today. He's closing his seed round next month and asked if I know any fintech design partners."*

**Agent does:**

```python
def log_interaction(contact_id, type_, summary, action_items=None, sentiment="warm"):
    data = load()
    contact = next((c for c in data["contacts"] if c["id"] == contact_id), None)
    if not contact:
        return None
    interaction = {
        "id": f"int_{uuid.uuid4().hex[:8]}",
        "date": datetime.now(timezone.utc).date().isoformat(),
        "type": type_,
        "summary": summary,
        "action_items": action_items or [],
        "sentiment": sentiment,
    }
    contact["interactions"].append(interaction)
    contact["updated_at"] = datetime.now(timezone.utc).isoformat()

    # Auto-advance next follow-up
    cadence = contact.get("follow_up", {}).get("cadence_days", 90)
    next_date = datetime.now(timezone.utc).date() + timedelta(days=cadence)
    contact["follow_up"]["next_date"] = next_date.isoformat()

    save(data)
    return interaction["id"]

# Action items parsed from the user's summary:
# [
#   {"text": "Intro Alex to my friend at Plaid", "due": "2026-07-14", "done": false}
# ]
```

**Auto-extract action items:** If the user's summary contains phrases like *"asked me to"*, *"I should"*, *"remind me to"*, *"need to"* — surface them as action items and confirm.

### Step 4: Set & Check Follow-up Reminders

**Set a follow-up:**

```python
from datetime import datetime, timedelta, timezone

def set_follow_up(contact_id, days_from_now, note=""):
    data = load()
    contact = next(c for c in data["contacts"] if c["id"] == contact_id)
    contact["follow_up"]["next_date"] = (
        datetime.now(timezone.utc).date() + timedelta(days=days_from_now)
    ).isoformat()
    contact["follow_up"]["note"] = note
    save(data)
```

**List today's follow-ups (the most common daily check):**

```python
def todays_follow_ups():
    data = load()
    today = datetime.now(timezone.utc).date().isoformat()
    overdue, today_, upcoming = [], [], []
    horizon = (datetime.now(timezone.utc).date() + timedelta(days=7)).isoformat()

    for c in data["contacts"]:
        next_date = c.get("follow_up", {}).get("next_date")
        if not next_date:
            continue
        if next_date < today:
            overdue.append(c)
        elif next_date == today:
            today_.append(c)
        elif next_date <= horizon:
            upcoming.append(c)
    return overdue, today_, upcoming

# Pretty print:
# === OVERDUE (3) ===
#   - Alex Chen (A) — last touched 47 days ago, follow-up was due 2026-06-20
#     Note: "Follow up after intro to Plaid friend"
#   ...
# === TODAY (1) ===
#   - Sarah Wong (A) — Config conference lead
# === NEXT 7 DAYS (2) ===
#   - ...
```

### Step 5: Search, Filter, and Network Stats

**Search by name/alias/company/tag:**

```python
def search(query):
    q = query.lower()
    data = load()
    results = []
    for c in data["contacts"]:
        haystack = " ".join([
            c["name"], " ".join(c.get("aliases", [])),
            c.get("company", "") or "", c.get("role", "") or "",
            " ".join(c.get("tags", []))
        ]).lower()
        if q in haystack:
            results.append(c)
    return results

# Examples:
# search("stripe")  → all contacts at Stripe
# search("founder") → all contacts tagged "founder"
# search("alex")    → matches Alex Chen, Alex Wang, etc.
```

**Filter dormant contacts (haven't touched in N days):**

```python
from datetime import date

def dormant(days=180):
    data = load()
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    return [c for c in data["contacts"]
            if not c["interactions"] or c["interactions"][-1]["date"] < cutoff]

# dormant(180) → contacts you haven't spoken to in 6+ months
```

**Network statistics:**

```python
def stats():
    data = load()
    contacts = data["contacts"]
    now = date.today()
    this_month = now.replace(day=1).isoformat()

    by_tier = {"A": 0, "B": 0, "C": 0}
    by_relationship = {}
    new_this_month = 0
    dormant_90 = 0

    for c in contacts:
        by_tier[c.get("tier", "B")] = by_tier.get(c.get("tier", "B"), 0) + 1
        rel = c.get("relationship", "other")
        by_relationship[rel] = by_relationship.get(rel, 0) + 1
        if c["created_at"][:7] == this_month[:7]:
            new_this_month += 1
        last = c["interactions"][-1]["date"] if c["interactions"] else c["created_at"][:10]
        if last < (now - timedelta(days=90)).isoformat():
            dormant_90 += 1

    return {
        "total": len(contacts),
        "by_tier": by_tier,
        "by_relationship": by_relationship,
        "new_this_month": new_this_month,
        "dormant_90_days": dormant_90,
    }
```

**Sample stats output:**

```
[STATS] Network: 87 contacts · A=12 B=53 C=22
  By relationship: professional=64 personal=18 family=5
  New this month:  4
  Dormant (90d+):  23
  Follow-ups today: 3
```

### Step 6: Export & Backup

**Export to CSV** (for backup, import into Google Contacts, etc.):

```python
import csv

def export_csv(path="~/.hermes/personal-crm/export.csv"):
    data = load()
    rows = []
    for c in data["contacts"]:
        rows.append({
            "name": c["name"],
            "role": c.get("role", ""),
            "company": c.get("company", ""),
            "email": c.get("channels", {}).get("email", ""),
            "phone": c.get("channels", {}).get("phone", ""),
            "linkedin": c.get("channels", {}).get("linkedin", ""),
            "tags": ",".join(c.get("tags", [])),
            "tier": c.get("tier", ""),
            "last_touched": c["interactions"][-1]["date"] if c["interactions"] else "",
            "next_follow_up": c.get("follow_up", {}).get("next_date", ""),
        })
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path
```

**Export to Markdown** (human-readable backup):

```python
def export_markdown(path="~/.hermes/personal-crm/export.md"):
    data = load()
    lines = [f"# Personal CRM — {len(data['contacts'])} contacts\n"]
    for c in sorted(data["contacts"], key=lambda x: x["name"]):
        lines.append(f"## {c['name']}")
        if c.get("role") or c.get("company"):
            lines.append(f"**{c.get('role', '')}** at **{c.get('company', '')}**")
        if c.get("channels", {}).get("email"):
            lines.append(f"- Email: {c['channels']['email']}")
        if c.get("channels", {}).get("linkedin"):
            lines.append(f"- LinkedIn: {c['channels']['linkedin']}")
        if c.get("tags"):
            lines.append(f"- Tags: {', '.join(c['tags'])}")
        if c.get("how_we_met"):
            lines.append(f"\n> Met: {c['how_we_met']}\n")
        if c["interactions"]:
            lines.append("\n### Recent interactions\n")
            for i in reversed(c["interactions"][-5:]):
                lines.append(f"- **{i['date']}** ({i['type']}): {i['summary']}")
        lines.append("\n---\n")
    Path(path).write_text("\n".join(lines))
    return path
```

### Step 7: Privacy & Local-Only Discipline

**Hard rules — never violate:**

1. **Never send contacts to any external API** without explicit user confirmation. Reading the file to summarize is fine; uploading it is not.
2. **No cloud backup** by default. If the user wants backup, suggest `cp ~/.hermes/personal-crm ~/Dropbox/PersonalCRM/` or a cron rsync to their own server.
3. **Encryption at rest** is the user's responsibility. Recommend: `gpg --symmetric contacts.json` before putting it in cloud storage.
4. **PII handling:** When the user mentions a contact's medical info, financial info, or anything sensitive, store it but **never** include it in summaries, exports, or follow-up suggestions unless the user explicitly asks.
5. **Family contacts (`relationship=family`)** are excluded from dormant/network-stat nudges by default — a CRM is for *active* relationship maintenance, not guilt.

---

## Example Invocations

### Example 1: Adding a Contact from a Conference

**User:** *"I just met Priya Patel at the AI Engineer Summit. She's a research scientist at DeepMind, and we talked about her work on chain-of-thought reasoning. Her email is priya.patel@deepmind.com. Add her to my CRM as a high-priority contact."*

**Agent:**

```
[PARSE] Extracting contact details from message...
[DRAFT] New contact:
  Name:     Priya Patel
  Role:     Research Scientist
  Company:  DeepMind
  Email:    priya.patel@deepmind.com
  How we met: AI Engineer Summit, July 2026
  Tags:     [AI, research, summit-2026]
  Tier:     A (you said high-priority)
  Follow-up: 30 days
[CONFIRM] Save to ~/.hermes/personal-crm/contacts.json? (y/n/edit)
```

After `y`:

```
[OK] Saved contact ct_018 — Priya Patel
[NOTE] Reminder: follow up with Priya around 2026-08-07
```

### Example 2: Logging a Coffee Chat and Getting a Follow-up Plan

**User:** *"I had coffee with Alex Chen yesterday. He just closed his seed round. He's looking for design partners in fintech — I said I'd intro him to my friend at Plaid."*

**Agent:**

```
[FOUND] Alex Chen (ct_001), last interaction 2026-06-12
[PARSE] Detected action item: "Intro Alex to Plaid friend"
[DRAFT] New interaction log:
  Date:      2026-07-07
  Type:      in-person (coffee)
  Summary:   Just closed seed round. Looking for design partners in fintech.
  Action:    Intro Alex to my friend at Plaid (due 2026-07-14)
  Sentiment: warm
[CONFIRM] Save? (y/n)

> y

[OK] Logged interaction int_023
[OK] Next follow-up with Alex: 2026-08-06 (30 days from today)
[REMIND] I'll surface this on 2026-07-14 to remind you about the Plaid intro.
```

### Example 3: Daily Check — Who to Ping Today

**User:** *"Show me my follow-ups for today"*

**Agent:**

```
[FOLLOW-UPS] 2026-07-08

  OVERDUE (2):
    1. Alex Chen (A) — was due 2026-06-20, 18 days late
       Last: "Just closed seed round..."
       Note: "Follow up after Plaid intro"
    2. Jordan Lee (B) — was due 2026-07-05, 3 days late
       Last: "Switching jobs to Anthropic..."

  TODAY (1):
    3. Sarah Wong (A)
       Note: "Config conference lead"

  NEXT 7 DAYS (2):
    4. Maya Singh (A) — 2026-07-12
    5. Tom Wright (B) — 2026-07-14

  Suggested actions:
    - Send a quick "how's the Plaid intro going?" to Alex
    - DM Sarah on LinkedIn re: AI tools chat
    - Text Jordan to congratulate on Anthropic move
```

### Example 4: Reconnecting with Dormant Contacts

**User:** *"Who in my network haven't I talked to in over 6 months? I want to do a reconnection pass."*

**Agent:**

```
[DORMANT] 23 contacts not touched in 180+ days:

  A-tier (5):
    - David Kim (Stripe) — last: 2025-11-04, 247 days
    - Lisa Park (Sequoia) — last: 2025-12-12, 209 days
    - Marcus Johnson (founder) — last: 2025-10-22, 260 days
    - ...

  B-tier (18):
    - ...

[SUGGEST] Reconnection message templates:
  1. "Hey [name], it's been a while — saw [recent thing about them]..."
  2. "Hi [name], randomly thought of you — how's [their company] going?"
  3. "Long time no talk. I'm [doing X] and would love your take on [Y]."

Want me to draft personalized reconnection messages for your top 5 dormant A-tier contacts?
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Contact added with wrong name spelling** | Always echo back the parsed name in confirmation. Chinese pinyin + characters both work; ask the user which to store. |
| 2 | **User says "I met someone" without enough detail** | Ask 1–3 specific questions (role, company, how-met) before saving. Don't invent details. |
| 3 | **Duplicate contacts (Alex Chen vs Alex C.)** | On add, run `search()` first and warn: *"You already have 'Alex Chen' (ct_001). Is this the same person? (y/merge/new)"* |
| 4 | **Timezone confusion in interaction dates** | Always store dates in ISO format (`YYYY-MM-DD`) and convert from user's locale. Confirm "today" = user's local today. |
| 5 | **Sentiment misclassified** | Don't infer sentiment from text. If user doesn't say "warm/cold/neutral", default to `"neutral"` and let them edit. |
| 6 | **Action items forgotten** | When parsing an interaction, look for keywords: *"asked me to"*, *"I should"*, *"need to"*, *"remind me to"*, *"by Friday"*. Surface as action items. |
| 7 | **Tier creep (everything becomes A)** | Tier should reflect strategic value, not likeability. Periodic review: *"You have 24 A-tier contacts — is that realistic?"* |
| 8 | **Dormant list is overwhelming (200+ contacts)** | Filter by tier first (show only A, then B). Allow `dormant(180, tier="A")`. |
| 9 | **Exported CSV has weird characters** | Use `encoding="utf-8-sig"` (with BOM) for Excel compatibility, and quote fields with commas. |
| 10 | **Accidentally storing secrets (API keys, passwords)** | If a channel value contains `sk-`, `ghp_`, or looks like a credential, refuse to save and warn the user. |
| 11 | **Family contacts triggering "overdue" guilt** | Filter out `relationship=family` from follow-up suggestions by default. |
| 12 | **JSON file corruption after a crash** | Keep one backup: `cp contacts.json contacts.json.bak` before any bulk edit. Use atomic writes: write to `.tmp` then `mv` to `contacts.json`. |
| 13 | **Mixing up professional and personal contacts in search** | Add `relationship` filter to search: `search("stripe", relationship="professional")` |
| 14 | **Follow-up cadence not matching reality** | On every interaction log, ask: *"When should I remind you next? (default 30d for A, 90d for B, 180d for C)"* |
| 15 | **Stale `next_date` after long absence** | When logging a new interaction, automatically reset `next_date` to `today + cadence_days`. Don't let stale follow-ups pile up. |

---

## Verification Checklist

Before claiming the skill is working end-to-end, confirm:

- [ ] `~/.hermes/personal-crm/contacts.json` exists and is valid JSON
- [ ] Adding a contact via natural language works, with confirmation step
- [ ] Logging an interaction appends to the correct contact, with timestamp and summary
- [ ] Action items are auto-extracted from phrases like "I should" / "remind me to"
- [ ] "Today's follow-ups" command lists overdue, today, and next-7-days correctly
- [ ] `dormant(180)` returns contacts whose last interaction is 180+ days ago
- [ ] Search by name, alias, company, and tag all work
- [ ] Stats command reports total, by-tier, by-relationship, new-this-month, dormant count
- [ ] CSV export opens in Excel/Numbers without encoding issues
- [ ] Markdown export produces a human-readable file
- [ ] No contact data leaves the local machine
- [ ] Family contacts are excluded from follow-up nudges
- [ ] Duplicate detection warns before creating a near-identical contact
- [ ] Atomic writes (`.tmp` + `mv`) prevent corruption on crash
- [ ] Credentials (API keys, tokens) are rejected from channel fields

---

## Data Sources & Accuracy

**Data sources used by this skill:**

| Source | What it provides | Accuracy |
|--------|------------------|----------|
| **User input (natural language)** | Contact details, interactions, follow-ups | Source of truth — but may have typos, misheard names. Always confirm. |
| **`~/.hermes/personal-crm/contacts.json`** | All persisted data | Local file, accuracy = user's diligence in keeping it updated |
| **System date** (`date` command, `datetime.now()`) | "Today", interaction timestamps, follow-up dates | Trust system clock. Cross-timezone users should set `TZ` env var. |

**What this skill does NOT do:**

- ❌ Does not enrich contacts with LinkedIn/email lookup data (privacy)
- ❌ Does not sync to cloud (intentional — local-only)
- ❌ Does not send emails/messages on the user's behalf (would require explicit send tools)
- ❌ Does not infer sentiment, intent, or relationship value beyond what the user states
- ❌ Does not deduplicate across multiple JSON files (one CRM = one file)

**Accuracy discipline:**

- Never auto-correct a name. *"Alex"* ≠ *"Alex Chen"* — ask.
- Never merge two contacts silently. Always confirm.
- Never infer email/phone from a name (e.g., don't guess `firstname.lastname@company.com`).
- Always preserve original spelling in `aliases` so the user can search by any name they've used.

**Storage limits:** JSON file gets slow above ~10,000 contacts. At that scale, suggest migrating to SQLite (the same `add_contact` / `search` / `log_interaction` API can be backed by SQLite without changing the skill workflow).
