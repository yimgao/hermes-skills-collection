---
name: weekly-meal-planner
description: "Plan a 7-day meal calendar from chat — dietary prefs, allergies, household size, weekday-time budget, pantry-first, variety rules, leftover linkage, consolidated shopping list with quantity math. Pairs with pantry-manager and recipe-generator. Local-only Markdown output."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, meal-planning, weekly-meals, grocery, shopping-list, cooking, food-waste, dietary, calendar, batch-cooking, local-first]
    related_skills: [recipe-generator, pantry-manager, personal-expense-tracker, fitness-planner, calendar-optimizer]
---

# Weekly Meal Planner / 一周菜谱规划师

> One conversation → a full 7-day meal calendar that respects your diet, time, budget, and pantry — with a deduplicated shopping list that already does the unit math so you don't buy two heads of garlic.

## Overview

Weekly Meal Planner turns a few chat messages into a **complete weekly meal calendar** — breakfast, lunch, dinner, and optional snacks — that is **pantry-first, diet-aware, time-budgeted, and variety-balanced**. It does *not* just generate recipes (use `recipe-generator` for that). It orchestrates them across a week: rotating proteins, reusing leftovers, batching weekend prep for weekday speed, and producing a shopping list whose quantities are already consolidated (3 recipes asking for "1 onion" becomes "3 onions").

| Capability | What It Does | Typical Use |
|---|---|---|
| **Profile Capture** | Household size, diet (omnivore/veg/vegan/keto/halal/kosher), allergies, dislikes, weekday time budget, weekend time budget, budget per week | First-time setup |
| **Pantry Pull** | Reads `~/.hermes/data/pantry-manager/pantry.json` if present — prioritizes items expiring within 7 days | "Plan my week, use up the chicken" |
| **Calendar Constraints** | Pulls `~/.hermes/data/calendar-optimizer/calendar.ics` — flags days with no lunch break or evening meetings | "I have dinner with friends Thursday" |
| **Recipe Bank** | Local JSON of known recipes with metadata (tags, time, difficulty, cuisine, protein, vegetarian, freezer-friendly) | Reuse instead of reinvent |
| **Variety Engine** | No protein repeats within 3 days; rotates cuisine (Asian/Mediterranean/American/Mexican/Indian); rotates cooking method | Prevents "chicken again?" fatigue |
| **Time Budget Mapping** | Weekday ≤ 30 min dinners → sheet-pan / stir-fry / one-pot; weekend slots can host braises, roasts, batch cooks | "30-min weeknights" |
| **Batch-Cook Linkage** | Sunday roast → Monday/Monday leftovers → Wednesday stir-fry with shredded leftovers | Cuts weekday work in half |
| **Leftover Tracker** | Tags recipes with `yields_leftovers_for: N`; pairs producer + consumer slots automatically | Reduces food waste |
| **Consolidated Shopping List** | Sums quantities across recipes (3×1 onion = 3 onions, 2×200g chicken = 400g chicken); groups by aisle (produce/protein/dairy/pantry/frozen) | Single trip |
| **Budget Guardrail** | Estimates per-ingredient cost from local price dictionary; flags if total exceeds weekly cap |
| **Output Formats** | Calendar table (Markdown / printable), recipe cards, shopping list (Markdown + plain-text for phone), ICS events for "cook at 6pm" reminders | Paste into Notes / print / import |
| **Local-First** | Plan stored as Markdown in `~/.hermes/data/weekly-meal-planner/`; no cloud, no signup | Auditable, shareable |

## When to Use

- *"Plan my meals for next week — 2 people, 30-min weeknights, vegetarian, no peanuts"*
- *"I have chicken thighs expiring Tuesday and a CSA box of greens — build my week around those"*
- *"周日做一次大采购 + 备菜，给我排 7 天"*
- *"I have $80 for groceries this week for a family of 4 — make it work"*
- *"Generate a shopping list from last week's plan but skip Sunday because we're out"*
- *"Swap Wednesday's dinner for something kid-friendly"*
- *"Show me which days need batch-cook prep"*
- *"Generate ICS events for the cook slots so I get reminders"*

## Core Workflow

### Step 1: Build or load the household profile

```bash
mkdir -p ~/.hermes/data/weekly-meal-planner
# profile.json lives next to the plan
```

**Schema (`profile.json`):**

```json
{
  "household_size": 2,
  "diet": "omnivore",
  "allergies": ["peanut", "shellfish"],
  "dislikes": ["liver", "blue cheese"],
  "weekday_dinner_minutes": 30,
  "weekend_cook_minutes": 120,
  "weekly_grocery_budget_usd": 80,
  "favorite_cuisines": ["japanese", "italian", "mexican"],
  "kitchen_equipment": ["oven", "stovetop", "instant-pot", "air-fryer"],
  "leftovers_tolerance": "high",
  "notes": "Tuesday dinner out with friends. Thursday lunch is at desk."
}
```

**Capture by chat.** First-time setup asks the user a focused block of questions; subsequent weeks inherit and only ask what changed.

> *"I'll need 6 quick answers: how many people, diet, allergies, weekday time budget, weekend time, weekly grocery budget. Anything else is optional."*

If the profile already exists, load it and confirm only deltas:

> *"Same as last week except: salmon on Friday instead of chicken, and budget now $90. Sound right?"*

---

### Step 2: Pull context — pantry, calendar, recipe bank

**A. Pantry-first priority.** If `~/.hermes/data/pantry-manager/pantry.json` exists, parse it and rank ingredients by expiry:

```python
import json, datetime
from pathlib import Path

PANTRY = Path.home() / ".hermes/data/pantry-manager/pantry.json"
def expiring_within(days=7):
    if not PANTRY.exists(): return []
    data = json.loads(PANTRY.read_text())
    cutoff = datetime.date.today() + datetime.timedelta(days=days)
    items = []
    for batch in data.get("batches", []):
        exp = datetime.date.fromisoformat(batch["expires_on"])
        if exp <= cutoff:
            items.append((batch["name"], (cutoff - exp).days, batch["quantity"]))
    return sorted(items, key=lambda x: x[1])  # soonest first
```

Any item expiring within 7 days gets **forced inclusion** — at least one recipe in the week must consume it.

**B. Calendar awareness.** If `~/.hermes/data/calendar-optimizer/calendar.ics` is available (or the user pastes events), scan Mon–Sun:

- Days with a `LUNCH-OUT` or `DINNER-OUT` event → skip that slot.
- Days with evening meetings after 7pm → mark dinner as "must be < 20 min" or "leftover night".
- Days with a 60+ min gap at noon → "leftover-prep" slot.

**C. Recipe bank** (`~/.hermes/data/weekly-meal-planner/recipes.json`). Built up over time; ship with 30+ seed recipes tagged with metadata:

```json
{
  "id": "sheet-pan-chicken-broccoli",
  "name": "Sheet-pan Chicken & Broccoli",
  "meal": "dinner",
  "cuisine": "american",
  "protein": "chicken",
  "is_vegetarian": false,
  "time_minutes": 25,
  "difficulty": "easy",
  "freezer_friendly": false,
  "yields_leftovers_for": 0,
  "uses_leftovers_from": [],
  "ingredients": [
    {"name": "chicken thigh", "qty": 600, "unit": "g"},
    {"name": "broccoli", "qty": 1, "unit": "head"},
    {"name": "olive oil", "qty": 2, "unit": "tbsp"},
    {"name": "garlic", "qty": 3, "unit": "cloves"}
  ]
}
```

Seeds included with the skill cover: 7× quick weeknight dinners, 4× weekend batch cooks, 5× breakfasts, 4× lunch salads/bowls, 3× vegetarian mains, 2× vegan mains.

---

### Step 3: Generate the 7-day grid

Run the constraint solver. Pure-Python, no external libs required.

```python
def plan(profile, pantry_expiring, calendar_constraints, recipes):
    days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    grid = {d: {"breakfast": None, "lunch": None, "dinner": None} for d in days}

    # 1) Fill forced slots first
    for item in pantry_expiring:
        recipe = find_recipe_using(item.name, recipes)
        if recipe: grid[soonest_free_slot(item.expires_in_days, grid)] = recipe

    # 2) Weekday dinners: time-budget + no-repeat-protein-in-3-days
    recent_proteins = []
    for d in days[:5]:
        if calendar_constraints[d].dinner_out: continue
        candidates = [r for r in recipes if r["meal"]=="dinner"
                      and r["time_minutes"] <= profile["weekday_dinner_minutes"]
                      and r["protein"] not in recent_proteins[-3:]
                      and not violates_diet(r, profile)]
        grid[d]["dinner"] = pick(candidates, weights={"variety":1,"cuisine_pref":2})

    # 3) Weekend: batch-cook on Sunday, reuse Mon/Tue/Wed
    sunday_batch = pick_batch_cook(recipes, profile)
    grid["Sun"]["dinner"] = sunday_batch
    for d in ["Mon","Tue"]:
        if not calendar_constraints[d].dinner_out:
            grid[d]["dinner"] = find_recipe(uses_leftovers_from=sunday_batch.id)

    # 4) Lunches: leftovers from previous dinner, or salad/grain-bowl
    for d in days:
        if calendar_constraints[d].lunch_out: continue
        prev_dinner = grid[prev(d)]["dinner"]
        if prev_dinner and prev_dinner.get("yields_leftovers_for",0) >= 1:
            grid[d]["lunch"] = label_as_leftover(prev_dinner)
        else:
            grid[d]["lunch"] = pick_lunch(recipes)

    # 5) Breakfasts: rotating 5 options across the week
    grid = rotate_breakfasts(grid, recipes)

    return grid
```

**Variety rules enforced:**
- No protein repeats within 3 days
- No cuisine repeats 2 days in a row
- At least 1 vegetarian dinner per week (unless profile says otherwise)
- At least 2 sheet-pan / one-pot / no-knife recipes for tight weeks
- Force-include expiring pantry items

---

### Step 4: Build the consolidated shopping list

Aggregate every ingredient from the 7-day grid; consolidate; group by aisle.

```python
from collections import defaultdict
from pint import UnitRegistry  # optional; pure-stdlib fallback below
ureg = UnitRegistry()

def aggregate(plan):
    totals = defaultdict(lambda: defaultdict(float))  # name -> {unit: qty}
    for day, meals in plan.items():
        for slot, recipe in meals.items():
            if not recipe: continue
            for ing in recipe["ingredients"]:
                # convert to canonical unit (g, ml, count)
                qty = to_canonical(ing["qty"], ing["unit"])
                totals[ing["name"]][ing["unit"]] += ing["qty"]
    return totals

def group_by_aisle(totals, aisle_map):
    grouped = defaultdict(list)
    for name, units in totals.items():
        aisle = aisle_map.get(normalize(name), "other")
        grouped[aisle].append({"name": name, "qty": units})
    return grouped
```

**Default aisle map** (`aisles.json`):
```json
{
  "produce": ["onion","garlic","tomato","broccoli","spinach","lemon","carrot","pepper","potato","ginger"],
  "protein": ["chicken","beef","salmon","tofu","egg","shrimp","pork","lentil","chickpea"],
  "dairy": ["milk","yogurt","butter","cheese","cream"],
  "pantry":  ["rice","pasta","olive oil","soy sauce","salt","pepper","cumin","flour","sugar"],
  "frozen":  ["frozen peas","ice cream","frozen berries"],
  "bakery":  ["bread","tortilla","pita"]
}
```

If pantry-manager is installed, **subtract** what you already have at home before adding to the list. If something expires during the week (e.g., leftover chicken from Sunday), do NOT put it on the shopping list.

**Output the list grouped by aisle, sorted alphabetically within aisle:**

```markdown
# 🛒 Shopping List — Week of Aug 25

## Produce
- 3 × onion
- 2 × broccoli head
- 500 g spinach
- 1 × lemon

## Protein
- 800 g chicken thigh
- 400 g salmon fillet
- 12 × egg

## Dairy
- 1 L milk
- 200 g feta

## Pantry
- 500 g rice
- 200 ml olive oil

---
Estimated cost: $74 / Budget $80 ✅
Already in pantry (subtracted): garlic, salt, olive oil (partial)
Expiring this week (force-included): chicken thigh 600g (exp Mon)
```

---

### Step 5: Persist + deliver

```bash
mkdir -p ~/.hermes/data/weekly-meal-planner/2026-W35
```

Files written:

| File | Purpose |
|---|---|
| `plan.md` | Human-readable 7-day calendar + shopping list |
| `plan.json` | Machine-readable (for ICS generation, replanning) |
| `shopping-list.md` | Plain-text list (paste into Notes / print) |
| `ics/cooking-slots.ics` | Optional ICS events "Cook dinner at 6pm" Mon–Sun |
| `cost-estimate.json` | Per-ingredient cost + total + over-budget flag |

**Generate ICS events** (optional, if user wants calendar reminders):

```python
def emit_ics(plan, week_start_date):
    lines = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//weekly-meal-planner//EN"]
    for day, meals in plan.items():
        for slot, recipe in meals.items():
            if not recipe or slot != "dinner": continue
            dt = week_start_date + timedelta(days=days.index(day))
            lines += [
                "BEGIN:VEVENT",
                f"DTSTART;TZID=America/Los_Angeles:{dt}T180000",
                f"DTEND;TZID=America/Los_Angeles:{dt}T183000",
                f"SUMMARY:Cook: {recipe['name']}",
                f"DESCRIPTION:Time: {recipe['time_minutes']} min | Difficulty: {recipe['difficulty']}",
                "END:VEVENT"
            ]
    lines.append("END:VCALENDAR")
    return "\n".join(lines)
```

---

## Example Invocations

### Example 1: First-time weekly plan, 2-person household

> **User:** Plan my meals for next week. Two of us, omnivore but we like 1-2 vegetarian dinners, no shellfish, peanut allergy for my partner. Weekday dinners must be ≤30 min. Sundays I have 2 hours to cook. Budget $80.

> **Agent:** *"Quick profile — household 2, omnivore + 1-2 veg dinners/week, no shellfish, peanut-free, weekday ≤30 min, Sunday 2 hrs, $80 budget. Saving as `~/.hermes/data/weekly-meal-planner/profile.json`. Confirm?"*

> **User:** Yes, also I have half a head of broccoli and some chicken thighs I need to use by Tuesday.

> **Agent:** Runs pantry pull → forces chicken thighs onto Monday. Builds grid:

```markdown
# Week of Sep 1 — 7-Day Plan

| Day | Breakfast | Lunch | Dinner |
|-----|-----------|-------|--------|
| Mon | Overnight oats | Turkey sandwich | Sheet-pan chicken & broccoli *(use expiring chicken)* |
| Tue | Yogurt parfait | Leftover chicken bowl | Veggie stir-fry with rice *(20 min)* |
| Wed | Avocado toast | Lentil salad | Salmon tacos *(25 min, leftover-friendly)* |
| Thu | Smoothie | Leftover salmon bowl | One-pot pasta primavera *(veg, 25 min)* |
| Fri | Scrambled eggs + toast | Grain bowl | Sheet-pan sausage & peppers *(30 min)* |
| Sat | Pancakes | Out | Pizza night *(homemade)* |
| Sun | French toast | Roast chicken prep | Sunday roast chicken + 3 sides *(batch)* |
```

Then outputs the **shopping list grouped by aisle**, **cost estimate $76 / $80**, **leftover note: Sun roast → Mon/Tue/Wed lunches**, **3 batch-cook time slots flagged on Sunday**.

---

### Example 2: Re-plan around a dinner-out

> **User:** Swap Thursday dinner — I have dinner with Priya at a restaurant. Also make Friday kid-friendly, my in-laws are visiting.

> **Agent:** *"Removing Thursday dinner, adding 'restaurant with Priya' placeholder. Friday: was salmon tacos → swapping to baked chicken tenders + roasted carrots (kid-friendly, 30 min). Adjusted shopping list: -salmon -tortilla, +chicken tender -carrot. New total $71."*

---

### Example 3: Pantry-driven planning

> **User:** 冰箱里有 4 个西红柿、500g 意面、半袋菠菜、一盒豆腐——下周给我排 7 天，尽量用掉这些。

> **Agent:** Parses 4 tomatoes (exp in 5 days), pasta 500g, spinach (exp in 3 days), tofu (exp in 7 days). Builds a week where Mon–Wed use these as anchors:

```markdown
| Day | Dinner |
|-----|--------|
| Mon | Tomato pasta + spinach (use expiring spinach) |
| Tue | Mapo tofu + rice (use tofu) |
| Wed | Caprese + eggs (use last 2 tomatoes) |
| Thu–Sun | (new protein purchases — list below) |
```

Shopping list shows: **add chicken 600g, ground beef 400g, salmon 400g, onions, garlic**. **Do not add**: tomatoes, pasta, spinach, tofu.

---

## Common Pitfalls

| Pitfall | Solution |
|---|---|
| Recipe asks for "1 onion" three times → user buys 1 onion | Always consolidate units in Step 4 before printing list |
| User has an allergy but agent includes that recipe | Filter `allergies ⊄ recipe.ingredients` AND `recipe.tags` before selecting |
| "Vegetarian" but recipe includes fish sauce | Strict veg = no animal products at all; flag hidden animal products (fish sauce, oyster sauce, parmesan, anchovy, lard) in recipe metadata |
| Sunday roast planned for 2 hours but profile says 60 min | Filter weekend slots by `time_minutes ≤ profile.weekend_cook_minutes` |
| Plan reuses chicken on Mon AND Wed → boring | Track `recent_proteins` window of 3 days |
| Calendar conflict missed — lunch-out day still has lunch planned | Cross-reference `calendar-optimizer` output; mark lunch-out days as `skipped` |
| Cost estimate wildly off — agent says $30 but reality is $80 | Use a local price dictionary (`prices.json`) and weight by region (Bay Area ≠ rural Midwest). Update prices quarterly from user's receipts |
| Pantry subtraction wrong — adds garlic even though 3 heads at home | Read `pantry.json` and subtract `min(recipe_qty, pantry_qty)` per ingredient |
| Leftover tag misused — Monday "leftover chicken" when Sunday was roast beef | Link by recipe ID, not by protein name; Sunday's `recipe.id` must equal Monday's `uses_leftovers_from` |
| Budget exceeded silently | Always print `Estimated cost: $X / Budget $Y ✅/⚠️ OVER BY $Z` at the top of the shopping list |
| Plan ignores user's "no cilantro" / "no mushrooms" | `dislikes` is a hard filter, same as allergies; check both name AND common aliases |
| ICS events fire at 6pm but user gets home at 7 | Ask for "cook window start" in profile; default to 6pm but override per request |

---

## Verification Checklist

Before delivering a plan, the agent must confirm:

- [ ] Profile loaded or captured (all required fields: household_size, diet, allergies, weekday_min, weekend_min, budget)
- [ ] Pantry-pulled and expiring items are force-included somewhere in the 7-day grid
- [ ] Calendar constraints applied (lunch-out / dinner-out days marked skipped)
- [ ] No recipe violates diet (vegetarian/vegan/kosher/halal) or contains any item in `allergies`
- [ ] No protein repeats within any 3-day window
- [ ] No cuisine repeats 2 days in a row (soft check; allow if forced)
- [ ] At least 1 vegetarian dinner if profile.diet is `omnivore-flex`
- [ ] Weekday dinner `time_minutes ≤ profile.weekday_dinner_minutes`
- [ ] Weekend dinner `time_minutes ≤ profile.weekend_cook_minutes` (or marked batch-cook)
- [ ] Sunday batch-cook (if present) yields leftovers linked to Mon/Tue
- [ ] Shopping list quantities are consolidated (no duplicates for same item)
- [ ] Pantry stock is subtracted from shopping list
- [ ] Shopping list grouped by aisle, sorted alphabetically within aisle
- [ ] Total cost estimate printed vs. budget with over/under flag
- [ ] Plan saved to `~/.hermes/data/weekly-meal-planner/{ISO-week}/plan.md`
- [ ] JSON saved alongside for re-planning / ICS export
- [ ] Optional ICS events generated for cook slots if user requested

---

## Data Sources & Accuracy

| Source | What it provides | Local / Online | Update cadence |
|---|---|---|---|
| `~/.hermes/data/pantry-manager/pantry.json` | What user already has + expiry dates | Local | Real-time when user logs |
| `~/.hermes/data/calendar-optimizer/calendar.ics` | Calendar constraints (lunch/dinner out, evening meetings) | Local | Real-time |
| `recipes.json` (shipped + user-added) | Recipe bank with metadata | Local | User can add; skill ships ~30 seeds |
| `aisles.json` (shipped) | Ingredient → aisle mapping | Local | Stable |
| `prices.json` (user-maintained) | Per-ingredient cost estimates | Local | User updates from receipts |
| USDA FoodData Central API *(optional)* | Nutrition per recipe (calories, protein, macros) | Online, free | Per-recipe on demand |
| OpenStreetMap *(optional)* | Find nearest grocery store for the shopping trip | Online | Per query |

**Accuracy notes:**
- Recipe times are **estimates** — actual cook time varies by equipment. Add a 20% buffer when user has only 30 min.
- Cost estimates are **ballpark** until user populates `prices.json` from their own store. Provide a "calibrate from your last receipt" prompt on first use.
- Leftover safety: only plan Mon/Tue leftovers from Sun batch; never Wed/Thu leftovers (food safety window).
- The skill **does not** give nutritional or medical dietary advice — for medical conditions (diabetes, CKD, etc.), refer to a registered dietitian.

---

## Integration Notes

**Pairs naturally with:**

- **`recipe-generator`** — for any recipe the user wants more detail on
- **`pantry-manager`** — supplies the inventory + expiring items
- **`personal-expense-tracker`** — log grocery cost after the shopping trip
- **`fitness-planner`** — align macros if user has a calorie/protein target
- **`calendar-optimizer`** — pull dinner-out / lunch-out events
- **`daily-briefing`** — include "Today's dinner: Sheet-pan chicken. Start at 6:15pm" in the morning brief

**Files written** (all under `~/.hermes/data/weekly-meal-planner/`):

```
profile.json              # household prefs, captured once + delta each week
recipes.json              # recipe bank, user-extendable
aisles.json               # ingredient → aisle mapping (shipped)
prices.json               # cost estimates (user-populated)
2026-W35/
  plan.md                 # human-readable 7-day calendar
  plan.json               # machine-readable
  shopping-list.md                 # pasteable list
  ics/cooking-slots.ics   # optional calendar reminders
  cost-estimate.json      # per-ingredient cost breakdown
```