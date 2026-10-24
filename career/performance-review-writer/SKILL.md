---
name: performance-review-writer
description: "Use when writing a self-review, building a brag doc, assembling a promotion packet, or asking peers for feedback. Turns scattered git commits, OKRs, and half-remembered wins into a quantified, defensible review — with impact scoring, promo-gap analysis, and a lint pass that kills 'helped with' language. Local JSON, no HR tool needed."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [career, performance-review, brag-doc, promotion, self-review, feedback, okr, management, writing]
    related_skills: [quarterly-goals-coach, standup-status-updater, deep-work-canvas, salary-negotiation-coach, job-tracker, weekly-review]
---

# Performance Review Writer / 绩效自评 · 晋升材料 · Brag Doc

> Two weeks before review season you try to remember what you did in February. You can't. You write "worked on reliability improvements and helped with the migration" — and get a "meets expectations" while the person who kept a running log gets "exceeds."

This skill builds the log **before** you need it, then turns it into three deliverables: a **self-review**, a **promotion packet**, and a **peer-feedback request** that people actually answer.

## Overview

| 能力 | 命令 / 触发 | 输出 |
|---|---|---|
| 📓 记一条 win | `win: <一句话>` | 追加到 `brag.json`，带日期/scope/axis/指标 |
| 🔍 自动采集证据 | `harvest` | 扫 git 仓库 + OKR + canvas，产出候选 win 列表 |
| ✍️ 写自评 | `self-review 2026H2` | 5 段式自评草稿（成果/影响/成长/目标/评级论证） |
| 🎯 晋升材料 | `promo L5` | 按目标职级逐条对标 + 差距清单 + sponsor 一页纸 |
| 📊 影响力量化 | `stats` | 按季度/维度/影响半径统计，找出证据缺口 |
| 🙋 要反馈 | `feedback-ask` | 给同事的 3 问模板（30 秒能答完的那种） |
| 🧹 文风体检 | `lint draft.md` | 揪出 "helped with"、无数字、"we" 冒功、空泛成长项 |
| 🔁 定期提醒 | cron | 每周五提醒补 log，评审季前 30 天提醒开写 |

**核心原则：评审不是写作比赛，是证据整理。** 写得漂亮但没数字，评委会问"所以呢"；数字齐全但没叙事，评委记不住你是谁。这个 skill 两者都管。

## When to Use

- 公司评审季要交自评（半年/年度），打开文档一片空白
- 想升职，但不知道"我现在够不够"，也不知道材料缺什么
- 刚做完一个大项目，怕过两个月忘了量化结果 → 现在就 log
- 要给同事写 peer feedback，不知道怎么问才不烦人
- 想知道自己这半年到底干了啥（年终总结、简历更新、面试讲故事都复用）
- 管理岗：给下属写 review 需要证据链（本 skill 的 lint 与 rubric 同样适用）
- 中文场景：`帮我写今年的绩效自评`、`我要评 P7 了，材料怎么准备`、`帮我整理 brag doc`

## Core Workflow

### Step 1: 建立 Brag Doc（10 秒一条，别等评审季）

数据落在 `~/.hermes/data/perf-review/brag.json`。**不是日记，是弹药库** —— 只记能进材料的东西。

```bash
S=~/dev/skills/hermes-skills-collection/career/performance-review-writer/scripts
python3 $S/brag.py add \
  --title "Cut checkout p95 latency 42%" \
  --date 2026-10-14 \
  --scope team \
  --axis technical \
  --metric "p95 latency" --before 4200 --after 2440 --unit ms \
  --evidence "https://github.com/acme/api/pull/812" \
  --stakeholder "VP Eng"
```

也可以在对话里直接说，Hermes 解析后入库：

> `win: 把 checkout p95 从 4.2s 降到 2.4s，起因是黑五压测，方案是异步化 webhook，影响整个支付团队`

**一条好 win 的 5 个字段**（缺哪个，脚本会提示补）：

| 字段 | 含义 | 反例 | 正例 |
|---|---|---|---|
| `title` | 一句话结论 + 数字 | "优化了支付流程" | "Cut checkout p95 42% (4.2s→2.4s)" |
| `scope` | 影响半径 | 不填 | `self` / `team` / `org` / `company` |
| `axis` | 能力维度 | 不填 | `execution` / `technical` / `leadership` / `collaboration` / `business` |
| `metric` | 可验证的量 | "更快了" | before 4200 / after 2440 / unit ms |
| `evidence` | 谁能证明 | 无 | PR 链接、看板截图、邮件、文档 |

`scope` 和 `axis` 是晋升评审真正的评分维度 —— 见 Step 4。没有指标时用 `--impact-pct` 或 `--qualitative` 标注（诚实标注比编数字安全）。

### Step 2: 采集证据（补上你没记的部分）

你当然没记全。`harvest.py` 从三个地方把事实捞出来，生成**候选**清单，你只做勾选。

```bash
S=~/dev/skills/hermes-skills-collection/career/performance-review-writer/scripts

# 扫最近 90 天的 git（可多次 --repo，或 --scan 扫描一个目录下的所有仓库）
python3 $S/harvest.py \
  --since 2026-07-01 \
  --repo ~/dev/acme/api \
  --repo ~/dev/acme/web \
  --out ~/perf/candidates.md

# 只看某个仓库里你自己（默认按 git config user.email 过滤）
python3 $S/harvest.py --since 2026-07-01 --repo ~/dev/acme/api --author you@acme.com
```

三个证据源：

| 来源 | 拿到什么 | 路径 |
|---|---|---|
| **git** | commit 类型分布、增删行数、热点模块、perf/fix 关键词、PR 号 | `--repo` / `--scan` |
| **OKR** | KR 完成度、目标从 0.24 → 0.86 的推进 | `~/.hermes/goals/*.json` |
| **canvas** | `done:` 行、决策记录、关闭的 open loop | `~/.hermes/data/deep-work-canvas/*.md` |

输出是**候选**，不是结论。每条带 `confidence`：`high`（有 PR + 指标）/ `medium`（有 commit 簇）/ `low`（仅关键词）。规则：

- `high` → 直接 `brag.py add`
- `medium` → 补一句"为什么重要"再入库
- `low` → 只在你还记得上下文时才用，别把 `fix typo` 写成"提升代码质量"

**关键判断：commit 数量不是影响力。** 300 个 commit 修 CSS 不如 1 个把 p99 砍半的 commit。harvest 只是防止你漏掉，评分靠 Step 1 的 5 个字段。

### Step 3: 写自评（5 段式，别写流水账）

```bash
python3 $S/brag.py rollup --period 2026H2        # 生成 markdown 素材表
python3 $S/brag.py stats                        # 维度覆盖 + 缺口
```

拿到素材表后，按固定结构写。**这个结构的顺序是有讲究的**：先说结论，再给证据，最后才谈成长 —— 评委平均花 3 分钟看一份自评，前 200 字决定印象。

```markdown
## 1. 一句话总结（≤40 字，必须带数字）
把 checkout p95 砍掉 42%，支撑黑五 3.2× 流量零事故。

## 2. 关键成果（3–5 条，每条一个 STAR+Impact）
- **问题**：黑五压测显示 checkout p95 4.2s，预估转化损失 ~$180k
- **动作**：把 webhook 同步调用改为异步队列 + 幂等重放（我主导设计，2 人协作）
- **结果**：p95 2.44s（-42%），黑五 3.2× 流量零 P1，转化 +1.8pp
- **证据**：PR #812、Grafana 面板、黑五复盘文档

## 3. 影响半径（评审真正在看的）
团队内 → 支付组 6 人复用该队列；跨团队 → 被风控组采纳为异步标准；
组织级 → 写入 platform handbook 第 4 章。

## 4. 成长与不足（1–2 条，必须"具体 + 已采取动作 + 时间"）
Q3 我在跨团队对齐上偏慢（支付改造晚了 9 天）。已改为：改造前先出 1 页 RFC，
提前 5 个工作日拉齐风控/财务。Q4 两次跨团队项目均按期。

## 5. 下期目标（3 条，与团队 OKR 对齐，可验证）
```

**三条硬规则：**

1. **每条成果必须有数字**，没有数字就写"范围"（6 人 / 3 个团队 / 上线 4 个区）。
2. **"我"和"我们"要分清** —— 协作项目写 `我主导 X，与 Y 协作完成 Z`。全篇"we"= 评委无法给你打分。
3. **成长项不能是伪缺点**（"我太追求完美了"）。真缺点 + 已采取的动作 + 可验证的时间点，才是加分项。

写完后**必须过 lint**：

```bash
python3 $S/lint.py ~/perf/self-review-2026H2.md
```

lint 会揪出：弱动词开头（helped/worked on/responsible for）、无数字条目、we/I 比例失衡、空泛成长项、超长句、重复条目。有 `ERROR` 就不交。

### Step 4: 晋升材料（对标目标职级，不是罗列功劳）

晋升不是"我做了很多"，而是"我已经在按下一级的方式工作"。所以要先知道下一级要什么。

```bash
python3 $S/brag.py gaps --level senior      # 也接受 L5 / IC5 / staff / principal
```

输出三个区块：

| 区块 | 含义 | 怎么用 |
|---|---|---|
| **已满足** | 有证据支撑的维度 | 直接进 packet，作为主打 |
| **证据不足** | 做了但没量化/没记录 | 评审前 2 周补数据、补证人 |
| **完全缺失** | 一级要求里一条都没有 | 这才是真正的差距 —— 要么补，要么换目标职级 |

职级模型（可被 `--levels` 覆盖）：

| 职级 | 影响半径要求 | 维度覆盖 | 典型信号 |
|---|---|---|---|
| `mid` | 3 个 team 级成果 | ≥2 | 独立交付模块 |
| `senior` | 1 个 org 级 + 5 个 team 级 | ≥3 | 定义方案、带 1–2 人、跨团队被咨询 |
| `staff` | 2 个 org 级 + 8 个 team 级 | ≥4 | 定标准、解模糊问题、影响多个团队路线图 |
| `principal` | 4 个 org 级 + 10 个 team 级 | 5 | 定公司级技术方向 |

**晋升 packet 的三件套：**

1. **一页纸 summary** —— 给 skip-level 和 committee 看的，只有数字和影响半径（他们不认识你）。
2. **证据表** —— 每条成果 → 对应职级要求 → 证人姓名。证人必须**事先知情**（评审前打招呼，别让评委冷启动去问人家）。
3. **sponsor 简报** —— 给你的 manager/赞助人 5 句话，让他能在 calibration meeting 上替你说话。**没有 sponsor 的 packet 是废纸** —— 这是政治现实，不是技巧。

校准会（calibration）前必问自己的三个问题：

- 如果 committee 只记得我的一句话，那句是什么？（答不上 → summary 没写好）
- 我的最大成果，换成同组任何人都能做到吗？（能 → 不是 promo 级证据）
- 我的证人会在会上主动提我吗？（不会 → 先去沟通）

### Step 5: 要 peer feedback（问对了才有人回）

大多数"求反馈"消息没人回，因为它要求对方**从零回忆 + 组织语言**。解法：把回忆工作替他们做完，只留判断题。

```bash
python3 $S/brag.py feedback-ask \
  --to "Maya (风控)" --about "支付异步队列改造" \
  --channel slack
```

生成的模板（Slack 版，中文同理）：

```text
Hey Maya — review season, and I'm asking a small group for input.
Context: I led the async queue rewrite for checkout webhooks (I owned the
idempotent-replay design; you were the main consumer on the risk side).

Two questions, 2 minutes max — a sentence each is plenty:
1. What specifically worked when we coordinated the rollout?
2. What's one thing I could do differently next time we do a cross-team cutover?

No need to polish it — bullet fragments are perfect. Thanks.
```

**四个设计要点，缺一个回复率就掉一半：**

| 要点 | 为什么 |
|---|---|
| 给上下文（你做了什么 + 对方在其中的位置） | 免去对方回忆，也暗示"这事和你有关" |
| 只问 2 个问题（1 正 + 1 改进） | 3 个以上 → 拖延 → 不回 |
| 明确"一句也行/碎片也行" | 降低对方的心理成本 |
| 给 deadline 但不施压（"周五前就好，不回也没事"） | 制造温和的紧迫感 |

收回来的反馈存进 `brag.json` 的 `feedback` 数组，两个用途：① 自评第 4 段（成长项）有真材实料；② 晋升时证人名单是现成的。

**收到负面反馈怎么办**：不要辩解，写进自评并给出"已采取动作"。评审看到的是你处理反馈的能力，不是你完美无瑕。

## Example Invocations

### 例 1：评审季前一周，从零开始

> **用户**：下周要交年度自评了，我完全没记录，怎么办？我是后端，今年主要做了支付改造和一次线上事故处理。

**Agent**：
1. `harvest.py --since 2026-01-01 --scan ~/dev/acme` → 捞出 214 个 commit，聚成 7 个候选（支付队列重构 / 事故 #4412 修复 / 3 个内部库 / 2 个依赖升级）
2. 逐条问用户要指标：「支付改造上线后 p95 有变化吗？事故影响多少用户多少分钟？」——用户报 `4.2s→2.44s`、`影响 1.2 万用户，恢复 47 分钟`
3. `brag.py add` 入库 5 条（丢掉 2 条依赖升级，不够格进材料）
4. `brag.py stats` → 覆盖 `execution/technical` 两维，**缺 leadership / business** → 追问「有没有带人、有没有影响路线图？」→ 补出「带 1 名新人 3 个月转正」「用事故复盘推动 SLO 制度落地」
5. 输出 5 段式自评 + `lint` 通过（0 error, 2 warn：一处 "helped with" 已改写）
6. 附 3 条 peer feedback 请求模板（风控 / SRE / 直属 leader）

**交付**：`~/perf/self-review-2026.md` + 3 条待发消息。

### 例 2：想升 senior，但不确定够不够

> **用户**：我准备提 L5（senior），帮我看看材料够不够。

**Agent**：
1. `brag.py gaps --level L5` → 输出：
   - ✅ 已满足：team 级 6 条（要求 5）、`technical` 维度扎实
   - ⚠️ 证据不足：1 条 org 级成果存在但无量化（"支付组外 3 个团队在用" → 需补：具体团队名 + 使用量）
   - ❌ 完全缺失：`leadership` 维度 —— 无带人/带项目记录
2. 直说结论：「**现在提会卡在 leadership**。两条路：① 推迟一个季度，Q1 主动认领一个 2 人以上的跨团队项目；② 现在提，但把'主导支付改造，协调 3 个团队'重写成 leadership 证据 —— 成功率约五成。」
3. 用户选 ② → 追问协调细节（拉了几次会、拍板了什么、有无冲突解决）→ 提炼出 2 条 leadership 证据
4. 生成 promo packet 三件套：一页纸 summary、证据表（含证人）、给 manager 的 5 句 sponsor 简报
5. 提醒：「评审前 2 周找风控 Maya 和 SRE 的 Tom 打招呼，让他们知道在评 L5、以及希望他们提哪一件具体事。」

### 例 3：只是想把日常 log 起来

> **用户**：win: 今天把 CI 从 22 分钟砍到 9 分钟，缓存命中率从 40% 提到 88%

**Agent**：
1. 解析：`title` = "Cut CI runtime 22min → 9min (-59%)"、`scope` = team、`axis` = technical、指标齐全
2. 追问一个缺的字段：「这影响了多少人？」→ "整个后端 40 人"→ scope 提升为 `org`（40 人跨 3 个团队）
3. `brag.py add` 入库，回一句：「已记录（第 14 条，Q4）。当前维度覆盖：technical 7 / execution 4 / collaboration 2 / leadership 1 / business 0 —— business 是唯一空档，下次有影响收入/成本的事记得 log。」
4. 顺手：`python3 $S/brag.py list --since 30d` 展示最近条目，防止重复记录

## Scripts

All three are stdlib-only Python 3, no network, no install step.

```bash
S=~/dev/skills/hermes-skills-collection/career/performance-review-writer/scripts
```

| 脚本 | 作用 | 常用参数 |
|---|---|---|
| `brag.py` | 入库 / 统计 / rollup / 晋升差距 / 反馈模板 | `--data PATH` 覆盖数据文件 |
| `harvest.py` | 从 git + OKR + canvas 采集候选证据 | `--since` `--repo` `--scan` `--author` `--json` `--out` |
| `lint.py` | 自评文风与完整性检查，非 0 退出码可接 CI | `--required` `--max-words` `--expect-min` `--json` |

**brag.py 子命令**

```text
add            写入一条 win（--title --axis 必填；--scope 默认 team）
patch <id>     补字段（--evidence / --scope / --impact-pct …）
list           列表（--period 2026Q4 --axis --scope）
stats          维度覆盖 / 影响半径分布 / 季度分布 / Top5 / 数据质量
rollup         生成 markdown 证据表（直接贴进自评）
gaps           --level senior|staff|L5|IC6|… 对标 + 三档结论 + 判定
feedback-ask   生成 --channel slack|email|zh 的求反馈模板
feedback-log   收回来存进 feedback 数组
export         --format md|json
```

**impact score = scope 权重 × 提升幅度**

| scope | 权重 | 例 |
|---|---|---|
| `self` | 0.5 | 自己效率提升 |
| `team` | 1.0 | 6 人团队受益 |
| `org` | 2.0 | 跨 3 个团队 / 40 人 |
| `company` | 3.0 | 全公司制度 / 收入影响 |

所以「p95 -42%，team 级」得分 41.9；「CI 22→9 分钟（-59%），org 级」得分 118.2。**这个分数只用来排序和识别缺口，不是给你的绩效打分** —— 评审看的是叙事 + 证据，不是数字大小。

**harvest.py 的产物是候选，不是结论**

- `high` → 有 PR 号 + perf/feat 关键词，可直接入库
- `medium` → commit 簇或体量够大，补一句"为什么重要"
- `low` → 单个 chore/docs commit，通常不进材料

`brag.py` 会自动给每条打质量标记：`MISSING_METRIC`（无数字）、`NO_EVIDENCE`（无证据）、`NO_AXIS`、`SELF_SCOPE`（影响半径太小）。这些标记就是评审前两周的 to-do 清单。

**lint.py 检查项**

| Code | 级别 | 拦截什么 |
|---|---|---|
| `WEAK_VERB` | ERROR | 以 helped / worked on / was responsible / 参与 / 协助 / 负责 开头 |
| `WE_OVERLOAD` | ERROR | "we/我们" 次数多于 "I/我"（≥3 次时触发） |
| `FAKE_WEAKNESS` | ERROR | 追求完美 / perfectionist 类伪装缺点 |
| `EMPTY_GROWTH` | ERROR | 成长段没有任何条目 |
| `MISSING_SECTION` | ERROR | `--required` 指定的段落缺失 |
| `LEAK` | ERROR | 疑似 API key / 邮箱 / 卡号 |
| `NO_NUMBER` | WARN | 成果条目无任何数字（成长/目标段豁免） |
| `NO_STRONG_VERB` | WARN | 成果条目没有强动词 |
| `VAGUE` | WARN | "大幅 / 有所提升 / various improvements" 等空话 |
| `TOO_LONG` | WARN | 单条超 `--max-words`（默认 60） |
| `GROWTH_NO_TIMELINE` | WARN | 成长项没有时间点 |
| `DUPLICATE` | WARN | 两条相似度 >82% |
| `SUMMARY_NO_NUMBER` | WARN | 开头段没有数字 |
| `THIN` | WARN | 条目数少于 `--expect-min` |

有 ERROR 时退出码为 1，可以直接挂 pre-commit 或 CI：

```bash
python3 $S/lint.py ~/perf/self-review.md --required "Accomplishments,Growth,Goals" || exit 1
```

**已实测**：英文好稿 0 error / 0 warn；中文好稿 0 error / 0 warn；中英烂稿各触发 5–6 个 ERROR（弱动词、伪缺点、重复、无数字）；含 key/邮箱的稿子触发 2 个 LEAK。`harvest.py` 在真实仓库（19 commits）分组出 18 个主题；`brag.py` 增删改查、Q4/H2 期间过滤、职级别名（L5→senior）均通过。

### Cron: 让记录变成习惯

评审季才想起记录，是这个流程唯一的致命失败点。两个 cron 就够：

```bash
# 每周五 17:30 提醒补 log（发到你的常用渠道）
hermes cron add "brag-weekly-nudge" \
  --schedule "30 17 * * 5" \
  --prompt "Run harvest.py --since 7d --scan ~/dev and show me new candidate wins. Ask me for metrics on anything high/medium confidence I haven't logged. Keep it to one message." \
  --skill performance-review-writer

# 评审季前 30 天开写（示例：年度评审在 12 月）
hermes cron add "self-review-kickoff" \
  --schedule "0 9 1 11 *" \
  --prompt "Review season in 30 days. Run brag.py stats --period $(date +%Y) and gaps --level senior, then draft my 5-section self-review and lint it." \
  --skill performance-review-writer
```



## Common Pitfalls

| 问题 | 解决方案 |
|---|---|
| 评审季才开始记，二月的事全忘了 | cron 每周五提醒 `win:` 补记；harvest 兜底扫 git |
| 自评写成"参与了/协助了/负责了" | `lint.py` 强制弱动词检查；改成"主导/设计/推动/砍掉" |
| 通篇没有数字 | lint 每条必须有数字或范围；没有就补影响面（人数/团队数/流量） |
| "we" 冒功或过度谦虚 | lint 检查 we/I 比例；协作写"我主导 X，与 Y 协作 Z" |
| 成长项写成伪缺点（"太追求完美"） | lint 检测伪缺点词库；要求"具体事 + 已行动 + 时间点" |
| commit 数量当业绩 | harvest 只是防漏，评分看 scope × 指标；300 个 typo fix 不进材料 |
| 晋升材料只列功劳，不标影响半径 | `gaps --level` 强制按 scope 对标；缺 org 级就明说不够 |
| 证人没提前打招呼 | packet 生成时输出待办："评审前 2 周联系 X/Y/Z" |
| 中文自评直接翻译英文模板，读着别扭 | 中文模式用"主导/推进/落地/沉淀"，避免" leverage/owned"直译 |
| 把公司机密指标贴进不可信工具 | 全部本地 JSON，零上传；lint 有密钥/邮箱泄露扫描 |
| 一年一个 brag.json 导致跨年统计混乱 | 按 `date` 过滤，`rollup --period 2026H2` 自动切；不需要分文件 |

## Verification Checklist

- [ ] `brag.json` 至少 5 条，每条有 `scope` + `axis` + 指标（或显式 `qualitative`）
- [ ] 每条关键成果有 `evidence`（PR 链接 / 看板 / 文档），能 30 秒内翻出来
- [ ] 自评 5 段齐全，第一段 ≤40 字且带数字
- [ ] `lint.py` 结果：**0 ERROR**（warn 可接受，但逐条看过）
- [ ] "we/I" 比例合理：协作项目明确写了"我主导什么"
- [ ] 成长项 = 真缺点 + 已采取动作 + 可验证时间
- [ ] 晋升场景：`gaps --level X` 无 ❌，或已知 ❌ 并有应对方案
- [ ] 证人名单已列，且**已提前沟通**（不是评审当天才想起）
- [ ] sponsor 简报 ≤5 句，manager 说"能用"
- [ ] 一页纸 summary 给不看代码的人读一遍，能说出你做了什么

## Data Sources & Accuracy

| 数据 | 来源 | 可靠性 |
|---|---|---|
| git 证据 | 本地仓库 `git log --numstat`，按 `user.email` 过滤 | 高（客观），但不含设计与协调工作 |
| OKR 进度 | `~/.hermes/goals/*.json`（quarterly-goals-coach 格式） | 高，取决于你是否如实更新 |
| 工作日志 | `~/.hermes/data/deep-work-canvas/*.md` 的 `done:` / `decide:` 行 | 中（自述） |
| 指标（before/after） | **用户提供** —— 脚本不会替你去 Grafana 抓数 | 取决于用户；无法验证时必须标注 `qualitative` |
| 职级要求 | 内置通用模型（mid/senior/staff/principal） | **低——仅供参照**。真实标准以你公司职级文档为准，务必 `--levels` 覆盖 |
| peer feedback | 用户粘贴的原文 | 高（一手），不要改写对方的话 |

**诚实性约束（重要）：**

- 本 skill **不生成虚构指标**。缺数字时脚本输出 `MISSING_METRIC` 警告，要求你补或标 `qualitative`，绝不自动填充。
- 晋升 `gaps` 的判断基于"有没有记录"，不是"你是否真的做到了" —— 记录缺失 ≠ 能力缺失，但评审只看记录。
- 内置职级模型是行业通用近似（参考大厂公开 ladder 的共性），**不同公司差异极大**（尤其 scope 定义）。用之前先替换成你公司的。
- 所有数据留在 `~/.hermes/data/perf-review/`，不上传、不联网。


