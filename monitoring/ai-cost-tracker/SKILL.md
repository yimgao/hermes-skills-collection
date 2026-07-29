---
name: ai-cost-tracker
description: "Track AI/LLM API spend per provider, model, and project — log calls by chat, see daily/weekly/monthly burn, get budget alerts, find costly prompts, and project end-of-month cost. Covers OpenAI, Anthropic, Google, DeepSeek, Mistral, Groq, Ollama, vLLM, and custom endpoints."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [monitoring, finance, ai-costs, llm-spend, api-tracking, budgeting, observability, local-first]
    related_skills: [subscription-manager, prompt-library, prompt-benchmarker, model-comparator, daily-briefing]
---

# AI Cost Tracker / AI 花费追踪器

> 知道每一块钱花在哪个 provider、哪个 model、哪个项目上 —— 不靠发票、账单或公司报销系统。

## Overview

AI Cost Tracker 是一个本地优先的 LLM 花费账本。它不是账单解析器（账单通常 30 天后才到），而是一个**调用即记账**的工作流：每次 API 调用都记一行，按 provider / model / project / date 聚合，找出最贵 prompt、最烧钱项目、月底超支风险。

| 能力 | 作用 | 典型场景 |
|---|---|---|
| 聊天记账 | 用户说"刚调了 gpt-4o 12k 输入 1.8k 输出" → 自动入库 | 不想每次打开 dashboard |
| 自动归类 | 按 `provider`、`model`、`project`、`feature` 分组 | 多项目、多团队共用账号 |
| 实时趋势 | 今日 / 本周 / 本月 / 滚动 30 天 | 看到烧钱斜率 |
| 预算告警 | 设定月度上限，到 70% / 90% / 100% 提醒 | 避免月底天价账单 |
| 最贵 prompt 排行 | 找出输入 token 爆炸或反复 retry 的 prompt | 优化大上下文调用 |
| 月底预测 | 用近 7 天斜率线性外推月底数字 | 月初知道该不该收紧 |
| 本地优先 | 全部数据存 `~/.hermes/data/ai-costs.json` | 不上传任何云端 |
| Cron 兼容 | 可每日定时汇总 + 推送 | 接入 daily-briefing |

默认数据文件：`~/.hermes/data/ai-costs.json`（JSONL 格式，每调用一行）。预算配置：`~/.hermes/data/ai-costs-budget.json`。汇率可选 `~/.hermes/data/ai-costs-rates.json`。

## When to Use

- *“刚用 gpt-4o 跑了 8.2k 输入 / 1.4k 输出”*
- *“Add Anthropic claude-sonnet-4 5.1k in / 920 out on project ‘launch-deck’”*
- *“这个月 AI 花了多少？”*
- *“Set my monthly budget to $120, alert at 80%”*
- *“哪个 prompt 最贵？”*
- *“Project end-of-month spend？”*
- *“Compare OpenAI vs Anthropic cost this week”*
- *“Show me tokens per day for the last 14 days”*
- *“我刚调 DeepSeek 12k 输入 4k 输出”*
- *“按项目给我算一下这周烧了多少”*
- *“Set hard cap at $200/month — refuse any spend beyond”*
- *“Import my OpenAI usage CSV from June”*

不用于：抓取账单 PDF（用 `pdf-toolkit`）；模型选型决策（用 `model-comparator`）；prompt 效果对比（用 `prompt-benchmarker`）；已支付的月度总支出归档（用 `subscription-manager`）。

## Core Workflow

### Step 1：首次配置

第一次使用前，确认三个数据文件：

```bash
mkdir -p ~/.hermes/data
[ -f ~/.hermes/data/ai-costs.json ] || echo '{"version":1,"calls":[]}' > ~/.hermes/data/ai-costs.json
```

可选：写入预算文件：

```bash
cat > ~/.hermes/data/ai-costs-budget.json <<'EOF'
{
  "monthly_usd": 120,
  "alert_thresholds_pct": [70, 90, 100],
  "hard_cap_usd": 200,
  "currency_display": "USD",
  "projects": {
    "launch-deck":   { "monthly_usd": 50 },
    "research-bot":  { "monthly_usd": 40 },
    "_default":      { "monthly_usd": 80 }
  }
}
EOF
```

记录定价（agent 会引用，不需要每次问用户）：

```bash
cat > ~/.hermes/data/ai-costs-rates.json <<'EOF'
{
  "USD_per_1k_tokens": {
    "openai/gpt-4o":          { "input": 0.0025,  "output": 0.01   },
    "openai/gpt-4o-mini":     { "input": 0.00015, "output": 0.0006 },
    "openai/o1":              { "input": 0.015,   "output": 0.06   },
    "openai/o3-mini":         { "input": 0.0011,  "output": 0.0044 },
    "anthropic/claude-sonnet-4":  { "input": 0.003,   "output": 0.015  },
    "anthropic/claude-haiku-4":   { "input": 0.0008,  "output": 0.004  },
    "google/gemini-2.5-pro":      { "input": 0.00125, "output": 0.01   },
    "google/gemini-2.5-flash":    { "input": 0.0003,  "output": 0.0025 },
    "deepseek/deepseek-chat":     { "input": 0.00027, "output": 0.0011 },
    "groq/llama-3.3-70b":         { "input": 0.00059, "output": 0.00079 },
    "local/ollama":               { "input": 0,       "output": 0      }
  },
  "last_updated": "2026-07-28"
}
EOF
```

- 价格必须标注来源（OpenAI 定价页、Anthropic 文档等），过期超过 30 天需用户确认是否更新。
- 用户若报自定义 endpoint（例如自托管 vLLM），`provider` 用 `local`，单价格全部写 0；`cost_usd` 也置 0，但仍记录 token 用于容量规划。
- 多货币支持：`cost_usd` 始终是基准货币；本地货币可在导出时换算。

### Step 2：单次记账

用户典型说法：

> *“Logged gpt-4o, project launch-deck, 8200 in, 1400 out.”*

Agent 解析并生成一行 JSONL：

```json
{
  "ts": "2026-07-28T14:32:11Z",
  "provider": "openai",
  "model": "gpt-4o",
  "project": "launch-deck",
  "feature": "draft-reply",
  "input_tokens": 8200,
  "output_tokens": 1400,
  "cache_read_tokens": 0,
  "cache_write_tokens": 0,
  "cost_usd": 0.0345,
  "source": "chat",
  "notes": null
}
```

字段规则：

- **必填**：`ts`、`provider`、`model`、`input_tokens`、`output_tokens`。
- **可选**：`project`（默认 `_unassigned`）、`feature`（agent 内部子任务，如 `summarize`、`embed`）、`cache_*`（Anthropic / OpenAI prompt caching）、`source`（`chat` / `csv` / `api`）、`notes`。
- 数字支持 `1.2k` / `1.2K` / `1.2 thousand` / 纯数字。`M` / `million` 视情况接受，但要二次确认。
- 用户报 `image` / `audio` / `embedding` 维度时，记录到 `notes` 里并标 `[非token计费，待核对]`，不假装计算。
- Agent **必须**用定价表算出 `cost_usd`，而不是凭空捏造；找不到的 model 必须问用户单价，绝不脑补。

写入文件：

```bash
jq -c '.calls += [<new_row>]' ~/.hermes/data/ai-costs.json \
  | sponge ~/.hermes/data/ai-costs.json
# 如果没有 sponge：
jq -c '.calls += [<new_row>]' ~/.hermes/data/ai-costs.json \
  > ~/.hermes/data/ai-costs.json.tmp \
  && mv ~/.hermes/data/ai-costs.json.tmp ~/.hermes/data/ai-costs.json
```

### Step 3：聚合查询

最少要支持以下 7 类查询（默认时区是 `~/.hermes/config.yaml` 的 `timezone`，否则 UTC）：

```bash
# 今日总览
jq '[.calls[] | select(.ts | startswith("2026-07-28"))]
      | {count: length, usd: (map(.cost_usd) | add)}' \
   ~/.hermes/data/ai-costs.json

# 本月按 provider 聚合
jq --arg ym '2026-07' '
  [.calls[] | select(.ts | startswith($ym))]
  | group_by(.provider)
  | map({provider: .[0].provider,
         usd: (map(.cost_usd) | add | .*1000|round/1000),
         calls: length})
' ~/.hermes/data/ai-costs.json

# 按 project
jq '[.calls[]] | group_by(.project)
  | map({project: .[0].project,
         usd: (map(.cost_usd) | add),
         tokens_in:  (map(.input_tokens)  | add),
         tokens_out: (map(.output_tokens) | add)})' \
   ~/.hermes/data/ai-costs.json
```

Agent 回答时必须给出：

1. **当期总额**（金额 + 调用次数）。
2. **Top 3** provider / model / project 排序（带百分比）。
3. **对比前期**：与上月同日 / 上周同日对比（多了多少 %）。
4. **月底预测**：用近 7 天的日均 × 当月剩余天数，标注 `linear_extrapolation`。
5. **预算状态**：剩余预算 = `monthly_usd` − 当月已花；触发阈值时主动提醒。

### Step 4：预算告警与硬上限

每次写入或聚合后检查：

```python
spent = current_month_total_usd(project)
limit = budget["projects"].get(project, budget["projects"]["_default"])["monthly_usd"]
pct = spent / limit * 100

for t in budget["alert_thresholds_pct"]:  # [70, 90, 100]
    if pct >= t and not already_alerted(t, project, month):
        notify(f"⚠️  AI cost {pct:.0f}% of monthly cap "
               f"(${spent:.2f}/${limit:.2f}) for project '{project}'")
        mark_alerted(t, project, month)

if budget.get("hard_cap_usd") and global_spent >= budget["hard_cap_usd"]:
    raise HardCapExceeded(global_spent, budget["hard_cap_usd"])
```

- **软提醒**：70% / 90% 时只发通知，仍允许记账。
- **硬上限**：超过 `hard_cap_usd` 时**拒绝**写入并提示用户 `Increase cap or pause project`；agent 不替用户做暂停决定。
- **去重**：同一 project 同一阈值同一月只发一次；写入 `~/.hermes/data/ai-costs-alerts.log`。

### Step 5：找最贵 prompt

```bash
jq '[.calls[] | select(.ts | startswith("2026-07"))]
  | sort_by(-.cost_usd) | .[0:10]
  | map({ts, project, model,
         cost_usd: (.cost_usd|.*1000|round/1000),
         in:  .input_tokens,
         out: .output_tokens})' \
   ~/.hermes/data/ai-costs.json
```

Agent 在结果里给出三条诊断：

1. **大上下文嫌疑**：当 `input_tokens > 50_000` 且 `cost_usd` 排名前列 —— 提示检查 prompt 模板或分段。
2. **循环 retry 嫌疑**：同一 `project` + `feature` 一天内 ≥ 5 次相似 token 量 —— 可能是错误循环。
3. **昂贵 model 错配嫌疑**：分类、抽取等轻任务用了 `o1` / `claude-sonnet-4` —— 推荐换 `gpt-4o-mini` / `claude-haiku-4`。

提示用户可能想用 `prompt-library` 或 `prompt-benchmarker` 做后续优化；agent 不替用户直接修改 prompt。

### Step 6：批量导入与对账

支持两种导入源：

**a) OpenAI Usage CSV**

```bash
python3 scripts/import_openai_csv.py \
  --in  ~/Downloads/openai-usage-2026-06.csv \
  --out ~/.hermes/data/ai-costs.json
```

必填列：`timestamp` / `model` / `input_tokens` / `output_tokens`。CSV 中已有金额字段时优先使用并写入 `cost_usd_source: "csv"`，否则用定价表重算并标注 `cost_usd_source: "rates"`。

**b) Anthropic / 自定义 JSON**

```bash
python3 scripts/import_jsonl.py \
  --provider anthropic \
  --in  ~/Downloads/anthropic-2026-06.jsonl \
  --out ~/.hermes/data/ai-costs.json
```

导入后必须跑对账脚本：

```bash
python3 scripts/reconcile.py \
  --calls ~/.hermes/data/ai-costs.json \
  --csv   ~/Downloads/openai-usage-2026-06.csv
```

输出 `delta_usd`、`delta_pct`、最大单笔差异。如差异 > 5%，先报告再决定保留哪一边；agent 不擅自覆盖用户原始 CSV。

### Step 7：周报与 cron

```bash
# 手动周报（过去 7 天）
hermes -s ai-cost-tracker "weekly AI spend report"

# 每日 23:50 推送当月汇总到 daily-briefing
hermes cron add ai-cost-daily \
  --schedule "50 23 * * *" \
  --skill ai-cost-tracker \
  --prompt "Render today's daily AI cost card (spent, top project, projected EOM)"
```

cron prompt 应输出 ≤ 12 行的卡片：金额、Top 3 project、剩余预算、当月 EOM 预测、与昨日对比 delta。不要在 cron 输出里贴整张 JSON。

## Example Invocations

### 示例 1：单次记账 + 触发预算告警

**User：** *“Just used claude-sonnet-4 for project 'research-bot', 51k in, 9.2k out.”*

**Agent：**

> 已写入 1 行。`cost_usd = 0.003 × 51 + 0.015 × 9.2 = $0.291`。本月 `research-bot` 已花 $32.84 / $40 限额 = **82.1%**，触发 80% 告警阈值（第一次）。剩余 $7.16 ≈ 还能跑约 24 次同等调用。是否要：(a) 上调该 project 限额、(b) 切到 `claude-haiku-4`（约 1/4 价）、(c) 加 prompt cache 减少 input token？等你的决定再动配置。

### 示例 2：月底预测

**User：** *“What will I spend on AI this month end?”*

**Agent：**

> 截至 2026-07-28 已用 **$84.12**（调用 4,217 次）。近 7 天日均 $4.62 × 剩余 3 天 = 线性外推 **$97.98**。预算 $120，节奏在轨。若保持当前斜率，月底剩余 $22。提示：7/22 那天的 `gpt-4o` 单笔 $6.30（project `launch-deck`）拉高了斜率 —— 想看那次的 prompt 吗？

### 示例 3：最贵 prompt 排查

**User：** *“Find the 5 most expensive calls this month.”*

**Agent：**

> Top 5 已列出。诊断：
>
> 1. `$6.30` / 7/22 / `launch-deck` / `gpt-4o` — `input=1.8M, output=4.1k`，**疑似粘贴整本书做摘要**。
> 2. `$3.85` / 7/19 / `research-bot` / `claude-sonnet-4` — `feature=retry-loop`，当日 18 次同 token 量调用，**疑似错误循环**。
> 3. `$2.10` / 7/24 / `launch-deck` / `claude-sonnet-4` — `feature=classify-email`，**疑似昂贵 model 错配**，可换 `haiku-4` 省 75%。
>
> 原始 JSONL 已附在附件；未做修改。建议下一步用 `prompt-library` 归档这次诊断，或用 `prompt-benchmarker` 对比 cheaper model 效果。

## Common Pitfalls

| 问题 | 解决方案 |
|---|---|
| 用户报“几 k tokens”但数字含糊 | 强制要 `12345` 或 `12.3k` 形式；不允许脑补 |
| Model 拼写错误（`gpt4o` / `claude-sonnet`） | 模糊匹配 + 列出候选项让用户选 |
| 定价表过期超过 30 天 | 提示用户确认，不静默用旧价 |
| 重复记账（同一调用记两次） | 检查最近 60 秒同 `(provider, model, tokens_in, tokens_out, project)` 是否已存在 |
| 多货币混入（USD / RMB / EUR） | 统一换算到基准货币并标注汇率来源；汇率也存 `ai-costs-rates.json` |
| 把 `image` / `audio` / `embedding` 当 token 算 | 记 `notes` 并标 `[非token]`，不假装换算成 USD |
| 用户忘记 `project` 字段 | 默认 `_unassigned`，但聚合里要明确显示提醒 |
| 硬上限触发后仍继续记 | 抛错并停止写入；不替用户做放宽决定 |
| 导入 CSV 覆盖已有数据 | 永远用 append + `source` 字段；冲突时只追加新行 |
| 误把 `cache_read` 当 `input` 计费 | 严格按 provider 规则：`cache_read` 通常 0.1× 输入价，`cache_write` 通常 1.25× |
| 用户用本地 Ollama / vLLM | 单价全 0，但 token 必须照记，便于容量规划 |
| agent 把推断的 cost_usd 写成权威值 | `cost_usd_source` 必须为 `rates` / `csv` / `api` 之一，未知则 `[待确认]` |

## Verification Checklist

- [ ] 数据文件 `~/.hermes/data/ai-costs.json` 存在且是合法 JSON
- [ ] 预算文件 `~/.hermes/data/ai-costs-budget.json` 已读
- [ ] 定价文件 `~/.hermes/data/ai-costs-rates.json` 含 `last_updated` 且未超 30 天（过期要问）
- [ ] 每条记录含 `ts / provider / model / input_tokens / output_tokens / cost_usd`
- [ ] `provider` 来自受控词表（openai / anthropic / google / deepseek / mistral / groq / local / other）
- [ ] `cost_usd >= 0` 且 `cost_usd_source` 明确
- [ ] 重复检测：60 秒窗口内同 `(provider, model, tokens_in, tokens_out, project)` 已去重
- [ ] 聚合查询使用了 `jq` 或 Python `json` 模块，未引入未声明依赖
- [ ] 预算告警去重：同 `(project, threshold, ym)` 只发一次
- [ ] 硬上限超额时写入被拒绝并明确提示
- [ ] CSV 导入是 append，未覆盖；`source="csv"` 已标记
- [ ] 所有计算结果可追溯：用户可复现每个 `cost_usd`
- [ ] 数据文件中无 API key、token、cookie、邮箱明文

## Data Sources & Accuracy

- **首要数据源**：用户即时提供的 `input_tokens` / `output_tokens` / `provider` / `model`。Agent **不**主动调任何厂商 API（用户明确要求且授权时除外），所有计费靠本地定价表。
- **定价表来源**：OpenAI 定价页（`https://openai.com/api/pricing/`）、Anthropic 定价页、Google AI Studio、DeepSeek / Groq / Mistral 公开定价。每次写入必须带 `last_updated`；过期强制询问用户。
- **汇率来源**：如使用 `currency_display` 非 USD，每日用 `https://api.frankfurter.app/latest?from=USD`（无需 key）拉取，并写入 `ai-costs-rates.json` 的 `fx` 字段；网络失败时回退到上日汇率并标注 `[stale]`。
- **CSV 账单**：用户提供的官方使用 CSV 优先于本地定价表；对账后差额写入 `reconcile.log`，不擅自修改用户原始账单。
- **推断标记**：当 token 数由“几 k”模糊推断时，标 `[estimated]` 并在 24 小时内允许用户修正；agent 不假装精度。
- **概率 / 预测**：月底预测是线性外推，必须明确写 `linear_extrapolation`，不要写成“确定金额”；预算告警是确定性事实，可直接说。
- **隐私**：默认本地 JSON；`.env` / `auth.json` / API key 永不进入数据文件；导出到 Git 前先 grep `sk-` / `Bearer` / 邮箱字面量。
- **不替用户决定**：不自动停用项目、不自动切 model、不自动调价；任何写配置的操作必须显式确认。