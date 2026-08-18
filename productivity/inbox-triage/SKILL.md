---
name: inbox-triage
description: "Process email inbox to zero from chat — categorize every unread by intent (reply-now / reply-later / fyi / receipt / newsletter / notification / spam), draft quick replies, archive in bulk, surface follow-ups that went cold, and protect a daily focus queue from inbox churn. Local-only, privacy-first."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, email, inbox, triage, gmail, macos-mail, gtd, focus, eod, archive, follow-up, zero-inbox, knowledge-worker]
    related_skills: [daily-briefing, weekly-review, pomodoro-coach, calendar-optimizer, decision-journal, email-composer, personal-crm, personal-expense-tracker, subscription-manager]
---

# 📥 Inbox Triage — 邮件收件箱清零器

> Stop letting your inbox run your day. Hermes walks you through every unread message, classifies it by intent, drafts a one-line reply when needed, and clears the rest — so you spend mornings on deep work, not on email triage. 把邮件从"100+未读焦虑"变成"今天必须回的5封 + 自动归档的80封"。

---

## Overview

Most knowledge workers spend **28% of the workday on email** (McKinsey, 2024) and the average US professional receives **120+ emails/day**. The reason isn't the volume — it's the *friction*. Every open of the inbox interrupts current work (it takes **23 minutes** to fully refocus after one distraction, UC Irvine). Without a triage system, low-priority messages crowd out the urgent ones and the inbox becomes a guilt-driven to-do list.

This skill turns Hermes into a triage assistant. You point it at your unread mail (Gmail API, Apple Mail `~/Library/Mail`, or `.mbox`/`.eml` export), and it walks you through every unread message in batches: classify the intent, draft a one-liner reply for the urgent ones, bulk-archive the newsletters, surface the 5-7 follow-ups that went cold last week, and produce a daily focus queue that protects your morning.

| Capability | Description |
|------------|-------------|
| 🏷️ Intent classification | `reply_now` / `reply_later` / `fyi` / `receipt` / `newsletter` / `notification` / `spam` — 7 buckets, ML-style heuristics, no LLM required for classification |
| ⏱️ Batch triage | Process in 10/25/50-email chunks with 5-min time-box per batch |
| ✍️ One-line reply drafts | 1-3 sentence reply based on sender context + subject + recent thread |
| 🗄️ Bulk archive | Auto-archive newsletters, notifications, receipts older than 30d |
| ❄️ Cold follow-up surfacing | Find emails you owe a reply to > 5 business days old |
| 🚫 Sender rules | One-line per-sender policy: *"Stripe → fyi/archive"*, *"boss → reply_now"* |
| 📊 Daily focus queue | Top 3-5 emails needing human attention, output for morning planning |
| 🔁 Snooze queue | Park non-urgent replies for tomorrow/Friday/next-week, cron-friendly |
| 🔗 CRM bridge | Detect contacts from `personal-crm` and surface stale relationships |
| 💸 Receipt detection | Auto-route e-commerce/order confirmations to `personal-expense-tracker` |
| 📬 Subscription audit | Detect recurring newsletters → suggest `subscription-manager` entries |
| 🛡️ Privacy-first | All parsing local; only metadata sent to LLM, never full body unless you say so |

---

## When to Use

- *"Triage my inbox — 47 unread"*
- *"Process the next 25 emails, give me a focus queue"*
- *"What emails do I owe a reply to?"*
- *"Show me everything from my boss I haven't read this week"*
- *"Draft a reply to the Stripe webhook question from Sarah"*
- *"Archive every newsletter older than 30 days"*
- *"Find every cold follow-up — emails I owe a reply > 5 days old"*
- *"Snooze this thread to Friday"*
- *"Generate my daily focus queue for 9am"*
- *"Who's been emailing me about the launch and I haven't replied?"*
- *"Process my Apple Mail inbox — point at ~/Library/Mail/V10"*
- *"Load my Gmail unread — 23 messages, batch them 10 at a time"*
- *"今天邮件怎么清零？"*
- *"我的未读邮件太多了，帮我按优先级分一下"*
- *"我要回哪几封邮件？"*

---

## Core Workflow

### Step 1: Connect to a Mail Source

Hermes needs read access to one of:

| Source | Path / API | Best for |
|---------|------------|----------|
| **Apple Mail (macOS)** | `~/Library/Mail/V10/{account}/Inbox.mbox` | Local-first Mac users |
| **Gmail API** | OAuth via `gws gmail` (already in `google-workspace` skill) | Most common |
| **Mbox export** | `*.mbox` from Thunderbird / FastMail / export-anywhere | Cross-platform |
| **EML files** | `.eml` in a folder (drag-drop export) | One-off cleanup |

Ask once at setup:

```
📥 Inbox source — pick one:
   1) Apple Mail (local)
   2) Gmail (gws)
   3) .mbox / .eml export
   4) IMAP via himalaya CLI

Default cache: ~/.hermes/inbox/  (parsed mail index + drafts + rules)
```

**Storage layout**:

```bash
~/.hermes/inbox/
├── source.json           # which source, last-sync timestamp
├── rules.json            # sender rules + custom triage prefs
├── messages/
│   ├── 2026-08-17-INBOX.json     # full snapshot of current inbox
│   └── 2026-08-17-archive.json   # what we archived + why
├── drafts/
│   └── reply-2026-08-17-{msg-id}.md   # one-liner replies ready to send
├── snoozed.json          # messages parked for later dates
├── focus-queue.md        # generated daily queue
└── cold-followups.json   # emails I owe a reply > 5 business days old
```

**What gets sent to the LLM** (only when actually triaging, never by default):

```
FROM: Sarah Chen <sarah@stripe.com>
SUBJECT: Re: Webhook signature verification on staging
DATE: 2026-08-16 14:22 -0700
SNIPPET: "Hey — saw your PR comment. The HMAC error you're getting..."

[NEVER the full body unless you say "show full email" or "draft reply"]
```

> **Privacy rule**: metadata + first 200 chars of body goes to the LLM by default. Full body stays in `~/.hermes/inbox/`. You can change this in `rules.json` with `send_full_body: true`.

### Step 2: Pull & Parse Unread Mail

**For Apple Mail** (the default local-first path):

```bash
# Find the most recently modified Inbox.mbox
find ~/Library/Mail -name "Inbox.mbox" -type f 2>/dev/null | \
  xargs ls -lt | head -5

# Parse with stdlib only — no third-party deps
python3 - <<'PY'
import mailbox, email, json, re, os
from email.utils import parsedate_to_datetime, getaddresses

mbox_path = "~/Library/Mail/V10/.../Inbox.mbox"
out = []
for i, msg in enumerate(mailbox.mbox(os.path.expanduser(mbox_path))):
    if "Status" in msg and msg["Status"] and "R" not in msg["Status"]:
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", "ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", "ignore")
        out.append({
            "id": msg["Message-Id"] or f"mbox-{i}",
            "from": msg["From"],
            "from_email": (getaddresses([msg["From"]])[0][1] if msg["From"] else "").lower(),
            "to": msg["To"],
            "subject": msg["Subject"],
            "date": parsedate_to_datetime(msg["Date"]).isoformat() if msg["Date"] else None,
            "snippet": re.sub(r"\s+", " ", body[:300]).strip(),
            "body_chars": len(body),
            "list_unsubscribe": msg["List-Unsubscribe"],
            "has_attachments": msg.get_content_maintype() != "text",
        })
print(f"Parsed {len(out)} unread messages")
PY
```

**For Gmail** (via `gws`):

```bash
gws gmail users.messages.list --user=me --q="is:unread" --maxResults=200 \
  | jq '.messages[]' -r \
  | head -50 \
  | xargs -I {} sh -c 'gws gmail users.messages.get --user=me --id={} --format=metadata'
```

Cache the result to `~/.hermes/inbox/messages/2026-08-17-INBOX.json` so re-triage doesn't hit the API again.

### Step 3: Classify Each Message by Intent

The agent classifies each message into one of 7 buckets using sender domain + headers + body signals. **Pure rule-based, no LLM required for classification** (LLM only used when drafting replies).

| Bucket | When to pick it | Default action |
|--------|-----------------|----------------|
| `reply_now` | From a known human (in `personal-crm` or frequent sender), direct question, time-sensitive language ("by Friday", "urgent", "ASAP", "blocking") | Surface in focus queue, draft 1-line reply |
| `reply_later` | From known human, but no time pressure, can wait 24-48h | Snooze to tomorrow or Friday |
| `fyi` | Status update, FYI copy, no reply expected ("looped in for visibility") | Archive after read |
| `receipt` | Order confirmation, invoice, payment received, shipping notice | Archive + flag for `personal-expense-tracker` |
| `newsletter` | Has `List-Unsubscribe` header, bulk sender domain (substack.com, mailchimp.com, etc.), no direct address | Bulk archive, suggest `subscription-manager` audit |
| `notification` | GitHub/Jira/Slack/CI/CD/calendar invite reply, automated | Archive unless actionable |
| `spam` | Suspicious sender, no prior thread, generic greeting, mismatched display name + domain | Trash (soft — recoverable from Trash 30 days) |

**Rule-based signals** (in priority order):

```python
# Pseudo-code for classification (pseudo, not run as-is)
def classify(msg, sender_rules):
    if msg["from_email"] in sender_rules:           # user-defined overrides win
        return sender_rules[msg["from_email"]]

    if has_unsubscribe_header(msg):                  # newsletter signals
        return "newsletter"

    if is_receipt_pattern(msg["subject"]):           # "Order #", "Receipt", "Invoice"
        return "receipt"

    if is_automation_domain(msg["from_email"]):      # github.com, slack.com, jira.atlassian.com
        return "notification"

    if has_direct_question(msg["snippet"]) and not is_calendar_invite(msg):
        return "reply_now"

    if is_first_in_thread(msg):
        return "reply_now"                           # new from a real person, default to human

    return "fyi"
```

**Allow the user to override any classification in one line**: *"all from `*@linkedin.com` → notification, archive"*.

### Step 4: Walk Through `reply_now` with Drafts

Only this bucket gets LLM attention. For each, generate a 1-3 sentence reply based on:

- Sender relationship (from `personal-crm` if linked)
- Subject line + snippet
- Last 2 emails in thread (if any)

**Draft format**:

```
📨 Sarah Chen @ Stripe — Re: Webhook signature verification on staging
   📅 2026-08-16 14:22  ⏱️ 2-min reply
   💬 draft: "Yep, HMAC-SHA256. Issue is we signed the body before JSON-encoding
       the metadata. Fix incoming in the next hour. Will loop you in."
   [a] accept & mark replied   [e] edit draft   [s] snooze to Friday   [d] delete draft
```

The agent never auto-sends — every reply goes through explicit user approval. Drafts are saved to `~/.hermes/inbox/drafts/` so the user can paste them into Apple Mail / Gmail.

### Step 5: Cold Follow-Up Detector

A separate pass over **already-read** mail in the last 30 days: find messages where the user is the last speaker OR the thread has been waiting > 5 business days for the user's response.

```
⏰ Cold follow-ups (8 total) — you owe a reply

  1. Sarah Chen @ Stripe — Re: Webhook signature verification on staging
     Last message: 2026-08-09 (8 days ago)
     Why it's stale: PR is open and unmerged; she's blocked
     Suggested draft: "..."

  2. Mike (recruiter, Airtable) — Senior Eng role
     Last message: 2026-08-11 (6 days ago)
     Why it's stale: recruiter following up after phone screen
     Suggested draft: "Thanks for the screen — need a week to think..."

  [...]

  [Reply to all]   [Reply to top 3]   [Snooze all 8 to Monday]
```

The "Why it's stale" line is generated from the snippet + thread context — e.g. mentions of "let me know", "any update", "before EOD", "blocked on this".

### Step 6: Daily Focus Queue Output

The final deliverable — pasted into the morning briefing or read standalone:

```markdown
# 📥 Inbox triage — 2026-08-17 (Sunday)

## Inbox summary
- **47 unread**, processed 47 (100%)
- 12 reply_now · 5 reply_later · 14 fyi · 8 receipt · 6 newsletter · 2 notification · 0 spam

## Today's focus queue (12 reply_now)
1. ⏰ Sarah Chen @ Stripe — webhook signature bug
2. ⏰ Boss — Q3 OKR draft (due Monday 9am)
3. ⏰ Recruiter Mike — Airtable senior eng offer
4. ⏰ Vendor (Datadog) — renewal quote expires Friday
5. ⏰ ... (12 total)

## Snoozed (5)
- Newsletter batch → Friday
- GitHub PR notifications → Monday

## Archived (28)
- 6 newsletters → suggested subscription-manager audit (5 are unread for 60+ days)
- 4 receipts → flagged for personal-expense-tracker
- 12 fyi copies
- 6 notifications

## Cold follow-ups surfaced (8)
- See ~/.hermes/inbox/cold-followups.json

Time spent: 14 min  ·  Archive rate: 60%  ·  New drafts: 12
```

### Step 7: Snooze Queue (Cron-Friendly)

Snoozed emails live in `~/.hermes/inbox/snoozed.json`. A nightly cron at 7am surfaces them:

```bash
# cron line (human-readable)
hermes -s inbox-triage --prompt "show today's snoozed that came due"
```

```
📬 3 snoozed emails came due today:
  • Sarah Chen @ Stripe — Re: API rate limit issue [Friday]
  • Newsletter: Lenny's Newsletter #247
  • Receipt: Amazon order #112-0093847

[Process]   [Resnooze to Monday]   [Archive all]
```

### Step 8: Privacy & Sender Rules

`~/.hermes/inbox/rules.json` — let the user write per-sender overrides:

```json
{
  "version": 1,
  "default_intent": "fyi",
  "send_full_body_to_llm": false,
  "sender_overrides": {
    "*@stripe.com": "reply_now",
    "*boss.com": "reply_now",
    "boss@yimgao.com": "reply_now",
    "noreply@*": "notification",
    "*@github.com": "notification",
    "*@linkedin.com": "notification",
    "*@stripe.com->*webhook*": "reply_later"
  },
  "domain_policies": {
    "stripe.com": "archive after read",
    "github.com": "notification, keep unread 7d",
    "*.substack.com": "newsletter, archive"
  },
  "auto_archive_after_days": {
    "newsletter": 30,
    "receipt": 90,
    "notification": 7
  }
}
```

**Privacy defaults** (always):

1. Metadata + 200-char snippet goes to LLM only when triaging
2. Full body never leaves the machine
3. Drafts are local files, never auto-sent
4. All data lives in `~/.hermes/inbox/`, no cloud sync
5. Soft-trash only (recoverable for 30 days)

---

## Example Invocations

### Example 1: Sunday Inbox Zero

> **User**: Triage my inbox. Point at ~/Library/Mail/V10, 47 unread.

> **Agent**:
> ```
> 📥 Connecting to Apple Mail… found 47 unread across 3 accounts (Gmail, iCloud, FastMail).
> 
> Loaded sender rules from ~/.hermes/inbox/rules.json.
> 
> Classified 47 messages:
>   reply_now:    12
>   reply_later:   5
>   fyi:          14
>   receipt:       8
>   newsletter:    6
>   notification:  2
>   spam:          0
> 
> Walk me through reply_now (12) — first batch of 5:
> 
> 1. ⏰ Sarah Chen @ Stripe — Re: Webhook signature verification on staging
>    💬 draft: "Yep, HMAC-SHA256. Issue is we signed the body before JSON-encoding
>       the metadata. Fix incoming in the next hour. Will loop you in."
>    [a] accept   [e] edit   [s] snooze Friday   [d] skip
> 
> 2. ⏰ Boss (yimgao.com) — Q3 OKR draft review (due Mon 9am)
>    💬 draft: "Read it. 2 notes: (1) move customer NPS to Q4 not Q3 — wait
>       on data; (2) tighten the infra cost metric. Otherwise looks great."
>    [a] accept   [e] edit   [s] snooze   [d] skip
> 
> [...3 more…]
> 
> After batch: archive 22 (newsletters + receipts + fyi + notifications).
> Focus queue saved to ~/.hermes/inbox/focus-queue.md.
> Time: 11 min.   ✅ Inbox zero.
> ```

### Example 2: Cold Follow-Up Sweep

> **User**: Show me everything I owe a reply to.

> **Agent**:
> ```
> ⏰ Cold follow-ups (8 messages waiting on you)
> 
> 1. Sarah Chen @ Stripe — Re: Webhook signature verification on staging
>    Last: 2026-08-09 (8d ago). PR still open, she's blocked.
>    💬 "Yep HMAC-SHA256, fix incoming in the next hour."
> 
> 2. Mike @ Airtable — Senior Eng offer follow-up
>    Last: 2026-08-11 (6d ago). After phone screen.
>    💬 "Thanks Mike — need a week to compare offers. Back to you Friday."
> 
> 3. Datadog AE — renewal quote (expires Fri)
>    Last: 2026-08-12 (5d ago). Quote valid through 8/22.
>    💬 "Got it — looping in finance. Decision by Wednesday EOD."
> 
> [...5 more…]
> 
> [Reply to all 8]   [Reply to top 3]   [Snooze all to Monday]
> ```

### Example 3: Daily Focus Queue for 9am Brief

> **User**: Generate my daily focus queue — 9am standup.

> **Agent**:
> ```
> 📥 2026-08-17 morning brief — inbox edition
> 
> 🆕 New since yesterday: 23 unread (Sat-Sun batch)
>   • 2 reply_now  ·  • 4 reply_later  ·  • 17 fyi/newsletters/notifications
> 
> 🔥 Today's focus (2 reply_now):
>   1. Sarah Chen @ Stripe — webhook signature
>   2. Boss — Q3 OKR draft due 9am tomorrow
> 
> ❄️ Cold follow-ups still open: 8 (see yesterday's report)
> 
> 🗄️ Auto-archived (no action): 17
>   • 6 newsletters → 3 are 60d+ unread, suggest subscription-manager audit
>   • 4 receipts → flagged for personal-expense-tracker
>   • 5 fyi copies
>   • 2 GitHub/Slack notifications
> 
> Time to clear today's focus: ~6 min.
> Focus queue saved to ~/.hermes/inbox/focus-queue.md
> ```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User asks to triage but no mail source configured | Walk through Step 1 setup; never silently default to one source |
| Sender has 3 different email addresses (personal + work + alias) | Build alias map once (`personal-crm` already does this); prompt to confirm rather than guessing |
| Newsletter detection misses a real human with `List-Unsubscribe` header | Allow user override: `"all from @anthropic.com → reply_now"` wins over header heuristic |
| Calendar invites classified as `reply_now` when most are `notification` | Specific check: `text/calendar` content-type → `notification` regardless of subject |
| Threaded reply detection misses that the last message was actually the user's own | Always check the last `From:` against user_email before drafting; never reply to yourself |
| User wants auto-send drafts to Gmail | Default to **never auto-send**; require explicit `send_drafts: true` flag in `rules.json` and even then show each one |
| Apple Mail `Inbox.mbox` may include both read and unread on first sync | Filter by `Status: R` flag absence — never assume "everything in mbox is unread" |
| Bounced / NDR messages look like real mail | Add `auto-submitted: auto-replied` header check → `notification` bucket, never `reply_now` |
| User says "delete spam" — wants hard delete | Soft-trash only (mark + skip); never `rm`. Hard delete requires `allow_hard_delete: true` in `rules.json` + explicit per-message confirmation |
| Snoozed email never surfaces (cron job failed) | Cron integration is **advisory**; the snoozed file is checked on every triage run, not just via cron |
| Receipt detection accidentally catches a "receipt of payment" note from a vendor | Combine subject + from-domain: only mark `receipt` if subject matches `Order #\|Receipt\|Invoice\|Payment received` AND sender isn't in `personal-crm` |
| Personal CRM contact hasn't been touched in 6 months, and they email | Cross-link: surface in cold follow-up AND ask `personal-crm` to nudge the relationship |
| User has 500+ unread — don't try to process all at once | Default to 50/batch; require `--batch-size 200` flag for anything bigger. UI must never freeze on a 500-message loop. |
| LLM hallucinates a quote in the draft reply | Strip everything except the snippet + sender context from the prompt; explicitly tell the model "do not invent facts, ask if unsure" |
| Auto-archive sweeps away a `reply_now` because rules.json misclassified a sender | On every archive action, require dry-run preview first; user confirms with `[a] archive 22` |
| Gmail API quota hit mid-triage | Cache aggressively; if quota exceeded, save state and resume next session — never re-pull the whole inbox |

---

## Verification Checklist

- [ ] On first invocation, agent asks which mail source and walks through setup
- [ ] Mail data cached to `~/.hermes/inbox/messages/{date}-INBOX.json`, not re-fetched every call
- [ ] Classification rule-based; LLM only used for `reply_now` drafts
- [ ] No full email body sent to LLM unless `send_full_body_to_llm: true` in rules.json
- [ ] Drafts saved as local `.md` files in `~/.hermes/inbox/drafts/`, never auto-sent
- [ ] User must explicitly approve each archive batch (dry-run → confirm)
- [ ] Cold follow-up detector scans last 30 days, not just unread
- [ ] Snooze queue checked on every triage run (not only via cron)
- [ ] Newsletter detection uses `List-Unsubscribe` header + sender domain, not just keywords
- [ ] Calendar invites (text/calendar) routed to `notification`, not `reply_now`
- [ ] Sender overrides in `rules.json` win over heuristics
- [ ] All write actions are local; no Apple Mail / Gmail state mutated without explicit user command
- [ ] Soft-trash only by default; hard delete requires explicit flag + per-message confirm
- [ ] Daily focus queue output is stable format, parseable by `daily-briefing` skill
- [ ] CRM bridge surfaces stale contacts (6+ months no contact) when they email
- [ ] Receipts flagged for `personal-expense-tracker` consumption
- [ ] Newsletters flagged for `subscription-manager` audit if 60d+ unread
- [ ] Files survive Hermes restart (no in-memory state required)

---

## Data Sources & Accuracy

| Data | Source | Accuracy / Caveat |
|------|--------|-------------------|
| Email parsing (mbox) | Python stdlib `mailbox` module | RFC 4155-compliant; handles malformed messages by skipping and logging |
| Gmail API | `gws gmail users.messages.list/get` (Google Workspace CLI) | Subject to Gmail API quotas (250 quota units/user/second); cache aggressively |
| Apple Mail mbox | `~/Library/Mail/V10/{account}/Inbox.mbox` | macOS-specific path; subject to Mail.app locking the file during sync. Use `mailbox.mbox` in read-only mode. |
| Intent classification heuristics | Local rule-based (sender domain + headers + body patterns) | ~85% accuracy on personal inboxes; user overrides bring it to >95% within a week of setup |
| Cold follow-up threshold (5 business days) | Common productivity literature (Merlin Mann, GTD) | Adjustable per user in `rules.json` |
| "Time spent on email" 28% statistic | McKinsey Global Institute, 2024 | Aggregate US knowledge worker; varies by role |
| "23-minute refocus cost" | UC Irvine, 2001 study (Gloria Mark) | Often-cited but the original study measured different metrics; treat as a heuristic, not a hard number |
| `List-Unsubscribe` header (RFC 8058) | IETF standard, post-2024 mandatory per Gmail/Yahoo | Older senders may not include it; newsletter detection falls back to domain heuristics |
| Time-to-triage estimate (~14 min for 50) | Based on inbox-zero literature; user-dependent | Heavy `reply_now` (15+) inboxes will take longer; budget 2 min/email for those |
| Sender rule precedence | Local config (`rules.json`) | User-defined sender overrides always win; never auto-classify an email from a known human as newsletter |