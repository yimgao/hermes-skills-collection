---
name: file-organizer
description: "Use when cleaning up cluttered folders — scans a directory, categorizes files by type, and suggests an organization plan."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [file-management, organization, cleanup, utility, productivity]
    related_skills: [disk-cleanup-advisor, format-converter]
---

# File Organizer

> Scan a cluttered folder and get a plan to organize it. Categorizes files by type, date, and project — then suggests a clean structure.

---

## When to Use

- *"Clean up my Downloads folder"*
- *"Organize my Desktop — it's a mess"*
- *"帮我整理这个项目文件夹"*
- *"Sort these files into proper directories"*

---

## Core Workflow

### Step 1: Scan Directory

```bash
ls -la {path}
# or for recursive
find {path} -type f | head -100
```

### Step 2: Categorize

Group files by:
- **Type:** pdf, docx, image, video, code, archive
- **Date:** last modified (this week, this month, older)
- **Project:** by filename prefix or content pattern
- **Size:** large files (>100MB) worth noting

### Step 3: Generate Plan

```markdown
# Folder Organization: {path}

**Current state:** {N} files, {N} folders

---

## By Type
| Type | Count | Size | Suggested Folder |
|------|-------|------|-----------------|
| PDF | {N} | {N}MB | `./documents/` |
| Images | {N} | {N}MB | `./images/` |
| Code | {N} | {N}MB | `./code/` |
| Archives | {N} | {N}MB | `./archives/` |

## Proposed Structure
```
{path}/
├── documents/
│   ├── reports/
│   └── manuals/
├── images/
│   ├── screenshots/
│   └── photos/
├── code/
│   ├── python/
│   └── web/
├── archives/
└── _unsorted/
```

## Large Files to Review
| File | Size | Last Modified |
|------|------|---------------|
| {name} | {N}MB | {date} |
```
