---
name: project-scaffolder
description: "Use when starting a new project — generates a complete project skeleton with directory structure, config files, .gitignore, README template, and optional git init from a natural language description."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [scaffolding, project-setup, boilerplate, dev-tools, template]
    related_skills: [writing-plans, spike]
---

# Project Scaffolder

> Generate a complete project skeleton from a natural language description. Creates directory structure, configuration files, .gitignore, README, and optionally initializes git.

---

## Overview

This skill generates a ready-to-use project scaffold from a plain English description. Instead of manually creating folders and config files every time you start a new project, just describe what you want — the skill handles the rest.

**What it generates:**
| Item | Details |
|------|---------|
| **Directory structure** | src/, tests/, docs/, scripts/, etc. |
| **Config files** | pyproject.toml, package.json, tsconfig, Dockerfile, etc. |
| **.gitignore** | Language/framework-appropriate patterns |
| **README.md** | Project name, description, setup instructions |
| **Optional extras** | CI config, pre-commit hooks, Makefile, env example |

---

## When to Use

- User asks: *"Scaffold a FastAPI project with SQLAlchemy and pytest"*
- User asks: *"Create a Next.js app with Tailwind and TypeScript"*
- User asks: *"Set up a Python CLI project with click and poetry"*
- User asks: *"Initialize a Go microservice project structure"*
- User asks: *"Give me a Rust CLI project skeleton"*

---

## Core Workflow

### Step 1: Parse the Request

Extract from the user's description:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `language` | Primary programming language | Python, TypeScript, Go, Rust, Elixir |
| `framework` | Web framework / library | FastAPI, Next.js, Express, Gin, Actix |
| `features` | Additional libs / tools | SQLAlchemy, Prisma, pytest, Tailwind |
| `project_type` | Kind of project | API, CLI, Library, Microservice, Full-stack |
| `package_manager` | npm, pip, poetry, cargo, go mod | Auto-detect from language |

### Step 2: Generate Project Structure

Create the scaffold under the user's specified directory (or suggest a name).

**Common project archetypes:**

#### Python API (FastAPI)
```
{project-name}/
├── .gitignore
├── README.md
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── health.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py
│   └── schemas/
│       ├── __init__.py
│       └── common.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_health.py
├── alembic/
│   └── versions/
└── scripts/
    ├── setup.sh
    └── run.sh
```

**Python CLI (click + poetry)**
```
{project-name}/
├── .gitignore
├── README.md
├── pyproject.toml
├── Makefile
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py
│   ├── commands/
│   │   ├── __init__.py
│   │   └── hello.py
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_cli.py
└── scripts/
    └── lint.sh
```

#### TypeScript / Next.js
```
{project-name}/
├── .gitignore
├── README.md
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.js
├── postcss.config.js
├── .env.local.example
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   └── ui/
│   ├── lib/
│   │   └── utils.ts
│   └── types/
│       └── index.ts
├── public/
└── __tests__/
    └── page.test.tsx
```

#### Go Microservice
```
{project-name}/
├── .gitignore
├── README.md
├── go.mod
├── Makefile
├── Dockerfile
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handler/
│   │   └── health.go
│   ├── service/
│   │   └── service.go
│   ├── repository/
│   │   └── repository.go
│   └── config/
│       └── config.go
├── pkg/
│   └── middleware/
│       └── logging.go
└── scripts/
    └── migrate.sh
```

### Step 3: Generate Config Files

Generate proper config files with sensible defaults:

#### pyproject.toml (Python)
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{project-name}"
version = "0.1.0"
description = "{description}"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.3.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"
```

#### .gitignore (multi-language)
```
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.venv/
.env

# Node
node_modules/
.next/
dist/
.env.local
*.tsbuildinfo

# Go
*.exe
*.exe~
*.dll
*.so
*.dylib

# Rust
/target/
**/*.rs.bk

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

### Step 4: Generate README

Use a standard README template:

```markdown
# {Project Name}

> {One-line description}

## 🚀 Quick Start

```bash
# Clone and enter
git clone https://github.com/{user}/{project}
cd {project}

# Install dependencies
{install_command}

# Run
{run_command}
```

## 📁 Project Structure

```
{TODO: add tree output}
```

## 🧪 Testing

```bash
{test_command}
```

## 📝 License

MIT
```

### Step 5: Optional Git Init

If the user requests it (or if they don't say otherwise):

```bash
cd {project-name}
git init
git add -A
git commit -m "chore: initial scaffold — {description}"
```

---

## Template Reference

| Language | pyproject.toml | package.json | go.mod | Cargo.toml |
|----------|---------------|--------------|--------|-----------|
| **Python (API)** | ✅ FastAPI + SQLAlchemy | — | — | — |
| **Python (CLI)** | ✅ click + pytest | — | — | — |
| **TypeScript** | — | ✅ Next.js + Tailwind | — | — |
| **Go** | — | — | ✅ Gin + air | — |
| **Rust** | — | — | — | ✅ clap + reqwest |
| **Elixir** | — | — | — | — (mix new) |

| File | Content |
|------|---------|
| **Dockerfile** | Multi-stage build, language-optimized |
| **docker-compose.yml** | App + DB (Postgres/Redis) |
| **Makefile** | Common commands: run, test, lint, clean |
| **.env.example** | All required env vars with dummy values |
| **.github/workflows/ci.yml** | Run tests on push/PR |

---

## Example Invocations

### Example 1: Python API
```
User: Scaffold a FastAPI project with SQLAlchemy, pytest, and Docker
Hermes should:
  1. Create directory structure (src/api/, src/core/, tests/, etc.)
  2. Generate pyproject.toml with fastapi, sqlalchemy, uvicorn, pytest
  3. Generate main.py with health endpoint
  4. Generate .gitignore
  5. Generate README.md
  6. Generate Dockerfile + docker-compose.yml
  7. Generate .env.example
  8. Run git init + first commit
  9. Present the created structure
```

### Example 2: TypeScript
```
User: Create a Next.js project with TypeScript and Tailwind
Hermes should:
  1. Create src/app/, src/components/, src/lib/
  2. Generate package.json, tsconfig.json, next.config.js, tailwind.config.js
  3. Generate layout.tsx, page.tsx, globals.css
  4. Generate .gitignore, README.md, .env.local.example
  5. Present the structure
```

### Example 3: Go
```
User: Give me a Go microservice with Gin and a health check
Hermes should:
  1. Create cmd/server/, internal/handler/, internal/config/
  2. Generate go.mod, main.go, health handler
  3. Generate Makefile, Dockerfile
  4. Generate .gitignore, README.md
  5. Present the structure
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Too many files for a simple project.** | Adjust scope to the project's size. A CLI tool doesn't need Docker. |
| 2 | **Wrong config syntax.** | Use standard templates. For pyproject.toml, use `hatchling` (not `setuptools` for modern Python). |
| 3 | **Git init when user didn't ask.** | Ask first, or default to no git init. Let user opt in. |
| 4 | **Overwriting existing files.** | If target directory exists and is non-empty, warn the user. |
| 5 | **Outdated dependency versions.** | Use recent stable versions. Note that versions should be verified at time of use. |
| 6 | **Missing essential files.** | Every project needs at minimum: .gitignore, README.md, and the main entry point. |

---

## Verification Checklist

- [ ] Language and framework correctly identified from description
- [ ] Directory structure created under the specified path
- [ ] Config files generated with correct syntax
- [ ] .gitignore covers language + OS + IDE patterns
- [ ] README.md has project name, description, quick start
- [ ] Entry point file created and functional
- [ ] Dockerfile present (if API / microservice type)
- [ ] .env.example present (if config uses env vars)
- [ ] Git init + first commit done (if requested)
- [ ] Present the created tree structure to user
