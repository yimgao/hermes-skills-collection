---
name: website-health-monitor
description: "Monitor website availability, SSL expiry, response time, content changes, and DNS health. Cron-ready alerts."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [monitoring, uptime, ssl, dns, site-health, cron]
    related_skills: [cron-pipeline-builder, product-pricing-tracker]
---

# Website Health Monitor (网站健康监控)

Monitor one or more websites for uptime, performance, SSL certificate validity, DNS resolution, and content changes. Outputs a structured health report and supports cron-based periodic checks with alert thresholds.

## Overview

| Capability | Description |
|-----------|-------------|
| **Uptime Check** | HTTP HEAD/GET request - status code, redirect chain, final URL |
| **Response Time** | Total request duration in ms, with warning/critical thresholds |
| **SSL Certificate** | Expiry date, days remaining, issuer, SAN list |
| **DNS Resolution** | A/AAAA/CNAME records, resolution time, nameservers |
| **Content Change** | Hash comparison of page body against a stored baseline |
| **Batch Check** | Validate multiple URLs in one invocation - returns a summary table |

## When to Use

- You want to verify a deployment just went live before announcing it
- You need a weekly health check across your personal/project sites
- You want SSL expiry alerts before certs expire
- You are debugging a slow or flaky site and need timing data
- You want to detect content changes on a competitor or reference page
- You need to prove uptime during an incident post-mortem

## Core Workflow

### Step 1: Single Site Health Check

Ask Hermes to check a single URL:

User: "Check the health of https://example.com"

Hermes should:

1. Run `curl -sI -o /dev/null -w "%{http_code} %{time_total}" https://example.com` for status/timing
2. Run `curl -v https://example.com 2>&1 | grep -iE 'expire date|issuer|not after'` for SSL info
3. Run `dig +short example.com A` for DNS resolution
4. Compile results into a structured health table

Output template:

| Metric | Value | Status |
|--------|-------|--------|
| HTTP Status | 200 | OK |
| Response Time | 342ms | OK |
| SSL Expiry | 2026-09-15 (78 days) | Warning |
| DNS A Record | 93.184.216.34 | OK |
| Content Hash | a1b2c3d4... | Matches baseline |

### Step 2: Batch Health Report

User: "Check all the sites in sites.txt"

Hermes reads each URL from the file and runs the single-site check in a loop, then produces a summary markdown table sorted by status (failing sites first).

### Step 3: Deploy as Cron Job

User: "Set up a weekly site health monitor that checks my 3 sites every Monday at 9 AM and reports to me"

Use the cron-pipeline-builder skill. Store baseline hashes in ~/.hermes/data/site-metrics.json:

```json
{
  "https://example.com": {
    "baseline_hash": "sha256:a1b2c3...",
    "last_checked": "2026-06-29T09:00:00Z",
    "history": []
  }
}
```

The cron job should:
- Run health checks on schedule
- Compare against stored baselines
- If any metric exceeds thresholds (4xx/5xx, SSL under 30 days, response over 2000ms), flag as CRITICAL
- Return a health report as the cron job output

## Example Invocations

### Example 1: Quick deployment verification

**User:** "Check if my new blog at blog.yimgao.dev is live and healthy"

**Agent:**
```
[EXEC] curl -sI -o /dev/null -w "%{http_code} %{time_total}" https://blog.yimgao.dev
[INFO] HTTP 200 - 287ms
[EXEC] curl -v https://blog.yimgao.dev 2>&1 | grep -iE 'expire date|issuer'
[INFO] SSL: expires 2026-10-12 - issuer: Let's Encrypt
[EXEC] dig +short blog.yimgao.dev A
[INFO] DNS: 185.199.108.153 (Cloudflare)

Health Report - blog.yimgao.dev
- Status: 200 OK
- Response: 287ms OK
- SSL: 105 days remaining OK
- DNS: 1 record, 12ms OK
- Verdict: Healthy - site is live
```

### Example 2: SSL expiry audit across all domains

**User:** "Check SSL certs in my domains.txt - warn if any expires within 60 days"

**Agent:**
```
Processing 5 domains...
Domain              Days Left   Issuer
yimgao.com          184         Let's Encrypt
api.yimgao.com      47  WARN    Let's Encrypt
docs.yimgao.com     203         Cloudflare CA
blog.yimgao.dev     92          Let's Encrypt
status.yimgao.io    CONNECT_ERR -
WARNING: api.yimgao.com SSL expires in 47 days
CRITICAL: status.yimgao.io is unreachable
```

### Example 3: Daily batch health check with cron

**User:** "Monitor yimgao.com, api.yimgao.com, and docs.yimgao.com every morning at 8 AM"

**Agent:**
```
[INFO] Creating baseline for 3 sites...
[EXEC] curl ssl dns -> yimgao.com [200 - 412ms]
[EXEC] curl ssl dns -> api.yimgao.com [200 - 89ms]
[EXEC] curl ssl dns -> docs.yimgao.com [301 to 200 - 234ms]
[INFO] Baselines saved to ~/.hermes/data/site-metrics.json
[INFO] Setting up cron schedule: 0 8 * * *
[INFO] Cron job installed. Output delivered to @admin.
```

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| SSL info not returned by curl | Use `openssl s_client -connect host:443 -servername host 2>/dev/null </dev/null` for raw cert data |
| Redirect chain hides real status | Follow with `-L` flag: `curl -sL -o /dev/null -w "%{http_code}"` |
| DNS slow on first check | Use `dig +noall +answer` for faster parsing or add local cache |
| Content hash noise from dynamic pages | Hash a stable asset (CSS/JS) instead of full body |
| Rate limiting by target site | Add `-H "User-Agent: Mozilla/5.0"` and space checks 30s+ apart |
| Non-standard ports for SSL | Pass explicitly: `openssl s_client -connect host:8443` |

## Verification Checklist

- [ ] Single URL returns correct HTTP status, timing, SSL, DNS
- [ ] Batch check returns a sorted summary table
- [ ] SSL expiry correctly calculates days remaining
- [ ] Content hash correctly detects changes (add/remove an element to test)
- [ ] Cron pipeline runs without errors and delivers output
- [ ] Edge cases: invalid URL, timeout (30s), non-200 status, redirect chains
- [ ] Unreachable sites do not crash batch - logged as ERROR with context

## Data Sources and Accuracy

| Data Point | Tool | Accuracy |
|-----------|------|----------|
| HTTP Status / Timing | curl | Real-time - exact network measurement |
| SSL Certificate | curl -v or openssl s_client | Direct server response - accurate at check time |
| DNS Records | dig (system resolver) | Depends on local DNS cache TTL |
| Content Changes | SHA-256 hash of page body | Exact - any byte-level change detected |
| Response Time | curl -w "%{time_total}" | Sub-millisecond precision; varies by network path |
