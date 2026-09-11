---
name: pr-description-writer
description: "Turn a raw diff (or branch / commit list) into a complete, paste-ready pull-request description — Conventional-Commits title, 'Why' rationale, 'What changed' breakdown, test plan, breaking-change callout, migration notes, screenshot placeholders, reviewer checklist, and a 1-line slack/teams teaser. Adapts to GitHub, GitLab, Bitbucket, and Azure DevOps PR templates. Pairs with changelog-generator (release-level) and code-review-helper (review-side)."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [dev-tools, pr, pull-request, code-review, conventional-commits, documentation, developer-experience, git, github, gitlab, bitbucket, azure-devops, changelog, release-notes]
    related_skills: [changelog-generator, code-review-helper, codebase-tour-guide, dependency-auditor, api-contract-tester, git-history-analyst, project-scaffolder, api-doc-generator, secret-scanner]
---

# 📝 PR Description Writer — Pull Request 描述生成器

> You just finished 4 hours of work, `git diff` shows 1,200 lines across 17 files, and your team requires a structured PR description before review. Don't write it from scratch at 6pm. Tell Hermes what you changed, paste the diff (or branch name), and get a **complete, template-aware PR body** in 30 seconds — title, rationale, file-grouped changeset, test plan, breaking-change banner, migration notes, reviewer checklist, and a one-line announcement for Slack/Teams.

## Overview / 概述

PR Description Writer takes the *unstructured* work that lives in a branch (commits, diff, ticket text) and turns it into the *structured artifact* your team actually needs: a PR description that survives first-pass review, satisfies lint/CI templates, gives reviewers the right context, and gets the right people pinged. It's the **author side** of `code-review-helper` and the **PR-level cousin** of `changelog-generator` (which is release-level, multi-commit).

The skill answers the 7 questions every reviewer actually has:

1. **What is this PR trying to do?** — 1-line summary, tied to a ticket
2. **Why this approach?** — rationale + alternatives considered
3. **What changed?** — file-grouped changeset with line counts
4. **How do I verify it?** — test plan, manual steps, screenshots
5. **Will it break anything?** — breaking-change callout, migration steps
6. **What's left?** — TODOs, follow-ups, out-of-scope notes
7. **Who needs to review?** — CODEOWNERS-driven reviewer suggestions

It is **branch-aware** (reads commits + diff + linked issue), **template-aware** (detects `.github/pull_request_template.md` / `.gitlab/merge_request_templates/` / Atlassian template), **scope-aware** (groups by directory/feature, not file list), and **platform-aware** (emits the right markdown dialect for GitHub vs GitLab vs Bitbucket vs Azure DevOps). Output is local Markdown; nothing is pushed or opened.

| 能力 | 说明 | 实现方式 |
|------|------|---------|
| 🎯 Conventional-Commits 标题 | `type(scope): subject` from changed paths + diff content | Heuristic on diff keywords + path |
| 📋 "Why" + 备选方案 | Rationale + alternatives-considered, derived from commit messages + branch name + linked ticket | Commit parser + NL prompt |
| 📂 文件分组 changeset | Group by directory / feature module, not flat list | Path clustering + scope detection |
| 📏 规模评分 XS/S/M/L/XL | files / +lines / -lines → reviewer-time hint | git diff --stat |
| 🧪 测试计划 | Infer test plan from diff (new test files → "added X tests"; refactor → "rerun Y") | File globs + commit keywords |
| 💥 Breaking-change 横幅 | Detect API/schema/CLI/env changes, emit `⚠️ BREAKING` block | Path + diff heuristics |
| 🔁 Migration notes | Auto-suggest migration steps when breaking (env var rename, schema migration, deprecation) | Pattern templates |
| 📸 Screenshot 占位 | `[Screenshot: <description>]` blocks for UI diffs | Detect `.css`/`.tsx`/`.vue`/`.html` |
| ✅ Reviewer checklist | 8-pt self-check (tests, docs, types, secrets, migrations, perf, accessibility, roll-back) | Static checklist |
| 👥 Reviewer 建议 | From `.github/CODEOWNERS` or `CODEOWNERS` file | Glob match |
| 📢 1-行 Slack/Teams 预告 | "🚀 [BE] Stripe webhook retries — 14 files, +412/-98, breaking, needs review from @payments" | Derived |
| 🏷️ Label 建议 | `feature`/`bug`/`refactor`/`breaking`/`docs`/`chore`/`perf` | Branch + diff keywords |
| 🔧 平台适配 | GitHub / GitLab / Bitbucket / Azure DevOps markdown dialect | Template detection |
| 🪞 模板感知 | If repo has a PR template, slot content into its sections | Read template file |
| 🔒 零推送 | Generates file only; user copies/pastes or uses `gh pr create --body-file` | Local-only |

## When to Use / 适用场景

- *"Write the PR description for this branch — base is `main`, head is `feat/stripe-retries`"*
- *"Here's my diff (paste 1,200 lines) — turn it into a PR body for GitHub"*
- *"I just rebased 6 commits into 1 — generate the PR description from the squashed diff"*
- *"We have a `.github/pull_request_template.md` — fill it out from my branch"*
- *"Detect if this PR is breaking and draft the migration section"*
- *"I need a Slack one-liner to ping the payments team about this PR"*
- *"Show me the CODEOWNERS-based reviewer list for the files I changed"*
- *"Generate the PR title using Conventional Commits — `feat(api):` style"*
- *"This is for GitLab, not GitHub — use their MR template"*
- *"生成 PR 描述 — 分支是 feat/login-v2，改了 12 个文件"*
- *"刚 push 了分支，PR description 还是空的，帮我写一版"*
- *"我团队要求 PR 必须包含：Why / What / Test Plan / Breaking — 给我按这个结构填"*
- *"本地 review 完，准备发团队评审——给我一个完整的 PR body"*

**不适用于**：跨多个独立功能的 mega-PR (先拆 PR)、需要业务背景的"why"（skill 只能从 commit/branch/ticket 推断；缺信息时会显式 ask）、纯文档 typo 修复（用 `changelog-generator` 即可）、release notes（用 `changelog-generator`）。

## Core Workflow / 核心工作流

### Step 1：抓取改动（git stat + commit list）

> **目标**：在 10 秒内拿到 diff 元数据，不读真实代码内容（除非用户明确粘贴）。

```bash
# 1.1 当前分支 vs base
git rev-parse --abbrev-ref HEAD
git log --oneline main..HEAD           # 提交列表
git diff main...HEAD --stat            # 文件级 stat
git diff main...HEAD --shortstat       # 总计
git diff main...HEAD --name-only       # 文件名（用于 CODEOWNERS）

# 1.2 范围 + 数量
git diff main...HEAD --stat | tail -1  # "N files changed, +X, -Y"

# 1.3 ticket / branch 命名提示
git rev-parse --abbrev-ref HEAD | grep -Eo '(PROJ-[0-9]+|#[0-9]+|[A-Z]+-[0-9]+)'

# 1.4 已有 PR 模板？
ls .github/pull_request_template.md 2>/dev/null \
  || ls .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null \
  || ls .gitlab/merge_request_templates/ 2>/dev/null \
  || ls .bitbucket/ 2>/dev/null
```

**输出字段**：`branch`、`base`、`commits[]`、`files_changed`、`insertions`、`deletions`、`ticket_hint`、`has_template`、`template_path`、`codeowners_path`。

如果分支不存在或 base 拼错 → 立即提示用户，不要猜。

```bash
# 1.5 复杂度评分
python3 - <<'PY'
import subprocess, re
stat = subprocess.check_output(["git", "diff", "main...HEAD", "--shortstat"], text=True).strip()
m = re.search(r"(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?", stat)
files = int(m.group(1)) if m else 0
ins   = int(m.group(2)) if m and m.group(2) else 0
dels  = int(m.group(3)) if m and m.group(3) else 0
score = "XL" if files>40 or ins+dels>1500 else \
        "L"  if files>15 or ins+dels>500  else \
        "M"  if files>5  or ins+dels>150  else \
        "S"  if files>0  else "XS"
print(f"{files} files, +{ins}/-{dels}, size={score}")
PY
```

### Step 2：分类改动（按 feature 目录分组 + 类型推断）

> **目标**：把扁平的文件列表变成有意义的 changeset 分组。

```python
import subprocess, re
from collections import defaultdict
from pathlib import Path

paths = subprocess.check_output(
    ["git", "diff", "main...HEAD", "--name-only"], text=True
).splitlines()

# 1. 目录聚类（用第 1-2 层目录当 "feature"）
buckets = defaultdict(list)
for p in paths:
    parts = Path(p).parts
    if len(parts) >= 2 and parts[0] in ("src", "app", "lib", "pkg", "internal", "packages", "apps"):
        key = "/".join(parts[:2])        # src/api, src/auth ...
    elif len(parts) >= 1:
        key = parts[0]                   # docs/, infra/, tests/
    else:
        key = "root"
    buckets[key].append(p)

# 2. 每文件打 type 标签
def file_type(p: str) -> str:
    name = Path(p).name
    if name.startswith("test_") or "/tests/" in p or "/__tests__/" in p or "/spec/" in p:
        return "test"
    if name.endswith((".md", ".rst", ".txt", "README")) or "/docs/" in p:
        return "docs"
    if name in (".env.example", "docker-compose.yml", "Dockerfile", "package.json",
                "pyproject.toml", "go.mod", "Cargo.toml", "requirements.txt",
                "package-lock.json", "yarn.lock", "pnpm-lock.yaml"):
        return "config"
    if "/migrations/" in p or name.endswith((".sql",)):
        return "migration"
    if re.search(r"\.test\.|\.spec\.|_test\.|Test\.php$", name):
        return "test"
    return "feat"

# 3. 检测 breaking 信号
BREAKING_PATTERNS = [
    r"^--[a-z-]+",                         # CLI flag 改名/删除
    r"\bBREAKING[ -]CHANGE",
    r"\bdeprecat", r"\bremov", r"\bdelete", r"\bdrop\b",
    r"\benv.*(?:rename|remove|change)",
    r"\bapi.*v\d", r"/v\d+/",              # 路径版本号
    r"^!?\s*\*?(?:feat|fix|refactor).*!:",  # Conventional Commits `!`
]
def is_breaking(p: str, commit_msgs: list[str]) -> bool:
    if any(re.search(pat, p, re.I) for pat in BREAKING_PATTERNS[:2]):
        return True
    if any(re.search(pat, m, re.I) for pat in BREAKING_PATTERNS):
        return True
    # Conventional Commits `!` 在 type 后
    if any(re.match(r"^[a-z]+(\([^)]+\))?!:", m) for m in commit_msgs):
        return True
    return False
```

**输出**：`changeset = [{"group": "src/api", "files": [...], "types": {"feat": 3, "test": 1}}, ...]` + `breaking: bool` + `breaking_files: list[str]`。

### Step 3：填模板 / 生成结构

> **目标**：要么套用仓库的 PR 模板，要么用默认 7 段式结构。

#### 3a. 如果仓库有模板（最优先）

读取模板的占位符（H2 标题 + 复选框 + "..." 行），逐段映射：

```text
模板占位符              → skill 产出
## Summary             → Step 2 的 1-行总结 + ticket
## Why / Context       → Step 2 的 rationale（来自 commit + branch name）
## What changed        → Step 2 的 changeset 分组
## How to test         → Step 4 的 test plan
## Breaking changes    → Step 2 的 breaking 检测 + migration
## Screenshots         → 占位块（如有 UI 文件）
## Checklist           → Step 5 的 reviewer checklist
```

#### 3b. 默认 7 段式（无模板时）

```text
## Summary
## Why
## What changed
## How to test
## Breaking changes
## Out of scope / Follow-ups
## Reviewer checklist
```

**每个 section 的产出规则**：

| Section | 长度 | 来源 |
|---------|------|------|
| Summary | 1 行，< 100 字符 | Conventional-Commits subject + ticket |
| Why | 2-4 句 | commit message body × branch name + 必要时显式 ask 用户 |
| What changed | 1 个文件分组表 | Step 2 buckets |
| How to test | 3-7 个 bullet | new test files → 列出；refactor → "rerun X"；UI → "manual: ..." |
| Breaking changes | 0 / 横幅块 | Step 2 breaking detection |
| Out of scope | 1-3 行 | 推测（"未涉及 X；Y 留作 follow-up #ISSUE"） |
| Reviewer checklist | 8 个 `[ ]` 项 | 静态清单 + 上下文相关补充 |

**生成 Conventional-Commits 标题**：

```python
import re
from collections import Counter

def infer_type(changeset: dict, msgs: list[str]) -> str:
    text = " ".join(msgs).lower() + " " + " ".join(changeset.keys()).lower()
    if re.search(r"\bfix\b|bug|broken|regression", text):  return "fix"
    if re.search(r"\brefactor\b|cleanup|rename", text):    return "refactor"
    if re.search(r"\bperf\b|slow|latency|optimi", text):   return "perf"
    if re.search(r"\bdoc\b|readme|comment", text):         return "docs"
    if re.search(r"\btest\b|spec", text) and len(changeset) <= 2:
                                                           return "test"
    if re.search(r"\bchore\b|bump|upgrade|ci", text):      return "chore"
    if re.search(r"\bstyle\b|format|lint", text):         return "style"
    return "feat"

# scope = 最高频的 top-level feature 目录
def infer_scope(buckets_keys: list[str]) -> str | None:
    counts = Counter()
    for k in buckets_keys:
        parts = k.split("/")
        if len(parts) >= 2 and parts[0] in ("src","app","lib","pkg","internal","packages","apps"):
            counts[parts[1]] += 1
    return counts.most_common(1)[0][0] if counts else None

def make_title(changeset, msgs, ticket=None):
    t = infer_type(changeset, msgs)
    s = infer_scope(list(changeset.keys()))
    subject = re.sub(r"^(fix|feat|refactor|perf|docs|test|chore|style)(\([^)]+\))?!?:\s*",
                     "", msgs[0], flags=re.I).strip().rstrip(".")
    if len(subject) > 60:
        subject = subject[:57] + "..."
    prefix = f"{t}({s})" if s else t
    bang = "!" if any(re.match(r"^[a-z]+(\([^)]+\))?!:", m) for m in msgs) else ""
    title = f"{prefix}{bang}: {subject}"
    if ticket:
        title = f"{title} ({ticket})"
    return title
```

### Step 4：测试计划 + 截图占位

```text
Test plan:

- [ ] Unit: `pytest tests/<new_test_path> -v`  (or repo's test runner)
- [ ] Integration: ...
- [ ] Manual smoke: <具体步骤> (auto-filled when UI files in diff)
- [ ] Regression: re-run <受影响区域的旧测试>

Screenshots / Recordings:
- [Screenshot: <feature> — before/after]
- [Screenshot: <edge case> — error state]
```

**自动触发条件**：

| 触发 | 输出 |
|------|------|
| 文件含 `.css`/`.scss`/`.tsx`/`.vue`/`.svelte`/`.html` | "📸 UI 改动 — 请附 before/after 截图" |
| 文件含 `migrations/` 或 `*.sql` | "⚠️ DB migration — 在 staging 跑一次 `migrate up/down/up`" |
| 文件含 `Dockerfile` / `docker-compose.yml` | "🐳 容器改动 — `docker build` 验证 + 清理旧镜像" |
| 文件含 `.github/workflows/` | "⚙️ CI 改动 — 触发一次 dry-run 确认 secrets 可用" |
| 文件含 `package.json` / `requirements.txt` | "📦 依赖变化 — 跑一次 `npm ci` / `pip install -r` 在干净环境" |
| breaking 标志 = True | "🔁 Migration 步骤详见下节" |

### Step 5：Reviewer 建议 + 清单 + 1-行预告

```bash
# 5.1 CODEOWNERS 匹配
codeowners_file=".github/CODEOWNERS"
if [ -f "$codeowners_file" ] || [ -f "CODEOWNERS" ]; then
    co="${codeowners_file:-CODEOWNERS}"
    changed_files=$(git diff main...HEAD --name-only)
    owners=$(echo "$changed_files" | while read f; do
        awk -v file="$f" '
            /^[^#]/ { pattern=$1; sub(/^[^ ]+ +/, ""); owners=$0;
                      if (match_file(pattern, file)) print owners }
            function match_file(p, f,    i, parts, pats) {
                gsub(/\*/,"[^/]*", p); gsub(/\?/,".", p);
                return (f ~ "^" p)
            }' "$co"
    done | sort -u)
    echo "$owners"
fi
```

**Reviewer checklist (8 项)**：

```text
- [ ] Tests cover new behavior
- [ ] Docs / CHANGELOG updated (or explicitly N/A)
- [ ] No secrets / .env values committed
- [ ] DB / API migrations are reversible
- [ ] No new lint / type / build warnings
- [ ] Performance impact considered (N+1, large payloads, cold-start)
- [ ] Accessibility / i18n considered (UI changes)
- [ ] Roll-back plan is "revert this PR" (no data backfill required)
```

**1-行 Slack 预告**：

```text
🚀 [{SCOPE}] {TITLE} — {N} files, +{INS}/-{DEL}, {SIZE}{BREAKING_TAG}, needs review from {OWNERS}
```

### Step 6：写到本地文件 + 给出推送建议

```bash
# 6.1 输出位置
output="pr-description-$(git rev-parse --abbrev-ref HEAD | tr '/' '-').md"
# 或: .hermes/pr/<branch>.md

# 6.2 不自动推送，只给可选命令
echo "生成完成 → $output"
echo ""
echo "可选的下一步："
echo "  gh pr create --title \"$TITLE\" --body-file $output        # GitHub"
echo "  glab mr create --title \"$TITLE\" --description $output   # GitLab"
echo "  bb pr create --title \"$TITLE\" --body \"\$(cat $output)\" # Bitbucket"
echo "  az repos pr create --title \"$TITLE\" --description \"\$(cat $output)\" # Azure DevOps"
```

## Example Invocations / 对话示例

### 示例 1：标准 GitHub PR 描述

> **User**: 我刚 push 了 `feat/stripe-retries` 分支，base 是 `main`。帮我写个 PR description。
>
> **Agent**:
> 1. 跑 Step 1：6 commits, 14 files, +412/-98, size=L, no template found, no CODEOWNERS
> 2. 跑 Step 2：changeset = `src/api/webhooks` (5), `src/services/payments` (3), `tests/...` (4), `docs/runbooks/stripe.md` (1), `requirements.txt` (1)
> 3. breaking 检测：True（`src/api/webhooks/stripe.py` 含 BREAKING 注释 + commit `feat!: ...`）
> 4. infer type=`feat`, scope=`api`
> 5. 产出：
>
> ```markdown
> ## Summary
> feat(api)!: add Stripe webhook retry policy with exponential backoff (#PAY-1247)
>
> ## Why
> Current webhook handler fails open on transient Stripe errors, causing
> downstream subscription state drift. We need bounded retries with a clear
> dead-letter queue so a Stripe outage doesn't silently drop events.
>
> Alternatives considered:
> - Celery + Redis (rejected: adds infra surface for one job)
> - Stripe's built-in retry config alone (insufficient: 3-day window too short for our 7-day refund flow)
>
> ## What changed
>
> | Area | Type | Files |
> |------|------|-------|
> | `src/api/webhooks/` | feat + breaking | 5 (+210/-72) |
> | `src/services/payments/` | feat | 3 (+120/-15) |
> | `tests/` | test | 4 (+75/-3) |
> | `docs/runbooks/stripe.md` | docs | 1 (+7/-2) |
> | `requirements.txt` | config | 1 (+1/-0) |
>
> ## How to test
> - [ ] `pytest tests/api/test_webhook_retries.py -v` — 12 new test cases
> - [ ] Manual: `stripe trigger payment_intent.succeeded` in test mode, watch DLQ
> - [ ] Regression: `pytest tests/services/test_payments.py -v`
>
> ## ⚠️ Breaking changes
>
> - `POST /api/webhooks/stripe` now requires `STRIPE_RETRY_POLICY` env var
>   (default: `exp:6,cap:300`). Old payloads without `idempotency_key` will
>   be rejected with `400`.
> - `webhook_dead_letter` table is added via migration `0042_*.sql`
>   (reversible).
>
> ### Migration
> 1. `python manage.py migrate` (adds DLQ table)
> 2. Set `STRIPE_RETRY_POLICY=exp:6,cap:300` in staging + prod env
> 3. Verify `/health/webhooks` returns 200
> 4. Rollback: `python manage.py migrate 0041_*.sql` (drops DLQ table)
>
> ## Out of scope
> - Slack alerts on DLQ → follow-up #PAY-1251
> - Replay endpoint for DLQ messages → follow-up #PAY-1252
>
> ## Reviewer checklist
> - [ ] Tests cover new behavior
> - [ ] Docs / CHANGELOG updated
> - [ ] No secrets / .env values committed
> - [ ] DB / API migrations are reversible ✅
> - [ ] No new lint / type / build warnings
> - [ ] Performance impact considered
> - [ ] N/A (no UI changes)
> - [ ] Roll-back plan is "revert this PR"
>
> ---
> 🚀 [api] feat(api)!: Stripe webhook retry policy — 14 files, +412/-98, size=L ⚠️ BREAKING, needs review from @payments-team
> ```

### 示例 2：套用仓库现有 PR 模板

> **User**: 我们有 `.github/pull_request_template.md`，里面分 `## What & Why` / `## How to test` / `## Risk & Rollback` / `## Reviewer notes`。帮我按这个填，从分支 `fix/login-redirect-loop`。
>
> **Agent**:
> 1. 读到模板，4 个 section
> 2. 跑 Step 1：3 commits, 5 files, +38/-22, size=S, ticket=`#AUTH-882`
> 3. 跑 Step 2：changeset = `src/auth/` (3), `tests/auth/` (2)
> 4. breaking=False
> 5. 填进模板：
>
> ```markdown
> ## What & Why
> <!-- What does this PR do? Why is this change needed? -->
> fix(auth): resolve login redirect loop when session cookie has trailing slash (#AUTH-882)
>
> Users on `/login/` (with trailing slash) were redirected to `/login` (no slash),
> which then redirected back to `/login/`, creating an infinite loop. Session
> middleware now canonicalizes the path before redirect.
>
> ## How to test
> <!-- Steps to verify the change works as expected -->
> - [ ] Manual: log in via `/login/` (trailing slash) — should land on `/dashboard` in 1 redirect
> - [ ] `pytest tests/auth/test_session_middleware.py -v` — 4 new test cases
> - [ ] Regression: `pytest tests/auth/ -v`
>
> ## Risk & Rollback
> <!-- What could go wrong? How do we roll back? -->
> - **Risk**: low — single middleware change, covered by tests
> - **Affected paths**: `/login/*` only
> - **Rollback**: `git revert <sha>` is safe (no schema/data change)
> - **Monitoring**: watch `auth_redirect_count_total` in Grafana for 1h
>
> ## Reviewer notes
> <!-- Anything else reviewers should know? -->
> - This is a partial fix; full canonical-path enforcement is tracked in #AUTH-901
> - No breaking change
> - Deploy during business hours, low traffic preferred
> ```

### 示例 3：中文分支 + GitLab MR

> **User**: 分支 `fix/订单导出超时` 推到了 GitLab，base 是 `develop`。帮我写 MR 描述，中英混合。
>
> **Agent**:
> 1. 跑 Step 1：2 commits, 4 files, +56/-12, size=S, 平台=GitLab（`.gitlab/merge_request_templates/` 存在）
> 2. 跑 Step 2：changeset = `src/orders/export.py` (1), `src/celery/tasks.py` (1), `tests/orders/` (2)
> 3. breaking=False
> 4. 标题：`fix(orders): 修复订单导出超时 (timeout 30s→120s)`
> 5. 产出 GitLab MR 格式（用 `>` 引用块、checkmark 复选框）：
>
> ```markdown
> ## 概要
> > 修复大批量订单导出任务在数据量 >5k 时超时失败的问题。
>
> ## 改动原因
> - 当前 `celery_task_hard_time_limit=30s` 在双 11 活动期间频繁超时
> - 改为 `120s` + 增加分批处理 (`batch_size=500`)
> - 失败任务自动重试 2 次，间隔指数退避
>
> ## 改动清单
>
> | 文件 | 改动 | 行数 |
> |------|------|------|
> | `src/orders/export.py` | 核心逻辑 | +38/-8 |
> | `src/celery/tasks.py` | timeout + 重试 | +12/-3 |
> | `tests/orders/test_export.py` | 新增 6 个测试 | +50/-1 |
> | `tests/celery/test_tasks.py` | 重试测试 | +6/-0 |
>
> ## 测试
> - [x] `pytest tests/orders/test_export.py -v` — 6/6 passed
> - [x] 手动测试 8k 订单 → 42s 完成，无超时
> - [x] 监控 `celery_task_timeout_total` 在 staging 1h 内为 0
>
> ## 影响范围
> - 部署后需要重启 celery worker
> - 无 schema 变更，无需 DB migration
> - 可随时回滚（`git revert`）
>
> ## 关注人
> @orders-team @sre-oncall
> ```
> 1-行通知：
> ```text
> 🔧 [orders] 修复订单导出超时 — 4 files, +56/-12, size=S, @orders-team 评审
> ```

## Common Pitfalls / 常见陷阱

| 问题 | 解决方案 |
|------|---------|
| 分支名带个人前缀（`yimgao/feat-...`）干扰 scope 推断 | Strip `username/` + WIP/fixup/squash! 前缀后再分类 |
| 一次 commit 改了 8 个无关功能 | 不要试图智能分组；提示用户 "This commit spans multiple concerns — consider splitting into N PRs" |
| Conventional Commits `!:` 标志位丢了，导致漏判 breaking | 显式正则 `^[a-z]+(\([^)]+\))?!:` |
| 模板里有 emoji 占位符（`<!-- 🚀 ... -->`） | 把内容塞进注释内/后，不删除原始装饰 |
| 仓库有 CODEOWNERS 但 pattern 用了 `*` 全局 | 优先匹配最具体的 pattern；`/` 结尾的 pattern 严格匹配目录 |
| 用户说 "写 PR description" 但没指定 base | 默认 base=`main`；如果 `main` 不存在则尝试 `master`/`develop`，仍失败 → 显式 ask |
| UI 改动但用户没贴截图 | 不强求；只生成 `[Screenshot: ...]` 占位符让用户后补 |
| Breaking 改动需要 migration 脚本但仓库没有 | 给出"骨架"步骤（`migrate up/down`），不伪造完整 SQL |
| 用户已经开了 PR（`gh pr view` 返回非空） | 优先 fetch 现有 PR body → 只在空白处补全；不覆盖 reviewer 已写的内容 |
| `git diff` 输出过大（>5MB） | 只跑 `--stat` + `--name-only`；不读完整 diff 进 LLM 上下文 |
| Monorepo 一次 PR 改 200+ 文件 | 标记 `size=XL`，推荐拆分；grouping 按 `apps/<name>/` / `packages/<name>/` 切分 |
| 用户给出的是 GitLab/Bitbucket 但 skill 默认写 GitHub 风格 | 检测 `.gitlab-ci.yml` / `bitbucket-pipelines.yml` / `azure-pipelines.yml` 切平台 dialect |
| Conventional Commits subject 太长（>72 字符） | 自动截断到 60 + `...`；提示用户编辑 |
| 仓库有多个 PR 模板（在 `.github/PULL_REQUEST_TEMPLATE/` 目录） | 列出选项让用户选，或默认第一个 |
| 关联了 GitHub issue 但 commit message 没写 ticket | 跑 `git log --grep` 找 `#\d+`，再 fallback 到 branch name 正则 |

## Verification Checklist / 验证清单

输出 PR 描述前自查：

- [ ] 标题符合 Conventional Commits：`type(scope): subject`（scope 可选，< 72 字符）
- [ ] Summary ≤ 100 字符，1 句，包含 ticket 引用
- [ ] Why 段至少 2 句，解释了"为什么不" + "为什么这样"
- [ ] What changed 表格行数 ≤ 8（更大的话折叠到 `<details>`）
- [ ] 至少 1 个 `[ ]` checkbox 在 test plan
- [ ] breaking=True 时有 `⚠️ Breaking changes` 横幅 + Migration 子节
- [ ] Reviewer checklist 完整 8 项
- [ ] 不包含 secret 字符串、`.env` 内容、个人 token
- [ ] 平台方言正确：GitHub 用 `###` 折叠、GitLab 用 `>` 引用、Bitbucket 限制 HTML
- [ ] 1-行预告格式：`🚀 [scope] title — N files, +X/-Y, size=?, needs review from @team`
- [ ] 文件写到 `pr-description-<branch>.md` 而不是 `~/.zsh_history`

## Data Sources & Accuracy / 数据来源与准确性

| 数据 | 来源 | 准确性 |
|------|------|--------|
| 改动文件列表 | `git diff base...HEAD --name-only` | 100% 准确（直接读 git） |
| commit messages | `git log base...HEAD` | 100% 准确 |
| 规模评分 | `git diff --shortstat` + 启发式阈值 | 准确（与 GitHub/GitLab UI 一致） |
| 类型推断（feat/fix/...） | commit message + branch name 正则匹配 | 90%（依赖 commit 规范） |
| Scope 推断 | 改动的 top-level 目录聚类 | 85%（遇到 monorepo / 扁平结构会失效） |
| Breaking 检测 | path + commit + diff pattern | 80%（diff 内容只看 metadata；如需看真实代码需用户粘贴） |
| Reviewer 建议 | `CODEOWNERS` glob 匹配 | 100%（如果 CODEOWNERS 文件存在） |
| 模板填充 | 读 `.github/pull_request_template.md` | 100%（直接读文件） |
| 平台检测 | CI 配置文件存在性 | 95%（混合 CI 平台时取第一个） |
| Test plan 推断 | 文件 glob（`tests/`、`*_test.py`、`.spec.`） | 75%（重构无新测试会显示空） |
| 截图占位 | 路径含 `.css`/`.tsx`/`.vue` | 70%（可能在 commit message 已说"no UI"） |

**不做的事**（避免幻觉）：

- 不读 diff 的实际代码行（除非用户显式粘贴）——避免上下文爆炸
- 不猜业务"why"（会显式 ask 用户，或在 commit/branch 都没线索时标注 `<TODO: fill in>`）
- 不修改 git 历史、不 push、不创建 PR（仅生成文件 + 给命令）
- 不访问 `~/.hermes/auth.json` 或 `.env`（即使有 secret scanner 的对称需要，也不触碰凭证）
- 不联网拉 GitHub API（除非用户显式说"fetch existing PR"）

**已知限制**：

- Squash merge 后 25 commits → 1 时，原 commit message 中的 "Why" 链会丢失（建议用户保留 1-3 个详细 body 后再 squash）
- Submodule 改动不会被 `git diff` 列出（提示用户单独 add commit message 描述）
- LFS / 二进制文件不计入 +/− 行数但计入 files changed
- Conventional Commits 之外的 commit 风格（gitmoji、custom prefix）会推断错；提示用户在 Why 段手动修正
