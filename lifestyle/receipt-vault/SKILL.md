---
name: receipt-vault
description: "Digitize every paper and email receipt, warranty card, serial number, and proof-of-purchase — searchable vault, warranty-expiry warnings, insurance-claim export, tax-deductible auto-tagging, and homeowner move-in / move-out handoff packet. Local-first JSON, photo/OCR pipeline, ships with category taxonomy."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, receipts, warranty, proof-of-purchase, insurance, home-inventory, returns, claims, ocd, household]
    related_skills: [home-maintenance-tracker, personal-expense-tracker, renewal-reminder, tax-prep-assistant, moving-relocator, inventory-builder]
---

# 🧾 Receipt Vault（票据/保修/凭证保险库）

> Stop digging through kitchen drawers after the laptop dies. Every receipt, warranty card, serial number, and proof-of-purchase in one searchable local vault — with warranty-expiry warnings, deductible-tax auto-tagging, and insurance-claim exports.

---

## Overview

Most households lose **20–40% of their receipts within 12 months** and over half of all warranty cards before the warranty expires. When something breaks (laptop, dishwasher, refrigerator, phone), the manufacturer asks for proof-of-purchase and serial number within 14 days — and you cannot find either. When you file an insurance claim (homeowners, renters, auto, travel), the adjuster wants an itemized loss list with values and receipts. When you do your taxes, the Schedule A deductions and small-business expenses live in a different pile again.

Receipt Vault turns Hermes into a **single chat-based vault** for all of it. You snap a photo or paste an email receipt, Hermes OCRs/transcribes it, then enriches with category, warranty length, deductible flag, and a `search-by-anything` index. Expiring warranties surface as cron-friendly alerts. Claim packets (homeowners, auto, travel) compile in one command.

| 能力 | 作用 | 典型场景 |
|---|---|---|
| 🖼️ 拍照入库 | 拍纸质小票/保修卡 → 自动 OCR → 归类 | 周末一次性扫抽屉里的票根 |
| 📧 转发入库 | `vault@…` 邮箱转发、或粘贴邮件正文 | 电商发票自动进库 |
| 🔎 全文搜索 | 关键词、品牌、型号、SN、商家、金额、时间 | "找 2024 年那台 MacBook 的发票" |
| 🛡️ 保修追踪 | purchase_date + warranty_months → 自动算到期 | 提前 30/60/90 天提醒 |
| 💰 税务标记 | 标记 deductible (Schedule A/C)、reimbursable、business_use | 报税季秒出报表 |
| 🏷️ 智能分类 | 18 个默认类别 + 自定义 tag | electronics / furniture / apparel / medical |
| 📦 位置标签 | 抽屉 / 卧室柜 / 车库 / 父母家 — 实物存放 | "现在小票在哪"问题终结 |
| 🆔 序列号库 | serial / model / IMEI 单独索引 | 报失、注册、保修都用得上 |
| 📈 估值快照 | current_value 字段 + 折旧规则 | 保险投保证明 |
| 🚨 索赔导出 | 一次性输出 homeowners / auto / travel 索赔包 | 暴风雨/失窃/行李延误 |
| 🏠 进/退房包 | 入住清单 + 退房取证包 | 房东/租客交接 |
| 🔁 退货倒计时 | 自购买起 N 天提醒可退窗口 | 错过退货期 |
| 💾 本地优先 | 数据存 `~/.hermes/vault/` + blob 文件夹 | 无云端、无泄漏 |
| ⏰ Cron 兼容 | 每日扫保修 / 退货 / deductible 截止 | 接入 daily-briefing |

**数据文件:**
- `~/.hermes/vault/items.json` — 元数据（每件商品一条）
- `~/.hermes/vault/warranties.json` — 保修规则表（按类别默认长度，可覆盖）
- `~/.hermes/vault/blob/` — 原始图片/PDF，文件名 `<item_id>.<ext>`

---

## When to Use

- *"Throw this in the vault"*（贴图或说 "I just bought …"）
- *"Log a receipt: Sony WH-1000XM5 from Best Buy, $399, 2-year warranty"*
- *"Add MacBook Pro 14" M3, purchased 2024-11-22 from Apple, $1999, 3-year AppleCare"*
- *"Where's the receipt for my Dyson?"*
- *"Show me everything that came from Costco last year"*
- *"What's expiring its warranty in the next 90 days?"*
- *"Compile my homeowners-insurance claim packet — burst pipe damaged: living-room TV, Persian rug, bookshelf"*
- *"What can I claim on Schedule A this year?"*
- *"I just moved — generate a move-in inventory with serial numbers"*
- *"Returning within 30 days — does the report show what's still in window?"*
- *"Add IMEI 359242… for my iPhone"*
- *"Help me find the model number for my dryer"*（sn-finder 工作流）
- *"租约到期，帮我生成 move-out 凭证包给房东"*
- *"帮我把这些报销票归类一下，年底要交"*
- *"Loss list for auto claim — total loss on my 2022 Civic"*
- *"Receipts older than 7 years that I can shred?"*

不用于：日常现金流记账（用 `personal-expense-tracker`）；云存储账单（用 `subscription-manager`）；信用卡刷卡流水（让银行导 CSV 后用 `csv-explorer`）。

---

## Core Workflow

### Step 1: 初始化 Vault

第一次使用：

```bash
mkdir -p ~/.hermes/vault/blob

[ -f ~/.hermes/vault/items.json ] || cat > ~/.hermes/vault/items.json <<'EOF'
{
  "version": 1,
  "created_at": "2026-09-26",
  "settings": {
    "default_currency": "USD",
    "warranty_alert_days": [90, 60, 30, 7],
    "return_window_days_default": 30,
    "shred_after_years": 7,
    "valuation_method": "depreciation_straight_line",
    "ocr_engine": "vision-api",
    "auto_tag_tax_deductible": true
  },
  "items": []
}
EOF

[ -f ~/.hermes/vault/warranties.json ] || cat > ~/.hermes/vault/warranties.json <<'EOF'
{
  "version": 1,
  "default_warranty_months_by_category": {
    "electronics_laptop":   12,
    "electronics_phone":    12,
    "electronics_camera":   12,
    "electronics_audio":    12,
    "electronics_kitchen":  12,
    "appliance_major":      24,
    "appliance_small":      12,
    "furniture":            12,
    "mattress":             120,
    "jewelry":              0,
    "apparel":              0,
    "tools_power":          36,
    "tools_hand":           0,
    "vehicle_part":         12,
    "medical_device":       24,
    "sporting_goods":       12,
    "software":             0,
    "service_contract":     0,
    "other":                0
  },
  "category_tax_deductible_defaults": {
    "medical_device":   "schedule_a_medical",
    "office_equipment": "schedule_c_business",
    "education":        "schedule_a_tuition",
    "charity":          "schedule_a_charity"
  }
}
EOF
```

向用户确认 4 件事（合理默认值下面标出）：

1. **币种**：`USD` / `CNY` / `EUR` / `GBP` / `JPY` / multi
2. **保修默认长度**：上表按类别的默认值，5 秒内可改
3. **存储路径**：`~/.hermes/vault/` 默认，可改到 iCloud / Dropbox 同步
4. **OCR 方式**：vision API / 本地 Tesseract / 仅手动

---

### Step 2: 入库一条 Item

用户说法：
- *"Snap this receipt"*（贴图）
- *"Email forwarded — here's the body: …"*
- *"Just bought Sony WH-1000XM5 from Best Buy, $399. Paid with Amex. Box says 1-year warranty."*
- *"把京东这个发票入账：iPhone 15，¥5999，AppleCare+ 2 年"*

Agent 解析生成：

```json
// ~/.hermes/vault/items.json
{
  "id": "rc-2026-09-26-001",
  "added_at": "2026-09-26T14:32:11Z",
  "purchase_date": "2026-09-25",
  "merchant": "Best Buy",
  "title": "Sony WH-1000XM5 Wireless Headphones",
  "category": "electronics_audio",
  "tags": ["noise-cancelling", "bluetooth", "personal"],
  "price": {
    "amount": 399.00,
    "currency": "USD",
    "tax": 32.50,
    "total": 431.50
  },
  "payment": { "method": "credit_card_amex", "last4": "1234" },
  "serial_number": null,
  "model_number": "WH-1000XM5/B",
  "warranty": {
    "expires_on": "2027-09-25",
    "length_months": 12,
    "provider": "Sony",
    "type": "manufacturer",
    "extended": false
  },
  "return_window_expires_on": "2026-10-25",
  "location": "living-room-desk",
  "current_value_usd": 399.00,
  "tax_deductible": null,
  "images": ["rc-2026-09-26-001.front.jpg", "rc-2026-09-26-001.back.jpg"],
  "raw_ocr_text": "BEST BUY  #1142  ...",
  "notes": ""
}
```

**分类规则**（agent 默认推断，用户可改）：

| 类别 | 关键词 |
|---|---|
| `electronics_laptop` | macbook, thinkpad, xps, laptop, notebook |
| `electronics_phone` | iphone, pixel, galaxy, smartphone |
| `electronics_audio` | headphones, earbuds, speaker, soundbar |
| `electronics_kitchen` | air fryer, espresso, instant pot |
| `appliance_major` | refrigerator, washer, dryer, dishwasher, oven |
| `appliance_small` | microwave, toaster, blender, vacuum |
| `furniture` | sofa, desk, chair, bookshelf, mattress |
| `tools_power` | drill, miter saw, pressure washer |
| `vehicle_part` | tires, battery (car), car seat, dashcam |
| `medical_device` | cpap, hearing aid, glasses, brace |
| `jewelry` | ring, watch, necklace |
| `apparel` | coat, shoes, jacket (单件 > $100 才建议入) |
| `software` | license, saas, microsoft, adobe |
| `service_contract` | warranty extension, support plan |
| `education` | course, textbook, certification |
| `charity` | donation, goodwill receipt |
| `office_equipment` | monitor, keyboard (work-from-home) |

入库后 agent 自动做的事：
- 📐 计算 `warranty.expires_on`、`return_window_expires_on`
- 🏷️ 根据 `warranties.json` 默认补 `warranty.length_months`
- 💡 如果商家/品牌有已知 warranty length（如 Apple 默认 1 年、Costco 大电器默认 2 年），覆盖默认
- 📁 图片保存到 `~/.hermes/vault/blob/<id>.<ext>`
- 🔔 设置 cron 提醒：到期前 90 / 60 / 30 / 7 天
- ✅ 回复确认（id + 摘要 + 到期日 + 退货窗口）

---

### Step 3: 检索 & 查询

| 用户问题 | Agent 做法 |
|---|---|
| "找 2024 年那台 MacBook 的发票" | 按 title/merchant/date 全文搜索；返回 item + blob 路径 |
| "Sony 买了什么？" | 按 merchant 聚合 + 总价 |
| "保修明年要过期的？" | 扫 `warranty.expires_on` 在 [today, today+90d] |
| "Costco 去年一共多少钱" | 按 merchant+date range 聚合 |
| "IMEI 359242…" | 单独索引 `serial_number` 字段 |
| "退货窗口还开的" | 扫 `return_window_expires_on` in [today, today+N] |

例：搜索 *"macbook"* 返回：

```text
🔍 1 match for "macbook"

  rc-2024-11-22-007  MacBook Pro 14" M3 Pro
  Purchased 2024-11-22 — Apple Fifth Ave — $1,999.00
  Warranty: 2027-11-22  (36mo, AppleCare+)
  Return window: closed
  Blob: rc-2024-11-22-007.front.jpg, rc-2024-11-22-007.back.jpg

  → 打开 / 复制 / 导出发票 PDF? (y/n)
```

---

### Step 4: 保修 / 退货告警（Cron 接入）

```bash
# ~/.hermes/cron/daily-briefing/cron.d/receipt-vault-alerts.sh
#!/usr/bin/env bash
# 每天 7:30 跑一次
~/.hermes/bin/hermes -s receipt-vault --cron "vault.alerts.daily"
```

输出示例（嵌入 daily-briefing）：

```text
🧾 Receipt Vault — 今天的提醒

  ⚠️ 保修即将到期（30 天内）:
    - Bose QC45 退货窗今天关 (purchased 2025-09-26)
    - LG Washer 保修 8 天后到期 (2026-10-04)

  💸 已过退货窗但还能"换货"（看商家政策）:
    - iPad mini @ Best Buy — 12 天前 (通常 14 天内有效)

  🗑️ 可碎纸（>7y 且无保修）:
    - 7 张 old receipts, sum $842
```

告警等级：
- **🔴 过期未处理** — 已过 return_window_expires_on 但还没标记为"留 / 退"
- **🟠 30 天内到期** — warranty 或 return
- **🟡 90 天内到期** — warranty
- **🟢 仅提醒** — pure deduction-window / shred-eligible

---

### Step 5: 保险/报税 索赔导出

#### 5a. 保险索赔包（homeowners / auto / travel）

用户：

> *"Compile my homeowners-insurance claim packet — burst pipe damaged: living-room TV, Persian rug, bookshelf"*

Agent 输出一个 markdown packet：

```text
# Insurance Claim Packet — Burst Pipe, 2026-09-12

## 损失清单
| Item | Original | Age | Current Value | Receipt | SN |
|------|---------:|----:|--------------:|---------|----|
| LG OLED C3 65" TV | $1,799 | 1y 4mo | $1,266 | ✅ rc-2025-05-22 | 305MX8H… |
| Persian rug (8x10) | $2,400 | 3y | $1,440 | ✅ rc-2023-04-11 | — |
| IKEA bookshelf | $329 | 4y | $98 | ✅ rc-2022-08-30 | — |
| **Total loss** | **$4,528** | | **$2,804** | | |

## 附文件
- 3 个原件图片 (front + back)
- 1 张购买凭证 PDF
- 折旧计算（直线法，剩余 5/10/15 年）

## 模板邮件给 adjuster
(下面给一段 100 字的英文/中文模板，可粘贴直接发)

## Checklist 提交时确认
- [ ] 已拍实物损失照片
- [ ] 已拍湿区照片
- [ ] 已联系 mitigation 团队
- [ ] 完整损失清单含 SN 列表
```

#### 5b. 报税导出（Schedule A & C）

> *"What can I claim this year on Schedule A?"*

```text
📋 报税清单 — Tax Year 2026

  🏥 Schedule A — Medical
    - CPAP supplies       $842
    - Glasses frames      $620
    - Orthodontist        $3,100
    Subtotal: $4,562

  🎓 Schedule A — Tuition
    - Coursera Plus       $399
    Subtotal: $399

  💼 Schedule C — Business
    - 50" monitor         $649 (office)
    - Mechanical keyboard $189
    Subtotal: $838

  ❤️ Schedule A — Charity
    - Goodwill (5 donations) $1,180
    Subtotal: $1,180

  Total Schedule A: $5,961  (need > 7.5% AGI threshold)
  Total Schedule C: $838    (business meals extra)
```

带 PDF / CSV 下载链接。

#### 5c. Move-in / Move-out inventory

> *"I just moved — generate move-in inventory with serial numbers."*

```text
# Move-in Inventory — 2026-09-26, Apt 5B

## Electronics (14 items)
| Item | SN | Model | Purchased |
|------|----|-------|-----------|
| MacBook Pro 14" | C02-… | M3 Pro | 2024-11-22 |
| Sony WH-1000XM5 | — | WH-1000XM5/B | 2026-09-25 |
...

## Appliances (6 items)
...

Total insured value: $18,442 (for renters insurance schedule)
```

退房版额外加：
- 各房间 4-方向拍照 checklist
- 与入住拍同角度对比
- 已损坏/磨损 record
- 押金扣减风险预判

---

## Example Invocations

### 例 1 — 拍照 + OCR 流水线

> **User:**（贴图：MacBook Pro 收据照片）
>
> *"Add this to the vault."*

**Agent:**

```text
[OCR] Reading image…
  Merchant:    Apple Fifth Avenue
  Date:        2024-11-22
  Items:       1 × MacBook Pro 14" M3 Pro  $1,999.00
  Tax:         $187.92
  Total:       $2,186.92
  Paid with:   Apple Card •••• 4321

→ Confirmed details?

  Title:   MacBook Pro 14" M3 Pro (Standard config)
  Category: electronics_laptop
  Serial #: ?
  Warranty: 12mo manufacturer → expires 2025-11-22
  Return:   until 2024-12-22 (closed)

User reply: "Serial C02ZK7H7MD6T, I have AppleCare+ until 2027-11-22"

[OK] rc-2024-11-22-007 saved
  - Front + back images stored to ~/.hermes/vault/blob/
  - AppleCare+ recorded: 36mo, expires 2027-11-22
  - Cron alert set: 90/60/30/7 days before expiry
  - Search index rebuilt (1 item, 1 SN)
```

### 例 2 — 商家聚合 + 报税

> **User:** *"All my Amazon orders from 2026, I want to see what was deductible."*

**Agent:**

```text
📦 Amazon 2026 — 87 orders, $9,142 total

  By category:
    electronics_kitchen   31 items  $2,840
    office_equipment      14 items  $3,920  (auto-tagged: schedule_c)
    apparel              22 items  $1,180
    ...

  Deductible (Schedule C, business use):
    - USB-C hub                  $89
    - 4K webcam                  $199
    - Standing desk converter    $249
    - ...
    Subtotal: $2,847

→ Export CSV / itemize for CPA? (y/n)
```

### 例 3 — 失窃报案 + 索赔包

> **User:** *"Someone broke into my car last night — make me the insurance claim packet."*

**Agent:**

```text
🚨 Auto Theft Claim — Honda Civic 2022

  Loss summary:
    - Vehicle (total loss): 2022 Civic EX, $22,400 (2022-09 purchase)
    - In-car at time of theft:
        • Beats Studio headphones      $349  (receipt ✅, SN: …)
        • Sunglasses (Ray-Ban)          $220  (receipt ✅)
        • Gym bag + contents           ~$180  (estimate)
    Total documented loss: $23,149

📎 Compiling packet
  - 3 receipts (front + back images)
  - Key/registration photos
  - Vehicle valuation (KBB + Edmunds avg)
  - Theft deterrent documentation
  - Police report template (CA DMV SR-1 due in 10 days)

→ Push to Drive + email PDF?
```

---

## Common Pitfalls

| 问题 | 解决方案 |
|---|---|
| OCR 误读金额/日期 | 永远要求用户复核关键数字（total / date）；不允许自动写入未确认金额 |
| 保修长度猜错 | 默认值仅当用户没给出；列出"已知默认"如 AppleCare+、Costco，让用户二次确认 |
| 同一商品两次入库 | 按 `merchant + title + serial_number` 三元组做去重；冲突时返回 diff 让用户选 |
| 价格币种混用 | `settings.default_currency` 是基准；任何外币按用户当天汇率换算并保留原值 |
| 图片过大（>10MB） | 压缩到 200dpi / 2MB；原图归档为 `*.orig.jpg`，OCR 用压缩版 |
| 没有 SN 的物品（衣服/食物） | 允许 `serial_number: null`，跳过 SN 索引；不强制要求 |
| 报税年度错乱 | `tax_year` 字段以"购买日期所在年度"为准；跨年度购买可手动 override |
| 厂商退货政策比商家短 | 返回 window 用商家最短的；建议额外记录 `manufacturer_return_window` |
| 私人 vs 公司混存 | 用 `tags: [business_use_pct]`（如 70/30）；可批量按 tag 过滤导报税 |
| 多人共享 vault | 用 `owners` 数组；操作日志记录"谁添加/改/删" |
| 失窃后 SN 被改 | 失窃报案时打印 SN + 设备照片 + IMEI 一并作为证据，不依赖数据库最新值 |
| 索赔导出小数点错位 | currency-aware 格式化；显示两位小数；总价额外加 `±5% confidence` 备注 |

---

## Verification Checklist

每次 claim/export 前自动跑：

- [ ] 每条出库 item 都有 `purchase_date` 和 `price.amount`
- [ ] 保修关键 item（≥$1000）的 `serial_number` 不为 `null`
- [ ] 同一索赔包内没有重复 item
- [ ] 总价 / 折旧计算与最新 settings 一致（汇率 / 折旧方法）
- [ ] 索赔叙事文本不出现 PII（电话 / 信用卡完整号）— 用 masked last4
- [ ] 已过期 items 不进"现行 inventory" — 它们进 `archive` 数组
- [ ] Export 时间戳 + 用户签名 (actor) + 数据快照已写入 ledger
- [ ] 用户复核过关键数字（OCR 自动标注 `confidence: <0.95` 时弹窗）

---

## Data Sources & Accuracy

**OCR 来源：**
- 默认：Hermes vision model (内置)
- 备选：Tesseract 5 (本地, 离线)
- 高级：Google Vision / AWS Textract (用户付费, 高精度)

**保修默认长度来源：**
- `warranties.json` 内置表（基于公开 50+ 品牌调研）
- 用户首次配置 30 天后要求确认是否更新
- 任何"超长保修"（>5y）必须用户明确输入

**折旧方法：**
- 默认直线法（straight-line over category lifespan）
- 用户可改 `declining_balance`、`useful_life_override`
- 类别寿命：laptop 5y / phone 3y / appliance_major 10y / furniture 10y / mattress 8y

**报税数据：**
- ❌ 不连接银行/信用卡机构（隐私优先）
- ✅ 用户粘贴 CSV / 截图 → CSV-explorer 风格的列检测
- Schedule A 阈值计算用 IRS 公布数字，标记 "Based on IRS Pub 502 / 526 / 530"
- 所有 deductible flag 都标 **[uncertified]** — 最终由 CPA/IRS 决定

**估值数据：**
- ❌ 不抓取 eBay sold / KBB（避免被反爬阻断）
- ✅ 默认直线折旧；用户可手动 override `current_value_usd` 字段
- 投保金额提示 + 注释"按 replacement cost vs actual cash value 区别"

**保真度边界：**
- 本 skill 不做法律或税务建议。Claim packets 是"组织员"不是"顾问"。
- 所有 deductible / warranty claim 数字以原始文档为准，本地存档为参考。
- 报警失误（漏报告警）不为错过保修窗口负责 — 用户应主动查询。
