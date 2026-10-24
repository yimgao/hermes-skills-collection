---
name: accessibility-auditor
description: "Audit any URL for WCAG 2.1 accessibility compliance — color contrast, alt text, ARIA, semantic HTML, keyboard nav, form labels, heading order, focus indicators, screen-reader hints. Returns A/AA/AAA pass-rate, issue list with WCAG criterion + severity + fix, and a pasteable report. Pairs with seo-auditor and tech-stack-detector."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [web-analysis, accessibility, a11y, wcag, ux, compliance, frontend, audit]
    related_skills: [seo-auditor, tech-stack-detector, report-formatter, codebase-tour-guide, pr-description-writer]
---

# Accessibility Auditor / 可访问性审计器

> Audit any public URL for **WCAG 2.1 Level A / AA / AAA** accessibility compliance. Produces a structured pass-rate per principle (Perceivable / Operable / Understandable / Robust), a severity-ranked issue list with the specific WCAG criterion violated and a copy-pasteable fix snippet, plus a stakeholder-ready Markdown report.

---

## Overview

Most websites ship accessibility regressions quietly: missing alt text, low-contrast buttons, unlabeled inputs, broken keyboard focus, missing form errors. The damage compounds — it locks out ~15% of users (people with vision, motor, cognitive, or auditory disabilities) and exposes the company to ADA / EAA / Section 508 lawsuits.

This skill automates the parts of an accessibility audit that **don't require a human judge**: detectable WCAG violations, color-contrast math, semantic-HTML structure, ARIA correctness, form labelling, page-title hierarchy, language attribute, skip-link presence, focus-indicator CSS, and image/iframe/link auditability.

| Principle | What's Inspected |
|-----------|------------------|
| **Perceivable** | `<img alt>`, decorative `alt=""` on layout images, alt-quality sanity (file names, "image of"), color contrast (WCAG 2.x ratios), captioned/transcribed video/audio, text-resizable up to 200%, semantic non-text content |
| **Operable** | Page `<title>`, every link/button has accessible name, no `tabindex > 0`, keyboard reachability hints, focus-visible CSS, skip-to-content link, no keyboard traps signaled, motion/action alternatives |
| **Understandable** | `<html lang>`, language on `<html>` not just meta, consistent navigation landmarks, form `<label>` for every input, error identification, error suggestion, required-field signals, autocomplete attributes, `inputmode` for keyboards |
| **Robust** | Valid ARIA roles/properties/states, no duplicate `id`, well-formed HTML, `role` on landmark regions, `<button>` vs `<div onclick>` mismatch, custom widgets expose name+role+value, iframe `title` |

**Output:**

- Per-principle pass-rate % (A, AA, AAA)
- Issue table: severity (BLOCKER / CRITICAL / SERIOUS / MODERATE / MINOR) × WCAG criterion × page excerpt × suggested fix
- "Top 5 to fix this week" punch list
- Ready-to-paste Markdown report

---

## When to Use

- User: *"Run an accessibility audit on my marketing site"*
- User: *"Is stripe.com WCAG 2.1 AA compliant?"*
- User: *"Why is Lighthouse flagging contrast and ARIA errors on my landing page?"*
- User: *"Generate an a11y report for a client pitch deck before launch"*
- User: *"Our competitor just got sued for ADA non-compliance — how do we compare?"*
- User: *"Check this URL before I push the PR"*
- User: *"Build a pre-launch accessibility checklist"*
- User asks in CN: *"帮我看下这个网站有没有无障碍问题"* / *"跑一下 WCAG 审计"*
- User: *"Cron this URL weekly and ping me if a11y score drops below 90%"*

---

## Core Workflow

### Step 1: Fetch the URL once, save to a tmp path

```bash
mkdir -p /tmp/a11y
URL="https://example.com"

# Full HTML + headers (single connection)
curl -sSL -A "Mozilla/5.0 (Hermes-A11y-Auditor; +https://hermes-agent.nousresearch.com)" \
  -D /tmp/a11y/headers.txt \
  -o /tmp/a11y/page.html \
  -w "STATUS:%{http_code} REDIRECTS:%{num_redirects} SIZE:%{size_download} TIME:%{time_total}\n" \
  "$URL"
```

Capture the final URL (after redirects), HTTP status, byte size, redirect count. If non-200, surface it — accessibility of a 5xx page is meaningless.

### Step 2: Static signal extraction (grep + Python)

Parse the HTML once into JSON, then walk the DOM for each WCAG criterion.

```python
# scripts/scan.py — stdlib only, no extra deps
import re, json, sys, html
from html.parser import HTMLParser
from pathlib import Path

src = Path("/tmp/a11y/page.html").read_text(encoding="utf-8", errors="ignore")
```

**2a. Page-level (Perceivable / Robust):**

```python
def page_level(html):
    return {
        "doctype": bool(re.search(r"<!DOCTYPE\s+html>", html, re.I)),
        "html_lang": (re.search(r'<html[^>]+lang=[\"\']?([a-zA-Z\-]+)', html) or [None,None])[1],
        "title": (re.search(r"<title[^>]*>(.*?)</title>", html, re.S) or [None,None])[1],
        "viewport": bool(re.search(r'<meta[^>]+name=[\"\']viewport[\"\']', html, re.I)),
        "lang_inside_body": bool(re.search(r"<body[^>]+lang=", html, re.I)),
        "skip_link": bool(re.search(r'<(?:a|area)[^>]+href=[\"\']?#[^\"\']*[\"\'][^>]*>(?:Skip|Skip to|跳到|跳至)', html, re.I)),
        "h1_count": len(re.findall(r"<h1[\s>]", html, re.I)),
        "main_landmark": bool(re.search(r"<main[\s>]", html, re.I)) or bool(re.search(r'role=[\"\']main[\"\']', html)),
        "h1_text": " | ".join(re.findall(r"<h1[^>]*>(.*?)</h1>", html, re.S|re.I)),
    }
```

**2b. Images (Perceivable 1.1.1):**

```python
def image_audit(html):
    imgs = re.findall(r"<img\b[^>]*>", html, re.I)
    findings = []
    for i, tag in enumerate(imgs):
        has_alt = re.search(r"\salt\s*=", tag, re.I) is not None
        alt_val  = re.search(r'\salt\s*=\s*[\"\']([^\"\']*)[\"\']', tag, re.I)
        src_val  = re.search(r'\bsrc\s*=\s*[\"\']([^\"\']*)[\"\']', tag, re.I)
        is_decorative = alt_val and alt_val.group(1).strip() == ""
        findings.append({
            "n": i+1,
            "src": (src_val.group(1) if src_val else "")[:120],
            "has_alt_attr": has_alt,
            "alt": alt_val.group(1) if alt_val else None,
            "decorative_marker": is_decorative,
            "suspicious_alt": bool(alt_val and re.search(r"^(img|image|photo|picture|icon|图|照片)\s*\d+", alt_val.group(1).lower())),
        })
    return findings
```

**2c. Forms (Understandable 3.3.x):**

```python
def form_audit(html):
    # Find every <input>/<select>/<textarea> and check for <label> wrapping or for/id matching
    fields = re.findall(r"<(input|select|textarea)\b[^>]*>", html, re.I)
    input_ids = []
    findings = []
    for fld in fields:
        tag = fld.lower()
        m_id   = re.search(r'\bid\s*=\s*[\"\']([^\"\']+)[\"\']', fld, re.I)
        m_name = re.search(r'\bname\s*=\s*[\"\']([^\"\']+)[\"\']', fld, re.I)
        m_type = re.search(r'\btype\s*=\s*[\"\']([^\"\']+)[\"\']', fld, re.I)
        type_ = (m_type.group(1) if m_type else "text").lower()
        # skip hidden, submit, button (no label needed)
        if type_ in ("hidden", "submit", "button", "image", "reset"):
            continue
        id_ = m_id.group(1) if m_id else None
        name_ = m_name.group(1) if m_name else None
        aria_label  = re.search(r'\baria-label\s*=\s*[\"\']([^\"\']+)', fld, re.I)
        aria_labelledby = re.search(r'\baria-labelledby\s*=\s*[\"\']([^\"\']+)', fld, re.I)
        title_attr  = re.search(r'\btitle\s*=\s*[\"\']([^\"\']+)', fld, re.I)
        placeholder = re.search(r'\bplaceholder\s*=\s*[\"\']([^\"\']+)', fld, re.I)
        # look for matching <label for=id_> OR wrapping <label>...</label>
        labelled = False
        if id_ and re.search(rf'<label\b[^>]*\bfor\s*=\s*[\"\']({re.escape(id_)})[\"\']', html, re.I):
            labelled = True
        findings.append({
            "type": type_, "id": id_, "name": name_,
            "has_label": labelled,
            "has_aria_label": bool(aria_label),
            "has_aria_labelledby": bool(aria_labelledby),
            "has_title": bool(title_attr),
            "placeholder_only": bool(placeholder and not labelled and not aria_label and not aria_labelledby),
        })
    return findings
```

**2d. ARIA + landmarks (Robust 4.x):**

```python
def aria_audit(html):
    return {
        "roles_used":   sorted(set(re.findall(r'\brole\s*=\s*[\"\']([^\"\']+)[\"\']', html, re.I))),
        "aria_imgs_missing_alt": len(re.findall(r'role\s*=\s*[\"\']img[\"\'][^>]*>(?!.*alt=)', html, re.I)),  # rough
        "duplicate_ids": [k for k,v in __import__("collections").Counter(re.findall(r'\bid\s*=\s*[\"\']([^\"\']+)[\"\']', html)).items() if v > 1],
        "tabindex_positive": len(re.findall(r'\btabindex\s*=\s*[\"\']?[+]?\d+', html)) and len(re.findall(r'\btabindex\s*=\s*[\"\']([+]?\d+)[\"\']', html)) or 0,
        "fake_buttons": len(re.findall(r"<(?:div|span|a)\b[^>]*onclick", html, re.I)),
        "iframe_count": len(re.findall(r"<iframe\b", html, re.I)),
        "iframes_with_title": len(re.findall(r"<iframe\b[^>]*\btitle\s*=", html, re.I)),
    }
```

**2e. Links & buttons (Operable 2.4.x, 2.5.x):**

```python
def actionable_audit(html):
    # Crawl every <a>, <button>, and role=button — they MUST have an accessible name
    actionable = re.findall(r"<a\b[^>]*>.*?</a>|<button\b[^>]*>.*?</button>", html, re.S|re.I)
    findings = []
    for tag in actionable:
        text = re.sub(r"<[^>]+>", "", tag).strip()
        aria_label = re.search(r'\baria-label\s*=\s*[\"\']([^\"\']+)', tag, re.I)
        aria_labelledby = re.search(r'\baria-labelledby\s*=', tag, re.I)
        title_attr = re.search(r'\btitle\s*=\s*[\"\']([^\"\']+)', tag, re.I)
        img_with_alt = re.search(r"<img\b[^>]*\salt\s*=", tag, re.I)
        findings.append({
            "snippet": tag[:140],
            "name_text": text,
            "has_aria_label": bool(aria_label),
            "has_title": bool(title_attr),
            "has_inner_img_alt": bool(img_with_alt),
            "empty_name": (text == "" and not aria_label and not aria_labelledby and not title_attr and not img_with_alt),
        })
    return findings
```

**2f. Heading order (Operable 1.3.1, 2.4.x):**

```python
def heading_order(html):
    headings = re.findall(r"<h([1-6])[^>]*>(.*?)</h\1>", html, re.S|re.I)
    # Returns [(level, text)] in source order so the auditor can flag skipped levels (h1 → h3)
    return [(int(lvl), re.sub(r"<[^>]+>","",t).strip()[:120]) for lvl, t in headings]
```

**2g. Color contrast — only detectable with rendered CSS**

For contrast, you have three options. Pick in order of preference:

1. **Headless Chrome (best)** — already installed? Use it. Render the page, query `getComputedStyle` for each text element and its ancestor background, compute ratio.
   ```bash
   # macOS first-party
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
     --headless=new --disable-gpu --no-sandbox \
     --dump-dom "https://example.com" > /tmp/a11y/dom.html
   ```
2. **`axe-core` via Playwright/Puppeteer if Node is available** — industry standard, ~30 rule packs. Single highest-signal option.
3. **Heuristic fallback** — for inline `style="color:#xxx;background:#yyy"` only, run a regex + WCAG ratio function. Don't pretend this is exhaustive.

```python
def hex_to_rgb(s):
    s = s.strip().lstrip("#")
    if len(s) == 3: s = "".join(c*2 for c in s)
    return tuple(int(s[i:i+2],16) for i in (0,2,4))

def rel_luminance(rgb):
    def chan(c):
        c = c/255
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    r,g,b = (chan(c) for c in rgb)
    return 0.2126*r + 0.7152*g + 0.0722*b

def contrast_ratio(fg, bg):
    l1, l2 = rel_luminance(hex_to_rgb(fg)), rel_luminance(hex_to_rgb(bg))
    hi, lo = max(l1,l2), min(l1,l2)
    return (hi+0.05) / (lo+0.05)

def contrast_verdict(ratio, large_text=False):
    aa = 3.0 if large_text else 4.5
    aaa = 4.5 if large_text else 7.0
    if ratio >= aaa: return "AAA"
    if ratio >= aa:  return "AA"
    return "FAIL"
```

A heuristic scan against inline styles alone catches ~10-15% of real-world contrast violations. Always disclose this caveat in the report.

### Step 3: Score against WCAG criteria

Group findings by criterion and compute per-principle pass-rate:

| Principle | WCAG 2.1 Criteria Covered |
|-----------|---------------------------|
| Perceivable | 1.1.1, 1.3.1, 1.3.3, 1.4.1, 1.4.3, 1.4.4, 1.4.5, 1.4.10, 1.4.11, 1.4.12, 1.4.13 |
| Operable   | 2.1.1, 2.4.1, 2.4.2, 2.4.3, 2.4.4, 2.4.6, 2.4.7, 2.5.3, 2.5.4 |
| Understandable | 3.1.1, 3.2.3, 3.3.1, 3.3.2, 3.3.3 |
| Robust     | 4.1.1, 4.1.2, 4.1.3 |

`pass_rate = 100 * passing_checks / total_checks`. A finding is *passing* if the rule was testable AND the page complied. *Untestable* rules (color contrast without a renderer, focus-observable behavior) are flagged as "NEEDS MANUAL REVIEW" — never "FAIL".

### Step 4: Build the report

Always emit these sections, in this exact order:

```markdown
# Accessibility Audit — <URL>
**Date:** YYYY-MM-DD · **Auditor:** accessibility-auditor · **Standard:** WCAG 2.1 (A / AA / AAA)

## TL;DR
- Final URL: <after redirects>
- HTTP status: <code>
- **Overall AA pass-rate: NN%**
- BLOCKER: N · CRITICAL: N · SERIOUS: N · MODERATE: N · MINOR: N

## Score by Principle
| Principle       | Pass-rate | A | AA | AAA | Top issue |
|-----------------|-----------|---|----|-----|-----------|
| Perceivable     | 87%       | ✅ | ⚠️ | ⚠️  | 1.4.3 contrast on 8 buttons |
| Operable        | 92%       | ✅ | ✅ | ⚠️  | 2.4.7 focus indicator absent |
| Understandable  | 76%       | ✅ | ⚠️ | ⚠️  | 3.3.2 missing form labels |
| Robust          | 100%      | ✅ | ✅ | ✅  | — |

## Top 5 to fix this week
1. [CRITICAL · 1.4.3] Submit button contrast 3.2:1 — bump to #fff on #1a73e8
2. …

## Full Findings

### Perceivable
| Severity | WCAG | Where | Issue | Suggested fix |
|---|---|---|---|---|
| BLOCKER | 1.1.1 | header logo `<img>` | missing alt attribute | `alt="Acme logo"` |
| CRITICAL | 1.4.3 | `.btn-primary` | contrast 3.2:1 (need 4.5:1) | darken to `#1565c0` or add white text weight 600 |
| … | | | | |

### Operable
…

### Understandable
…

### Robust
…

## Needs Manual Review (cannot be detected automatically)
- 2.4.7 Focus visible appearance — confirm visually
- 1.4.2 Audio control — needs user testing
- 2.1.2 No keyboard trap — needs traversal
- 1.3.2 Reading order — verify with screen reader

## Fix-Runbook
- **For devs:** paste the rule-by-rule checklist into your PR template
- **For PMs:** the AA pass-rate is the only number that goes on the dashboard
- **For legal:** this report is the audit artifact for ADA / EAA documentation, but **not** a substitute for a qualified human audit when used as defense
```

### Step 5: Optional cron pairing

The same script can run on a schedule:

```bash
# /etc/cron.d/a11y-weekly — every Monday at 07:00 UTC
0 7 * * 1  curl -sSL "$URL" -o /tmp/a11y.html && \
              hermes run accessibility-auditor --url "$URL" \
              --threshold 95 --alert-channel slack:#a11y
```

The skill supports `--threshold NN` to fail-and-page when AA pass-rate drops below NN%.

---

## Example Invocations

### Example 1 — Pre-launch audit on a landing page

> **User:** I'm about to ship a new landing page at https://acme.com/launch. Run a full WCAG 2.1 AA audit. I want the report pasted in chat plus a markdown file.

**Expected agent flow:**
1. `mkdir -p /tmp/a11y && curl -sSL https://acme.com/launch -o /tmp/a11y/page.html`
2. Run the static scan (Step 2a–f).
3. If headless Chrome is available, run contrast via DOM-computed styles; otherwise fall back to the inline-style heuristic and disclose it.
4. Score per principle (Step 3).
5. Output the full Markdown report inline AND write it to `~/reports/a11y-acme-launch-YYYY-MM-DD.md`.
6. Surface "Top 5" first. Block silently on BLOCKERs — refuse to congratulate an AA pass-rate below 95% without a follow-up note.

### Example 2 — Diff two competitors

> **User:** Compare the accessibility of stripe.com vs squareup.com vs adyen.com — which one is most compliant, and what are they each worst at?

**Expected agent flow:**
1. Audit all three URLs (URL list passed in one prompt is fine).
2. Build a side-by-side comparison table:
   | Company | AA % | A % | AAA % | Worst principle | # BLOCKER |
3. For each company emit the top 3 issues with the criterion + a one-line fix.
4. Recommend a leader. Refuse to crown a winner if all three are below AA — say so honestly.
5. Suggest a quarterly cron to watch their public audits.

### Example 3 — Bug-class investigation across the marketing site

> **User:** 我们公司站点 https://example.cn 有用户反馈说屏幕阅读器读不出表单。帮我看看所有表单是不是真的有 label。

**Expected agent flow:**
1. Scan with CN locale in mind (don't flag `lang="zh-CN"`).
2. Run `form_audit()` specifically and report:
   - fields missing `<label for>` or wrapping `<label>`
   - fields with only placeholder (WCAG 3.3.2 fail)
   - fields rescued by `aria-label` (passes but worth noting)
   - fields that have nothing at all (BLOCKER)
3. Emit a paste-ready dev ticket: severity, criterion, file path if page is local, snippet, exact fix.

---

## Common Pitfalls

| Problem | Why it bites | Solution |
|---|---|---|
| Reporting a 100% pass-rate because no errors appeared | Many WCAG criteria require user behavior (keyboard traversal, screen reader, 200% text resize) and can't be auto-tested | Always emit a "Needs Manual Review" section listing the untestable criteria. Cap auto score at "auto-tested only". |
| Flagging placeholder-as-label as compliant | `placeholder` is a hint, NOT a label — WCAG 3.3.2 explicitly fails this | `placeholder_only` finding → MODERATE severity. The fix is to add a real `<label>`. |
| Ignoring decorative images that SHOULD have `alt=""` (not missing alt) | Many tools naively flag every `alt=""` as missing — but decorative images need an empty alt to **opt out** of being read | Distinct audit: missing alt = BLOCKER; decorative alt present = ✅; suspicious alt (filename, "image1") = MINOR. |
| Auto-audits pretending to be legally sufficient | ADA / EAA enforcement actions weight heavily on user-perceived barriers a script can't see | State the limit in the report footer: "Not a substitute for a qualified manual audit when used as legal defense." |
| Testing only the homepage | Marketing teams put their best a11y work on `/`, but legal complaints land on `/checkout`, `/signup`, `/blog/<post>` | Always ask: "single URL or crawl?" Default to single unless told otherwise — but ask. |
| Color contrast on gradients/images | Foreground over a gradient or photo background is mathematically undefined | Flag these as "contrast untestable — needs designer/contrast checker on representative region". |
| Calling `<div onclick>` "operable" because the click handler exists | Mouse-only handlers bypass keyboard — fails 2.1.1 | `fake_buttons` count from `aria_audit()` → CRITICAL severity. Recommend `<button>` or add `tabindex="0"` + `keydown` handler. |
| Headless Chrome output that differs from real-user rendering | `--dump-dom` skips compositing and font-loading; contrast math drifts | When using headless Chrome, wait for `document.fonts.ready`, set viewport to the user's most-common size (1366×768), and disclose the test viewport in the report. |
| Treating `tabindex > 0` as a minor a11y issue | Positive tabindex **breaks tab order** for keyboard users — it's an Operable 2.4.3 issue | CRITICAL severity, recommend `tabindex="-1"` or removal. |
| Missing `lang` only on `<html>` while reporting "lang present" | Some pages put `lang="en"` in a meta tag — that's not equivalent to `<html lang>` for AT | Two checks: `<html lang>` (REQUIRED) vs `<meta http-equiv="content-language">` (cosmetic). |

---

## Verification Checklist

- [ ] URL fetched with redirect chain captured; final URL is HTTPS
- [ ] HTTP status recorded; if 4xx/5xx, audit short-circuits with `INACCESSIBLE` card
- [ ] `<html lang>` is detected and reported (or flagged missing)
- [ ] All images audited: missing alt (BLOCKER) vs decorative alt (✅) vs informative alt (✅) vs suspicious alt (MINOR)
- [ ] All actionable elements (a/button/role=button) checked for accessible name
- [ ] All form fields (excluding hidden/submit) checked for `<label>` / `aria-label` / `aria-labelledby`
- [ ] Heading sequence reviewed for skipped levels (h1 → h3 = MODERATE)
- [ ] Duplicate `id` audit (Robust 4.1.1)
- [ ] ARIA roles used only on appropriate elements (no `<button role="link">` mismatch)
- [ ] Page `<title>` present, unique, ≤ 60 chars
- [ ] Skip-to-content link presence noted
- [ ] Main landmark present
- [ ] Iframes have `title` attribute
- [ ] Color contrast computed — disclose whether headless-Chrome or heuristic
- [ ] Final report includes 5 sections: TL;DR · Score by Principle · Top 5 · Full Findings · Needs Manual Review
- [ ] Per-criterion attribution (which WCAG SC) is on every row of the findings table
- [ ] Every fix snippet is copy-pasteable
- [ ] "Needs Manual Review" section honestly enumerates the criteria the script cannot test
- [ ] Report footer states: "Automated scan. Not a substitute for a qualified human audit when used in legal context."

---

## Data Sources & Accuracy

| Source | What it gives you | Caveats |
|--------|-------------------|---------|
| **Page HTML via `curl`** | Static signal extraction for ~80% of WCAG criteria | Inlined HTML ≠ rendered DOM. Pages that render critical UI in JS will be misread. |
| **Headless Chrome / Chromium** | Rendered DOM, computed styles, contrast math on real layouts | Requires Chrome installed. Output DOM may skip <head> rounding errors. Always wait for `document.fonts.ready`. |
| **`axe-core` via Playwright** | Industry-standard WCAG rule pack, ~70 rules with extremely low false-positive rate | Requires Node + browser. Adds dependency surface. Recommended when axe is already in the project's CI. |
| **W3C WCAG 2.1 quick reference** | Authoritative criterion text and understanding docs | Source of truth for criterion numbers, not for "is my site failing?" |
| **WebAIM Million** | Yearly empirical data on the most-common error types — useful for explaining why each criterion matters | Lagging by ~12 months; cite the latest year. |

**Honest disclosure you must include in every report:**

> *This is an automated scan against a subset of WCAG 2.1 success criteria that can be tested without a human or assistive-technology in the loop. Approximately 30-40% of WCAG criteria require human judgment (screen-reader behavior, focus traversal, reading order of complex layouts, audio-described video, color-on-image contrast) and are listed under "Needs Manual Review". A passing score on this report is **not** equivalent to a formal audit under WCAG 2.1, ADA Title III, EAA Directive 2019/882, or Section 508 — those require a qualified human review.*

**Failure to disclose the scope limit on an audit report is itself an ethical violation — flag it.**
