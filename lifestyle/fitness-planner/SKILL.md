---
name: fitness-planner
description: "Use when creating workout plans — generates weekly training schedules based on goals (strength/hypertrophy/fat loss), equipment available, and days per week."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [fitness, workout, exercise, training, health, gym]
    related_skills: [meal-planner, recipe-generator, travel-itinerary-planner]
---

# Fitness Planner

> Generate weekly workout plans based on your goals, equipment, and schedule. Structured training programs with exercise selection, sets, reps, and progression.

---

## When to Use

- *"Create a 4-day push/pull/legs workout plan"*
- *"I want to lose weight — give me a weekly gym plan"*
- *"Home workout plan with just dumbbells"*
- *"帮我做个增肌训练计划"*

---

## Core Workflow

### Step 1: Gather Details

| Parameter | Options |
|-----------|---------|
| Goal | Strength / Hypertrophy / Fat Loss / Endurance / General |
| Days/week | 2, 3, 4, 5, 6 |
| Equipment | Gym / Home / Dumbbells only / Bodyweight |
| Experience | Beginner / Intermediate / Advanced |
| Focus | Full body / Upper/Lower / PPL / Push/Pull/Legs |

### Step 2: Design Program

Common splits:
```
3-day: Full Body (M/W/F) or Push/Pull/Legs
4-day: Upper/Lower (x2) or PPL + accessory
5-day: PPL + Upper + Lower
6-day: PPL (x2)
```

### Step 3: Generate Plan

```markdown
# 🏋️ Workout Plan

**Goal:** {Strength/Hypertrophy/Fat Loss}
**Schedule:** {N} days/week
**Split:** {Full Body / PPL / Upper-Lower}
**Level:** {Beginner/Intermediate}

---

## Weekly Schedule
| Day | Workout | Focus |
|-----|---------|-------|
| Mon | Push | Chest, Shoulders, Triceps |
| Tue | Pull | Back, Biceps, Rear Delts |
| Wed | Rest | — |
| Thu | Legs | Quads, Hamstrings, Glutes |
| Fri | Push | (same, heavier) |
| Sat | Pull | (same, heavier) |
| Sun | Rest | — |

## Day 1: Push

| Exercise | Sets × Reps | Rest | Notes |
|----------|-------------|------|-------|
| Bench Press | 4×8-10 | 90s | Main lift |
| Overhead Press | 3×10-12 | 60s | Superset with next |
| Lateral Raise | 3×15 | 45s | Light weight |
| Tricep Pushdown | 3×12-15 | 45s | Drop set last set |

## Progression
- Add 5 lbs to main lifts each week
- If you hit all reps, increase weight next session
- Deload week every 6th week

## 💡 Tips
- Warm up 5-10 min before each session
- Rest 90s for compound, 45-60s for isolation
- Progressive overload is key
```
