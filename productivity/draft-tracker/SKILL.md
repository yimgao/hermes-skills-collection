---
name: draft-tracker
description: "Never lose a half-written email, blog post, LinkedIn DM, or idea again — capture drafts-in-progress from chat, surface them when you're back at the keyboard, set stale-draft alerts, and finish or discard in 30 seconds. Pairs with daily-shutdown, daily-briefing, inbox-triage, message-tone-adjuster."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, drafts, capture, writing, ideas, journaling, gtd, knowledge, follow-up, mvp, blocks, zero-friction]
    related_skills: [daily-shutdown, daily-briefing, inbox-triage, message-tone-adjuster, weekly-review, decision-journal, personal-crm, standup-status-updater]
---

# 🪶 Draft Tracker — 别让半成品溜走

> That LinkedIn DM you wrote three paragraphs of and then got pulled into a meeting? It's gone. The 600-word blog intro that had a great hook? Gone. The Slack message you rage-typed at 11pm? Gone. This skill catches every half-baked draft the second you stop typing, parks it safely, and puts it back in front of you when you're ready.

---

## Overview

`draft-tracker` is the **anti-amnesia layer for in-progress writing**. Most knowledge-work disasters aren't catastrophic — they're *forgotten*. You start an email, get interrupted, never come back. You draft a Substack intro, lose the thread, can't find the file. You write a tough message in Notes app, chicken out, lose the nerve *and* the wording.

`draft-tracker` solves this with **one trivial chat command**:
```
park: angry reply to Sarah about the missed deadline, 2 paragraphs done
```
…and the draft is saved with timestamp, context, and a follow-up date. Tomorrow at 8am you get a `daily-briefing`-style nudge: *"You have 3 unfinished drafts. 'angry reply to Sarah' is now 28 days stale — finish, rewrite, or trash?"*

The power isn't the storage — it's the **resurfacing loop**.

| Capability | Description |
|---|---|
| ⚡ **One-line park** | Save any in-progress draft with NL: title, context, what it is, how far along |
| 📋 **Multi-format drafts** | Emails, DMs, blog posts, essays, Slack messages, replies, ideas, meeting notes, code comments |
| ⏰ **Stale-draft detection** | Auto-flag ones you keep avoiding (15d / 30d / 60d tiers) |
| 🔁 **Resurface at right time** | Morning brief lists drafts; weekly review deep-cleans; cron for stale alerts |
| ✍️ **Resume in 30s** | `resume [id]` dumps the draft back with last-known context & word count |
| 🗑️ **Trash or convert** | One command to discard, or convert to idea/email/task/journal entry |
| 🔗 **Link to context** | Tag with recipient, project, intent — auto-suggest links from inbox/CRM |
| 📈 **Draft velocity** | Track how many you park, finish, abandon — spot the procrastination patterns |
| 🧹 **Weekly purge** | Friday auto-prompt: *"5 drafts are >30d stale. Finish 3, trash 2?"* |
| 🔒 **Local-first** | All drafts in `~/.hermes/drafts/drafts.json` — never uploaded, exportable |

---

## When to Use

Use `draft-tracker` when the user says any of:

**Direct triggers:**
- *"park this draft"* / *"save this for later"* / *"stash this"*
- *"I started writing an email but…"* / *"I had a great blog intro but…"*
- *"show my unfinished drafts"* / *"what did I leave half-done?"*
- *"resume draft #5"* / *"continue draft 'angry reply to Sarah'"*
- *"trash this draft"* / *"throw away draft #12"*
- *"show stale drafts"* / *"what drafts are more than a month old?"*
- *"I wrote half a LinkedIn DM last week — where is it?"*
- *"convert draft to email"* / *"send this draft"* / *"finish draft for me"*
- *"drafts older than 30 days"* / *"drafts I keep avoiding"*

**Indirect triggers (Hermes should ask):**
- User says *"I had a great idea but lost it"* → offer to park future ones
- User says *"I'll finish that later"* mid-message → "Want me to park it?"
- User pastes a partial email/DM/essay without sending → "Park as draft?"
- During `daily-shutdown`, scan for unfinished pomodoros/parked items
- During `weekly-review`, force-rank drafts by stale-age

**Don't use when:**
- The text is finished and ready to send (use `email-composer` / `message-tone-adjuster`)
- The user wants a brand-new piece written from scratch (use `linkedin-post-generator` / `twitter-thread-writer` / etc.)
- The user wants to track formal Tasks/Todos (use a TODO app — drafts ≠ todos)

---

## Core Workflow

### Step 1 — Detect Storage & Initialize

```bash
# Storage paths (auto-created on first use)
DRAFTS_DIR=~/.hermes/drafts
DRAFTS_FILE=$DRAFTS_DIR/drafts.json
CONTEXT_DIR=$DRAFTS_DIR/context   # optional: email threads, CRM pulls
ARCHIVE_DIR=$DRAFTS_DIR/archive  # soft-deleted drafts kept 90d

# Initialize on first run
mkdir -p "$DRAFTS_DIR" "$CONTEXT_DIR" "$ARCHIVE_DIR"
[ -f "$DRAFTS_FILE" ] || echo '[]' > "$DRAFTS_FILE"
```

Schema (one JSON record per draft):

```json
{
  "id": "d-2026-09-17-001",
  "title": "angry reply to Sarah about missed deadline",
  "type": "email|blog_post|linkedin_dm|twitter_thread|essay|reply|idea|note|slack_message|newsletter|other",
  "intent": "reply_to|outreach|content|vent|explainer|pitch|other",
  "recipient": "Sarah Chen",
  "project": "Q3 launch",
  "status": "parked|in_progress|stalled|finished|trashed",
  "body": "Full text of the draft (whatever was written)",
  "word_count": 187,
  "char_count": 1102,
  "created_at": "2026-09-17T14:23:11Z",
  "updated_at": "2026-09-17T14:23:11Z",
  "parked_at": "2026-09-17T14:23:11Z",
  "stale_threshold_days": 7,
  "stale_tier": "fresh|warning|critical",
  "resurfaced_count": 0,
  "tags": ["work", "Q3-launch", "needs-tone-soften"],
  "related": ["inbox:thread-1234", "crm:sarah-chen"],
  "next_step": "softer tone, ask for status by Friday",
  "cron_followup": "2026-09-24T08:00:00Z"
}
```

### Step 2 — Park, Resume, Finish, Trash

**Park a draft** (the most common verb):

```
User: park: tough reply to Marcus about the late invoice, 3 paragraphs done,
      wanted to soften the tone, send Tuesday
```

Parse → extract:
- `title` = "tough reply to Marcus about the late invoice"
- `type` = "email"
- `intent` = "reply_to"
- `recipient` = "Marcus"
- `body` = whatever they pasted (if any) OR placeholder
- `next_step` = "soften the tone, send Tuesday"
- `cron_followup` = next Tuesday 8am

If the user *also* pastes the actual text:
```
User: park: blog intro on AI hiring, here's what I have:

      "The first thing to understand about AI hiring in 2026 is that nobody..."
      [continues for 500 chars]
```
→ save `body` as the pasted text.

**Resume a draft:**

```
User: resume d-2026-09-17-001
User: resume the "angry reply to Sarah" draft
```
Output:
```
📌 d-2026-09-17-001 — Angry reply to Sarah about missed deadline
   Status: parked · Stale: 4 days · Word count: 187
   Recipient: Sarah Chen · Project: Q3 launch
   Last parked: Sep 17, 14:23
   Next step: softer tone, ask for status by Friday

   ━━━ DRAFT ━━━
   Sarah — I need to flag the Aug 31 deadline...
   ━━━ END ━━━

   💡 Resurface options:
   1. Edit & finish (paste new version)
   2. Hand to message-tone-adjuster to soften tone
   3. Trash (soft-delete, recoverable 90d)
   4. Convert to: [email] [todo] [idea] [journal]
```

**Stale tiers:**
- 0–7 days: `fresh` (no nudges)
- 8–30 days: `warning` (appear in `daily-briefing` once)
- 31–90 days: `critical` (appear in `weekly-review` & dedicated cron)
- 90+ days: auto-archive with one final "trash or revive?" ping

**Trash / finish:**
```
User: trash d-2026-09-17-001   → moves to ARCHIVE_DIR with status=trashed
User: finish d-2026-09-17-001  → status=finished, keeps body, removes from active list
User: archive old              → bulk-trash all drafts >90d
```

### Step 3 — Surface, Stale-Detect, Integrate

**Morning brief integration:**
```
📝 Drafts on your radar: 3 unfinished
   • d-...001 "tough reply to Marcus" — 12d stale, sent yet?
   • d-...007 "blog intro on AI hiring" — 6d, almost there?
   • d-...014 "LinkedIn DM to Maya" — 1d fresh

   Want to resume one now? → "resume d-001"
```

**Weekly review deep-clean (auto-prompt Friday 4pm):**
```
🧹 Drafts audit — 5 unfinished, here's the breakdown:

   ▸ 2d: LinkedIn DM to Maya [reply_to]
   ▸ 9d: Blog intro on AI hiring [content] ⚠️
   ▸ 12d: Tough reply to Marcus [reply_to] ⚠️
   ▸ 41d: Newsletter #14 lede [content] 🚨
   ▸ 87d: Angry reply to Sarah [vent] 🚨

   Stale drafts cost you more than fresh ones. Pick a verdict:
   1. Resume each one now (5–10 min)
   2. Hand off the 2 worst to message-tone-adjuster / linkedin-post-generator
   3. Bulk-trash anything >60d
   4. Convert to idea/email/todo
```

**Stale-draft cron (optional, sample at `cron/drafts-stale-weekly.yaml`):**
```yaml
name: drafts-stale-weekly
schedule: "0 16 * * 5"   # Fri 4pm
prompt: |
  Load drafts.json, find all parked/stalled drafts >14d.
  For each, ask: finish | rewrite via tone-skill | trash | snooze 30d.
  Deliver a single audit table to Admin.
```

### Step 4 — Edge Cases & Smart Behavior

| Situation | Behavior |
|---|---|
| User parks the same draft twice | Detect duplicate by title similarity (>0.8 Levenshtein) → "You have 'reply to Marcus about invoice' parked Sep 10. Update it or new draft?" |
| User pastes text but says "I deleted it" / "throw it away" | Don't park — confirm: "Got it. Discarding without saving. (y/n)" |
| User says "save this email I'm about to write" before typing | Park with empty body, status `blank`, followup same day |
| User wants to *finish* the draft in chat | Use the appropriate writing skill (`linkedin-post-generator`, `message-tone-adjuster`, etc.), then auto-update draft status to `finished` with the new body |
| Draft body contains PII (SSN, credit card) | Warn: "I see what looks like a credit card number. Park anyway? (It will live in your local file.)" |
| 100+ drafts accumulated | Run one-time "draft archaeology" — sort by age, surface 5 most-recent + 5 oldest, ask user to triage |
| User asks "what was I working on last Tuesday?" | Time-window search across drafts by `updated_at` |
| Cross-skill handoff | Park from `inbox-triage`, `daily-shutdown`, `meeting-prep-brief` outputs — they all can write to drafts.json |

### Step 5 — Optional Integrations

**Inbox-triage handoff:** When `inbox-triage` finds an email needing a reply but the user says "I'll get to it later" → auto-park as draft.

**Daily-shutdown handoff:** At end of day, surface unfinished drafts:
*"3 drafts parked. Pick tomorrow's first move? Reply to Marcus, or finish the AI-hiring post?"*

**message-tone-adjuster handoff:** When resuming a draft with `tone=aggressive` or user says "it's too harsh" → auto-pipe to `message-tone-adjuster`.

**Decision-journal handoff:** When user says *"I keep meaning to write down why I chose X"* and parks a half-thought → offer: "Convert to decision-journal entry?"

---

## Example Invocations

### Example 1 — The Lost LinkedIn DM

```
User: I started DMing my ex-coworker Maya about a referral to Anthropic
       and I lost it. I had a really good opener about the eval work we
       did together. Can you help me find it or rewrite it?

Hermes: I'll check your parked drafts first.

      → search drafts.json for: recipient~Maya, type=linkedin_dm, intent=referral

      Found it — d-2026-09-08-003, parked 9 days ago:

      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      📌 Maya — eval work referral opener
      Status: parked · 9d stale · 142 words
      Tags: #referral #anthropic #warm-intro
      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

      "Hey Maya — random one. We worked together on the eval pipeline
      back at Stripe (the one with the 4am Saturday pager rotation
      that I'm pretty sure made us both better engineers 😄). I'm
      exploring Anthropic for a research-engineer role and remembered
      you mentioned someone on the eval team. No pressure at all —
      totally fine to ignore. If you're ever open to a 5-min chat,
      I'd love your read on the team. Either way, hope eval-coffee
      is treating you well."

      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

      Want me to:
      1. Hand it to message-tone-adjuster for a freshness check
      2. Resume it as-is (paste into LinkedIn)
      3. Update with new info you've forgotten
      4. Trash (rewrite from scratch)

User: 2, paste it

Hermes: ✅ Logged "resume" — d-...003 marked flipped to "finished".
        Status now: finished, last touched just now.
        Pasting in 3…2…1…
        [draft text]
```

### Example 2 — Half-Written Reply During Shutdown

```
User: park: apology to David for missing his launch event, 1 paragraph,
      want to suggest coffee next week to make up

Hermes: 🚗 Parked as d-2026-09-17-007

      📌 Apology to David — missed launch event
      Type: email · Status: parked · 38 words
      Recipient: David Park · Project: Launch Week
      Next step: suggest coffee next week to make up
      Follow-up: Mon Sep 22, 8:00 AM

      ━━━ DRAFT ━━━
      David — I owe you a real apology. Your launch last Thursday
      was something I wanted to be at, and the timing just collapsed
      on me. No excuses — I should have texted.
      ━━━ END ━━━

      I'll remind you Monday morning. Want me to:
      a) Add a softer-tone polish pass now?
      b) Set a Wed 9am follow-up if you want extra buffer?
      c) Just leave it?

User: c

Hermes: ✅ Quiet until Monday. Have a good night.
```

### Example 3 — Weekly Stale-Draft Audit

```
User: show me drafts I keep avoiding

Hermes: 🚨 Stale Draft Audit — 4 parked, 3 are 14d+

   ┌────────────────────────────────────────────────────────────────┐
   │ ID        │ Age  │ Type    │ Title                            │
   ├───────────┼──────┼─────────┼─────────────────────────────────┤
   │ d-09-04-2 │ 13d  │ blog    │ "Why I left my last company"     │
   │ d-08-21-9 │ 2417 │ linkedin│ "Congrats to Sarah on promo"     │
   │ d-08-12-1 │ 3617 │ reply   │ "Tough reply to Marcus invoice"  │
   │ d-07-04-7 │ 7417 │ essay   │ "Notes on small-model evals"     │
   └────────────────────────────────────────────────────────────────┘

   🚨 36d+ (3 of 4) — these are costing you mental rent.

   Quick verdict (one-line each):
   • d-09-04-2 → "finish in 20 min"
   • d-08-21-9 → "trash, too late"
   • d-08-12-1 → "rewrite via message-tone-adjuster"
   • d-07-04-7 → "convert to decision-journal entry"

   Reply like: "finish 09-04-2, trash 08-21-9, rewrite 08-12-1, convert 07-04-7"
   …or pick numbers: "1=finish, 2=trash, 3=rewrite, 4=convert"

User: 1=finish, 2=trash, 3=rewrite, 4=convert

Hermes:
   ✅ d-09-04-2 marked finished (you said you'll do it now — paste final?)
   🗑️ d-08-21-9 trashed (recoverable 90d from ~/.hermes/drafts/archive)
   🔄 d-08-12-1 handed to message-tone-adjuster — output ready in next message
   📓 d-07-04-7 converted to decision-journal entry d-...004 (title: "Why I think small-model evals matter")

   4 of 4 cleared in 12 seconds. Your parked-draft queue is now zero.
```

---

## Common Pitfalls

| Problem | Solution |
|---|---|
| User says "save this" mid-message but didn't say *what* | Ask: "Save what? The whole message? Just the last paragraph? A title only?" |
| User has hundreds of drafts already (legacy) | Run "draft archaeology" once — sort by age, surface top 5 fresh + 5 oldest, do a triage pass before going operational |
| Body contains PII (SSN, full credit card, private keys) | Warn but don't block: "I see what looks like a credit card number (XXXX-XXXX-XXXX-1234). Confirm to park anyway?" |
| User wants to "finish this draft for me" | Don't auto-finish — hand off to the right writing skill (`linkedin-post-generator`, `message-tone-adjuster`, `twitter-thread-writer`) and mark status as `in_progress` |
| Parked draft gets re-parked as "duplicate" | Detect via title similarity; offer to update existing vs. create new |
| Draft body contains code / JSON / tables | Save verbatim; on resume, render as code-fence; don't try to re-format |
| User parks a draft of something they already sent | Detect overlap (e.g., message already in inbox-triage history) → "Did you already send this? Mark as sent instead?" |
| Storage file grows huge (50k+ words) | Auto-archive any `finished` or `trashed` draft >90d to a rolling archive file, keep active JSON small |
| Two devices / two sessions park at once | Use atomic write (`mv tmp drafts.json`) + per-id timestamp to avoid race |
| User says "I lost a draft" and it's actually in trash/archive | Check archive_dir before saying "not found"; drafts live 90d after trash |
| User wants drafts in Notion / Obsidian / Apple Notes | Provide one-time export script, don't try to live-sync |
| Drafts feel like a TODO list creep | Keep them separate: drafts ≠ todos. Optional: at weekly review, ask "any of these drafts actually todos?" |

---

## Verification Checklist

Before claiming a draft-tracker session is complete:

- [ ] `~/.hermes/drafts/drafts.json` exists and is valid JSON
- [ ] Each park produced a unique `id` with today's date
- [ ] `body` contains whatever the user pasted (or empty string if title-only park)
- [ ] `status`, `stale_tier`, `cron_followup` are correctly computed
- [ ] Resume command dumps the full `body` plus metadata context
- [ ] Trash command moves file to `archive/` with `status=trashed` and keeps recoverable copy for 90d
- [ ] Stale-draft query correctly buckets by age (7/30/60/90 day thresholds)
- [ ] No PII auto-redacted silently — warnings only, with user confirmation
- [ ] Daily-briefing-style morning nudge lists unfinished drafts (if integrated)
- [ ] Weekly-review integration deep-cleans >14d drafts (if integrated)
- [ ] Cross-skill handoff works: `inbox-triage`, `daily-shutdown`, `message-tone-adjuster`
- [ ] Output never claims "saved" without actually writing to disk
- [ ] Draft body never logged to console in full (privacy) — preview only

---

## Data Sources & Accuracy

| Source | Use | Accuracy |
|---|---|---|
| User input (chat) | Title, body, recipient, project, tags, next-step | 100% — user-provided |
| `~/.hermes/drafts/drafts.json` | Persistent store | Local file, atomic write, no cloud |
| Local clock (`date` / `Date.now()`) | `created_at`, `parked_at`, `cron_followup` | System clock, timezone-aware |
| Levenshtein / token similarity (stdlib) | Duplicate detection on park | ~95% on titles >5 chars |
| Cross-skill: `personal-crm/contacts.json` | Recipient auto-suggest | Local read-only |
| Cross-skill: `inbox-triage/index.json` | Auto-detect already-sent messages | Local read-only |

**Privacy guarantees:**
- All drafts live locally under `~/.hermes/drafts/`
- Never uploaded to any cloud endpoint
- Atomic writes — no partial saves
- Soft-delete (90-day archive) lets you recover from "I trashed it by mistake"
- One-line export to JSON / Markdown if you want to back up or migrate

**Failure modes:**
- Disk full → write fails → user is told "couldn't save, here's the draft text you can copy"
- JSON corruption → on load, fall back to last good backup + warn
- User crosses 1000 drafts → prompt for cleanup, slow down with filters

---

> *"The best time to finish a draft was yesterday. The second-best time is when it's parked, not lost."*