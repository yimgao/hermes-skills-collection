---
name: meeting-minutes-generator
description: "Transform raw meeting notes, transcripts, or voice memo summaries into structured meeting minutes with action items, decisions, attendees, and follow-ups."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [meeting, minutes, notes, communication, productivity, action-items, collaboration]
    related_skills: [email-composer, presentation-helper, study-planner, flashcard-generator]
---

# 📝 Meeting Minutes Generator — 会议纪要生成器

> Transform raw meeting notes, transcripts, or voice memo summaries into clean, structured meeting minutes with action items, decisions, and follow-ups. 将原始会议记录、转录文本或语音备忘摘要整理为结构清晰的会议纪要，包含行动项、决策和跟进计划。

---

## Overview

| Capability | Description |
|------------|-------------|
| **Raw Notes → Minutes** | Turn messy bullet points or free-form notes into structured minutes |
| **Transcript Processing** | Extract decisions and action items from full meeting transcripts |
| **Voice Memo Summary** | Accept brief spoken-note summaries and expand into proper minutes |
| **Action Item Extraction** | Auto-detect owners, deadlines, and responsibilities |
| **Decision Logging** | Capture key decisions with rationale and context |
| **Follow-up Scheduling** | Generate next-meeting agenda items and check-in dates |
| **Multi-format Output** | Markdown, plain text, or JSON for integration with other tools |
| **Chinese/English Bilingual** | Input and output in either language, or mixed |

---

## When to Use

- *"I just had a 30-minute standup — here are my notes, turn them into minutes"*
- *"Here's the transcript from our sprint planning, extract action items"*
- *"Turn these meeting notes into a formatted minutes document with owners and deadlines"*
- *"Generate follow-up items from yesterday's client call notes"*
- *"帮我整理一下这次会议记录，生成正式的会议纪要"*
- *"从这段对话中提取所有决策点和待办事项"*

---

## Core Workflow

### Step 1: Collect Input Material

Accept any of these forms:

| Input Type | Example | Best For |
|------------|---------|----------|
| **Free-form bullet points** | `- Discussed API v2 timeline\n- John will draft spec by Friday` | Quick standups, informal syncs |
| **Full conversation transcript** | Multi-turn dialogue with timestamps | Client calls, detailed reviews |
| **Voice memo summary** | 2-3 sentence spoken recap | Post-call quick notes |
| **Structured agenda + notes** | Pre-existing agenda with scribbles | Formal board/steering meetings |

Ask the user to paste their raw material. If the material is sparse, ask clarifying questions:

- How many people attended? Who were they?
- What was the meeting type? (standup / sprint planning / client call / 1:1 / board meeting)
- Duration?
- Any decisions made that aren't explicitly noted?

### Step 2: Structure the Minutes

Use this template to organize output. Maintain the original language of the input.

```markdown
# Meeting Minutes: {Meeting Title}

**Date:** {YYYY-MM-DD}
**Time:** {start} – {end}
**Duration:** {N minutes}
**Type:** {Standup / Sprint Planning / Client Call / 1:1 / Design Review / Board / Other}
**Location:** {Zoom / In-person / Slack thread / Phone}

## Attendees
- {Name} ({Role}) — Present
- {Name} ({Role}) — Present
- {Name} ({Role}) — Apologies / Absent

## Agenda
1. {Topic 1}
2. {Topic 2}
3. {Topic 3}

---

## Discussion Summary

### 1. {Topic 1}
{2-3 sentence summary of what was discussed, key points raised, and any disagreements or open questions.}

### 2. {Topic 2}
{2-3 sentence summary.}

### 3. {Topic 3}
{2-3 sentence summary.}

---

## Key Decisions

| # | Decision | Rationale | Decided By |
|---|----------|-----------|------------|
| 1 | {Decision} | {Why} | {Who} |
| 2 | {Decision} | {Why} | {Who} |

## Action Items

| # | Action | Owner | Deadline | Status |
|---|--------|-------|----------|--------|
| 1 | {What needs to be done} | @{Name} | {YYYY-MM-DD} | 🟡 In Progress |
| 2 | {What needs to be done} | @{Name} | {YYYY-MM-DD} | 🔴 Not Started |
| 3 | {Follow up with client on pricing} | @{Name} | EOW | 🟢 Complete |

## Next Steps
- {Next meeting scheduled: YYYY-MM-DD}
- {Check-in on item #2 before next sync}
- {Share minutes with wider team}

---

*Minutes prepared by Hermes Meeting Minutes Generator*
*Reviewed by: {Name}*
```

**Rules:**
- If action items lack an explicit owner, flag them: `⚠️ No owner assigned — suggest: @{Name}?`
- If deadlines are missing, prompt: `⏰ No deadline set — recommend: end of week?`
- Preserve the user's original language; do not translate unless asked.
- If the input is clearly Chinese, output in Chinese; if English, output in English. For mixed input, default to the dominant language.
- Maintain a neutral, factual tone. Do not editorialize.

### Step 3: Validate & Deliver

After generating the minutes:

1. **Check for ambiguity**: Are all attendees named? Are all decisions logged?
2. **Flag missing owners**: Every action item needs an owner. If missing, call it out.
3. **Flag missing deadlines**: Every action item needs a deadline. If missing, suggest a reasonable one.
4. **Offer format choice**: Markdown (default), plain text, or JSON.
5. **Offer follow-up**: *"I can also draft a follow-up email to share these minutes — just say the word."*

---

## Example Invocations

### Example 1: Standup Notes → Minutes

**User:**
```
Here are my standup notes from this morning:
- Ali: Finished auth module, PR up for review
- Busy working on payment integration, blocked by API key
- Mei: Design mocks ready for review, link in Figma
- Discussed: need to decide on DB migration strategy this week
- Decision: Use PostgreSQL, no more debating
- Action: Sam to write migration plan by Thursday
```

**Agent output:**
```markdown
# Meeting Minutes: Daily Standup

**Date:** 2026-06-26
**Duration:** ~15 minutes
**Type:** Daily Standup

## Attendees
- Ali
- Busy
- Mei
- Sam (mentioned, not present)

## Discussion Summary

### Progress Updates
- **Ali:** Auth module complete. PR is open for review.
- **Busy:** Payment integration in progress — blocked by missing API key. Needs unblock.
- **Mei:** Design mocks ready in Figma. Ready for team review.

### Key Discussion
Team aligned on database migration strategy — consensus reached after debate.

## Key Decisions

| # | Decision | Rationale | Decided By |
|---|----------|-----------|------------|
| 1 | Use PostgreSQL for the project | Ends ongoing debate; aligns with infra team's existing expertise | Team consensus |

## Action Items

| # | Action | Owner | Deadline | Status |
|---|--------|-------|----------|--------|
| 1 | Write database migration plan | @Sam | 2026-06-29 (Thu) | 🔴 Not Started |
| 2 | Unblock payment integration API key | @Busy | 2026-06-27 | 🔴 Not Started |
| 3 | Review Ali's auth module PR | @Mei, @Sam | 2026-06-27 | 🟡 In Progress |

## Next Steps
- Next standup: tomorrow same time
- Sam to share migration plan before Thursday's sync
- Mei to share Figma link in team channel
```

---

### Example 2: Client Call Transcript → Minutes

**User:**
```
Client call transcript (edited):
Me: Can you confirm the deadline for phase 1?
Client (Sarah): We need it by July 15, no later.
Me: Got it. And the budget cap we discussed?
Client (Sarah): $45k total, $25k for phase 1, $20k for phase 2.
Me: Who's our point of contact for technical questions?
Client (Sarah): Our engineer Leo will be the main contact. I'll intro you via email.
Me: One more thing — do you want weekly or bi-weekly progress reports?
Client (Sarah): Weekly please. Every Friday by EOD.
Decision: Phase 1 scope frozen as-is, no additional features.
```

**Agent output:**
```markdown
# Meeting Minutes: Client Call — Project Sync

**Date:** 2026-06-26
**Duration:** ~20 minutes
**Type:** Client Call

## Attendees
- You (Your Company)
- Sarah (Client — Decision Maker)
- Leo (Client — Technical Contact, mentioned)

## Discussion Summary

### Phase 1 Deadline
Client confirmed hard deadline of **July 15**. No extensions possible.

### Budget Confirmation
- Total budget: **$45,000**
- Phase 1 allocation: **$25,000**
- Phase 2 allocation: **$20,000**

### Communication
- Weekly progress reports required — due every **Friday by EOD**
- Leo will be the technical point of contact (intro email pending)
- Sarah to make email introduction

## Key Decisions

| # | Decision | Rationale | Decided By |
|---|----------|-----------|------------|
| 1 | Phase 1 scope frozen — no additional features | Must meet July 15 deadline | Sarah (Client) |
| 2 | Weekly reporting cadence (Fridays EOD) | Client preference for frequent updates | Sarah (Client) |

## Action Items

| # | Action | Owner | Deadline | Status |
|---|--------|-------|----------|--------|
| 1 | Send intro email connecting Leo as technical POC | @Sarah (Client) | 2026-06-28 | 🔴 Not Started |
| 2 | Set up weekly report template | @You | 2026-06-28 | 🔴 Not Started |
| 3 | First weekly progress report | @You | 2026-07-03 (Fri) | 🔴 Not Started |

## Next Steps
- Wait for Sarah's intro email with Leo
- Prepare weekly report template
- Schedule next sync for week of June 30
```

---

### Example 3: Chinese Input — 中文会议记录

**用户：**
```
今天下午的产品评审会笔记：
- 张伟：新版本用户反馈不错，但首页加载慢了200ms
- 李婷：建议加个骨架屏，预计2天开发
- 王芳：竞品分析显示他们都做了深色模式
- 决定：Q3做深色模式，优先级P2
- 决定：骨架屏本周就做，P1
- 行动：李婷出骨架屏设计方案，周五前
- 行动：王芳整理深色模式竞品报告，下周三
```

**Agent 输出：**
```markdown
# 会议纪要：产品评审会

**日期：** 2026-06-26
**时长：** ~30分钟
**类型：** 产品评审

## 参会人员
- 张伟（产品）
- 李婷（前端开发）
- 王芳（设计）

## 讨论摘要

### 用户反馈与性能问题
新版本用户反馈整体正面，但首页加载速度变慢约200ms。需要优先解决性能回归问题。

### 骨架屏方案
李婷提出添加骨架屏（Skeleton Screen）以改善首屏加载体验，预计开发时间2天。团队一致同意立即执行。

### 深色模式规划
王芳分享了竞品分析结果——主要竞品均已支持深色模式。团队决定纳入Q3规划。

## 关键决策

| # | 决策 | 原因 | 决策者 |
|---|------|------|--------|
| 1 | 骨架屏本周开发，优先级 P1 | 解决首页加载体验问题 | 团队一致 |
| 2 | 深色模式 Q3 实施，优先级 P2 | 竞品已支持，但非紧急 | 团队一致 |

## 待办事项

| # | 行动 | 负责人 | 截止日期 | 状态 |
|---|------|--------|----------|------|
| 1 | 出骨架屏设计方案 | @李婷 | 2026-06-28 (周五) | 🔴 未开始 |
| 2 | 整理深色模式竞品分析报告 | @王芳 | 2026-07-02 (下周三) | 🔴 未开始 |
| 3 | 修复首页 200ms 加载延迟 | @张伟 | 2026-06-27 | 🟡 进行中 |

## 后续步骤
- 下次评审会：下周一同一时间
- 李婷完成设计后发起 PR review
- 王芳报告完成后同步给团队
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| **Input is too sparse** (e.g., only 1-2 bullet points) | Ask clarifying questions before generating: Who attended? Any decisions? What's the next step? |
| **Meeting type unclear** | Infer from content (standup = daily progress, sprint planning = story points/backlog, client call = requirements/budget) — if ambiguous, ask |
| **No explicit owners for action items** | Flag: `⚠️ No owner — suggest @{Person} based on context?` |
| **No deadlines mentioned** | Flag: `⏰ No deadline set — recommend end of week / next meeting?` |
| **Mixed Chinese/English input** | Default to the dominant language. If roughly equal, ask the user which language they prefer for output |
| **Multiple decisions buried in narrative** | Re-read carefully. Every "we decided", "let's go with", "agreed on" is a decision. Extract all of them |
| **Duplicate or contradictory action items** | Check for consistency. If the same action has two different owners or deadlines, flag the conflict |
| **Transcript is very long (30+ minutes of conversation)** | Summarize discussion topics first, then extract decisions + actions. Do not reproduce every turn of dialogue |

---

## Verification Checklist

- [ ] All attendees listed with names (not just roles like "client")
- [ ] Meeting type, date, and duration captured
- [ ] Every decision logged with a clear why
- [ ] Every action item has an owner (flagged if missing)
- [ ] Every action item has a deadline (flagged if missing)
- [ ] Discussion summary is concise — 2-3 sentences per topic, not a transcript replay
- [ ] Language consistency: output matches input language unless requested otherwise
- [ ] Follow-up / next steps section included
- [ ] Action items are concrete and actionable (not vague like "look into it")
- [ ] Format chosen: Markdown (default), plain text, or JSON — confirmed with user

---

## Data Sources & Accuracy

- **Input source:** User-provided notes, transcripts, or voice memo summaries. Accuracy depends entirely on the quality and completeness of the input.
- **No external data sources** — all information is extracted from the user's raw material.
- **Hallucination risk:** The agent will never invent attendees, decisions, or actions that weren't in the input. If information is missing, it will be flagged rather than fabricated.
- **Best practice:** For important meetings, encourage users to paste notes immediately after the meeting while details are fresh.
- **Privacy:** Meeting minutes are generated in-session only. No data is stored or sent to any external service unless the user explicitly asks to save or share them.
