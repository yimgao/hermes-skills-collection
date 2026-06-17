# 🧩 Hermes Skills Collection

A curated collection of reusable [Hermes Agent](https://hermes-agent.nousresearch.com) skills, organized by category. Each skill provides a structured workflow that Hermes can follow to complete complex tasks — from market research to creative work.

---

## 📁 Structure

```
hermes-skills-collection/
├── README.md
├── research/
│   └── local-competitive-analysis/
│       ├── SKILL.md        # Local market competitive analysis skill
│       └── (future skills)
└── (more categories coming)
```

---

## 📦 Skills

### 🔬 Research

| Skill | Description | Industry | Location | Install |
|-------|-------------|----------|----------|---------|
| **local-competitive-analysis** | Analyze local competitors for a specific business type in a given city. Auto-detects location via IP. Produces structured market reports with SWOT, market gap analysis, and strategic recommendations. | Required | Optional (auto-detect) | `hermes skills install https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/research/local-competitive-analysis/SKILL.md` |

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
```

Then prompt:

> *"Analyze the ramen market in Shibuya, Tokyo"*
> *"I want to open a coffee shop. What's the local competition like?"*
> *"Research bakeries near me"*

---

## ➕ Adding a New Skill

1. Pick a category (or create a new one)
2. Create `SKILL.md` with proper frontmatter (name, description, version, author, license, tags)
3. Add your skill to the table in this README
4. Commit and push

---

## 📝 License

MIT — feel free to use, share, and contribute.
