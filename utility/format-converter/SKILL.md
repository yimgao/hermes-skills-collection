---
name: format-converter
description: "Use when converting between data formats — transforms JSON, YAML, TOML, CSV, and Markdown tables into each other."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [converter, json, yaml, toml, csv, format, utility]
    related_skills: [json-explorer, file-organizer]
---

# Format Converter

> Convert between data formats: JSON ↔ YAML ↔ TOML ↔ CSV ↔ Markdown table. Auto-detects input format.

---

## When to Use

- *"Convert this JSON to YAML"*
- *"Turn this CSV into a Markdown table"*
- *"I need this TOML config as JSON"*
- *"Convert this API response to CSV"*

---

## Core Workflow

### Step 1: Detect Input Format

Look at the content:
- Starts with `{` or `[` → JSON
- Starts with `key:` or `---` → YAML
- Contains `[tool]` or `key = "value"` → TOML
- Contains `,` rows with first line as header → CSV
- Contains `\|` with `---|---` → Markdown table

### Step 2: Convert

Use Python stdlib or system tools:

```python
import json, yaml, csv, io

# JSON → YAML
data = json.loads(json_str)
yaml_str = yaml.dump(data, default_flow_style=False)

# YAML → JSON
data = yaml.safe_load(yaml_str)
json_str = json.dumps(data, indent=2)

# JSON → CSV (flat objects)
data = json.loads(json_str)
output = io.StringIO()
writer = csv.DictWriter(output, fieldnames=data[0].keys())
writer.writeheader()
writer.writerows(data)
```

### Step 3: Output

Show original vs converted, with line count comparison.

**Supported conversions:**
| From → To | Status |
|-----------|--------|
| JSON → YAML | ✅ |
| YAML → JSON | ✅ |
| JSON → TOML | ✅ (flat) |
| TOML → JSON | ✅ |
| CSV → Markdown | ✅ |
| Markdown → CSV | ✅ |
| JSON → CSV | ✅ (flat objects) |
| CSV → JSON | ✅ |
