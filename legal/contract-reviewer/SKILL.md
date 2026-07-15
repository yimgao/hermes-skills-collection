---
name: contract-reviewer
description: "Review any contract (NDA, freelance SOW, SaaS TOS, lease, employment offer) for red flags, unfair clauses, missing protections, and plain-language summary. Outputs a risk-scored redline + negotiation talking points. Never drafts legal advice — surfaces issues for you and your lawyer."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [legal, contract, freelance, nda, lease, saas, employment, red-flags, negotiation, due-diligence]
    related_skills: [salary-negotiation-coach, email-composer, business-plan-generator, pitch-deck-helper]
---

# ⚖️ Contract Reviewer — 合同审查助手

> Read any contract in plain English (or 中文), get a risk-scored redline with red-flag clauses highlighted, missing protections called out, and negotiation talking points you can actually send. 任何合同 (NDA、外包 SOW、SaaS 服务条款、租约、Offer Letter)：用大白话拆解风险，标红危险条款，补齐缺漏保护，给出可发邮件的谈判话术。

---

## Overview

This skill turns Hermes into a **first-pass contract reviewer**. You drop a contract (PDF, plain text, or pasted clause) and Hermes returns:

1. A **plain-language summary** (what is this actually saying?)
2. A **red-flag scan** with severity ratings (🔴 high / 🟡 medium / 🟢 low)
3. **Missing protections** common for this contract type
4. **Negotiation talking points** — email-ready language
5. A **risk score** (0-100) + an "act now / send to lawyer / safe to sign" verdict

Hermes does **not** replace a lawyer. It surfaces issues fast so you know what to negotiate, what to ask a lawyer about, and what to never sign as-is. Best for NDAs, freelance SOWs, Saa TOS, residential leases, equity clawback clauses, IP assignment, and employment offers where the user is **not** the legal counsel.

All summaries live locally in `~/.hermes/contract-reviewer/` — contracts are sensitive and never uploaded except via the user's explicit `analyze` invocation.

| Capability | Description |
|------------|-------------|
| **Plain-language summary** | Strip the legalese; explain each section like you'd tell a friend |
| **Risk scoring 0-100** | Weighted score across 8 risk dimensions (IP, liability, payment, IP assignment, termination, exclusivity, indemnity, governing law) |
| **Red-flag highlight** | Mark problematic clauses with severity + 1-line why it matters |
| **Missing-protection check** | Compare against a baseline for the contract type; flag missing clauses |
| **Negotiation email drafts** | Ready-to-send counter-proposals, redlines, asks |
| **Multi-jurisdiction awareness** | US / EU / China / Singapore flag-difference notes |
| **Side-by-side diff** | Compare your draft vs. counterparty's redline |
| **PDF / DOCX / TXT input** | Read PDFs via `pdftotext`; DOCX via `pandoc`; otherwise plaintext |
| **Privacy-first** | Default local-only; no cloud upload unless you say `--share` |
| **Pre-sign checklist** | Export a Markdown checklist tied to each red flag |

## When to Use

- *"Review this freelance SOW I got from a startup — fair or predatory?"*
- *"I got a job offer with 4-year RSU vest and IP assignment — what should I push back on?"*
- *"Is this residential lease standard? Can I negotiate the security deposit clause?"*
- *"Compare these two NDAs — one-way vs mutual"*
- *"What does 'indemnification' actually mean in this vendor agreement?"*
- *"帮我看一下这份外包合同有没有坑"*
- *"这个 offer letter 的竞业限制条款合理吗？"*

**Do NOT use for**: criminal matters, ongoing litigation, anything where you ARE the legal counsel, anything requiring jurisdiction-specific case-law citation. When in doubt, the skill tells you "send this to a real lawyer."

## Core Workflow

### Step 1 — Ingest the contract

Accept the contract in any of these forms:

```bash
# 1. PDF on disk
pdftotext contract.pdf - | hermes -s contract-reviewer "review this"

# 2. DOCX
pandoc contract.docx -t plain | hermes -s contract-reviewer "review this freelance SOW"

# 3. Pasted text
hermes -s contract-reviewer "review this clause: [paste]"

# 4. Image scan (poor quality fallback) — extract via OCR first
ocrmypdf scan.pdf clean.pdf && pdftotext clean.pdf - | hermes -s contract-reviewer
```

**Detect contract type first** — pattern-match on signals:

| Signal | Likely type |
|--------|-------------|
| "Statement of Work", "Deliverables", "Milestones" | Freelance SOW |
| "Terms of Service", "Acceptable Use", "User-Generated Content" | SaaS / TOS |
| "Lessor", "Lessee", "Security Deposit", "Premises" | Residential lease |
| "Offer of Employment", "At-will", "RSU", "Stock option" | Employment offer |
| "Mutual Non-Disclosure", "Confidential Information" | NDA |
| "Master Services Agreement", "Statement of Work", "Change Order" | MSA / Consulting |
| "Artist", "Recording", "Royalty", "Mechanical rights" | Entertainment / Music |

If unclear, ask one clarifying question: *"What kind of contract is this?"*

### Step 2 — Risk scan (8 dimensions)

Score each dimension 0-10; total is **weighted average × 10** (so a 0-100 score).

| Dimension | Weight | What to flag |
|-----------|--------|-------------|
| **Intellectual Property** | 20% | Broad IP assignment ("all work product", "any invention conceived during term"); missing moral rights; no carve-out for prior inventions / open-source |
| **Liability & Indemnity** | 20% | Unlimited liability; one-way indemnity; consequential damages waived by you only; IP infringement indemnity placed on weaker party |
| **Payment & Term** | 15% | Net-60+ payment terms; late-fee asymmetry; no kill-fee; auto-renewal without notice; rate-lock absent |
| **Termination & Exit** | 15% | Termination-for-convenience one-way; missing cure period; data-return clause absent; non-solicit 24+ months post-term |
| **Exclusivity & Non-compete** | 10% | Worldwide non-compete; non-compete exceeds 12 months; non-solicit covers all clients (not just those you serviced) |
| **Confidentiality scope** | 5% | Definition too broad ("all information disclosed"); perpetual obligations; no exceptions (public domain, independently developed) |
| **Governing Law & Disputes** | 10% | Mandatory arbitration in counterparty's jurisdiction; class-action waiver in consumer TOS; jury waiver |
| **Misc boilerplate** | 5% | Missing entire-agreement clause; unilateral amendment; assignment on M&A without consent |

Risk-band mapping:

| Score | Verdict | Action |
|-------|---------|--------|
| 0-25 | 🟢 Low risk | Sign with minor edits |
| 26-50 | 🟡 Medium | Negotiate the 🟡 items; safe to sign after redline |
| 51-75 | 🟠 High | Counter-propose; do NOT sign as-is |
| 76-100 | 🔴 Critical | Reject / walk away / mandatory lawyer review |

### Step 3 — Output: the review package

Always return **all five** sections in this order, in plain language first, then bullets:

```markdown
## 1. Plain-language summary
[3-5 sentences: what is this contract, who owes what to whom, when does it end, what's the big risk]

## 2. Risk score: 62/100 🟠 High
- IP: 8/10 — broad assignment
- Liability: 9/10 — unlimited indemnity
- Payment: 4/10 — net-45 OK
[... per-dimension breakdown]

## 3. 🔴 Red flags
| # | Clause | Severity | Why it matters |
|---|--------|----------|----------------|
| 1 | §4.2 "all work product" | 🔴 | Assigns IP on anything you touch during the engagement, even unrelated side projects |
| 2 | §11 indemnity | 🔴 | You indemnify them for "any claim," unlimited |
| 3 | §15 non-compete 24mo | 🟠 | Worldwide non-compete exceeds industry standard (12mo, regional) |

## 4. ⚠️ Missing protections
- [ ] No carve-out for prior inventions / open-source contributions
- [ ] No data-return / porting clause on termination
- [ ] No mutual indemnification

## 5. ✉️ Negotiation talking points (email-ready)

> Subject: Quick redline on SOW — three asks before signing

Hi [Name],

Thanks for sending this over. I went through it and three items need adjusting before I can sign. I'd like to:
1. Narrow §4.2 IP assignment to **work product within this engagement**, with a carve-out for my existing tools and open-source contributions.
2. Cap indemnity at fees paid (or 1× fees, whichever is greater) and make it **mutual**.
3. Reduce the non-compete to **12 months, limited to direct competitors in [vertical/region]**.

Happy to discuss on a quick call if helpful.

Best,
[You]
```

**Critical safety rails** — never violate:

1. **Disclaimer first line, every review**: *"⚠️ Not legal advice. This surfaces common issues and patterns. For binding decisions, consult a licensed attorney in your jurisdiction."*
2. **Jurisdiction matters** — if contract type + jurisdiction unknown, ask before scoring governing-law.
3. **Never claim enforceability** — say "This clause is **commonly struck down** in [jurisdiction]" not "This is unenforceable."
4. **Never invent case law** — if asked for citations, point to the user's lawyer.
5. **Confidential content** — by default, run local-only. If user adds `--share`, flag a warning.

### Step 4 — Persist + track (optional)

After review, save a structured summary to `~/.hermes/contract-reviewer/contracts/<date>-<slug>.json`:

```json
{
  "slug": "freelance-sow-acme-2026-07",
  "type": "freelance_sow",
  "jurisdiction": "California, USA",
  "score": 62,
  "verdict": "high_risk",
  "red_flags_count": {"high": 2, "medium": 3, "low": 1},
  "reviewed_at": "2026-07-14T10:00:00Z",
  "negotiation_status": "drafting_email",
  "lawyer_referral": true,
  "notes": "Push back on IP assignment §4.2 + indemnity §11"
}
```

Track open negotiations with cron-friendly status updates:

```bash
hermes -s contract-reviewer "list pending contract reviews"
hermes -s contract-reviewer "update status of freelance-sow-acme-2026-07 → counterparty_replied"
```

### Step 5 — Diff mode (bonus)

When two versions exist (your draft vs. theirs):

```bash
diff -u draft-v1.md counterparty-v2.md | hermes -s contract-reviewer "diff these and tell me what changed in risk"
```

Returns "Risk went from 41 → 67; counterparty added one-way indemnity (§11) and tightened non-compete geography."

## Example Invocations

### Example 1 — Freelance SOW

> **User**: "Review this freelance SOW I got from a Series B startup. PDF attached."

> **Hermes**:
> ```
> ## 1. Plain-language summary
> You're doing a 3-month design sprint at $120/hr, deliver a clickable Figma prototype + design system. They own everything you make. You have a 24-month worldwide non-compete. They can fire you on 7 days' notice with no kill-fee.
>
> ## 2. Risk score: 67/100 🟠 High
> | Dimension | Score |
> |-----------|-------|
> | IP | 9/10 |
> | Liability | 6/10 |
> | Payment | 3/10 |
> | Termination | 8/10 |
> | Exclusivity | 9/10 |
> | Confidentiality | 4/10 |
> | Governing law | 5/10 |
> | Boilerplate | 3/10 |
>
> ## 3. 🔴 Red flags
> | # | Clause | Severity | Why |
> |---|--------|----------|-----|
> | 1 | §4.2 "all work product" | 🔴 | Sweeping IP grab — assigns anything you make during the term, even personal projects at 2am |
> | 2 | §9.1 24mo non-compete, worldwide | 🔴 | Two-times the industry standard; not enforceable in CA but they can try |
> | 3 | §6 termination 7 days, no kill-fee | 🟠 | They can walk cheaply; you can't |
> | 4 | §11 indemnity uncapped | 🟠 | You carry unlimited liability for client claims |
>
> ## 4. ⚠️ Missing protections
> - [ ] Prior-inventions carve-out
> - [ ] Kill-fee on early termination (½ remaining fees)
> - [ ] Mutual indemnity
> - [ ] Mutual non-compete (currently one-way)
> - [ ] Data / design file return clause
>
> ## 5. ✉️ Negotiation email
> [full email draft as in Step 3]
>
> ⚠️ Not legal advice. For binding decisions, consult a licensed attorney in your jurisdiction.
> ```

### Example 2 — Job offer

> **User**: "我刚拿到一个 startup 的 offer，年薪 $145k + 0.15% RSU (4年 vest, 1年 cliff), at-will, IP 全部归公司。帮我看下。" (offer includes broad IP, 1-year cliff, no severance)

> **Hermes**:
> ```
> ## 1. Plain-language summary
> 加州 startup 的 at-will offer: 四年 RSU、一年悬崖，全职工作期间的所有发明都归公司（包括你自己下班后写的项目）；他们可以随时让你走，无遣散金。
>
> ## 2. Risk score: 58/100 🟠 High
> | 维度 | 分数 |
> |------|------|
> | 知识产权 | 9/10 — §7 全部 IP 转让 |
> | 终止 | 7/10 — at-will，无遣散 |
> | 股权 | 6/10 — 4年 vest + 1年 cliff 标准，但无 acceleration 触发 |
> | 竞业 | N/A — 加州法律禁止非竞争 |
> | 保密 | 5/10 |
>
> ## 3. 🔴 红旗
> | # | 条款 | 严重 | 为什么重要 |
> |---|------|------|-----------|
> | 1 | §7 IP assignment 无 prior-invention 例外 | 🔴 | 你下班后写的开源/副业项目也归公司 |
> | 2 | §3 at-will | 🟠 | 任何时候无理由解雇，无遣散 |
> | 3 | §5 1-year cliff | 🟡 | 标准但偏高，问能否降到 6 个月 |
> | 4 | 无 double-trigger acceleration | 🟡 | 公司被收购时你的 RSU 不会加速行权 |
>
> ## 4. ⚠️ 缺漏保护
> - [ ] Prior-inventions 列表（附件 A）
> - [ ] Side-project / 开源贡献豁免
> - [ ] Double-trigger acceleration (control-change 后 50% vest)
> - [ ] Severance: at-will 解雇 ≥ 3 个月薪资
> - [ ] D&O 保险条款（高层才需要）
>
> ## 5. ✉️ 谈判话术
> > Subject: 几个关于 offer 的小问题
> >
> > 谢谢 offer！整体非常兴奋，有三个条款想聊一下：
> > 1. §7 IP 加入附件 A "Prior Inventions"，明确我的 GitHub/personal projects 不属于 work product
> > 2. 加 double-trigger acceleration (50% on change-of-control)
> > 3. Cliff 从 12 个月降到 6 个月
> >
> > 这三条在同类 startup 里都比较常见，看看能否调整？
> >
> > Best,
> > [You]
> ```

### Example 3 — SaaS Terms of Service (consumer-side)

> **User**: "I'm signing up for a SaaS tool for work. Their TOS has class-action waiver and mandatory arbitration. Is that a deal-breaker?"

> **Hermes**:
> ```
> ## 1. Plain-language summary
> Standard SaaS TOS for a B2B tool. By clicking "I agree" you waive your right to sue them or join a class action; disputes go to binding arbitration in Delaware.
>
> ## 2. Risk score: 31/100 🟡 Medium
> [per-dim table]
>
> ## 3. 🟡 Red flags
> | # | Clause | Severity | Why |
> |---|--------|----------|-----|
> | 1 | §14 mandatory arbitration, AAA, Delaware | 🟡 | Forces individual arbitration; limits discovery |
> | 2 | §14.2 class-action waiver | 🟡 | Cannot join others in suit — but this is now standard in US B2B |
> | 3 | §9 unilateral amendment | 🟡 | They can change terms on 30 days' notice — opt-out window unclear |
>
> ## 4. ⚠️ What's NOT red flags (industry standard)
> - As-is warranty disclaimer
> - Limitation of liability to fees paid in 12 months
> - Data processing addendum referenced (DPA)
>
> ## 5. My take
> For a B2B SaaS at this size, the score is normal. Arbitration + class-waiver are industry-standard and likely enforceable (subject to your jurisdiction). The unilateral-amendment clause is the only one I'd email them about; ask for a 60-day notice and explicit opt-out.
>
> ⚠️ Not legal advice. ...
> ```

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| **User pastes a single clause and expects a full verdict** | First clarify scope: *"This is one clause out of context. Want me to (a) flag issues just in this clause, (b) ask you to paste more, or (c) run a full review on the document when you have it?"* |
| **User asks "is this enforceable?"** | Reframe: *"I can flag what's commonly struck down in [jurisdiction], but only a licensed attorney can give you a binding opinion on enforceability."* |
| **Contract is non-English (中文 / Korean / etc.)** | Translate to English internally, then review. Output bilingual summary for clarity. |
| **Image-only PDF (scan, no OCR)** | Run `ocrmypdf` first; warn user if OCR is poor ("extraction may miss 10-20% of text — consider re-scan") |
| **User wants to negotiate but the other party is corporate legal** | Don't sugarcoat: provide their-counterparty-perspective counter-arguments so user is prepared |
| **User signs anyway despite 🔴 flags** | Add a one-line *"you signed this on [date], knowing the flagged risks above"* note in the saved record |
| **False positives on standard clauses** ("broad IP" can be standard in some industries) | Always note industry context — entertainment vs. SaaS vs. manufacturing have different baselines |
| **User asks for case-law citations** | Always say: *"I don't cite case law — point your lawyer at §X and they can research in 15 minutes"* |
| **Multi-jurisdiction contract (e.g., US company + EU counterparty)** | Flag GDPR/DPA requirements, SCCs, data residency as separate dimension |
| **User mistakes summary for advice** | Always end with the disclaimer block |

## Verification Checklist

Before delivering a review, confirm:

- [ ] Disclaimer line appears in output
- [ ] Risk score is present (0-100) with verdict band
- [ ] All 8 dimensions scored individually with one-line justification
- [ ] Red-flag table has severity, clause reference, and 1-line "why it matters"
- [ ] Missing-protection section has at least 3 items for typical contracts
- [ ] Negotiation talking points are email-ready (subject line, greeting, sign-off)
- [ ] Jurisdiction was either detected or flagged as "unknown — please confirm"
- [ ] If contract type unclear, asked one clarifying question instead of guessing
- [ ] No fabricated case citations, statutes, or "this is enforceable in <state>" claims
- [ ] If user pasted fewer than 200 words, warned about scope ("this is a clause, not a full review")
- [ ] Saved to `~/.hermes/contract-reviewer/` if user opted into tracking
- [ ] Output language matches user input (English ↔ 中文 mixed handled gracefully)

## Data Sources & Accuracy

This skill is **opinion-driven, not data-driven** — it encodes well-known legal-pattern heuristics from public sources:

- **Baseline contract templates**: American Bar Association (ABA) model agreements, AIGA standard agreements, ASMP (American Society of Media Photographers) freelance contracts, 80/20 Software standard SOWs
- **Common risk patterns**: derived from public lawyer-blogs (LawInsider, ContractsCounsel, Rocket Lawyer, UpCounsel), LegalZoom clause libraries, and SEC EDGAR public filings
- **Jurisdiction notes**: US state laws (especially CA Labor Code §2870 on employee IP, CA B&P §16600 on non-competes, NY Gen. Oblig. §5-321 on same), EU consumer-rights directives, Singapore Employment Act, PRC 劳动合同法 (Labour Contract Law)
- **Risk-score weights**: tuned to match common deal-attorney prioritization (IP > liability > payment > termination — mirrors typical SOW review sequencing)

**Accuracy guardrails**:

- All 8 risk dimensions have a fixed definition (see Step 2 table) so reviews are comparable across contracts
- Severity bands (🔴🟠🟡🟢) match Conventional contract-counsel priority conventions
- Jurisdiction-specific claims are limited to widely-cited statutes (e.g., "CA bans non-competes under B&P §16600") — never case names
- Negotiation scripts are based on common-courtesy framing used in published ABA contract-negotiation guides, not legal research

**Out-of-scope by design**: case-law citations, jurisdiction-specific litigation outcomes, statutory interpretation beyond widely-known worker-protection statutes. Those require a lawyer.

**Limits**:

- Does NOT replace a lawyer
- Does NOT validate a contract against specific industry regulations (HIPAA, SOX, ITAR, etc. — flag and refer)
- Does NOT review tax implications of equity / deferred compensation
- Does NOT cover private-company M&A documents, securities offerings, or anything filed with the SEC
- Does NOT support cross-border tax structuring

When in doubt → recommend the user spend $200-500 on a one-hour lawyer review. Always cheaper than signing a bad contract.
