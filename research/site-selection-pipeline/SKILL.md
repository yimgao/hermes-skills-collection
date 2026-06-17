---
name: site-selection-pipeline
description: "Use when finding the best location to open a business — runs restaurant-site-finder then local-competitive-analysis on the top city, producing one comprehensive report."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [site-selection, pipeline, restaurant, competitive-analysis, demographics, location-intelligence]
    related_skills: [restaurant-site-finder, local-competitive-analysis, writing-plans]
---

# Site Selection Pipeline

> Run two skills in sequence: first find the best city (restaurant-site-finder), then deep-dive into local competition (local-competitive-analysis). Produces one comprehensive report.

---

## When to Use

- *"Find the best city to open a ramen shop, then analyze the local competition"*
- *"我想开家奶茶店，帮我先选城市再看竞品"*
- *"Best location for my business + competitor deep dive"*
- *"Full site selection analysis for a new restaurant"*

---

## Pipeline Workflow

### Phase 1: Site Finder
Run `restaurant-site-finder` to identify the top candidate city.

Input: cuisine, budget, region, priority
Output: ranked Top 5 cities with scores

### Phase 2: Local Competitive Analysis
Take the #1 city from Phase 1 and run `local-competitive-analysis` on it.

Input: industry (cuisine), location (#1 city)
Output: local competitor landscape, SWOT, market gaps

### Phase 3: Combined Report
Merge both into one report:

```markdown
# Complete Site Selection Report: {Cuisine}

---

# PART 1: 全美城市筛选
[restaurant-site-finder output: Top 5 cities with scoring matrix]

---

# PART 2: 本地竞品深度分析
[local-competitive-analysis output: Top 5 competitors, SWOT, gaps]

---

# 🎯 Final Recommendation
[Combined: best city + best neighborhood + competitive positioning]
```
