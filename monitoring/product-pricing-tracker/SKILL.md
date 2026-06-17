---
name: product-pricing-tracker
description: "Use when monitoring competitor or product pricing over time. Tracks pricing page changes, detects price drops/increases, and generates price change reports. Designed to pair with cron for recurring checks."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [pricing, monitoring, competitive-intelligence, cron, ecommerce, saas]
    related_skills: [local-competitive-analysis, competitive-research]
---

# Product Pricing Tracker

> Monitor competitor or product pricing over time. Detects price drops, increases, plan changes, and new offerings — designed to pair with cron for recurring automated checks.

---

## Overview

This skill helps you track pricing changes for any product or service over time. It scrapes a pricing page, records a baseline snapshot, and on subsequent runs detects what changed — price increases/drops, new plan tiers, removed features, promotional offers, etc.

When paired with a [cron job](https://hermes-agent.nousresearch.com/docs/agent/cron), it becomes a fully automatic competitive pricing monitor: check weekly/daily and get notified only when something changes.

**What it can track:**
| Type | Examples |
|------|----------|
| **SaaS pricing** | Plan names, monthly/yearly prices, feature lists per tier |
| **E-commerce** | Product prices, discounts, stock status, shipping costs |
| **Subscription changes** | New plans introduced, old plans retired, price increases |
| **Promotions** | Discount codes, limited-time offers, bundle deals |

---

## When to Use

- User asks: *"Set up price monitoring for Notion's pricing page"*
- User asks: *"Check if Vercel changed their pricing recently"*
- User asks: *"Compare this product's price to last month"*
- User asks: *"Monitor OpenAI API pricing changes"*
- User asks: *"Track Black Friday discounts for my competitors"*

---

## Core Workflow

### Step 1: Gather Pricing Data

Given a URL (usually `/pricing` page), collect comprehensive data:

#### 1a. Fetch Page Content
```bash
curl -sL https://{url} 2>&1
```

#### 1b. Extract Pricing Structure

Look for:
- **Plan names** — "Free", "Pro", "Team", "Enterprise"
- **Price amounts** — `$X/mo`, `$X/year`, `¥X`, `€X`
- **Billing intervals** — monthly, annual, one-time
- **Feature lists** — what each tier includes
- **Usage limits** — seats, storage, API calls, projects
- **Promotions** — discount badges, "Save X%", limited-time offers
- **CTA buttons** — "Get Started", "Contact Sales", "Free Trial"

Patterns to search:
```python
# Common price patterns in HTML
\$[\d,]+(?:\.\d{2})?\s*(\/mo|\/month|\/year|\/yr|\/seat)?
\$\d+-\$\d+
from \$\d+
```

#### 1c. Handle Dynamic Pricing Pages

If the page uses JavaScript to render prices (common with modern SPAs), use the browser:

```javascript
// In browser console, extract visible pricing
document.querySelectorAll('[class*="price"], [class*="plan"], [class*="tier"]')
  .forEach(el => console.log(el.innerText.trim()));
```

### Step 2: Save Baseline Snapshot

Save the pricing data as a structured JSON file:

```
~/research/pricing-tracker/{product-name}/baseline.json
~/research/pricing-tracker/{product-name}/history/
```

**Baseline format:**
```json
{
  "product": "Product Name",
  "url": "https://example.com/pricing",
  "snapshot_date": "YYYY-MM-DD",
  "plans": [
    {
      "name": "Free",
      "price": "$0",
      "interval": "month",
      "features": ["Feature 1", "Feature 2"]
    },
    {
      "name": "Pro",
      "price": "$20",
      "interval": "month",
      "features": ["Feature 1", "Feature 2", "Feature 3"]
    }
  ],
  "metadata": {
    "has_free_trial": true,
    "has_enterprise": true,
    "currency": "USD",
    "source": "curl/browser"
  }
}
```

### Step 3: Detect Changes (Subsequent Runs)

On subsequent checks, compare new data against the last snapshot:

1. Scrape current pricing
2. Compare plan names, prices, and feature lists
3. Identify:
   - **Price changes** — "$15 → $20/mo" (+33%)
   - **New plans** — previously absent tier
   - **Removed plans** — tier no longer exists
   - **Feature changes** — added/removed features per tier
   - **Promotional changes** — new discount badges or expired offers

### Step 4: Generate Change Report

```markdown
# Pricing Change Report: {Product Name}

**Date:** {YYYY-MM-DD}
**Previous Check:** {YYYY-MM-DD}
**URL:** {url}

---

## 📊 Summary

| Metric | Value |
|--------|-------|
| **Status** | ✅ No changes / ⚠️ Changes detected / 🚨 Significant changes |
| **Plans tracked** | {N} |
| **Changes found** | {N} |
| **Next check** | {suggested interval} |

---

## 🔄 Changes Detected

### {Plan Name 1}
| Dimension | Before | After | Delta |
|-----------|--------|-------|-------|
| Price | $15/mo | $20/mo | **+$5 (+33%)** 🔺 |
| Storage | 10 GB | 10 GB | — |
| Team seats | 5 | 5 | — |

### {Plan Name 2}
| Dimension | Before | After | Delta |
|-----------|--------|-------|-------|
| Price | $0 | $0 | — |
| Features | Basic export | Basic export + API access | **+1 feature** ✨ |

### 🆕 New: {Plan Name}
| Detail | Value |
|--------|-------|
| Price | $50/mo |
| Position | Between Pro and Enterprise |
| Key features | ... |

### 🗑️ Removed: {Plan Name}
This plan is no longer listed on the pricing page.

---

## 📈 Pricing Trend

```
Date        | Free  | Pro   | Team  | Enterprise
2026-01-01  | $0    | $15   | $30   | Custom
2026-03-01  | $0    | $15   | $30   | Custom
2026-06-17  | $0    | $20   | $35   | $150
```

---

## 💡 Analysis

{2-3 sentence strategic interpretation:
- Is this a broad price increase (inflation / value capture)?
- Are they adding more free tier features (land-grab)?
- Did they restructure plans to push users to higher tiers?
- Any competitive signal (responding to rival's pricing change)?}

---

## 🔗 Sources

- Pricing page: {url}
- Previous snapshot: {path to baseline/history}
```

### Step 5: Set Up Cron Monitoring (Optional)

If the user wants ongoing tracking, offer to set up a cron job:

```bash
# Weekly check every Monday at 9 AM
cronjob \
  action=create \
  schedule="0 9 * * 1" \
  name="price-tracker-{product}" \
  prompt="Check {product} pricing at {url} for changes. Compare against the last snapshot at ~/research/pricing-tracker/{product}/baseline.json"
  skills=["product-pricing-tracker"]
```

---

## Example Invocations

### Example 1: Initial setup (one-time)
```
User: Track Notion's pricing for me
Hermes should:
  1. Fetch https://www.notion.so/pricing
  2. Extract plan names, prices, features
  3. Create baseline at ~/research/pricing-tracker/notion/
  4. Present current pricing summary
  5. Offer to set up cron monitoring
```

### Example 2: Check for changes
```
User: Has Vercel changed their pricing since last month?
Hermes should:
  1. Fetch https://vercel.com/pricing
  2. Compare with ~/research/pricing-tracker/vercel/baseline.json
  3. Generate change report
  4. Update baseline if changes found
```

### Example 3: Monitor multiple competitors
```
User: Set up weekly price monitoring for Linear, Notion, and Monday.com
Hermes should:
  1. Create baselines for all three
  2. Set up 3 cron jobs (staggered to avoid rate limits)
  3. Present initial comparison table
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **JavaScript-rendered pricing.** | Use browser (browser_navigate) instead of curl. Check for lazy-loaded pricing tables. |
| 2 | **Dynamic pricing (logged-in users see different prices).** | Note whether the pricing is public or account-based. Adjust expectations. |
| 3 | **Currency/locale differences.** | Explicitly capture currency (`$`, `€`, `¥`) and billing interval (`/mo`, `/yr`). |
| 4 | **A/B tested pricing pages.** | Run 2-3 checks within an hour to detect variability. Report if pricing appears to vary. |
| 5 | **Pricing in images / SVGs.** | Extract alt text or use vision tools. Note as "non-machine-readable" if undetectable. |
| 6 | **Feature lists change without price change.** | Still report — feature changes are strategic signals even without price movement. |
| 7 | **Cron job fails (pricing page changed layout).** | Recommend check alert: if the script can't find price patterns, flag for manual review. |

---

## Verification Checklist

- [ ] Pricing page successfully fetched (curl or browser)
- [ ] Plan names, prices, and intervals extracted
- [ ] Feature lists captured per tier
- [ ] Baseline JSON saved to `~/research/pricing-tracker/{product}/`
- [ ] If checking changes: compared against last snapshot
- [ ] Change report generated with before/after comparison
- [ ] Currency and billing interval noted
- [ ] Cron job offered / set up (if recurring monitoring requested)
