---
name: prompt-library
description: "Save, version, tag, search, and reuse your best LLM prompts — personal prompt manager with local JSON storage, semantic search, and instant retrieval by chat"
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [prompt-engineering, library, reuse, productivity, llm, knowledge-management]
    related_skills: [prompt-benchmarker, model-comparator, llm-output-validator, web-clipper]
---

# Prompt Library（个人 Prompt 库 / 个人提示词管理）

> Stop losing great prompts in chat history. Save the ones that worked, tag them, version them, search them, and reuse them with one line. Your personal library of proven LLM prompts — fully local, fully searchable.

| Capability | Description |
|-----------|-------------|
| 💾 Save prompts | *"Save this prompt as 'cold-email-v2'"* — captured instantly |
| 🏷️ Tag & organize | Multi-tag, project, model target, language (en/zh/code) |
| 🔍 Smart search | Find by intent, not just exact text — *"show me all coding refactor prompts"* |
| 📜 Versioning | Edit → automatic version history; never lose the old one |
| 📋 Reuse in 1 line | *"Use cold-email-v2 on: Acme Corp, hiring PM, ..."* |
| ⭐ Star ratings | Mark winners; library surfaces the highest-rated first |
| 📊 Usage stats | Which prompts you actually use vs. forget about |
| 💾 Local-first | All data in `~/.hermes/data/prompts.json` — no cloud, no leak |

---

## When to Use

- *"Save this prompt — it's been working great for code reviews"*
- *"Find my prompt for writing investor updates"*
- *"Show me all Chinese prompts I saved last month"*
- *"Update cold-email-v2 to mention the new product line"*
- *"Use my 'meeting-summary' prompt on these raw notes…"*
- *"What was that prompt I used for the Stripe negotiation email?"*
- *"Compare v1 and v3 of my 'linkedin-post' prompt"*
- *"Delete the 12 prompts I never used"*
- *"Show me my top 5 most-used prompts this month"*
- *"帮我存一下这个 prompt，下次还想用"*
- *"我想找一个能写小红书爆款标题的 prompt"*

---

## Core Workflow

### Step 1: Save a Prompt

User says: *"Save this prompt as 'cold-email-v2' — 'You are a B2B SaaS founder writing a cold email to {{company}} about {{pain_point}}…'"*

The agent parses:

```yaml
name: cold-email-v2          # unique slug (kebab-case, versioned)
content: |
  You are a B2B SaaS founder writing a cold email to {{company}} about {{pain_point}}.
  Keep it under 80 words. Subject line max 6 words. Open with a specific observation.
variables:                    # auto-detected from {{...}} or {…}
  - company
  - pain_point
tags: [email, b2b, sales, en] # auto-suggested, user can override
model_target: [gpt-4, claude] # which model(s) it works best on
language: en                  # en | zh | code | mixed
star_rating: 4                # optional, user-set
project: "acme-outreach"      # optional grouping
notes: "Best open rate so far — 42% reply" # optional context
```

**Storage location:** `~/.hermes/data/prompts.json`

```json
{
  "prompts": {
    "cold-email-v2": {
      "id": "cold-email-v2",
      "name": "Cold Email v2 — B2B SaaS Outreach",
      "content": "You are a B2B SaaS founder writing a cold email to {{company}} about {{pain_point}}. Keep it under 80 words. Subject line max 6 words. Open with a specific observation.",
      "variables": ["company", "pain_point"],
      "tags": ["email", "b2b", "sales", "en"],
      "model_target": ["gpt-4", "claude-3.5"],
      "language": "en",
      "star_rating": 4,
      "project": "acme-outreach",
      "notes": "Best open rate so far — 42% reply",
      "version": 2,
      "version_history": [
        {
          "version": 1,
          "content": "Write a cold email to {{company}}.",
          "saved_at": "2026-05-12T10:30:00Z",
          "note": "Initial draft — too generic"
        }
      ],
      "usage_count": 7,
      "last_used": "2026-07-15T09:14:00Z",
      "created_at": "2026-05-12T10:30:00Z",
      "updated_at": "2026-07-15T09:14:00Z"
    }
  }
}
```

**Confirmation message:**

```
✅ Saved "cold-email-v2" (v2) — 2 variables, 4 tags
📁 project: acme-outreach  ·  ⭐ 4/5  ·  used 7x
```

---

### Step 2: Search & Retrieve

User says any of:
- *"Find my prompt for writing investor updates"* (intent search)
- *"Show me all coding prompts tagged 'refactor'"* (tag filter)
- *"What's cold-email-v2?"* (exact slug)
- *"Show prompts I saved this week"*
- *"最近一个月我存的所有中文 prompt"*

**Search modes the agent runs:**

| Mode | Trigger Examples | Method |
|------|------------------|--------|
| Exact slug | `"cold-email-v2"` | direct lookup |
| Keyword | `"investor update prompt"` | scan name + tags + notes |
| Intent | `"something for writing cold emails"` | match tags + project + LLM-reasoned relevance |
| Tag filter | `"tagged 'refactor'"` / `"project:my-app"` | exact filter |
| Recent | `"this week"`, `"last month"` | timestamp filter |
| Top-rated | `"best prompts"`, `"top 5"` | sort by star × usage |
| Variables | `"prompts that take a {{company}}"` | scan `variables[]` |

**Output format (always):**

```markdown
### 🔍 3 prompts matched "cold email"

| Slug | Tags | ⭐ | Used | Updated |
|------|------|---|------|---------|
| **cold-email-v2** | email, b2b, sales | 4 | 7x | 2 days ago |
| cold-email-v1 | email, sales | 3 | 2x | 2 months ago |
| followup-email | email, b2b | — | 0 | 1 week ago |

→ **cold-email-v2** (current)
> You are a B2B SaaS founder writing a cold email to {{company}} about {{pain_point}}…
> Variables: `{{company}}`, `{{pain_point}}`

To use: *"use cold-email-v2 on Stripe, hiring SDRs"*
```

**Auto-render the actual prompt content** when there are 1-3 results; show preview + slug when 4+.

---

### Step 3: Reuse a Prompt

User says: *"Use cold-email-v2 on Stripe, hiring SDRs, observability platform"*

The agent:
1. Looks up the prompt by slug
2. Extracts variables (`{{company}}`, `{{pain_point}}`) — map by position if not labeled
3. Substitutes and produces a ready-to-paste / ready-to-send block
4. Increments `usage_count` and updates `last_used`

**Output:**

```markdown
📋 **cold-email-v2** v2 · 7 prior uses

**Filled template:**

> You are a B2B SaaS founder writing a cold email to **Stripe** about **hiring SDRs, observability platform**. Keep it under 80 words. Subject line max 6 words. Open with a specific observation.

**Used variables:**
- `{{company}}` → Stripe
- `{{pain_point}}` → hiring SDRs, observability platform

✅ Usage logged (now 8x).

Want me to run this against your LLM now, or just hand you the filled prompt?
```

If variables are missing or ambiguous, ask in **one** clarifying question — never silently guess.

---

### Step 4: Edit & Version

User says: *"Update cold-email-v2 — add a CTA at the end"* or *"Make a v3 with a more aggressive opener"*

The agent:
1. Fetches current prompt
2. Saves current to `version_history[]` with auto-generated diff note
3. Updates content; bumps `version`; sets `updated_at`
4. Optionally clears `star_rating` (treat new version as unrated until re-tested)

**Diff display (only when version > 1):**

```
📜 cold-email-v2 — v1 → v2

- Write a cold email to {{company}}.
+ You are a B2B SaaS founder writing a cold email to {{company}} about {{pain_point}}.
+ Keep it under 80 words. Subject line max 6 words.

💡 Auto-note: "added role, specificity, and length constraint"
```

---

### Step 5: Cleanup & Maintenance

User says: *"Delete prompts I never used"* / *"Show me duplicates"*

The agent runs:

```bash
# Detect orphans
jq '.prompts | to_entries | map(select(.value.usage_count == 0))' ~/.hermes/data/prompts.json

# Detect near-duplicates by token overlap
python3 -c "
import json
from collections import Counter
prompts = json.load(open('/Users/USER/.hermes/data/prompts.json'))['prompts']
words = {k: Counter(v['content'].lower().split()) for k, v in prompts.items()}
keys = list(words.keys())
for i, a in enumerate(keys):
    for b in keys[i+1:]:
        common = sum((words[a] & words[b]).values())
        if common > 50:
            print(f'Duplicate: {a} ↔ {b} (overlap={common})')
"
```

Then presents the cleanup plan and **asks before deleting** — never destructive without confirmation.

---

## Example Invocations

### Example 1 — Save → Reuse (most common path)

> **User:** Save this prompt as "linkedin-post-formula":
> "Write a LinkedIn post about {{topic}} using the PAS framework (Problem-Agitate-Solution). Hook in first line. Max 3000 chars. 3-5 short paragraphs. End with a question."
>
> **Agent:** ✅ Saved **linkedin-post-formula** (v1) — 1 variable (`{{topic}}`), tags: linkedin, writing, en
>
> **User:** Use linkedin-post-formula on: getting rejected by 7 VCs in a row
>
> **Agent:** 📋 **linkedin-post-formula** v1 · first use
>
> **Filled template:**
> > Write a LinkedIn post about **getting rejected by 7 VCs in a row** using the PAS framework (Problem-Agitate-Solution). Hook in first line. Max 3000 chars. 3-5 short paragraphs. End with a question.
>
> Want me to run it now, or copy this filled prompt?

### Example 2 — Search by intent

> **User:** What's that prompt I used for the Stripe negotiation email?
>
> **Agent:** Found 2 matches for "negotiation email":
>
> | Slug | Tags | ⭐ | Used |
> |------|------|---|------|
> | **salary-counter** | career, negotiation, email, en | 5 | 12x |
> | offer-letter-followup | career, email | 3 | 1x |
>
> **salary-counter** (most likely — used 12x, ⭐5)
> > You are a senior negotiator drafting a counter-offer email to {{company}}. Total comp target: {{target}}. Current offer: {{current_offer}}. Anchor high, justify with market data, never apologize, close with a clear question…
>
> Variables: `{{company}}`, `{{target}}`, `{{current_offer}}`

### Example 3 — Cleanup

> **User:** Show me prompts I never used
>
> **Agent:** Found **8 prompts with 0 uses**, saved more than 14 days ago:
>
> | Slug | Saved | Days unused |
> |------|-------|-------------|
> | meeting-summary-zh | 2026-04-12 | 92 |
> | code-review-strict | 2026-05-03 | 71 |
> | … | … | … |
>
> 🗑️ Delete all 8? (y/n — I'll keep `meeting-summary-zh` since you tagged it `keep`)
> Or: *"delete the 6 oldest"*

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User pastes a giant prompt with no slug | Auto-generate slug from first 4-5 words + dedup check; ask for confirmation |
| Same slug, different content | Detect → either bump version or prompt *"Update existing v3?"* / *"Save as new slug?"* |
| User says *"find my prompt"* but library is empty | Reply: *"Library is empty. Save your first prompt: paste it and say 'save as…'"* |
| Variables in prompt but user gives only some | List provided values, **ask in one question** for missing ones — never silent-fail |
| User asks for prompt from memory but slug has changed | Fuzzy match by tag/content prefix; if no match, show closest 3 |
| Slug collision across versions (v2 saved twice) | Append timestamp suffix or auto-bump to v3 |
| Search returns too many results | Default to top 10 sorted by `usage_count × star_rating`; offer to narrow |
| Storage file corrupted / missing | Back up to `prompts.json.bak` before any write; on load, validate JSON; if fail, restore from `.bak` |
| User wants to export library | Provide `cp ~/.hermes/data/prompts.json ~/Desktop/prompts-export.json` |
| User wants to import from another tool | Define JSON schema in this file; write a tiny import script on demand |

---

## Verification Checklist

Before claiming a save / search / reuse is complete:

- [ ] Prompt content stored verbatim (no truncation, no LLM rephrasing)
- [ ] Variables correctly extracted from `{{...}}` patterns
- [ ] Tags auto-suggested from content + user-overridable
- [ ] Slug unique — checked against existing library before write
- [ ] `version` auto-bumped on edit (not on first save)
- [ ] Old content moved to `version_history[]` with timestamp
- [ ] `usage_count` incremented on every reuse
- [ ] `last_used` updated on every reuse
- [ ] Empty / missing fields get sensible defaults (not null)
- [ ] Destructive actions (delete / overwrite) require explicit yes
- [ ] JSON file valid after every write (`python3 -c "json.load(open(...))"`)
- [ ] Search returns ranked results (usage × rating, then recency)
- [ ] Response shows slug + tags + usage so user can verify at a glance

---

## Data Sources & Accuracy

- **Storage:** `~/.hermes/data/prompts.json` — single source of truth, plain JSON, no database
- **Search:** in-memory scan of JSON (works for libraries up to ~10,000 prompts); switch to SQLite FTS5 above that
- **Tag suggestions:** keyword extraction from prompt content (top 5 nouns + verbs), filtered against a stopword list
- **Variable detection:** regex `\{\{?(\w+)\}?\}` — supports both `{{var}}` and `{var}` styles
- **Star ratings:** user-set only; default 0 (unrated) on save
- **Version history:** unbounded — recommend user runs `cleanup` quarterly
- **No external API calls** — all operations local; safe for prompts containing proprietary info
- **Privacy:** prompts never leave the machine; export requires explicit user action

> 💡 **Tip:** Combine with `prompt-benchmarker` to A/B test which version of your saved prompt actually performs better — closes the loop between library and optimization.