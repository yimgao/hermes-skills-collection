---
name: log-analyzer
description: "Parse, filter, and analyze log files from any source — web servers, application logs, system logs, or custom formats. Extract error patterns, frequency distributions, timelines, and actionable summaries using grep, awk, sed, jq, and Python. No ELK stack needed."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [devops, logs, debugging, error-analysis, monitoring, grep, awk, syslog, nginx, troubleshooting, observability]
    related_skills: [website-health-monitor, cron-pipeline-builder, tech-stack-detector]
---

# Log Analyzer (日志分析器)

> Parse, filter, and surface actionable insights from logs without a full observability stack. Run queries, extract error patterns, generate timelines, and find needle-in-haystack issues using standard Unix tools and lightweight Python scripts.

---

## Overview

Every system produces logs — but extracting signal from noise is the hard part. This skill teaches Hermes how to analyze log files of any format, at any scale, using tools already on the machine. Whether it's a single nginx `access.log`, a multi-gigabyte syslog, a docker-compose log dump, or a stack trace from a crash, you can slice, aggregate, and summarize in seconds.

**Capabilities covered:**

| Capability | Tools Used | Typical Output |
|------------|-----------|----------------|
| **Format Detection** | `file`, `head`, pattern matching | Identifies nginx, Apache, syslog, JSON-Lines, Python traceback, CSV |
| **Time-range Filtering** | `awk`, `grep` with regex | Extract logs from a specific hour/day |
| **Error Extraction** | `grep -E`, `jq` | All ERROR/WARN/FATAL lines with context |
| **Frequency Analysis** | `awk`, `sort`, `uniq -c` | Top errors, top IPs, top endpoints, top users |
| **Timeline Bucketing** | `awk`, `cut` | Errors per minute/hour (for spike detection) |
| **Pattern Summary** | Python `re` module | Cluster similar errors, count occurrences |
| **Anomaly Detection** | Python + `collections.Counter` | Lines that deviate from normal pattern |
| **Traceback Collation** | Python | Group identical stack traces, show first occurrence |
| **JSON-Logs Query** | `jq` | Extract specific fields, filter by severity, build data table |

---

## When to Use

- User asks: *"What's going on with the server? Check the logs."*
- User asks: *"Find all 5xx errors in today's nginx log"*
- User asks: *"Are there spikes in errors over the last 24 hours?"*
- User asks: *"Summarize the application logs — what's the top error?"*
- User asks: *"Find the stack traces in this crash dump"*
- User asks: *"Check if there are any DDoS signs in the access log"*
- User asks: *"Is the database connection failing? Check the logs for 'connection refused'"*
- User asks: *"Can you analyze this docker-compose log output?"*
- User asks: *"Compare today's error rate with yesterday's"*

---

## Core Workflow

### Step 1: Detect Log Format and Structure

Always start by identifying the log format. This determines which tools and patterns to use.

```bash
# Quick format detection — first 5 lines + file type
head -5 /var/log/nginx/access.log
file /var/log/nginx/access.log
```

**Common log format signatures:**

| Format | Sample Line | Key Feature | Best Tool |
|--------|-------------|-------------|-----------|
| **nginx access** | `192.168.1.1 - - [03/Jul/2026:12:34:56 +0000] "GET /api/users HTTP/1.1" 200 1234` | IP + bracketed date + quoted method/URL + HTTP status + bytes | `grep`, `awk` |
| **Apache access** | `192.168.1.1 - frank [03/Jul/2026:12:34:56 -0700] "GET /index.html HTTP/1.1" 200 2326` | Combined log format + user field | `grep`, `awk` |
| **syslog** | `Jul  3 12:34:56 hostname sshd[1234]: Failed password for root from 10.0.0.1 port 22 ssh2` | Date + hostname + service[PID]: message | `grep -E`, `awk` |
| **JSON-lines** | `{"time":"2026-07-03T12:34:56Z","level":"ERROR","service":"api","message":"DB timeout"}` | One JSON object per line | `jq` |
| **Python traceback** | `Traceback (most recent call last):` then `  File "...", line N, in func` then `ErrorType: message` | Multi-line stack trace | Python `re` |
| **Docker compose logs** | `service_name  | 2026-07-03 12:34:56 ERROR DB connection timeout` | Pipe-delimited service name + color codes | `grep`, `sed` |

**Detection script (shell):**

```bash
detect_log_format() {
  local sample
  sample=$(head -3 "$1")
  if echo "$sample" | grep -q '^{.*"level"'; then
    echo "json-lines"
  elif echo "$sample" | grep -qE '^\S+ \S+ \S+ \S+ \['; then
    echo "nginx-access"
  elif echo "$sample" | grep -qE '^\S+ \S+ \S+ \[.*\] "GET|POST|PUT|DELETE'; then
    echo "apache-access"
  elif echo "$sample" | grep -qE '^[A-Z][a-z]{2}\s+\d+\s+\d+:\d+:\d+\s+\S+\s+\S+\['; then
    echo "syslog"
  elif echo "$sample" | grep -q 'Traceback (most recent call last)'; then
    echo "python-traceback"
  elif echo "$sample" | grep -qE '^\w+\s+\|\s+\d{4}-\d{2}-\d{2}'; then
    echo "docker-compose"
  else
    echo "unknown"
  fi
}
```

### Step 2: Filter by Time Range

Extract logs from a specific time window. Logs can be huge — always narrow the range first.

**For nginx/Apache (timestamps in brackets):**

```bash
# Extract log entries between 12:00 and 12:59 on July 3
grep '03/Jul/2026:12:' /var/log/nginx/access.log

# Between 12:30 and 12:59
grep -E '03/Jul/2026:12:[3-5][0-9]' /var/log/nginx/access.log

# Using awk for exact time comparison
awk -F'[:[]' '$5 >= "03/Jul/2026:12:00:00" && $5 <= "03/Jul/2026:14:00:00"' /var/log/nginx/access.log
```

**For syslog:**

```bash
# Yesterday's logs only
grep "$(date -d yesterday '+%b %e')" /var/log/syslog

# Specific service for last hour
awk -v d="$(date -d '1 hour ago' '+%b %e %H')" '$0 ~ d && /sshd/' /var/log/syslog
```

**For JSON-lines (using jq):**

```bash
# Filter by time range in ISO format
jq 'select(.time >= "2026-07-03T12:00:00Z" and .time <= "2026-07-03T13:00:00Z")' /var/log/app/*.log

# Filter by time and severity
jq 'select(.time >= "2026-07-03T12:00:00Z" and .level == "ERROR")' /var/log/app/*.log
```

### Step 3: Extract Errors and Issues

Once you have the time range, extract the signals.

**nginx — find all 4xx/5xx responses:**

```bash
# All 5xx errors
grep ' 5[0-9][0-9] ' /var/log/nginx/access.log

# Count by status code
grep -oE ' [45][0-9]{2} ' /var/log/nginx/access.log | sort | uniq -c | sort -rn

# Top 10 IPs generating 5xx errors
grep ' 5[0-9][0-9] ' /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# Top 10 endpoints returning errors
grep ' 5[0-9][0-9] ' /var/log/nginx/access.log | awk -F'"' '{print $2}' | awk '{print $2}' | sort | uniq -c | sort -rn | head -10

# Slow requests (response time > 5s, if $upstream_response_time is logged)
awk '$NF > 5' /var/log/nginx/access.log | head -20
```

**syslog — find common error patterns:**

```bash
# All errors in syslog
grep -iE 'error|fail|critical|denied|refused|timeout' /var/log/syslog

# Per-service error count
grep -i 'error' /var/log/syslog | awk '{for(i=5;i<=NF;i++){if($i~/\[/){print $i;break}}}' | tr -d '[' | sort | uniq -c | sort -rn

# SSH-related events
grep sshd /var/log/syslog | grep -iE 'failed|invalid|error|break-in'
```

**JSON-lines — deep query with jq:**

```bash
# Errors by service
jq -r 'select(.level == "ERROR") | .service' /var/log/app/*.log | sort | uniq -c | sort -rn

# Most frequent error messages
jq -r 'select(.level == "ERROR") | .message' /var/log/app/*.log | sort | uniq -c | sort -rn | head -20

# Error timeline (count by minute)
jq -r 'select(.level == "ERROR") | .time[:16]' /var/log/app/*.log | sort | uniq -c | sort -n

# Show full context of ERROR entries grouped by service
jq -r 'select(.level == "ERROR") | "[\(.time[:19])] [\(.service)] [\(.level)] \(.message)"' /var/log/app/*.log
```

### Step 4: Timeline and Trend Analysis

Understand *when* errors happen to spot spikes.

**Errors per minute (nginx):**

```bash
# Extract timestamp for each 5xx, truncate to minute, count
grep ' 5[0-9][0-9] ' /var/log/nginx/access.log | \
  grep -oE '\[[^]]+\]' | \
  sed 's/\[//;s/\]//' | \
  awk '{print $2}' | \
  cut -d: -f1-2 | \
  sort | uniq -c | sort -n | tail -20
```

**Errors per hour (syslog):**

```bash
grep -i 'error' /var/log/syslog | \
  awk '{print $3}' | \
  cut -d: -f1 | \
  sort | uniq -c | sort -n
```

**Python — timeline bucketing (works on any line-based log):**

```python
#!/usr/bin/env python3
"""Parse log, bucket errors by minute, detect spikes."""
import sys
import re
from collections import Counter
from datetime import datetime

def parse_timestamp(line, fmt):
    """Try to extract timestamp. Returns (datetime, rest) or None."""
    # Try nginx/apache format: [03/Jul/2026:12:34:56
    m = re.search(r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})', line)
    if m:
        return datetime.strptime(m.group(1), '%d/%b/%Y:%H:%M:%S')
    # Try ISO format: 2026-07-03T12:34:56
    m = re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})', line)
    if m:
        return datetime.fromisoformat(m.group(1))
    return None

buckets = Counter()
error_lines = []

for line in sys.stdin:
    ts = parse_timestamp(line)
    if not ts:
        continue
    bucket = ts.strftime('%Y-%m-%d %H:%M')  # per-minute
    buckets[bucket] += 1
    error_lines.append((ts, line.rstrip()))

# Print buckets
for bucket, count in sorted(buckets.items()):
    bar = '█' * min(count, 60)
    print(f"{bucket}  {count:4d}  {bar}")

# Detect spikes (buckets > 2 stddev above mean)
if buckets:
    counts = list(buckets.values())
    mean = sum(counts) / len(counts)
    variance = sum((c - mean) ** 2 for c in counts) / len(counts)
    stddev = variance ** 0.5
    threshold = mean + 2 * stddev
    print(f"\nMean: {mean:.1f}, StdDev: {stddev:.1f}, Spike threshold: {threshold:.1f}")
    for bucket, count in sorted(buckets.items()):
        if count > threshold:
            print(f"⚠️  SPIKE at {bucket}: {count} errors (threshold={threshold:.0f})")
```

### Step 5: Pattern Summary and Root Cause

Group similar errors to find the root cause, not just the symptom.

**Python — error clustering:**

```python
#!/usr/bin/env python3
"""Cluster similar error messages by prefix/template."""

import sys
import re
from collections import Counter

def get_error_type(line):
    """Extract error type from common formats."""
    # Python traceback
    m = re.search(r'(\w+Error|Exception|Fault|Failure):\s*', line)
    if m:
        return m.group(1)
    # ERROR level log with message
    m = re.search(r'\b(ERROR|FATAL|CRITICAL)\b\s*[:=-]?\s*(.+)', line, re.IGNORECASE)
    if m:
        # Normalize: replace variable parts (IPs, IDs, numbers)
        msg = m.group(2).strip()
        msg = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '{IP}', msg)
        msg = re.sub(r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b', '{UUID}', msg)
        msg = re.sub(r'\b\d{4,}\b', '{N}', msg)
        return msg[:120]  # truncate long messages
    # HTTP status codes
    m = re.search(r'\b(5\d{2}|4\d{2})\b', line)
    if m:
        return f"HTTP_{m.group(1)}"
    return None

errors = Counter()
for line in sys.stdin:
    etype = get_error_type(line)
    if etype:
        errors[etype] += 1

print("=== Error Pattern Summary ===")
for pattern, count in errors.most_common(30):
    print(f"{count:6d}  |  {pattern}")
print(f"\nTotal error lines classified: {sum(errors.values())}")
```

**Usage:**

```bash
# Pipe error lines into the classifier
grep ' 5[0-9][0-9] ' /var/log/nginx/access.log | python3 classify_errors.py

# Or from syslog
grep -i 'error' /var/log/syslog | python3 classify_errors.py

# Or from docker compose logs
cat docker-compose-logs.txt | grep ERROR | python3 classify_errors.py
```

### Step 6: Multi-file Analysis (Cron/CI logs, Journal, Docker)

**Docker container logs:**

```bash
# All containers, ERROR level only
docker logs my_container 2>&1 | grep -iE 'error|exception|traceback'

# Docker compose — specific service
docker compose logs api 2>&1 | grep -iE 'error|fatal'

# Since a specific time
docker logs --since "2026-07-03T12:00:00" my_container 2>&1 | grep -i error
```

**journalctl (systemd):**

```bash
# Recent errors
sudo journalctl -p err -n 50 --no-pager

# Since boot
sudo journalctl -p err -b --no-pager

# For a specific unit, last hour
sudo journalctl -u nginx.service --since "1 hour ago" -p err --no-pager

# Follow errors in real-time (for live debugging)
sudo journalctl -f -p err -u api.service
```

**Cron job logs:**

```bash
# Check cron output for Hermes jobs
grep -iE 'error|fail|timeout' ~/.hermes/logs/*.log

# Check recent cron runs
ls -lt ~/.hermes/logs/ | head -10
```

### Step 7: Compare with Baseline (Yesterday vs Today)

Detect regressions by comparing error rates over time.

```bash
# nginx — yesterday's vs today's 5xx rate
echo "=== Yesterday ==="
grep "$(date -d yesterday '+%d/%b/%Y')" /var/log/nginx/access.log | grep -c ' 5[0-9][0-9] '
echo "=== Today ==="
grep "$(date '+%d/%b/%Y')" /var/log/nginx/access.log | grep -c ' 5[0-9][0-9] '

# Compare top error IPs between two days
echo "=== Yesterday ==="
grep "$(date -d yesterday '+%d/%b/%Y')" /var/log/nginx/access.log | grep ' 5[0-9][0-9] ' | awk '{print $1}' | sort | uniq -c | sort -rn | head -5
echo "=== Today ==="
grep "$(date '+%d/%b/%Y')" /var/log/nginx/access.log | grep ' 5[0-9][0-9] ' | awk '{print $1}' | sort | uniq -c | sort -rn | head -5
```

---

## Example Invocations

### Example 1: Investigate a Production Error Spike

**User:** *"Our API is returning 500 errors, check nginx access.log for the last hour"*

**Agent should:**

```bash
# 1. Detect format and get recent errors
head -3 /var/log/nginx/access.log

# 2. Filter last hour
HOUR=$(date '+%d/%b/%Y:%H')
grep "$HOUR" /var/log/nginx/access.log > /tmp/recent-errors.log

# 3. Count 5xx
grep -c ' 5[0-9][0-9] ' /tmp/recent-errors.log

# 4. Top endpoints with errors
grep ' 5[0-9][0-9] ' /tmp/recent-errors.log | awk -F'"' '{print $2}' | awk '{print $2}' | sort | uniq -c | sort -rn | head -10

# 5. Show a few example 500 lines with full context
grep ' 500 ' /tmp/recent-errors.log | head -5

# 6. Slow upstream response times (if logged)
grep ' 500 ' /tmp/recent-errors.log | awk '{print $NF}' | sort -n | tail -5
```

**Typical diagnosis output:**

```
[LOG] Format: nginx access (combined)
[INFO] Last hour: 342 requests, 47 5xx (13.7% error rate)
[TREND] Top error endpoints:
  18  |  /api/payments/checkout
  12  |  /api/orders/batch
   8  |  /api/users/verify
   5  |  /api/health
[WARN] Upstream response times on 500s: avg 28.3s (indicates upstream timeout)
[SUGGEST] Check payments service — 38% of 500s go to /api/payments/*
```

### Example 2: Docker Compose Log Analysis

**User:** *"My microservice stack is failing. Check the docker compose logs for errors."*

**Agent should:**

```bash
# 1. Collect logs from all services
docker compose logs --tail=500 > /tmp/compose-logs.txt 2>&1

# 2. Count errors per service
grep -E '(ERROR|FATAL|Exception)' /tmp/compose-logs.txt | \
  sed 's/^\([^|]*\)|.*/\1/' | \
  sort | uniq -c | sort -rn

# 3. Show error messages grouped by service
for svc in $(docker compose ps --services); do
  count=$(grep "$svc" /tmp/compose-logs.txt | grep -c -iE 'error|fatal|exception')
  [ "$count" -gt 0 ] && echo "[$svc] $count errors"
done

# 4. For the service with most errors, show context
docker compose logs payment-service --tail=100 2>&1 | grep -iE 'error|exception' -A 3 -B 2

# 5. Check if there's a cascading failure (services failing in sequence)
grep -E 'Connection refused|timeout|unreachable' /tmp/compose-logs.txt | head -20
```

### Example 3: Systemd Journal + Syslog Investigation

**User:** *"The server keeps going down at night. Check system logs."*

**Agent should:**

```bash
# 1. Check kernel messages for OOM or hardware errors
sudo journalctl -k --since "1 day ago" -p err --no-pager | grep -iE 'oom|panic|hung_task|watchdog|temperature'

# 2. Check for service crashes
sudo journalctl --since "1 day ago" -p err --no-pager | grep -iE 'failed|stopped|crashed|exited with' | head -30

# 3. Look for SSH break-in attempts
sudo journalctl -u sshd --since "1 day ago" --no-pager | grep -iE 'failed|invalid user|break-in' | \
  awk '{print $NF}' | sort | uniq -c | sort -rn | head -10

# 4. Disk/IO errors
grep -iE 'I/O error|disk failure|sda|nvme' /var/log/syslog | tail -20

# 5. Check cron for nightly jobs that might spike CPU
grep -iE 'error|fail|oom' ~/.hermes/logs/*.log 2>/dev/null | tail -10

# 6. If OOM found, check top memory consumers
sudo journalctl -k --since "1 day ago" | grep oom | tail -5
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Log file is huge (multi-GB)** | Always filter by time range first. Use `grep`, not full-file reads. Use `head`/`tail` for sampling. For multi-GB files, create a temp filtered file: `grep '2026-07-03' huge.log > /tmp/slice.log` |
| 2 | **Need sudo for system logs** | Wrap commands with `sudo journalctl` or `sudo cat /var/log/*`. Verify sudo access before proceeding. |
| 3 | **JSON-logs span multiple lines** | Use `jq -c` (compact output) or pre-merge with `jq -s` (read all objects into array). For pretty-printed multi-line JSON: `grep -Pzo '(?s)\{[^}]*\}'` |
| 4 | **Timestamps in non-standard format** | Use Python's `dateutil.parser` or `datetime.strptime` with a custom format. Show the user the first timestamp and ask if it looks right. |
| 5 | **Docker compose logs are interleaved** | Each line is prefixed with service name. Filter with `grep '^service_name'` or use `docker compose logs service_name`. |
| 6 | **grep match too broad (false positives)** | Use `-w` for word boundaries. Use `grep -i` only when needed. Chain patterns: `grep ' 500 '` (with spaces) vs `grep '500'` (matches anything with 500). |
| 7 | **Log rotation (current log is gzipped)** | Check for `.log.gz` files. Use `zgrep` instead of `grep`, `zcat` instead of `cat`. `zgrep -c ' 500 ' /var/log/nginx/access.log.2.gz` |
| 8 | **No logs at the specified path** | Check `/var/log/`, `journalctl`, docker logs, or `/tmp/`. Common locations: `/var/log/nginx/`, `/var/log/apache2/`, `/var/log/syslog`, `~/.pm2/logs/` |
| 9 | **Binary log formats (systemd journal)** | Use `journalctl` — it's designed for this. Never `grep` binary journal files directly. |
| 10 | **A container isn't logging to stdout** | Check if the app writes to files inside the container. Use `docker exec` to check: `docker exec my_container ls -la /var/log/app/` |

---

## Verification Checklist

- [ ] Log format correctly identified (nginx/apache/syslog/JSON/docker-compose)
- [ ] Time range filtering applied before full analysis
- [ ] Error frequency distribution generated (count by type or endpoint)
- [ ] Top error patterns extracted and grouped
- [ ] Timeline bucketing shows if there's a spike pattern
- [ ] Root cause identified (not just symptoms)
- [ ] For JSON logs: `jq` queries confirmed working on sample data
- [ ] For gzipped logs: `zgrep` used instead of `grep`
- [ ] For docker logs: correct service/container name verified
- [ ] For journalctl: correct unit name and priority used
- [ ] Temporary files cleaned up (if any created in /tmp/)

---

## Data Sources & Accuracy

### Log Sources
This skill reads local files only — it never sends logs to external services. All analysis happens on the machine where the logs exist.

### Accuracy Notes
| Factor | Impact |
|--------|--------|
| **Timestamp parsing** | Timestamp format must be known upfront. For unknown formats, use Python with `dateutil.parser` which handles ~90% of ISO/standard formats. |
| **grep false positives** | A regex for "error" also matches "error_handler_prefix". Use word boundaries (`\b` or surrounding spaces) and known patterns. |
| **JSON log depth** | `jq` handles arbitrary nesting. For deeply nested JSON, chain selects: `jq 'select(.metadata?.retry_count > 3)'` |
| **Log rotation** | Always check if the file was rotated. Newest data is in the non-numbered file. Yesterday's data may be in `.log.1` or `.log.gz`. |
| **Sample vs full** | For very large logs, sampling (every Nth line) can suffice for trend detection. Use `awk 'NR % 1000 == 0'` for sampling. |

### Security
- **NEVER** pipe logs into an external service without explicit user permission
- **NEVER** expose IP addresses or user IDs in summaries without the user's acknowledgment
- System logs (`/var/log/`) may contain PII — handle with care
- Docker logs may contain environment variables — avoid full dumps unless necessary
- If logs are analyzed from a third-party service (e.g., cloud log aggregator), verify the data is allowed to be processed
