---
name: spaced-repetition-coach
description: "Use when you want to actually remember what you study — schedules reviews with SM-2, runs quiz sessions from chat, tracks per-card retention, detects leech cards, and forecasts daily workload. Local JSON, no cloud, no Anki required."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [learning, spaced-repetition, sm2, memory, review, retention, flashcards, study]
    related_skills: [flashcard-generator, study-planner, bookshelf]
---

# Spaced Repetition Coach / 间隔重复复习教练

> `flashcard-generator` 负责**造卡**，本 skill 负责**让你真正记住**。SM-2 算法排期、聊天式测验、逐卡留存率追踪、顽固卡（leech）诊断、未来负荷预测。数据全部本地 JSON，不需要装 Anki。

---

## Overview

绝大多数人学习失败不是因为没做笔记，而是因为**没有在正确的时间复习**。本 skill 实现了完整的间隔重复复习引擎：你在聊天里报成绩，它负责算下次该什么时候再问你。

| 能力 | 做什么 | 典型场景 |
|------|--------|----------|
| **SM-2 排期** | 按 0–5 评分推算下次复习日，ease factor 自适应 | 每天只复习"快要忘记"的卡，不浪费时间 |
| **聊天式测验** | Agent 出题 → 你答 → 你自评 → 自动记账 | 通勤、排队时用语音/文字刷卡 |
| **逐卡留存率** | 统计每张卡的历史正确率与全局 retention% | 判断自己是真记住了还是在自欺 |
| **Leech 诊断** | 累计失败 ≥8 次自动标记，并给出改卡建议 | 停止无效硬背，改写卡片本身 |
| **负荷预测** | 未来 14 天每日到期卡数柱状图 | 提前发现"下周三 80 张"的雪崩 |
| **考试冲刺模式** | 提高目标留存率、压缩间隔上限 | 考前 3 周切换到 0.95 retention |
| **多 deck 管理** | 按主题分组，独立限额与统计 | `networking` / `system-design` / `japanese` 并行 |

**与既有 skill 的边界（无重叠）：**

| Skill | 职责 | 交接点 |
|-------|------|--------|
| `flashcard-generator` | 从笔记/文章**生成**卡片内容 | 生成后交给本 skill 排期 |
| `study-planner` | 规划**学什么、按什么顺序**（宏观日程） | 本 skill 管微观的"今天复习哪几张" |
| `spaced-repetition-coach` | **调度 + 测验 + 留存追踪**（本 skill） | — |

调度器实现见 [`scripts/sm2.py`](scripts/sm2.py)，算法推导见 [`references/algorithms.md`](references/algorithms.md)，卡片写法规则见 [`references/card-writing-rules.md`](references/card-writing-rules.md)。

---

## When to Use

- *"今天该复习哪些卡？"* / *"What's due today?"*
- *"Quiz me on my system-design deck"* / *"抽 10 张问我"*
- *"把这些卡加进来：TCP 三次握手、B+ 树、CAP 定理"*
- *"我这张卡老是记不住"* → leech 诊断 + 改卡建议
- *"我的留存率多少？我是真记住了还是在骗自己？"*
- *"下两周复习量长什么样？"*（负荷预测，避免雪崩）
- *"3 周后考 AWS SAA，切冲刺模式"*
- 想用间隔重复但**不想装 Anki / 不想把数据传云端**
- 配合 cron 做每天早上的"今日复习提醒"

**不适用：** 需要图片遮挡卡、手写识别、移动端同步 → 用 Anki 本体。本 skill 的 `history[]` 保留了 `(date, quality)` 对，随时可迁移。

---

## Core Workflow

### Step 1: 初始化卡库

数据默认落在 `~/.hermes/data/srs/cards.json`（可用 `SRS_PATH` 覆盖）。

```bash
# 从模板起步（含 settings + 2 张示例卡）
mkdir -p ~/.hermes/data/srs
cp templates/cards.json ~/.hermes/data/srs/cards.json

# 或者直接加第一张卡，文件会自动创建
python3 scripts/sm2.py add "TCP vs UDP?" "TCP=reliable/ordered; UDP=fast/lossy" networking
```

实测输出：

```
added c1 to deck 'networking' — due 2026-08-29
```

`settings` 可调项（见 `templates/cards.json`）：

| 键 | 默认 | 含义 |
|----|------|------|
| `daily_limit` | `20` | 每日复习队列上限 |
| `new_cards_per_day` | `10` | 每日新卡上限（新卡会产生 ~8–10 次未来复习） |
| `target_retention` | `0.9` | 目标留存率，冲刺模式调到 `0.95` |
| `leech_threshold` | `8` | 累计失败几次算 leech |

### Step 2: 加卡（Agent 必须先做卡质量检查）

用户给内容时，**不要照搬**。先按 [`references/card-writing-rules.md`](references/card-writing-rules.md) 的 6 条规则过一遍，最关键的是**一卡一事**：

```
用户：加一张卡，ACID 的四个特性
Agent：这张卡会变成 leech（一次考 4 个事实，部分回忆无法评分）。
       拆成 4 张 cloze：
         - 事务的 {{Atomicity}} 保证全部成功或全部回滚
         - 事务的 {{Consistency}} 保证数据始终满足约束
         - ...
       要按这个拆吗？
```

确认后批量加：

```bash
python3 scripts/sm2.py add "事务的 {{Atomicity}} 保证全部成功或全部回滚" "Atomicity" db
python3 scripts/sm2.py add "What is a B-tree?" "Balanced n-ary tree used for DB indexes" db
```

### Step 3: 看今日队列

```bash
python3 scripts/sm2.py due
```

实测输出：

```
2 card(s) due:

  [c1] TCP vs UDP?
  [c2] What is a B-tree?
```

排序规则是**逾期优先，其次难卡优先**（EF 低的先来）——趁注意力还在时处理最难的。逾期卡会带 `(overdue Nd)` 标记。

### Step 4: 跑测验（聊天式）

Agent 逐张出题，**只出 front，不能泄露 back**；用户答完后再揭示答案，然后请用户自评 0–5：

| 分 | 含义 | 结果 |
|----|------|------|
| 5 | 瞬间想起，毫无迟疑 | EF +0.10，间隔拉长 |
| 4 | 想了一下，答对了 | EF 不变 |
| 3 | 答对了但很吃力 | EF −0.14 |
| 2 | 答错，但答案就在嘴边 | **lapse**，明天重来 |
| 1 | 答错，看到答案才有印象 | **lapse** |
| 0 | 完全空白 | **lapse** |

**3 和 4 的分界线最重要。** 用户如果每张都报 5，间隔会跑得比真实记忆快，两周后集体崩盘。Agent 发现 >70% 的评分都是 5 时要主动提醒"评分是否偏乐观"。

记账：

```bash
python3 scripts/sm2.py grade c1 5
python3 scripts/sm2.py grade c2 2
```

实测输出：

```
c1: q=5 → interval 1d, EF 2.6, next 2026-08-30
c2: q=2 → interval 1d, EF 2.5, next 2026-08-30
```

复习完再看队列即清空：

```
Nothing due today. 🎉
```

### Step 5: 留存率与 leech 体检

```bash
python3 scripts/sm2.py stats
```

实测输出：

```
cards:      2
reviews:    2
retention:  50.0%
leeches:    0
```

**怎么读 retention：**

| 区间 | 判读 | 动作 |
|------|------|------|
| >95% | 复习过于频繁，在浪费时间 | 可接受更长间隔 / 降低目标留存率 |
| 85–95% | 健康区间 | 保持 |
| 70–85% | 卡片偏难或加卡太快 | 减少 `new_cards_per_day` |
| <70% | 卡片写得有问题 | 按卡质量三联表逐条改卡 |

leech 出现时（`⚠` 标记），**改卡而不是硬背**，四种处方按优先级：拆卡 → 改写 → 加助记/语境 → 挂起删除。诊断表见 [`references/card-writing-rules.md`](references/card-writing-rules.md)。

### Step 6: 负荷预测（防雪崩）

```bash
python3 scripts/sm2.py forecast 7
```

实测输出：

```
2026-08-29   0
2026-08-30  ██ 2
2026-08-31   0
2026-09-01   0
2026-09-02   0
2026-09-03   0
2026-09-04   0
```

看到某天出现尖峰（比如 80 张）就提前分流：那几天暂停加新卡。**每张新卡会在未来产生约 8–10 次复习**——今天狂加 50 张，下个月就是 400 次复习的一天。

### Step 7: 生成会话报告（可选）

用 [`templates/session-report.md`](templates/session-report.md) 渲染一份可存档的复习报告，含评分分布、lapse 清单、leech 处方、未来负荷。适合每周回顾时看趋势。

### Step 8: 挂 cron 做每日提醒

```bash
hermes cron add --name srs-daily \
  --schedule "0 8 * * *" \
  --prompt "用 spaced-repetition-coach 跑 scripts/sm2.py due 和 stats。若有到期卡，列出卡面并提示复习；若出现 leech，附上改卡建议。无到期卡则回复 [SILENT]。"
```

### Step 3.5 验证（本 skill 的代码全部实测通过）

```bash
python3 scripts/test_sm2.py
```

25 条断言全绿，覆盖首轮间隔、6 天固定步、EF 上下限、lapse 重置、leech 阈值、队列排序、留存率、JSON 往返、负荷预测、非法输入。

**授权阶段真实抓到的 bug：** 连续 30 次 q=5 会让间隔超出 `datetime.date.max`，抛 `OverflowError: date value out of range`。因此 `MAX_INTERVAL = 3650`（10 年上限）**是必需项而非装饰**，T6 断言专门锁住这个回归。

---

## Example Invocations

### Example 1: 从零开始建一个面试复习库

**用户：** *"我在准备 system design 面试，帮我建个复习库，先加 CAP 定理、一致性哈希、读写分离这三个概念"*

**Agent：**
1. `mkdir -p ~/.hermes/data/srs && cp templates/cards.json ~/.hermes/data/srs/cards.json`
2. 先做卡质量检查——"CAP 定理"作为一张卡太宽（一次考 3 个字母 + 取舍关系），建议拆：
   - `CAP 中 {{C}} 指所有节点读到同一份最新数据` → Consistency
   - `CAP 中网络分区发生时，必须在 {{一致性}} 和 {{可用性}} 之间取舍`
   - `Q: ZooKeeper 属于 CAP 里的哪两个？ A: CP`
3. 用户确认后 `python3 scripts/sm2.py add ... system-design` 逐条加入
4. 回报：*"已加 7 张卡到 `system-design` deck，全部今天到期。建议每天新卡不超过 10 张——你现在 7 张会在未来一个月产生约 60 次复习。要现在开始第一轮吗？"*

### Example 2: 日常复习会话

**用户：** *"Quiz me — 今天该复习什么？"*

**Agent：**
1. `python3 scripts/sm2.py due` → 3 张到期，其中 1 张逾期 4 天
2. 逐张出题（只出 front）：
   > **[c2]** *（逾期 4 天）* PostgreSQL listens on port \_\_\_ by default.
3. 用户：*"5432"*
4. Agent：*"✅ 正确。自评 0–5？"* → 用户：*"5，秒答"*
5. `python3 scripts/sm2.py grade c2 5` → `interval 6d, EF 2.6, next 2026-09-04`
6. 三张走完后汇总：*"3 张完成，2 张 q≥4，1 张 lapse（c7 一致性哈希，第 3 次失败了）。c7 快要变 leech 了——它现在同时问了'虚拟节点作用'和'扩容时迁移比例'两件事，建议拆成两张。要我改吗？"*

### Example 3: 留存率体检 + leech 抢救

**用户：** *"我感觉背了半天啥也没记住，帮我看看数据"*

**Agent：**
1. `python3 scripts/sm2.py stats` → `reviews: 412, retention: 68.4%, leeches: 6`
2. 判读：*"68% 留存率低于健康区间（85–95%），问题不在你的记性，在卡片质量——你有 6 张 leech 吃掉了大量复习时间。"*
3. 逐张开处方（按 `references/card-writing-rules.md` 三联表）：

   | 卡 | 失败次数 | 诊断 | 处方 |
   |----|----------|------|------|
   | c14 | 12 | 一次考 5 个 HTTP 状态码 | 拆成 5 张 cloze |
   | c31 | 9 | `SIGTERM=15` / `SIGKILL=9` 互相干扰 | 改问"哪个信号能被进程捕获" |
   | c47 | 8 | 你其实随手就能查的 API 签名 | 挂起——规则 6，可查的别背 |
4. `python3 scripts/sm2.py forecast 14` 确认改卡后负荷回落
5. 回报：*"改完这 6 张，预计留存率两周内回到 85% 以上。另外你 `new_cards_per_day` 是 25，建议降到 10。"*

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| 连续高分导致 `OverflowError: date value out of range` | **必须设 `MAX_INTERVAL`**（本 skill 为 3650 天）。约 30 次连续 q=5 就会让间隔超出 `datetime.date.max`。授权阶段真实触发，T6 断言已锁死此回归。 |
| lapse 时同时扣 EF，卡片再也翻不了身 | 经典 SM-2 在失败时**只重置 reps，不扣 EF**。两者都做会让 EF 两天内跌到 1.3 下限并永久卡死，该卡从此天天复习。见 `references/algorithms.md` 第 2 节。 |
| 用户每张都自评 5 | 间隔跑得比真实记忆快，两周后集体崩盘。Agent 监测到 >70% 评分为 5 时主动提示；强调 3（吃力但答对）和 4（迟疑后答对）的分界。 |
| 一次导入几百张卡 | 每张新卡产生 ~8–10 次未来复习。狂加 50 张 → 下月某天 400 次复习。用 `forecast` 先看负荷，`new_cards_per_day` 限流。 |
| 硬背 leech 卡 | leech 是**卡片设计 bug**，不是记性问题。按拆卡→改写→加助记→挂起的顺序处方，别加大复习强度。 |
| 直接套用别人的共享 deck，立刻全变 leech | 别人写的卡没有你的个人语境（规则 5）。要么自己重写，要么只当素材来源。 |
| 把可查的参考资料做成卡 | 完整 config schema、冷门 flag 属于笔记不属于复习队列。判据：你会乐意在干活时 `grep` 它吗？会 → 别做卡。 |
| 跨时区/夏令时导致"今天"漂移 | 本 skill 全程用**本地日期 ISO 串**（`YYYY-MM-DD`），不存时间不存时区。当天到期即全天有效，规避 DST 边界问题。 |
| 直接手改 `cards.json` 改坏了 JSON | 改完必须 `python3 -m json.tool ~/.hermes/data/srs/cards.json` 验一遍。优先用 CLI 而不是手编。 |
| 想迁移到 Anki/FSRS 时怕丢历史 | `history[]` 保留了全部 `(date, quality)` 对，正是 FSRS 拟合权重所需。SM-2 在 deck 攒够 ~1000 次复习前与 FSRS 排期几乎一致，不必急着迁。 |
| 一张卡答对了一半却不知道打几分 | 这是**一卡多事**的信号（规则 1），不是评分难题。拆卡，别纠结分数。 |

---

## Verification Checklist

- [ ] `python3 scripts/test_sm2.py` 25 条断言全部 PASS
- [ ] `MAX_INTERVAL` 上限存在，连续 30 次 q=5 不抛 `OverflowError`（T6）
- [ ] 首轮成功间隔 = 1 天，第二轮 = 6 天（SM-2 固定步，T1/T2）
- [ ] 第三轮起间隔 = `round(上次间隔 × EF)`（T3）
- [ ] lapse 后 `interval` 归 1、`reps` 归 0、`lapses` +1，且 EF 未被额外惩罚（T4）
- [ ] EF 严格夹在 [1.3, 2.7] 区间内（T5/T6）
- [ ] 累计失败 ≥8 次自动置 `leech: true` 并被 `leeches()` 捕获（T7）
- [ ] 到期队列按"逾期优先 → EF 低优先"排序，且 `limit` 生效（T8）
- [ ] 未复习的卡库 retention 返回 `None` 而非除零崩溃（T9）
- [ ] 非法评分（如 9）抛 `ValueError`（T10）
- [ ] `cards.json` JSON 往返无损（T11）
- [ ] `forecast` 天数与当日计数正确（T12）
- [ ] `templates/cards.json` 能被真实 CLI 直接加载（已实测 `due`/`grade`/`stats` 三条命令）
- [ ] 加卡前跑过卡质量检查，多事实卡已拆分
- [ ] 所有日期为本地 ISO 日期串，无时区字段
- [ ] 数据只写 `~/.hermes/data/srs/`（或 `SRS_PATH`），无任何网络请求

---

## Data Sources & Accuracy

**数据存储：** 全部本地，单文件 `~/.hermes/data/srs/cards.json`（`SRS_PATH` 可覆盖）。零网络请求、零云同步、零遥测。卡片内容和复习记录不离开本机。

**算法来源：** SM-2 来自 Wozniak & Gorzelanczyk (1994) 及 SuperMemo 公开的 Algorithm SM-2 描述；leech 阈值 8 次对齐 Anki 默认值；卡片写法规则来自 Wozniak《Twenty rules of formulating knowledge》(1999) 与 Nielsen《Augmenting Long-term Memory》(2018)。完整出处见 `references/algorithms.md` 与 `references/card-writing-rules.md` 的 Sources 段。

**准确性边界：**
- 间隔数字是**算法输出，不是对你个人记忆的测量**。SM-2 是启发式，不是针对你拟合的模型。
- `retention%` 依赖**自评质量**。自评虚高 → 留存率虚高，且间隔会过度拉长。这是本 skill 最大的误差源，无法从数据侧修正，只能靠评分诚实度。
- 遗忘曲线 `R(t) = e^(-t/S)` 是群体层面的近似，个体差异显著。
- FSRS 通常比 SM-2 少 20–30% 复习量，但需要约 1000 次复习历史来拟合权重；本 skill 选 SM-2 是因为零依赖、零训练数据即可工作。该数字引自 FSRS 项目公开对比，非本 skill 实测。
- 本文档中所有 `实测输出` 代码块均为 `scripts/sm2.py` 与 `scripts/test_sm2.py` 的真实运行结果（日期基准 2026-08-29），非手写示意。
