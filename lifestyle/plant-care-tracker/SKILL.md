---
name: plant-care-tracker
description: "Log houseplant care from chat — watering, fertilizing, repotting, pruning, propagation, light & humidity for every plant in your home. Multi-plant registry, species-specific cadences, overdue alerts, growth journal, pest/disease log, and propagate-to-gift tracking. All data local JSON, privacy-first."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, houseplants, gardening, watering-schedule, fertilizing, plant-care, propagation, indoor-garden, urban-jungle, plant-tracker, multi-plant]
    related_skills: [pet-care-tracker, home-maintenance-tracker, personal-expense-tracker, habit-tracker, personal-crm]
---

# 🌿 Plant Care Tracker — 室内植物养护追踪

> Stop killing your monstera with love. Track every watering, fertilizing, repotting, pruning, and propagation for every plant in your home — and walk into the next nursery trip knowing exactly which pot needs to move to a bigger one. 用对话记录每盆植物的浇水、施肥、换盆、修剪和扦插，从此告别"我又忘了浇"或"我是不是浇多了"。

---

## Overview

Most houseplant owners have one of two failure modes: **chronic overwatering** (the most common killer) and **silent neglect** (the "I forgot it existed for a month" pothos). Both come from the same root cause — no schedule, no memory, no feedback loop. This skill turns Hermes into a household plant logbook: you tell it what you did (*"watered the monstera, top inch dry"*) or what you noticed (*"the fiddle leaf dropped a new leaf but the edges are brown"*), and Hermes logs it, schedules the next watering, tracks growth and pest pressure, flags overdue plants, and exports a care profile you can hand to a plant-sitter when you travel.

| Capability | Description |
|------------|-------------|
| 🪴 Multi-plant registry | Each plant with species, cultivar, nickname, location, pot size, soil, light |
| 💧 Watering log + cadence | Per-species defaults (succulent 14d, monstera 7d, fern 3d) with manual override |
| 🪣 Soil moisture tracking | Tag each watering "dry to first knuckle / bone dry / still moist" — learns your plant |
| ☀️ Light & placement | Light type (direct/indirect/low) + window direction + hours of sun |
| 💦 Humidity & temperature | Per-room readings, ideal range per species, misting log |
| 🌱 Fertilizing schedule | Spring/summer cadence, NPK ratio, flush log to prevent salt buildup |
| ✂️ Pruning & shaping | Date, what cut, propagation candidate Y/N |
| 🧬 Propagation tracker | Cuttings in water/perlite/soil — root progress, ready-to-pot date |
| 🪴 Repotting log | Pot size, soil mix, root-bound notes, next-pot-up estimate |
| 🐛 Pest & disease log | Mealybugs, spider mites, fungus gnats, root rot — treatment & outcome |
| 📷 Growth journal | Free-form notes + height/leaf-count snapshots over time |
| 📅 Seasonal playbook | Spring growth push, summer heat, fall dormancy, winter low-light |
| 💰 Annual plant spend | Pots, soil, fertilizer, plants, tools, replacement rate |
| 🎁 Gift pipeline | "I've propagated 4 pothos — who in my CRM would love one?" |
| 🏖️ Plant-sitter export | Markdown care card per plant for travel handoff |
| 🔔 Overdue alerts | Anything past due shows in red. Cron-friendly weekly digest. |
| 💾 Local storage | All data in `~/.hermes/plants/` — no cloud, no leak |

---

## When to Use

- *"Add my monstera — Monstera deliciosa, ~2 years old, in a 6" pot, lives by the south window"*
- *"Watered the monstera, top inch was bone dry, also gave it a quarter-turn"*
- *"Fertilized the fiddle leaf fig with Dyna-Gro Foliage Pro 1 tsp/gal"*
- *"The pothos has 3 yellow leaves at the bottom — could be overwatering?"*
- *"Repot my calathea into a 7" pot with fresh aroid mix"*
- *"Log a cutting from the philodendron — 4 nodes, in water on the windowsill"*
- *"Found mealybugs on the hoya, treated with 70% isopropyl"*
- *"Which plants are overdue for watering this week?"*
- *"Set up a watering cadence for a new snake plant"*
- *"What's the humidity in my bathroom vs. my living room?"*
- *"I'm traveling for 10 days — generate a care card for my plant-sitter"*
- *"Show me the growth of my monstera over the last 6 months"*
- *"How much did I spend on plants last year?"*
- *"I just propagated 4 pothos cuttings — who in my network would want one?"*
- *"Spring is here — what should I fertilize and repot right now?"*
- *"The new leaf on my alocasia came in black and crispy — log it"*
- *"我家的龟背竹叶子边缘发黄，帮我记下来"*
- *"给我列一下这周所有要浇水的植物"*
- *"春节出门10天，帮我生成一份给朋友的养护说明"*
- *"我刚水插了一支绿萝，4个节点"*

不适用于：户外菜园/大田作物（用农业类工具）、大型景观树、纯水生/水族植物、需要专业园艺师诊断的真菌病害。

---

## Core Workflow

### Step 1：建立家庭植物册 (Plant Household Init)

首次使用时，建立本地数据目录并询问基础信息：

```bash
mkdir -p ~/.hermes/plants
```

询问用户（缺省可跳过，agent 应能使用 sensible defaults）：

1. **有多少盆植物？** 逐盆收集：
   - 昵称（如 "客厅龟背竹" / "Mona the monstera"）
   - 学名（Monstera deliciosa / Sansevieria trifasciata / 等） — agent 应能根据模糊描述自动补全
   - 品种（'Thai Constellation' / 'Cebu Blue' / '普通绿萝'）
   - 大致年龄或购入日期
   - 当前花盆尺寸（英寸/厘米）
   - 摆放位置（"南窗 1m 处" / "浴室淋浴旁" / "办公桌角落"）
   - 光照类型（直射 / 散射 / 低光 / 补光灯）
   - 当前高度 / 叶片数（可选 baseline）
   - 入手价格（可选，用于年度花费统计）

**自动常识库**：内置 ~80 种常见室内植物的默认养护参数（浇水频率区间、湿度需求、光照需求、施肥季节、毒性）。agent 用学名匹配，新物种可现场加。

**数据文件结构**：

```text
~/.hermes/plants/
├── household.json           # household meta + plant index
├── plants/
│   ├── monstera-01.json     # per-plant: profile, events[], notes[]
│   ├── snake-plant-01.json
│   └── ...
├── events-archive.jsonl     # append-only log of all care events
└── propagation-log.json     # cuttings + ready-to-gift pipeline
```

**`household.json` 示例**：

```json
{
  "version": 1,
  "household_name": "Living Room Jungle",
  "created": "2026-08-10",
  "plant_count": 12,
  "owner": "yimgao",
  "location": "Brooklyn, NY",
  "plants": [
    {
      "id": "monstera-01",
      "nickname": "Mona",
      "species": "Monstera deliciosa",
      "cultivar": "standard",
      "acquired": "2024-03-15",
      "pot_size_inches": 8,
      "location": "south window, 1m away",
      "light": "bright_indirect"
    }
  ]
}
```

### Step 2：日常养护记录 (Daily Care Logging)

用户的输入形式非常自由，agent 负责解析。常见输入模式：

| 用户说 | 解析为 |
|--------|--------|
| *"Watered the monstera"* | `event=water, plant=monstera-01, date=now` |
| *"Fertilized the fiddle leaf with 1/2 tsp Dyna-Gro 9-3-6"* | `event=fertilize, plant=fiddle-leaf-01, fertilizer=Dyna-Gro Foliage Pro, dose=0.5tsp, npk=9-3-6` |
| *"Repotted the calathea into a 7 inch pot"* | `event=repot, plant=calathea-01, new_pot_inches=7` |
| *"Took a cutting from the pothos, 3 nodes, into water"* | `event=propagate, parent=pothos-01, nodes=3, medium=water` |
| *"Found spider mites on the hoya, sprayed with neem"* | `event=pest, plant=hoya-01, pest=spider_mites, treatment=neem_oil` |
| *"New leaf unfurled on the philodendron!"* | `event=growth, plant=philodendron-01, type=new_leaf` |
| *"Monstera dropped a yellow leaf at the bottom"* | `event=leaf_event, plant=monstera-01, type=yellow_drop, position=lower` |

**写入逻辑**：

```bash
# 1. Append to event log (JSONL, immutable)
echo '{"ts":"2026-08-10T09:15:00Z","event":"water","plant_id":"monstera-01","soil_state":"dry_to_first_knuckle","volume_ml":250}' \
  >> ~/.hermes/plants/events-archive.jsonl

# 2. Update per-plant last-N-event cache
python3 - <<'PY'
import json, datetime, pathlib
p = pathlib.Path.home() / ".hermes/plants/plants/monstera-01.json"
data = json.loads(p.read_text())
data.setdefault("events", []).append({
    "ts": "2026-08-10T09:15:00Z",
    "event": "water",
    "soil_state": "dry_to_first_knuckle",
    "volume_ml": 250
})
data["last_watered"] = "2026-08-10T09:15:00Z"
data["next_water_due"] = "2026-08-17"  # species default + learned adjustment
p.write_text(json.dumps(data, indent=2, ensure_ascii=False))
PY
```

**Next-due 智能调度**：

每次浇水事件，agent 根据 4 个信号计算下次浇水日：

1. **物种默认区间**（succulent 14d / monstera 7d / fern 3d / calathea 4d / snake plant 21d …）
2. **历史平均**：过去 6 次实际浇水间隔的中位数
3. **季节调整**：冬季 ×1.5 / 夏季 ×0.7（冬季蒸发慢、夏季蒸发快）
4. **上次土壤状态**：本次记录"还湿润" → 推迟 1.5×；"彻底干透" → 保持；"干到第一节" → 保持

公式（agent 心算）：

```
next_due = last_event + max(species_default, learned_median × seasonal_factor × soil_state_factor)
```

### Step 3：查询、提醒与导出 (Query, Alerts, Export)

**逾期植物查询**：

```bash
python3 - <<'PY'
import json, datetime, pathlib
root = pathlib.Path.home() / ".hermes/plants/plants"
today = datetime.date.today()
overdue, due_soon, healthy = [], [], []
for p in root.glob("*.json"):
    d = json.loads(p.read_text())
    due = datetime.date.fromisoformat(d.get("next_water_due", "2099-01-01"))
    delta = (due - today).days
    rec = {"id": d["id"], "nickname": d["nickname"], "species": d["species"], "due": str(due), "delta_days": delta}
    (overdue if delta < 0 else due_soon if delta <= 3 else healthy).append(rec)

print("🔴 OVERDUE:")
for r in sorted(overdue, key=lambda x: x["delta_days"]):
    print(f"  - {r['nickname']} ({r['species']}) — {abs(r['delta_days'])}d overdue")
print("\n🟡 DUE WITHIN 3 DAYS:")
for r in sorted(due_soon, key=lambda x: x["delta_days"]):
    print(f"  - {r['nickname']} ({r['species']}) — in {r['delta_days']}d")
print(f"\n🟢 Healthy: {len(healthy)} plants")
PY
```

**养护卡导出**（给 plant-sitter）：

```bash
python3 - <<'PY'
import json, pathlib
root = pathlib.Path.home() / ".hermes/plants/plants"
print("# 🌿 Plant Care Handoff — for Plant Sitter\n")
print("**Caretaker:** yimgao  ")
print("**Out:** 2026-08-15 → 2026-08-25  ")
print("**Emergency contact:** yimgao (WeChat: yg-dev)\n")
for p in sorted(root.glob("*.json")):
    d = json.loads(p.read_text())
    print(f"## {d['nickname']} — *{d['species']}*")
    print(f"- Location: {d['location']} | Light: {d['light']}")
    print(f"- Water: every {d.get('watering_interval_days', '?')}d, top inch should be dry")
    print(f"- Last watered: {d.get('last_watered', 'unknown')[:10]}")
    print(f"- Notes: {d.get('notes', '—')[:200]}\n")
PY
```

**传播/扦插到送礼管道**：

```bash
python3 - <<'PY'
import json, pathlib
log = json.loads((pathlib.Path.home() / ".hermes/plants/propagation-log.json").read_text())
ready = [c for c in log["cuttings"] if c.get("ready_to_pot") and not c.get("gifted_to")]
print(f"🌱 {len(ready)} cuttings ready to pot / gift:")
for c in ready:
    print(f"  - {c['parent_species']} cutting, {c['nodes']} nodes, roots {c.get('root_length_cm', '?')}cm")
    print(f"    propagated {c['propagated_date']} from {c['parent_plant_id']}")
PY
# 然后 agent 主动提示：要用 personal-crm 找收礼人吗？
```

**年度花费统计**：

```bash
python3 - <<'PY'
import json, pathlib, re
events = [json.loads(l) for l in (pathlib.Path.home() / ".hermes/plants/events-archive.jsonl").read_text().splitlines() if l]
# events 中 purchase / tool / pot 事件带 cost_usd 字段
# 简单聚合
from collections import defaultdict
spend = defaultdict(float)
for e in events:
    if e.get("event") == "purchase" and e.get("cost_usd"):
        spend[e.get("category", "other")] += e["cost_usd"]
total = sum(spend.values())
print(f"💰 2026 YTD plant spend: ${total:.2f}")
for cat, amt in sorted(spend.items(), key=lambda x: -x[1]):
    print(f"  - {cat}: ${amt:.2f}")
PY
```

---

## 物种默认参数参考 (Species Defaults Reference)

> 内置 ~80 种常见室内植物的合理区间。agent 引用此表，叠加用户历史和季节因子做实际调度。

| 物种 (Species) | 浇水间隔 (d) | 光照 | 湿度 | 施肥季节 | 难度 |
|---|---|---|---|---|---|
| Monstera deliciosa | 7–10 | bright indirect | 50–60% | spring–summer | easy |
| Ficus lyrata (Fiddle Leaf Fig) | 7–10 | bright indirect | 40–50% | spring–summer | hard |
| Sansevieria / Dracaena trifasciata | 14–21 | low to bright | 30–50% | sparse | very easy |
| Pothos (Epipremnum aureum) | 7–10 | low to bright | 40–60% | spring–summer | very easy |
| Philodendron (most) | 7–10 | bright indirect | 50–60% | spring–summer | easy |
| Calathea / Goeppertia | 3–5 | medium indirect | 60–80% | spring–summer | hard |
| ZZ plant (Zamioculcas) | 14–21 | low to bright | 30–50% | sparse | very easy |
| Alocasia | 5–7 | bright indirect | 60–80% | spring–summer | hard |
| Ficus elastica (Rubber plant) | 7–10 | bright indirect | 40–50% | spring–summer | easy |
| Hoya carnosa | 10–14 | bright indirect | 40–60% | spring–summer | easy |
| Spider plant (Chlorophytum) | 5–7 | medium indirect | 40–60% | spring–summer | very easy |
| Pilea peperomioides | 7–10 | bright indirect | 50% | spring–summer | easy |
| Bird of Paradise (Strelitzia nicolai) | 7–10 | bright direct | 50–60% | spring–summer | medium |
| Anthurium | 5–7 | bright indirect | 70–80% | year-round mild | medium |
| Begonia (Rex/cane) | 5–7 | medium indirect | 50–60% | spring–summer | medium |
| String of Pearls (Curio rowleyanus) | 10–14 | bright indirect | 40–50% | sparse | medium |
| Echeveria / Sempervivum | 14–21 | direct sun | 30–40% | spring only | easy |
| Haworthia / Gasteria | 14–21 | bright indirect | 30–40% | spring only | very easy |
| Christmas cactus (Schlumbergera) | 10–14 | bright indirect | 50% | fall bloom | easy |
| Air plants (Tillandsia) | soak weekly | bright indirect | 50–70% | monthly mist + soak | medium |
| Boston fern (Nephrolepis) | 2–4 | medium indirect | 70–90% | spring–summer | medium |
| African violet (Saintpaulia) | 5–7 (bottom) | bright indirect | 50–60% | year-round mild | medium |
| Orchids (Phalaenopsis) | 7–10 | bright indirect | 50–70% | weekly weak | medium |
| Bonsai (Ficus retusa / Juniper) | 2–5 | bright direct | 50% | spring–autumn | hard |

完整 80+ 物种表存在 `~/.hermes/plants/species-defaults.json`（agent 首次运行自动展开）。

---

## Common Pitfalls / 常见坑

| 坑 | 为什么出问题 | 解决方案 |
|---|---|---|
| 按固定日历浇水（每周一） | 季节/湿度/光照变化时土壤干得不一样 | 改成"按植物需要"——agent 建议周期，但用户每次记录土壤状态（干到哪） |
| 一次性给所有植物统一浇水 | 龟背竹和仙人掌需水量差 5 倍 | 每株独立 `next_water_due` 字段，永不批量 |
| 永远只记录"浇了"，不记"土的状态" | 失去学习信号，agent 无法校准间隔 | 强制记录 `soil_state: dry_to_first_knuckle / bone_dry / still_moist` |
| 把施肥和浇水同一天 | 干肥烧根；湿肥流失 | 区分事件：`fertilize` 独立于 `water`；施肥后 24h 内不浇清水会标注 |
| 冬天照夏季频率施肥 | 休眠期施肥烧根 | species-defaults 表里 `fertilize_season` 字段；冬季自动降低到 1/2 浓度或停 |
| 室内无湿度计硬拍"湿度 50%" | 各房间差异巨大，尤其北方暖气房 | 提示用户买 $10 湿度计；按 `room: humidity_pct` 字段记录 |
| 换盆后立刻正常浇水施肥 | 修根后根系弱，烧苗风险高 | 换盆事件触发"恢复期"标签：2 周内只清水、无肥 |
| 出门前一次性把所有植物浇透 | 积水烂根 | plant-sitter handoff 默认写"按各自周期，**不要提前浇**" |
| 笼统说"我的植物" | 12 盆植物无法确定是哪盆 | 强制要求 nickname 或 location 消歧；agent 第一次反问确认 |
| 忽略 drainage hole 状态 | 积水是头号杀手 | 记录每盆 pot 是否有 drainage；无 drainage 的植物自动降低 watering 频率并标记 |
| 复用 soil 但不标年份 | 旧土盐分累积、透气性下降 | repot 事件必须更新 `soil_age_months`；>18 月提示换土 |
| 把户外花园逻辑搬到室内 | 室内没风、没虫、湿度稳、雨淋不到 | 提示用户：室内浇水频率通常比户外低 30–50% |

---

## Example Invocations / 完整对话示例

### 示例 1：从零开始建立 6 盆植物的 household

> **User:** 我家刚买了 6 盆植物，帮我建一个养护追踪系统
>
> **Agent:** 好，先建数据目录。`mkdir -p ~/.hermes/plants` 已完成。
>
> 告诉我这 6 盆的：昵称、品种、摆放位置，我会自动匹配物种默认参数。
>
> 模板：
> ```
> 1. 昵称 + 品种 + 位置
> ```
>
> **User:**
> 1. 客厅龟背竹，普通品种，南窗
> 2. 卧室虎皮兰，Sansevieria trifasciata，角落
> 3. 浴室波士顿蕨，靠淋浴
> 4. 办公桌绿萝，金边品种，桌角
> 5. 厨房金钱树 ZZ，吊柜旁
> 6. 北窗琴叶榕，刚买的
>
> **Agent:** 收到。基于你给的描述，这是 6 盆的 profile：
>
> | 昵称 | 学名 | 位置 | 光照 | 浇水默认 |
> |---|---|---|---|---|
> | 客厅龟背竹 | Monstera deliciosa | 南窗 | 散射光 | 7–10d |
> | 卧室虎皮兰 | Sansevieria trifasciata | 角落 | 低光 | 14–21d |
> | 浴室波士顿蕨 | Nephrolepis exaltata | 靠淋浴 | 散射光 | 2–4d |
> | 办公桌金边绿萝 | Epipremnum aureum 'Golden' | 桌角 | 中等光 | 7–10d |
> | 厨房金钱树 | Zamioculcas zamiifolia | 吊柜旁 | 低光 | 14–21d |
> | 北窗琴叶榕 | Ficus lyrata | 北窗 | 散射光 | 7–10d |
>
> 已写入 `~/.hermes/plants/household.json`。下次浇水直接说"我浇了客厅龟背竹"就行。
>
> 提醒：北窗**对 Ficus lyrata 偏暗**，建议补光或 90 天观察落叶情况。

### 示例 2：日常浇水 + 自动学习 + 周报

> **User:** 浇了客厅龟背竹，土干到第一节
>
> **Agent:** 已记录：
> - 客厅龟背竹 (monstera-01): water event @ 2026-08-10, soil_state=dry_to_first_knuckle
> - 下次浇水预计: 2026-08-17（默认 7d）
> - 历史平均间隔: 8.2d（基于 5 次记录）→ 实际调度按 8d 计算
> - 下次实际预计: 2026-08-18
>
> **User:** 这周所有植物的状态？
>
> **Agent:**
> ```
> 🔴 OVERDUE:
>   - 卧室虎皮兰 (Sansevieria) — 4d overdue
>   - 厨房金钱树 (Zamioculcas) — 1d overdue
>
> 🟡 DUE WITHIN 3 DAYS:
>   - 办公桌金边绿萝 — in 1d
>   - 客厅龟背竹 — in 2d
>
> 🟢 Healthy: 2 plants (波士顿蕨、北窗琴叶榕)
> ```
>
> 建议：周末一起给 4 盆浇。虎皮兰记得"宁干勿湿"——检查土深 5cm 是否真的干。

### 示例 3：旅行 10 天，生成 plant-sitter handoff

> **User:** 我下周五出门 10 天，帮我生成一份给朋友的养护卡
>
> **Agent:** 已生成 `~/.hermes/plants/handoff-2026-08-15.md`，这是内容：
>
> ```markdown
> # 🌿 Plant Care Handoff
>
> **Caretaker:** yimgao
> **Out:** 2026-08-15 → 2026-08-25 (10 days)
> **Sitter:** [name]  **Emergency:** WeChat yg-dev
>
> ---
>
> ## 客厅龟背竹 — Monstera deliciosa
> - Location: 南窗 1m away, bright indirect
> - Water: every 7–10d, **only when top 1 inch is dry**
> - Schedule: water 8/17, then 8/24
> - Last watered: 8/10
> - ⚠️ **Don't overwater** — yellow leaves = STOP
> - Rotate 1/4 turn each watering for even growth
>
> ## 卧室虎皮兰 — Sansevieria trifasciata
> - Location: 角落 low light
> - Water: every 14–21d
> - Schedule: water 8/22 only (1x in 10 days)
> - ⚠️ **If unsure, don't water** — overwatering kills it
>
> ## 浴室波士顿蕨 — Nephrolepis exaltata
> - Location: 靠淋浴, high humidity
> - Water: every 2–4d, keep soil **consistently moist**
> - Schedule: water 8/15, 8/18, 8/21, 8/24 (4x)
> - Mist daily if bathroom isn't steamy
> - ⚠️ Browning fronds = needs more humidity
>
> ## 办公桌金边绿萝 — Epipremnum aureum
> - Location: 桌角
> - Water: every 7–10d
> - Schedule: water 8/22 (1x)
> - Very forgiving — better to under than over
>
> ## 厨房金钱树 — Zamioculcas zamiifolia
> - Location: 吊柜旁
> - Water: every 14–21d
> - Schedule: skip this trip — 1 watering total
>
> ## 北窗琴叶榕 — Ficus lyrata
> - Location: 北窗
> - Water: every 7–10d
> - Schedule: water 8/15, 8/22 (2x)
> - ⚠️ **Doesn't like to move** — keep it in same spot
> - ⚠️ Hates drafty AC
>
> ---
>
> **Summary:** 6 plants, ~10 waterings across 10 days.
> Each visit ≈ 5 minutes. Total sitter time: ~50 min over 10 days.
> ```
>
> 打印出来贴在冰箱上，或 WeChat 发给朋友。要我同时给朋友做个 1 分钟语音提示脚本吗？

### 示例 4：病虫害诊断与处理追踪

> **User:** 浴室波士顿蕨叶子上有小白虫，背面尤其多，会动
>
> **Agent:** 听起来是 **spider mites（红蜘蛛）** 或 **mealybugs（粉蚧）**。几个快速鉴别问题：
>
> 1. 小虫是**白色棉絮状**（粉蚧）还是**红色/褐色细小+有网**（红蜘蛛）？
> 2. 叶子有没有**细密的蜘蛛网**在叶腋？
> 3. 叶子有没有**黄斑+褪绿**？
>
> **User:** 1 是白棉絮，2 没有网，3 有黄斑
>
> **Agent:** 确诊：**粉蚧 (mealybugs)**。原因大概率是浴室湿度高 + 通风差 + 新买的植物带入。
>
> 建议处理：
> 1. **隔离**这盆蕨到阳台/独立房间，避免传染其他 5 盆
> 2. **70% 异丙醇**棉签点杀每个可见粉蚧
> 3. **整株冲洗**淋浴喷头，强力冲掉虫卵
> 4. **neem oil** 1% 喷洒全株（包括叶背），7 天一次，连续 3 次
> 5. 期间**降低浇水**让土壤干一点（虫在湿土繁殖快）
>
> 帮你记一下处理事件吗？
>
> **User:** 记，按你说的做了
>
> **Agent:** 已记录 4 个事件：
> - `pest`: 浴室波士顿蕨, mealybugs, 2026-08-10
> - `treatment`: isopropyl 70% spot treatment
> - `treatment`: shower rinse
> - `treatment`: neem oil 1% spray, next due 2026-08-17
>
> 7 天后我会提醒你复查并第二次喷 neem。**21 天后**我会让你做一次最终复盘——如果还有虫，可能需要 systemic insecticide（内吸式杀虫剂）或整株销毁以保护其他植物。

---

## Verification Checklist / 验证清单

部署前自检：

- [ ] `~/.hermes/plants/household.json` 已建立，含至少 1 盆植物 profile
- [ ] 物种识别：用户说"我的龟背竹"时，agent 能匹配到 `Monstera deliciosa` 并应用默认参数
- [ ] 浇水事件能写入 `events-archive.jsonl` 和 per-plant JSON 两条路径
- [ ] `next_water_due` 字段能基于物种默认 + 历史平均 + 季节 + 土壤状态 4 个因子计算
- [ ] 逾期查询能在 1 次 `python3` 调用内完成（< 50 株植物 < 100ms）
- [ ] 物种默认表至少 30 种常见室内植物；agent 能解释"为什么这盆要等 14d"
- [ ] 病虫害诊断至少能区分 5 种常见问题（粉蚧、红蜘蛛、fungus gnats、根腐、晒伤）
- [ ] 旅行 handoff 导出为可读 Markdown，含每盆具体日期
- [ ] 扦插日志独立于母株事件流，能追踪 root length 和 ready-to-pot
- [ ] 礼物提示能联动 `personal-crm` skill 的联系人列表
- [ ] 季节感知：12 月-2 月自动降低施肥频率 / 拉长浇水间隔
- [ ] 数据完全本地，不调用任何 cloud API（除可选的 species-lookup 百科）
- [ ] 数据 export 完整：1 次命令生成整个 household 的 .json 备份

---

## Data Sources & Accuracy / 数据来源与准确性

| 数据类型 | 来源 | 准确性 | 更新频率 |
|---|---|---|---|
| 物种默认养护参数 | 内置 curated JSON，基于 Missouri Botanical Garden / Royal Horticultural Society / Houseplant Hobbyist 综合 | 高 | 季度审阅，按用户反馈校正 |
| 浇水频率自适应 | 用户实际记录 + Python median 计算 | 随记录数提升（≥6 次后高置信） | 实时 |
| 病虫害诊断 | 内置诊断树 + 图像识别（可选 `vision_analyze`） | 中等——文本描述置信高，图像描述需用户确认 | 静态 |
| 季节因子 | 系统日期（北半球默认）+ 用户位置（可选 `~/.hermes/config.yaml`） | 高 | 实时 |
| 物种 ID 兜底 | 用户输入学名 / agent 用学名库匹配；未识别物种降级为 generic 类别 | 高（80+ 物种） | 静态 |
| 花费数据 | 用户手动输入 / OCR 收据（可选） | 高（手动） | 用户驱动 |
| 位置 / 湿度 | 用户手动记录 | 中——基于用户纪律 | 用户驱动 |

**准确性局限**：
- **微气候差异**：同一城市的两个公寓湿度可能差 30%。skill 假设用户手动记录关键环境数据。
- **品种差异**：同一物种不同 cultivar 需求不同（如 Philodendron 'Pink Princess' 比普通绿萝更需光）。agent 在 description 字段匹配 cultivar 关键词。
- **病虫害图像识别**：当前用文字描述匹配，置信度约 70%。生产级建议集成 Plantix / PlantNet API 作交叉验证。
- **新物种**：内置 30–80 种常见种；非常规种（特殊杂交、稀有 aroid）需要用户初次配置时手填参数。

**隐私**：所有数据本地 `~/.hermes/plants/`，agent 不上传植物清单、位置或养护历史。物种名如敏感（如高价 aroid 防盗窃），用户可关闭花名或位置字段的"导出"功能。

---

## 升级路径

- **v1.1**：图像识别病虫害（PlantNet / Plantix API 集成）
- **v1.2**：自动生成 QR code 贴花盆（每盆 1 个 QR → 扫码看 profile）
- **v2.0**：智能家居集成——读土壤湿度传感器（Xiaomi Mi Flora / Arduino）自动建议浇水
