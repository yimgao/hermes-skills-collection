---
name: job-tracker
description: "Use when tracking job applications — records company, role, date, status. Designed to pair with cron for follow-up reminders."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [job-hunt, tracking, applications, cron, career]
    related_skills: [jd-resume-matcher, cover-letter-writer, job-hunt-pipeline]
---

# Job Tracker

> Track your job applications. Records company, role, date, and status. View your pipeline at a glance. Pair with cron for automatic follow-up reminders.

---

## When to Use

- *"Track my application to Google for Software Engineer"*
- *"Show me all my applications"*
- *"Set up a weekly follow-up reminder for applications older than 2 weeks"*

---

## CLI Usage

```bash
cd ~/dev/job-hunt-tool
source .venv/bin/activate

# Record an application
python3 -m src track --company Google --role "Software Engineer" --status 投递

# View all applications
python3 -m src status
```

## Cron Reminder

```bash
cronjob \
  action=create \
  schedule="0 10 * * 1" \
  name="job-follow-up" \
  prompt="Check ~/dev/job-hunt-tool/data/applications.csv for applications 
  older than 2 weeks with status '投递' or '已联系'. Suggest follow-up emails."
```

## Output Example

```
📋 投递记录
┌────────────┬──────────┬──────────────────┬──────────┐
│ 日期        │ 公司     │ 职位             │ 状态     │
├────────────┼──────────┼──────────────────┼──────────┤
│ 2026-06-17 │ Google   │ Software Engineer │ 投递     │
│ 2026-06-15 │ Stripe   │ Senior Engineer  │ 面试     │
│ 2026-06-10 │ Notion   │ Full-stack       │ 拒绝     │
└────────────┴──────────┴──────────────────┴──────────┘
```
