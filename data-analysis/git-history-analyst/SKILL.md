---
name: git-history-analyst
description: "Use when analyzing git repository history — stats on contributors, commit patterns, code churn, module hotspots, and trends over time."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [git, analytics, repository, history, contribution, metrics]
    related_skills: [code-review-helper, changelog-generator]
---

# Git History Analyst

> Analyze git repository history. Stats on contributors, commit patterns, code churn, file hotspots, and trends over time.

---

## When to Use

- *"Who contributed the most code this month?"*
- *"Show me commit activity for the last 30 days"*
- *"Which files change most often?"*
- *"What's our team's coding pace this sprint?"*
- *"Analyze my open source contribution stats"*

---

## Core Workflow

### Step 1: Collect Git Stats

```bash
# Commit count per author (all time)
git shortlog -sn --all

# Commit count per author (last 30 days)
git shortlog -sn --since="30 days ago"

# File change frequency
git log --name-only --pretty=format: | sort | uniq -c | sort -rn | head -20

# Lines changed per author
git log --format='%aN' --numstat | awk '{if(NF==3){added+=$1;removed+=$2}else{print $1": +"added" -"removed;added=0;removed=0}}'

# Commits per day
git log --since="90 days ago" --format="%ad" --date=format:"%Y-%m-%d" | sort | uniq -c

# Bus factor (top 3 authors % of total)
git shortlog -sn --all | head -3
```

### Step 2: Generate Report

```markdown
# Git Repository Analysis

**Repo:** {name}
**Period:** {date range}
**Total commits:** {N}
**Total authors:** {N}

---

## 👥 Contributor Overview

| Author | Commits | Added | Removed | Files Changed |
|--------|---------|-------|---------|---------------|
| {name} | {N} | {+N} | {-N} | {N} |

**Bus Factor:** Top 3 authors = {X}% of all commits

## 📈 Activity Trends

| Month | Commits | Active Authors |
|-------|---------|----------------|
| May 2026 | {N} | {N} |
| Jun 2026 | {N} | {N} |

## 🔥 Hot Files (Most Changed)

| File | Changes | Last Modified |
|------|---------|---------------|
| src/main.py | {N} | {date} |
| src/api/routes.py | {N} | {date} |

## ⏰ Commit Patterns

- **Most active day:** Tuesday (35% of commits)
- **Most active hour:** 3-4 PM
- **Weekend commits:** 12% (healthy work-life balance?)
```

---

## Example

```
User: Show me my contribution stats for the last 30 days
Hermes should:
  1. git shortlog -sn --since="30 days ago"
  2. git log --numstat --since="30 days ago"
  3. git log --since="30 days ago" --format="%ad" --date=format:"%Y-%m-%d"
  4. Compile structured contribution report
```
