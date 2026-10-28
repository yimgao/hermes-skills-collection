---
name: purchase-advisor
description: "Use when deciding whether and what to buy — laptops, phones, appliances, cameras, furniture, e-bikes, TVs, gym memberships, or any purchase over ~$200. Compares candidates on total cost of ownership (not sticker price), checks whether today's price is genuinely a good deal against your own price history, detects fake discounts, scores specs by what YOU weight, and returns a BUY / FAIR / WAIT / SKIP verdict with a pasteable decision brief. Local JSON, no account needed."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, purchase, shopping, tco, price-tracking, decision, deal, buy, comparison, electronics, appliances]
    related_skills: [receipt-vault, personal-expense-tracker, bill-negotiator, subscription-manager, renewal-reminder, gift-finder, weekly-meal-planner]
---

# Purchase Advisor / 购买决策顾问

> You spent four evenings comparing laptops. The winning laptop cost $1,399. Then you found out the "free" 3-year warranty was $299, the tax was $110, the case you needed was $60, and your old laptop was worth $0 — not the $200 the trade-in page promised. Two years in, the thing cost **$1,870**, not $1,399.

This skill replaces sticker-price comparisons with **total cost of ownership**, replaces "is this on sale?" with "**is this a real deal against my own history?**", and ends with a **decision brief** you can paste to a partner, a group chat, or your future self.

## Overview

| 能力 | 命令 / 触发 | 输出 |
|---|---|---|
| 📊 总拥有成本 | `tco.py compare -d <id>` | 每个候选的 TCO 拆解 + 每月成本 + 排序 + 结论 |
| 🎯 规格打分 | `--spec key:value` | 6 维规格矩阵，按你的权重归一化打分 |
| ⚖️ 加权评分 | `--w-price / --w-specs / --w-*` | 综合分（价格 × 0.45 + 规格 × 0.55，按调研完整度扣分） |
| 💰 价格历史 | `pricecheck.py log --product "..." --price N` | 建立价格基线（本地 JSON，可 cron 定期记录） |
| 🏷️ 是不是真打折 | `pricecheck.py check --product "..."` | 当前价在历史区间的百分位 + 假折扣检测 |
| 🎯 目标价 | `pricecheck.py target --product "..." --target N` | 到目标价才买；否则给 WAIT |
| 📄 决策简报 | `brief.py -d <id>` | 7 节 Markdown 简报：结论/排序/TCO/风险/规格/缺口/下一步 |
| 🚨 隐藏成本预警 | 自动 | 订阅/保险/耗材占比过高时告警 |
| 🔁 定期盯价 | cron | 每周自动记录报价并在跌破目标价时提醒 |

**核心原则：买的是「未来 N 年的总成本」，不是「今天标签上的数字」。**

## When to Use

- 要买一台超过 $200 的东西，纠结于两三个型号
- 看到「原价 $1,299，现价 $899」的折扣，不确定是不是真的
- 想知道自己现在买还是等大促（双十一 / 黑五 / 开学季）
- 需要给伴侣 / 家人 / 同事解释「为什么选这个而不是那个」
- 想给一台设备估算几年内的真实花费（换机周期规划）
- 中文场景：`帮我比一下这三台笔记本`、`这个价格算便宜吗`、`现在买还是等双十一`、`帮我列个买相机的决策简报`
- 健身房年卡、相机、显示器、洗衣机、电动自行车、家具 —— 都适用

## Core Workflow

### Step 1: 定义决策（不要跳过）

先确定这四个参数，否则后面所有数字都是假的。

| 参数 | 说明 | 例 |
|---|---|---|
| **决策 ID** | 本地文件名，短横线分隔 | `laptop-2026` |
| **品类** | 用于挑选适用维度 | `laptop` / `appliance` / `furniture` |
| **评估周期** | 你预计用多久 —— **最关键** | 笔记本 4 年，手机 3 年，咖啡机 3 年 |
| **预算上限** | 超过就不看 | `2000 USD` |

> **周期决定结论。** 一台 $700 的意式咖啡机按 1 年算很贵，按 5 年算很便宜。**周期短就比总价，周期长就比每年成本 + 残值。**

```bash
S=~/dev/skills/hermes-skills-collection/lifestyle/purchase-advisor/scripts

# 建决策（第一个候选的 --title / --category / --horizon 会被记录下来）
python3 $S/tco.py -d laptop-2026 add --name "MacBook Air M4" \
  --price 1299 --tax 8.5 --horizon 4 --category laptop \
  --title "2026 主力笔记本" --currency USD
```

### Step 2: 录入候选（含隐藏成本）

**每个候选至少要有**：价格、税费、必需配件、残值。**漏掉配件是最常见的低估来源。**

```bash
python3 $S/tco.py -d laptop-2026 add --name "MacBook Air M4" \
  --price 1299 \
  --tax 8.5 \
  --accessories 180 \          # 内存/外接屏/保护壳 —— 没有就是低估
  --shipping 0 \
  --setup 0 \
  --disposal 120 \             # 旧电脑回收/销毁
  --resale 500 \               # 4 年后预计残值（保守估）
  --warranty 199 \             # 一次性延保
  --warranty-years 4 \
  --spec performance:9 \
  --spec display:8 \
  --spec battery:9 \
  --spec build:9 \
  --spec support:8 \
  --spec ecosystem:9 \
  --source "apple.com" \
  --url "https://apple.com/macbook-air"
```

**TCO 公式（脚本实现的就是这个）：**

```
TCO = 标价
    + 必需配件 + 运费 + 部署/迁移成本 + 旧机处理
    + 税费（标价 + 配件）× 税率
    + 经常性成本（订阅 / 保险 / 耗材 / 保养 / 延保）× 年数
    − 残值抵扣

每月成本 = TCO ÷ 周期 ÷ 12
```

**周期性成本的两种写法**（脚本都支持）：

```bash
# 写法 A：年费 × 年数
--subscription-annual 120 --subscription-years 4

# 写法 B：一次性总额（贴在"设备本体"上的终身订阅，如打印机云服务）
--subscription 499
```

### Step 3: 规格打分（按你的需求，不是厂商的营销）

6 个维度各打 0–10 分。**分数反映"对这个决策的重要程度"，不是"参数好不好"**。

| 维度 | 关键问题 |
|---|---|
| `performance` | 主力负载能跑多快？会不会在第 3 年开始卡？ |
| `display` | 面板素质 + 尺寸 —— 你真的每天看吗？ |
| `battery` | 真实续航 —— 厂商标称打个 7 折 |
| `build` | 材质、手感、做工 —— 三年后还愿意用吗？ |
| `support` | 保修覆盖、官方维修点、备件供应年限 |
| `ecosystem` | 与你现有设备/软件/账号的兼容性 |

**调整权重**（默认全部为 1.0）：

```bash
# 我更在乎续航和生态，性能可以妥协
python3 $S/tco.py -d laptop-2026 compare --horizon 4 \
  --w-performance 0.6 --w-display 0.8 --w-battery 1.5 \
  --w-build 0.8 --w-support 0.7 --w-ecosystem 1.4 \
  --w-price 0.5 --w-specs 0.5
```

### Step 4: 跑比较，拿到结论

```bash
python3 $S/tco.py -d laptop-2026 compare --horizon 4
```

```
  Decision : 2026 主力笔记本
  Horizon  : 4 years   Currency: USD

  CANDIDATE                         TCO   per/mo  price  specs  cov   FINAL
  -------------------------------------------------------------------------
  MacBook Air M4               1,409.41    29.36   1.00   0.96    6   0.980
  ThinkPad X1 Carbon G13       1,517.91    31.62   0.50   0.85    6   0.694
  Dell XPS 14                  1,626.41    33.88   0.00   0.81    6   0.448

  VERDICT  : BUY
             - MacBook Air M4 leads by 0.286 and is cheapest over 4y
```

**四种结论：**

| 结论 | 含义 | 下一步 |
|---|---|---|
| `BUY` | 综合分领先且差距明显 | 买 |
| `WAIT — better value elsewhere` | 有个更便宜且规格相当的选项 | 先看那个 |
| `CLOSE — too close to call` | 前两名差距 < 0.08 | 按直觉/非价格因素选，或再查 |
| `HOLD — research incomplete` | 领先者还有规格项没查 | **补齐再决策** |

**规格覆盖不足时 `HOLD` 会自动触发** —— 这是刻意的：没研究完就下结论是大多数买错的原因。

### Step 5: 验证价格（这一步最容易被跳过，也最值钱）

**先建基线，再看今天的价。** 没有历史，"打折"只是一句广告词。

```bash
# 记录一次报价
python3 $S/pricecheck.py log --product "Sony WH-1000XM5" \
  --price 279 --date 2026-10-20 --source bhphoto --list-price 399

# 设目标价
python3 $S/pricecheck.py target --product "Sony WH-1000XM5" --target 300 --max 350

# 检查当前价
python3 $S/pricecheck.py check --product "Sony WH-1000XM5"
```

```
    observed low            279.00
    10th percentile         283.00
    median                  299.00
    90th percentile         338.20
    observed high           348.00
    current percentile rank      33.3%   (100% = cheapest ever seen)
    list price              399.00   claimed discount  30.1%

  VERDICT : BUY NOW
            - at or below your target price (300.00)
            - only 3 sample(s) — log more before treating the band as reliable
```

**假折扣自动检测：**

| 情形 | 判定 |
|---|---|
| 折扣 < 10% | 假打折 —— 价格根本没动 |
| 折扣 ≥ 50% | 疑似「从未真实存在过的划线价」—— 去比价网站核实历史价 |
| 当前价 ≥ 划线价 | 完全没有折扣 |
| 样本 < 4 条 | 价格带不可靠，别信 |

**定期盯价（cron）：**

```cron
# 每周一早上 9 点记录一次报价
0 9 * * 1 cd ~/dev/skills/hermes-skills-collection/lifestyle/purchase-advisor/scripts && \
  python3 pricecheck.py check --product "Sony WH-1000XM5"
```

### Step 6: 生成决策简报

```bash
python3 $S/brief.py -d laptop-2026 --horizon 4 --out ~/Desktop/laptop-decision.md
```

简报包含 7 节：

1. **结论** — 推荐 + 备选 + "什么会改变这个结论"
2. **候选排序** — 到手价 / TCO / 每月 / 价格分 / 规格分 / 综合分
3. **TCO 明细** — 每一分钱来自哪里（可被质疑，可被复核）
4. **风险与隐藏成本** — 自动告警 + 通用检查清单
5. **规格对照矩阵** — 6 维评分表
6. **调研缺口** — 明确告诉你还差什么没查
7. **下一步** — 可勾选的行动项

**直接贴给伴侣/群聊/未来的自己** —— 这就是它存在的意义。

## Example Invocations

### 例 1：两台笔记本，纠结了一周

**用户：**
> 我要换笔记本，预算 2000 以内，用 4 年。候选：MacBook Air M4 1299、XPS 14 1499、ThinkPad X1 Carbon G13 1399。帮我算算哪个划算，我比较看重续航和生态。

**Agent：**
```bash
S=~/dev/skills/hermes-skills-collection/lifestyle/purchase-advisor/scripts
python3 $S/tco.py -d laptop add --name "MacBook Air M4" --price 1299 --tax 8.5 \
  --accessories 150 --resale 500 --spec performance:9 --spec display:8 \
  --spec battery:9 --spec build:9 --spec support:8 --spec ecosystem:9
python3 $S/tco.py -d laptop add --name "Dell XPS 14" --price 1499 --tax 8.5 \
  --accessories 120 --resale 450 --spec performance:9 --spec display:9 \
  --spec battery:7 --spec build:8 --spec support:6 --spec ecosystem:5
python3 $S/tco.py -d laptop add --name "ThinkPad X1 Carbon G13" --price 1399 --tax 8.5 \
  --accessories 100 --resale 480 --spec performance:8 --spec display:8 \
  --spec battery:8 --spec build:9 --spec support:9 --spec ecosystem:4
python3 $S/tco.py -d laptop compare --horizon 4 \
  --w-battery 1.5 --w-ecosystem 1.4 --w-performance 0.6
python3 $S/brief.py -d laptop --horizon 4
```

**输出要点：** MacBook Air 以 0.98 综合分领先，4 年 TCO 1,409，月均 29.36 —— 在你加重了续航（1.5）和生态（1.4）权重后，X1 的续航优势不再抵消生态差距。简报第 6 节指出你还没查 X1 的 **support** 维度。

---

### 例 2：这个折扣是真的吗？

**用户：**
> 我看到索尼 WH-1000XM5 在某商城标价 399，现在卖 279，说"限时特惠"。划算吗？

**Agent：**
```bash
S=~/dev/skills/hermes-skills-collection/lifestyle/purchase-advisor/scripts
# 先建历史基线（你之前记的价格）
python3 $S/pricecheck.py log --product "Sony WH-1000XM5" --price 348 --date 2026-08-01 --source bestbuy --list-price 399
python3 $S/pricecheck.py log --product "Sony WH-1000XM5" --price 299 --date 2026-09-12 --source amazon
python3 $S/pricecheck.py log --product "Sony WH-1000XM5" --price 279 --date 2026-10-20 --source mall --list-price 399
python3 $S/pricecheck.py target --product "Sony WH-1000XM5" --target 300
python3 $S/pricecheck.py check --product "Sony WH-1000XM5"
```

**输出要点：** 当前价 279 处于历史区间的 33.3% 百分位，**低于你的目标价 300**，判定 `BUY NOW`。但脚本同时提示「只有 3 个样本」—— 建议再观察一周，或者用 `pricecheck.py log` 补两条历史记录再确认。划线价 399 确实存在（BestBuy 同月价），折扣 30% 属于真实促销，不是假打折。

---

### 例 3：健身年卡，别被"半价"骗了

**用户：**
> 健身房年卡标价 198，现在 99，说是半价促销，帮我判断。

**Agent：**
```bash
S=~/dev/skills/hermes-skills-collection/lifestyle/purchase-advisor/scripts
python3 $S/pricecheck.py log --product "Gym Membership Annual" --price 99 --date 2026-10-01 --source gym.com --list-price 198
python3 $S/pricecheck.py log --product "Gym Membership Annual" --price 99 --date 2026-10-20 --source gym.com --list-price 198
python3 $S/pricecheck.py check --product "Gym Membership Annual"
```

**输出要点：** 两个采样点价格完全相同（99），历史价带宽度为零 —— **这本身说明 198 从未是真实成交价**。脚本输出「claimed discount 50% — verify it is a genuine sale, not a never-real list price」。结论：`SKIP / WAIT`，请去比价网站核实真实年卡价格，并把 99 记为基线。

## Common Pitfalls

| 问题 | 解决方案 |
|---|---|
| 只比标价，不算配件 | 配件往往是 10–15% 的隐藏成本。`--accessories` 必填 |
| 忘了旧设备处理/残值 | `--disposal` 和 `--resale` 会让"贵的那个"变便宜，务必估算 |
| 评估周期设错 | 周期短→比总价；周期长→比月均 + 残值。用 `--horizon` 跑两遍对比 |
| 规格分按"参数好不好"打 | 应按**对你的重要程度**打分。调 `--w-*` 权重，而不是改分数 |
| 拿价格分和规格分直接比 | 两者量纲不同。必须先各自归一化（脚本已做） |
| 没研究完就下结论 | `HOLD — research incomplete` 是保护机制，补齐第 6 节缺口 |
| 把划线价当真价 | 永远用 `pricecheck.py` 对比自己的历史，划线价不作数 |
| 样本太少就下结论 | < 4 个采样点时价格带不可靠，脚本会明确警告 |
| 忽略经常性成本 | 订阅/耗材/保养是「租」的信号。占比 > 25% 触发告警 |
| 沉没成本混进来 | TCO 只算**这笔决策新产生的成本**，旧设备已经花掉的钱不算 |
| 中文环境直接抄美元参数 | `--tax` 传税率百分比（8.5 = 8.5%），不是 0.085 |
| 决策文件搞混 | 每次决策用独立 ID（`laptop-2026`），别复用 `default` |

## Verification Checklist

- [ ] 决策 ID、品类、评估周期、预算上限都已确定并记录
- [ ] 每个候选都填了 `--price`、`--tax`、`--accessories`、`--resale`
- [ ] 周期性成本（订阅/保险/耗材/保养/延保）已确认有没有、要几年
- [ ] 旧设备处理成本 `--disposal` 已估算
- [ ] 6 个规格维度都已打分，且分数反映**你的**优先级
- [ ] 权重按需调整过（默认 1.0 全等权 = 默认平均对待）
- [ ] `tco.py compare` 已运行，结论不是 `HOLD`
- [ ] 价格历史样本 ≥ 4 条，或已明确接受"样本不足"的警告
- [ ] 划线价与历史价已核对，折扣比例 < 50%
- [ ] `brief.py` 已生成并通读
- [ ] 简报第 6 节「调研缺口」为空，或已明确接受该风险
- [ ] 若结论是 `WAIT`，已设定目标价 + 复查日期
- [ ] 下单后用 `receipt-vault` 归档收据与保修卡

## Data Sources & Accuracy

**数据来源**

| 来源 | 用途 | 可靠性 |
|---|---|---|
| 厂商官网 / 零售商店价 | 标价、配件价格 | 高 —— 官方口径 |
| 厂商规格页 | 规格打分的事实基础 | 高 —— 但续航需打 7 折 |
| 用户自建价格历史（本地 JSON） | 价格带、百分位 | **取决于你记录的样本量** |
| 划线价（list price） | 折扣幅度 | **低 —— 可能从未真实成交** |
| 二手/回收报价 | 残值 | 中 —— 挂牌价通常高于成交价 |

**准确性边界（务必告诉用户）**

- **TCO 是估算，不是账单。** 输入的残值、耗材、保养都是你的估计值。脚本保证**算术正确**，不保证**输入正确**。
- **价格历史完全依赖你的记录。** 本 skill 不联网抓价，不会凭空产生历史。样本 < 4 时价格带无统计意义。
- **规格分是主观输入。** 脚本负责加权与归一化，**不负责判断某台机器好不好**。
- **税费默认按标价+配件计算**，不含退税、优惠券、返现、企业折扣 —— 有的话手动调 `--price`。
- **不含机会成本、融资成本、汇率波动。** 跨币种请自行换算后使用。
- **残值是最不可靠的输入。** 保守估低，别估高 —— 高估残值会系统性地偏向"现在买贵的"。

**隐私**

全部数据落在 `~/.hermes/data/purchase-advisor/`（`decisions/` 与 `prices/` 两个子目录），纯本地 JSON，**不上传任何价格、偏好或购物记录**。用 `tco.py clear -d <id>` 删除单个决策。

**脚本**

| 脚本 | 作用 | 依赖 |
|---|---|---|
| `scripts/tco.py` | TCO 计算 + 加权评分 + 结论 | Python 3 stdlib |
| `scripts/pricecheck.py` | 价格历史 + 百分位 + 假折扣检测 | Python 3 stdlib |
| `scripts/brief.py` | 渲染 7 节决策简报 | Python 3 stdlib |

三个脚本均已在本地端到端验证：跨脚本 TCO 数值一致（340.36 = 340.36、1,035.61 = 1,035.61），四种结论分支（BUY / WAIT / CLOSE / HOLD）均已触发测试，假折扣与样本不足告警均已验证。
