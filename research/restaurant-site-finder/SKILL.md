---
name: restaurant-site-finder
description: "Use when finding the best location to open a restaurant — analyzes population, demographics, competitor density, income, foot traffic, and rent to rank potential cities."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [site-selection, restaurant, location-intelligence, demographics, market-analysis]
    related_skills: [local-competitive-analysis, competitive-research, writing-plans]
---

# Restaurant Site Finder

> Find the best location to open a restaurant. Analyzes population, demographics, competitor density, income levels, foot traffic, and commercial rent to rank potential cities.

---

## Overview

This skill helps you find the optimal location for opening a restaurant — specifically tailored to a cuisine type (e.g., ramen + dumplings, bubble tea, taco shop). It researches multiple data points per candidate city and produces a ranked list with detailed reasoning.

**What it analyzes per city:**

| Category | Data Points |
|----------|-------------|
| **👥 Population** | Total population, population growth trend, density |
| **🎯 Target demo** | Asian population %, young adults (20-40) %, family % |
| **💰 Economics** | Median household income, median rent, disposable income |
| **🍜 Competitors** | Number of same-cuisine restaurants, avg rating, market saturation |
| **🚶 Foot traffic** | Walkability score, downtown activity, tourism volume |
| **🏠 Rent** | Avg commercial rent per sq ft, lease terms, availability |
| **📈 Growth** | New housing developments, population inflow, commercial growth |

---

## When to Use

- *"Find the best US cities to open a ramen + dumpling shop"*
- *"我想到美国开家拉面饺子店，哪座城市最合适？"*
- *"Best locations for a bubble tea shop on the West Coast"*
- *"Compare Austin vs Denver for opening a ramen shop"*
- *"Where should I open my first restaurant?"*

---

## Core Workflow

### Step 1: Define Criteria

Clarify with the user:

| Parameter | Example |
|-----------|---------|
| **Cuisine** | Ramen + Dumplings |
| **Budget** | $200K startup, $5K/mo rent max |
| **Region** | US (or specific: West Coast, East Coast, Midwest) |
| **City size** | Major / Mid-size / Small |
| **Target demo** | Young professionals / Families / College students |
| **Priority** | Low competition > High foot traffic > Low rent |

If the user doesn't specify, use defaults:
- Cuisine: as stated
- Region: Continental US
- City size: Mid-to-major
- Priority: Balance of all factors

### Step 2: Generate Candidate Cities

Based on the cuisine type, generate an initial list of 8-12 candidate cities.

**For Asian cuisine (ramen, dumplings, bubble tea):**
- Cities with strong existing Asian food culture
- Growing Asian population (not just traditional hubs)
- College towns with diverse student bodies

**General starter list (customize per cuisine):**

| Tier | Cities |
|------|--------|
| Tier 1 (proven) | San Francisco, Los Angeles, NYC, Seattle, Vancouver |
| Tier 2 (growing) | Austin, Denver, Portland, Nashville, Charlotte, Raleigh |
| Tier 3 (emerging) | Columbus, Indianapolis, Salt Lake City, Boise, Omaha |
| Tier 4 (wildcard) | Spokane, Madison, Albuquerque, Tulsa, Knoxville |

### Step 3: Research Each City

For each candidate city, search for:

```python
# Population & demographics
"{city} population 2026"
"{city} asian population percentage"
"{city} median household income 2026"

# Competitor analysis
"ramen {city}"
"dumplings {city}"
"asian restaurants {city}"

# Real estate
"commercial rent {city} per square foot restaurant"
"{city} downtown retail vacancy rate"

# Growth
"{city} fastest growing neighborhoods"
"{city} population growth 2026"
```

### Step 4: Score & Rank

Score each city on a 1-10 scale across dimensions:

| Dimension | Weight | Data Source |
|-----------|--------|-------------|
| **Market demand** | 25% | Asian pop %, young adult %, population growth |
| **Competition gap** | 25% | # of same-cuisine restaurants vs demand |
| **Affordability** | 20% | Commercial rent, startup costs, median income |
| **Foot traffic** | 15% | Walkability, tourism, downtown density |
| **Growth potential** | 15% | Population inflow, new developments, trend |

### Step 5: Generate Report

```markdown
# Restaurant Site Analysis: {Cuisine}

**Date:** {YYYY-MM-DD}
**Region:** {US / specific region}
**Budget:** ${N}K startup · ${N}/mo rent max
**Priority:** {criteria}

---

## 🏆 Top 5 Recommendations

| Rank | City | Score | Best For | Est. Startup |
|------|------|-------|----------|-------------|
| 🥇 | **{City}, {State}** | **{N}/10** | {key strength} | ${N}K |
| 🥈 | **{City}, {State}** | **{N}/10** | {key strength} | ${N}K |
| 🥉 | **{City}, {State}** | **{N}/10** | {key strength} | ${N}K |
| 4 | {City}, {State} | {N}/10 | {key strength} | ${N}K |
| 5 | {City}, {State} | {N}/10 | {key strength} | ${N}K |

---

## 📊 Detailed Analysis

### 🥇 {City}, {State} — {N}/10

**Why it ranks #1:** {2-3 sentence summary}

#### 👥 Demographics
| Metric | Value | vs National | Score |
|--------|-------|-------------|-------|
| Population | {N} | {+/-}% | {N}/10 |
| Asian population | {N}% | {+/-}% | {N}/10 |
| Median age | {N} | {+/-} | {N}/10 |
| Median HH income | ${N}K | {+/-}% | {N}/10 |

#### 🍜 Competitor Landscape
- **Total ramen shops:** {N} ({avg rating: X.X})
- **Total dumpling shops:** {N} ({avg rating: X.X})
- **Market saturation:** {Low / Medium / High}
- **Top competitor:** {Name} ({Rating})
- **Gap:** {What's missing}

#### 🏠 Real Estate
- **Avg restaurant rent:** ${N}/sqft/mo
- **Downtown vacancy:** {N}%
- **Best neighborhoods:** {Area 1}, {Area 2}
- **Estimated buildout:** ${N}K

#### 📈 Growth Indicators
- **Population growth:** {+/-}% (past 5 years)
- **New developments:** {description}
- **Tourism:** {N}M visitors/year
- **Trend:** {up-and-coming / established / saturated}

#### 💡 Verdict
{Would I open a {cuisine} shop here? Why or why not.}

---

### 🥈 {City}, {State} — {N}/10
[Same structure]

---

## 📋 Comparison Matrix

| City | Score | Asian% | Competitors | Rent/sqft | Growth | Best Neighborhood |
|------|-------|--------|-------------|-----------|--------|-------------------|
| {City} | {N} | {N}% | {N} | ${N} | {+/-}% | {Area} |
| {City} | {N} | {N}% | {N} | ${N} | {+/-}% | {Area} |
| {City} | {N} | {N}% | {N} | ${N} | {+/-}% | {Area} |

---

## 🏠 Neighborhood Deep Dive (Top City)

### Best Area: {Neighborhood Name}

**Why:** {2-3 sentences}

| Factor | Assessment |
|--------|-----------|
| Foot traffic | {High/Medium/Low} — {details} |
| Nearby anchors | {Grocery, transit, office towers, universities} |
| Competitors nearby | {list within 3 blocks} |
| Rent estimate | ${N}/sqft/mo |
| Parking | {Street/Lot/Garage/None} |
| Visibility | {Storefront / Strip mall / Food court} |

### Runner-up: {Neighborhood Name}
{2-3 sentences}

---

## 🎯 Final Recommendation

**If you had to pick one city today: {City}, {State}**

**Why:** {3-4 paragraph executive summary covering:
- Market demand (why this city needs your cuisine)
- Competition (why you can win)
- Economics (why the math works)
- Risk factors (what to watch out for)}

---

## 📋 Sources

- {Source URL 1}
- {Source URL 2}
- Wikipedia population data
- Census demographic data
- Google Maps competitor search
- Commercial real estate listings
```

---

## Example Method: Scoring

When evaluating cities, use this rubric:

| Score | Meaning |
|-------|---------|
| 9-10 | Ideal — strong demand, low competition, good economics |
| 7-8 | Good — solid opportunity, minor trade-offs |
| 5-6 | Average — feasible but not optimal |
| 3-4 | Weak — significant challenges |
| 1-2 | Poor — do not recommend |

**Weighted scoring formula:**
```
Score = (demand_score × 0.25) + (competition_gap × 0.25) + 
        (affordability × 0.20) + (foot_traffic × 0.15) + (growth × 0.15)
```

---

## Example Invocation

```
User: Find the best US cities to open a ramen + dumpling shop. 
      Budget: $300K. Prefer growing mid-size cities.

Hermes should:
  1. Generate candidate list (12 cities across tiers)
  2. For each city, search:
     - Population & Asian %
     - # of ramen/dumpling shops + ratings
     - Median income, commercial rent
     - Growth trends
  3. Score each on 5 dimensions
  4. Produce ranked Top 5 with detailed analysis
  5. Include neighborhood deep dive for #1
  6. Save to ~/dev/reports/site-analysis/
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Outdated demographic data.** | Use latest census + city-specific reports. Prefer 2025-2026 data. |
| 2 | **Assuming one Asian cuisine fits all.** | A ramen shop in the Midwest needs different positioning than in SF. |
| 3 | **Ignoring existing saturation.** | Just because a city has Asian population doesn't mean it needs another ramen shop. |
| 4 | **Rent ≠ total cost.** | Factor in buildout, equipment, permits, insurance, labor. |
| 5 | **College towns look good on paper.** | Demand drops 50%+ during summer. Need year-round traffic. |
| 6 | **Forgetting local regulations.** | Check liquor license availability, health dept requirements, zoning. |

---

## Verification Checklist

- [ ] Criteria clarified (cuisine, budget, region, priority)
- [ ] 8-12 candidate cities generated
- [ ] Population + Asian % data collected per city
- [ ] Competitor count (ramen + dumpling) per city
- [ ] Rent estimates per city
- [ ] Growth indicators per city
- [ ] Each city scored on 5 weighted dimensions
- [ ] Top 5 ranked with clear reasoning
- [ ] Neighborhood deep dive for #1 city
- [ ] Final recommendation with executive summary
- [ ] Saved to `~/dev/reports/site-analysis/`
