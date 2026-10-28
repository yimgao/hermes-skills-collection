---
name: command-journal
description: "Use when you remember doing something but can't remember the exact command — 'how did I do X again?', 'what was that ffmpeg flag', 'find that kubectl command I used last week', 'which curl flags did I use for the S3 upload', 'what config did I change to fix this'. Ingests your shell history (zsh/bash/fish) into a local searchable index, keeps a tagged recipe book of commands that worked, and returns the exact command with its note, tags and last-used date. Also tracks config-change knowledge so you know what you changed and when. Local JSON, stdlib-only, zero upload."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [utility, shell, terminal, history, recipes, recall, cheat-sheet, kubectl, docker, ffmpeg, aws, troubleshooting, config, local-first, privacy]
    related_skills: [web-clipper, file-organizer, disk-cleanup-advisor, format-converter, env-setup-debugger, log-analyzer, secret-scanner, dependency-auditor, git-history-analyst, browser-bookmark-cleaner]
---

# Command Journal / 命令日志本

> You fixed the deploy last Tuesday. It worked. Now the same alert fires and you have **no idea** what you ran — was it `kubectl rollout restart`? `kubectl delete pod`? Did you need `--force`? You scroll 4,000 lines of history with `history | grep kube` and find nine near-misses, one of which is the command that 500'd.
>
> 上周二你修好了部署。当时确实成功了。现在同样的告警又炸了，你**完全不记得**当时跑的是什么——`kubectl rollout restart`？`kubectl delete pod`？要不要加 `--force`？你在 4,000 行历史里翻找，只找到九条差一点点的，其中一条正是当初 500 的那条。

This skill gives your machine a memory of what you actually ran: **shell history becomes a searchable index**, commands that worked become **tagged recipes**, and config changes get **tied to a symptom**.

| Capability | What It Does | How |
|---|---|---|
| 🗂️ 历史索引 | Indexes zsh/bash/fish history into a searchable corpus | `journal.py history` |
| 📖 配方本 | Saves a working command + note + tags as a named recipe | `journal.py add "..." --title "..." --tags a,b` |
| 🔎 模糊召回 | Weighted full-text search across recipes + history | `journal.py search "restart gateway"` |
| 🏷️ 标签过滤 | Filters recipes by tag, project, or tool | `journal.py list --tag k8s` |
| 📊 使用统计 | Top tools, command frequency, stale recipes | `journal.py stats` |
| 🩺 症状→解法 | Maps a symptom phrase to the config/command that fixed it | recipe `note` + tag convention |
| 📤 导出 | Markdown cheatsheet or JSON | `journal.py export --format md` |
| ⏰ 定时刷新 | Hourly cron to keep the index warm | `ingest-history.sh` |

**Design principle: this skill never executes anything.** It records and recalls. Nothing runs, nothing is sent anywhere.

## Overview / 概述

Command Journal sits in the gap between "web bookmarks" (things other people wrote) and "shell history" (everything you ran, including 4,000 useless `ls` lines). The useful material is a small set of commands that:

1. **Worked** and you'd want again.
2. **Are hard to reconstruct** — long flag combinations, obscure subcommands, one-liners with 6 pipes.
3. **Were run in a specific context** — only useful for one project, one server, one bug.

A raw history file gives you all three facts *if* you remember to look and know roughly what to grep for. A journal gives you them by *intent*.

| Storage | Path | Format |
|---|---|---|
| Recipes (your saved commands) | `~/.hermes/command-journal/journal.json` | JSON, atomic writes |
| History index (ingested shell history) | `~/.hermes/command-journal/history.json` | JSON |
| Exported cheatsheet | wherever you point `--out` | Markdown |

Set `COMMAND_JOURNAL_HOME` to relocate everything (used by the test suite and by anyone who wants the journal on iCloud/Dropbox).

## When to Use / 适用场景

- "我上次重启服务是怎么做的来着？"
- "How do I do that S3 upload again? I don't remember the flags."
- "What's the kubectl command for rolling back a failed deployment?"
- "找出我上次改的那个 nginx 配置"
- "Which curl flags did I use for the webhook test?"
- "我上次解决这个 502 到底改了什么？"
- "What was that ffmpeg one-liner for compressing video?"
- "Show me the commands I run most often with kubectl."
- "我有一堆收藏的命令，能不能整理成一份 cheatsheet？"

**Not for:** executing commands, auditing what happened on a *server* (use `log-analyzer`), reading another person's shell (not yours), or storing secrets (a password pasted into a recipe sits in plaintext on disk — see Pitfalls).

## Core Workflow / 核心工作流

### Step 1：建立索引（一次性）

Ingest your shell history. The parser understands zsh extended format (`: <epoch>:<elapsed>;cmd`), bash with `#<epoch>` timestamp lines, and plain lines. Duplicates are collapsed and the result is cached, so re-running is cheap and idempotent.

```bash
cd ~/.hermes/skills/utility/command-journal/scripts   # or wherever you installed it

# Ingest default locations: ~/.zsh_history, ~/.bash_history, fish_history
python3 journal.py history

# Add your own history file
python3 journal.py history --file ~/.zsh_sessions/backup

# Index literally everything (no usefulness filter)
python3 journal.py history --all
```

The usefulness filter keeps commands that are long enough to matter, involve a real tool with flags, and aren't pure navigation (`ls`, `cd`, `git status`). On a typical machine this drops ~95% of history noise.

```
history: +34 new, 34 total indexed (from 1078 raw lines)
```

### Step 2：搜索（回答"我怎么做过的"）

```bash
python3 journal.py search restart gateway
```

```
1. [RECIPE] restart api gateway in prod
   note: scale to zero first
   tags: deploy, k8s, prod
   $ kubectl --namespace prod rollout restart deployment/api-gateway
   id: cj-0001   score: 19.0

2. [HISTORY] docker build --no-cache -t acme/api:1.4.2 .
   last used: 2026-10-21T09:14:02
```

Scoring is weighted so the *saved recipe* beats a raw history line of the same relevance:

| Field | Weight | Rationale |
|---|---|---|
| Recipe `title` | +5.0 | You named it; the name is the intent |
| Recipe `tags` | +3.0 | Explicit classification |
| Recipe `note` | +2.0 | The "why" you wrote down |
| Recipe `command` | +1.5 | Raw text match |
| Exact command match | +20.0 | Near-certain intent |
| Recency | +0 … +2.0 | Decays over 90 days |

A query with **no** match returns exit code 1 and prints nothing but a hint — it never returns a wall of weakly-related results. Use `--json` to pipe results into another tool, `--limit N` to cap results.

### Step 3：保存配方（回答"下次直接用"）

When a command actually works, save it *with context*. The context is what makes it findable later.

```bash
python3 journal.py add \
  "kubectl --namespace prod rollout restart deployment/api-gateway" \
  --title "restart api gateway in prod" \
  --note "scale to zero first, wait for rollout status" \
  --tags k8s,prod,deploy \
  --run
```

Rules that matter:

- **`--title` is in your own words.** "restart api gateway in prod" is searchable; `kubectl --namespace prod rollout restart deployment/api-gateway` is not, because you search by intent, not by syntax.
- **`--note` captures the non-obvious.** The flags are in the command. The *conditions* ("scale to zero first", "needs the VPN on") are not — put them in the note.
- **`--tags` are for filtering, not prose.** Use short lowercase keys: `k8s`, `aws`, `db`, `acme-api`, `debug`.
- **`--run` records that you just ran it.** Use it when you add a recipe for something you just executed and confirmed.

### Step 4：症状 → 解法（最高价值的用法）

When something breaks, you usually don't know the command — you know the *symptom*. Encode recipes so the symptom is a searchable term.

```bash
python3 journal.py add \
  "sudo nginx -t && sudo systemctl reload nginx" \
  --title "fix nginx 502 after config edit" \
  --note "always -t first; reload not restart, keeps connections" \
  --tags nginx,debug,502,ops
```

Now "502" or "nginx config" retrieves the fix, and the note explains the trap (`-t` before `reload`). The same trick works for:

| Symptom you'll hit | Tag to use | What you store |
|---|---|---|
| 502 / 504 from nginx | `nginx`, `502` | the validate-then-reload command |
| Pod stuck in `CrashLoopBackOff` | `k8s`, `crashloop` | the `logs --previous` + `describe` pair |
| CI failing on a lockfile | `ci`, `lockfile` | the delete-and-regenerate command |
| "Permission denied" on a key | `ssh`, `chmod` | `chmod 600 ~/.ssh/id_ed25519` |
| SSL cert expiring | `tls`, `certbot` | the renew + reload command |
| Local DB won't start | `db`, `docker` | the reset command (and what it destroys) |

**Always note the destructive part.** A journal entry that says "reset the DB" without "this deletes the volume" is a trap you'll spring on yourself in six months.

### Step 5：查看与维护

```bash
python3 journal.py list                    # all recipes, newest first
python3 journal.py list --tag k8s          # filter by tag
python3 journal.py show cj-0007            # full JSON for one recipe
python3 journal.py stats                   # top tools, top tags, stale recipes
python3 journal.py export --format md      # cheatsheet to stdout
python3 journal.py export --out ~/cheatsheet.md
python3 journal.py forget cj-0007          # delete a recipe
```

`stats` surfaces **stale recipes** — anything untouched for 180 days. That's your cue to either re-verify (is this still the right command?) or delete it.

### Step 6：定时刷新（可选但推荐）

Your history only grows if something reads it. A hourly cron keeps the index warm so Step 2 is instant.

```bash
chmod +x scripts/ingest-history.sh

# crontab -e
0 * * * * ~/.hermes/skills/utility/command-journal/scripts/ingest-history.sh \
  >> ~/command-journal-ingest.log 2>&1
```

The script is read-only on your history files, idempotent, and writes atomically (temp file + rename), so an interrupted run never corrupts the journal.

## Example Invocations / 调用示例

### 示例 1：崩溃后的召回

> **User**: 我上周修好了我们的 api gateway，现在它又 502 了。我当时到底跑了什么命令？
>
> **Agent**:
> ```bash
> python3 ~/.hermes/skills/utility/command-journal/scripts/journal.py search gateway 502 restart
> ```
> ```
> 1. [RECIPE] restart api gateway in prod
>    note: scale to zero first, wait for rollout status
>    tags: deploy, k8s, prod
>    $ kubectl --namespace prod rollout restart deployment/api-gateway
>    id: cj-0001   score: 21.5
>
> 2. [HISTORY] kubectl rollout undo deployment/api-gateway -n prod
>    last used: 2026-10-14T16:02:41
> ```
> 找到两条相关记录。第一条是你自己保存的配方（`cj-0001`），注释里写了「先缩容到 0，等 rollout 状态」。第二条是历史里的回滚命令——如果新版本有问题，用 `kubectl rollout undo` 更直接。
>
> **建议**：先看 `kubectl rollout status deployment/api-gateway -n prod` 确认是哪个版本出的问题，再决定重启还是回滚。

### 示例 2：存一条带陷阱说明的配方

> **User**: 帮我记一下 nginx 改完配置怎么生效。
>
> **Agent**:
> ```bash
> python3 journal.py add \
>   "sudo nginx -t && sudo systemctl reload nginx" \
>   --title "reload nginx after config edit" \
>   --note "always -t first; use reload not restart so connections drain" \
>   --tags nginx,ops,config \
>   --run
> ```
> ```
> saved cj-0012: reload nginx after config edit
> marked as just-run (this skill records commands, it never executes them)
> ```
> 已保存 `cj-0012`。关键点写进 note 了：`-t` 必须先跑（否则 reload 会静默失败），以及用 `reload` 而不是 `restart`，避免掐断现有连接。下次搜「nginx」「config」都能找到。

### 示例 3：整理成一份 cheatsheet

> **User**: 我收藏了不少命令，整理成一份 Markdown 给我。
>
> **Agent**:
> ```bash
> python3 journal.py stats
> ```
> ```
> recipes        : 34
> history indexed: 812
>
> top tags:
>     12  k8s
>      8  aws
>      6  nginx
>      4  db
> ```
> ```bash
> python3 journal.py export --out ~/Documents/command-cheatsheet.md
> ```
> ```
> wrote ~/Documents/command-cheatsheet.md
> ```
> 34 条配方已导出，按最近使用排序，每条带命令、注释和标签。
>
> 另外 `stats` 标出 **3 条超过 180 天没动过的配方**（`cj-0003` `cj-0005` `cj-0011`）——建议确认它们现在还是对的，否则删掉，免得以后搜出来误导自己。

## Common Pitfalls / 常见陷阱

| 问题 | 解决方案 |
|---|---|
| 标题写成命令本身，搜不到 | `--title` 用**你脑子里的说法**（「重启生产环境的 api 网关」），命令放 `--command` 位置。搜的是意图不是语法 |
| 只存命令不存 note | 命令里的 flag 下一周你还会忘；note 记**条件和坑**：「需要先开 VPN」「这个会删 volume」 |
| 密码 / token 进了配方 | 配方以明文存盘。**绝不**存凭证。用 `--note "key 在 1Password 的 acme/k8s 条目"` 代替粘贴 |
| 搜索返回一堆不相关结果 | 已修：无匹配时返回空并 exit 1。若你自己扩展了 `score()`，注意 recency boost 只能在**真的有匹配**之后加，否则任何查询都会命中所有条目 |
| 历史文件巨大，索引慢 | `history` 有 usefulness 过滤，默认只索引有意义的命令。索引结果存在 `history.json`，重复运行不会重复添加 |
| bash 历史没有时间戳 | 支持无时间戳格式：这些条目 `last used` 会缺失，但依然可搜。想要时间戳请在 bash 里开 `export HISTTIMEFORMAT='%s '` |
| 配方过时了误导未来的你 | `stats` 标出 180 天未用的条目。定期 review，或把不用的 `forget` 掉 |
| 以为它会执行命令 | 它**只记录和召回**。`--run` 只标记「我刚跑过」，不会替你跑。要执行请自己在终端跑 |
| `journal.json` 写坏了 | 写入用 temp + rename 的原子方式，几乎不会损坏。万一真坏了，工具会重建空 journal 而不会崩——但旧配方就没了，记得偶尔 `export --format json` 备份 |
| 跨机器用同一个 journal | `COMMAND_JOURNAL_HOME` 指向同步盘即可，但 JSON 文件在并发写入时可能冲突。每台机器各用各的目录更安全 |

## Verification Checklist / 验证清单

- [ ] `python3 journal.py history` 输出 `+N new`，且第二次运行输出 `+0 new`（幂等）
- [ ] `python3 journal.py add "..." --title "..." --tags "a,b"` 返回 `saved cj-XXXX`
- [ ] `python3 journal.py search <你的真实意图词>` 第一条命中正确的配方
- [ ] 搜一个**不存在**的词 → 退出码 1，输出「no matches」，且**不**列出任何配方
- [ ] `python3 journal.py list` 显示全部配方，`--tag` 过滤有效
- [ ] `python3 journal.py stats` 显示 recipes 数、history 数、top tags
- [ ] `python3 journal.py export --format md` 生成带命令块和注释的 Markdown
- [ ] `python3 journal.py show cj-0001` 返回合法 JSON
- [ ] `python3 journal.py forget cj-0001` 后 `list` 中不再出现
- [ ] `python3 scripts/selftest.py` → `34 passed, 0 failed`
- [ ] 全部配方里**没有**任何明文密码、token、私钥
- [ ] 确认 `~/.hermes/command-journal/` 权限为 `700`（配方里可能包含内网主机名和路径）

## Data Sources & Accuracy / 数据来源与准确性

| 来源 | 内容 | 准确性说明 |
|---|---|---|
| `~/.zsh_history` | zsh 命令历史（含扩展时间戳） | 精确反映执行过的命令，但**不包括**你后来手动改过、没跑过的命令 |
| `~/.bash_history` | bash 命令历史 | 无 `HISTTIMEFORMAT` 时无时间戳 |
| `fish_history` | fish 命令历史 | YAML 格式，当前解析器按纯文本行处理，可能漏掉多行命令 |
| `journal.json` | 你手动保存的配方 | **唯一可靠来源**——它带你的意图、注释和标签 |
| `history.json` | 索引缓存 | 派生数据，删掉重跑 `history` 即可重建 |

**局限与诚实说明：**

1. **历史记录的是你跑过的，不是你想起来的。** 一条命令如果失败后你改了参数重跑，journal 里会有两条。搜出来的那条不一定是对的——看注释、看时间。
2. **历史不含环境上下文。** 同一条 `npm run build` 在两个项目里含义不同。journal 的 `--cwd` 字段和 `--tags` 就是为了补上这一层。
3. **本 skill 不验证命令是否仍然有效。** 它记录的是历史事实。CLI 工具会改 flag，所以请把搜索结果当作起点而非终点——尤其是危险操作（`rm`、`drop`、`kubectl delete`）执行前确认当前文档。
4. **不会联网。** 全部本地解析，零上传，历史文件只读。
5. **搜索是词法匹配，不是语义。** 搜「重启」找不到标题里写「restart」的条目。跨语言场景请用命令里的英文 token 搜（`search restart gateway` 而非 `搜索 重启 网关`）。

## Companion Skills / 配套技能

- **`env-setup-debugger`** — 当你想不起来**环境配置**怎么配的时候（PATH、env var、版本冲突），那个 skill 负责诊断环境；本 skill 负责找回你**已经解决过**时用过的命令。
- **`log-analyzer`** — 分析**服务端**日志；本 skill 处理**你本机**跑过的命令。
- **`secret-scanner`** — 上传代码前扫密钥。本 skill 的配方可能含主机名、路径、偶尔的凭证——配合它一起用。
- **`file-organizer`** — 整理磁盘上的文件；本 skill 整理你**脑子里的操作记忆**。
- **`git-history-analyst`** — 分析仓库历史；本 skill 分析**shell** 历史。
