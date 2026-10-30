---
name: document-briefing
description: "Turn any long document into a cited, actionable briefing — a 60-page contract, annual report, policy PDF, white paper, deck, or paper. Builds a page/slide/line-indexed map of the source, ranks the evidence that matters to your question, writes a BLUF briefing where every claim carries a real locator, then runs an anti-hallucination check that fails on invented page numbers and on quotes that are not verbatim. Handles PDF / DOCX / PPTX / HTML / MD / TXT, bilingual CN-EN, local-only, stdlib-first."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [productivity, documents, pdf, docx, pptx, reading, summarization, briefing, citations, page-numbers, contracts, due-diligence, research, annual-report, policy, compliance, anti-hallucination, local-first, bilingual]
    related_skills: [pdf-toolkit, ocr-and-documents, contract-reviewer, arxiv-paper-summarizer, fact-checker, meeting-prep-brief, decision-journal, report-formatter, screenshot-to-report, web-clipper, deep-work-canvas]
---

# 📄 Document Briefing — 长文档简报生成器

> You get a 62-page supplier contract at 9pm. Somewhere in it: a 60-day non-renewal window, a liability cap of $50,400, and a 1.5%/month late fee. You need three answers — *what did I agree to, what could hurt me, what do I do before Friday* — and you need them to be **true**, with page numbers you can point at in a meeting.
>
> 晚上 9 点你收到一份 62 页的供应商合同。里面有：60 天不续约窗口、$50,400 责任上限、每月 1.5% 滞纳金。你只需要三个答案——**我答应了什么、哪里会伤到我、周五之前我要做什么**——而且必须**准确**，带上能在会上指出来的页码。

The hard part was never "summarize". It is **not lying about page numbers**. Ask any model to summarize page 41 of a PDF it never parsed and it will invent a plausible section heading. This skill separates the two jobs:

| Job | Who does it | Why |
|---|---|---|
| Extract text + assign **stable locators** | `docdigest.py` (deterministic) | A page number must come from the file, not from a guess |
| Decide **what matters to you** | Hermes (judgement) | Only you know why you're reading it |
| Prove the claims | `docdigest.py check` (mechanical) | Fails on invented locators and fake quotes |

**Rule of the skill: no locator, no claim.** 没有定位，就没有结论。

## Overview / 概述

This skill covers the whole "I was handed a document" loop: understand its shape before reading it linearly, pull only the evidence that answers your question, write a briefing with traceable citations, and mechanically verify those citations before you send it to anyone.

| 能力 | 做什么 | 命令 |
|---|---|---|
| 🗺️ 文档地图 | Units + locators + word counts + reading time + heading candidates | `docdigest.py outline FILE` |
| 🎯 定向取证 | Ranks sentences toward your question (`--focus`) | `docdigest.py extract FILE --focus "termination"` |
| 💰 数字/日期清点 | Every amount, percentage, and date with its locator | included in digest |
| ⚖️ 义务语言抽取 | `shall / must / may not / 不得 / 必须 / 应当` sentences | included in digest |
| 🧾 JSON 交付 | Full digest for downstream scripts or your own ranking | `--json` |
| ✅ 引用校验 | Fails on non-existent pages, warns on non-verbatim quotes | `docdigest.py check FILE BRIEF.md` |
| 🔬 自检 | 38 assertions across 6 formats, incl. scanned-PDF and CJK | `python3 selftest.py` |
| 📦 5 种交付形态 | Exec one-pager, legal clause table, decision memo, reading packet, Q&A sheet | Step 5 |

**Supported formats**

| Format | Locator | Engine | Notes |
|---|---|---|---|
| `.pdf` | `p.7` | `pypdf` (or `PyPDF2`) | Needs a text layer — scanned PDFs are detected and refused with OCR guidance |
| `.docx` | `¶12` | stdlib `zipfile` + XML | Heading styles (`Heading1`, `标题 1`) honoured |
| `.pptx` | `slide.4` | stdlib `zipfile` + XML | One locator per slide; first text run = title |
| `.html` | `¶9` | `bs4` (optional) or stdlib `HTMLParser` | Drops `nav` / `script` / `style` / `footer` |
| `.md .txt .csv .log .json .yaml .py` | `L120-180` | plain read | Hard-wrapped prose is re-joined before sentence splitting |
| `.doc` (legacy) | — | — | Refused with the exact `textutil` convert command |

**What it deliberately does not do:** OCR (use `ocr-and-documents`), read charts/images, reconstruct complex multi-column table structure, or judge legal merit (use `contract-reviewer` for risk scoring against playbooks).

## When to Use / 适用场景

- "这份 60 页的合同到底要我签什么？" / "What am I actually agreeing to?"
- "Summarize this annual report — and cite the pages, I'm presenting it."
- "我把招股书丢给你，重点看风险因素和关联交易"
- "What are the payment terms, termination rights, and liability cap in this MSA?"
- "这份政策文件对我们团队有什么影响？有哪些截止日期？"
- "I have 40 minutes before this meeting — brief me on the 80-page board pack."
- "Extract every deadline and dollar amount from this document into a table."
- "这篇 30 页论文的方法和结论到底是什么，有没有明显缺陷？"
- "Did this contract auto-renew? What's the notice window?"
- "把这个 report 的 key numbers 抽出来，我要交叉核对一遍"

**Not for:** documents you wrote (you know them), a 2-paragraph email (just read it), scanned images with no text layer (OCR first), or any task where you need the document *rewritten* rather than understood (use `contract-drafter`, `report-formatter`).

## Core Workflow / 核心工作流

### Step 0 — 自检与安装（每次新机器做一次）

```bash
# pypdf is the only non-stdlib requirement, and only for PDFs
python3 -c "import pypdf" 2>/dev/null || pip3 install --quiet pypdf

# prove the whole pipeline works on this machine (38 assertions, no network)
cd ~/.hermes/skills/productivity/document-briefing/scripts
python3 selftest.py
```

Expected tail: `PASS 38 · FAIL 0 · SKIP 0`. If PDF tests `SKIP`, `cupsfilter` is absent — everything else still works. If `fitz`/`pdfplumber` are already installed, prefer `pdfplumber` manually for two-column PDFs (see Pitfalls).

Shortcut for a single question: skip to Step 2 with `--focus`.

### Step 1 — 先看地图，不要顺序读（Map before you read）

Never paste 60 pages into context. First get the shape: how many units, where the section boundaries are, how long it is, where the numbers live.

> 下文示例从脚本目录执行。在别处运行时，把 `docdigest.py` 换成绝对路径，例如
> `python3 ~/.hermes/skills/productivity/document-briefing/scripts/docdigest.py outline FILE`。

```bash
cd ~/.hermes/skills/productivity/document-briefing/scripts
python3 docdigest.py outline ~/Downloads/supplier-msa.pdf
```

```
# Document map — supplier-msa.pdf

- kind: **pdf** · locator: **page** · units: **62** · words: **28,410** · reading time: **~129 min**

## Headings worth reading first / 先读这几节
- `p.2` ★ Term and Termination
- `p.4` ★ Fees and Payment
- `p.9` ★ Limitation of Liability
- `p.14` ★ Data Protection
- `p.31` ★ Risk Factors

## Structure (read in this order) / 文档结构
| # | Locator | Words | Opening line |
|---|---------|-------|--------------|
| 1 | `p.1` | 212 | MASTER SERVICES AGREEMENT This Master Services Agreement...
| 2 | `p.2` | 604 | 1. Term and Termination This agreement shall commence on...

## Candidate evidence — quote from these, do not invent / 可引用证据
- `p.2` (score 13.5) — Customer must give sixty (60) days notice of non-renewal, otherwise the agreement auto-renews at a 7% increase.
- `p.9` (score 10.3) — Aggregate liability is capped at the fees paid in the preceding twelve months, not to exceed $50,400.

## Numbers found / 数字：$4,200 · $50,400 · 1.5% · 7% · 99.9%
## Dates found / 日期：2026-03-01 · 2026-05-15
```

Read the map and decide: which 4–8 units actually matter? Everything else you will cite only if the user asks.

### Step 2 — 定向取证（Targeted evidence, not full text）

Two moves. Pick one or both:

```bash
# A. rank evidence toward the question you were asked
python3 docdigest.py extract contract.pdf --focus "termination liability cap"

# B. pull only the pages that matter, and keep the machine-readable version
python3 docdigest.py extract contract.pdf --json --max-pages 12 --out /tmp/d.json
```

- `--focus "<phrase>"` adds +2.5 to any sentence sharing tokens with your phrase — so the evidence list becomes *your* list, not a generic one.
- `--max-pages N` caps a 300-page filing to its first N pages (annual reports put the numbers early; contracts put them everywhere).
- `--chunk-words 400` splits `.txt` / `.md` / `.html` into finer units when you need tighter locators.
- `--per-unit 8` widens the evidence pull per unit when a section is dense.

Then, and only then, if a single unit is still ambiguous, read that unit's text in full from the JSON. One page of real text beats sixty pages of guessing.

### Step 3 — 按模板写简报（Write the briefing, in a fixed shape）

Use this skeleton. The sections are not decoration — they are the questions a reader actually has, and their order is what makes a briefing fast to consume.

```markdown
# Briefing — <document name> (<unit count> units, ~<read time> min source)

## TL;DR  (≤3 sentences, BLUF)
The single most important thing, and whether it needs action.

## What it is
Type of document, parties, dates, scope — only facts that are locatable.

## Key numbers
| Item | Value | Source |
|---|---|---|
| Monthly fee | $4,200 | [p.4] |

## Obligations & deadlines  ← the section people forget
- Customer must give 60 days notice of non-renewal, or auto-renews +7% [p.2]
- Implementation due 2026-05-15 or full refund [p.6]

## Risks / what could hurt you
- Liability capped at $50,400 — under a serious incident you carry the rest [p.9]

## What to do next
- [ ] Calendar the non-renewal notice before 2027-01-01 [p.2]
- [ ] Ask for the cap to move to 24 months of fees [p.9]

## Open questions  (things the document does not answer)
- No mention of data-residency for backups — clarify before signing.
```

**Three hard rules while writing**

1. **Every factual claim gets a locator** in the exact form the tool printed — `[p.2]`, `[slide.4]`, `[¶12]`, `[L120-180]`. Ranges are fine: `[p.4-6]`.
2. **Quotation marks mean verbatim.** If you put `"..."` next to a citation, those words must be copied from that unit character for character. Paraphrase freely — just don't use quote marks for it.
3. **"Open questions" is mandatory.** A briefing with no unanswered questions is either a document with no gaps (rare) or a briefing that quietly filled them with invention (common).

### Step 4 — 机械校验引用（Verify before you deliver）

```bash
python3 docdigest.py check contract.pdf briefing.md
```

```
checked briefing.md against supplier-msa.pdf (pdf, 62 units)
  citations: 14 · verified: 14 · errors: 0 · warnings: 0

PASS — every citation resolves to a real locator in the source.
```

Failure output tells you exactly which line to fix:

```
  ERROR   L7     [p.99]       locator does not exist: p.99
  WARN    L12    [p.9]        quoted text is not verbatim in the cited unit — drop the quotes or copy exactly
```

| Exit | Meaning | Action |
|---|---|---|
| `0` | every locator exists, every quote is verbatim | deliver |
| `1` | at least one invented locator | fix the line, re-run — do not hand over a briefing with a red line |
| `2` | source unreadable (scanned PDF / missing file) | OCR or fix the path first |

Loop `check → fix` until it exits 0. This is the single most valuable step in the skill: it is the difference between "a summary" and "a summary you can defend in a meeting".

### Step 5 — 交付形态（Pick the delivery shape）

Same digest, five outputs. Ask which one, or infer from the audience.

| Form | Use when | Shape |
|---|---|---|
| **Exec one-pager** | Sending upward | TL;DR + 3 numbers + 2 risks + 1 ask |
| **Clause table** | Contract / policy | `Clause · What it says · Why it matters · Locator` |
| **Decision memo** | Choosing between options | Options, criteria, evidence per criterion, recommendation, what would change my mind |
| **Reading packet** | Pre-meeting | 5 bullets per section, ordered by the document's own structure |
| **Q&A sheet** | You'll be asked questions | 10 likely questions, each answered with a locator, plus the ones the doc can't answer |

For a contract whose *risk* is the question (not its content), hand off to `contract-reviewer` — this skill locates clauses, that skill scores them against playbooks and drafts redlines.

### Step 6 —（可选）归档与追踪

```bash
# keep the machine-readable digest next to the briefing
python3 docdigest.py extract contract.pdf --json --out ~/Documents/briefs/msa-2026.digest.json
```

Then log the decision in `decision-journal` ("signed the MSA with the 7% auto-renew because…") so that in 11 months, when it renews, you have the reasoning and not just the invoice.

## Example Invocations / 调用示例

### 示例 1 — 供应商合同，周五前要签（中文）

> **用户**：这是供应商发来的 MSA，62 页，我周五要签。帮我看看有什么坑。
>
> **Agent**：先出地图，不逐页读。
> ```bash
> python3 docdigest.py outline supplier-msa.pdf
> ```
> 62 个单元，2.8 万词，约 129 分钟原文。重点节落在 p.2（期限与终止）、p.4（费用）、p.9（责任限制）、p.14（数据保护）。数字清点发现 4 个金额、3 个日期。
>
> 然后定向取证：
> ```bash
> python3 docdigest.py extract supplier-msa.pdf --focus "termination liability data"
> ```
>
> **交付**（节选，每条都带定位）：
>
> | 条款 | 内容 | 为什么重要 | 位置 |
> |---|---|---|---|
> | 自动续约 | 到期前 60 天不通知即自动续约，涨幅 7% | 忘记一次就锁一年，且每年递增 | `[p.2]` |
> | 责任上限 | 累计赔偿上限为前 12 个月费用，最高 $50,400 | 一次严重事故你自担超出部分 | `[p.9]` |
> | 滞纳金 | 每月 1.5%（年化 18%） | 高于市场常见 1% 或按 LPR 计 | `[p.4]` |
> | 交付退款 | 2026-05-15 前未完成初始交付可全额退款 | 唯一对你有利的退出条款 | `[p.6]` |
>
> **下一步**：① 立刻在日历上设 2026-12-15 的不续约提醒 `[p.2]`；② 要求把责任上限改为 24 个月费用 `[p.9]`；③ 要求滞纳金降到 1% `[p.4]`。
>
> **文档没回答的问题**：备份数据的存储地域？分包商是否需要同等保密义务？——两处都建议书面澄清。
>
> ```bash
> python3 docdigest.py check supplier-msa.pdf briefing.md
> # PASS — 14 citations verified
> ```

### 示例 2 — 财报，一页纸 exec brief（English）

> **User**: Here's the 180-page annual report. I present in 40 minutes. One page, and cite pages — the CFO will check.
>
> **Agent**: `outline --max-pages 40` first — annual reports front-load the numbers.
> ```bash
> python3 docdigest.py extract annual-report.pdf --max-pages 40 --focus "revenue margin risk guidance"
> ```
> Key sentences cluster on p.3 (revenue), p.7 (segment margins), p.22 (risk factors), p.31 (guidance).
>
> **Briefing**
>
> **TL;DR** — Revenue grew 18% to $61.3M but gross margin fell 240bp to 61.2% because of egress costs `[p.3]` `[p.7]`. Guidance was cut for FY27 `[p.31]`, and the two largest customers are 34% of revenue `[p.22]`. Net: growth is real, quality of growth is worse.
>
> | Metric | Value | Source |
> |---|---|---|
> | Revenue | $61.3M, +18% YoY | `[p.3]` |
> | Gross margin | 61.2%, −240bp | `[p.7]` |
> | Top-2 customer concentration | 34% | `[p.22]` |
> | FY27 guidance | lowered | `[p.31]` |
>
> **Two questions to expect**: why margin fell (answer with `[p.7]` egress + hosting mix); what happens if the top customer churns (the doc does not answer this — say so).
>
> ```bash
> python3 docdigest.py check annual-report.pdf brief.md   # PASS — 9 citations verified
> ```

### 示例 3 — 扫描版 PDF，先 OCR 再简报（故障处理闭环）

> **用户**：这份 PDF 帮我总结一下。
>
> **Agent**：
> ```bash
> python3 docdigest.py stats lease.pdf
> ```
> ```
> ERROR no usable text layer (18 pages, 0 words) — this is a scanned PDF.
> OCR it first: `ocrmypdf in.pdf out.pdf`, or use the ocr-and-documents skill, then re-run.
> ```
> 这是一份扫描件，没有文字层。**不能**凭图像猜内容——猜出来的页码全是假的。
>
> ```bash
> ocrmypdf --language chi_sim+eng --deskew lease.pdf lease-ocr.pdf
> python3 docdigest.py outline lease-ocr.pdf
> ```
> 现在有 18 个单元、4,120 词、p.3 是"押金与退还"、p.11 是"提前解约"。继续 Step 2–4，`check` 通过后交付。
>
> 如果用户只想快速看押金条款，可以 `--focus "deposit return"` 直接定位到 p.3 与 p.11，不必通读。

## Common Pitfalls / 常见陷阱

| 问题 | 原因 | 解决方案 |
|---|---|---|
| `no usable text layer` / 0 词 | 扫描件或纯图片 PDF | `ocrmypdf --language chi_sim+eng in.pdf out.pdf`，或走 `ocr-and-documents`；**不要**凭截图猜内容 |
| 双栏 PDF 文字串行、句子被搅乱 | `pypdf` 按内容流顺序取字，不识别栏 | 装 `pdfplumber`，用 `extract_text(layout=True)` 手工取，或 `pdftotext -layout` 转成 txt 再跑本工具 |
| 页码对不上纸质版 | PDF 前置封面/目录导致 PDF 页码 ≠ 印刷页码 | 以工具输出的 `p.N` 为准，并在简报里注明"页码为 PDF 页" |
| `check` 报 locator doesn't exist | 引用了没抽到的页（常见于幻觉、或 `--max-pages` 截断） | 改引用；截断时不要引用超出范围的页 |
| `check` 报 quote not verbatim | 用了引号但写的是转述 | 要么删引号改成转述，要么逐字复制；中文引号 `「」` 与 `""` 都识别 |
| 表格里的数字漏了 / 串行 | PDF 表格没有结构信息 | 用数字清点表交叉核对；关键表手工核对原页；必要时 `pdfplumber` 抽表 |
| 长文档塞爆上下文 | 把全文喂进 prompt | 永远先 `outline`；只取 4–8 个相关单元；`--json --out` 落盘按需读 |
| `.doc` 读不出 | 老旧二进制格式 | `textutil -convert docx file.doc`（macOS）或 LibreOffice 转换 |
| 中文标点变成半角逗号 | 之前用 NFKC 归一化会折全角标点 | 已修复：`clean()` 保留原始标点，`norm()` 只用于匹配。若自行改脚本勿回退 |
| 硬换行导致句子被切成碎片 | txt/md 按 78 字符硬折行 | 已内置 `unwrap()`：`\n` 只代表段落/标题/列表边界；列表项与表格行不合并 |
| 把"待确认问题"写成零 | 为了显得完整而填补空白 | "Open questions / 待确认" 是必填段；空着就是编造 |
| 责任上限、终止权被漏掉 | 只做了摘要没做"义务与期限" | 模板强制 `Obligations & deadlines` 段；digest 已抽出 must/shall/不得 句子 |
| PPTX 标题识别成正文 | 首个文本块不一定是标题 | 以 `headings` 字段为准；slide 级定位不受影响 |

## Verification Checklist / 验证清单

- [ ] `python3 selftest.py` 退出码 0（`PASS 38 · FAIL 0`）
- [ ] 交付前跑过 `docdigest.py outline`，知道文档有多少单元、多长
- [ ] 简报里**每条**事实性陈述都带 locator，格式与工具输出一致（`[p.N]` / `[¶N]` / `[slide.N]` / `[L.a-b]`）
- [ ] 所有引号内的文字都是逐字复制的原文，没有把转述放进引号
- [ ] 简报包含 `Obligations & deadlines` 段（有的话），且每条指向具体定位
- [ ] 简报包含 `Open questions` 段，且至少列出文档未回答的问题
- [ ] `docdigest.py check` 退出码 0，`errors: 0`
- [ ] 引用的页码是 PDF 页（非印刷页），必要时在文首注明
- [ ] 数字表格里的金额/百分比与 digest 的 "Numbers found" 交叉核对过
- [ ] 扫描件已 OCR，**没有**任何凭图像推测出来的内容
- [ ] 超过 `--max-pages` 的文档，没有引用被截断范围之外的页

## Data Sources & Accuracy / 数据来源与准确性

**来源**：完全来自你本机上的那个文件。没有网络请求，没有上传，没有第三方 API。`docdigest.py` 只做三件事：读文件字节、抽文字、给每个单元编号。

**技术栈**

| 组件 | 用途 | 依赖 |
|---|---|---|
| `pypdf` / `PyPDF2` | PDF 文字层抽取 | 唯一可选第三方依赖，缺失时 PDF 不可用，其余格式照常 |
| stdlib `zipfile` + `re` | DOCX / PPTX 解包与段落切分 | 零依赖 |
| `bs4` | HTML 解析加速 | 可选，缺失时回退 stdlib `HTMLParser` |
| `cupsfilter` | 仅 selftest 生成测试 PDF | 可选，macOS 自带 |

**准确性边界（重要）**

- **定位与引用是机械可验证的**：`check` 能证明"p.9 存在"和"这句话逐字出现在 p.9"。这是硬事实。
- **重要性排序是启发式的**：`score_sentence` 用信号词、金额、日期、否定、篇章位置加权。它能可靠地把"责任上限"排到前面，但不能替代你判断什么对你的场景重要。永远用 `--focus` 把你的问题喂进去。
- **`check` 不能验证推论**：它不会告诉你"因此你应当拒签"是否正确。它只保证前提可追溯。
- **PDF 没有表格结构**：复杂表格可能串行；涉及金额时以数字清点为准并抽检原页。
- **不读图表与图片**：图表里的数字不会被抽取。需要时走 `screenshot-to-report` 单独处理。

**隐私**：文档内容只在本机内存与临时文件里流转。`--out` 写到哪里由你决定。处理合同、病历、财报这类敏感文件时不需要联网。

## Companion Skills / 配套技能

| 场景 | 配合技能 |
|---|---|
| 扫描件没有文字层 | `ocr-and-documents` → 再回到本技能 |
| 需要 PDF 合并/拆分/加水印 | `pdf-toolkit` |
| 合同风险打分与红线批注 | `contract-reviewer`（本技能负责定位，它负责判断） |
| 学术论文快速精读 | `arxiv-paper-summarizer`（论文专用视角） |
| 要核实文档里的外部事实 | `fact-checker` |
| 开会前要一份会前包 | `meeting-prep-brief` + 本技能的 Reading packet |
| 把结论记录成可回溯决策 | `decision-journal` |
| 图表里的数字 | `screenshot-to-report` |
| 输出成对外可发的报告 | `report-formatter` |

```bash
# install
hermes skills install https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/productivity/document-briefing/SKILL.md
```

```bash
# verify after install
cd ~/.hermes/skills/productivity/document-briefing/scripts && python3 selftest.py
```
