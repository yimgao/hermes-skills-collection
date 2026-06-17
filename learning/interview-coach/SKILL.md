---
name: interview-coach
description: "Use when preparing for job interviews — practices STAR responses, generates industry-specific questions, and provides feedback on answers."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [interview, career, job-search, star-method, coaching]
    related_skills: [email-composer, presentation-helper]
---

# Interview Coach

> Prepare for job interviews. Generates industry-specific questions, coaches STAR responses, and provides structured feedback.

---

## When to Use

- *"Help me prepare for a product manager interview"*
- *"Practice behavioral interview questions"*
- *"Give me a mock interview for a software engineering role"*
- *"帮我准备面试，用 STAR 法则"*

---

## Core Workflow

### Step 1: Gather Context

| Parameter | Example |
|-----------|---------|
| Role | Product Manager, Software Engineer, Data Scientist |
| Level | Entry, Mid, Senior, Staff |
| Industry | Tech, Finance, Consulting |
| Company | FAANG, Startup, Traditional |
| Interview stage | Phone screen, Onsite, Behavioral, Technical |

### Step 2: Generate Questions

**Behavioral (STAR):**
```
- Tell me about a time you led a difficult project
- Describe a conflict with a teammate and how you resolved it
- Tell me about a time you failed
```

**Role-specific:**
- PM: "How would you prioritize 10 features with limited engineering capacity?"
- Engineer: "Design a rate limiter"
- Data Scientist: "How would you design an A/B test?"

**Company-specific:** Search for known interview formats.

### Step 3: STAR Coaching

```
S — Situation: "In my previous role at X, we were facing…"
T — Task: "I was responsible for…"
A — Action: "I did three things: first…, then…, finally…"
R — Result: "As a result, metric improved by X% / we shipped Y / team grew to Z"

Check:
✅ Situation is specific (not vague)
✅ Action uses "I" not "we"
✅ Result is quantified
✅ Takes 60-90 seconds
```

### Step 4: Mock Interview

```markdown
# Interview Prep: {Role} at {Company}

## Focus Areas
1. Behavioral — 3 STAR stories to prepare
2. Technical — 2 system design questions
3. Case — 1 product sense question

## Practice Question 1
{Q}
**Expected framework:** {approach}
**Key points to hit:** {list}

## Feedback
✅ You clearly stated the situation
✅ Action had 3 concrete steps
⚠️ Result could be more quantified — try "reduced churn by 15%"
```
