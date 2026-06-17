---
name: model-comparator
description: "Use when comparing AI models — searches latest pricing, context lengths, benchmarks, and capabilities to produce a comparison table with recommendations."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [ai-models, comparison, pricing, llm, benchmarks, selection]
    related_skills: [prompt-benchmarker, product-pricing-tracker]
---

# Model Comparator

> Compare AI models across pricing, context length, benchmarks, and capabilities. Produces a side-by-side comparison with usage recommendations.

---

## When to Use

- *"Compare GPT-4o, Claude 4, and Gemini 2.5"*
- *"Which model is best for code generation?"*
- *"What's the cheapest model with 100K context?"*
- *"Compare open source vs closed source LLMs"*

---

## Core Workflow

### Step 1: Define Scope

| Parameter | Values |
|-----------|--------|
| Models | GPT-4o, Claude 4, Gemini 2.5, Llama 4, DeepSeek-V4 |
| Dimension | Pricing / Context / Speed / Capability |
| Use case | Chat / Code / Reasoning / Vision |

### Step 2: Collect Data

Search for each model's latest:
- **Pricing:** Input $/M tokens, Output $/M tokens
- **Context:** Max tokens, supported
- **Capabilities:** Vision, file upload, web search, function calling, structured output
- **Speed:** Tokens per second (if available)
- **Benchmarks:** MMLU, HumanEval, GSM8K (latest published)

### Step 3: Generate Comparison

```markdown
# AI Model Comparison

**Date:** {YYYY-MM-DD}
**Focus:** {use case}

---

## 📊 Pricing & Specs

| Model | Input $/M tok | Output $/M tok | Context | Speed |
|-------|---------------|----------------|---------|-------|
| GPT-4o | $2.50 | $10.00 | 128K | Fast |
| Claude 4 | $3.00 | $15.00 | 200K | Medium |
| Gemini 2.5 | $1.25 | $5.00 | 1M | Fast |

## 🏆 Benchmark Scores

| Model | MMLU | HumanEval | GSM8K |
|-------|------|-----------|-------|
| GPT-4o | 88.7 | 90.2 | 95.3 |
| Claude 4 | 89.1 | 92.0 | 96.0 |

## 💡 Recommendations

| Use Case | Best Model | Why |
|----------|------------|-----|
| Code generation | Claude 4 | Highest HumanEval |
| Cost-sensitive | Gemini 2.5 | Cheapest + 1M context |
| General chat | GPT-4o | Best all-rounder |
```
