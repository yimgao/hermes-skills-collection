---
name: env-setup-debugger
description: "Use when diagnosing project environment issues — checks language versions, dependency installation, PATH config, env vars, and provides fix suggestions."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [debugging, environment, setup, dev-tools, troubleshooting]
    related_skills: [code-review-helper, project-scaffolder]
---

# Environment Setup Debugger

> Diagnose "my project won't run" issues. Checks language versions, dependency installation, PATH, env vars, and common configuration problems.

---

## When to Use

- *"My Python project won't start — help!"*
- *"Node modules aren't installing correctly"*
- *"I get 'command not found' after installing"*
- *"The Docker container fails to build"*
- *"帮我看看为什么我的项目跑不起来"*

---

## Core Workflow

### Step 1: Collect Environment Info

```bash
# OS
uname -a

# Language runtimes
python3 --version 2>&1 || node --version 2>&1 || go version 2>&1 || rustc --version 2>&1
pip --version 2>&1 || npm --version 2>&1

# Project config
cat pyproject.toml 2>/dev/null || cat package.json 2>/dev/null || cat Cargo.toml 2>/dev/null

# Env check
python3 -c "import sys; print(sys.path)" 2>&1
echo $PATH | tr ':' '\n'
```

### Step 2: Run Diagnostics

**Python checks:**
| Issue | Check | Fix |
|-------|-------|-----|
| Wrong Python version | `python3 --version` vs pyproject.toml `requires-python` | Install correct version |
| Missing venv | No `.venv/` or `venv/` directory | `python3 -m venv .venv` |
| Dependencies not installed | ModuleNotFoundError on run | `pip install -e ".[dev]"` |
| Conflicting packages | `pip check` | Reinstall with fresh venv |

**Node checks:**
| Issue | Check | Fix |
|-------|-------|-----|
| Node version mismatch | `node --version` vs engines in package.json | Use nvm |
| Missing node_modules | No `node_modules/` | `npm install` |
| Package lock drift | package-lock.json vs package.json | `npm ci` |

**Docker checks:**
| Issue | Check | Fix |
|-------|-------|-----|
| Build failure | `docker build .` logs | Check Dockerfile syntax |
| Port conflict | `lsof -i :{port}` | Change port or kill process |

### Step 3: Generate Diagnosis Report

```markdown
# Environment Diagnosis

**Project:** {name}
**OS:** {OS version}
**Date:** {YYYY-MM-DD}

---

## ✅ Passed Checks

- [x] Python 3.11 installed (required: >=3.11)
- [x] Virtual environment active
- [x] All deps installed

## ❌ Failed Checks

### {Issue title}
- **Diagnosis:** {what's wrong}
- **Cause:** {root cause}
- **Fix:** {step-by-step fix}
- **Command:** `{fix command}`

## 📋 Recommended Fix Order

1. {Fix 1}
2. {Fix 2}
3. {Fix 3}

---

## Quick Fix Script

```bash
# Run these in order:
{fix commands}
```
```

---

## Example

```
User: I can't run my FastAPI project, it says "module not found: sqlalchemy"
Hermes should:
  1. Check Python version
  2. Check if venv is activated
  3. Check if sqlalchemy is in pyproject.toml
  4. Run pip list | grep sqlalchemy
  5. Suggest: pip install -e ".[dev]" or activate venv
  6. Generate diagnosis report
```
