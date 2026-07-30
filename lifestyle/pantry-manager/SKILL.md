---
name: pantry-manager
description: "Use when tracking pantry, fridge, or freezer inventory; logging groceries by natural language; finding food that expires soon; planning meals from what is already available; or generating a deduplicated shopping list. Local-first and barcode-optional."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, pantry, groceries, inventory, expiration, meal-planning, food-waste, local-first]
    related_skills: [recipe-generator, personal-expense-tracker, home-maintenance-tracker]
---

# Pantry Manager / 家庭食材库存管家

> 知道家里有什么、什么快坏了、今晚先吃什么；先消耗库存，再去买菜。

## Overview

Pantry Manager 把冰箱、冷冻室和储物柜变成一份可核对的本地库存。用户可以用自然语言入库、消耗、移动、盘点和查询；Agent 将模糊单位标准化，按保质期排序，并基于现有食材生成“先吃清单”和缺口最小的购物单。

| 能力 | 做什么 | 典型场景 |
|---|---|---|
| 自然语言记账 | 解析品名、数量、单位、位置、日期 | “买了两盒鸡蛋和 3 个牛油果” |
| 批次级库存 | 同一食材按购买/开封/到期批次分开 | 先用旧牛奶，不覆盖新牛奶 |
| 临期提醒 | 计算已过期、48 小时、7 天风险 | 减少食物浪费 |
| 先进先出 | 消耗最早到期批次 | “用了 200ml 牛奶” |
| 库存驱动做饭 | 优先临期食材，列出缺少项 | 今晚吃什么 |
| 购物清单 | 对照目标库存和现有数量去重 | 不重复买盐和酱油 |
| 本地优先 | JSON 文件，不要求账号或云服务 | 可备份、可迁移、隐私可控 |

默认目录为 `~/.hermes/data/pantry-manager/`。复制 [templates/pantry.json](templates/pantry.json) 作为初始账本；字段与日期规则见 [references/storage-rules.md](references/storage-rules.md)；每次批量修改后运行 [scripts/validate.py](scripts/validate.py)。

## When to Use

- “冰箱里还有什么？”
- “牛奶明天到期，今晚能做什么？”
- “买了 500g 鸡胸、两盒蘑菇，记一下。”
- “我用了三个鸡蛋和半袋菠菜。”
- “周末做咖喱，看看家里缺什么，生成购物清单。”
- “盘点冷冻室，把没确认过的项目列出来。”
- 用户希望按临期、位置、类别或数量查询家庭食材。

不用于：医疗级饮食建议、食物安全检测、自动下单，或替代包装标签与当地食品安全部门指导。`recipe-generator` 负责创作菜谱；本 skill 负责库存事实、临期优先级和采购缺口。

## Core Workflow

### Step 1：初始化库存与规则

```bash
mkdir -p ~/.hermes/data/pantry-manager
cp templates/pantry.json ~/.hermes/data/pantry-manager/pantry.json
python3 scripts/validate.py ~/.hermes/data/pantry-manager/pantry.json
```

初始化时只确认高价值偏好：

1. 存储区域：`pantry`、`fridge`、`freezer`，以及用户自定义区域。
2. 日期格式统一为 ISO `YYYY-MM-DD`。
3. 默认临期窗口：冷藏 3 天、常温 14 天、冷冻 30 天；用户可覆盖。
4. 常用计量单位：`g`、`kg`、`ml`、`l`、`count`、`pack`。
5. 是否追踪“最低库存”；仅对经常补货的主食和调味料开启。

不要扫描 `.env`、`auth.json` 或邮件账号来猜购物记录。需要导入收据时，让用户提供经过确认的文本或 CSV。

### Step 2：记录入库，保留批次

每次入库创建独立批次，不因名称相同而覆盖：

```text
用户：刚买了两瓶 1L 牛奶，一瓶 8 月 3 日到期，一瓶 8 月 8 日到期。
Agent：已建立 2 个 milk 批次，各 1000 ml，位置 fridge，到期日分别为 2026-08-03 和 2026-08-08。
```

解析规则：

- 保留用户原始文本到 `source_note`，标准化名称写入 `name`。
- “一袋”“一盒”无法换算时保留 `pack`，不要编造克数。
- 包装上的 `best before` 与 `use by` 不等价，写入 `date_type`。
- 只有日期没有年份时，结合当前日期选择最近的未来日期，并明确回显假设。
- 没有到期日则写 `null`；可提供保守估计，但必须标记 `estimated_expiry: true`。
- 已开封时记录 `opened_at`，必要时使用更短的开封后期限。

### Step 3：消耗、移动和纠错

消耗默认采用 **FEFO（First Expired, First Out，最早到期先用）**：

1. 找到标准化名称相同且状态为 `active` 的批次。
2. 按有效日期排序：`use_by` → `best_before` → 无日期。
3. 从最早批次扣减，允许一次消耗跨多个批次。
4. 数量降为 0 时标记 `consumed`，不删除历史。
5. 单位不兼容时停止扣减并要求换算依据，例如 `count` 不能自动减 `g`。

常见更新：

```text
“用了 300ml 牛奶” → 从最早到期批次扣减
“鸡胸移到冷冻室” → 更新 location，并记录 moved_at
“刚才不是 5 个苹果，是 6 个” → 追加 adjustment，不静默改历史
“这盒草莓坏了” → 状态 spoiled，并计入浪费统计
```

### Step 4：生成临期队列与食物安全提示

每天或每次查询时计算：

- **expired**：有效日期早于今天。
- **urgent**：0–2 天内到期，或已开封且接近开封后期限。
- **soon**：3–7 天内到期。
- **stable**：超过窗口或无明确短期风险。
- **unknown**：无日期且无法可靠估计。

排序优先级：`use_by` 过期 > 已开封 > 48 小时内 > 7 天内 > 无日期待盘点。

安全规则：

- `use by` 已过期的高风险冷藏食品不建议“闻一下继续吃”。
- `best before` 通常描述品质而非安全，但仍需检查包装、储存条件和当地指南。
- 停电、温度异常、包装鼓包、霉菌、异味等情况单独提高风险，不仅看日期。
- Agent 不声称能从文本判断食品安全；不确定时建议丢弃并参考当地官方指南。

### Step 5：从库存生成用餐方案

先选 1–3 个临期食材，再交给 `recipe-generator` 组合菜谱。每个建议必须列出：

1. 将消耗的库存批次与数量。
2. 已有食材。
3. 缺少食材及可选替代。
4. 是否满足用户的过敏、饮食或时间限制。
5. 做完后的预计剩余量。

不要为了“清库存”给出不合理组合。优先：完整一餐、缺口少、临期风险高、操作时间符合用户要求。

### Step 6：生成去重购物清单

购物清单来源可包括：用户明确要求、菜谱缺口、低于 `par_level` 的补货项。输出前：

- 从需求量中减去可用库存，但过期/损坏/预留批次不算可用。
- 合并标准化同义词，如 `scallion` / `green onion`；保留用户语言展示。
- 单位可换算才合并，不能把“2 个柠檬”和“200g 柠檬”硬拼。
- 按 produce、dairy、meat、frozen、dry goods、household 分区。
- 不自动购买；价格和店铺信息必须注明来源与抓取日期。

### Step 7：盘点与验证

建议每周快速盘点冷藏区、每月盘点常温和冷冻区：

1. 列出超过 30 天未确认的活跃批次。
2. 用户按“还有 / 用完 / 坏了 / 数量调整”确认。
3. 保留调整记录和盘点时间。
4. 验证账本结构：

```bash
python3 scripts/validate.py ~/.hermes/data/pantry-manager/pantry.json
```

预期成功输出：`OK: pantry.json (... active batches)`。验证失败时先备份原文件，再修正；不要用空模板覆盖真实库存。

## Example Invocations

### 示例 1：入库并提示临期

**User：**“买了 12 个鸡蛋、500g 鸡胸和两盒蘑菇。鸡胸 8 月 1 日到期，蘑菇大概三天内吃。”

**Agent：**
> 已记录 3 类、4 个批次：鸡蛋 12 count（到期未知）、鸡胸 500g（use-by 2026-08-01）、蘑菇 2 pack（预计 2026-08-01，标记为估算）。鸡胸和蘑菇进入 urgent 队列。包装上的鸡蛋日期方便确认吗？若没有，我会保持 unknown，不替你编日期。

### 示例 2：先吃什么

**User：**“冰箱里牛奶明天到期，菠菜也蔫了，20 分钟能做什么？”

**Agent：**
> 优先消耗牛奶和菠菜。建议：菠菜奶香炒蛋，约 15 分钟；库存可用：菠菜 180g、牛奶 250ml、鸡蛋 4 个。缺口：无。预计做完剩余牛奶 150ml、鸡蛋 1 个。若菠菜已有黏液或明显异味，不建议使用；仅“有点蔫”可先确认状态。要我按实际用量扣库存吗？

### 示例 3：购物清单去重

**User：**“周末做番茄牛肉意面，给 4 个人列购物清单，先看家里有什么。”

**Agent：**
> 库存已有：意面 700g、罐装番茄 2×400g、洋葱 2 个、橄榄油。缺少：牛肉末约 500g、大蒜 1 头、帕玛森 100g；盐和黑胡椒高于最低库存，不重复加入。清单已按肉类、蔬果、乳制品分组。数量基于 4 人份估算，购买前请确认是否有人不吃牛肉或乳制品。

## Common Pitfalls

| 问题 | 解决方案 |
|---|---|
| 同名食材合并后丢失到期日 | 保留批次；展示时可汇总，扣减时按 FEFO |
| 把 `best before` 当成 `use by` | 保存 `date_type`，安全提示使用不同措辞 |
| “一盒”被擅自换成克数 | 无包装规格就保留 `pack`，不要伪造换算 |
| 用户说“用了半袋”但原批次是克 | 若净重已知则换算；未知则记录剩余比例或要求确认 |
| 只按日期判断安全 | 同时考虑开封、温度、包装、污染迹象和官方指南 |
| 没日期就生成精确到期日 | 使用 `null` 或清晰标记估算值与依据 |
| 自动把购物清单当订单提交 | 默认只生成清单，任何购买都需用户明确授权 |
| 盘点时直接删除不存在项目 | 改状态并保留历史，便于分析消耗和浪费 |
| 菜谱忽略过敏或饮食限制 | 每次生成前应用用户已确认的约束；未知则标注 |
| 在 Git 中提交家庭饮食隐私 | 数据目录保持本地，公开仓库只提交空模板 |

## Verification Checklist

- [ ] `name` 与目录 `pantry-manager` 一致
- [ ] 每个库存项有唯一 `id`、标准化名称、数量、单位和位置
- [ ] 同名不同到期日保持独立批次
- [ ] 日期为 ISO 格式，未知值使用 `null`
- [ ] 估算日期带 `estimated_expiry: true`
- [ ] `best_before` 与 `use_by` 未混用
- [ ] 消耗按 FEFO 且不会产生负库存
- [ ] 单位不兼容时未自动换算
- [ ] 过期或损坏批次未计入可用库存
- [ ] 购物清单已扣除可用库存并去重
- [ ] 食物安全提示未作确定性诊断
- [ ] 批量修改后 `scripts/validate.py` 返回 `OK`
- [ ] 本地数据不包含凭证，也未提交到公共仓库

## Data Sources & Accuracy

- **库存事实**：以用户确认、包装标签、收据文本和实际盘点为准。Agent 推断不能覆盖用户确认值。
- **日期含义**：`use by`、`best before`、`sell by` 在不同国家/地区定义不同；保存标签原文和地区，解释时优先当地食品安全部门规则。
- **估算保质期**：只能作为盘点优先级，不是安全保证。必须记录估算依据和创建日期。
- **菜谱数量**：份量与消耗量为估计；实际包装规格、烹饪损耗和食量会造成偏差。
- **价格/商店数据**：若联网查询，记录 URL、货币、地区、抓取日期；促销和库存会快速变化。
- **隐私与安全**：默认只写 `~/.hermes/data/pantry-manager/`。不得读取或输出 `.env`、`auth.json`、令牌、银行卡号或不必要的家庭敏感信息。
