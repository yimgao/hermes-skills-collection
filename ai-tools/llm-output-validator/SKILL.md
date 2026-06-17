---
name: llm-output-validator
description: "Use when verifying LLM-generated content quality — checks for factual errors, logical contradictions, format compliance, and completeness against requirements."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [llm, validation, quality-assurance, testing, output-checking]
    related_skills: [prompt-benchmarker, code-review-helper]
---

# LLM Output Validator

> Verify LLM-generated content quality and accuracy. Checks for factual errors, logical contradictions, format compliance, and completeness against the original requirements.

---

## When to Use

- *"Verify this LLM-generated summary is accurate"*
- *"Check if the output follows my format requirements"*
- *"Find factual errors in this AI-generated article"*
- *"Validate this translated text for consistency"*

---

## Core Workflow

### Step 1: Get Requirements + Output

Extract from the original prompt:
- **Format requirements** (bullet points, JSON, table, markdown)
- **Content requirements** (what must be included)
- **Length constraints**
- **Tone/style requirements**

### Step 2: Run Checks

| Check | What It Detects | Method |
|-------|-----------------|--------|
| **Factual accuracy** | Hallucinated facts, wrong numbers | Cross-reference with source |
| **Format compliance** | Missing sections, wrong structure | Regex pattern matching |
| **Completeness** | Missing required elements | Checklist against prompt |
| **Logical consistency** | Contradictions within output | Read-through, identify conflicts |
| **Length compliance** | Too short or too long | Word/token count |
| **Tone match** | Off-tone phrasing | Style comparison with requirements |

### Step 3: Generate Validation Report

```markdown
# LLM Output Validation

**Requirements:** {description}
**Output length:** {N} words (required: {M})

---

## ✅ Passed Checks

- [x] Format: Correct markdown structure
- [x] Length: Within range
- [x] Tone: Professional, matches brief

## ❌ Issues Found ({N})

### Issue 1: Factual Error
- **Detail:** "Company was founded in 2019" but source says 2015
- **Severity:** 🔴 Critical
- **Fix:** Correct to 2015

### Issue 2: Missing Section
- **Detail:** "Pricing" section mentioned in prompt but absent in output
- **Severity:** 🟡 Warning
- **Fix:** Add pricing section

## 📊 Quality Score

| Criteria | Score | Notes |
|----------|-------|-------|
| Accuracy | 4/5 | 1 factual error |
| Completeness | 3/5 | Missing 1 section |
| Format | 5/5 | Perfect |
| Consistency | 5/5 | No contradictions |
| **Overall** | **4.3/5** | Good, needs minor fixes |
```
