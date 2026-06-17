---
name: code-review-helper
description: "Use when reviewing code changes — analyzes diffs or PRs for logic issues, security risks, style problems, and improvement suggestions."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [code-review, pr-review, quality, security, static-analysis]
    related_skills: [project-scaffolder, api-doc-generator]
---

# Code Review Helper

> Structured code review from git diffs or PRs. Analyzes changes for logic bugs, security risks, code style, and performance issues.

---

## When to Use

- *"Review this PR for me: https://github.com/.../pull/123"*
- *"Review the uncommitted changes in this repo"*
- *"Look at this diff and tell me what's wrong"*
- *"Check this code for security issues"*

---

## Core Workflow

### Step 1: Get the Diff

```bash
# Uncommitted changes
git diff

# Specific files
git diff -- main.py src/

# Between branches
git diff main...feature-branch

# From PR URL (if gh CLI available)
gh pr view 123 --json body,additions,deletions,files
```

### Step 2: Analyze

For each file changed, check:

**🔴 Critical:**
- Logic errors (off-by-one, wrong comparison, missing edge cases)
- Security vulnerabilities (SQL injection, XSS, hardcoded secrets, unsafe eval)
- Data loss risks (destructive migrations, missing validations)
- Authentication/authorization gaps

**🟡 Warning:**
- Code smells (duplicated code, overly complex functions, magic numbers)
- Performance issues (N+1 queries, missing indexes, unnecessary loops)
- Error handling gaps (bare excepts, swallowed exceptions)
- Type safety issues (missing type hints, any usage)

**🔵 Suggestion:**
- Style inconsistencies (naming conventions, formatting)
- Documentation gaps (missing docstrings/comments)
- Test coverage (untested paths)
- Refactoring opportunities

### Step 3: Generate Review

```markdown
# Code Review: {PR title / scope}

**Files:** {N}
**Lines:** +{N}/-{N}

---

## 🔴 Critical Issues ({N})

### {file}:{line} — {issue title}
**Problem:** {description}
**Risk:** {security/crash/data-loss}
**Fix:** {suggested code}

---

## 🟡 Warnings ({N})

| File | Line | Issue | Severity |
|------|------|-------|----------|
| {path} | {L} | {description} | perf/safety/style |

---

## 🔵 Suggestions ({N})

| File | Suggestion |
|------|-----------|
| {path} | {description} |

---

## 📊 Summary

| Metric | Value |
|--------|-------|
| 🔴 Critical | {N} |
| 🟡 Warning | {N} |
| 🔵 Suggestion | {N} |
| ✅ Looks good | {N} files |
| **Overall** | ✅/⚠️/🚨 |
```

---

## Example

```
User: Review my uncommitted changes
Hermes should:
  1. Run git diff
  2. Parse each changed hunk
  3. Check for common issues per language
  4. Generate review report
  5. Present with priority levels
```
