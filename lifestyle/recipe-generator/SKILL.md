---
name: recipe-generator
description: "Use when generating recipes from available ingredients — suggests dishes based on what's in the fridge, considers dietary restrictions, and provides step-by-step instructions."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [cooking, recipe, food, meal-planning, ingredients]
    related_skills: [meal-planner, fitness-planner, travel-itinerary-planner]
---

# Recipe Generator

> Generate recipes from ingredients you already have. Say what's in your fridge and get step-by-step recipes with estimated time and difficulty.

---

## When to Use

- *"I have chicken, broccoli, and cheese — what can I make?"*
- *"冰箱里有鸡蛋、豆腐、青椒，能做啥？"*
- *"Give me a quick dinner recipe with pantry staples"*
- *"Healthy recipe using salmon and asparagus"*

---

## Core Workflow

### Step 1: List Ingredients

Accept ingredients as a comma-separated list. Clarify:
- **Main protein** (chicken, tofu, fish, none)
- **Vegetables** (what's available)
- **Pantry staples** (rice, pasta, eggs, oil, spices)
- **Dietary restrictions** (vegetarian, vegan, gluten-free, keto)

### Step 2: Generate Recipe(s)

For each recipe, provide:

```markdown
# 🍳 {Recipe Name}

**Prep time:** {N} min
**Cook time:** {N} min
**Difficulty:** {Easy/Medium/Hard}
**Dietary:** {Labels}

---

## Ingredients
| Ingredient | Amount |
|------------|--------|
| {item} | {quantity} |
| {item} | {quantity} |

## Instructions
1. {Step 1}
2. {Step 2}
3. {Step 3}

## 💡 Tips
- {Tip 1}
- {Substitution 1}
```
