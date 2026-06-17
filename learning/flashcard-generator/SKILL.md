---
name: flashcard-generator
description: "Use when studying — converts notes, articles, or any text into Anki-compatible flashcards (Q&A format) for spaced repetition learning."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [study, flashcards, anki, spaced-repetition, learning, memorization]
    related_skills: [study-planner, arxiv-paper-summarizer]
---

# Flashcard Generator

> Convert notes, articles, or any text into flashcards for spaced repetition. Outputs in Anki-compatible format.

---

## When to Use

- *"Turn these notes into flashcards for studying"*
- *"Make Anki cards from this article"*
- *"Create flashcards for my exam next week"*
- *"帮我从这篇文章生成记忆卡片"*

---

## Core Workflow

### Step 1: Ingest Content

Accept: paste text, article URL, PDF, or notes file.

### Step 2: Extract Concepts

Identify key facts, definitions, relationships, and lists.

**Card types:**
| Type | Format | Example |
|------|--------|---------|
| Basic | Q: {question} → A: {answer} | Q: What is RAM? → A: Random Access Memory |
| Cloze | {text with {...} blank} | {...} is the capital of France |
| List | Q: List 3 types of X → A: 1..., 2..., 3... |
| Compare | Q: Compare X and Y → A: Table |

### Step 3: Output

```markdown
# Flashcards: {Topic}
**Count:** {N} cards
**Format:** Anki-compatible (CSV)

---

## Card 1
**Type:** Basic
**Q:** What is {concept}?
**A:** {definition}

## Card 2
**Type:** Cloze
**Front:** The {{c1::mitochondria}} is the powerhouse of the cell.
**Back:** mitochondria

---

## Anki Import (CSV)
```csv
"What is RAM?","Random Access Memory"
"What does CPU stand for?","Central Processing Unit"
```
```

Save to `~/dev/reports/flashcards/{topic}-{date}.md`.
