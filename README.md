# 🧩 Hermes Skills Collection

A curated collection of reusable [Hermes Agent](https://hermes-agent.nousresearch.com) skills, organized by category. Each skill provides a structured workflow that Hermes can follow to complete complex tasks — from market research to creative work.

---

## 📁 Structure

```
hermes-skills-collection/
├── README.md
├── research/                         ← 市场调研类
│   ├── local-competitive-analysis/
│   ├── arxiv-paper-summarizer/
│   └── competitor-news-monitor/
├── web-analysis/                     ← Web 技术分析类
│   └── tech-stack-detector/
├── monitoring/                       ← 定时监控类
│   └── product-pricing-tracker/
├── content-creation/                 ← 内容创作类
│   ├── newsletter-digest/
│   └── content-repurposer/
├── dev-tools/                        ← 开发工具类
│   └── project-scaffolder/
└── lifestyle/                        ← 生活出行类
    └── travel-itinerary-planner/
```

---

## 📦 Skills

### 🔬 Research

| Skill | Description | Parameters | Install |
|-------|-------------|------------|---------|
| **local-competitive-analysis** | Analyze local competitors. Auto-detects location via IP. SWOT, market gap, strategic recommendations. | `industry` (req), `location` (opt) | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/research/local-competitive-analysis/SKILL.md) |
| **competitor-news-monitor** | Monitor competitors for news, launches, funding, market moves. Pairs with cron for automated briefings. | `competitor_list` (req) | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/research/competitor-news-monitor/SKILL.md) |
| **arxiv-paper-summarizer** | Summarize arXiv papers in English or Chinese. Extracts method, results, limitations. Supports batch + cron monitoring. | `paper_id` or `search_query` (req) | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/research/arxiv-paper-summarizer/SKILL.md) |

### 🌐 Web Analysis

| Skill | Description | Parameters | Install |
|-------|-------------|------------|---------|
| **tech-stack-detector** | Detect frameworks, CDNs, hosting, analytics, JS libs from any URL using headers, HTML, browser globals, DNS, SSL. | `url` (req) | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/web-analysis/tech-stack-detector/SKILL.md) |

### 📊 Monitoring

| Skill | Description | Parameters | Install |
|-------|-------------|------------|---------|
| **product-pricing-tracker** | Track pricing changes over time. Baseline snapshot + change detection. Pairs with cron for recurring checks. | `url` (req), `product_name` (req) | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/monitoring/product-pricing-tracker/SKILL.md) |

### ✍️ Content Creation

| Skill | Description | Parameters | Install |
|-------|-------------|------------|---------|
| **newsletter-digest** | Generate curated newsletters / weekly digests on any topic. Multi-source research + polished template. | `topic` (req), `timeframe`/`language` (opt) | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/newsletter-digest/SKILL.md) |
| **content-repurposer** | One piece of content → Twitter thread, LinkedIn post, 小红书文案, newsletter blurb, key takeaways. | `source` (req), `formats` (req) | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/content-repurposer/SKILL.md) |

### 🛠️ Dev Tools

| Skill | Description | Parameters | Install |
|-------|-------------|------------|---------|
| **project-scaffolder** | Generate complete project skeleton from natural language. Config files, .gitignore, README, optional git init. | `description` (req — e.g. "FastAPI + SQLAlchemy") | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/project-scaffolder/SKILL.md) |

### 🏝️ Lifestyle

| Skill | Description | Parameters | Install |
|-------|-------------|------------|---------|
| **travel-itinerary-planner** | Day-by-day travel itinerary. Attractions, dining, logistics, budget, packing list, alternative plans. | `destination` (req), `days` (req), `style`/`interests` (opt) | [install](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/travel-itinerary-planner/SKILL.md) |

---

## 🚀 Usage

### Install a skill

```bash
hermes skills install <raw-url-to-SKILL.md>
```

### Use a skill

```bash
hermes -s local-competitive-analysis
# or
hermes -s tech-stack-detector
```

Then prompt:

> *"Analyze the ramen market in Shibuya, Tokyo"*
> *"What tech stack does stripe.com use?"*
> *"Track Notion's pricing for me"*
> *"Monitor OpenAI, Anthropic, and Google DeepMind"*
> *"Summarize https://arxiv.org/abs/2401.12345"*
> *"帮我总结这篇 arxiv 论文，用中文"*
> *"Generate a weekly AI newsletter about LLMs"*
> *"Turn this blog post into a Twitter thread"*
> *"Scaffold a FastAPI project with SQLAlchemy and pytest"*
> *"Plan a 4-day trip to Kyoto"*

---

## ➕ Adding a New Skill

1. Pick a category (or create a new one)
2. Create `SKILL.md` with proper frontmatter (name, description, version, author, license, tags, related_skills)
3. Add your skill to the table in this README
4. Commit and push

---

## 📝 License

MIT — feel free to use, share, and contribute.
