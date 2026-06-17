---
name: study-planner
description: "Use when planning study for exams or certifications — creates a day-by-day study schedule based on the time available, material volume, and difficulty."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [study, planner, exam, certification, time-management, learning]
    related_skills: [flashcard-generator, interview-coach, travel-itinerary-planner]
---

# Study Planner

> Create a day-by-day study plan for exams or certifications. Based on time available, material volume, and difficulty — schedules topics and review sessions.

---

## When to Use

- *"I have 30 days to prepare for the AWS Solutions Architect exam"*
- *"帮我制定一个30天的日语N2学习计划"*
- *"Create a study schedule for my final exams"*
- *"I need to pass the PMP — plan my study"*

---

## Core Workflow

### Step 1: Gather Requirements

| Parameter | Example |
|-----------|---------|
| Subject/Exam | AWS SAA, JLPT N2, PMP, GRE |
| Days until exam | 30, 60, 90 |
| Hours per day available | 1, 2, 4 |
| Current level | Beginner, Intermediate, Review |
| Materials | Books, courses, practice tests |

### Step 2: Design Schedule

```
Week 1-2: Foundation (learn new concepts)
  → 60% learning + 40% review

Week 3-4: Practice (apply knowledge)
  → 40% learning + 60% practice tests

Week 5+: Mastery
  → 20% review + 80% mock exams + weak area focus
```

### Step 3: Output

```markdown
# Study Plan: {Exam/Subject}

**Exam date:** {YYYY-MM-DD}
**Daily study time:** {N} hours
**Total study hours:** {N}

---

## Weekly Overview

| Week | Focus | Hours | Key Activities |
|------|-------|-------|----------------|
| 1 | Foundation | {N} | {topics} |
| 2 | Foundation | {N} | {topics} |
| 3 | Practice | {N} | {practice tests} |
| 4 | Review | {N} | {weak areas} |

## Day-by-Day

### Week 1
| Day | Topic | Activity | Time |
|-----|-------|----------|------|
| Mon | {topic} | Read Ch1-2 + notes | 2h |
| Tue | {topic} | Read Ch3 + flashcards | 2h |
| Wed | {topic} | Practice quiz Ch1-3 | 1.5h |
| Thu | {topic} | Read Ch4-5 | 2h |
| Fri | {topic} | Review all week | 1h |
| Sat | Rest | — | — |
| Sun | {weak area} | Extra practice | 1h |
```
