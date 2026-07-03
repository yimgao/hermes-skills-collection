---
name: csv-explorer
description: "Analyze CSV/TSV files — infer schemas, detect data quality issues, generate summary statistics, identify outliers, and produce a comprehensive structured report."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [csv, data-analysis, profiling, statistics, data-quality, tabular]
    related_skills: [json-explorer, format-converter, screenshot-to-report]
---

# CSV Explorer

> Analyze tabular data (CSV/TSV) — infer column schemas, detect data quality issues, generate summary statistics, identify outliers and anomalies, and produce a comprehensive structured report.

---

## Overview

| Capability | Description |
|------------|-------------|
| **Schema Inference** | Detect column names, data types, null ratios |
| **Summary Statistics** | Count, mean, median, std, min, max, quartiles per numeric column |
| **Value Distribution** | Frequency counts for categorical/text columns |
| **Data Quality** | Missing values, duplicates, inconsistent formatting, type coercion |
| **Outlier Detection** | IQR-based and z-score outlier identification |
| **Correlation Analysis** | Pairwise correlation matrix for numeric columns |
| **Cross-column Validation** | Check for invalid combinations (e.g. end_date < start_date) |

---

## When to Use

- *"Analyze this CSV file and tell me about the data"*
- *"Check this CSV for data quality issues"*
- *"Show me summary statistics for this dataset"*
- *"Are there any outliers in this CSV?"*
- *"What columns have missing values?"*
- *"Profile this TSV export and give me a report"*
- *"Compare column distributions between these two CSV files"*

---

## Core Workflow

### Step 1: Read & Parse

Use Python's `csv` module (stdlib) for reliable parsing. Detect delimiter automatically.

```python
import csv, io, os
from collections import Counter

def detect_delimiter(path, sample_size=5):
    """Detect CSV vs TSV vs custom delimiter."""
    with open(path) as f:
        sample = f.read(4096)
    sniffer = csv.Sniffer()
    try:
        return sniffer.sniff(sample).delimiter
    except csv.Error:
        return ','  # fallback

def read_csv(path):
    delimiter = detect_delimiter(path)
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        rows = list(reader)
    return rows, reader.fieldnames
```

### Step 2: Schema Inference & Type Detection

Classify each column by examining sample values:

```python
import statistics
from collections import Counter

def infer_type(values, sample_limit=100):
    """Infer best type: int, float, date, boolean, or string."""
    non_null = [v.strip() for v in values if v and v.strip()]
    if not non_null:
        return 'null'
    
    # Check boolean
    bool_vals = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}
    if all(v.lower() in bool_vals for v in non_null[:sample_limit]):
        return 'boolean'
    
    # Check int
    try:
        ints = [int(v) for v in non_null[:sample_limit]]
        return 'integer'
    except ValueError:
        pass
    
    # Check float
    try:
        floats = [float(v) for v in non_null[:sample_limit]]
        return 'float'
    except ValueError:
        pass
    
    # Check date (YYYY-MM-DD, MM/DD/YYYY, etc.)
    import re
    date_patterns = [
        r'^\d{4}-\d{2}-\d{2}$',
        r'^\d{2}/\d{2}/\d{4}$',
        r'^\d{4}/\d{2}/\d{2}$',
        r'^\d{2}-\d{2}-\d{4}$',
    ]
    sample = non_null[:sample_limit]
    date_match = sum(
        1 for v in sample 
        if any(re.match(p, v) for p in date_patterns)
    )
    if date_match > len(sample) * 0.8:
        return 'date'
    
    return 'string'
```

### Step 3: Generate Statistics

```python
def summarize_column(values, col_type):
    """Generate summary stats based on inferred type."""
    non_null = [v.strip() for v in values if v and v.strip()]
    null_count = sum(1 for v in values if not v or not v.strip())
    
    result = {
        'null_count': null_count,
        'null_pct': round(null_count / max(len(values), 1) * 100, 1),
        'unique_count': len(set(non_null)),
    }
    
    if col_type in ('integer', 'float'):
        nums = [float(v) for v in non_null]
        result.update({
            'min': min(nums), 'max': max(nums),
            'mean': round(statistics.mean(nums), 2),
            'median': round(statistics.median(nums), 2),
            'stdev': round(statistics.stdev(nums), 2) if len(nums) > 1 else 0,
            'q1': round(statistics.quantiles(nums, n=4)[0], 2),
            'q3': round(statistics.quantiles(nums, n=4)[2], 2),
        })
        # Outlier detection (IQR)
        iqr = result['q3'] - result['q1']
        lower = result['q1'] - 1.5 * iqr
        upper = result['q3'] + 1.5 * iqr
        outliers = [v for v in nums if v < lower or v > upper]
        result['outliers'] = {'count': len(outliers), 'threshold': (lower, upper)}
    
    if col_type == 'string':
        # Top 10 most frequent values
        counter = Counter(non_null)
        result['top_values'] = counter.most_common(10)
    
    return result
```

### Step 4: Data Quality Checks

| Check | Method |
|-------|--------|
| Missing values | Count empty/blank per column |
| Duplicate rows | `len(rows) - len(set(tuple(r.items()) for r in rows))` |
| Inconsistent casing | Compare `str.lower()` vs original for categorical columns |
| Trailing whitespace | Check if any values differ from their `strip()` version |
| Mixed types in column | Parse each value and flag columns with >1 inferred type |
| Unrealistic values | Compare min/max against reasonable bounds for the column name |
| Cross-column logic | Check date ranges, status flows, foreign key references |

### Step 5: Generate Report

```markdown
# CSV Data Profile Report

**File:** `{filename}`
**Size:** {N} rows × {N} columns
**Delimiter:** {comma/tab/pipe}

---

## 📊 Dataset Overview

| Metric | Value |
|--------|-------|
| Total rows | {N} |
| Total columns | {N} |
| Duplicate rows | {N} ({P}%) |
| Columns with nulls | {N}/{N} |
| Memory estimate | {N} KB |

## 🔍 Column Schema

| # | Column | Type | Null % | Unique | Min | Max | Mean | Median |
|---|--------|------|--------|--------|-----|-----|------|--------|
| 1 | `id` | integer | 0% | 1000 | 1 | 1000 | 500.5 | 500.5 |
| 2 | `name` | string | 2.1% | 980 | — | — | — | — |
| 3 | `salary` | float | 5.3% | 850 | 30K | 250K | 85K | 78K |

## ⚠️ Data Quality Issues

- **Column `email`:** 23 null values (2.3%) — should be required
- **Column `age`:** 3 outliers detected (values > 120)
- **Column `state`:** Inconsistent casing: "CA" vs "ca" vs "Ca"
- **Column `zip_code`:** 5 values have non-numeric characters
- **Duplicate rows:** 12 exact duplicates found

## 📈 Distribution Highlights

### Numeric Columns

**`salary`** — Right-skewed (mean > median)

| Percentile | Value |
|------------|-------|
| Min | $30,000 |
| Q1 | $55,000 |
| Median | $78,000 |
| Q3 | $105,000 |
| Max | $250,000 |

**Outlier count:** 8 rows (above $195K or below $12K)

### Categorical Columns

**`department`** — Top 5 values:
| Value | Count | % |
|-------|-------|---|
| Engineering | 340 | 34% |
| Sales | 210 | 21% |
| Marketing | 180 | 18% |
| HR | 120 | 12% |
| Finance | 95 | 10% |

## 🔗 Correlation Matrix

| | id | salary | years_exp | age |
|---|----|--------|-----------|-----|
| id | 1.00 | 0.02 | 0.01 | 0.00 |
| salary | 0.02 | 1.00 | **0.67** | **0.42** |
| years_exp | 0.01 | **0.67** | 1.00 | **0.71** |
| age | 0.00 | **0.42** | **0.71** | 1.00 |

**Notable correlations:** `salary` ↔ `years_exp` (0.67), `years_exp` ↔ `age` (0.71)
```

---

## Example Invocations

### Example 1: Basic Data Profile

```
User: "Analyze this CSV file: employees.csv"

Hermes should:
  1. Read and parse `employees.csv`
  2. Infer schema: id(int), name(str), salary(float), dept(str), hire_date(date)
  3. Generate summary statistics per column
  4. Check for duplicates, nulls, outliers
  5. Produce the profile report above
```

### Example 2: Quality Check on Exported Data

```
User: "Check data_export.csv for quality issues before I load it into production"

Hermes should:
  1. Read the CSV and note row count
  2. Run all quality checks: duplicates, nulls, type consistency, outliers
  3. Flag any columns with >5% null rate as "needs attention"
  4. Check if primary-key column has duplicates (if name suggests 'id')
  5. Verify date columns parse correctly (no 2025-02-30 type errors)
  6. Generate a concise QA report with 3 categories: PASS / WARN / FAIL
```

### Example 3: Compare Two CSV Files

```
User: "Compare last week's sales.csv with this week's sales_new.csv — what changed?"

Hermes should:
  1. Profile both files independently
  2. Compare row counts, column counts, schema
  3. Detect new/missing columns
  4. For shared numeric columns, report mean/median shifts >5%
  5. For categorical columns, report significant distribution changes
  6. Generate a diff report: "Added 12 products, removed col 'old_price'"
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| **Encoding issues** (UTF-8 BOM, Latin-1) | Try `utf-8-sig` first, fallback to `latin-1` or `chardet` |
| **CSV with header and no header** | Check first row against data types; if first row values are non-numeric for numeric columns, treat as header |
| **Very large files** (>100MB) | Sample first 10K rows for profiling; use `csv.reader` iterator instead of loading all |
| **Quoted fields with commas** | Always use Python's `csv` module, never naive `str.split(',')` |
| **Empty/missing file** | Check `os.path.getsize()` > 0 before parsing |
| **Inconsistent date formats** | Use `dateutil.parser` or try multiple common formats; report ambiguous rows |
| **Leading/trailing whitespace** | Always strip values during parsing; report whitespace issues separately |
| **Numeric columns with currency symbols** | Strip `$`, `€`, `¥`, commas, `%` before type detection; note original format |

---

## Verification Checklist

- [ ] CSV file parsed successfully with correct delimiter detection
- [ ] Schema inferred and reported (column names + types)
- [ ] Summary statistics generated for each column (type-appropriate)
- [ ] Null counts and percentages reported
- [ ] Duplicate rows detected and counted
- [ ] Outliers identified (for numeric columns)
- [ ] Data quality issues flagged (inconsistent casing, whitespace, mixed types)
- [ ] Top value frequencies listed for categorical columns
- [ ] Correlation matrix generated (for datasets with 2+ numeric columns)
- [ ] Report produced in structured Markdown

---

## Data Sources & Accuracy

This skill operates entirely on user-provided files. No external APIs are used. Accuracy depends on:

- **Type inference** uses heuristic sampling (first 100 non-null values) — may misclassify edge cases like zip codes (numeric string) as integers
- **Outlier detection** uses IQR method (1.5× rule) — may not suit multimodal distributions
- **Correlation** is Pearson's r (linear) — non-linear relationships may be missed
- **Date parsing** supports ISO 8601, US (MM/DD/YYYY), and EU (DD/MM/YYYY) formats but may confuse ambiguous dates
