---
name: screenshot-to-report
description: "Use when extracting data from website screenshots or images — reads visible text, tables, and numbers, then compiles a structured Markdown report."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [screenshot, ocr, data-extraction, reporting, web-scraping]
    related_skills: [tech-stack-detector, json-explorer]
---

# Screenshot to Report

> Extract data from webpage screenshots — reads visible text, tables, charts, and numbers, then compiles everything into a structured Markdown report.

---

## When to Use

- *"Extract the data from this screenshot (attach image)"*
- *"Turn this dashboard screenshot into a report"*
- *"Read the table from this webpage screenshot"*
- *"Compare two screenshots and tell me what changed"*

---

## Core Workflow

### Step 1: Capture or Receive Input

If the user attaches a screenshot, use vision tools to read it.

If the user provides a URL, navigate to it and take screenshots of relevant sections.

### Step 2: Extract Information

Use vision analysis to extract:
- **Text content** — all readable text
- **Tables** — rows and columns, header detection
- **Numbers** — metrics, percentages, currency values
- **Charts** — labels, values, trends (up/down/flat)
- **UI elements** — buttons, navigation, layout structure

### Step 3: Generate Report

```markdown
# Screenshot Analysis Report

**Source:** {URL or filename}
**Captured:** {YYYY-MM-DD HH:MM}

---

## 📋 Extracted Content

### Text
{paragraphs of extracted text}

### Tables
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| {value} | {value} | {value} |

### Key Metrics
- **{Metric 1}:** {value}
- **{Metric 2}:** {value}

## 💡 Key Observations

- {finding 1}
- {finding 2}
```
