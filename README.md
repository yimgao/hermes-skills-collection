# 🧩 Hermes Skills Collection

A curated collection of reusable [Hermes Agent](https://hermes-agent.nousresearch.com) skills, organized by category. Each skill provides a structured workflow that Hermes can follow to complete complex tasks — from market research to creative work.

---

## 📁 Structure

```
hermes-skills-collection/
├── README.md
├── research/                         ← 市场调研类
│   └── local-competitive-analysis/
│       └── SKILL.md
├── web-analysis/                     ← Web 技术分析类
│   └── tech-stack-detector/
│       └── SKILL.md
├── monitoring/                       ← 定时监控类
│   └── product-pricing-tracker/
│       └── SKILL.md
├── content-creation/                 ← 内容创作类
│   ├── newsletter-digest/
│   │   └── SKILL.md
│   └── content-repurposer/
│       └── SKILL.md
└── lifestyle/                        ← 生活出行类
    └── travel-itinerary-planner/
        └── SKILL.md
```

---

## 📦 Skills

### 🔬 Research

| Skill | Description | Parameters | Install |
|-------|-------------|------------|---------|
| **local-competitive-analysis** | Analyze local competitors for a specific business type in a given city. Auto-detects location via IP. Produces structured market reports with SWOT, market gap analysis, and strategic recommendations. | `industry` (req), `location` (opt) | [install link](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/research/local-competitive-analysis/SKILL.md) |

### 🌐 Web Analysis

| Skill | Description | Parameters | Install |
|-------|-------------|------------|---------|
| **tech-stack-detector** | Analyze any website's technology stack — detect frameworks, CDNs, analytics, hosting, and JS libraries from HTTP headers, HTML, browser globals, DNS, and SSL. | `url` (req) | [install link](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/web-analysis/tech-stack-detector/SKILL.md) |

### 📊 Monitoring

| Skill | Description | Parameters | Install |
|-------|-------------|------------|---------|
| **product-pricing-tracker** | Monitor competitor or product pricing over time. Scrapes pricing pages, detects changes (price drops/increases, new plans, removed features), and generates change reports. Designed to pair with cron for recurring checks. | `url` (req), `product_name` (req) | [install link](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/monitoring/product-pricing-tracker/SKILL.md) |

### ✍️ Content Creation

| Skill | Description | Parameters | Install |
|-------|-------------|------------|---------|
| **newsletter-digest** | Generate a curated newsletter or weekly digest on any topic. Searches multiple sources, summarizes key stories, and formats output as a polished newsletter ready to send. Pairs with cron for automation. | `topic` (req), `timeframe` (opt), `language` (opt) | [install link](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/newsletter-digest/SKILL.md) |
| **content-repurposer** | Transform a single piece of content into multiple platform-optimized formats: Twitter threads, LinkedIn posts, 小红书文案, newsletter blurbs, key takeaways, and more. | `source` (req — URL or text), `formats` (req) | [install link](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/content-creation/content-repurposer/SKILL.md) |

### 🏝️ Lifestyle

| Skill | Description | Parameters | Install |
|-------|-------------|------------|---------|
| **travel-itinerary-planner** | Generate a day-by-day travel itinerary for any destination. Researches attractions, restaurants, transportation, and practical tips. Covers budget breakdown, packing checklist, and alternative plans. | `destination` (req), `days` (req), `travel_style` (opt), `interests` (opt) | [install link](https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/lifestyle/travel-itinerary-planner/SKILL.md) |

---

## 🚀 Usage

### Install a skill

```bash
hermes skills install <raw-url-to-SKILL.md>
```

Example:

```bash
hermes skills install https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/research/local-competitive-analysis/SKILL.md
```

### Use a skill

Once installed, load the skill and ask:

```bash
hermes -s local-competitive-analysis
# or
hermes -s tech-stack-detector
# or
hermes -s product-pricing-tracker
```

Then prompt:

> *"Analyze the ramen market in Shibuya, Tokyo"*
> *"I want to open a coffee shop. What's the local competition like?"*
> *"What tech stack does stripe.com use?"*
> *"Analyze https://vercel.com — what are they built with?"*
> *"Track Notion's pricing for me"*
> *"Has Vercel changed their pricing since last month?"*
> *"Generate a weekly AI newsletter about LLMs"*
> *"Turn this blog post into a Twitter thread and LinkedIn post"*
> *"帮我把我这篇英文文章改成小红书文案"*
> *"Plan a 4-day trip to Kyoto"*
> *"I have one day in Shanghai. What should I do?"*

---

## ➕ Adding a New Skill

1. Pick a category (or create a new one)
2. Create `SKILL.md` with proper frontmatter (name, description, version, author, license, tags, related_skills)
3. Add your skill to the table in this README
4. Commit and push

---

## 📝 License

MIT — feel free to use, share, and contribute.
