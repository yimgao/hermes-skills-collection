---
name: prompt-benchmarker
description: "Use when comparing prompt variations — runs multiple prompt versions against test cases, scores outputs, and recommends the best prompt."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [prompt-engineering, benchmarking, testing, llm, optimization]
    related_skills: [llm-output-validator, model-comparator]
---

# Prompt Benchmarker

> Compare prompt variations to find the best one. Runs multiple prompts against test cases, scores outputs on relevance, completeness, and format compliance.

---

## When to Use

- *"Which of these prompts works better?"*
- *"Help me optimize my system prompt"*
- *"A/B test these two prompt versions"*
- *"Quantify which prompt gets better results"*

---

## Core Workflow

### Step 1: Define Test

```yaml
prompts:
  - name: "Version A"
    text: "Summarize the following text in 3 bullet points..."
  - name: "Version B"
    text: "You are an expert summarizer. Give me..."

test_cases:
  - input: "Long article text..."
    expected: "3 bullet points"
  - input: "Another article..."
    expected: "3 bullet points"

criteria:
  - "Follows format (3 bullet points)"
  - "Captures key information"
  - "No hallucinated content"
```

### Step 2: Run & Score

For each prompt × test case:
1. Send prompt + input to the LLM
2. Score output on each criterion (1-5)
3. Calculate average score per prompt

### Step 3: Recommend

```markdown
# Prompt Benchmark Results

## Overall Scores
| Prompt | Avg Score | Format | Accuracy | Completeness |
|--------|-----------|--------|----------|-------------|
| Version A | 4.2/5 | 4.5 | 4.0 | 4.0 |
| Version B | 3.8/5 | 3.0 | 4.5 | 4.0 |

## Winner: Version A
**Why:** Significantly better format compliance while maintaining accuracy.

## Sample Outputs
### Version A (Test 1)
{output}

### Version B (Test 1)
{output}
```
