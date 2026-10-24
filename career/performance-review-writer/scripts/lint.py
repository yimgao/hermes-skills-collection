#!/usr/bin/env python3
"""lint.py — enforce the rules that make a self-review survive calibration.

Checks a markdown self-review draft for the failure modes that get people
downgraded: weak verbs, unquantified bullets, "we" credit-taking, fake
growth areas, bloat, duplicates, and accidental secret leakage.

Usage:
  python3 lint.py draft.md
  python3 lint.py draft.md --json
  python3 lint.py draft.md --required "Accomplishments,Growth,Goals" --max-words 60

Exit code: 0 = no ERROR, 1 = at least one ERROR (safe for CI / pre-submit hook).
"""
import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

STRONG_VERBS = {
    # English
    "led", "lead", "designed", "built", "shipped", "launched", "cut", "reduced", "increased",
    "grew", "migrated", "rearchitected", "rewrote", "automated", "eliminated", "recovered",
    "negotiated", "drove", "owned", "created", "delivered", "scaled", "unblocked", "mentored",
    "coached", "established", "defined", "drove", "consolidated", "instrumented", "resolved",
    "diagnosed", "prioritized", "partnered", "aligned", "standardized", "rolled", "onboarded",
    "hired", "founded", "reversed", "doubled", "tripled", "saved", "secured", "closed",
    "stabilized", "refactored", "optimized", "accelerated", "simplified", "decommissioned",
    # 中文
    "主导", "设计", "落地", "推动", "搭建", "重构", "优化", "砍掉", "降低", "提升", "拉齐",
    "解决", "搭建", "梳理", "沉淀", "引入", "替换", "合并", "拆分", "迁移", "上线", "交付",
    "带", "培养", "制定", "建立", "打通", "缩短", "减少", "翻倍", "修复", "治理", "规范",
}

WEAK_OPENERS = [
    "helped", "help with", "worked on", "was involved", "participated", "assisted",
    "supported", "contributed to", "responsible for", "tasked with", "in charge of",
    "was part of", "was responsible", "was tasked", "was in charge", "did some",
    "various", "misc",
    "参与", "协助", "配合", "帮助", "负责了", "负责", "做了一些", "跟进", "支持", "投入",
]

VAGUE_PHRASES = [
    "various improvements", "several things", "a lot of work", "many tasks",
    "improved performance", "better quality", "more efficient", "enhanced the system",
    "worked closely with", "successfully", "significantly", "significantly improved",
    "大幅", "一定程度", "有所提升", "较好地", "积极参与", "认真完成", "努力",
]

FAKE_WEAKNESSES = [
    "perfectionist", "too much of a perfectionist", "work too hard", "care too much",
    "too detail-oriented", "too passionate", "impatient with slow processes",
    "追求完美", "太追求完美", "工作太拼", "过于认真", "对自己要求太高", "太较真",
]

LEAK_PATTERNS = [
    (re.compile(r"\b(sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,})\b"), "looks like an API key"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b"), "personal email address"),
    (re.compile(r"\b(?:\d[ -]?){13,16}\b"), "possible card/account number"),
]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(.*)$")
DIGIT_RE = re.compile(r"\d")
TIMELINE_RE = re.compile(
    r"(Q[1-4]|H[12]|20\d\d|next \d+ (?:days|weeks|months)|by (?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
    r"|\d+\s*(?:days?|weeks?|months?)|下季度|下个季度|明年|上半年|下半年|\d+\s*(?:天|周|个月))", re.I)


# ---------------------------------------------------------------- parsing
def parse(md_text):
    """Return (sections, bullets). Sections keyed by heading text."""
    sections = []
    bullets = []  # (section, text, line_no)
    cur = "_intro"
    sections.append(cur)
    for i, line in enumerate(md_text.splitlines(), 1):
        h = HEADING_RE.match(line)
        if h:
            cur = h.group(2).strip()
            sections.append(cur)
            continue
        b = BULLET_RE.match(line)
        if b and b.group(1).strip():
            bullets.append((cur, b.group(1).strip(), i))
    return sections, bullets


def words(text):
    """CJK-aware word count: CJK chars count as 1 word each."""
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z][A-Za-z'\-]*", text))
    return cjk + latin


def first_token(text):
    t = re.sub(r"^[*_`\s]+", "", text)
    m = re.match(r"([A-Za-z']+|[\u4e00-\u9fff]{1,3})", t)
    return (m.group(1) if m else "").lower()


def has_strong_verb(text):
    t = text.lower()
    if any(v in t for v in STRONG_VERBS):
        return True
    return False


def pronoun_profile(md_text):
    i_hits = len(re.findall(r"\b(I|I've|I'd|my|me)\b", md_text))
    we_hits = len(re.findall(r"\b(we|we've|our|us)\b", md_text))
    zh_i = md_text.count("我") - md_text.count("我们")
    zh_we = md_text.count("我们") + md_text.count("咱们")
    return i_hits + max(zh_i, 0), we_hits + zh_we


def find_section(sections, keywords):
    for s in sections:
        low = s.lower()
        if any(k.lower() in low for k in keywords):
            return s
    return None


# ---------------------------------------------------------------- checks
def check(md_text, bullets, sections, args):
    issues = []  # dict(level, code, where, msg, fix)

    def add(level, code, where, msg, fix):
        issues.append({"level": level, "code": code, "where": where, "msg": msg, "fix": fix})

    # 1. required sections
    for req in [r.strip() for r in (args.required or "").split(",") if r.strip()]:
        if not find_section(sections, [req]):
            add("ERROR", "MISSING_SECTION", "document",
                f"required section '{req}' not found",
                f"add a heading containing '{req}'")

    # 2. per-bullet checks on accomplishment-like bullets
    NON_RESULT = ("growth", "development", "improve", "goal", "next", "plan",
                  "成长", "不足", "改进", "目标", "计划")
    for sec, text, ln in bullets:
        low = text.lower()
        tok = first_token(text)
        is_result = not any(k in sec.lower() for k in NON_RESULT)
        # weak opener — must be at the START, not somewhere mid-sentence
        flat = re.sub(r"^[\s*_`>#\-]+", "", text).lower()
        if flat.startswith("i "):
            flat = flat[2:]
        weak_hit = next((w for w in WEAK_OPENERS if flat.startswith(w)), None)
        if weak_hit:
            add("ERROR", "WEAK_VERB", f"L{ln}",
                f"opens with a passive/weak phrase ('{weak_hit}')",
                "lead with what YOU did: led / built / cut / 主导 / 落地 / 砍掉")
        # no number (results only — goals are forward-looking by nature)
        if is_result and not DIGIT_RE.search(text):
            add("WARN", "NO_NUMBER", f"L{ln}",
                "no number anywhere in the bullet",
                "add magnitude (-42%), volume (3.2×), or radius (6 people / 3 teams)")
        # vague phrase
        for v in VAGUE_PHRASES:
            if v in low:
                add("WARN", "VAGUE", f"L{ln}", f"vague filler: '{v}'",
                    "replace with the actual change measured, or delete")
                break
        # length
        w = words(text)
        if w > args.max_words:
            add("WARN", "TOO_LONG", f"L{ln}", f"{w} words (limit {args.max_words})",
                "split into problem / action / result, or cut the middle")
        # strong verb coverage (results only)
        if is_result and not has_strong_verb(text) and not any(
                x in low for x in ("evidence", "证据", "链接")):
            add("WARN", "NO_STRONG_VERB", f"L{ln}",
                "no strong action verb found",
                "state the action: designed / shipped / migrated / 重构 / 推动")

    # 3. we/I balance
    i_n, we_n = pronoun_profile(md_text)
    if we_n > i_n and we_n >= 3:
        add("ERROR", "WE_OVERLOAD", "document",
            f"'we/我们' {we_n}× vs 'I/我' {i_n}× — the reviewer cannot score a team",
            "rewrite collaborative wins as 'I led X; worked with Y on Z'")

    # 4. fake weaknesses (longest match only, once per phrase)
    lowdoc = md_text.lower()
    fw_hits = sorted({fw for fw in FAKE_WEAKNESSES if fw.lower() in lowdoc},
                     key=len, reverse=True)
    kept = []
    for fw in fw_hits:
        if any(fw.lower() in k.lower() for k in kept):
            continue  # "perfectionist" is covered by "too much of a perfectionist"
        kept.append(fw)
        add("ERROR", "FAKE_WEAKNESS", "document",
            f"humble-brag weakness detected: '{fw}'",
            "name a real gap + the action you took + when it will show")

    # 5. growth section quality
    gsec = find_section(sections, ["growth", "development", "improve", "成长", "不足", "改进"])
    if gsec:
        g_bullets = [b for b in bullets if b[0] == gsec]
        if not g_bullets:
            add("ERROR", "EMPTY_GROWTH", gsec, "growth section has no bullets",
                "1–2 real gaps, each with a concrete countermeasure")
        for _, text, ln in g_bullets:
            if not TIMELINE_RE.search(text):
                add("WARN", "GROWTH_NO_TIMELINE", f"L{ln}",
                    "growth item has no timeframe",
                    "add 'by Q1' / 'next 90 days' so it reads as a plan, not a confession")

    # 6. duplicates
    seen = []
    for sec, text, ln in bullets:
        norm = re.sub(r"[^a-z0-9\u4e00-\u9fff ]", "", text.lower())
        for prev_text, prev_ln in seen:
            ratio = SequenceMatcher(None, norm, prev_text).ratio()
            if ratio > 0.82:
                add("WARN", "DUPLICATE", f"L{ln}",
                    f"~{int(ratio*100)}% similar to L{prev_ln}",
                    "merge them, or keep only the stronger one")
                break
        seen.append((norm, ln))

    # 7. leakage
    for pat, label in LEAK_PATTERNS:
        for m in pat.finditer(md_text):
            add("ERROR", "LEAK", "document", f"{label}: {m.group(0)[:12]}…",
                "remove before pasting into any HR tool")

    # 8. numbering sanity
    if args.expect_min and len(bullets) < args.expect_min:
        add("WARN", "THIN", "document",
            f"only {len(bullets)} bullets (expected ≥{args.expect_min})",
            "3–5 accomplishments minimum; fewer reads as a light half")

    # 9. summary first-paragraph
    paras = [p.strip() for p in re.split(r"\n\s*\n", md_text) if p.strip()]
    first = next((p for p in paras if not p.startswith("#")), "")
    if first and not DIGIT_RE.search(first):
        add("WARN", "SUMMARY_NO_NUMBER", "document",
            "opening paragraph has no number",
            "reviewers read ~3 minutes; front-load the single best metric")

    return issues


# ---------------------------------------------------------------- report
def report(issues, path, bullets, md_text):
    errors = [i for i in issues if i["level"] == "ERROR"]
    warns = [i for i in issues if i["level"] == "WARN"]
    i_n, we_n = pronoun_profile(md_text)
    print(f"# Self-review lint — {path}")
    print(f"\n{len(bullets)} bullets · I/我={i_n} · we/我们={we_n} · "
          f"{len(errors)} ERROR · {len(warns)} WARN\n")
    if errors:
        print("## ERROR — do not submit until fixed")
        print("| Where | Code | Problem | Fix |")
        print("|---|---|---|---|")
        for i in errors:
            print(f"| {i['where']} | `{i['code']}` | {i['msg']} | {i['fix']} |")
        print()
    if warns:
        print("## WARN — read each one, fix or consciously accept")
        print("| Where | Code | Problem | Fix |")
        print("|---|---|---|---|")
        for i in warns:
            print(f"| {i['where']} | `{i['code']}` | {i['msg']} | {i['fix']} |")
        print()
    if not issues:
        print("✅ Clean. Every bullet has a number, a strong verb, and no we-overload.")
        print("   Last check before submitting: can a stranger read your summary and")
        print("   say what you did and how big it was? If not, it's still a draft.")
    else:
        print(f"**Verdict: {'NOT READY' if errors else 'SHIPPABLE'}** "
              f"— {len(errors)} blocking, {len(warns)} advisory.")
    return 0 if not errors else 1


def main():
    ap = argparse.ArgumentParser(description="Lint a self-review / brag doc draft")
    ap.add_argument("path")
    ap.add_argument("--required", default="",
                    help="comma-separated required section keywords")
    ap.add_argument("--max-words", type=int, default=60, help="per-bullet word budget")
    ap.add_argument("--expect-min", type=int, default=0, help="minimum bullet count")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    p = Path(args.path).expanduser()
    if not p.exists():
        sys.exit(f"[FATAL] no such file: {p}")
    md = p.read_text(errors="ignore")
    sections, bullets = parse(md)
    issues = check(md, bullets, sections, args)

    if args.json:
        print(json.dumps({"path": str(p), "bullets": len(bullets), "issues": issues},
                         ensure_ascii=False, indent=2))
        sys.exit(0 if not any(i["level"] == "ERROR" for i in issues) else 1)
    sys.exit(report(issues, p.name, bullets, md))


if __name__ == "__main__":
    main()


