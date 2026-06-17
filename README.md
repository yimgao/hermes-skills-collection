# 🧩 Hermes Skills Collection

A curated collection of reusable [Hermes Agent](https://hermes-agent.nousresearch.com) skills, organized by category. Each skill provides a structured workflow that Hermes can follow to complete complex tasks.

**24 skills · 10 categories**

---

## 📁 Structure

```
hermes-skills-collection/
├── meta/                  ← 技能中心
├── research/              ← 市场调研类 (3)
├── web-analysis/          ← Web 技术分析类 (1)
├── monitoring/            ← 定时监控类 (1)
├── data-analysis/         ← 数据分析类 (3)
├── content-creation/      ← 内容创作类 (4)
├── dev-tools/             ← 开发工具类 (4)
├── ai-tools/              ← AI 工具类 (3)
└── lifestyle/             ← 生活出行类 (4)
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

### 🌐 Web Analysis
| Skill | Description | Install |
|-------|-------------|---------|
| **tech-stack-detector** | Detect frameworks, CDN, hosting, analytics from any URL. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/web-analysis/tech-stack-detector/SKILL.md) |

### 📊 Monitoring
| Skill | Description | Install |
|-------|-------------|---------|
| **product-pricing-tracker** | Track pricing changes. Baseline + cron. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/monitoring/product-pricing-tracker/SKILL.md) |

### 📊 Data Analysis
| Skill | Description | Install |
|-------|-------------|---------|
| **json-explorer** | Explore complex JSON: schema, depth, types, anomalies. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/data-analysis/json-explorer/SKILL.md) |
| **screenshot-to-report** | Extract data from screenshots/images into structured reports. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/data-analysis/screenshot-to-report/SKILL.md) |
| **git-history-analyst** | Analyze git repos: contributors, churn, hotspots, trends. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/data-analysis/git-history-analyst/SKILL.md) |

### 🛠️ Dev Tools
| Skill | Description | Install |
|-------|-------------|---------|
| **project-scaffolder** | Generate project skeletons from description. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/project-scaffolder/SKILL.md) |
| **api-doc-generator** | Auto-generate API docs from code routes/schemas. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/api-doc-generator/SKILL.md) |
| **code-review-helper** | Structured code review from diffs/PRs. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/code-review-helper/SKILL.md) |
| **env-setup-debugger** | Diagnose project environment issues. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/env-setup-debugger/SKILL.md) |

### ✍️ Content Creation
| Skill | Description | Install |
|-------|-------------|---------|
| **newsletter-digest** | Curated weekly digests. Cron-ready. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/newsletter-digest/SKILL.md) |
| **content-repurposer** | One content → Twitter, LinkedIn, 小红书, newsletter. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/content-repurposer/SKILL.md) |
| **twitter-thread-writer** | Optimized Twitter threads. ≤280 chars, hook, CTA. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/twitter-thread-writer/SKILL.md) |
| **brand-voice-generator** | Analyze brand communication → voice guide. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/brand-voice-generator/SKILL.md) |

### 🧠 AI Tools
| Skill | Description | Install |
|-------|-------------|---------|
| **prompt-benchmarker** | A/B test prompts, score outputs, recommend best. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/ai-tools/prompt-benchmarker/SKILL.md) |
| **model-comparator** | Compare AI models: pricing, context, benchmarks. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/ai-tools/model-comparator/SKILL.md) |
| **llm-output-validator** | Verify LLM output: facts, format, consistency. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/ai-tools/llm-output-validator/SKILL.md) |

### 🏝️ Lifestyle
| Skill | Description | Install |
|-------|-------------|---------|
| **travel-itinerary-planner** | Day-by-day trip plans with budget + logistics. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/travel-itinerary-planner/SKILL.md) |
| **gift-finder** | Personalized gift recommendations. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/gift-finder/SKILL.md) |
| **recipe-generator** | Recipes from ingredients you have. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/recipe-generator/SKILL.md) |
| **fitness-planner** | Weekly workout plans. Goals + equipment based. | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/fitness-planner/SKILL.md) |

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

---

## 📝 License

MIT
