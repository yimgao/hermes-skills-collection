---
name: skill-hub
description: "Use when you want to discover or decide which Hermes skill to use for a task. Lists all available skills, their purposes, and helps match user requests to the right skill."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [meta, skills, discovery, directory, help]
    related_skills: []
---

# 🧩 Skill Hub

> Discover which Hermes skill to use for any task. Lists all available skills, their triggers, and helps match your request to the right tool.

---

## Overview

This is a meta-skill — it helps you find the right skill for whatever you want to do. Instead of remembering which skill does what, just tell the hub what you need and it will recommend the best skill.

---

## When to Use

- *"What skills do you have?"*
- *"I want to analyze something — which skill should I use?"*
- *"What can you help me with?"*
- *"Is there a skill that can do X?"*

---

## Skill Directory

### 🔬 Research
| Skill | When to Use |
|-------|-------------|
| **local-competitive-analysis** | Analyze local competitors for a business type (e.g., "ramen near me") |
| **competitor-news-monitor** | Track what competitors are doing — news, launches, funding |
| **arxiv-paper-summarizer** | Summarize arXiv papers in English or Chinese |

### 🌐 Web Analysis
| Skill | When to Use |
|-------|-------------|
| **tech-stack-detector** | What tech does a website use? Framework, hosting, CDN, analytics |

### 📊 Monitoring
| Skill | When to Use |
|-------|-------------|
| **product-pricing-tracker** | Track pricing changes over time. Pairs with cron. |

### 📊 Data Analysis
| Skill | When to Use |
|-------|-------------|
| **json-explorer** | Explore and understand complex JSON structures |
| **screenshot-to-report** | Extract data from webpage screenshots into reports |
| **git-history-analyst** | Analyze git commit history — who, when, what, trends |

### 🛠️ Dev Tools
| Skill | When to Use |
|-------|-------------|
| **project-scaffolder** | Generate project skeleton from description |
| **api-doc-generator** | Auto-generate API docs from code |
| **code-review-helper** | Structured code review from diff/PR |
| **env-setup-debugger** | Diagnose project environment issues |

### ✍️ Content Creation
| Skill | When to Use |
|-------|-------------|
| **newsletter-digest** | Generate curated weekly digests on any topic |
| **content-repurposer** | One content → Twitter, LinkedIn, 小红书, newsletter |
| **twitter-thread-writer** | Turn long content into optimized Twitter threads |
| **brand-voice-generator** | Analyze and document a brand's communication style |

### 🧠 AI Tools
| Skill | When to Use |
|-------|-------------|
| **prompt-benchmarker** | Compare prompt variations to find the best one |
| **model-comparator** | Compare AI models: pricing, context, benchmarks |
| **llm-output-validator** | Verify LLM output quality and accuracy |

### 🏝️ Lifestyle
| Skill | When to Use |
|-------|-------------|
| **travel-itinerary-planner** | Day-by-day trip plans with budget, dining, logistics |
| **gift-finder** | Find the perfect gift for someone |
| **recipe-generator** | Generate recipes from ingredients you have |
| **fitness-planner** | Weekly workout plans based on goals and equipment |
| **habit-tracker** | Define habits, check in daily, monitor streaks, get weekly summaries |

---

## How to Use

```bash
# Load this skill
hermes -s skill-hub

# Then just say what you want
# "I want to check a website's tech stack"
# "有什么技能可以分析竞品？"
# "I need to create a project from scratch"
```
