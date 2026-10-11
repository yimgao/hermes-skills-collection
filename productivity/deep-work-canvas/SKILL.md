---
name: deep-work-canvas
description: "A single living Markdown file per project — goals, scope, current focus, open loops, decisions, blockers, parking lot, daily log, weekly snapshot. One `today: <project>` command switches the canvas, one `note …` parks anything, one `end of day` rolls the focus forward. Replaces sticky notes, Notion fluff, and 14-doc chaos. Pairs with daily-briefing, daily-shutdown, draft-tracker, decision-journal, weekly-review, pomodoro-coach, standup-status-updater."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, project, dashboard, canvas, second-brain, gtd, deep-work, knowledge-work, focus, journaling, mermaid, single-file, privacy-first, mvp]
    related_skills: [daily-briefing, daily-shutdown, draft-tracker, decision-journal, weekly-review, pomodoro-coach, standup-status-updater, inbox-triage, meeting-prep-brief, quarterly-goals-coach]
---

# 🧭 Deep Work Canvas — 一份活文档管一个项目

> Most projects aren't chaotic because the work is hard — they're chaotic because the *state of the work* lives in 14 places: Slack DMs, Notion pages, mental notes, your last meeting's whiteboard, and a Trello board you haven't opened in three weeks. **Deep Work Canvas** compresses all of that into one Markdown file per project, with a `today: <project>` switch so you always know what you're actually doing right now.

---

## Overview

`deep-work-canvas` is a **file-system-as-database** productivity skill. Each project you care about gets exactly one Markdown file at `~/.hermes/data/deep-work-canvas/<slug>.md`. One additional file — `~/.hermes/data/deep-work-canvas/.active.json` — holds the **current focus pointer** (which project you're on, when you started, what the next concrete move is).

The point isn't the Markdown. The point is the **contract**:

- Every project has the *same shape* (8 fixed sections).
- Switching projects is one command: `today: launch-deck`.
- You can never lose "what was I doing on X?" because the answer is always in that project's canvas, under `## Current Focus`.
- "Where did I park that idea about a Chrome extension?" → it lives in the canvas you were on at the time.

| Capability | Description |
|---|---|
| 🗂️ **One file per project** | Local Markdown; readable in any editor; never locked to a SaaS |
| 🎯 **Live focus pointer** | `.active.json` tracks current project + started-at + next-move |
| 📝 **8 fixed sections** | Always: Goal · Scope · Current Focus · Open Loops · Decisions · Blockers · Parking Lot · Log |
| 🪶 **One-line park** | `note: …` appends to the active canvas's parking lot |
| 🔀 **One-command switch** | `today: <slug>` swaps focus, logs the switch with timestamp |
| 📅 **Daily log auto-roll** | Each day, `## Log` gets a dated entry; weekly snapshot rolls stats |
| 🪞 **Mermaid state diagram** | Every canvas can render a focus flow you can paste anywhere |
| 🔁 **End-of-day rollforward** | Pair with `daily-shutdown`: unfinished loops roll into tomorrow |
| 📊 **Weekly snapshot** | Sun 8pm: 7-day stats — focus minutes, loops opened/closed, decisions made |
| 🔗 **Cross-skill hooks** | `daily-briefing` shows active project; `standup` pulls Current Focus; `weekly-review` reports per-canvas velocity |
| 🧹 **Stale-canvas radar** | Canvas untouched for 30d → flagged `dormant`; 90d → archive nudge |
| 🔒 **Local-first / portable** | `~/.hermes/data/deep-work-canvas/` — `git init` it, sync via Dropbox, whatever |
| 🛡️ **Privacy-first** | Code-level sketches, drafts, names never leave the machine |

---

## When to Use

Use `deep-work-canvas` when you hear any of:

**Direct triggers:**
- *"what should I work on today?"* / *"where am I?"* / *"what's my current focus?"*
- *"switch to project X"* / *"today: launch-deck"* / *"start project alpha"*
- *"park this idea on the current canvas"* / *"note: …"*
- *"log: shipped the webhook retry, bumped retry count to 3"* / *"log a 50-min focus block on the Q3 strategy doc"*
- *"show all my canvases"* / *"list my projects"* / *"which projects are active vs dormant?"*
- *"end-of-day on the launch deck — roll my loops to tomorrow"*
- *"I have 6 projects going, I can't keep them straight — set up a canvas per project"*
- *"snapshot week 41"* / *"what did I do on alpha last week?"*
- *"archive the dormant canvas for Side Project Z"*
- *"migrate my Trello / Notion / Obsidian projects into canvases"*

**Indirect / relational triggers:**
- *"I keep starting things and forgetting what I was doing"* → fragmented focus
- *"I have 20 browser tabs and 4 docs open per project"* → canvas consolidates
- *"My standup takes 20 minutes because I can't remember what I did"* → canvas has the log
- *"I want to read the state of a project in under 60 seconds"* → 8-section template

**NOT for:**
- Personal-life tracking (use `personal-crm`, `bookshelf`, `habit-tracker`, `renewal-reminder`)
- Cross-project goals (use `quarterly-goals-coach`; canvases roll up *into* quarters)
- Code repos (use `codebase-tour-guide`); canvases describe work, not source

---

## Core Workflow

### Step 1 — Initialize the canvas store

Create the directory and pick a slug convention. Default: lowercase-kebab.

```bash
mkdir -p ~/.hermes/data/deep-work-canvas
touch ~/.hermes/data/deep-work-canvas/.active.json      # current focus pointer
touch ~/.hermes/data/deep-work-canvas/.index.json       # all-canvas registry
```

Write `.active.json` on first run:

```json
{
  "active_slug": null,
  "started_at": null,
  "next_move": null
}
```

`.index.json` is the canonical list:

```json
{
  "canvases": [
    {
      "slug": "launch-deck",
      "title": "Launch Deck v3",
      "created_at": "2026-09-01",
      "last_touched": "2026-10-10",
      "status": "active",
      "tags": ["work", "exec-review"]
    }
  ]
}
```

Ask the user 4 onboarding questions once:

| Question | Why |
|---|---|
| 1. *How many projects are you juggling right now?* (1–3 = simple; 4–7 = standard; 8+ = needs ruthless pruning) |
| 2. *Where do you draft today?* (Notion / Obsidian / Google Docs / Notes app / nowhere) — migration strategy depends on this |
| 3. *Want me to capture the first 5 projects in one batch, or one-at-a-time?* |
| 4. *Single-device or multi-device?* (changes sync recommendation — `git`, Dropbox, iCloud, none) |

### Step 2 — Create the first canvas (file scaffolding)

For each project the user names, create `~/.hermes/data/deep-work-canvas/<slug>.md` from the template in `templates/canvas.md`. Eight fixed sections, always in this order:

| # | Section | What it holds | Update cadence |
|---|---|---|---|
| 1 | **Goal** | The one-sentence outcome this project produces | Once + on major pivot |
| 2 | **Scope** | In-scope / out-of-scope / non-goals | Weekly |
| 3 | **Current Focus** | Exactly what you're doing *right now* + next concrete move | Multiple times/day |
| 4 | **Open Loops** | Things you opened but didn't close — threads waiting on someone | Daily |
| 5 | **Decisions** | Append-only log linking to `decision-journal` entries | When made |
| 6 | **Blockers** | What's stopping forward motion, by category (you / them / waiting / unclear) | Daily |
| 7 | **Parking Lot** | Ideas, snippets, half-thoughts that aren't actionable *now* | Continuous |
| 8 | **Log** | Time-stamped diary — `## YYYY-MM-DD` headings, free-form under each | Continuous |

The full template lives at `templates/canvas.md`. The agent **never** invents section 9. If a project needs more, that means it's actually two projects — split the canvas.

Copy the template:

```bash
cp templates/canvas.md ~/.hermes/data/deep-work-canvas/launch-deck.md
```

Light validation is automatic — `scripts/validate.py` enforces:

- 8 sections present, in order
- Each section non-empty (parking lot allowed to be empty with `- _(none yet)_`)
- `## Current Focus` has both a *what* and a *next concrete move*

See `references/sections.md` for the full per-section spec.

### Step 3 — Switch the focus pointer

The user's primary verb:

> *"today: launch-deck"* / *"switch to alpha"* / *"what am I on?"*

Implementation:

```bash
# Reading the pointer
cat ~/.hermes/data/deep-work-canvas/.active.json
# { "active_slug": "launch-deck", "started_at": "2026-10-10T08:14:02Z", "next_move": "Slide 7 — ask Sarah for actuals" }

# Setting the pointer
echo '{"active_slug":"alpha","started_at":"'$(date -u +%FT%TZ)'","next_move":"null"}' \
  > ~/.hermes/data/deep-work-canvas/.active.json
```

When `today:` is invoked:

1. If `active_slug` was set, append a `## YYYY-MM-DD` entry to the **previous** canvas's log: `↩ switched to <new-slug>`.
2. Rewrite `.active.json` with new slug + fresh `started_at`.
3. If a `next_move` exists in `.active.json`, ask the user to confirm: *"Want to commit to <next-move> as today's first task?"* — on yes, write it into the new canvas's `## Current Focus`.

Auto-suggest the next project to switch to by analyzing `.index.json`:

- `status == "active"` AND `last_touched < 3d ago` → green (fresh)
- `status == "active"` AND `last_touched` 3–14d → amber
- `status == "active"` AND `last_touched > 14d` → **stale — ask user**: keep, archive, or re-activate?
- `status == "dormant"` (touched >30d, user-marked) → grey

### Step 4 — Park a note, log a block, file a decision

The three daily verbs:

```
note: ask Marcus about the pricing tier copy — Sarah said he'd have it Friday
log: 47-min focus block on the webhook retry backoff math
decide: ship with naive retry (3x, exp backoff) → linked to dec-2026-10-07-retry-strategy
block: waiting on legal redline — 4 days in, no reply
focus: draft slide 7 (actuals) — should take 30 min
done: shipped webhook retry; bumped retry count to 3, log → dec-…
```

Verb-to-section mapping is fixed (do not invent verbs):

| Verb | Section | Append format |
|---|---|---|
| `note:` / `note that` | Parking Lot | `- [YYYY-MM-DD HH:MM] <text>` |
| `log:` / `logged` | Log | under `## YYYY-MM-DD`, `- <text>` |
| `decide:` | Decisions | `- YYYY-MM-DD — <title> → \`decision-journal/dec-…md\`` |
| `block:` / `blocker:` | Blockers | sub-section `### You / Them / Waiting / Unclear` |
| `focus:` | Current Focus | replaces the `<next move>` line |
| `done:` | Current Focus (suffix) → Log | marked `✅ <date>` then moved to Log |
| `loop:` / `open:` | Open Loops | `- [id#NN] <text> — opened YYYY-MM-DD` |

Each addition is one write per canvas file — no DB, no indexing service. The agent reads the file, appends a line, writes it back. For canvases > 200 lines, the agent reads only the relevant section (`read_file` with offset/limit).

### Step 5 — End-of-day and weekly snapshots

Pair `end-of-day` with `daily-shutdown`. The canvas-specific ritual:

1. Ask: *"What's the unfinished-loop count on <active-slug>?"* — count `- [ ]` in `## Open Loops`.
2. If > 0: *"Want to roll loops >2d into tomorrow's plan? I'll mark them `[→ YYYY-MM-DD]`."*
3. Pull the most recent `## Current Focus`. If concrete-move still says "TBD", flag with `⚠`.
4. Ask: *"Score the day 1–10. One-word summary?"* — append to log.

For weekly snapshot (Sun 8pm or Monday morning):

```bash
# Run from anywhere
python3 ~/.hermes/skills/productivity/deep-work-canvas/scripts/weekly-snapshot.py
# Walks every canvas, summarizes last 7 days
# Output: per-canvas focus-minutes, loops-opened/closed, decisions, blockers resolved
# Writes a `## Snapshot — week-of YYYY-MM-DD` block into each canvas's Log
```

Snapshot never edits the prior week — it's append-only, like the log itself.

### Step 6 — Dorman­cy radar and archival

On any `today:` invocation, check the previous canvas:

- If `last_touched > 14d`: surface a one-line warning: *"⚠ alpha is 17d cold. Keep, archive, or stay dormant?"*
- If `last_touched > 30d`: mark `status = "dormant"` in `.index.json` automatically.
- If `last_touched > 90d`: ask *"Move <slug> to `archived/`?"* — never auto-archive.

Archive move is just `mv`:

```bash
mkdir -p ~/.hermes/data/deep-work-canvas/archived
mv ~/.hermes/data/deep-work-canvas/old-project.md \
   ~/.hermes/data/deep-work-canvas/archived/2026-05-old-project.md
```

When a dormant canvas is reactivated, prepend a `↩ Reactivated YYYY-MM-DD` to its log. The 8 sections stay intact — a canvas is never "deleted", only retired.

---

## Example Invocations

### 示例 1：Onboarding a new user with 6 active projects

**User:** *"I have 6 projects going and I keep losing track. Set up canvases for them."*

**Agent:**
> 我先问 4 个问题定锚点：① 项目数量；② 你现在在哪记东西；③ 我一次性给你铺 6 个还是一对一；④ 单设备还是多设备。然后铺目录和模板，每个 canvas 用 `## Current Focus` 撑住"现在到底在做什么"。铺好之后，命令动词稳定下来只有 7 个：`today:`、`note:`、`log:`、`decide:`、`block:`、`focus:`、`done:`。铺好之后第一件事告诉我你在哪个项目上，我把它写进 `.active.json`。

### 示例 2：Daily use — switching, parking, logging

**User:** *"today: launch-deck. focus: rework slide 7 with Sarah's actuals."*

**Agent:**
> `↩ switched from alpha → launch-deck at 2026-10-10 09:02.` 已经在 `## Current Focus` 写好：*"rework slide 7 with Sarah's actuals"*，并把下一动作标黄。30 分钟后你说 `log: 30-min focus block on slide 7`，会进 `## Log`。如果这是要决策的事，明天说 `decide: …` 我会建议链到 `decision-journal`。

### 示例 3：Recovery — pickup after vacation

**User:** *"I was on alpha and went on PTO for 2 weeks — walk me through what's open."*

**Agent:**
> 打开 `alpha.md` 的 `## Open Loops`，按"等待谁"分组。要我标记 `[→ YYYY-MM-DD]` 表示延后到本周 / 下周吗？`## Blockers` 现在是空的——你不在的时候没人催你。`## Parking Lot` 有 7 条——逐条过一下决定丢弃、归档还是升级到 `decide:`。`## Current Focus` 还是你走之前写的："*mock the new ingest API*" —— 要把这个作为今天的第一件事吗？

### 示例 4：Weekly review integration

**User:** *"Sunday review — show me per-canvas velocity."*

**Agent:**
> 跑 `scripts/weekly-snapshot.py`。结果：launch-deck 4h 12min focus / 3 loops closed / 1 decision / 0 blockers。alpha 1h 48min / 1 loop closed / 0 decisions / 1 blocker。你本周 38% 时间在 launch-deck，建议 alpha 升级到 `quarterly-goals-coach` 的 KRs 还是降级到 dorm­ant 候选？已写快照进每个 canvas 的 `## Log`。

### 示例 5：Migrating from Notion

**User:** *"I have 14 Notion pages across 4 project databases — migrate them into canvases."*

**Agent:**
> 4 个数据库 → 4 个 canvas slug（每个数据库顶层项目）。每个 Notion 页面映射到 canvas 的 `## Open Loops`、`## Parking Lot`、或 `## Decisions`，按页面类型判断：task → Open Loop；idea → Parking Lot；decision → 写一条 `decide:` + 提议链接到 `decision-journal`。我会先 dump 一份 Notion export 到 `~/Downloads/notion-export/` 然后做 4 次 dry-run，问你"这条放 Open Loops 还是 Parking Lot？"再落盘。

---

## Common Pitfalls

| 问题 | 解决方案 |
|---|---|
| Canvas 越写越长变成墙 | 超过 250 行问用户"分裂成两个 canvas？"——通常就是两个项目。 |
| `## Current Focus` 写"做各种事" | 必须只 1 个动词 + 1 个可验证产物。超过 1 个就分裂 canvas。 |
| 把决策藏在 `## Log` 里 | 决策必须进 `## Decisions` 并链接 `decision-journal`。 |
| Open Loops 变成垃圾桶 | 30 天未关闭的 loop 强制问"关、转、保留"。 |
| `## Scope` 永远不更新 | 每月初提醒一次"scope 还是上个月的吗？" |
| 一个 canvas 管 6 个项目 | 看到 `# Work`、`# Personal` 混合的标签时立刻拆。 |
| Parking Lot 永远不清 | 每两周一次 parking-lot-triage：`note: …` 是输入，不是永久存储。 |
| 用 emoji 替代动词 | 严格 7 动词；emoji 仅做视觉分组。 |
| 在 canvas 外用 `note:` | 总是进 `.active.json` 当前 slug 的 canvas。 |
| 想用 `git` 同步但是没有 `.gitignore` | 模板默认把 `.active.json` 和 `.index.json` 加进去——避免 merge 冲突。 |
| 误以为 canvas 是任务管理器 | Canvas 描述*状态*；任务用 `inbox-triage` 或 `pomodoro-coach`。 |
| 多设备同步把 `.active.json` 互相覆盖 | 在 `.index.json` 里给每台设备加 `device_id`，或干脆把 `.active.json` 排除出同步。 |
| 以为 `done:` 会自动关 Open Loop | `done:` 只标记当前 focus 完成；Open Loops 用 `- [x]` 手动关。 |
| Log 条目变成会议纪要 | 日志是 1 行；详细会议用 `meeting-minutes-generator`，然后贴一行链接进 log。 |
| 看不懂 canvas 是干嘛的 | `## Goal` 必须一句话写出产出物；模糊 → 重写。 |
| 一个人用 8 个 canvas 但只 touch 2 个 | 其余的转 dormant / 合并 / 删除。先合并，再考虑保留。 |
| 把 canvas 名 / slug 改掉 | 改名要全仓搜旧 slug；`.index.json` 必须同步改。 |
| "我什么都用 markdown 写" → 用 canvas 写代码 | 代码归 git。canvas 用于描述代码 *状态*。 |

---

## Verification Checklist

- [ ] 仓库目录 `~/.hermes/data/deep-work-canvas/` 存在
- [ ] `.active.json` 有效 JSON 且 `active_slug` 指向真实文件
- [ ] `.index.json` 有效 JSON 且 `canvases` 数组每个元素都指向真实文件
- [ ] 每个 canvas 文件正好有 8 个二级标题（顺序固定）
- [ ] `## Goal` 是单句且包含一个可验证的产出物
- [ ] `## Current Focus` 同时包含 `> 当前在做` 和 `> 下一动作` 两行
- [ ] `## Scope` 含三个子项：`in`、`out`、`non-goals`
- [ ] `## Open Loops` 用 `- [ ]` 或 `- [x]` 列表格式，可被脚本解析
- [ ] `## Decisions` 每条都引用一个存在的 `decision-journal` 文件
- [ ] `## Blockers` 至少有一个子标题（`### You / Them / Waiting / Unclear`）
- [ ] `## Parking Lot` 用 `- [YYYY-MM-DD HH:MM]` 时间戳前缀
- [ ] `## Log` 中最近的日期标题为今天或昨天
- [ ] `scripts/validate.py <slug>.md` 返回 `OK`
- [ ] `scripts/weekly-snapshot.py` 跑通且输出可读
- [ ] `last_touched` 不超过 30 天的 canvas 其 `status == active`
- [ ] 设备同步目录（如有）`.gitignore` / 同步排除列表里包含 `.active.json`
- [ ] 没有 canvas 文件包含密码、token、私钥或完整证件号

---

## Data Sources & Accuracy

| 来源 | 用途 | 准确性 |
|---|---|---|
| 用户口述的项目 | slug、Title、Goal、Scope | 来自用户，agent 不脑补 |
| 用户 `log:` / `note:` / `focus:` 等等的命令 | 写入对应 section | 字面保留，不修字 |
| `~/.hermes/data/deep-work-canvas/` 目录 | 全部 state-of-truth | 单一可信源 |
| `~/.hermes/data/decision-journal/`（cross-skill） | Decisions section 引用 | 仅读链接，不复制内容 |
| `~/.hermes/data/pomodoro/`（cross-skill） | 每周焦点分钟数 | 只读取聚合数据 |
| 系统时间 `date -u +%FT%TZ` | 时间戳前缀 | 用于 `## Log` 和 `## Parking Lot` |

**Never 原则：**
- 不写不存在的 loop id（每条 `- [id#NN]` 在 `## Open Loops` 中唯一）
- 不"猜测"决策——决策必须由用户主动说 `decide:` 才能记录
- 不为老 canvas 重写历史——只追加 `↩ Reactivated YYYY-MM-DD`
- 不在没有用户确认的情况下合并/分裂/归档 canvas
- 不往 canvas 写真实凭证、私人证件号、医疗原件、API 密钥

**同步精度：**
- 单设备：模板默认 `~/.hermes/data/deep-work-canvas/`，无云。
- 多设备：建议 `git init` + `.gitignore` 排除 `.active.json`；或用 Dropbox / iCloud Drive 同步，**注意** `.active.json` 是冲突点——跨设备用 `--device-id <name>` 区分。
- 迁移：从 Notion → export → 一次跑 1 个数据库；从 Obsidian → 整 vault 拉一遍后挑 active；从 Trello → board 导出 CSV → 每张卡=`focus:` 或 `note:`。

**验证脚本：** `scripts/validate.py`（见 `scripts/`）强制执行 8-section-in-order、loop id 唯一、`## Current Focus` 双行 schema、和"无敏感凭证"的启发式扫描。

**已知限制：**
- 单一用户、单一焦点指针。不支持团队多人协作（多用户版本应改用独立的 `~/.hermes/data/deep-work-canvas-<user>/`）。
- Markdown 大文件读慢：`> 500 行` 时强建议分裂。
- 时间戳只在写入瞬间记一次——之后编辑不等于改时间戳。dorm­ant 检测依靠 `.index.json` 的 `last_touched`，依赖于 `note:` / `focus:` 写入时刷新它。如果用户直接 vim 编辑文件，请自己跑 `touch -m` 同步时间。
