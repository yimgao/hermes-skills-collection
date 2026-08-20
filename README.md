# 🧩 Hermes Skills Collection

A curated collection of reusable [Hermes Agent](https://hermes-agent.nousresearch.com) skills, organized by category. Each skill provides a structured workflow that Hermes can follow to complete complex tasks.

**90 skills · 19 categories**

---

## 📁 Structure

```text
hermes-skills-collection/
├── meta/              ← 技能中心 (1)
├── research/          ← 市场调研类 (5)
├── web-analysis/      ← Web 技术分析类 (2)
├── monitoring/        ← 定时监控类 (3)
├── business/          ← 商业计划类 (3)
├── career/            ← 求职求职类 (6)
├── communication/     ← 沟通写作类 (3)
├── data-analysis/     ← 数据分析类 (5)
├── content-creation/  ← 内容创作类 (9)
├── dev-tools/         ← 开发工具类 (9)
├── devops/            ← CI/CD 与自动化类 (3)
├── ai-tools/          ← AI 工具类 (4)
├── learning/          ← 学习规划类 (3)
├── lifestyle/         ← 生活出行类 (14)
├── utility/           ← 系统工具类 (6)
├── finance/           ← 个人财务类 (5)
├── security/          ← 安全审计类 (2)
├── legal/             ← 法律合同类 (1)
└── productivity/      ← 专注力与时间管理类 (5)
```

---

## 📦 Skills

### 🧩 Meta

| Skill | Description | Install |
|-------|-------------|---------|
| **skill-hub** | Discover which skill to use for any task. Lists all skills with triggers and recommendations. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/meta/skill-hub/SKILL.md) |

### 🔬 Research

| Skill | Description | Install |
|-------|-------------|---------|
| **local-competitive-analysis** | Analyze local competitors. Auto IP location. SWOT + market gap. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/research/local-competitive-analysis/SKILL.md) |
| **competitor-news-monitor** | Track competitor news, launches, funding. Pairs with cron. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/research/competitor-news-monitor/SKILL.md) |
| **arxiv-paper-summarizer** | Summarize arXiv papers. English/中文. Batch + cron. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/research/arxiv-paper-summarizer/SKILL.md) |
| **restaurant-site-finder** | Find optimal US cities for a restaurant. Population, demo, competitors, rent, growth. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/research/restaurant-site-finder/SKILL.md) |
| **site-selection-pipeline** | End-to-end site selection: demographics → competition → financial model. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/research/site-selection-pipeline/SKILL.md) |

### 🌐 Web Analysis

| Skill | Description | Install |
|-------|-------------|---------|
| **tech-stack-detector** | Detect frameworks, CDN, hosting, analytics from any URL. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/web-analysis/tech-stack-detector/SKILL.md) |
| **seo-auditor** | Full on-page & technical SEO audit — meta tags, headings, schema, robots.txt, social tags, performance indicators. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/web-analysis/seo-auditor/SKILL.md) |

### 📊 Monitoring

| Skill | Description | Install |
|-------|-------------|---------|
| **product-pricing-tracker** | Track pricing changes. Baseline + cron. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/monitoring/product-pricing-tracker/SKILL.md) |
| **website-health-monitor** | Monitor uptime, SSL expiry, DNS, response time, content changes. Cron-ready. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/monitoring/website-health-monitor/SKILL.md) |
| **ai-cost-tracker** | Log LLM API spend per provider/model/project by chat — daily/weekly/monthly burn, budget alerts, EOM projection, top-prompt diagnosis. Local JSON, cron-ready. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/monitoring/ai-cost-tracker/SKILL.md) |

### 📊 Data Analysis

| Skill | Description | Install |
|-------|-------------|---------|
| **json-explorer** | Explore complex JSON: schema, depth, types, anomalies. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/data-analysis/json-explorer/SKILL.md) |
| **screenshot-to-report** | Extract data from screenshots/images into structured reports. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/data-analysis/screenshot-to-report/SKILL.md) |
| **git-history-analyst** | Analyze git repos: contributors, churn, hotspots, trends. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/data-analysis/git-history-analyst/SKILL.md) |
| **csv-explorer** | Profile CSV/TSV files: schema, stats, quality, outliers. Python stdlib only. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/data-analysis/csv-explorer/SKILL.md) |
| **time-series-analyzer** | Time series from CSV/JSON — trend (OLS), seasonality (autocorrelation), anomalies (z-score/IQR), change points (CUSUM), Holt forecast, cross-correlation. Pure stdlib. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/data-analysis/time-series-analyzer/SKILL.md) |

### 🛠️ Dev Tools

| Skill | Description | Install |
|-------|-------------|---------|
| **project-scaffolder** | Generate project skeletons from description. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/project-scaffolder/SKILL.md) |
| **api-doc-generator** | Auto-generate API docs from code routes/schemas. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/api-doc-generator/SKILL.md) |
| **code-review-helper** | Structured code review from diffs/PRs. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/code-review-helper/SKILL.md) |
| **env-setup-debugger** | Diagnose project environment issues. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/env-setup-debugger/SKILL.md) |
| **dependency-auditor** | Audit deps: outdated, security vulns, stale lockfiles, unused packages across npm/pip/cargo/go/gem/maven. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/dependency-auditor/SKILL.md) |
| **regex-builder** | Build, debug, explain, and translate regular expressions across PCRE/Python/JS/Go — with 30+ battle-tested patterns and live test harness. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/regex-builder/SKILL.md) |
| **changelog-generator** | Generate CHANGELOG.md from git history — auto-categorize Conventional Commits, per-tag release notes, breaking-change callouts, next-version bump suggestion, Keep-a-Changelog or Conventional output. Zero external deps. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/changelog-generator/SKILL.md) |
| **api-contract-tester** | Validate HTTP APIs against OpenAPI contracts: status/schema/header checks, breaking-change detection, safe CI reports. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/api-contract-tester/SKILL.md) |
| **codebase-tour-guide** | Take a structured 15-minute tour of any unfamiliar codebase — entry points, module dependency graph, mermaid architecture diagrams, conventions, hotspots, risks, and onboarding playbook. Static read-only analysis, zero execution. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/codebase-tour-guide/SKILL.md) |

### ⚙️ DevOps

| Skill | Description | Install |
|-------|-------------|---------|
| **cron-pipeline-builder** | Build automated cron pipelines: chaining, watchdogs, multi-stage workflows. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/devops/cron-pipeline-builder/SKILL.md) |
| **log-analyzer** | Parse, filter, and analyze log files from web servers, apps, syslog, or Docker — extract error patterns, timelines, and root causes using grep/awk/jq/Python. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/devops/log-analyzer/SKILL.md) |
| **incident-runbook** | Structured incident response from chat — severity rubric, triage questions, hypothesis tree, mitigation checklist, status-page drafts, blameless postmortem skeleton. Local Markdown. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/devops/incident-runbook/SKILL.md) |

### ✍️ Content Creation

| Skill | Description | Install |
|-------|-------------|---------|
| **content-repurposer** | One content → Twitter, LinkedIn, 小红书, newsletter. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/content-repurposer/SKILL.md) |
| **xiaohongshu-post-writer** | 小红书爆款笔记生成器. AI 决定标题/内容/标签. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/xiaohongshu-post-writer/SKILL.md) |
| **xiaohongshu-tool** | 小红书浏览器操作 — 搜索/发布/互动. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/xiaohongshu-tool/SKILL.md) |
| **newsletter-digest** | Curated weekly digests. Cron-ready. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/newsletter-digest/SKILL.md) |
| **twitter-thread-writer** | Optimized Twitter threads. ≤280 chars, hook, CTA. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/twitter-thread-writer/SKILL.md) |
| **brand-voice-generator** | Analyze brand communication → voice guide. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/brand-voice-generator/SKILL.md) |
| **report-formatter** | Format analysis reports for sharing. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/report-formatter/SKILL.md) |
| **linkedin-post-generator** | Hook-driven LinkedIn posts. ≤3000 chars, white-space optimized, algorithm-aware CTAs. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/linkedin-post-generator/SKILL.md) |
| **youtube-script-writer** | Retention-engineered YouTube scripts — 8s hook, open loops, pattern interrupts, B-roll cues, SEO metadata bundle. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/youtube-script-writer/SKILL.md) |

### 🧠 AI Tools

| Skill | Description | Install |
|-------|-------------|---------|
| **prompt-benchmarker** | A/B test prompts, score outputs, recommend best. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/ai-tools/prompt-benchmarker/SKILL.md) |
| **model-comparator** | Compare AI models: pricing, context, benchmarks. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/ai-tools/model-comparator/SKILL.md) |
| **llm-output-validator** | Verify LLM output: facts, format, consistency. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/ai-tools/llm-output-validator/SKILL.md) |
| **prompt-library** | Save, version, tag, search & reuse your best LLM prompts — personal prompt manager with local JSON, intent search & 1-line retrieval. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/ai-tools/prompt-library/SKILL.md) |

### 💼 Business

| Skill | Description | Install |
|-------|-------------|---------|
| **business-plan-generator** | Generate complete business plans from concept. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/business/business-plan-generator/SKILL.md) |
| **market-sizing** | TAM / SAM / SOM calculations with data sources. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/business/market-sizing/SKILL.md) |
| **pitch-deck-helper** | Structure pitch deck slides for investors. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/business/pitch-deck-helper/SKILL.md) |

### 🎯 Career

| Skill | Description | Install |
|-------|-------------|---------|
| **job-hunt-pipeline** | Full job search pipeline: match → tailor → apply → track. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/career/job-hunt-pipeline/SKILL.md) |
| **salary-negotiation-coach** | Counter-offer scripts, market-rate data, total-comp modeling, equity negotiation, BATNA strategy + freelance rate setting. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/career/salary-negotiation-coach/SKILL.md) |
| **jd-resume-matcher** | Match resume against job description. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/career/jd-resume-matcher/SKILL.md) |
| **resume-tailor** | Customize resume for specific jobs. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/career/resume-tailor/SKILL.md) |
| **cover-letter-writer** | Generate job application cover letters. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/career/cover-letter-writer/SKILL.md) |
| **job-tracker** | Track job applications: company, role, status, notes. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/career/job-tracker/SKILL.md) |

### 💬 Communication

| Skill | Description | Install |
|-------|-------------|---------|
| **email-composer** | Draft professional emails. Business/job/client tone. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/communication/email-composer/SKILL.md) |
| **presentation-helper** | Structure presentations from notes/content. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/communication/presentation-helper/SKILL.md) |
| **meeting-minutes-generator** | Transform raw notes/transcripts into structured minutes with actions & decisions. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/communication/meeting-minutes-generator/SKILL.md) |

### 📚 Learning

| Skill | Description | Install |
|-------|-------------|---------|
| **flashcard-generator** | Convert notes/articles into study flashcards. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/learning/flashcard-generator/SKILL.md) |
| **interview-coach** | Practice STAR method interviews with feedback. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/learning/interview-coach/SKILL.md) |
| **study-planner** | Create study plans for exams/certifications. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/learning/study-planner/SKILL.md) |

### 🏝️ Lifestyle

| Skill | Description | Install |
|-------|-------------|---------|
| **travel-itinerary-planner** | Day-by-day trip plans with budget + logistics. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/travel-itinerary-planner/SKILL.md) |
| **gift-finder** | Personalized gift recommendations. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/gift-finder/SKILL.md) |
| **recipe-generator** | Recipes from ingredients you have. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/recipe-generator/SKILL.md) |
| **fitness-planner** | Weekly workout plans. Goals + equipment based. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/fitness-planner/SKILL.md) |
| **habit-tracker** | Define habits, check in daily, track streaks, get weekly summaries. Local JSON storage. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/habit-tracker/SKILL.md) |
| **personal-crm** | Track people in your life — contacts, meetings, follow-ups, relationship health. Local JSON, zero cloud. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/personal-crm/SKILL.md) |
| **sleep-tracker** | Log sleep via chat, get correlations with caffeine/stress/exercise, weekly reports, personalized sleep hygiene tips. All data local. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/sleep-tracker/SKILL.md) |
| **symptom-diary** | Track symptoms, medications & supplements from chat — severity 1-10, body-system classification, adherence %, flare detection, side-effect flagging, doctor-ready report export. All data local. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/symptom-diary/SKILL.md) |
| **bookshelf** | Track everything you read — books, articles, papers, audiobooks. NL logging, quotes, ratings, reading streaks, pace-to-goal, yearly recap, re-read reminders. All data local JSON. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/bookshelf/SKILL.md) |
| **home-maintenance-tracker** | Log every filter, repair, and service — HVAC, water heater, appliances, gutters, roof. NL logging, cadence scheduling, overdue alerts, warranty tracking, seasonal playbook, annual cost report. All data local JSON. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/home-maintenance-tracker/SKILL.md) |
| **pantry-manager** | Track pantry/fridge/freezer inventory by chat, prioritize expiring food, plan meals from stock, and generate deduplicated shopping lists. Local JSON. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/pantry-manager/SKILL.md) |
| **pet-care-tracker** | Log pet health from chat — vaccines, flea/heartworm preventatives, medications, weight, vet visits, behavior for multi-pet households. Vet-ready export. Local JSON. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/pet-care-tracker/SKILL.md) |
| **plant-care-tracker** | Track every houseplant — watering/fertilizing/repotting cadence, species-aware defaults, growth journal, pest log, propagation pipeline, plant-sitter handoff. Local JSON. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/plant-care-tracker/SKILL.md) |
| **car-maintenance-tracker** | Log vehicle service & ownership from chat — oil/tires/brakes/battery by mileage-or-time cadences, fuel-economy anomaly detection, registration/insurance/warranty tracking, cost-per-mile, dealer-ready service record export. Multi-vehicle, local JSON, privacy-first. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/car-maintenance-tracker/SKILL.md) |

### 🔧 Utility

| Skill | Description | Install |
|-------|-------------|---------|
| **disk-cleanup-advisor** | Scan drive usage, find large files, suggest cleanup. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/utility/disk-cleanup-advisor/SKILL.md) |
| **web-clipper** | Save, organize, search, and retrieve web bookmarks. Local JSON storage. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/utility/web-clipper/SKILL.md) |
| **file-organizer** | Organize cluttered folders by type/date/project. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/utility/file-organizer/SKILL.md) |
| **format-converter** | Convert between data formats (JSON/CSV/XML/YAML). | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/utility/format-converter/SKILL.md) |
| **pdf-toolkit** | Extract text & tables, merge, split, rotate, redact, fill forms, watermark, compress, encrypt — no GUI, no upload. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/utility/pdf-toolkit/SKILL.md) |
| **browser-bookmark-cleaner** | Clean exported browser bookmarks locally: normalize URLs, detect duplicates, audit dead links, suggest tags, and generate a reviewable report without auto-deleting. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/utility/browser-bookmark-cleaner/SKILL.md) |

### 💰 Finance

| Skill | Description | Install |
|-------|-------------|---------|
| **personal-expense-tracker** | Log expenses by NL, categorize, set budgets, monthly reports — all through chat. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/finance/personal-expense-tracker/SKILL.md) |
| **subscription-manager** | Track recurring subs & free trials, see true monthly burn, get renewal alerts, and find zombie subscriptions you forgot you were paying for. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/finance/subscription-manager/SKILL.md) |
| **net-worth-tracker** | Balance-sheet tracker — log assets/liabilities by chat, monthly snapshots, trend chart, debt-payoff avalanche vs snowball, asset allocation. All local JSON. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/finance/net-worth-tracker/SKILL.md) |
| **tax-prep-assistant** | Year-round US tax assistant — log deductible expenses by chat, auto-categorize Schedule A/C, missed-write-off detector, quarterly-estimate reminders, Schedule preview + document checklist. All local JSON. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/finance/tax-prep-assistant/SKILL.md) |
| **investment-portfolio-tracker** | Track investment positions by chat — buy/sell lots, cost basis, unrealized P/L, target-vs-actual allocation, rebalance suggestions, dividends & interest, tax-loss harvesting candidates. All local JSON. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/finance/investment-portfolio-tracker/SKILL.md) |

### 🔒 Security

| Skill | Description | Install |
|-------|-------------|---------|
| **password-auditor** | Audit password strength, check breaches via HIBP API, generate secure passwords/passphrases, detect reuse. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/security/password-auditor/SKILL.md) |
| **secret-scanner** | Scan codebases & git history for leaked secrets — API keys, tokens, private keys, .env leaks. Risk-classified, commit-pinned local report. Zero upload. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/security/secret-scanner/SKILL.md) |

### ⚖️ Legal

| Skill | Description | Install |
|-------|-------------|---------|
| **contract-reviewer** | Review any contract — NDA, freelance SOW, SaaS TOS, lease, offer letter. Risk-scored redline + missing-protections checklist + email-ready negotiation talking points. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/legal/contract-reviewer/SKILL.md) |

### ⚡ Productivity

| Skill | Description | Install |
|-------|-------------|---------|
| **pomodoro-coach** | Run Pomodoro / deep work sessions from chat — log focus blocks, track distractions, identify your peak hours, daily & weekly focus reports. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/productivity/pomodoro-coach/SKILL.md) |
| **weekly-review** | GTD-style weekly review from chat — 7 guided steps (open loops, wins, lessons, role goals, rocks, inbox zero, gratitude). Auto-pulls from pomodoro, habits, sleep, expenses, CRM. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/productivity/weekly-review/SKILL.md) |
| **daily-briefing** | Personalized morning brief — weather, calendar, top 3, sleep recovery, habit streak, watchlist moves, news, CRM touch-ups, AI-suggested time-blocked schedule. Cron-ready. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/productivity/daily-briefing/SKILL.md) |
| **decision-journal** | Record important decisions before outcomes are known — options, assumptions, evidence, confidence, reversibility, review dates, and calibration. Local Markdown. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/productivity/decision-journal/SKILL.md) |
| **calendar-optimizer** | Analyze calendar patterns from ICS / Google Calendar — meeting load, fragmentation, deep-work windows, batch-able meetings. Local analysis, privacy-first. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/productivity/calendar-optimizer/SKILL.md) |
| **inbox-triage** | Process email inbox to zero from chat — classify every message by intent (reply_now / reply_later / fyi / receipt / newsletter / notification / spam), draft one-line replies, bulk-archive, surface cold follow-ups, daily focus queue. Local-only, privacy-first. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/productivity/inbox-triage/SKILL.md) |

---

## 🚀 Usage

```bash
# Install any skill
hermes skills install <raw-url>

# Use
hermes -s skill-hub
```

Then prompt:

> *"What skills do you have?"*
> *"Analyze the ramen market near me"*
> *"What tech stack does stripe.com use?"*
> *"Scaffold a FastAPI project"*
> *"Review my uncommitted changes"*
> *"Summarize arxiv 2401.09670"*
> *"Track Notion's pricing"*
> *"Monitor OpenAI this week"*
> *"I have chicken and broccoli — what can I cook?"*
> *"Plan a 4-day trip to Kyoto"*
> *"帮我写一篇小红书笔记"*
> *"帮我申请Google的SDE岗位"*
> *"I got a $165k offer from Stripe — help me counter to $185k"*
> *"Write a LinkedIn post about getting rejected by Y Combinator"*
> *"Set up a cron pipeline: collect news at 7AM, analyze at 7:05, deliver at 7:10"*
> *"Monitor disk space and alert me above 80%"*
> *"I just met Sarah at a meetup, add her to my CRM"*
> *"Who in my network haven't I talked to in 6 months?"*
| *I slept 11pm to 6:45am, felt tired, woke twice*
> *What affects my sleep the most?*
> *Show me my sleep debt this week*
> *Start a 25-min pomodoro on the launch deck*
> *When am I most productive this week?*
> *Sunday review time*
> *Show me my 4-week trend*
> *What keeps showing up as an open loop?*
> *Save this prompt as 'cold-email-v2'*
> *Find my prompt for writing investor updates*
> *Use linkedin-post-formula on: getting rejected by 7 VCs in a row*
> *Show me prompts I never used*
> *Review this freelance SOW — fair deal or red flags?*
> *I got a job offer with broad IP assignment — what should I push back on?*
> *Is this residential lease standard — can I negotiate the deposit clause?*
> *Add Project Hail Mary to my shelf — I just started it*
> *Log a quote from Meditations page 42: "You have power over your mind..."*
| *Generate my 2026 year-end reading recap*
| *Set up my net worth — I have $14k cash, $32k brokerage, $51k 401k, and $1,850 on a credit card*
| *What's my net worth trend over the last 6 months?*
| *Compare avalanche vs snowball for my 3 debts if I throw $500/mo extra*
| *I just changed the furnace filter — 16x25x1 MERV 11, $14*
| *What's due for home maintenance this month?*
| *My water heater warranty expired — what should I do?*
| *Generate my fall home maintenance playbook*
| *Morning briefing*
| *Give me my daily brief*
| *Plan my Tuesday*
| *"Record why I chose the managed database, then review the decision in 90 days"*
| *"Run an OpenAPI contract test against my staging API and fail CI on breaking responses"*
| *"Logged gpt-4o, project launch-deck, 8200 in / 1400 out"*
| *"What will I spend on AI this month end?"*
| *"Find the 5 most expensive calls this month"*
| *"Set my AI budget to $120/month, alert at 80%"*
| *"What's expiring in my fridge, and what can I cook tonight?"*
| *"Stripe webhooks are 500ing, walk me through the runbook"*
| *"Write a status page update — search latency is 4s for everyone in US"*
| *"Generate the postmortem for last Tuesday's 47-min checkout outage"*
| *Is this a SEV1? 12% of renewals are failing on the Stripe webhook* |
| *Gave Mochi her Heartgard and NexGard, 22.4 lb* |
| *What's overdue across all my pets this week?* |
| *Export Mochi's medical history for boarding next month* |
| *Bean (kitten) just got her FVRCP #2 — log it* |
| *Scan this repo for leaked API keys before I open-source it* |
| *Find which commit introduced my AWS key AKIA...* |
| *Watered the monstera, top inch dry* |
| *Set up a watering cadence for a new snake plant* |
| *Which plants are overdue this week?* |
| *Generate a care card for my plant-sitter, I'm traveling 10 days* |
| *I just propagated 4 pothos cuttings — who in my network would want one?* |
| *Found mealybugs on my hoya, treated with 70% isopropyl* |
| *I'm taking over a Python analytics-pipeline repo — give me a codebase tour* |
| *New intern joining Monday — generate an onboarding playbook from our backend* |
| *Triage my inbox — 47 unread, point at Apple Mail* |
| *What emails do I owe a reply to?* |
| *Show me today's focus queue* |
| *Archive every newsletter older than 30 days* |
| *Draft a 2-sentence reply to the Stripe webhook thread* |

## Skills 标准格式

每个 skill 遵循 Hermes 标准格式：

```yaml
---
name: skill-name
description: "One-line description of what this skill does"
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [category, keywords]
    related_skills: [other-skills]
---
```

每个 SKILL.md 包含：
1. **YAML frontmatter** — 元数据
2. **Overview** — 技能概述
3. **When to Use** — 什么时候用
4. **Workflow** — 步骤 1/2/3
5. **Common Pitfalls** — 常见陷阱
6. **Verification Checklist** — 验证清单
7. **Data Sources & Accuracy** — 数据来源说明

---

## 📝 License

MIT
