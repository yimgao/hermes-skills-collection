---
name: business-plan-generator
description: "Use when writing a business plan — generates a complete plan with executive summary, market analysis, competitive strategy, financial projections, and operations."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [business-plan, startup, entrepreneurship, funding, strategy]
    related_skills: [site-selection-pipeline, market-sizing, pitch-deck-helper]
---

# Business Plan Generator

> Generate a complete business plan from your concept. Covers executive summary, market analysis, competitive strategy, marketing, operations, financial projections, and funding ask.

---

## When to Use

- *"Write a business plan for my ramen shop in Durham, NC"*
- *"I need a business plan for investors"*
- *"Create a lean canvas for my startup idea"*
- *"Help me structure my business idea into a plan"*

---

## Core Workflow

### Step 1: Gather Information

Collect from the user:

| Section | What to ask |
|---------|-------------|
| **Concept** | What's the business? What makes it unique? |
| **Location** | City, neighborhood, type of space |
| **Target customer** | Who will buy? Demographics, psychographics |
| **Pricing** | Price range, average ticket |
| **Startup needs** | How much capital? What will it fund? |
| **Team** | Founder experience, key hires needed |

### Step 2: Generate Sections

```markdown
# Business Plan: {Business Name}

**Date:** {YYYY-MM-DD}
**Prepared for:** {Purpose — funding / personal / partnership}

---

## 1. Executive Summary
{2-3 paragraphs: concept, market opportunity, competitive advantage, financial ask}

## 2. Company Description
{Mission, vision, legal structure, founding story}

## 3. Market Analysis
{Industry overview, target market, TAM/SAM/SOM, market trends}

## 4. Competitive Analysis
{Direct competitors, indirect competitors, competitive advantage}

## 5. Marketing & Sales
{Go-to-market strategy, channels, pricing, promotions}

## 6. Operations
{Location, facilities, technology, staffing, suppliers}

## 7. Financial Projections
### Startup Costs
| Item | Cost |
|------|------|
| Lease deposits | ${N} |
| Equipment | ${N} |
| Buildout | ${N} |
| Initial inventory | ${N} |
| Marketing launch | ${N} |
| Working capital | ${N} |
| **Total** | **${N}** |

### Revenue Projection (Year 1-3)
| Metric | Year 1 | Year 2 | Year 3 |
|--------|--------|--------|--------|
| Revenue | ${N} | ${N} | ${N} |
| COGS | ${N} | ${N} | ${N} |
| Gross margin | {N}% | {N}% | {N}% |
| Operating expenses | ${N} | ${N} | ${N} |
| Net profit | ${N} | ${N} | ${N} |

## 8. Funding Ask
{How much, what for, proposed terms, use of funds table}

## 9. Milestones
| Timeline | Milestone |
|----------|-----------|
| Month 1-3 | {milestone} |
| Month 4-6 | {milestone} |
| Month 7-12 | {milestone} |
```

---

## Example

```
User: Write a business plan for a ramen + dumpling bar in Downtown Durham, NC
Hermes should:
  1. Ask about concept, budget, target customer
  2. Generate all 9 sections
  3. Include financial projections
  4. Save to ~/dev/reports/business-plans/
```
