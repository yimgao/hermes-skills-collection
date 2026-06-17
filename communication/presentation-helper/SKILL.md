---
name: presentation-helper
description: "Use when preparing presentations — converts notes or content into slide structures with talking points, visuals suggestions, and timing."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [presentation, slides, public-speaking, deck, keynote, powerpoint]
    related_skills: [pitch-deck-helper, email-composer, business-plan-generator]
---

# Presentation Helper

> Turn notes or content into a structured presentation. Generates slide outlines, talking points, visual suggestions, and timing estimates.

---

## When to Use

- *"Turn my business plan into a presentation"*
- *"Help me structure a 10-min presentation about my project"*
- *"Create slides for a team meeting update"*
- *"I have to give a talk — help me outline it"*

---

## Core Workflow

### Step 1: Define Scope

| Parameter | Example |
|-----------|---------|
| Topic | Business plan, Project update, Conference talk |
| Duration | 5 min, 10 min, 20 min, 45 min |
| Audience | Investors, Team, Conference, Clients |
| Tone | Formal, Inspiring, Educational, Casual |

### Step 2: Structure Slides

**Rule of thumb:** 1 slide per 1-2 minutes.

**10-minute talk = 6-8 slides:**
```
1. Title — hook / question
2. Problem — why should we care (1:30)
3. Solution — what you did (2:00)
4. Evidence — data / results (2:00)
5. Impact — so what (1:30)
6. Next steps — call to action (1:30)
7. Q&A — contact / thank you (0:30)
```

### Step 3: Per-Slide Detail

```markdown
## Slide 3: Solution
**Content:** Describe what you built
**Talking points:**
- "We solved X by doing Y"
- "The key insight was…"
- Demo / screenshot here
**Visual:** Screenshot or diagram
**Time:** 2 min
**Transition:** "So how did we validate this?"
```

### Step 4: Output

```markdown
# Presentation: {Title}

**Duration:** {N} min
**Audience:** {type}
**Slides:** {N}

---

| Slide | Title | Time | Key Message |
|-------|-------|------|-------------|
| 1 | {Title} | 1 min | Hook |
| 2 | Problem | 1:30 | {pain point} |
| 3 | Solution | 2 min | {your idea} |
| 4 | Results | 2 min | {data} |
| 5 | Next steps | 1:30 | {CTA} |
| 6 | Q&A | 1 min | — |

## Full Script
[Slide-by-slide talking points]

## Visual Suggestions
- Slide 3: Architecture diagram
- Slide 4: Bar chart comparing before/after
```
