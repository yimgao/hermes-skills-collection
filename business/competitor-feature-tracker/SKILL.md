---
name: competitor-feature-tracker
description: "Use when monitoring 2-5 competitors' product features over time. Tracks changelogs, release notes, and product pages; detects new/removed/deprecated features; builds a per-competitor feature matrix; flags gaps vs. your product. Local JSON, cron-ready."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [competitive-intelligence, product, monitoring, saas, changelog, feature-matrix, cron, business]
    related_skills: [competitor-news-monitor, product-pricing-tracker, market-sizing, local-competitive-analysis, business-plan-generator]
---

# Competitor Feature Tracker / 竞品功能追踪器

> Track 2-5 competitors' product features, changelogs, and release notes over time. Build a side-by-side feature matrix, detect new/removed/deprecated features, and surface gaps versus your own product. Local JSON, designed to pair with cron for automatic weekly or monthly snapshots.

## Overview

You know your competitors exist, but you rarely know **what they shipped last week**. Product launches, beta flags, deprecations, "AI" badges, integrations, and pricing-tier reshuffles all live across scattered changelogs, blog posts, release notes pages, and X/Twitter announcements.

This skill turns that firehose into a **structured feature matrix** you can actually act on.

**What it tracks:**

| Signal | Where it comes from |
|--------|---------------------|
| **New feature** | Changelog page, "What's New" blog, release notes, GitHub releases |
| **Beta / early-access** | "Try it now" banners, feature flags, waitlist pages |
| **Removed / deprecated** | Sunset notices, "moved to…" redirects, EOL announcements |
| **Pricing-tier reshuffle** | New plan names, feature-gating shifts, free → paid moves |
| **Integration / partner** | New connectors, marketplace listings, "Now integrates with X" |
| **AI / model claim** | "Powered by GPT-4o", "built-in assistant", RAG, agents |
| **Platform expansion** | New regions, new OS app, mobile, CLI, browser extension |
| **Status / launch** | Public launch, GA, open beta, private alpha |

## When to Use

- User asks: *"Track what Linear, Notion, and Height ship each week"*
- User asks: *"Build a feature matrix for me vs. my top 3 competitors"*
- User asks: *"What features has Vercel added in the last 90 days?"*
- User asks: *"Where am I falling behind — show me the gap"*
- User asks: *"Set up a weekly changelog digest for these 4 SaaS tools"*
- User asks: *"Did anyone ship a feature like [X] this month?"*
- User asks: *"We just launched [feature] — who else has it and who doesn't?"*

## Core Workflow

### Step 1: Define Watchlist

Accept a watchlist of 2-5 competitors. Each entry has a name, the canonical product URL, and (ideally) a direct changelog URL.

```yaml
watchlist:
  - name: "Linear"
    product_url: "https://linear.app"
    changelog_url: "https://linear.app/changelog"
    docs_url: "https://linear.app/docs"
    twitter: "@linear"
  - name: "Height"
    product_url: "https://height.app"
    changelog_url: "https://height.app/changelog"
  - name: "Notion"
    product_url: "https://notion.so"
    changelog_url: "https://www.notion.so/releases"
```

If the user just types `"track: Linear, Height, Notion"`, resolve the changelog URL automatically:

```bash
# Quick URL guess — try common paths
for path in changelog releases "whats-new" "what's-new" updates news; do
  curl -sIL "https://$domain/$path" | head -1
done
```

Store the watchlist at `~/research/competitor-features/watchlist.yaml`. Re-use it on every run.

### Step 2: Pull Fresh Snapshots

For each competitor, harvest their current feature surface from multiple sources:

**Primary — their own changelog:**
```bash
# Plain HTML changelogs
curl -sL "$changelog_url" > /tmp/comp_changelog.html

# Or use the platform skill if available
# hermes -s web-scraping-systems --url "$changelog_url" --max-pages 5
```

**Secondary — release notes / blog / docs:**
- `{product}/blog`, `{product}/releases`, `{product}/docs/changelog`
- GitHub Releases: `https://github.com/{org}/{repo}/releases` (open-source tools)
- Product Hunt launches: `https://www.producthunt.com/posts/{slug}`
- Status page: `https://status.{domain}` (incidents can imply new infra)

**Tertiary — community signals:**
- Reddit: `site:reddit.com {competitor} new feature`
- X/Twitter: `from:{handle} launch` or `from:{handle} shipped`
- Hacker News: `site:news.ycombinator.com {competitor}`
- G2 / Capterra reviews (recent ones mention new features)
- YouTube: `{competitor} new feature {month}`

**Heuristic order of trust:**
1. Official changelog (highest — canonical)
2. Blog post / release notes
3. Docs update / screenshot
4. Founder/PM tweet
5. Community mention (lowest — verify)

### Step 3: Extract & Normalize Features

From each source, extract atomic features using a **stable vocabulary** so you can diff across weeks.

**Feature record schema:**
```json
{
  "id": "linear-2026-10-08-issues-v2",
  "competitor": "Linear",
  "first_seen": "2026-10-08",
  "last_updated": "2026-10-08",
  "title": "Issues v2 (redesigned issue detail)",
  "summary": "Redesigned issue detail with custom layouts, tabs, and synced sidebar.",
  "category": "core",
  "status": "shipped",
  "tags": ["ui", "core-workflow", "redesign"],
  "tier": "all",
  "sources": [
    {"url": "https://linear.app/changelog/2026-10-08-issues-v2", "kind": "changelog"},
    {"url": "https://twitter.com/linear/status/...", "kind": "tweet"}
  ],
  "ai_related": false,
  "notes": ""
}
```

**Standard categories (use these — don't invent new ones):**

| Category | What it covers |
|----------|----------------|
| `core` | Main workflow object (issues, docs, rows, etc.) |
| `collaboration` | Comments, mentions, sharing, multi-player |
| `automation` | Triggers, rules, workflows, bots |
| `ai` | AI features, agents, RAG, copilots |
| `integration` | Connectors, API, webhooks, marketplace |
| `mobile` | iOS, Android, offline, push |
| `reporting` | Dashboards, charts, exports |
| `admin` | SSO, SCIM, audit, permissions |
| `pricing-tier` | New plans, gating changes, free→paid moves |
| `platform` | CLI, SDK, browser extension, new OS |
| `deprecation` | Sunset, EOL, removed |

**Status values:** `shipped` (GA), `beta` (opt-in), `alpha` (private), `deprecated`, `removed`, `planned` (announced roadmap).

### Step 4: Detect Changes Against History

Store every snapshot under `~/research/competitor-features/{competitor}/history/YYYY-MM-DD.json`. To detect changes, diff the new snapshot against the latest one:

```python
# Pseudocode
old = load(f"{base}/history/{prev_date}.json")
new = load(f"{base}/history/{today}.json")

old_ids = {f["id"] for f in old["features"]}
new_ids = {f["id"] for f in new["features"]}

added     = new_ids - old_ids                # NEW since last run
removed   = old_ids - new_ids                # NO LONGER mentioned
updated   = [f for f in new_ids & old_ids
             if new[f] != old[f]]            # CHANGED description/tier/status
promoted  = [f for f in new_ids & old_ids
             if old[f]["status"] == "beta"
             and new[f]["status"] == "shipped"]  # moved to GA
deprecated = [f for f in new_ids & old_ids
              if new[f]["status"] in ("deprecated", "removed")]
```

**Special detections worth flagging:**

| Signal | Why it matters |
|--------|----------------|
| **Tier moved: `all` → `pro+`** | Competitor monetized a formerly-free feature |
| **Status: `beta` → `shipped`** | Now competitive parity required |
| **New category present** | Strategic pivot (e.g. first `ai` feature) |
| **Removed/deprecated at scale** | Tech debt or intentional narrowing |
| **First mention of a keyword** | `"agents"`, `"voice"`, `"RAG"` — emerging themes |

### Step 5: Build the Feature Matrix

Maintain a per-competitor **feature matrix** that updates on every run:

```markdown
# Feature Matrix — Q4 2026

Generated: 2026-10-12  |  Your product: Acme PM
Rows = capabilities. Columns = presence + tier + status + first-seen.

| Capability                  | Acme (you) | Linear | Height | Notion |
|-----------------------------|------------|--------|--------|--------|
| Custom issue layouts        | —          | ✅ Pro | ❌     | ❌     |
| AI triage suggestions       | ✅ Beta    | ✅ All | ✅ All | ❌     |
| Slack integration           | ✅ All     | ✅ All | ✅ All | ✅ All |
| Mobile offline mode         | ❌         | ✅ All | ✅ Pro | ✅ Pro |
| Workflow automations        | ✅ Pro     | ✅ Pro | ❌     | ✅ All |
| Audit log export            | ✅ Ent     | ✅ Ent | ✅ Ent | ✅ Ent |
| Public roadmap              | ❌         | ✅ All | ❌     | ❌     |
| Voice commands              | ❌         | ❌    | ❌     | ✅ Beta|
| GraphQL API                 | ❌         | ✅ Pro | ❌     | ❌     |
| SSO + SCIM                  | ✅ Ent     | ✅ Ent | ✅ Ent | ✅ Ent |

Legend: ✅ = shipped  •  🟡 = beta/alpha  •  ❌ = absent  •  — = unknown
Tiers:  All / Free / Pro / Team / Ent / Beta
```

**How to populate the "you" column:** ask the user once for their own product's feature list, or accept a pasted feature list / Notion export / a `competitor-features/your-product.yaml` file. Cache it.

### Step 6: Generate the Weekly Diff Report

**Single-competitor diff:**

```markdown
# Linear — Week of 2026-10-06 → 2026-10-12

**New (3)**
- 🚀 `linear-2026-10-08-issues-v2` — Issues v2 (redesigned) — *core, shipped*
- 🤖 `linear-2026-10-10-cmd-k-ai` — Cmd-K AI (beta) — *ai, beta, all tiers*
- 🌍 `linear-2026-10-11-eu-region` — EU data residency — *platform, shipped, enterprise*

**Promoted (1)**
- ✅ `linear-2026-09-22-graphs` moved beta → shipped (now in Pro+)

**Deprecated (0)**
- (none)

**Tier shifts (1)**
- ⚠️ `linear-public-api-v1` previously `all` → now `pro+` (monetized!)

**AI signals this week: 2 new** (Cmd-K AI beta, public-API AI endpoint teaser)
```

**Multi-competitor roll-up:**

```markdown
# Competitive Feature Digest — Week of 2026-10-06

**Tracked:** Linear, Height, Notion  •  **Active competitors:** 3

## 🏆 Top moves (Critical)
- **Linear** — Issues v2 redesign (their biggest UI rewrite since 2024)
- **Notion** — Voice commands beta (enters a category nobody else has)

## ⚠️ Notable
- **Height** — Shipped custom fields v3 (parity with Linear)
- **Linear** — Monetized public API (free → Pro+)

## 🧭 Trend across vendors
- **AI** — 4 new AI features this week across the 3 vendors (Cmd-K, suggestions, smart-search, voice)
- **Integrations** — Slack, GitHub, Figma all extended with bidirectional sync
- **Pricing-tier reshuffles** — 2 vendors moved free features up-tier

## 📊 Your gaps (auto-detected)
- ❌ You have no `ai` features; 3/3 competitors now ship one
- ❌ You have no `mobile` features; 2/3 do
- ✅ You are the only one with `audit log export` at Ent tier (defensible niche)
```

### Step 7: Cron for Automatic Tracking

```bash
# ~/.hermes/cron/competitor-features.yaml
name: weekly-competitor-features
schedule: "0 9 * * 1"          # Mondays 9am
prompt: |
  Run competitor-feature-tracker on the watchlist at
  ~/research/competitor-features/watchlist.yaml.
  Compare against the last snapshot, generate the weekly diff report,
  append to ~/research/competitor-features/digest/weekly/YYYY-WW.md,
  and post the roll-up to my morning briefing.
```

The skill is **idempotent** — every run appends a new dated snapshot, never overwrites history.

## Example Invocations

### Example 1 — New founder, just defined watchlist

> *"I'm building an AI project management tool. Track Linear, Height, and Asana for me. Build a feature matrix and show me where I'm behind."*

**Agent response:**

1. Creates `~/research/competitor-features/watchlist.yaml` with Linear, Height, Asana + resolved changelog URLs.
2. Pulls current changelogs (last 90 days) for all three.
3. Asks the user for their own product's feature list (or accepts a YAML).
4. Generates the feature matrix, populates their column, calls out gaps.
5. Saves a baseline snapshot dated 2026-10-12.

### Example 2 — Weekly automated cron

> *"Set up a weekly changelog digest for Linear, Notion, and Coda. I want to see only what changed since last week."*

**Agent response:**

1. Writes `~/.hermes/cron/competitor-features-weekly.yaml`.
2. Stores the baseline in `~/research/competitor-features/`.
3. On Monday 9am: pulls the latest changelogs, diffs against the prior Monday's snapshot, posts a 3-vendor roll-up to the user's `daily-briefing`.

### Example 3 — Targeted gap query

> *"Did any project-management tool ship a 'voice commands' feature in the last 60 days?"*

**Agent response:**

1. Searches all 3 vendors' changelogs and blogs for `voice`, `voice commands`, `speak`, `transcribe`.
2. Cross-references with X/Twitter (`from:linear`, `from:notion`, `from:height`) and Product Hunt.
3. Returns a 1-line answer + cited sources: *"Yes — Notion shipped 'Voice commands' (beta) on 2026-10-09."* with a link.

### Example 4 — Defensive move

> *"We just launched 'audit log export' at the Enterprise tier. Who else has this, and on what tier?"*

**Agent response:**

1. Searches every competitor for `audit log`, `export`, `compliance`, `SOC 2`, `immutable log`.
2. Returns a mini-matrix: `Linear: Ent`, `Height: Ent`, `Notion: Ent`, `Asana: Pro+`.
3. Conclusion: *"You are at parity on the high end, but Asana ships it cheaper (Pro vs Ent). Your differentiator is not 'having' the feature, it's the export format / retention window."*

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Changelog URL 404s or redirects | Try the alternate paths (`/releases`, `/whats-new`, `/updates`, `/news`); fall back to blog search `site:{domain} changelog` |
| SPA changelog renders blank via `curl` | Use a headless browser (Playwright/Chromium) or scrape the JSON behind `/api/changelog` if exposed |
| Competitor merges many tiny changes into one bullet | Split by feature verb: each verb = one feature record. *"Faster sync, new keyboard shortcuts, dark mode"* = 3 records |
| Two vendors use the same word for different things | The `category` enum enforces apples-to-apples. Always set category + status; reject "unspecified" |
| Feature shipped but only on Enterprise | Always capture `tier` — never let "shipped" hide the gating. A Pro+ ship ≠ an All-tier ship |
| New vendor added to watchlist mid-quarter | Run a **cold-start sweep** (last 90 days of changelog) before the first diff; without it, week-1 has no "added" because everything is "first-seen" |
| AI-washing / vague "AI-powered" claims | Tag `ai_related: true` only if the changelog names the model, capability, or use-case. Otherwise note in `notes` for follow-up |
| Deprecation hides a feature still in the UI | Cross-check the live product page (`/features`, `/docs`) — some "deprecated" features linger for quarters |
| You chase every feature a competitor ships | The matrix has a `notes` column for **strategic intent** ("do we need parity?"). Not every shipped feature deserves a response |
| Changelog only in foreign language | Translate before extracting; keep the original URL in `sources` so the user can verify |

## Verification Checklist

Before delivering any report, the agent should confirm:

- [ ] All `competitor-news-monitor` overlap avoided — this skill tracks **features**, that one tracks **news** (funding, hires, partnerships)
- [ ] Every feature record has: `id`, `competitor`, `first_seen`, `category`, `status`, `tier`, `sources[]`
- [ ] Sources are real URLs, not invented ones — verify the page exists before citing
- [ ] "New this week" count matches the actual `added` set in the diff (not 0 when there were changes)
- [ ] Feature matrix has at least one column for the user's own product (ask once, cache)
- [ ] Tier shifts are flagged explicitly — these are the highest-signal changes
- [ ] AI-related features are tagged so they can be filtered out / drilled into
- [ ] Snapshots are stored under `~/research/competitor-features/{competitor}/history/` with date-stamped filenames
- [ ] Watchlist is editable as a single YAML file at `~/research/competitor-features/watchlist.yaml`
- [ ] Cron output is appended, never overwriting prior weekly digests

## Data Sources & Accuracy

| Source | Reliability | When to use |
|--------|------------|-------------|
| Official changelog / release notes | **High** | Primary source for any feature claim |
| Official blog post | High | Tie a changelog entry to a launch narrative |
| Docs update | High | Catch new flags, params, or API endpoints |
| GitHub Releases | High | OSS tools — usually the most accurate source |
| Founder / PM tweet | Medium | Early signal — confirm against the changelog within 7 days |
| Product Hunt launch | Medium | Big launches only; usually pre-announced on the changelog |
| Reddit / HN / X mentions | Low | Lead-generation only — always cross-check the official source |
| G2 / Capterra recent reviews | Low | Useful for "users are seeing this feature" — verify before claiming it shipped |
| Status page incidents | Medium (inverted) | New infra / region launches sometimes appear as regional incidents first |

**Accuracy rules:**

1. **One canonical URL per feature claim** — usually the changelog entry, falling back to the blog post.
2. **Date stamp = first-seen date in the watchlist**, not the date the vendor claims they shipped (those often lag by days).
3. **Never fabricate a feature that doesn't appear in a citable source** — if you can't find it, mark it `planned` only when the vendor announced it on their own roadmap.
4. **Quote ≤15 words verbatim** from the changelog for the `summary`; paraphrase beyond that. Always link the source.
5. **Confidence note**: changelogs that are written by the vendor are reliable for *what shipped* but unreliable for *why it matters* — that judgment belongs to the agent's strategic layer, not the changelog text.

---

*Pairs well with: `competitor-news-monitor` (news/people/funding), `product-pricing-tracker` (pricing), `market-sizing` (TAM/SAM), `local-competitive-analysis` (offline SWOT), `business-plan-generator` (positioning), `daily-briefing` (weekly delivery slot), `weekly-review` (strategic reflection).*
