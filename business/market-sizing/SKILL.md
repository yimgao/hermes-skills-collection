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


---

## 📋 Data Sources & Accuracy

This skill relies on searching external data. Follow these guidelines to ensure accuracy:

### Primary vs Secondary Sources
| Priority | Source Type | Examples |
|----------|-------------|----------|
| 🥇 **Primary (prefer)** | Government / Official | Census.gov, BLS, city economic dev, official APIs |
| 🥈 **Secondary** | Aggregators / Reviews | Google Maps, Yelp, LoopNet, Wikipedia |
| 🥉 **Tertiary** | Estimates / Inferences | Industry reports, blog posts, news articles |

### Accuracy Rules
1. **Always cite the source** for each data point — don't state numbers without attribution
2. **When sources conflict**, prefer: government > official > aggregator > blog
3. **If data is unavailable**, say "Not found" — do NOT fabricate or approximate without stating it's an estimate
4. **Mark estimates clearly** with "~" or "estimated" — never present guesses as facts
5. **Use ranges** when uncertain (e.g., "$20-25/sqft" not "$22.50/sqft")
6. **Timestamp your data** — note when it was collected (e.g., "as of June 2026")

### When Web Search Returns Limited Data
- Note the limitation explicitly: "Google Maps limited view", "Search blocked by CAPTCHA"
- Fall back to known data or general market knowledge
- Explicitly mark knowledge-based data as "based on general market knowledge"
- Never invent competitor names, ratings, or prices

### Verification Checklist
- [ ] Every number attributed to a source
- [ ] Estimates clearly marked (use "~" or "estimated")
- [ ] Unavailable data noted as "not found"
- [ ] Data collection timestamp recorded
- [ ] Confidence level noted (High / Medium / Low)
