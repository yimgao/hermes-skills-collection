---
name: json-explorer
description: "Use when analyzing complex JSON data — infers schema, detects nesting depth, field types, and produces a structured data profile report."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [json, data-analysis, schema, exploration, api-response]
    related_skills: [csv-explorer, tech-stack-detector]
---

# JSON Explorer

> Explore and understand complex JSON structures. Infers schema, detects nesting depth, field types, missing values, and produces a structured data profile.

---

## When to Use

- *"Help me understand this JSON API response"*
- *"What fields are in this JSON file?"*
- *"Analyze the structure of this 10MB JSON"*
- *"Compare two JSON responses for differences"*

---

## Core Workflow

### Step 1: Load JSON

```python
import json
with open(path) as f:
    data = json.load(f)
```

### Step 2: Analyze Structure

Extract:
- **Top-level type:** object / array / primitive
- **Depth:** max nesting level
- **Fields:** all unique keys (recursive)
- **Types per field:** string, number, boolean, null, array, object
- **Null/missing ratio:** what % of records have null values
- **Sample values:** first 3 non-null values per field
- **Array lengths:** min/max/avg if field is array

### Step 3: Generate Report

```markdown
# JSON Profile

**File:** {path}
**Size:** {N} KB / {N} lines
**Top-level type:** {array/object}

---

## 📊 Overview

| Metric | Value |
|--------|-------|
| Total records | {N} |
| Total unique fields | {N} |
| Max nesting depth | {N} |
| Fields with nulls | {N}/{N} |

## 🔍 Field Summary

| Field | Type | Null % | Sample Values |
|-------|------|--------|---------------|
| `id` | number | 0% | 1, 2, 3 |
| `name` | string | 0% | "Alice", "Bob" |
| `email` | string | 12% | "a@b.com", null |
| `tags` | array(string) | 5% | ["dev"], ["design"] |
| `address.city` | string | 3% | "NYC", "SF" |

## 🏗️ Schema

```json
{
  "id": "number",
  "name": "string",
  "email?": "string | null",
  "tags": "string[]",
  "address": {
    "street": "string",
    "city": "string",
    "zip?": "string | null"
  }
}
```

## ⚠️ Anomalies

- Field `email` has 12% null rate
- Field `phone` only appears in 30% of records
- Array `tags` has inconsistent types (string vs number)
```
