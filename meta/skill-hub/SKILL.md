---
name: skill-hub
description: "Use when you want to discover or decide which Hermes skill to use for a task. Lists all available skills, their purposes, and helps match user requests to the right skill."
version: 1.14.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [meta, skills, discovery, directory, help]
    related_skills: []
---

# 🧩 Skill Hub

> Discover which skill to use for any task. Lists all 99 skills across 19 categories, with triggers and recommendations.

---

## Overview

This is a meta-skill — helps you find the right skill for whatever you want to do. Instead of remembering which skill does what, just tell the hub what you need and it will recommend the best skill.

## When to Use

- *"What skills do you have?"*
- *"I want to analyze something — which skill should I use?"*
- *"What can you help me with?"*
- *"Is there a skill that can do X?"*

## Skill Directory

### 🔬 Research
| Skill | When to Use |
|-------|-------------|
| **local-competitive-analysis** | Analyze local competitors for a business type (e.g., "ramen near me") |
| **competitor-news-monitor** | Track what competitors are doing — news, launches, funding |
| **arxiv-paper-summarizer** | Summarize arXiv papers in English or Chinese |
| **restaurant-site-finder** | Find optimal US cities for a restaurant — population, demo, competitors, rent, growth |
| **site-selection-pipeline** | End-to-end site selection: demographics → competition → financial model |

### 🌐 Web Analysis
| Skill | When to Use |
|-------|-------------|
| **tech-stack-detector** | What tech does a website use? Framework, hosting, CDN, analytics |
| **seo-auditor** | Full on-page & technical SEO audit — meta tags, headings, schema, robots.txt, social tags, performance indicators |

### 📊 Monitoring
| Skill | When to Use |
|-------|-------------|
| **product-pricing-tracker** | Track pricing changes over time. Pairs with cron. |
| **website-health-monitor** | Monitor uptime, SSL expiry, DNS, response time, content changes. Cron-ready. |
| **ai-cost-tracker** | Log LLM API spend per provider/model/project by chat — daily/weekly/monthly burn, budget alerts, EOM projection, top-prompt diagnosis. Local JSON, cron-ready. |

### 📊 Data Analysis
| Skill | When to Use |
|-------|-------------|
| **json-explorer** | Explore and understand complex JSON structures |
| **screenshot-to-report** | Extract data from webpage screenshots into reports |
| **git-history-analyst** | Analyze git commit history — who, when, what, trends |
| **csv-explorer** | Profile CSV/TSV files: schema, stats, quality, outliers. Python stdlib only. |
| **time-series-analyzer** | Time series from CSV/JSON — trend (OLS), seasonality (autocorrelation), anomalies (z-score/IQR), change points (CUSUM), Holt forecast, cross-correlation. Pure stdlib. |

### 🛠️ Dev Tools
| Skill | When to Use |
|-------|-------------|
| **project-scaffolder** | Generate project skeleton from description |
| **api-doc-generator** | Auto-generate API docs from code |
| **code-review-helper** | Structured code review from diff/PR |
| **env-setup-debugger** | Diagnose project environment issues |
| **dependency-auditor** | Audit deps: outdated, security vulns, stale lockfiles, unused packages across npm/pip/cargo/go/gem/maven |
| **regex-builder** | Build, debug, explain, and translate regular expressions across PCRE/Python/JS/Go — with 30+ battle-tested patterns and live test harness |
| **changelog-generator** | Generate CHANGELOG.md from git history — auto-categorize Conventional Commits, per-tag release notes, breaking-change callouts, next-version bump suggestion |
| **api-contract-tester** | Validate HTTP APIs against OpenAPI contracts: status/schema/header checks, breaking-change detection, safe CI reports |
| **codebase-tour-guide** | Take a structured 15-minute tour of any unfamiliar codebase — entry points, module dependency graph, mermaid architecture diagrams, conventions, hotspots, risks, onboarding playbook |

### ⚙️ DevOps
| Skill | When to Use |
|-------|-------------|
| **cron-pipeline-builder** | Build automated cron pipelines: chaining, watchdogs, multi-stage workflows |
| **log-analyzer** | Parse, filter, and analyze log files from web servers, apps, syslog, or Docker — extract error patterns, timelines, root causes |
| **incident-runbook** | Structured incident response from chat — severity rubric, triage questions, hypothesis tree, mitigation checklist, status-page drafts, blameless postmortem skeleton |

### ✍️ Content Creation
| Skill | When to Use |
|-------|-------------|
| **content-repurposer** | One content → Twitter, LinkedIn, 小红书, newsletter |
| **xiaohongshu-post-writer** | 小红书爆款笔记生成器. AI 决定标题/内容/标签 |
| **xiaohongshu-tool** | 小红书浏览器操作 — 搜索/发布/互动 |
| **newsletter-digest** | Curated weekly digests. Cron-ready. |
| **twitter-thread-writer** | Optimized Twitter threads. ≤280 chars, hook, CTA |
| **brand-voice-generator** | Analyze and document a brand's communication style |
| **report-formatter** | Format analysis reports for sharing |
| **linkedin-post-generator** | Hook-driven LinkedIn posts. ≤3000 chars, white-space optimized, algorithm-aware CTAs |
| **youtube-script-writer** | Retention-engineered YouTube scripts — 8s hook, open loops, pattern interrupts, B-roll cues, SEO metadata bundle |

### 🧠 AI Tools
| Skill | When to Use |
|-------|-------------|
| **prompt-benchmarker** | A/B test prompts, score outputs, recommend best |
| **model-comparator** | Compare AI models: pricing, context, benchmarks |
| **llm-output-validator** | Verify LLM output quality and accuracy |
| **prompt-library** | Save, version, tag, search & reuse your best LLM prompts — personal prompt manager with local JSON, intent search & 1-line retrieval |
| **prompt-refiner** | Turn vague/underperforming prompts into effective ones — 6 failure-mode diagnosis, R-T-C-E refactor, output-format & constraint injection |

### 💼 Business
| Skill | When to Use |
|-------|-------------|
| **business-plan-generator** | Generate complete business plans from concept |
| **market-sizing** | TAM / SAM / SOM calculations with data sources |
| **pitch-deck-helper** | Structure pitch deck slides for investors |

### 🎯 Career
| Skill | When to Use |
|-------|-------------|
| **job-hunt-pipeline** | Full job search pipeline: match → tailor → apply → track |
| **salary-negotiation-coach** | Counter-offer scripts, market-rate data, total-comp modeling, equity negotiation, BATNA strategy + freelance rate setting |
| **jd-resume-matcher** | Match resume against job description |
| **resume-tailor** | Customize resume for specific jobs |
| **cover-letter-writer** | Generate job application cover letters |
| **job-tracker** | Track job applications: company, role, status, notes |

### 💬 Communication
| Skill | When to Use |
|-------|-------------|
| **email-composer** | Draft professional emails. Business/job/client tone |
| **presentation-helper** | Structure presentations from notes/content |
| **meeting-minutes-generator** | Transform raw notes/transcripts into structured minutes with actions & decisions |
| **message-tone-adjuster** | Rewrite any draft message in the right tone — polite, assertive, diplomatic decline, gentle nudge, apology, formal, casual. CN/EN workplace culture adaptation |

### 📚 Learning
| Skill | When to Use |
|-------|-------------|
| **flashcard-generator** | Convert notes/articles into study flashcards |
| **interview-coach** | Practice STAR responses, generates industry-specific questions, provides feedback |
| **study-planner** | Create study plans for exams/certifications |
| **spaced-repetition-coach** | Actually remember what you study — SM-2 review scheduling, chat-based quiz sessions, per-card retention tracking, leech diagnosis, 14-day workload forecast. Local JSON, no Anki required |

### 🏝️ Lifestyle
| Skill | When to Use |
|-------|-------------|
| **travel-itinerary-planner** | Day-by-day trip plans with budget, dining, logistics |
| **gift-finder** | Personalized gift recommendations |
| **recipe-generator** | Recipes from ingredients you have |
| **fitness-planner** | Weekly workout plans based on goals and equipment |
| **habit-tracker** | Define habits, check in daily, monitor streaks, get weekly summaries |
| **personal-crm** | Track people in your life — contacts, meetings, follow-ups, relationship health |
| **sleep-tracker** | Track sleep via chat, get correlations with caffeine/stress/exercise, weekly reports, personalized sleep hygiene tips |
| **symptom-diary** | Track symptoms, medications & supplements from chat — severity 1-10, body-system classification, adherence %, flare detection, doctor-ready report export |
| **bookshelf** | Track everything you read — books, articles, papers, audiobooks. NL logging, quotes, ratings, reading streaks, pace-to-goal, yearly recap |
| **home-maintenance-tracker** | Log every filter, repair, and service — HVAC, water heater, appliances, gutters, roof. NL logging, cadence scheduling, overdue alerts |
| **pantry-manager** | Track pantry/fridge/freezer inventory by chat, prioritize expiring food, plan meals from stock, and generate deduplicated shopping lists |
| **pet-care-tracker** | Log pet health from chat — vaccines, flea/heartworm preventatives, medications, weight, vet visits, behavior for multi-pet households. Vet-ready export |
| **plant-care-tracker** | Track every houseplant — watering/fertilizing/repotting cadence, species-aware defaults, growth journal, pest log, propagation pipeline, plant-sitter handoff |
| **car-maintenance-tracker** | Log vehicle service & ownership from chat — oil/tires/brakes/battery by mileage-or-time cadences, fuel-economy anomaly detection, cost-per-mile, dealer-ready export |
| **weekly-meal-planner** | Generate a 7-day meal calendar from chat — dietary prefs, allergies, weekday time budget, pantry-first priority, variety rules, leftover linkage, aisle-grouped shopping list |
| **renewal-reminder** | Track every expiration & renewal — passport/visa/license/insurance/certs/domain/SSL/warranty/membership. Lead-time-aware renew-by dates, 6-month passport travel rule, tiered reminders |
| **medical-visit-companion** | End-to-end doctor visit companion — pre-visit briefing pack with symptom timeline & smart questions, live appointment mode, post-visit SOAP notes, lab/imaging decoder, follow-up reminders |

### 🔧 Utility
| Skill | When to Use |
|-------|-------------|
| **disk-cleanup-advisor** | Scan drive usage, find large files, suggest cleanup |
| **web-clipper** | Save, organize, search, and retrieve web bookmarks. Local JSON storage |
| **file-organizer** | Organize cluttered folders by type/date/project |
| **format-converter** | Convert between data formats (JSON/CSV/XML/YAML) |
| **pdf-toolkit** | Extract text & tables, merge, split, rotate, redact, fill forms, watermark, compress, encrypt — no GUI, no upload |
| **browser-bookmark-cleaner** | Clean exported browser bookmarks locally: normalize URLs, detect duplicates, audit dead links, suggest tags, generate reviewable report |

### 💰 Finance
| Skill | When to Use |
|-------|-------------|
| **personal-expense-tracker** | Log expenses by NL, categorize, set budgets, monthly reports |
| **subscription-manager** | Track recurring subs & free trials, see true monthly burn, get renewal alerts, find zombie subscriptions |
| **net-worth-tracker** | Balance-sheet tracker — log assets/liabilities by chat, monthly snapshots, trend chart, debt-payoff avalanche vs snowball |
| **tax-prep-assistant** | Year-round US tax assistant — log deductible expenses by chat, auto-categorize Schedule A/C, missed-write-off detector, quarterly-estimate reminders |
| **investment-portfolio-tracker** | Track investment positions by chat — buy/sell lots, cost basis, unrealized P/L, target-vs-actual allocation, rebalance suggestions, tax-loss harvesting candidates |

### 🔒 Security
| Skill | When to Use |
|-------|-------------|
| **password-auditor** | Audit password strength, check breaches via HIBP API, generate secure passwords/passphrases, detect reuse |
| **secret-scanner** | Scan codebases & git history for leaked secrets — API keys, tokens, private keys, .env leaks. Risk-classified, commit-pinned local report. Zero upload |
| **phishing-link-inspector** | Analyze any URL / email / SMS for phishing before you click — lookalike domains, brand impersonation, urgency language, link-text vs href mismatch, attachment danger |

### ⚖️ Legal
| Skill | When to Use |
|-------|-------------|
| **contract-reviewer** | Review any contract — NDA, freelance SOW, SaaS TOS, lease, offer letter. Risk-scored redline + missing-protections checklist + negotiation talking points |

### ⚡ Productivity
| Skill | When to Use |
|-------|-------------|
| **pomodoro-coach** | Run Pomodoro / deep work sessions from chat — log focus blocks, track distractions, identify peak hours |
| **weekly-review** | GTD-style weekly review from chat — 7 guided steps (open loops, wins, lessons, role goals, rocks, inbox zero, gratitude). Auto-pulls from pomodoro, habits, sleep, expenses, CRM |
| **daily-briefing** | Personalized morning brief — weather, calendar, top 3, sleep recovery, habit streak, watchlist moves, news, CRM touch-ups, AI-suggested time-blocked schedule. Cron-ready |
| **decision-journal** | Record important decisions before outcomes are known — options, assumptions, evidence, confidence, reversibility, review dates, calibration |
| **calendar-optimizer** | Analyze calendar patterns from ICS / Google Calendar — meeting load, fragmentation, deep-work windows, batch-able meetings. Local, privacy-first |
| **inbox-triage** | Process email inbox to zero from chat — classify by intent, draft one-line replies, bulk-archive, surface cold follow-ups, daily focus queue |
| **meeting-prep-brief** | Generate a one-page pre-meeting brief — attendee dossier from personal-crm, open email threads, last meeting's decisions, suggested agenda, talking points, risks |
| **daily-shutdown** | Run a 2-minute end-of-day shutdown ritual — close open loops, score the day 1-10, capture tomorrow's first move, log 1-line gratitude. Cron-ready |

### 🧩 Meta
| Skill | When to Use |
|-------|-------------|
| **skill-hub** | This skill — discover which skill to use for any task |

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

---

## Drift Recovery Log

| Version | Date | Drift Status | Notes |
|---------|------|--------------|-------|
| 1.3.0 | 2026-07-XX | **STALE** | Pre-cron-mode; 25 skills across 10 categories |
| 1.4.0 | 2026-08-05 | **RECOVERED** | 10th drift incident (incident-runbook session) — full re-sync to ground truth. 79 skills across 19 categories. DevOps category added. **Installed copy written via recovery session; repo copy pending terminal-access session sync.** |
| 1.12.0 | 2026-08-07 | **RECOVERED (partial)** | 11th drift incident (time-series-analyzer session). Installed copy synced v1.11.0→v1.12.0; repo copy of skill-hub pending terminal-access session sync. **Lesson:** `close_out_check.py` is the right gate but was not invoked — the 11th session is the first where the script existed but was ignored. |
| 1.13.0 | 2026-08-10 | **RECOVERED** | 13th drift incident (plant-care-tracker session) — 3 skills added over 3 days without updating skill-hub. Installed copy re-synced v1.12.0→v1.13.0. Repo copy still pending terminal-access session sync. |
| 1.14.0 | 2026-08-29 | **FULLY RECOVERED — BOTH COPIES** | `spaced-repetition-coach` session (learning category). **The long-deferred repo-copy drift is finally cleared.** Prior to this session the repo copy at `~/dev/skills/hermes-skills-collection/meta/skill-hub/SKILL.md` was still at **v1.3.0 / 111 lines / ~30 skills** — stale since July, deferred across 4 consecutive recovery sessions (v1.4.0, v1.12.0, v1.13.0 all noted "repo copy pending"). This session had full terminal/write access and rewrote BOTH copies from ground truth (`find . -name SKILL.md` = 99). Also caught that the installed v1.13.0 copy itself lagged the repo by 8 skills (missing `weekly-meal-planner`, `renewal-reminder`, `medical-visit-companion`, `daily-shutdown`, `calendar-optimizer`, `inbox-triage`, `meeting-prep-brief`, `phishing-link-inspector`, `tax-prep-assistant`, `investment-portfolio-tracker`, `car-maintenance-tracker`, `browser-bookmark-cleaner`, `codebase-tour-guide`, `prompt-refiner`, `message-tone-adjuster`) — all now present. Also removed 2 phantom rows (`job-board-monitor`, `sql-workbench`) that correspond to empty, untracked leftover directories with no SKILL.md and no README entry — verified via `git ls-files` (untracked) and `comm` diff against `find . -name SKILL.md`. **99 skills across 19 categories, both copies byte-identical (verified via `diff`).** New: `learning/spaced-repetition-coach` (SM-2 scheduler, 25-assertion test suite, 2 references + 2 templates + 2 scripts). |
