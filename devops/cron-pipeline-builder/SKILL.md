---
name: cron-pipeline-builder
description: "Use when setting up automated data pipelines, recurring monitoring tasks, or chained workflows using Hermes cron. Covers job scheduling, watchdog scripts, job chaining with context_from, delivery routing, and job lifecycle management."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [cron, pipeline, automation, scheduling, monitoring, devops, workflow, watchdog]
    related_skills: [product-pricing-tracker, competitor-news-monitor, newsletter-digest, webhook-subscriptions]
---

# Cron Pipeline Builder

> Build automated data pipelines with Hermes cron — from simple recurring checks to multi-stage chained workflows that collect, process, and deliver without manual intervention.

---

## Overview

Hermes cron is a full-featured scheduler built into the agent. This skill teaches you how to use it like a pro — not just scheduling a single job, but building **pipelines**: chains of jobs where one feeds into the next, watchdog scripts that stay silent until something changes, and multi-channel delivery that routes the right data to the right place.

**Pipeline patterns covered:**
| Pattern | Description | Use Case |
|---------|-------------|----------|
| **Simple Recurring** | One job, one schedule | Daily news briefing |
| **Watchdog** | Script runs, stays silent if nothing changed | Price change detection |
| **Chained** | Job B uses Job A's output as input | Collect → Analyze → Report |
| **Fan-out** | One collector feeds multiple consumers | Data source → Multiple analyses |
| **Heartbeat** | Periodic "still alive" check | Service uptime monitoring |

---

## When to Use

- User asks: *"Check this pricing page every week and tell me if anything changed"*
- User asks: *"Set up a daily briefing of my competitors' news"*
- User asks: *"Monitor disk space and alert me when it's over 80%"*
- User asks: *"Scrape data then run analysis on it automatically"*
- User asks: *"Send a weekly summary to my Telegram every Monday"*
- User asks: *"Create a pipeline: crawl → process → report"*
- User asks: *"Cron job that stays quiet unless there's something to report"*

---

## Core Workflow

### Step 1: Understand the Cron Tool

The `cronjob` tool is your single entry point. It accepts these key parameters:

| Parameter | Purpose | Required? |
|-----------|---------|-----------|
| `action` | `create`, `list`, `update`, `pause`, `resume`, `remove`, `run` | ✅ Always |
| `schedule` | Cron expression, duration string, or ISO timestamp | ✅ On create |
| `prompt` | What the agent should do each tick | ✅ On create (unless `no_agent`) |
| `name` | Human-friendly label | Optional |
| `skills` | List of skills to load before running | Optional |
| `script` | Path to a script file (watchdog or collector) | Optional |
| `no_agent` | `true` = script-only, no LLM tokens burned | Default: false |
| `deliver` | Where to send the output | Auto-detects by default |
| `repeat` | Run N times then stop | Optional |
| `context_from` | Job IDs whose output feeds into this job's context | Optional |

### Step 2: Basic Recurring Job

The simplest pattern: one job, one schedule, direct delivery.

```
User: "Check HackerNews frontpage every day at 9 AM and summarize the top stories"
Hermes should:
  1. Create a cron job:
     cronjob(action='create', schedule='0 9 * * *',
             name='daily-hn-summary',
             prompt='Fetch HackerNews frontpage, summarize top 5 stories in a bullet list',
             skills=['web'])
  2. Confirm the job is created and active
```

**Schedule format reference:**
| Format | Meaning |
|--------|---------|
| `"30m"` | Every 30 minutes |
| `"every 2h"` | Every 2 hours |
| `"0 9 * * *"` | Daily at 9:00 AM |
| `"0 9 * * 1"` | Every Monday at 9:00 AM |
| `"2026-07-01T09:00:00"` | One shot on July 1st at 9 AM |

### Step 3: Watchdog Pattern (Silent Until Change)

This is the most efficient pattern for monitoring. The job runs a **script** that:
- **Stays silent** (empty stdout) when everything is normal — no tokens burned, no messages sent
- **Reports** only when the threshold is breached or something changed

**How it works:**
```
cronjob(
  action='create',
  schedule='every 1h',
  name='disk-watchdog',
  script='~/.hermes/scripts/disk-check.sh',   ← the script IS the check
  no_agent=True                                 ← no LLM involved, pure script
)
```

- `no_agent=True` → the scheduler runs the script directly. No LLM context, no token burn.
- **Empty stdout** → silent tick (nothing delivered to you).
- **Non-empty stdout** → output delivered as a message.
- **Non-zero exit / timeout** → error alert sent automatically.

#### Watchdog Script Template (Disk Space)

```bash
#!/bin/bash
# ~/.hermes/scripts/disk-check.sh
THRESHOLD=80
USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ "$USAGE" -gt "$THRESHOLD" ]; then
  echo "[WARN] Disk usage at ${USAGE}% — exceeds ${THRESHOLD}% threshold"
  df -h /
fi
# Silent when below threshold — nothing output, nothing delivered
```

#### Watchdog Script Template (Price Change)

```python
#!/usr/bin/env python3
# ~/.hermes/scripts/price-check.py
"""Compares current price against last snapshot. Silent if unchanged."""
import json, urllib.request, os

SNAPSHOT = os.path.expanduser("~/research/pricing/notion-baseline.json")
URL = "https://www.notion.so/pricing"

# Fetch current page
resp = urllib.request.urlopen(URL)
html = resp.read().decode()

# Extract price (simple pattern — real usage may need browser)
import re
prices = re.findall(r'\$(\d+)\s*/mo', html)
current = {"plans": [{"name": p} for p in prices]}

with open(SNAPSHET) as f:
    baseline = json.load(f)

if current != baseline:
    print(f"[CHANGE] Pricing structure changed at {URL}")
    print(json.dumps(current, indent=2))
    # Update baseline
    with open(SNAPSHOT, 'w') as f:
        json.dump(current, f, indent=2)
```

### Step 4: Chaining Jobs (context_from)

The real power: **chain jobs** so Job B automatically receives Job A's last output in its context.

```
Collector Job (A) ──context_from──▶ Analyzer Job (B) ──context_from──▶ Reporter Job (C)
```

**Two-step setup:**

```python
# Step 1: Create collector
cronjob(action='create',
        schedule='every 6h',
        name='reddit-collector',
        script='~/.hermes/scripts/collect-reddit.py',
        no_agent=True)

# Step 2: Note the returned job_id (say "job_abc123")
# Create analyzer that consumes collector's output
cronjob(action='create',
        schedule='every 6h',
        name='reddit-analyzer',
        prompt='Read the Reddit data from the collector job. Analyze sentiment and trending topics. Produce a summary report.',
        context_from=['job_abc123'])
```

**Important:** `context_from` injects the **most recent completed output** of the upstream job. There is no guarantee both run in the same tick — if Job A hasn't finished yet when Job B fires, Job B gets the last completed run's output.

#### Three-Stage Pipeline Example

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  📡 Collector       │     │  🧠 Analyzer        │     │  📬 Reporter        │
│  no_agent=True      │────▶│  Skills loaded      │────▶│  Delivers summary   │
│  Scrapes raw data   │     │  Processes + scores │     │  To Telegram/Discord│
│  Outputs JSON       │     │  Generates report   │     │  Clean & formatted  │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
      schedule: 6h                 schedule: 6h+5m          schedule: 6h+10m
```

Create order (collector → analyzer → reporter):

```bash
# 1. Collector — script-only, no agent
cronjob \
  action=create \
  schedule="0 */6 * * *" \
  name="news-collector" \
  script="~/.hermes/scripts/scrape-news.py" \
  no_agent=true

# 2. Analyzer — uses collector's output
cronjob \
  action=create \
  schedule="5 */6 * * *" \
  name="news-analyzer" \
  prompt="Analyze the raw data from context. Identify top stories, sentiment trends, and actionable insights." \
  context_from=["job_from_step_1"]

# 3. Reporter — uses analyzer's output, sends formatted briefing
cronjob \
  action=create \
  schedule="10 */6 * * *" \
  name="news-reporter" \
  prompt="Format the analysis into a clean daily briefing. Use markdown with sections for Top Stories, Trends, and Action Items." \
  context_from=["job_from_step_2"]
```

### Step 5: Delivery Routing

By default, cron job output delivers back to the **origin conversation** (where the job was created). Override with `deliver`:

| Value | Behavior |
|-------|----------|
| `"origin"` (default) | Deliver back to where it was created |
| `"local"` | Save only, no delivery |
| `"all"` | Fan out to every connected home channel |
| `"telegram:-1001234567890:17585"` | Specific Telegram chat + thread |
| `"discord:#engineering"` | Specific Discord channel |
| `"origin,all"` | Origin channel + all connected homes |

```bash
# Deliver weekly report to Telegram AND Discord
cronjob \
  action=create \
  schedule="0 9 * * 1" \
  name="weekly-briefing" \
  prompt="Generate this week's industry briefing..." \
  deliver="telegram:-1001234567890,origin"
```

### Step 6: Job Lifecycle Management

```bash
# List all jobs
cronjob action=list

# Pause a job (stops execution but preserves config)
cronjob action=pause job_id="job_abc123"

# Resume
cronjob action=resume job_id="job_abc123"

# Run once immediately (for testing)
cronjob action=run job_id="job_abc123"

# Update — change schedule, prompt, or skills
cronjob action=update job_id="job_abc123" schedule="0 9 * * *" prompt="New prompt..."

# Remove permanently
cronjob action=remove job_id="job_abc123"

# Clear context_from chain
cronjob action=update job_id="job_abc123" context_from=[]
```

### Step 7: Working with Skills in Cron

Skills load specialized knowledge into the cron run. The agent loads them in order before executing the prompt.

```bash
# Competitor news monitor — uses 2 skills
cronjob \
  action=create \
  schedule="0 8 * * 1" \
  name="monday-competitors" \
  prompt="Run competitor monitoring on OpenAI, Anthropic, and Google. Generate structured briefing." \
  skills=["competitor-news-monitor", "local-competitive-analysis"]
```

**Performance tip:** Use `enabled_toolsets` to restrict tools when your job doesn't need the full toolkit:

```bash
# Web-only job — no terminal, no filesystem needed
cronjob \
  action=create \
  schedule="0 9 * * *" \
  name="web-only-check" \
  prompt="Check {url} for changes" \
  enabled_toolsets=["web"]
```

Available toolsets: `web`, `terminal`, `file`, `browser`, `search`, `delegation`, `skills`, `vision`, `image_gen`, `video_gen`, `computer_use`, `x_search`

### Step 8: Model Override

Set a specific model for a cron job (useful for cost control — use cheaper models for routine checks):

```bash
# Use cheap model for daily checks
cronjob \
  action=create \
  schedule="0 9 * * *" \
  name="cheap-daily-check" \
  prompt="Quick check..." \
  model={provider: "openrouter", model: "deepseek/deepseek-chat"}
```

Omit `provider` to pin whatever provider is active at creation time. This prevents the job from breaking if you switch providers later.

---

## Complete Pipeline Examples

### Example 1: Competitor Price Watchdog

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│  Price Watchdog             │     │  Weekly Report              │
│  no_agent=True              │────▶│  Agent-driven               │
│  Runs every 1h              │     │  Runs every Monday 9AM      │
│  Silent unless price changed│     │  Summarizes all changes     │
└─────────────────────────────┘     └─────────────────────────────┘
```

```python
# Step 1: Create the watchdog script
write_file("~/.hermes/scripts/price-watch.py", """#!/usr/bin/env python3
\"\"\"Silent watchdog: compares current pricing to baseline. Reports only on change.\"\"\"
import json, os, re, urllib.request

PRODUCT = "notion"
URL = "https://www.notion.so/pricing"
DIR = os.path.expanduser(f"~/research/pricing-tracker/{PRODUCT}")
os.makedirs(DIR, exist_ok=True)
SNAPSHOT = f"{DIR}/current.json"
HISTORY = f"{DIR}/history"

resp = urllib.request.urlopen(URL)
html = resp.read().decode()
prices = re.findall(r'(\\$[\\d,]+(?:\\\\.\\d{2})?\\s*(?:/mo|/year|/yr)?)', html)
# Use regex in actual implementation
current = {"product": PRODUCT, "url": URL, "scraped": True}

if os.path.exists(SNAPSHOT):
    with open(SNAPSHOT) as f:
        baseline = json.load(f)
    if current != baseline:
        print(f"[CHANGE] {PRODUCT} pricing changed!")
        print(f"  Before: {json.dumps(baseline, indent=2)}")
        print(f"  After:  {json.dumps(current, indent=2)}")
        # Archive old snapshot
        with open(f"{HISTORY}/{int(os.path.getmtime(SNAPSHOT))}.json", 'w') as f:
            json.dump(baseline, f)
else:
    print(f"[INFO] Baseline created for {PRODUCT}")

with open(SNAPSHOT, 'w') as f:
    json.dump(current, f, indent=2)
""")
```

### Example 2: Daily Newsletter Pipeline

```
Collect: Scrape 5 sources ──▶ Analyze: Summarize + classify ──▶ Deliver: Formatted email/social
```

```bash
# Collector — every morning at 7AM
cronjob action=create schedule="0 7 * * *" name="news-collector" no_agent=true script="~/.hermes/scripts/news-collector.sh"

# Analyzer — 5 minutes later, reads collector output
cronjob action=create schedule="5 7 * * *" name="news-analyzer" \
  prompt="I have raw news data from context. Categorize into tech/business/ai, summarize each article in 2-3 sentences, rank by importance." \
  context_from=["<collector_job_id>"]

# Reporter — 10 minutes later, formats and delivers
cronjob action=create schedule="10 7 * * *" name="news-reporter" \
  prompt="Format the analysis into a clean daily newsletter with sections, emoji headers, and a good-morning greeting." \
  context_from=["<analyzer_job_id>"] \
  deliver="all"
```

### Example 3: Service Uptime Heartbeat

```bash
# Heartbeat script — stays silent when healthy
cat > ~/.hermes/scripts/heartbeat.sh << 'SCRIPT'
#!/bin/bash
URL="$1"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")
if [ "$STATUS" != "200" ]; then
  echo "[ALERT] $URL returned HTTP $STATUS"
fi
SCRIPT

cronjob action=create schedule="every 5m" name="bridge-social-heartbeat" no_agent=true \
  script="~/.hermes/scripts/heartbeat.sh https://bridge-social.com"
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Job created but never fires.** | Check schedule syntax. "every 6h" works, "6h" does not. Use `cronjob action=list` to verify. |
| 2 | **Watchdog reports every time (never silent).** | Your script always outputs something. Debug: run `bash script.sh` manually — if it always prints, it always delivers. Empty stdout = silent tick. |
| 3 | **context_from not working as expected.** | Remember: injects the *most recent completed* output. If Job A never ran, Job B gets empty context. Always create upstream jobs first and note their IDs. |
| 4 | **Cron job uses wrong model / costs too much.** | Set `model={provider, model}` to pin a cheaper model. Or use `no_agent=True` for pure-script jobs. |
| 5 | **Job stopped but I don't know why.** | Check `cronjob action=list` for status. Non-zero exit sends an error alert. Check script for crashes. |
| 6 | **Can't find a job ID.** | `cronjob action=list` shows all jobs with IDs. Do NOT guess or fabricate IDs. |
| 7 | **Time zones.** | Cron expressions use the server's timezone (typically UTC). Adjust accordingly or use relative durations like `"every 8h"`. |
| 8 | **Job output too long / spammy.** | Use `no_agent=True` with a well-designed script that filters noise. Or chain: collector (silent) → reporter (compact). |
| 9 | **Skills not loading in cron.** | Verify skill is installed (`ls ~/.hermes/skills/<category>/<name>/SKILL.md`). Pass correct skill name string. |
| 10 | **Removing a job that's referenced by context_from.** | Other jobs referencing it will get empty context. Update those jobs first: `cronjob action=update job_id="..." context_from=[]`. |

---

## Verification Checklist

- [ ] Cron job created and visible in `cronjob action=list`
- [ ] Schedule format validated (not a common mistake: `0 9 * * *` works, not `0 9 ***`)
- [ ] For watchdog (`no_agent=True`): script tested manually — empty stdout when normal, output when triggered
- [ ] For chained jobs: upstream job IDs confirmed via `cronjob action=list`
- [ ] For watchdog: script made executable (`chmod +x`)
- [ ] Delivery target verified (receiving output where expected)
- [ ] Skills loaded by job actually exist (check `ls ~/.hermes/skills/`)
- [ ] Model override set if cost is a concern
- [ ] `enabled_toolsets` set if job has limited tool needs
- [ ] Pipeline timing staggered (5-10 min gaps so upstream finishes first)

---

## 📋 Data Sources & Accuracy

This skill does not collect or handle external data by itself — it orchestrates the infrastructure for automated data pipelines. The accuracy of pipeline output depends entirely on:

### Pipeline Accuracy Rules
1. **Scripts must be tested** before deploying as `no_agent=True` watchdogs — run `bash script.sh` manually and verify behavior
2. **Upstream jobs in a chain must finish before downstream fires** — stagger schedules by 5-10 minutes
3. **Watchdog silence is intentional** — an empty-output watchdog that never fires means no threshold was breached, not that the job failed
4. **Job timestamps are in UTC** — if you see output at unexpected local times, check the timezone mismatch
5. **Non-zero exits are alerted** — if a watchdog stops reporting, check `cronjob action=list` for error status
6. **Job output preserves script content precisely** — `no_agent=True` delivers stdout verbatim; there is no LLM reformatting or hallucination risk in the watchdog pattern

### Security Notes
- Scripts under `~/.hermes/scripts/` have filesystem access — do not write untrusted code
- Environment variables (API keys, tokens) are not automatically exposed to cron scripts — use absolute paths or source config explicitly
- `deliver="all"` fans out to every connected channel — test with `deliver="origin"` first

### Verification Checklist
- [ ] Scripts tested manually before deployment
- [ ] Pipeline stagger timing validated (no race conditions)
- [ ] Watchdog produces empty stdout in normal state
- [ ] Watchdog produces non-empty stdout when threshold breached
- [ ] Non-zero exit behavior understood (error alerted)
- [ ] delivery target confirmed
