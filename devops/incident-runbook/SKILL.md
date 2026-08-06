---
name: incident-runbook
description: "Run a structured incident response from chat — severity classification, timeline, hypothesis tree, mitigation checklist, status update templates, and a postmortem skeleton. Pairs with log-analyzer and website-health-monitor. Local Markdown storage."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [devops, sre, incident-response, on-call, postmortem, runbook, sev1, sev2, pagerduty, status-page, blameless, observability]
    related_skills: [log-analyzer, website-health-monitor, cron-pipeline-builder, ai-cost-tracker, decision-journal]
---

# Incident Runbook (事件响应手册)

> When production breaks, panic is the enemy. This skill turns chaotic "the site is down" moments into a disciplined response — a clean hypothesis ladder, a live timeline, a status-page draft, and a blameless postmortem — all driven from chat.

---

## Overview

Every on-call engineer eventually lives this scene: it's 2:47 AM, the page fires, and you need to figure out *what broke*, *how bad it is*, *who to tell*, and *how to fix it* — usually in that order, usually in parallel. This skill gives Hermes the muscle memory of a seasoned SRE: ask the right triage questions first, classify severity by blast radius (not just by alarm), build a hypothesis tree instead of guessing, write status updates that don't lie, and end with a postmortem skeleton that's actually useful for prevention.

Everything is stored locally as Markdown so the incident log survives even if your SaaS tools are down — which, ironically, is when you need them most.

| Capability | What it does | When it helps |
|------------|--------------|---------------|
| **Severity classification** | Maps symptom → SEV1/SEV2/SEV3 by user-impact, blast radius, and revenue | First 60 seconds |
| **Triage questionnaire** | Asks the 6 must-know questions before you touch anything | First 5 minutes |
| **Hypothesis tree** | Ranks possible causes by likelihood + ease-of-check | First 15 minutes |
| **Live timeline** | Auto-records T0, mitigations, customer comms | Throughout |
| **Status update templates** | Pre-written customer-facing, internal, and exec drafts | Every 30 min during incident |
| **Mitigation checklist** | Common fixes (rollback, drain, restart, scale, feature-flag) | Active mitigation phase |
| **Postmortem skeleton** | Blameless timeline + 5-Whys + action items | Within 48h of resolution |
| **Local archive** | All artifacts in `~/incidents/{incident-id}/` | Survives outages |

---

## When to Use

- User says: *"Stripe webhook is returning 500s, customers are complaining"*
- User says: *"Site is down — help me triage"*
- User says: *"We're getting paged, walk me through the runbook"*
- User says: *"Help me write an incident postmortem for last Tuesday's outage"*
- User says: *"Database CPU is at 98%, is this SEV1?"*
- User says: *"Write a status page update — we're seeing elevated latency"*
- User says: *"Generate the customer-facing incident report for last night's 47-min outage"*
- User says: *"I need to roll back a deploy — give me the checklist"*
- User says: *"Help me run a blameless postmortem — same incident broke twice in a month"*

Do NOT use for: long-term architectural post-mortems (use `decision-journal` instead), routine maintenance (use `home-maintenance-tracker`), or non-incident debugging where time pressure isn't there.

---

## Core Workflow

### Step 1: Capture the Incident ID & Open the Workspace

Every incident gets a short ID (`INC-YYYYMMDD-NN`) and a dedicated folder. Use date + sequential count.

```bash
# Create workspace
INC_ID="INC-$(date +%Y%m%d)-01"
INC_DIR="$HOME/incidents/$INC_ID"
mkdir -p "$INC_DIR"/{logs,comms,artifacts}

# Initialize incident log
T0=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
cat > "$INC_DIR/incident.md" <<EOF
# Incident: $INC_ID

**Status:** OPEN
**T0 (first detected):** $T0
**Severity:** TBD
**Incident Commander:** $(whoami)
**Declared by:** TBD

## Timeline
- $T0 — Incident opened

## Hypotheses
- TBD

## Mitigations Applied
- TBD

## Status Updates Sent
- TBD

EOF
echo "Workspace: $INC_DIR"
```

### Step 2: Triage — Ask the 6 Must-Know Questions

Before touching anything, force the responder (or yourself) to answer these. They prevent 80% of "fix the wrong thing" mistakes.

1. **What is the user-visible symptom?** (e.g., "checkout returns 500", "login slow", "dashboard blank")
2. **When did it start?** (exact T0 from alarms, not when you noticed)
3. **What is the blast radius?** (1 user? 1%? 50%? all users? which region/segment?)
4. **What changed recently?** (deploy, config change, infra change, third-party status)
5. **Is it getting better, worse, or stable?** (trend over the last 5–15 minutes)
6. **Is there a workaround?** (rollback? feature flag? failover? drain?)

Use this script-style prompt template when triaging with the user:

```text
"Run incident triage:
  Symptom: <paste alert>
  Detected at: <time>
  Recent changes: <deploys, configs, or 'none known'>
  Affected scope: <users/region/feature>
  Trend: <getting worse/stable/intermittent>
"
```

Then Hermes will:
- Classify severity (SEV1/SEV2/SEV3) using the matrix below
- Generate 3–5 ranked hypotheses
- Suggest the cheapest first check for each hypothesis

**Severity matrix (use this exact rubric):**

| Severity | User Impact | Blast Radius | Response Time | Examples |
|----------|-------------|--------------|---------------|----------|
| **SEV1** | Complete outage OR data loss OR security breach | >25% of users OR all paying customers OR revenue-critical path | Page everyone, war room in 15 min | Total site down, payments failing, breach in progress |
| **SEV2** | Major degradation OR partial outage | 5–25% of users OR single critical feature broken | Page on-call + 1 backup, fix in 1h | Checkout broken for new users, search returns empty, 50% error rate on API |
| **SEV3** | Minor degradation | <5% of users OR non-critical feature OR workaround exists | Business hours fix | Slow dashboard for one tenant, cosmetic bug, single endpoint 503 |
| **SEV4** | Internal-only | No customer impact | Backlog | Dev environment down, flaky test |

### Step 3: Build the Hypothesis Tree

Don't guess. Branch outward from most likely → least likely, weighted by:
- **Likelihood** × **Ease of check** (cheap wins first)
- **Recent change correlation** (deploys, config pushes, infra events in last 24h)

Always start with the cheapest, fastest signal:

```text
Hypothesis Tree (rank by cheap-to-check):
1. (HIGH × CHEAP) Recent deploy broke it → check `git log --since="4h ago" --oneline` + rollback button
2. (HIGH × CHEAP) External dependency down → check status pages (Stripe, AWS, Cloudflare, OpenAI, DB vendor)
3. (MED × CHEAP) Resource exhaustion (CPU/mem/disk/conn) → check dashboards in 30 sec
4. (MED × MED) Bad config / secret rotation → diff current config vs last-known-good
5. (LOW × EXPENSIVE) Data corruption / migration bug → only after others ruled out
```

For each hypothesis, append to `incident.md`:

```bash
cat >> "$INC_DIR/incident.md" <<EOF

## Hypotheses (ranked)
1. **[H1] Recent deploy regression** — likelihood: HIGH, check: \`git log --since="4h ago"\` + diff last deploy
2. **[H2] External dep down** — likelihood: HIGH, check: status.{stripe,aws,cloudflare}.com
3. **[H3] Resource exhaustion** — likelihood: MED, check: \`htop\`, \`df -h\`, DB connection count
EOF
```

### Step 4: Run Mitigations & Record Timeline

Every action gets a timestamped line in `incident.md`. This is your single source of truth.

Common mitigations (always copy/adapt, never invent):

| Mitigation | When to use | Risk | Speed |
|------------|-------------|------|-------|
| **Rollback deploy** | Suspect recent deploy, no DB migrations | Low (if no schema change) | 2–5 min |
| **Toggle feature flag** | Known feature, can isolate | Very low | 30 sec |
| **Scale up (HPA)** | CPU/mem/queue saturation | Low (cost) | 3–10 min |
| **Restart pods/instances** | Memory leak, stuck connections | Medium (brief blip) | 1–3 min |
| **Drain traffic to healthy region** | Single-region issue | Medium | 5–15 min |
| **Failover DB / promote replica** | DB primary corrupt | HIGH (data risk) | 10–30 min |
| **Throttle / rate limit** | Cascading overload | Low | 1 min |
| **Cache-bypass** | Stale cache poisoning | Low | 2 min |

Append each mitigation:

```bash
T_NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "- $T_NOW — Mitigation applied: rollback to v2.4.1 (assumes H1)" >> "$INC_DIR/incident.md"
```

### Step 5: Write Status Updates

The hardest part. Keep them honest, brief, and frequent. Provide 3 templates:

**Customer-facing (status page):**

```text
[INVESTIGATING] We are investigating reports of errors affecting <feature>.
We will provide an update in <30 minutes> or as soon as we have more information.
Posted: <timestamp>
```

```text
[IDENTIFIED] The issue has been identified as <one-sentence root cause>.
Our team is deploying a fix. Customers may experience <brief impact description>.
ETA to resolution: <X minutes>.
Posted: <timestamp>
```

```text
[RESOLVED] This incident is resolved as of <timestamp>.
Total duration: <X minutes>.
Affected: <% of users> experienced <symptom>.
A full postmortem will be published within 5 business days.
Posted: <timestamp>
```

**Internal (Slack #incidents):**

```text
:red_circle: *SEV2 — INC-20260104-01*
*Symptom:* checkout returns 500
*T0:* 14:23 UTC
*Affected:* ~12% of new checkouts (us-east-1)
*Current hypothesis:* H1 — recent deploy v2.5.0
*Action:* rolling back to v2.4.1
*Next update:* 14:55 UTC
```

**Exec (only for SEV1/SEV2 lasting >30 min):**

```text
SEV1 — payment processing outage
Started: 14:23 UTC | Duration so far: 42 min
Customer impact: ~30% of US checkouts failing
Root cause: suspected deploy v2.5.0 — rolling back
Revenue at risk: ~$XK/hour (rough estimate)
Next update: 15:15 UTC
```

Save each to `$INC_DIR/comms/`:

```bash
echo "$STATUS_TEXT" > "$INC_DIR/comms/status-update-$(date +%H%M).txt"
```

### Step 6: Close Out & Generate Postmortem Skeleton

After mitigation confirmed (errors dropped, alerts green for 15+ min), close the incident and write the skeleton **within 24h while memory is fresh**. Use the blameless format:

```bash
T_RESOLVED=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$INC_DIR/postmortem.md" <<EOF
# Postmortem: $INC_ID

## Summary
- **Incident:** <one-sentence description>
- **Duration:** <X minutes>
- **Severity:** SEV?
- **Customer impact:** <X% of users, $Y revenue lost>
- **Root cause:** <one-sentence>

## Timeline (UTC)
- $T0 — First alert / first user report
- T+5 — On-call paged
- T+8 — Severity set to SEV?
- T+12 — Hypothesis ranked, mitigation started
- T+25 — Mitigation applied (rollback)
- T+35 — Errors dropped below threshold
- T+$T_DURATION — Resolved, monitoring

## Root Cause
<2-3 paragraphs. What actually broke and why.>

## Contributing Factors
- Process gap: e.g., "no automated rollback on error-rate spike"
- Tech debt: e.g., "single-region deployment made rollback risky"
- Visibility: e.g., "alert fired 4 min after user-visible impact"
- Communication: e.g., "no customer comms for first 18 min"

## What Went Well
- Fast detection by <alert source>
- Quick rollback decision
- Clean comms cadence (every 30 min)

## What Went Wrong
- Alert threshold too lenient
- Rollback runbook missing for this service
- Customer comm delayed

## 5-Whys (blameless)
1. Why did users see errors? → Bad deploy shipped to prod
2. Why was the bad deploy shipped? → Tests passed but didn't catch race condition
3. Why didn't tests catch it? → Integration test didn't simulate concurrent load
4. Why no concurrent load test? → CI pipeline only runs unit + smoke
5. Why no load test? → No team owner for the perf test suite

## Action Items
| Action | Owner | Priority | Due |
|--------|-------|----------|-----|
| Add concurrent integration test | @alice | P1 | +1 week |
| Tighten alert threshold to <2% errors | @bob | P1 | +3 days |
| Document rollback runbook for checkout-svc | @carol | P2 | +2 weeks |
| Add auto-rollback on error-rate spike | @dave | P2 | +1 month |

## Lessons Learned
- <bullet 1>
- <bullet 2>

EOF

echo "Postmortem skeleton: $INC_DIR/postmortem.md"
```

Then update `incident.md` status to CLOSED and append a one-line summary.

---

## Example Invocations

### Example 1 — Live Triage During an Outage

```
User: Stripe webhooks are returning 500s, payment team is pinging me, site still works.
      Help me triage.

Hermes:
  [EXEC] incident-runbook active. Opening INC-20260104-01.
  
  Asking 6 triage questions before we touch anything:
  1. What is the user-visible symptom? → Stripe webhooks 500
  2. When did it start? → ~14:23 UTC (when did the alarm fire?)
  3. What is the blast radius? → which webhook endpoint, % of payments affected?
  4. What changed recently? → any deploys / config pushes / Stripe SDK updates in last 24h?
  5. Trend? → getting worse / stable / intermittent?
  6. Workaround? → can we retry? disable the integration? switch to backup processor?
  
  Waiting on (3), (4), (5). Once I have them, I'll classify SEV and build the hypothesis tree.
  
  Workspace: ~/incidents/INC-20260104-01/
```

```
User: 3) only the subscriptions webhook, maybe 15% of renewals. 4) yes, deploy v3.2.0 at 14:05.
      5) stable, not getting worse. 6) yes, we can disable auto-renewal emails for now.

Hermes:
  [INFO] Severity: SEV2 — 15% of subscription renewals failing, no data loss, workaround available.
  
  Hypothesis tree (ranked by cheap-to-check × likelihood):
  1. [H1] Deploy v3.2.0 broke webhook signature validation → HIGH × CHEAP
     Check: `git diff v3.1.0..v3.2.0 -- src/webhooks/`
  2. [H2] Stripe API version mismatch → MED × CHEAP
     Check: `grep -r "api_version" src/`
  3. [H3] Stripe-side incident → MED × CHEAP
     Check: status.stripe.com
  
  Recommended first action: roll back to v3.1.0 (~2 min, reversible, low risk).
  
  Status update draft for #incidents Slack:
  :large_orange_diamond: *SEV2 — INC-20260104-01*
  Symptom: Stripe subscriptions webhook 500s
  Affected: ~15% of subscription renewals
  Hypothesis: H1 — deploy v3.2.0 at 14:05 UTC
  Action: rolling back to v3.1.0
  Workaround: auto-renewal emails disabled
  Next update: 14:55 UTC
  
  Want me to draft the status page text too, and execute the rollback?
```

### Example 2 — Status Page Update Drafting

```
User: Write a status page update — our search API latency spiked to 4s, affecting all US users,
      started 12 min ago, we just identified it as a bad Elasticsearch shard.

Hermes:
  [INFO] Drafting customer-facing status updates — 3 phases.
  
  [INVESTIGATING — posted 12 min ago, send NOW to update:]
  "We are investigating reports of elevated latency affecting search for US customers.
   Our team is actively working on this. Next update within 30 minutes."
  
  [IDENTIFIED — send after you confirm root cause:]
  "The issue has been identified as a corrupted shard in our search cluster.
   We are rerouting search traffic to healthy shards. Customers may continue to see
   slower search results for the next 5–10 minutes.
   ETA to resolution: 10 minutes."
  
  [RESOLVED — send after green for 15+ min:]
  "This incident is resolved as of 13:45 UTC. Total duration: 35 minutes.
   During this window, US customers experienced slower search results.
   A full postmortem will be published within 5 business days."
  
  Saved to: ~/incidents/INC-20260104-02/comms/status-update-{investigating,identified,resolved}.txt
  SEV2 classification — internal #incidents draft also ready.
```

### Example 3 — Postmortem from a Resolved Incident

```
User: Generate the postmortem for last Tuesday's 47-min checkout outage. I have the timeline
      in ~/incidents/INC-20251210-01/incident.md.

Hermes:
  [EXEC] Reading ~/incidents/INC-20251210-01/incident.md...
  
  Detected: SEV1, 47 min, deploy rollback, ~22% revenue impact.
  
  Generating blameless postmortem skeleton at ~/incidents/INC-20251210-01/postmortem.md.
  
  Pre-filled sections:
  ✓ Timeline (parsed 8 events from your notes)
  ✓ Severity classification (SEV1 — 22% revenue impact, >25 min)
  ✓ 5-Whys starter (deploy skipped staging soak time)
  ✓ Action items table (5 items, owners needed)
  
  Sections for you to fill:
  - Root cause narrative (2-3 paragraphs, what actually broke)
  - What went well / what went wrong (subjective)
  - Lessons learned (1-3 takeaways)
  
  3 questions to refine the action items:
  1. Who owns the "add canary deploys" action? (P1, +2 weeks)
  2. Should "tighten rollback SLO to <5min" be P1 or P2?
  3. Any contributing factors I missed (third-party deps, traffic spike, etc.)?
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Severity declared too high → war-room everyone for a small bug | Use the severity matrix: blast radius + duration + revenue. SEV1 = >25% users OR all paying OR revenue-critical. Don't guess. |
| Severity declared too low → missed SLA breach | Default to ONE level higher than your gut, then downgrade after 15 min of data. Easier to relax than to escalate mid-incident. |
| No T0 recorded → can't compute MTTR, no SLA evidence | First action in `incident.md` is always `$T0 = date -u`. Even a rough estimate is better than nothing. |
| Jumping straight to "restart everything" without hypotheses | Always Step 2 first. "Have you tried turning it off and on again" without a hypothesis hides the real cause. |
| Rolling forward a "fix" instead of rolling back the deploy | Rule of thumb: during incident, only roll back, never roll forward. Forward fixes ship after the postmortem. |
| Status updates written in jargon ("elevated 5xx in us-east-1c auth pool") | Customer-facing = plain English: "Some users may see errors when logging in." Internal = technical. Never the reverse. |
| Postmortem skipped because "we're busy shipping features" | The postmortem is the only thing that prevents the same incident recurring. Block 30 min on calendar within 24h. Non-negotiable for SEV1/SEV2. |
| Postmortem turns into blame ("@alice broke it with her deploy") | Blameless language: "the deploy" not "@alice's deploy". Ask "what about the system let this happen?" not "who did this?" |
| Action items without owners or due dates → nothing happens | Every action item: owner + priority (P1/P2/P3) + due date. Review at next incident retro. |
| Working directory inside an outage-affected filesystem | Always write to `~/incidents/` (your local home), NOT to a remote share that might be the source of the outage. |
| Time fields in local timezone → confusing when comparing to vendor logs | Always UTC: `date -u +"%Y-%m-%dT%H:%M:%SZ"`. Trust me. |
| Incident "closed" before monitoring for 30+ min | Resolution requires: errors <threshold for 15 min AND no new alerts AND customer comms sent. Premature closing = silent re-incident. |

---

## Verification Checklist

Before claiming the incident is closed, confirm:

- [ ] All 6 triage questions answered and recorded in `incident.md`
- [ ] Severity classified using the rubric (matrix above), not by gut
- [ ] Hypothesis tree written with at least 3 ranked hypotheses
- [ ] Each hypothesis has a cheap "first check" command
- [ ] Timeline records every: detection, escalation, mitigation, comm, resolution event
- [ ] At least one customer-facing status update sent during the incident (if SEV1/SEV2)
- [ ] Internal `#incidents` update sent every 30 min during active incident
- [ ] Mitigation was rolled BACK, not rolled FORWARD (with rare exception)
- [ ] All actions append-only to `incident.md` (never edit/delete past entries)
- [ ] Incident folder archived: `~/incidents/{ID}/` with `incident.md`, `postmortem.md`, `comms/`, `logs/`
- [ ] Postmortem skeleton written within 48h with: timeline, root cause, 5-Whys, action items (owners + due dates)
- [ ] Action items filed as tickets/issues with priorities
- [ ] Lessons-learned section has 1–3 actionable takeaways (not platitudes)
- [ ] Blameless language throughout — no individual blame, system focus
- [ ] Incident closed in any external tools (PagerDuty, Statuspage, Jira)

---

## Data Sources & Accuracy

**All data is local and human-typed — no automatic scraping.** This skill is a structured workflow + templates, not a data collector. Everything you produce lives in `~/incidents/`.

| Source | Type | Reliability |
|--------|------|-------------|
| User-reported symptoms, timestamps, deploy IDs | Firsthand | High (but biased — what they noticed) |
| `git log`, `kubectl get events`, deployment records | Firsthand | Very high (ground truth) |
| External status pages (Stripe, AWS, Cloudflare, vendor) | Third-party | High — but check within incident window |
| Application metrics (Datadog, Grafana, CloudWatch) | Firsthand observability | Very high — primary signal |
| Log files (read via `log-analyzer` skill) | Firsthand | High when correlated with timeline |

**Severity classification is opinionated** but follows widely-adopted SRE practice (similar to Google's SRE book and PagerDuty's SEV definitions). If your company has a formal SEV matrix, defer to that — adjust the matrix in Step 2 to match.

**Timestamps must be UTC** to stay consistent across vendors, vendors' status pages (often UTC), and your local team logs. Convert at display time if needed.

**The hypothesis tree is a heuristic, not a guarantee.** It ranks by "cheap to check × likely", not by scientific certainty. The goal is to find the real cause in <15 minutes, not exhaustively prove causation — that's the postmortem's job.

**Local storage** means your incident record survives even when the SaaS observability tools are down. Backup `~/incidents/` to git or encrypted cloud weekly so you don't lose institutional memory of past incidents.