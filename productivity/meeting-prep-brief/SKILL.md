---
name: meeting-prep-brief
description: "Generate a one-page pre-meeting brief from chat — attendee context from personal-crm, open threads from inbox-triage, last meeting's decisions, decision-journal entries, and a suggested agenda. Local-only, 5 minutes before any meeting."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, meetings, prep, brief, agenda, talking-points, 1on1, standup, manager, sales-call, knowledge-worker, local-first]
    related_skills: [calendar-optimizer, meeting-minutes-generator, personal-crm, inbox-triage, decision-journal, daily-briefing, weekly-review]
---

# 🎯 Meeting Prep Brief — 会前简报生成器

> Walk into any meeting already briefed. Hermes assembles a one-page pre-meeting brief in under 5 minutes — attendee context, open threads, last decision, suggested agenda, talking points, and risks to flag. 让任何会都"准备好了才进"。

---

## Overview

Most professionals walk into meetings **cold**: 47% admit they've been caught off-guard by a question in a 1:1 or client call (Asana *Anatomy of Work* 2024). The cost isn't embarrassment — it's that **underprepared meetings run 23% longer** and produce **31% fewer decisions** than briefed ones (Verizon Media / re:Work research). The reason isn't lack of information; it's that the information lives in five different places: your calendar, your CRM, your inbox, last meeting's minutes, and your head.

This skill turns Hermes into a meeting-prep assistant. You point it at an upcoming meeting (title, time, attendee names) and it pulls structured context from the skills already in your collection — `personal-crm` for attendee background, `inbox-triage` for open threads, `meeting-minutes-generator`'s archive for last meeting's decisions, `decision-journal` for pending reviews, `calendar-optimizer` for slot context — and synthesizes a one-page brief: who they are, what they want, what's open, suggested agenda, talking points, risks to flag. Output is markdown, pasteable into Notion/Obsidian/email.

| Capability | Description |
|------------|-------------|
| 🧑‍🤝‍🧑 Attendee dossier | Pull each attendee from `personal-crm` — last touchpoint, open follow-ups, sentiment, tier |
| 📧 Open-thread scan | Find recent emails from each attendee — unanswered threads, asks you owe |
| 📜 Last-meeting recap | Pull the prior meeting's minutes from `meeting-minutes-generator` archive — what was decided, what's open |
| 📒 Decision-journal pull | Surface pending decision reviews tied to this attendee or topic |
| 🎯 Agenda suggester | Generate a 3–5 item time-boxed agenda based on open items |
| 💬 Talking points | Pre-written questions, hypotheses to test, info to share |
| ⚠️ Risk flags | Topics attendees are likely to raise, sensitive decisions, blockers |
| 🧭 Meeting-type playbooks | Different briefs for 1:1, manager sync, sales call, standup, board, customer interview, all-hands |
| ⏱️ Time-budget aware | Brief respects meeting duration — 15-min sync ≠ 60-min review |
| 📄 Markdown / Plain text | One-page output, pasteable everywhere |
| 🛡️ Privacy-first | All cross-skill reads are local; no attendee data leaves your machine |

---

## When to Use

- *"Prep me for my 1:1 with Sarah at 2pm — she's the eng manager I met last month"*
- *"Generate a brief for the Acme sales call tomorrow at 10am"*
- *"What should I know before walking into the board meeting Friday?"*
- *"Brief me for my standup — 3 attendees, 15 min, what's open from yesterday?"*
- *"Give me a talking-points doc for the QBR with the customer success team"*
- *"Help me prep for a customer interview — they're a fintech PM team"*
- *"Pull everything we discussed last time with the VC, plus what's still open"*
- *"I'm about to walk into a salary negotiation — give me a brief"*
- *"Brief me for the all-hands — what did my team ship last week, what should I say?"*
- *"明天和老板的1:1，帮我准备一下会前简报"*
- *"客户会议前5分钟——给我一页纸brief"*

---

## Core Workflow

### Step 1: Identify the meeting

Accept any of these inputs:

```text
A) Calendar event description
   "Prep me for my 2pm with Sarah Chen (eng manager) — 30 min, project alpha sync"

B) ICS event block
   "Here's the .ics block: BEGIN:VEVENT … END:VEVENT"

C) Manual minimal spec
   "Tomorrow 10am, sales call with Acme Inc — John Buyer (CFO), Maya Champion (CTO). 45 min."
```

Extract or ask for these four fields:

| Field | Source | Fallback |
|-------|--------|----------|
| `meeting_type` | inferred from title/attendees | ask user |
| `attendees` | calendar / manual | ask user |
| `duration_min` | calendar | ask user |
| `topic` | calendar title | ask user |

**Meeting-type detection** (cheat-sheet — used to pick the right playbook):

| Title / signal pattern | Type | Playbook |
|------------------------|------|----------|
| `1:1`, `one-on-one`, `1-1`, `manager sync` | 1:1 | Personal, career, blockers, kudos |
| `standup`, `scrum`, `daily`, `15 min` | Standup | Yesterday / Today / Blockers only |
| `sales`, `demo`, `discovery call`, `pricing`, `proposal` | Sales | Buyer pain, ROI, next step |
| `customer interview`, `user research`, `usability` | Research | Hypotheses, open questions, no-pitch rule |
| `board`, `investor update`, `quarterly` | Board | KPIs, asks, narrative |
| `QBR`, `quarterly business review` | QBR | Wins, misses, next-quarter plan |
| `kickoff`, `project start`, `planning` | Kickoff | Goal, scope, risks, RACI |
| `retrospective`, `retro`, `lessons learned` | Retro | What worked / didn't / try next |
| `interview`, `candidate`, `hiring loop` | Interview | Rubric, probes, calibration |
| `all-hands`, `town hall` | All-hands | Wins, asks, AMA prep |
| `salary`, `comp`, `offer`, `negotiation` | Negotiation | BATNA, anchors, walk-away |
| `anything else` | Generic | Goals, agenda, decisions needed |

### Step 2: Pull cross-skill context

For each attendee, fan out local reads:

```bash
# 1) Attendee profile
ls ~/.hermes/personal-crm/contacts.json 2>/dev/null && \
  jq '.contacts[] | select(.name | test("Sarah Chen|Sarah C"; "i"))' \
     ~/.hermes/personal-crm/contacts.json

# 2) Recent interactions
jq --arg n "Sarah Chen" \
  '.contacts[] | select(.name==$n) | .interactions[-5:]' \
  ~/.hermes/personal-crm/contacts.json

# 3) Open follow-ups
jq --arg n "Sarah Chen" \
  '.contacts[] | select(.name==$n) | .follow_up' \
  ~/.hermes/personal-crm/contacts.json
```

For open email threads, if the user has run `inbox-triage`, surface from its cache:

```bash
ls ~/.hermes/inbox-triage/threads-*.json 2>/dev/null | tail -1 | \
  xargs -I{} jq --arg n "Sarah Chen" \
  '.[] | select(.from | test($n; "i")) | select(.status=="open")' {}
```

For prior meeting recap, look in `meeting-minutes-generator` archive:

```bash
ls ~/.hermes/meeting-minutes/archive/ 2>/dev/null | \
  grep -i "alpha\|sarah\|acme" | tail -3
```

For decision-journal pull:

```bash
ls ~/.hermes/data/decision-journal/ 2>/dev/null | \
  grep -i "alpha\|sarah\|acme" | head -5
```

**If a source doesn't exist**, don't fabricate — skip silently and note `unknown` in the brief. Never invent facts about people. If attendee is unknown to CRM, mark `[new contact — no history]`.

### Step 3: Generate the brief

Output a one-page Markdown document. Template (the only output format):

```markdown
# 📋 Meeting Prep — {TOPIC}
{YYYY-MM-DD HH:MM} · {DURATION_MIN} min · {MEETING_TYPE}

## 👥 Attendees
| Name | Role | Last touch | Open follow-ups | Sentiment |
|------|------|-----------|-----------------|-----------|
| Sarah Chen | Eng Manager, Acme | 2026-08-12 (kickoff) | intro to design partner | warm |

## 🎯 Why this meeting (your goals)
- {Goal 1 — concrete outcome}
- {Goal 2}

## 📌 Open threads (from inbox / past meetings)
- [ ] {Item 1 — owner, due date}
- [ ] {Item 2 — owner, due date}

## 🧭 Suggested agenda ({total_min} min)
1. {item} — {min} min — {purpose}
2. {item} — {min} min
3. Decisions needed: {list}

## 💬 Talking points / questions
- {Question 1 — to test hypothesis}
- {Question 2 — to surface risk}
- {Info to share — keep brief, 30 sec}

## ⚠️ Risks to anticipate
- {Likely tough question + your prepared answer}
- {Sensitivity — e.g., compensation, layoff rumor, escalation}

## 📚 Reference (deeper context)
- Last meeting: {filename or "n/a"}
- Decisions under review: {decision-journal entry or "none"}
- Related project: {link or "n/a"}

---
*Generated by meeting-prep-brief · {HH:MM} · local-only*
```

### Step 4: Tune by meeting type

Each playbook adjusts the **section weight**:

| Meeting type | Drop / shrink | Add / expand |
|--------------|--------------|--------------|
| **1:1** | "Reference" section | Add "Career/personal check-in" line; expand "Risks" to include their load |
| **Standup** | "Talking points", "Reference" | Replace "Agenda" with literal `Yesterday / Today / Blockers` |
| **Sales call** | "Risks" (downplay objections) | Add "Buyer pain hypotheses" + "ROI claim to test"; expand "Decisions needed" to next-step commit |
| **Customer interview** | "Talking points" (avoid leading) | Add "Hypotheses to test" + "What we will NOT pitch" |
| **Board / investor** | "Attendees" (names well-known) | Add "Top-line KPI", "Asks of board", "Bad-news handling" |
| **QBR** | Risks — soft-pedal | Add "Wins to celebrate", "Misses + postmortem", "Next-quarter bets" |
| **Kickoff** | "Open threads" | Add "Goal / non-goals", "RACI", "Top 3 risks" |
| **Retro** | "Goals" | Replace with "What worked / What didn't / What we'll try" |
| **Interview** | "Why this meeting" | Add "Rubric dimensions", "Probes", "Calibration anchors" |
| **All-hands** | "Attendees" (it's everyone) | Add "3 wins", "1 ask", "AMA prep — likely Qs" |
| **Negotiation** | generic agenda | Add "BATNA", "Anchors", "Walk-away number" |

### Step 5: Verify & ship

Before printing the brief, validate:

```text
✅ Required sections present (Attendees, Goals, Agenda, Talking points)
✅ Every attendee either has CRM context OR is marked [new contact]
✅ Every open thread has an owner and a due date or "TBD"
✅ Agenda total time ≤ meeting duration
✅ Risks section is not empty if meeting duration ≥ 30 min
✅ No fabricated facts (only sourced from local files or user-supplied input)
✅ Output fits on one page (~80 lines max)
```

If any check fails, fix in place before delivering. Never deliver a half-built brief.

---

## Example Invocations

### Example 1 — 1:1 with manager

**User:** *"Prep me for my 2pm with Sarah Chen (eng manager) — 30 min, project alpha sync. I haven't talked to her in 2 weeks."*

**Agent:**
> Generating brief. Pulling from personal-crm (last touch 2026-08-05, kickoff), inbox-triage (3 open threads), decision-journal (1 pending review on architecture choice).
>
> ```markdown
> # 📋 Meeting Prep — Project Alpha Sync
> 2026-08-20 14:00 · 30 min · 1:1
>
> ## 👥 Attendees
> | Name | Role | Last touch | Open follow-ups | Sentiment |
> |------|------|-----------|-----------------|-----------|
> | Sarah Chen | Eng Manager, Acme | 2026-08-05 (kickoff) | design partner intro, RFC review | warm |
>
> ## 🎯 Why this meeting
> - Confirm scope freeze for alpha milestone (was due last Friday)
> - Get her read on the auth refactor timeline — she's been quiet on the RFC
> - Unblock design-partner intro (you owe it 2 weeks)
>
> ## 📌 Open threads
> - [ ] YOU — Intro Sarah to design partner at Plaid (due 2026-08-08, overdue 12d)
> - [ ] SARAH — Sign off on RFC-014 (auth refactor) (due 2026-08-15, overdue 5d)
> - [ ] YOU — Send updated launch checklist (sent 2026-08-18, no reply)
>
> ## 🧭 Suggested agenda (30 min)
> 1. RFC-014 status & blockers — 8 min — decision: keep scope or descope auth?
> 2. Design-partner intro apology + new intro path — 5 min — re-commit date
> 3. Alpha milestone scope freeze — 10 min — decision: ship date
> 4. Sarah's load check-in — 5 min — open
> 5. Quick wins / kudos — 2 min — open
>
> ## 💬 Talking points
> - "Where's the resistance on RFC-014 — is it the timeline or the design?"
> - "What would help you most this week — heads-down time or more syncs?"
> - Share: design partner at Unit (not Plaid) replied — can intro this week
>
> ## ⚠️ Risks to anticipate
> - She may raise the missed intro. Lead with the apology, don't wait.
> - Auth refactor may have hidden infra cost — ask "what's the worst case you've seen?"
> - She's been quiet on Slack — might be load-related, not work-related.
>
> ## 📚 Reference
> - Last meeting: 2026-08-05-kickoff.md (kickoff doc)
> - Decision pending: 2026-07-25-auth-refactor.md (review due 2026-10-23)
> ```
>
> One flag: you owe her a design-partner intro from 12 days ago. I put the apology at minute 5 — earlier than the scope freeze — so it doesn't poison the rest of the meeting.

### Example 2 — sales call, last-minute

**User:** *"Brief me — Acme Inc sales call tomorrow 10am, 45 min. Attendees: John Buyer (CFO), Maya Champion (CTO). I'm pitching our enterprise tier."*

**Agent:**
> Generating brief. Both attendees are in personal-crm — last touch 2026-07-22 demo. Decision-journal shows a related open entry: "2026-07-18-enterprise-pricing.md" (pending review).
>
> ```markdown
> # 📋 Meeting Prep — Acme Inc Enterprise Pitch
> 2026-08-21 10:00 · 45 min · Sales
>
> ## 👥 Attendees
> | Name | Role | Last touch | Open follow-ups | Sentiment |
> |------|------|-----------|-----------------|-----------|
> | John Buyer | CFO, Acme | 2026-07-22 (demo) | ROI breakdown | analytical |
> | Maya Champion | CTO, Acme | 2026-07-22 (demo) | SSO/SAML docs | warm |
>
> ## 🎯 Why this meeting
> - Convert demo → paid enterprise trial
> - Surface any technical blockers Maya hasn't raised in writing
> - Land a specific next-step date, not "we'll be in touch"
>
> ## 📌 Open threads
> - [ ] YOU — Send ROI calculator to John (promised 2026-07-25, overdue 26d ⚠️)
> - [ ] YOU — SSO/SAML architecture doc to Maya (promised 2026-07-26, overdue 25d ⚠️)
> - [ ] JOHN — Send usage forecast by team (asked 2026-07-22, not received)
>
> ## 🧭 Suggested agenda (45 min)
> 1. Quick ROI recap (John's ask) — 8 min — frame the trial cost
> 2. SSO deep-dive (Maya's ask) — 12 min — show architecture, not slides
> 3. Trial scope proposal — 10 min — 30-day, 5 teams, conversion path
> 4. Pricing walkthrough — 8 min — anchor on enterprise tier, mention custom
> 5. Risks & open questions — 4 min — collect
> 6. Next step — 3 min — exact date for kickoff or proposal review
>
> ## 💬 Talking points
> - ROI: "Most enterprise customers see 3.2x in year 1 — here's how that math works for Acme."
> - SSO: open the dashboard live, don't show screenshots. Walk Maya through a real auth flow.
> - Trial: "I'd like to propose a 30-day, 5-team trial that converts to a paid annual on a specific date — what would that need to look like on your side?"
>
> ## ⚠️ Risks to anticipate
> - Both deliverables (ROI, SSO doc) are overdue by 25+ days. Lead with apology + fresh materials in the meeting, don't reference the originals.
> - John is "analytical" tier — he'll ask for numbers you don't have. Have a "let me get back to you by Friday" line ready.
> - Maya is warm but quiet. If she goes silent, ask her directly: "Anything blocking you that we haven't surfaced?"
>
> ## 📚 Reference
> - Decision pending: 2026-07-18-enterprise-pricing.md (review due — confirm pricing hasn't drifted)
> ```
>
> Heads-up: the overdue deliverables matter more than the pitch. If you walk in with the ROI calc and SSO doc freshly printed, the meeting changes character from "do they trust us" to "what's the trial scope." Want me to draft both before tomorrow?

### Example 3 — board meeting, week-before

**User:** *"Friday board meeting at 9am, 60 min. 4 VCs + my co-founder. Topic: pre-seed update. Generate a brief — what should I have ready?"*

**Agent:**
> Generating board-mode brief. No attendees in personal-crm (board investors are new context — marked `[new contact]`). No related decisions in journal. Defaulting to board playbook.
>
> ```markdown
> # 📋 Meeting Prep — Board Update (Pre-Seed)
> 2026-08-22 09:00 · 60 min · Board
>
> ## 👥 Attendees
> | Name | Role | Last touch | Open follow-ups | Sentiment |
> |------|------|-----------|-----------------|-----------|
> | [new contact] — VC #1 | Lead investor | — | — | unknown |
> | [new contact] — VC #2 | Partner | — | — | unknown |
> | [new contact] — VC #3 | Principal | — | — | unknown |
> | [new contact] — VC #4 | Angel | — | — | unknown |
> | Co-founder | Cofounder | daily | align on numbers | warm |
>
> ## 🎯 Why this meeting
> - Show 8-week traction vs plan
> - State the next round timing and amount
> - Surface 1 risk honestly (credibility > polish)
>
> ## 📌 Open threads
> - [ ] YOU — Align with co-founder on metric definitions (do this Wed, not Thu)
> - [ ] YOU — Send pre-read deck 24h before (Thu EOD)
>
> ## 🧭 Suggested agenda (60 min)
> 1. Top-line KPI walk — 10 min — retention curve, not vanity
> 2. What changed since last update — 10 min — wins + 1 honest miss
> 3. Hiring plan & runway — 10 min — explicit ask
> 4. Round timing & use of funds — 15 min — your ask
> 5. Q&A — 15 min — open
>
> ## 💬 Talking points
> - Anchor metric: choose ONE. Don't show 5 — pick the one that proves PMF or the gap.
> - "Here's what didn't work" — boards reward calibrated honesty. One slide, one paragraph.
> - Ask: "We're planning to raise in March — what conditions would make you more comfortable backing the next round?"
>
> ## ⚠️ Risks to anticipate
> - They WILL ask about runway. Have the exact months-of-runway number, not "we're fine."
> - One VC may push for "more metrics" — politely hold the line on the anchor.
> - Co-founder alignment risk: if you two disagree on a number in the room, you'll both look weak. Reconcile Wednesday.
>
> ## 📚 Reference
> - Last meeting: n/a (first board update)
> - Decisions pending: none related to board
> ```
>
> Three things I'd lock in before Friday: (1) the one anchor metric you and your co-founder agree on, (2) the runway number in months, (3) the one honest miss you choose to surface. Want me to draft the "what didn't work" paragraph?

---

## Common Pitfalls

| 问题 / Problem | 解决方案 / Solution |
|---|---|
| 跨 skill 数据不存在就开始脑补 | 不存在的字段一律 `unknown` 或 `[new contact]`；绝不编造人物背景或过往承诺 |
| 把所有会议都用同一模板 | 用 Step 1 的会议类型判断 + Step 4 的 playbook 调整；1:1 与 standup 的 brief 应该长得不一样 |
| Agenda 总时长超过会议时长 | 重新分配；如果时间不够，把"talking points"挪到会后异步，agenda 只保留决策项 |
| 漏掉未兑现的承诺（overdue 承诺） | 从 inbox-triage / decision-journal 自动扫描并排在 agenda 开头；这是"信任债"，必须先还 |
| 把 brief 写成传记 | 每个 attendee 限制 3 行：last touch / open follow-ups / sentiment；详情放 Reference 区 |
| 会议前 5 秒才想起来要 brief | 配 cron：meeting-prep-brief 在每场会议前 15 分钟自动触发（见 daily-briefing 模式） |
| 对陌生人编造 LinkedIn 式简介 | 标 `[new contact — no history]`；不联网、不推断行业、不脑补职位 |
| Talking points 写成剧本 | 列问题清单，不写逐字稿；过度准备的对话听起来像销售 |
| 忽略情感 / 人际信号 | sentiment 字段不是装饰；如果 CRM 显示"cool"，brief 必须显式提示"上次会议气氛偏冷" |
| 输出超过一页 | 严格控制 ≤80 行；长内容放进 Reference 区，让 brief 本身保持可扫读 |
| 跨设备读取 personal-crm 失败 | brief 启动时显式检查 `~/.hermes/personal-crm/contacts.json` 是否存在；不存在就只生成结构化空 brief |
| 用户说"随便准备一下" | 仍按完整流程跑，但把所有"未知"明确标注；不要因为用户不在意就降级质量 |

---

## Verification Checklist

- [ ] `meeting_type` 已识别或在 brief 顶部明确标注
- [ ] 每个 attendee 要么有 CRM 上下文，要么标注 `[new contact]`
- [ ] 每个 open thread 有 owner 和 due date（或明确标 "TBD"）
- [ ] Agenda 总时长 ≤ 会议时长
- [ ] Risks 区不为空（如果 meeting ≥ 30 min）
- [ ] Talking points 是问题清单，不是逐字稿
- [ ] 没有编造的人物信息、行业、职位或过往承诺
- [ ] 没有把凭证、token 或机密信息写入 brief
- [ ] 输出 ≤ 80 行（一页可读）
- [ ] 标注了所有未确认项为 `unknown` 或 `[待确认]`
- [ ] Reference 区引用了可追溯的文件名（last meeting / decision-journal entry）
- [ ] 跨 skill 数据缺失时显式提示用户，不是默默跳过

---

## Data Sources & Accuracy

- **首要数据源**：本地 `~/.hermes/personal-crm/contacts.json`、`~/.hermes/inbox-triage/threads-*.json`、`~/.hermes/meeting-minutes/archive/`、`~/.hermes/data/decision-journal/`、`~/.hermes/calendar-optimizer/events-*.json`。所有跨 skill 读取都是文件级，不联网。
- **用户实时输入**：会议标题、时间、参会者、议题——这些是 ground truth，brief 以此为锚。
- **推断标记**：sentiment（warm / cool / analytical / neutral）来自 CRM 历史交互记录，是已存推断而非实时心理分析，必须明确标注其依据是过去的交互而非当前心情。
- **联网禁止**：本 skill 默认不调用任何外部 API（不查 LinkedIn / 不查公司财报 / 不查新闻）。如需联网补充（如参会者新职位），必须用户显式同意且来源 URL 写进 Reference 区。
- **过期数据**：CRM / inbox / decision-journal 可能数日未更新；brief 应在 Reference 区标注每个数据源的"last sync"日期（如果可用），让用户判断可信度。
- **未确认项**：所有未在本地找到的数据标 `unknown` 或 `[待确认]`；不替用户编造、不替用户承诺。
- **隐私**：brief 默认仅输出到本地终端或用户剪贴板；不会自动上传到 Notion / Slack / 邮件。若用户要求分发，brief 内容中的人名、职位、内部代号属于敏感信息，需用户二次确认再分享。
- **不存储**：本 skill 不写自己的长期文件——所有输出都是临时 brief，不会污染其他 skill 的数据目录。

---