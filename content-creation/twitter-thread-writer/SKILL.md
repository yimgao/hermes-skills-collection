---
name: twitter-thread-writer
description: "Use when creating Twitter/X threads from long-form content — splits into ≤280-char tweets, optimizes hooks, and structures for engagement."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [twitter, thread, social-media, content-creation, engagement]
    related_skills: [content-repurposer, newsletter-digest]
---

# Twitter Thread Writer

> Turn long-form content into optimized Twitter threads. Auto-splits into ≤280 character tweets, crafts hooks, paces the narrative, and structures for maximum engagement.

---

## When to Use

- *"Turn this article into a Twitter thread"*
- *"Write a thread explaining this concept"*
- *"Create a viral thread about this topic"*
- *"帮我写一个中文 Twitter 线程"*

---

## Core Workflow

### Step 1: Understand the Content

Extract: core thesis, 3-5 key points, supporting examples, conclusion/CTA.

### Step 2: Structure the Thread

```
1/N {Hook — bold/controversial/question} 🧵
2/N {Context — why now}
3/N-5/N {Key points — each with an example}
N-1/N {Summary — the one thing to remember}
N/N {CTA — question or link}
```

### Step 3: Optimize Per Tweet

Rules:
- **≤280 chars** per tweet (enforce strictly)
- **1/N, 2/N** numbering
- 🧵 in tweet 1
- **Hook** is the most important sentence
- **Last tweet** = CTA (question, link, or poll)
- **Hashtags** only in last tweet, max 3
- **Line breaks** improve readability

### Step 4: Count & Verify

```python
for i, tweet in enumerate(thread, 1):
    assert len(tweet) <= 280, f"Tweet {i} exceeds 280 chars"
```
