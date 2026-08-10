---
name: secret-scanner
description: "Scan codebases and git history for accidentally committed secrets — API keys, tokens, private keys, .env files, connection strings. Classify risk, pinpoint commit introduction points, and generate a local remediation report. Zero cloud upload, pure grep/ripgrep + Python stdlib."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [security, secrets, api-keys, tokens, git-history, credential-leak, code-scan, privacy, devops]
    related_skills: [password-auditor, dependency-auditor, git-history-analyst, code-review-helper, env-setup-debugger]
---

# 🔐 Secret Scanner — 密钥泄露扫描器

> 每个开发者都至少把 API key 提交进过 git——区别是有些人发现了，有些人没有。这个 skill 把 Hermes 变成你的密钥雷达：扫描工作区与 git 历史，找出硬编码的 AWS key、GitHub token、私钥、.env 泄漏，定位是哪次 commit 引入的，并给出本地化的整改报告。所有检测在本地完成，密钥不出机器。

---

## Overview / 概述

Secret Scanner 对指定目录（默认是 git 仓库）做两层扫描：**工作区扫描**（当前文件）和 **git 历史扫描**（所有 commit，含已删除文件）。命中结果按风险等级分类，标注文件、行号、匹配模式、以及引入该密钥的 commit SHA 与时间。

| 能力 | 说明 | 实现方式 |
|------|------|---------|
| 🔑 密钥模式库 | 60+ 高置信度正则：AWS/GCP/Azure/GitHub/Slack/Stripe/OpenAI 等 | Python 正则 + ripgrep 备选 |
| 📄 文件类型过滤 | 默认扫全部，可指定只扫源码/配置文件/测试 | `--ext` 白名单 / `--ignore` 黑名单 |
| 🕵️ Git 历史扫描 | 找出已删除或已轮换但仍留在历史里的密钥 | `git log -p` + 逐 diff 匹配 |
| 🧭 Commit 溯源 | 定位密钥第一次出现的 commit、作者、日期 | `git log -S` + `git blame` |
| ⚠️ 风险分级 | HIGH（实时凭证）/ MEDIUM（疑似）/ LOW（误报候选） | 上下文启发式 |
| 🚫 排除误报 | 示例 key、mock 值、哈希占位、测试 fixture | 内置 denylist |
| 📋 整改报告 | Markdown 报告：文件→行号→commit→修复建议 | 本地生成 |
| 🔒 零上传 | 密钥只在本机匹配，不发送任何网络请求 | 纯本地执行 |

## When to Use / 适用场景

- *"扫一下这个项目有没有泄漏的 API key"*
- *"检查我的 git 历史里有没有提交过 .env"*
- *"我之前把 OpenAI key 提交过，后来删了，还能找回来吗？它在哪次 commit？"*
- *"发布开源项目前，帮我确认仓库里没有私钥或 token"*
- *"我的 AWS 密钥好像泄漏了，帮我找出所有用到它的地方"*
- *"部署前安全检查：这个 repo 可以直接公开吗？"*
- *"CI 日志或测试文件里有没有硬编码的密码？"*
- *"老板说仓库里有个 Slack token 泄漏了，帮我定位"*

不适用于：已联网的密钥轮换执行（只给建议，不自动调 API）、二进制文件内的密钥（需 strings + 人工确认）、需要 gitleaks/trufflehog 企业级规则集的场景（可并行安装两者做交叉验证）。

## Core Workflow / 核心工作流

### Step 1：确定扫描目标与范围

先确认目标路径和范围，避免误伤：

```bash
cd /path/to/project
# 1. 是 git 仓库吗？历史扫描需要它
git rev-parse --is-inside-work-tree
# 2. 确认大小，决定是否需要排除 node_modules / vendor / build
du -sh . 2>/dev/null
```

默认排除目录（防止噪音与假阳性）：
`node_modules/ vendor/ .git/ dist/ build/ target/ __pycache__/ .venv/ venv/ Pods/ .next/ coverage/ .terraform/`

### Step 2：工作区扫描（当前文件）

用核心正则库匹配当前工作区。优先 ripgrep（更快、默认尊重 `.gitignore`），回退 grep：

```bash
# 快速检查是否存在 .env 类文件（最常见泄漏源）
find . -name ".env*" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null

# 私钥文件（PEM 等）——高危
find . \( -name "*.pem" -o -name "*.key" -o -name "*.p12" -o -name "*.pfx" -o -name "id_rsa*" -o -name "id_ed25519*" \) \
  -not -path "*/.git/*" -not -path "*/node_modules/*" 2>/dev/null

# 高置信度密钥模式（ripgrep 风格）
rg -n --hidden -g '!{.git,node_modules,vendor,dist,build,__pycache__,.venv,venv}' \
  -e '(?i)(AKIA[0-9A-Z]{16})' \                                  # AWS Access Key ID
  -e '(?i)(gh[pousr]_[A-Za-z0-9_]{36,})' \                       # GitHub PAT / OAuth
  -e '(?i)(sk-(live|test)-[A-Za-z0-9]{20,})' \                   # Stripe
  -e '(?i)(xox[baprs]-[0-9A-Za-z-]{10,})' \                      # Slack token
  -e '(?i)(sk-[A-Za-z0-9]{20,})' \                               # OpenAI
  -e '(?i)(AIza[0-9A-Za-z_-]{35})' \                             # Google API key
  -e '-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----' \
  . 2>/dev/null
```

输出示例：
```
src/config.py:42:  api_key = "AKIAIOSFODNN7EXAMPLE"
tests/fixtures/token.json:7:  "slack": "xoxb-1234567890-abcdefghij"
```

### Step 3：Git 历史扫描（含已删除文件）

工作区干净 ≠ 历史干净。密钥一旦进过 commit，即使后来删除，也在 `.git` 对象库里永久存在。这一步找出所有历史命中：

```bash
# 全历史 diff 扫描（慢但彻底）
git log --all -p --no-color | rg -n \
  -e '(?i)(AKIA[0-9A-Z]{16})' \
  -e '(?i)(gh[pousr]_[A-Za-z0-9_]{36,})' \
  -e '(?i)(sk-(live|test)-[A-Za-z0-9]{20,})' \
  -e '(?i)(xox[baprs]-[0-9A-Za-z-]{10,})' \
  -e '-----BEGIN (RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----' \
  | head -50

# 更快：只搜曾存在但已删除的文件内容
git log --all --diff-filter=D --name-only --pretty=format:"%H" | grep -E '\.(env|pem|key|p12|pfx)$'

# 定位引入 commit（拿到密钥片段后）
git log --all -S 'AKIAIOSFODNN7EXAMPLE' --oneline --source
git log --all -S 'xoxb-1234567890' --pretty=format:"%h %an %ad %s" --date=short
```

`git log -S`（pickaxe）能精确找到密钥字符串**第一次出现**的 commit，配合 `git blame` 可定位到具体行。

### Step 4：分类、去误报、生成报告

对命中结果做三级分类：

| 等级 | 判定标准 | 处理 |
|------|---------|------|
| **HIGH** | 真实格式的密钥/私钥、出现在生产代码或 .env 泄漏中 | 立即轮换 + 从历史清除 |
| **MEDIUM** | 出现在测试文件、示例、文档中的疑似密钥 | 人工确认后清除或标注 |
| **LOW/误报** | `example`、`xxx`、`your-key-here`、`changeme`、哈希占位 | 忽略或加进 denylist |

内置误报 denylist（出现即降级）：`example`、`sample`、`test`、`mock`、`fake`、`placeholder`、`your_`、`changeme`、`xxx`、`XXXX`、`<...>`、`redacted`、`REPLACE_`。

最终输出 Markdown 报告（本地保存 `~/.hermes/secret-scanner/report-YYYY-MM-DD.md`）：

```markdown
# Secret Scan Report — 2026-08-09
## 范围
- 目标: /path/to/project (branch: main, HEAD: abc1234)
- 工作区文件数: 132 · git commits: 487

## HIGH (3)
| 文件 | 行 | 模式 | 引入 commit | 作者 | 日期 |
|------|----|------|------------|------|------|
| src/config.py | 42 | AWS Access Key | 8f3a2b1 | Alice | 2026-03-14 |
| .env | 1 | OpenAI sk-* | 2c9d0e7 | Bob | 2026-05-02 |
| deploy/id_rsa | 1 | PRIVATE KEY | 7a1b2c3 | Alice | 2025-11-30 |

## MEDIUM (2)
...

## 整改建议
1. 立即轮换 HIGH 项对应的真实凭证（AWS Console / GitHub / Stripe Dashboard）
2. 清除 git 历史：git filter-repo（见 Step 5）
3. 添加 .gitignore 与 pre-commit 钩子防止再犯
```

### Step 5：整改建议（只给命令，不代执行）

```bash
# 1. 立即把密钥从当前文件移除，改用环境变量 / 密钥管理服务
# 2. 用 git filter-repo 清除历史（推荐，重写历史）
pip install git-filter-repo
git filter-repo --replace-text <(echo 'AKIAIOSFODNN7EXAMPLE==>REDACTED') --force
# 3. 或最小侵入：确认密钥已轮换后，仅接受历史中存在但已失效
# 4. 防再犯：pre-commit 钩子（检测到密钥直接拒绝提交）
#    https://github.com/Yelp/detect-secrets 或 https://github.com/gitleaks/gitleaks
# 5. 推送后 GitHub 可能已自动标记 secret —— 去 Settings → Security 确认扫描状态
```

> ⚠️ 重写历史属于破坏性操作：**必须先轮换密钥**，且所有协作者需要重新 clone。未轮换就清历史等于给攻击者留后门。

## Example Invocations / 示例对话

**示例 1：发布前安全检查**

> **User**: 我要把这个 repo 开源，帮我检查有没有泄漏的密钥。
>
> **Agent**: 好的，开始两层扫描。先看工作区：
> - ✅ 未发现 .env / PEM / key 文件
> - ⚠️ 发现 1 处疑似 GitHub token：`src/github_client.py:18`
>
> 再看 git 历史（开源会暴露全部历史！）：
> - 🚨 **HIGH**: `config/keys.json` 曾在 commit `3a1f9c2`（2026-01-22, Alice）存在，内含 `sk-...` OpenAI key，后于 commit `7d02e4b` 删除——**但仍在历史对象库中，公开后任何人可提取**。
>
> 建议：轮换该 OpenAI key → `git filter-repo` 清除 → 重新 push。需要我给出完整命令序列吗？

**示例 2：密钥泄漏溯源**

> **User**: 我的 AWS key AKIAIOSFODNN7EXAMPLE 好像泄了，帮我查它进过哪些 commit。
>
> **Agent**: 用 pickaxe 搜索该密钥在历史中的所有出现：
> ```
> 8f3a2b1 (2026-03-14, Alice) add deployment config
> 9c0d1e2 (2026-03-15, Alice) fix typo in config
> b5e6f7a (2026-04-01, Bob) move secrets to env vars ← 删除操作
> ```
> 该密钥存在于 3 个 commit，于 4 月 1 日被移除。由于 AWS 密钥轮换需要时间，建议：1) 立即在 AWS Console 撤销该 key；2) 用 filter-repo 从历史清除。另外 `deploy/` 目录在 commit `1a2b3c4` 还提交过 `prod.pem`，一并处理。

**示例 3：CI 测试文件扫描**

> **User**: 扫一下 tests 目录，看有没有硬编码密码。
>
> **Agent**: 扫描 `tests/`（12 个文件）：发现 3 处 MEDIUM —— `tests/fixtures/auth.json` 里的 `"password": "P@ssw0rd123"`、`test_oauth.py:27` 的 `client_secret = "mock-secret-value"`。
> 前一个看起来像真实凭据的变体（建议确认），后两个是 mock 值（误报，可加 denylist）。生产代码目录 `app/` 干净。

## Common Pitfalls / 常见陷阱

| 问题 | 解决方案 |
|------|---------|
| 大量误报（示例 key、文档占位） | 启用 denylist 关键词（example/test/mock/xxx）；命中数骤降 70%+ |
| 只扫了工作区，漏掉历史密钥 | 开源/移交前必须跑 `git log --all -p` 或 `git log -S` 历史扫描 |
| 认为"删掉文件就安全了" | `.git` 对象库不会因删除而清理；必须 filter-repo 或轮换密钥 |
| 未轮换就重写历史 | 攻击者可能已拿到密钥；先轮换再清历史，顺序不可颠倒 |
| `.env` 被 `.gitignore` 忽略但早已提交 | `.gitignore` 只影响未来提交；已入库的用 `git rm --cached` + filter-repo |
| 扫到私钥但只是测试 fixture | 看路径（`test*`/`fixture`/`sample`）降级为 MEDIUM，人工确认 |
| ripgrep 未安装 | 回退 `grep -rEn`；macOS 自带 grep 但无 `.gitignore` 感知 |
| 大仓库历史扫描极慢 | 先按文件扩展名过滤（`--diff-filter=D` + `.env|.pem|.key`），再全量 |
| 忽略 submodule | `git submodule foreach` 对每个子模块单独跑历史扫描 |
| 误伤生成目录（node_modules 等） | 始终带排除列表；node_modules 里的"密钥"通常是依赖自带示例 |

## Verification Checklist / 验证清单

- [ ] 确认扫描目标路径正确，`.git` 存在且处于期望分支
- [ ] 工作区扫描跑完（.env 文件、私钥文件、正则模式三类）
- [ ] 历史扫描跑完（`git log --all -p` 或 pickaxe `-S`）
- [ ] 每个 HIGH 命中都能定位到引入 commit（SHA、作者、日期）
- [ ] denylist 已应用，误报已剔除或标注
- [ ] 报告写入 `~/.hermes/secret-scanner/`，含风险分级与整改建议
- [ ] 整改顺序正确：轮换 → 清除历史 → 防再犯钩子（如适用）
- [ ] 全程无任何网络请求发送密钥内容
- [ ] 向用户明确说明：HIGH 项必须轮换，历史重写是破坏性操作

## Data Sources & Accuracy / 数据来源与准确性

- **模式库**：基于行业公认的密钥格式（AWS `AKIA` 前缀 16 位、GitHub `ghp_` 36 位 token、Stripe `sk_live_`、Slack `xoxb-`、Google `AIza` 35 位、OpenAI `sk-`、PEM 私钥头等）与 [gitleaks](https://github.com/gitleaks/gitleaks) 规则集的开源子集整理。
- **扫描方式**：100% 本地执行（ripgrep/grep + `git log`），密钥内容不离开机器；无外部 API 依赖。
- **准确性说明**：正则匹配是"高概率提示"而非"确凿泄漏"——HIGH 判定基于格式完整性与上下文，仍需人工确认凭证是否有效；真实轮换操作请在对应平台控制台完成（本 skill 只给指引，不代执行）。
- **互补工具**：深度扫描可并行安装 `gitleaks`（go）或 `trufflehog`（python）做交叉验证；防再犯可接入 `detect-secrets` 的 pre-commit 钩子。
- **局限性**：无法检测二进制/压缩文件内的密钥（需 `strings` + 人工）；对低熵短密码（如 `"password": "abc123"`）不会标记——那是 `password-auditor` 的职责。
