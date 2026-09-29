---
name: contract-drafter
description: "Draft a balanced first-version contract from chat — NDA, freelance SOW, simple MSA, partnership agreement, residential lease addendum, equity advisor letter, content creator agreement, influencer deal memo, contractor agreement, simple consulting letter. Pulls protective clauses baseline for the contract type, jurisdiction-aware (US/EU/CN/SG/UK), role-aware (who is YOU: stronger/weaker party), red-flag annotated, with negotiation-ready language and a peer-review checklist. Sister skill to contract-reviewer (which reads). All drafts saved locally as Markdown + plain text."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [legal, contract, nda, freelance, sow, lease, partnership, equity, influencer, saas, drafting, templates]
    related_skills: [contract-reviewer, salary-negotiation-coach, bill-negotiator, business-plan-generator, referral-ask-drafter, email-composer]
---

# 📜 Contract Drafter — 合同起草助手

> Generate a balanced, protective first draft of any common small-business or personal contract from a short chat brief. Pick from 10 built-in contract templates (NDA, freelance SOW, simple MSA, partnership, residential lease addendum, equity advisor letter, content creator, influencer deal memo, consulting letter, contractor agreement), fill in party + deal terms, get a clean Markdown draft with red-flag annotations explaining every clause you might be giving up. **Sister skill** to `contract-reviewer` — that one *reads*; this one *writes*.

---

## Overview

Hermes becomes a **first-pass contract drafter** that produces a usable starting draft in under five minutes. You describe the deal in plain language ("I'm hiring a designer for a 6-week project, $8k, deliverables are hero images and 3 social cuts"), and you get back:

1. A **template-picked draft** with the right protective baseline for your role (you-as-vendor vs. you-as-client flips key clauses)
2. **Inline annotations** on every clause that flags "this favors the counterparty — here's the typical negotiation line"
3. **Two snapshots**: friendly plain-English summary the counterparty will accept, and the formal legalese version
4. A **peer-review checklist** of the 5-10 things to triple-check before signing
5. **Filing instructions**: where to save (`~/.hermes/contracts/`), how to convert to DOCX/PDF, version naming

This skill does **not** replace a lawyer for high-stakes deals (>$50k, M&A, IP-heavy SaaS, real-estate purchase, anything with regulatory exposure). It is a 0-to-60% draft tool so you're not starting from blank. Past that threshold the skill tells you when to escalate.

| Capability | Description |
|------------|-------------|
| **10 built-in templates** | NDA (mutual + one-way), freelance SOW, simple MSA, partnership, residential lease addendum, equity advisor letter, content creator, influencer deal memo, consulting letter, contractor agreement |
| **Role-aware drafting** | Auto-flips clauses (IP assignment, payment timing, termination right, indemnity) based on whether YOU are the service provider or the buyer of services |
| **Jurisdiction selection** | US-default, with optional EU/UK/China/Singapore/Canada variations on governing law, data protection, non-compete enforceability, electronic signature validity |
| **Plain-English + legalese dual track** | Friendly version for the human reader + formal version ready to print/send |
| **Inline red-flag annotations** | Each clause that's negotiable gets a `[NOTE]` block: typical market position + sample counter-language |
| **Auto-fill from chat** | Pulls parties, dates, amounts, deliverables from your one-paragraph brief — asks at most 3-5 clarifying questions for the gaps |
| **Peer-review checklist** | Auto-generated "before you sign" checklist tied to the specific draft |
| **Multi-format export** | Markdown (canonical), plain text, DOCX (via pandoc), PDF (via pandoc + wkhtmltopdf) |
| **Privacy-first local storage** | All drafts in `~/.hermes/contracts/` by default; never uploaded unless you say `--share` |
| **Side-by-side variants** | Generate two roles' versions (e.g., "draft it as if I were the consultant, then again as if I were the client") for one-pager comparison |
| **Amendment-aware** | "Add a §X.Y that the parties agree to …" — patch an existing draft without rewriting the whole thing |

## When to Use

- *"I just signed a freelance design contract — draft a counter that protects my IP and rates"*
- *"Generate an NDA for a coffee chat with a founder, mutual, California"*
- *"Write the SOW for my web developer — 6 weeks, $9k fixed price, WordPress + Stripe"*
- *"I'm hiring a fractional CMO. Draft a simple consulting agreement, 12 hrs/month, $15k/month"*
- *"Draft an equity advisor letter for a seed-stage advisor — 0.5% for 12 months"*
- *"I want a partnership agreement for a 50/50 podcast — both contribute time + cover costs"*
- *"Generate an influencer deal memo for a $2,500 IG reel"*
- *"Help me add a 'kill fee + IP reverts' amendment to my existing SOW"*
- *"I'm subletting a room — draft a residential lease addendum, CA, 6 months"*
- *"Draft a content creator agreement — scriptwriter gets 5% of gross ad rev for 24 months"*
- *"我们公司的外包合同要续约，给我起草一份中英文双语版 SOW"*
- *"我现在要约一个独立设计师做产品 logo 包装，帮我出一份合同草稿"*

**Do NOT use for**: M&A, securities issuances (use a securities lawyer), employment mass layoffs, real-estate purchase, anything in active litigation, immigration filings, or anything where you ARE the licensed attorney. Skill will tell you to escalate when the deal crosses the threshold.

## Core Workflow

### Step 1 — Classify the contract (auto + clarifying questions)

From the user's one-paragraph brief, classify the contract using signal-pattern matching — same playbook as `contract-reviewer`, but for drafting:

| Signal in user's brief | Template | Default flags |
|-----------------------|----------|---------------|
| "NDA", "confidentiality", "chat with someone about my idea" | `nda-mutual` or `nda-oneway` | term length, definition of confidential, residuals clause |
| "freelance", "designer/developer/writer", "project", "deliverables" | `freelance-sow` | IP assignment, kill fee, late payment |
| "consulting", "fractional", "hours per month", "advisor" | `consulting-letter` or `equity-advisor` if equity | exclusivity, non-solicit, IP carve-outs |
| "partnership", "50/50", "co-founder", "joint venture" | `partnership-agreement` | decision rights, capital calls, exit, dispute resolution |
| "lease addendum", "sublet", "room rental", "tenant" | `residential-lease-addendum` | deposit, maintenance, guest policy, early termination |
| "influencer", "creator", "Instagram/TikTok/YouTube brand deal" | `influencer-deal-memo` | usage rights, exclusivity, FTC disclosure, content approval |
| "content creator", "scriptwriter", "royalty", "% of revenue" | `content-creator-agreement` | credits, reversion, derivatives |
| "SaaS pilot", "vendor agreement", "we buy from them" | `simple-msa` | SLA, data protection, termination for convenience |
| "contractor agreement", "we hire a 1099", "we pay them" | `contractor-agreement` | misclassification clauses, expenses, tools |
| "equity advisor", "0.5%/1% for X months", "founder friend" | `equity-advisor-letter` | cliff/vest, information rights, secondary-sale |

Then ask **at most 5 clarifying questions** in one batch — never drill the user. Examples:

```
✓ Got it — freelance SOW, 6 weeks, $8k fixed price, WordPress + Stripe, you're the designer/vendor.
Quick 5 questions before I draft:
1. Jurisdiction? (default: California, US)
2. When does payment trigger — on signing, on milestones, or net-30 from final delivery?
3. Who owns the IP at the end — fully transferred to client, or shared with reuse rights for you?
4. How many revision rounds are included? (typical: 2-3)
5. Any non-compete or non-solicit — and if so, scope + term?
```

If jurisdiction is unclear, default to **California, US** — most permissive freelance-friendly default — and note that in the draft.

### Step 2 — Pull the protective baseline + role-flip

Each template ships with a "neutral baseline" of clauses. The role-flip layer then **moves clauses toward the user's protective side** (without going predatory — that breaks deals).

Baseline clause set per template, e.g., freelance SOW:

1. Parties & effective date
2. Scope of work + deliverables (deliverables list with acceptance criteria)
3. Term + milestones
4. Fees + payment terms (amount, schedule, late fee, expenses)
5. IP + work product (assignment vs. license + carve-outs)
6. Confidentiality (cross-referenced to NDA if separate)
7. Representations & warranties (the freelancer has right to provide services; no IP infringement)
8. Indemnification (mutual + capped)
9. Limitation of liability (capped at fees paid or 12-month fees)
10. Term + termination (for cause, for convenience, kill fee)
11. Independent contractor (no employment relationship)
12. Non-solicit (limited, time-bound)
13. Dispute resolution (mediation → arbitration → court)
14. Miscellaneous (entire agreement, amendment, assignment, governing law, e-sign)
15. Signature blocks

**Role-flip rules** (vendor vs. client):

| Clause | You're the VENDOR (freelancer/consultant) | You're the CLIENT (buyer) |
|--------|------------------------------------------|----------------------------|
| IP assignment | License + carve-outs for prior tools & open-source; client gets paid-up license to deliverables | Full assignment of deliverables with explicit "tools & pre-existing IP excluded" carve-out to keep vendor happy |
| Payment trigger | 50% on signing, 50% on delivery OR net-15 from milestone completion | Net-30 or Net-45 from invoice acceptance |
| Revisions | 2 rounds in scope; additional rounds $X/hr | "Reasonable revisions" until acceptance |
| Kill fee | 50% of remaining contract value on early termination by client | No kill fee OR 25% if vendor terminates without cause |
| Non-solicit | 12 months, named contacts only, no cold re-engage | 24 months for direct clients only (not the entire market) |
| Liability cap | 12-month fees paid (or actual damages) | 24-month fees paid |
| Warranty | "Services performed in workmanlike manner" — no broader | Add "fitness for particular purpose" disclaimer |

These flips are not loopholes — they are the **market standard for fair deals** in most US jurisdictions and most EU member states.

### Step 3 — Draft with inline red-flag annotations

Output the draft as **Markdown** with this structure:

```markdown
# [Contract Title]

**Effective date:** [DATE]  
**Parties:** [Party A (you)] and [Party B (counterparty)]  
**Governing law:** [State/Country] — default California unless stated otherwise

---

## §1. Scope of services
[Clause text in formal legalese]

> 📝 **[ANNOTATION — Vendor-favorable]** This wording locks the deliverable list
> to §1 only. If the client asks for "one more thing" mid-project, it's a
> change order at $X/hr. Negotiable to remove if you trust the counterparty.

## §2. Term
...

## §3. Fees & payment
...

[repeat for all 14-15 sections]

---

## ✓ Peer-review checklist before signing

- [ ] All bracketed `[placeholders]` filled in
- [ ] Jurisdiction confirmed with counterparty's principal place of business
- [ ] IP carve-out covers your real tools (list them)
- [ ] Payment terms match your cash flow (≤ Net-30 if you're vendor)
- [ ] Kill-fee clause present if you're the vendor
- [ ] Dispute resolution doesn't force you to litigate in counterparty's city
- [ ] Non-solicit scope is bounded (named clients only, time-limited)
- [ ] Signature blocks include printed name + title + date
- [ ] Counterparty is authorized signer (LLC: check secretary of state)
- [ ] If >$10k: ran contract-reviewer on the final draft

---

## Negotiation prefixes (paste as email opener)

> Subject: Quick redline on [contract name] — three asks before signing
>
> Hi [Name],
>
> Thanks for sending this over. Three small items before I sign:
> 1. [Specific clause + proposed language]
> 2. [...]
> 3. [...]
>
> Other than that, ready to go.
```

Always end with a **5-10 line plain-English summary** the counterparty can read in 60 seconds. Even signed-in-blood lawyers skim that first.

### Step 4 — Save locally + optional export

Default location: `~/.hermes/contracts/{type}-{counterparty-slug}-{YYYY-MM-DD}.md`

```bash
# Default — save as Markdown
mkdir -p ~/.hermes/contracts
hermes -s contract-drafter "draft freelance SOW with Acme — 6wk, $8k, designer = me"

# Export to DOCX for sending
pandoc ~/.hermes/contracts/freelance-sow-acme-2026-09-22.md \
  -o ~/Desktop/freelance-sow-acme.docx

# Export to PDF (with wkhtmltopdf or pandoc + latex)
pandoc ~/.hermes/contracts/freelance-sow-acme-2026-09-22.md \
  -o ~/Desktop/freelance-sow-acme.pdf --pdf-engine=wkhtmltopdf

# Share link (only if user says --share)
hermes -s contract-drafter --share "draft …"
```

When user later asks *"add a §7 termination for convenience"*, the skill patches the saved draft in place rather than rewriting the whole thing — preserves version history.

### Step 5 — Pair-review loop with `contract-reviewer`

Once a draft exists, the natural next move is to run `contract-reviewer` over the final version to catch anything the drafter missed. The two skills are intentionally complementary:

```
contract-drafter:    0 → 60%   (give me a starting draft)
contract-reviewer:   60 → 95%  (catch risks, suggest redlines)
real lawyer:         95 → 100% (sign-off on $50k+ deals)
```

If a draft touches threshold ($50k+ OR M&A OR regulated industry OR international tax exposure), the skill **flags the escalation** explicitly at the top:

> ⚠️ **This deal crosses the threshold where a real lawyer should review before signing.**
> Draft provided below as a starting point. Do not rely on it as-is.

## Example Invocations

### Example 1 — Freelance SOW (you're the vendor)

> **User:** I'm a freelance designer, just got off a call with Acme Corp. They want a
> brand refresh: new logo, brand guide, 5 social templates. Timeline 6 weeks, budget
> $9,500 fixed. I'm sending the first draft. Help me draft an SOW.
>
> **Hermes:** Got it. Before I write, four quick things:
>
> 1. **Your jurisdiction / theirs?** Acme is in Texas — I'll default to California
>    governing law (standard for freelance work) unless you say otherwise.
> 2. **Payment timing?** 50% on signing + 50% on final delivery is typical for
>    fixed-price work. Want that, or net-30 from each milestone?
> 3. **IP at the end — full assignment, or license + reuse rights for you?**
>    Most designers keep a license for portfolio + similar client work.
> 4. **Revisions?** 2 rounds in scope, additional at $150/hr is fair.
>
> Ok assuming 1=CA, 2=50/50, 3=license-with-portfolio-right, 4=2 rounds —
> drafting now.
>
> ```markdown
> # Statement of Work — Acme Corp Brand Refresh
>
> **Effective date:** 2026-09-22
> **Service provider:** [Your name / Your LLC], California, USA
> **Client:** Acme Corp, Delaware, operating in Texas
> **Governing law:** California
>
> ## §1. Scope
> Service provider will deliver, on a fixed-price basis:
> - **Logo suite**: primary mark, secondary mark, monochrome variant, favicon
> - **Brand guide**: 12-page PDF covering typography, color, voice, usage
> - **5 social templates**: 1080×1080 + 1080×1920, editable Figma
>
> > 📝 [ANNOTATION — Vendor-favorable] "On a fixed-price basis" locks budget.
> > Anything new is a change order at your hourly rate ($150/hr default).
>
> ## §2. Milestones & payment
> | Milestone | Deliverable | Due | % | Amount |
> |-----------|-------------|-----|---|--------|
> | M1 Kickoff | signed SOW + deposit | Week 0 | 50% | $4,750 |
> | M2 Brand exploration | 3 logo directions | Week 2 | — | — |
> | M3 Final logo + guide | Approved final + brand guide PDF | Week 5 | 50% | $4,750 |
> | M4 Social templates | 5 templates in Figma | Week 6 | — | (in M3) |
> ...
> ```
>
> Saved to `~/.hermes/contracts/freelance-sow-acme-2026-09-22.md`. Want me to
> also run `contract-reviewer` on the draft once you've filled in your details?

### Example 2 — NDA (mutual, casual)

> **User:** 我下周要和一位 YC 创始人咖啡聊我自己的想法。
> 帮我出一份简单的 mutual NDA，California。
>
> **Hermes:** 好的。一份 mutual NDA，California 州法。 标准 3 年保密期，
> 排除条款（公开信息、独立开发、对方已知的）齐全。
>
> ```markdown
> # Mutual Non-Disclosure Agreement
>
> **Effective date:** 2026-09-22
> **Party A:** [Your name], California, USA
> **Party B:** [Founder name], [their company], California, USA
> ...
> ## §1 Definition of Confidential Information
> "Confidential Information" means any non-public information disclosed by either party...
>
> ## §2 Exclusions
> Confidential Information does not include information that:
> (a) is or becomes publicly available through no fault of the receiving party;
> (b) was known to the receiving party prior to disclosure;
> (c) is independently developed without use of the disclosing party's information; or
> (d) is required to be disclosed by law, with prompt notice to the disclosing party.
>
> ## §3 Term
> This Agreement enters into effect on the Effective Date and continues for 3 years...
> ...
> ```
>
> 已存到 `~/.hermes/contracts/nda-mutual-foundercoffee-2026-09-22.md`.
> 提醒一句：和创业者朋友聊想法，**法律上 NDA 很难强制执行**，真出事不好打官司。
> 建议心里先分级——核心 idea 不聊，执行细节可以聊。要不要我也给一份不签 NDA
> 的 “分级讨论指南” 给你用？

### Example 3 — Amendment patch (skill's superpower)

> **User:** I have my existing freelance SOW saved at
> `~/.hermes/contracts/freelance-sow-acme-2026-09-22.md`. Add a §7 about
> termination for convenience, with a 14-day notice and a kill fee of 50% of
> remaining contract value. Don't rewrite the whole thing.
>
> **Hermes:** Patching now — won't touch the other sections.
>
> ```diff
> ## §6 Term
> This Agreement begins on the Effective Date and continues until the later of
> (a) acceptance of all Deliverables, or (b) 2026-12-31.
>
> +## §7 Termination for convenience
> +Either party may terminate this Agreement for convenience upon 14 days'
> +written notice to the other party. If Client terminates for convenience
> +before acceptance of all Deliverables, Client shall pay Service Provider
> +a kill fee equal to 50% of the unpaid balance of the fixed-price Fees,
> +due within 7 days of termination.
> +
> +> 📝 [ANNOTATION — Vendor-favorable] Standard freelance kill-fee for
> +> fixed-price work, protects the freelancer if the client walks mid-project.
> +> Industry range: 25-75% of remaining value.
> ```
>
> Patched in place. Three alternatives if they push back:
> 1. Reduce to 25% (you take more risk)
> 2. Tie kill-fee to % of work completed (more complex to calculate)
> 3. Tie kill-fee to actual hours logged + 20% cushion
>
> Want me to export the patched contract as a "v2 — 2026-09-22-amended" DOCX
> with redline-style formatting?

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| User asks for an employment contract | Reframe — most US/CA engagements default to 1099 contractor. If the role is genuinely W-2, redirect to employee offer letter templates with at-will language, and flag misclassification risk |
| User gives $0 detail ("just draft a contract") | Ask the 3-5 clarifying questions from Step 1. Never invent parties, amounts, deliverables — output a `[bracketed template]` with `[fill these in]` markers instead of guessing facts |
| User pastes an existing contract and asks to "improve it" | That's `contract-reviewer`'s job. Either hand off, or treat as a patch — ask "do you want me to redline the existing one, or use it as a model to draft a new one with similar scope?" |
| User wants to skip the peer-review checklist | Don't let them. Checklist is the whole point of the skill — the *draft* is good but the *checklist* is the safety net. Always emit it |
| User asks for high-stakes deal (>$50k, M&A, regulated) | Draft as starting point, but lead with explicit "this crosses the threshold where a real lawyer should sign off" banner. The skill should never pretend to be a substitute for counsel |
| User asks for a jurisdiction with strict non-compete (CA, MN, ND, OK) | Auto-skip or weaken the non-compete clause — those states void most non-competes. Mention it in annotation |
| User wants a contract in Chinese / Spanish / French | Match the language. Maintain legal vocabulary standard for that jurisdiction (PRC: 民法典 references; Spain: 西班牙语合同标准条款) |
| User asks for e-signature acceptance in a jurisdiction that requires wet ink (some PRC notarized types) | Flag in annotation: "this jurisdiction requires notarization; recommend DocuSign equivalent" |
| User wants to skip annotations | Provide a "clean" version in addition to the annotated one — annotations are invaluable for first-time drafters, noise for veterans |
| User wants to handle "oral agreements" / handshake deals | Refuse to backdate. Draft a written confirmation letter that memorializes the verbal terms |
| User updates an existing contract frequently | Use the patch flow (Step 4), not full re-draft. Maintain `~/.hermes/contracts/{name}/v{N}.md` versioning |

## Verification Checklist

Before finalizing any draft, confirm:

- [ ] All template placeholders filled or clearly marked `[FILL: ...]`
- [ ] Parties' full legal names + addresses listed (not just first names)
- [ ] Effective date specified (or "Effective Date" placeholder)
- [ ] Jurisdiction clause present and matches user's stated location
- [ ] Signature blocks include printed name + title + date line
- [ ] Money amounts in USD (or user's currency) with currency code, not just `$`
- [ ] If vendor: kill fee / late-payment / IP carve-out present
- [ ] If client: warranty / acceptance criteria / IP assignment present
- [ ] Non-compete scope bounded (named parties, time limit, geography)
- [ ] Dispute resolution present (mediation → arbitration → court, or just court)
- [ ] Plain-English summary at the end (3-5 bullet points, friendly tone)
- [ ] Peer-review checklist present (auto-generated)
- [ ] Escalation banner present if deal crosses legal-review threshold
- [ ] File saved locally with proper naming convention
- [ ] Run `contract-reviewer` on the final draft if user wants double-check

## Data Sources & Accuracy

This skill ships with a baseline of **10 hand-crafted templates**, each using market-standard clause language drawn from common US freelance / small-business templates (A Freelancer's Bill of Rights, AIGA Standard Agreement, ASCAP writer agreements, ASATA influencer templates, CAR residential lease addenda, AAUP consulting letter templates). The "role-flip" rules are based on widely-accepted US contract norms — not legal advice.

**Jurisdiction handling** is intentionally conservative: California is the default fallback because it's the most freelance-friendly US state and provides the best baseline for international comparison. State-specific clauses (e.g., non-compete in CA/MN/ND/OK, prompt-payment in NY, freelance isn't free act in CA) are surfaced in annotations when relevant.

**What this skill is NOT:** Legal advice. Not a substitute for a licensed attorney in your jurisdiction. Not appropriate for high-stakes deals (>$50k, regulated industries, M&A, securities, employment mass actions, immigration, real-estate purchase).

**What this skill IS:** A 0-to-60% first draft that saves 30-90 minutes of starting-from-blank time per contract, with inline teaching so you understand what each clause is doing. Pair it with `contract-reviewer` for safety, and pair it with `email-composer` for the negotiation outreach.
