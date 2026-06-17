---
name: market-sizing
description: "Use when estimating market size — calculates TAM, SAM, and SOM for any product or service using population data, adoption rates, and pricing."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [market-sizing, tam, sam, som, market-analysis, business-plan]
    related_skills: [business-plan-generator, site-selection-pipeline, competitive-research]
---

# Market Sizing

> Estimate your market size. Calculates TAM (Total Addressable Market), SAM (Serviceable Available Market), and SOM (Serviceable Obtainable Market) using top-down and bottom-up approaches.

---

## When to Use

- *"What's the market size for ramen in the US?"*
- *"How big is the bubble tea market in North Carolina?"*
- *"I need TAM/SAM/SOM numbers for my pitch deck"*
- *"Estimate the market opportunity for my business"*

---

## Core Workflow

### Step 1: Define Scope

| Parameter | Example |
|-----------|---------|
| Product/Service | Ramen restaurant |
| Geography | US → Southeast → NC → Raleigh-Durham |
| Customer segment | Dine-in customers, delivery, catering |

### Step 2: Top-Down Approach

**TAM:** Total global/national market
```
Search: "{industry} market size {year}"
Search: "{industry} industry revenue US"
```

**SAM:** Your serviceable portion
```
SAM = TAM × {geographic % × segment %}
```

**SOM:** Realistically obtainable
```
SOM = SAM × {market share % — usually 1-5% for new entrant}
```

### Step 3: Bottom-Up Approach

```
Available customers = {target population} × {% who eat this cuisine}
Annual visits per customer = {frequency}
Average spend per visit = ${N}
Revenue potential = customers × visits × spend
```

### Step 4: Output

```markdown
# Market Sizing: {Product}

**Date:** {YYYY-MM-DD}
**Geography:** {scope}

---

## Top-Down

| Metric | Value |
|--------|-------|
| US market size | ${N}B |
| Southeast region share | {N}% → ${N}M |
| NC state share | {N}% → ${N}M |
| **TAM** | **${N}B** |
| **SAM** (our segment) | **${N}M** |
| **SOM** (5% of SAM) | **${N}M** |

## Bottom-Up

| Metric | Value |
|--------|-------|
| Target population | {N} |
| Adoption rate | {N}% |
| Annual visits/customer | {N} |
| Avg spend | ${N} |
| **Revenue potential** | **${N}** |

## Sources
- {Source 1}
- {Source 2}
```
