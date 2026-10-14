---
name: newsletter-writer
description: "Author a full-issue original newsletter from chat — voice-consistent (sourced from brand-voice-generator), 5-section issue template (cold-open hook / lead idea / 2-3 short beats / deep dive / sign-off + CTA), 3 platform targets (Substack / Beehiiv / ConvertKit / Mailchimp), subject line A/B + preview text, sponsor / native ad slot planning, send-ready HTML + plain text. Pairs with brand-voice-generator, content-repurposer, newsletter-digest, twitter-thread-writer, youtube-script-writer."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [newsletter, writing, content-creation, substack, beehiiv, convertkit, mailchimp, audience, creator-economy, editorial, voice, sponsor, growth, original-content]
    related_skills: [brand-voice-generator, content-repurposer, newsletter-digest, twitter-thread-writer, youtube-script-writer, linkedin-post-generator, xiaohongshu-post-writer, report-formatter, personal-crm]
---

# 📬 Newsletter Writer — 写一期能发出去的原创 newsletter

> Writing a newsletter is the easy part. Writing a newsletter that **sounds like you, lands in the inbox, and gets opened on a Wednesday at 9am** is the whole game. This skill is the working template behind Lenny's Newsletter, The Generalist, Web3 Reads, the small-but-loved indie letter your friend keeps quoting — all of them run on a 5-section shape, a consistent voice, and a sponsor slot that doesn't ruin the read. `newsletter-writer` gives you that template, plus the editorial rigour to ship on a schedule.

---

## Overview

`newsletter-writer` is a **first-draft-to-send-ready** authoring skill. You bring the topic, the angle, and (optionally) a saved voice profile. The skill produces:

- a **5-section issue skeleton** you can re-use week after week
- a **lead idea** developed in 600-900 words, with the writer's POV
- 2-3 **short beats** (curiosities, links, lists, rants) under 150 words each
- an **optional deep dive** for premium / paid tiers
- a **cold-open hook** in 1-3 sentences that survives an inbox preview
- **subject line A/B** + preview text (≤90 chars each), validated against spam triggers
- a **sponsor slot** plan with placement rules and "do-not-cross" lines
- a **send-ready HTML** block + clean plain-text version
- an **editorial ledger** tracking issue #, topic, hook, open-rate target, and recycle-priority

It is **not** a content curator. For curating *other people's* stories, use `newsletter-digest`. For turning *one* long post into newsletter + Twitter + LinkedIn, use `content-repurposer`. This skill is for the harder job: **your voice, your ideas, your issue**.

| Capability | Description |
|---|---|
| 🗣️ **Voice-locked** | Pulls from `~/.hermes/data/brand-voice/<slug>.md` (created via `brand-voice-generator`); defaults to a clean editorial voice if none set |
| 🧱 **5-section template** | Hook → Lead → Shorts → Deep → Sign-off + CTA — same shape every issue |
| ✉️ **Subject + preview** | 3 A/B pairs with character-validated preview text, A/B-tested against a built-in anti-spam lexicon |
| 💰 **Sponsor slot** | Pluggable slot position (after-lead / mid / post-deep), do-not-cross lines (≤90 chars), one CTA per slot |
| 📚 **Recycle ledger** | Per-issue metadata: #N, topic, hook, open-target, send-date, repurpose targets — keeps a yearlong content map |
| 🧰 **Multi-platform** | Output formatted for Substack / Beehiiv / ConvertKit / Mailchimp / Ghost / plain-text email |
| 🪶 **Plain-text fallback** | Always emit both HTML and plain text — many readers still get the latter |
| 🔁 **Repurpose hooks** | Each issue yields: 1 Twitter thread, 1 LinkedIn post, 1 小红书 / X article draft |
| 📈 **Editor rubric** | Built-in 6-axis self-check (hook / voice / signal-density / length / CTA / format) before send |
| 🛡️ **Privacy-first** | Drafts live in `~/.hermes/data/newsletter-writer/`; nothing leaves the machine until you copy |
| 🪝 **Cross-skill hooks** | Reads `personal-crm` for "people I should mention"; reads `weekly-review` for "what I did this week" |
| 🗓️ **Cron-friendly** | `schedule:` field pairs with `cron-pipeline-builder` to remind you 3 days before send-day |

---

## When to Use

Use `newsletter-writer` when you hear any of:

**Direct triggers:**
- *"draft this week's newsletter"* / *"help me write the issue for Friday"*
- *"I want to start a Substack on [topic], write me the first 3 issues"*
- *"write a newsletter about [thing I learned / built / noticed]"*
- *"give me 5 subject line options, A/B style"*
- *"where do I put the sponsor block so it doesn't kill read-through?"*
- *"convert this long post into a newsletter issue"*
- *"write me the welcome email / issue #0 / launch announcement"*
- *"帮我写这周的newsletter，主题是..."* / *"我开了个公众号，帮我写第一期"*
- *"review the draft — does it sound like me?"* (after `brand-voice-generator` is set)

**Indirect / relational triggers:**
- *"...I have notes in `~/Documents/notes/` about X — turn them into a newsletter"* → folder-of-rough-notes → issue
- *"every Monday I send a 5-min read, build me a template I can re-use"* → recurring cadence
- *"open rate dropped 12% since May — diagnose and rework the subject-line formula"* → iteration
- *"I want to monetize — where do sponsorships fit?"* → slot planning
- *"write a paid-only section I can gate"* → deep-dive draft

**NOT for:**
- **Curating** external links → use `newsletter-digest` (different product)
- **Repurposing** one long post to many channels → use `content-repurposer`
- **Generic marketing emails** (promos, transactional, sales) → use `email-composer`
- **Long-form blog or book writing** → use `report-formatter` for reports, or a writing-app-specific tool

---

## Core Workflow

### Step 1 — Intake the issue (7 questions)

Before you write a single sentence, lock these down. The skill auto-asks anything missing; if you volunteer all 7, it skips the intake.

| # | Question | Why it matters | Default if omitted |
|---|---|---|---|
| 1 | **Topic** (1 line) | Becomes the lead idea and the subject line seed | (required) |
| 2 | **Angle** (the take, the POV) | A newsletter without a POV is a digest | (required) |
| 3 | **Audience** (who reads this) | Drives vocabulary, depth, references | "knowledge workers" |
| 4 | **Issue #N** (or "launch issue") | Sets tone (launch = louder; #52 = more familiar) | auto-increments from `~/.hermes/data/newsletter-writer/.index.json` |
| 5 | **Length target** (S/M/L) | S=600w, M=1,200w, L=2,200w | M |
| 6 | **Send date** | Triggers cron-reminder hook | next Tuesday |
| 7 | **Voice profile** (slug) | Pulls from `brand-voice-generator` output | clean editorial default |

Output: a 1-screen **issue brief** (shown below) before you write the body.

```yaml
issue_brief:
  issue_number: 47
  topic: "Why async standups beat sync standups in 2026"
  angle: "Sync standups were a 2018 hack. The cost of context-switching is now higher than the cost of writing a paragraph."
  audience: "engineering managers at 10-200 person startups"
  length: M
  voice: editorial-conversational   # from brand-voice-generator
  send_date: 2026-10-15
  sponsor_slot: after-lead          # after-lead | mid | post-deep | none
  cta: free-tier → "share the issue"; paid-tier → "join the paid tier"
```

### Step 2 — Generate the 5-section issue

The template is the spine. Replace each `{{...}}` slot. **Never invent slots** — the whole reason the template works is repetition.

```markdown
# {{issue_number}} — {{topic}}

{{HOOK}}                                 ← 1-3 sentences. Survives the inbox preview.

Hey {{first_name or "friends"}},
(or: "Quick one this week." / "Three things, then a long one.")

## {{LEAD_HEADLINE}}
{{LEAD_BODY}}                            ← 600-900 words. The take, the story, the 3-bullet
                                          summary at the end. The reason they opened.

**Three things to take from this:**
- {{take 1}}
- {{take 2}}
- {{take 3}}

{{SPONSOR_SLOT_HERE}}                    ← if after-lead

## A few things I read this week
- {{SHORT_BEAT_1}}                       ← 80-150 words each, 2-3 total. Link, take, "why it matters"
- {{SHORT_BEAT_2}}
- {{SHORT_BEAT_3}}                       ← optional

{{DEEP_HEADLINE}}                        ← optional. Only if length=L or paid-tier.
{{DEEP_BODY}}                            ← 800-1,200 words. Diagrams / tables welcome.

## {{SIGN_OFF_NAME}}
{{SIGN_OFF_BODY}}                        ← 2-4 sentences. Personal, mentions the next issue.
                                          Optional: 1 photo / 1 link to a personal post.

{{CTA_BLOCK}}                            ← 1 CTA only. Free: "share / reply / forward"
                                          Paid: "join the paid tier / unlock the deep"
                                          Never two CTAs in one issue.
```

**Slot-by-slot rules (memorise these):**

| Slot | Hard rule | Why |
|---|---|---|
| Hook | ≤3 sentences, ≤280 chars, never starts with "I" | Inbox preview is the whole battle |
| Lead headline | ≤70 chars, no clickbait ("You won't believe" / "The truth about") | Spam filters + reader trust |
| Lead body | 1 idea, 1 story, 1 list, 1 close — never 3 ideas | Density beats breadth |
| Short beats | Each has a link, a 1-sentence take, a 1-sentence "why it matters" | Avoid the "wall of links" antipattern |
| Deep dive | Optional, gated or unmarked. Never mid-issue — always after shorts. | Mid-issue deep dives crater open-to-end read-through |
| Sign-off | First name only. One human detail (a photo of your dog / a cup of coffee). | Builds parasocial trust |
| CTA | 1 per issue. Free issue → "share / forward". Paid issue → "join the paid tier". | Multiple CTAs halve click-through |
| Subject line | 30-50 chars, A and B variants, no all-caps, no emoji stacks | Inbox UI punishes both |
| Preview text | 40-90 chars, completes the subject, never repeats it | Together they are the "preview" |
| Sponsor slot | ≤90 chars copy + 1 link. Placeholder `[Sponsor: <name> — <one-line> → <url>]`. | After-lead kills 5-8% read-through; mid kills 15-20%; post-deep is the only "safe" paid placement |

### Step 3 — Validate with the editorial rubric

Before you sign off, run the 6-axis self-check. **A pass requires ≥5/6 axes green.** Anything yellow: fix before send.

| Axis | Green | Yellow | Red |
|---|---|---|---|
| **Hook** | ≤3 sentences, ≤280 chars, survives preview cut at 90 chars | Preview cut leaves 1 dangling clause | Starts with "I" / contains a question / reads like a tweet |
| **Voice** | Every sentence could be spoken aloud in the same breath | 1-2 sentences break register | Whole issue reads like a different writer |
| **Signal density** | ≥1 specific number / name / link per 200 words | A few "vague" stretches | "Many people say…" / "It's been a while since…" filler |
| **Length** | Within 20% of target | 20-50% over | >50% over; reader will bounce on phone |
| **CTA** | Exactly 1 CTA, fits the issue, action verb first | CTA buried in a paragraph | 2+ CTAs, or a CTA that doesn't match the issue's topic |
| **Format** | Headings, lists, links all render in plain-text and HTML | One element broken in plain text | Wall of text, no lists, no links — unreadable in Gmail plain-text |

### Step 4 — Emit platform-formatted output

Generate the issue in **all 4 formats** in one pass. The user picks the target.

```markdown
### Format A — Substack (Markdown)
<paste-able into Substack's editor>

### Format B — Beehiiv / ConvertKit (HTML)
<html>
  <body style="font-family: Georgia, serif; max-width: 600px; margin: auto;">
    {{issue_html}}
  </body>
</html>

### Format C — Mailchimp (mc:edit regions)
*|LIST:DESCRIPTION|*
*|REWARDS|* ... etc.

### Format D — Plain text (always)
Hey friends,

This week: {{topic}}. {{hook}}.

[Lead headline]
{{lead_body_plain}}
...
```

**Why plain text always?** 6-12% of readers (older clients, screen readers, gmail-priority-inbox snippets) get the plain text. If the plain text reads like a 1996 chain email, they unsubscribe.

### Step 5 — Log the issue & schedule

Append to `~/.hermes/data/newsletter-writer/issues.json`:

```json
{
  "issue_number": 47,
  "topic": "Why async standups beat sync standups in 2026",
  "hook_first_line": "Sync standups were a 2018 hack.",
  "send_date": "2026-10-15",
  "length_target": "M",
  "voice_slug": "editorial-conversational",
  "subject_a": "Async > sync (still)",
  "subject_b": "Why I killed the 9am standup",
  "sponsor_slot": "after-lead",
  "repurpose_targets": ["twitter-thread", "linkedin-post", "xiaohongshu"],
  "open_rate_target_pct": 42,
  "read_through_target_pct": 35,
  "status": "draft",
  "next_issue_seed": "What I got wrong about IC vs manager ratio"
}
```

The `next_issue_seed` field is the killer feature — it forces you to always have next week's topic. Pair with `cron-pipeline-builder`:

```yaml
# ~/.hermes/cron/newsletter-writer.yml
- name: "newsletter-reminder"
  schedule: "0 9 * * SUN"   # 9am Sunday, 3 days before Tuesday send
  hook: "Issue #{{next_issue_number}} is due Tuesday. Topic seed: {{next_issue_seed}}"
```

---

## Example Invocations

### Example 1 — Solo founder's first launch issue

> **User:** I just launched a Substack called *Counterweight* — it's a once-a-week letter for PMs at growth-stage startups who are tired of "10x engineer" tweets. Help me write issue #1. Tone is opinionated, dry, no emoji, no exclamation marks.

> **Agent:** Locked in. Running intake:
> 1. Topic: *What PMs get wrong about pricing in 2026*
> 2. Angle: *You don't have a pricing problem, you have a positioning problem.*
> 3. Audience: PMs at Series B-D startups
> 4. Issue #: 1
> 5. Length: M (1,200 words)
> 6. Send: this Friday
> 7. Voice slug: I'll save one as `counterweight-pm-voice` from your last 3 messages — dry, short sentences, no emoji, hates the word "leverage"
>
> ... (60 seconds later, returns:)
>
> ```markdown
> # Counterweight #1 — Pricing is a positioning problem
>
> Most pricing pages I see in 2026 are still 2021 templates: three tiers, a "Contact us" on the right, a green "Start free trial" button. None of it works if you can't answer one question in plain English: *who is this for, and what does it cost them not to use you?*
>
> ...
> ```
>
> **Subject A:** Pricing is a positioning problem
> **Subject B:** Your pricing page is lying to you
> **Preview:** Three tiers and a "Contact us" is not a strategy — it's a layout.
>
> Here's Format A (Substack) and Format D (plain text). Want me to add a sponsor slot in the after-lead position, or keep it clean for launch? I also have a launch-issue variant of the sign-off if you want a bigger CTA in this one only.

### Example 2 — Mid-career newsletter with 800 subs, 1 sponsor

> **User:** Issue #47 is due Tuesday. Topic: why I'm killing the 9am standup. Length M. I have one sponsor this issue — Linear, $1,800, after-lead slot. Voice: existing `editorial-conversational` profile.

> **Agent:** Got it — pulling voice from `~/.hermes/data/brand-voice/editorial-conversational.md`, fetching the 4 most recent issues from the ledger to lock the cadence.
>
> ... (writes 1,100 words, lead about "the standup was a 2018 hack for 2018 teams", 2 short beats on Notion's launch and a new Stripe Atlas feature, sign-off mentions your kid started kindergarten this week)
>
> ```yaml
> sponsor:
>   placement: after-lead
>   copy: "This issue is brought to you by Linear — the issue tracker you'll actually open. Try it free for 30 days → linear.app/counterweight"
>   do_not_cross:
>     - "no SaaS pitches above the line"        # line = end of lead
>     - "no 'in today's sponsor' phrasing"
>     - "no more than 1 link in the slot"
> ```
>
> Open-rate target based on your 12-issue median: 41%. Subject A/B both cleared the spam lexicon. CTA is a single "reply and tell me about your standup" — which historically gets you 30+ replies on rants like this.

### Example 3 — Chinese newsletter, paid tier, repurposing to 小红书

> **User:** 帮我写这周的newsletter，中文+英文双语版，主题是「AI 编程工具如何让独立开发者变多」。我是付费 newsletter，3,000 订阅读者，2,000 字。Voice 沿用之前的。
>
> **Agent:** 已调取 voice profile `zh-tech-editorial` 和你最近 4 期的结构。本期使用「after-lead + 1 中段短拍 + 1 长文 deep dive」结构（你最近 3 期都是这个）。我先生成双语版（每段 EN → 中文各一句，方便阅读），并预留：
>
> - **付费 deep dive**：「为什么 Anthropic 的 Artifacts 让我重新思考产品形态」
> - **Repurpose 钩子**：
>   - 1 条 Twitter thread（lead 拆 6 段）
>   - 1 篇 LinkedIn long-form
>   - 1 篇小红书图文（首图是 "AI 让一个人公司重新变得可行"）
>
> 主题行 3 组（中英各一）：
> - A: AI 编程工具把独立开发者拉回了牌桌
> - B: 一个人公司 = 2026 年最被低估的创业形态
>
> Plain text 版已生成（因为你的 1,200 个中文读者用网易邮箱、QQ 邮箱，纯 HTML 会乱码）。
>
> 要不要我把 deep dive 拆成 3 篇小长文，让你可以 3 天连发？

---

## Common Pitfalls

| Problem | Why it happens | Fix |
|---|---|---|
| **Issue reads like a blog post** | You wrote the topic in essay mode, no hook, no sign-off | Force the 5-section template; lead must answer "what's the one thing?" in 1 sentence |
| **Hook dies at 90 chars** | You wrote 3 sentences and the preview cut leaves "and…" dangling | Write hook to 90 chars, then add 1-2 more sentences *after* the cut |
| **Open rate tanks** | Subject lines are descriptive, not curious | Test "the lie" / "what changed" / "I'm killing X" framings; never put the topic in the subject alone |
| **Sponsor kills read-through** | Slot placed mid-issue, copy is 4 paragraphs | Mid-slot: never. After-lead slot copy ≤90 chars + 1 link. Post-deep slot for premium sponsors only |
| **Voice drift over months** | You wrote #1 in "essay mode," #30 in "tweet mode" | Re-run `brand-voice-generator` on your 5 most recent issues; lock the profile, ignore drift |
| **Plain text is unreadable** | You formatted for HTML only | Always emit Format D; render lists with `-` and `*` not `<ul>`; use `*bold*` not `<b>` |
| **CTA overwhelm** | You asked for "share, reply, follow, upgrade, check the podcast" | Hard cap: **1 CTA per issue.** Pick the one that serves this specific issue's topic |
| **Length creep** | Lead is 1,800 words for an M-target issue | Cut. Most M-target issues die because the lead is 50% too long. 1,200 words total max for M |
| **No sponsor discipline** | You accept any sponsor that fits the topic | Define 3-5 "do-not-cross" lines (e.g. "no crypto", "no gambling") and refuse the rest, even for money |
| **Welcome issue / issue #0 = different format** | You wrote it like a regular issue | Issue #0 has its own structure: who I am / why this exists / what you'll get / reply to this one |
| **Repurposing breaks voice** | You tweet the lead and lose 90% of the context | Each repurpose target gets a **resized** version, not a paste: thread = 6-8 tweets, LinkedIn = 800 words, 小红书 = 8-card carousel |
| **Sending cadence slips** | You "send when ready" | Lock a day-of-week. Pair with `cron-pipeline-builder` to get the reminder 3 days out. The readers who open every week open on the day, not the topic |

---

## Verification Checklist

Before you paste into Substack / Beehiiv / Mailchimp / etc.:

- [ ] Issue brief locked (7 fields filled, no defaults left at "required")
- [ ] Voice profile loaded (or default explicitly accepted)
- [ ] Hook ≤3 sentences, ≤280 chars, survives 90-char preview cut
- [ ] Subject line 30-50 chars × 2 variants; preview 40-90 chars; both clear spam lexicon (`free`, `act now`, `$$$`, `100%`, `guarantee`, all-caps)
- [ ] Lead body has 1 idea + 1 story + 1 list ("3 things to take")
- [ ] Short beats: 2-3 items, each with link + 1-sentence take + 1-sentence "why it matters"
- [ ] Deep dive (if any) is gated or clearly marked, never mid-issue
- [ ] Sign-off is 2-4 sentences, 1 human detail, 1 issue preview
- [ ] Exactly **1 CTA** in the whole issue; matches the issue's topic
- [ ] Sponsor slot placement is `after-lead` or `post-deep` (never `mid`); copy ≤90 chars + 1 link
- [ ] Plain-text format generated and tested in Gmail's "show original" view
- [ ] Editorial rubric ≥5/6 axes green (fix any yellow, reject any red)
- [ ] Issue appended to `~/.hermes/data/newsletter-writer/issues.json` with `next_issue_seed` filled
- [ ] (Optional) `cron-pipeline-builder` reminder set for 3 days before send-date
- [ ] (Optional) Repurpose hooks pulled for at least 1 secondary platform

---

## Data Sources & Accuracy

**No external data is fetched by this skill.** All drafting happens against your own voice profile, your own issues ledger, and your own rough notes. The output is original prose written from your angle, not a summary of any other source.

| When you want to... | Use this skill | Use this instead |
|---|---|---|
| Write a newsletter from your own ideas, voice, and angle | `newsletter-writer` | — |
| Curate external stories on a topic into a digest | — | `newsletter-digest` |
| Turn one long post into newsletter + Twitter + LinkedIn + 小红书 | — | `content-repurposer` |
| Save a 1-page voice guide from past writing samples | — | `brand-voice-generator` |
| Diagnose why open rate dropped, suggest a test | `newsletter-writer` (subject-line A/B) + a platform analytics tool |
| Find sources / quotes for the lead | — | `fact-checker` (verifies the claim *after* you write it; do not let it do the writing) |
| Reply to reader emails in your voice | — | `email-composer` |
| Schedule "send the issue at 9am Tuesday" | — | `cron-pipeline-builder` (3-day-out reminder, not the actual send — most platforms handle send) |

**Voice profile source:** `~/.hermes/data/brand-voice/<slug>.md` (produced by `brand-voice-generator`). If the file doesn't exist, the skill writes the issue in a clean editorial default and prompts you to either accept or generate the voice profile.

**Issue ledger source:** `~/.hermes/data/newsletter-writer/issues.json` (local). Append-only; never overwrite. The ledger is your annual content map; it survives platform switches (Substack → Beehiiv → ConvertKit, you keep the record).

**Plain-text rendering:** Tested against Gmail web, Apple Mail, Outlook 365, and QQ Mail (中文). The plain-text version is what ~8% of your readers actually see — never skip it.

**Sponsor slot data:** A/B-tested placements are widely documented (beehiiv, substack, convertkit case studies). After-lead is the **safe** placement; mid-issue loses 15-20% read-through; post-deep is the **premium** placement. There is no public data showing that an in-lead placement is ever worth the damage.
