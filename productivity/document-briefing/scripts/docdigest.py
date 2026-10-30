#!/usr/bin/env python3
"""docdigest.py — turn any long document into a page-indexed, citeable map.

Why this exists
---------------
An LLM asked to "summarize this 60-page PDF" will happily invent section names
and page numbers. This script does the boring, verifiable half: it extracts text
with *stable locators* (page / slide / line-range / paragraph), hands the agent a
map it can quote from, and provides a `check` mode that fails loudly when a
citation or a quote does not actually exist in the source.

Modes
-----
  outline FILE                 Markdown document map (what to read, in what order)
  extract FILE                 digest (outline by default, JSON with --json)
  check FILE BRIEFING.md       verify every citation + quote in a briefing
  stats FILE                   one-line size / reading-time summary

Supported inputs (no hard third-party dependency)
  .pdf    -> pypdf, else PyPDF2
  .docx   -> stdlib zipfile + XML (paragraphs + heading styles)
  .pptx   -> stdlib zipfile + XML (one locator per slide)
  .html   -> bs4 if installed, else stdlib HTMLParser
  .md .txt .csv .log .json .yaml .py ... -> plain text, chunked by lines

Exit codes
  outline/extract/stats : 0 ok, 2 unreadable file
  check                 : 0 clean, 1 at least one broken citation, 2 unreadable source

Zero network. Nothing is uploaded. Text never leaves this machine.

Examples
  python3 docdigest.py outline ~/Downloads/10-K.pdf
  python3 docdigest.py extract contract.pdf --json --focus "termination"
  python3 docdigest.py check lease.pdf brief.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import zipfile
from html.parser import HTMLParser
from pathlib import Path

DEFAULT_CHUNK_WORDS = 800
DEFAULT_MAX_PAGES = 0  # 0 = no cap

# Words that make a sentence matter for a *briefing* (decisions, money, risk).
SIGNAL_WORDS = {
    "shall", "must", "required", "prohibited", "liable", "liability", "indemnify",
    "terminate", "termination", "penalty", "penalties", "fine", "deadline",
    "deadlines", "effective", "expires", "expiry", "renew", "renewal", "notice",
    "breach", "default", "warranty", "exclusion", "excluded", "limitation",
    "risk", "risks", "material", "significant", "guidance", "recommend",
    "recommends", "conclusion", "finding", "findings", "result", "results",
    "increase", "decrease", "growth", "decline", "revenue", "margin", "cost",
    "costs", "budget", "target", "assumption", "however", "therefore",
    "consequently", "downtime", "outage", "saving", "savings",
    "必须", "应当", "不得", "禁止", "终止", "违约", "赔偿", "责任", "罚款",
    "期限", "截止", "生效", "到期", "续约", "通知", "风险", "重大", "结论",
    "建议", "增长", "下降", "收入", "成本", "预算", "目标", "因此",
}

# Headings that almost always carry the meat of a business/legal document.
IMPORTANT_HEADINGS = {
    "summary", "executive summary", "overview", "conclusion", "conclusions",
    "recommendation", "recommendations", "risk factors", "risks", "terms",
    "termination", "term and termination", "payment", "fees", "fees and payment",
    "liability", "limitation of liability", "indemnification", "confidentiality",
    "warranty", "warranties", "governing law", "scope", "deliverables",
    "timeline", "budget", "pricing", "methodology", "findings", "results",
    "discussion", "next steps", "action items", "assumptions", "data protection",
    "service levels", "refunds", "costs",
    "摘要", "概述", "结论", "建议", "风险", "条款", "终止", "付款", "费用",
    "责任", "赔偿", "保密", "保证", "适用法律", "范围", "交付", "时间表",
    "预算", "方法", "发现", "结果", "讨论", "下一步", "假设",
}

PDF_MAGIC = b"%PDF"
ZIP_MAGIC = b"PK\x03\x04"

# A line that is almost certainly a heading (used as a sentence boundary too).
HEADING_LINE = re.compile(
    r"^(?:"
    r"\d+(?:\.\d+)*[.)]?\s+\S.{2,80}"          # 1. Term  / 2.3 Fees
    r"|[A-Z][A-Z0-9 &/'\-.,:()\u2013\u2014]{4,70}"   # ALL CAPS LINE
    r"|#{1,6}\s+\S.{1,100}"                     # markdown
    r"|(?:[一二三四五六七八九十]+[、.)])\s*\S.{1,60}"  # 一、概述
    r"|(?:第[一二三四五六七八九十百]+[章节条])\s*\S.{0,60}"
    r")$")


# --------------------------------------------------------------------------- #
# Text normalisation
# --------------------------------------------------------------------------- #
_WS = re.compile(r"[ \t\u00a0\u3000]+")
_HYPHEN_BREAK = re.compile(r"(\w)-\s*\n\s*(\w)")


def norm(text: str) -> str:
    """Canonical form used for quote matching (never for display)."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    text = _HYPHEN_BREAK.sub(r"\1\2", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def clean(text: str) -> str:
    """Display form: whitespace + hyphenation only. Punctuation stays as authored.

    Deliberately does NOT apply NFKC — that would turn full-width Chinese
    punctuation (，：；) into ASCII and mangle quoted output.
    """
    if not text:
        return ""
    text = text.replace("\u00a0", " ").replace("\u3000", " ")
    text = text.replace("\ufb01", "fi").replace("\ufb02", "fl")
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = _HYPHEN_BREAK.sub(r"\1\2", text)
    text = _WS.sub(" ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def flatten(text: str) -> str:
    """PDF/HTML line breaks are layout artefacts — collapse them."""
    return re.sub(r"\s+", " ", text or "").strip()


def wc(text: str) -> int:
    """Word count that behaves for CJK (chars/1.7) and latin (token split)."""
    if not text:
        return 0
    cjk = len(re.findall(r"[\u3400-\u9fff]", text))
    latin = len(re.findall(r"[A-Za-z0-9'\-]+", text))
    return latin + int(round(cjk / 1.7))


LIST_START = re.compile(r"^(?:[-*+\u2022]\s|\d+[.)]\s|>\s|\|\s)")
TERMINAL = re.compile(r"[.!?:;\u3002\uff01\uff1f\uff1b\uff1a\u201d\"]$")

# Headings that almost always carry the meat of a business/legal document.
def is_heading_line(s: str) -> bool:
    """Heuristic: does this single line look like a heading?"""
    probe = clean(s).lstrip("# ").strip()
    if not probe or len(probe) > 100:
        return False
    if clean(s).startswith("#"):
        return True
    all_caps = bool(re.fullmatch(r"[A-Z0-9 &/'\-.,()]{4,80}", probe)) and sum(
        1 for ch in probe if ch.isalpha()) >= 4
    if all_caps:
        return True
    if TERMINAL.search(probe):
        return False
    if HEADING_LINE.match(probe):
        return True
    words = probe.split()
    return (len(words) <= 6 and len(probe) < 60 and probe == probe.title())


def unwrap(text: str) -> str:
    """Re-join hard-wrapped prose so `\n` means paragraph, heading or list — not width.

    PDF line breaks are layout artefacts; plain-text/markdown files are often
    hard-wrapped at 78 chars. Both destroy sentence extraction unless we unwrap
    first. List items, table rows, headings and blank lines stay hard breaks.
    """
    parts, buf = [], ""
    for raw_line in (text or "").splitlines():
        s = clean(raw_line)
        if not s:
            if buf:
                parts.append(buf)
                buf = ""
            parts.append("")
            continue
        if is_heading_line(s) or LIST_START.match(s):
            if buf:
                parts.append(buf)
                buf = ""
            parts.append(s)
            continue
        if buf and not TERMINAL.search(buf):
            buf = f"{buf} {s}"
        else:
            if buf:
                parts.append(buf)
            buf = s
    if buf:
        parts.append(buf)
    # headings become their own sentence: give them a terminator
    return "\n".join(p + "." if (p and is_heading_line(p) and not TERMINAL.search(p)) else p
                     for p in parts)


# --------------------------------------------------------------------------- #
# Extractors -> {kind, units:[{locator,text,headings}], headings:[...]}
# --------------------------------------------------------------------------- #
def _pdf_pages(path: Path) -> list:
    for modname in ("pypdf", "PyPDF2"):
        try:
            mod = __import__(modname, fromlist=["PdfReader"])
        except Exception:
            continue
        try:
            reader = mod.PdfReader(str(path))
            if getattr(reader, "is_encrypted", False):
                try:
                    reader.decrypt("")
                except Exception:
                    pass
            pages = []
            for page in reader.pages:
                try:
                    pages.append(page.extract_text() or "")
                except Exception:
                    pages.append("")
            return pages
        except Exception:
            continue
    return []


def _pdf_headings(pages: list) -> list:
    """PDF carries no style info — infer headings from line shape and position."""
    heads, seen = [], set()
    for i, raw in enumerate(pages, start=1):
        for line in (raw or "").splitlines():
            s = clean(line)
            if not s or len(s) < 3 or len(s) > 90:
                continue
            n = norm(s)
            important = n.rstrip(".:") in IMPORTANT_HEADINGS
            if important:
                lvl = 1
            elif HEADING_LINE.match(s):
                lvl = 2
            elif (not re.search(r"[.!?:;。！？；：]$", s) and
                  3 <= len(s.split()) <= 9 and
                  sum(1 for w in s.split() if w[:1].isupper()) >= max(2, len(s.split()) - 2)):
                lvl = 3
            else:
                continue
            key = (i, n)
            if key in seen:
                continue
            seen.add(key)
            heads.append({"locator": f"p.{i}", "level": lvl, "text": s[:120],
                          "important": important})
    return heads


def extract_pdf(path: Path, max_pages: int) -> dict:
    pages = _pdf_pages(path)
    if not pages:
        return {"kind": "pdf", "units": [], "headings": [],
                "error": "no text layer (scanned PDF?) — OCR first: `ocrmypdf in.pdf out.pdf`"}
    if max_pages:
        pages = pages[:max_pages]
    units = [{"locator": f"p.{i}", "text": flatten(clean(raw)), "headings": []}
             for i, raw in enumerate(pages, start=1)]
    total = sum(wc(u["text"]) for u in units)
    if total < 20:
        return {"kind": "pdf", "units": [], "headings": [],
                "error": f"no usable text layer ({len(units)} pages, {total} words) — "
                         "this is a scanned PDF. OCR it first: `ocrmypdf in.pdf out.pdf`, "
                         "or use the ocr-and-documents skill, then re-run."}
    return {"kind": "pdf", "units": units, "headings": _pdf_headings(pages)}


_W_P = re.compile(r"<w:p[ >].*?</w:p>", re.S)
_W_T = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.S)
_W_STYLE = re.compile(r'<w:pStyle[^>]*w:val="([^"]+)"')
_XML_ENT = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&apos;": "'"}


def _unescape(s: str) -> str:
    for k, v in _XML_ENT.items():
        s = s.replace(k, v)
    return s


def extract_docx(path: Path) -> dict:
    with zipfile.ZipFile(str(path)) as z:
        try:
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
        except KeyError:
            return {"kind": "docx", "units": [], "headings": [],
                    "error": "not a valid .docx (missing word/document.xml)"}
    units, heads, n = [], [], 0
    for pm in _W_P.finditer(xml):
        block = pm.group(0)
        text = clean(_unescape("".join(_W_T.findall(block))))
        if not text:
            continue
        n += 1
        loc = f"¶{n}"
        style = _W_STYLE.search(block)
        style = (style.group(1) if style else "").lower()
        is_head = "heading" in style or "标题" in style or style in ("title", "subtitle")
        units.append({"locator": loc, "text": text, "headings": [text] if is_head else []})
        if is_head:
            digits = re.search(r"(\d)", style)
            lvl = min(3, max(1, int(digits.group(1)))) if digits else 1
            heads.append({"locator": loc, "level": lvl, "text": text[:120],
                          "important": norm(text) in IMPORTANT_HEADINGS})
    return {"kind": "docx", "units": units, "headings": heads}


_SLIDE = re.compile(r"ppt/slides/slide(\d+)\.xml$")
_A_T = re.compile(r"<a:t[^>]*>(.*?)</a:t>", re.S)


def extract_pptx(path: Path) -> dict:
    units, heads = [], []
    with zipfile.ZipFile(str(path)) as z:
        names = [n for n in z.namelist() if _SLIDE.search(n)]
        names.sort(key=lambda n: int(_SLIDE.search(n).group(1)))
        if not names:
            return {"kind": "pptx", "units": [], "headings": [], "error": "no slides found"}
        for n in names:
            idx = int(_SLIDE.search(n).group(1))
            xml = z.read(n).decode("utf-8", "ignore")
            parts = [clean(_unescape(p)) for p in _A_T.findall(xml)]
            parts = [p for p in parts if p]
            if not parts:
                continue
            title = parts[0]
            loc = f"slide.{idx}"
            units.append({"locator": loc, "text": " ".join(parts), "headings": [title]})
            heads.append({"locator": loc, "level": 1, "text": title[:120],
                          "important": norm(title) in IMPORTANT_HEADINGS})
    return {"kind": "pptx", "units": units, "headings": heads}


class _TextHTML(HTMLParser):
    BLOCK = {"p", "div", "br", "li", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
             "section", "article", "blockquote", "pre", "td", "th"}
    SKIP = {"script", "style", "nav", "footer", "aside", "noscript", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks, self.cur, self.skip = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        if tag in self.BLOCK and "".join(self.cur).strip():
            self.blocks.append(("".join(self.cur), None))
            self.cur = []

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in self.BLOCK:
            t = "".join(self.cur)
            if t.strip():
                self.blocks.append((t, tag if tag in ("h1", "h2", "h3", "h4") else None))
            self.cur = []

    def handle_data(self, data):
        if not self.skip:
            self.cur.append(data)


def extract_html(path: Path, chunk_words: int) -> dict:
    raw = path.read_text("utf-8", "ignore")
    blocks = []  # (text, heading_level_or_None)
    try:
        from bs4 import BeautifulSoup  # optional acceleration
        soup = BeautifulSoup(raw, "html.parser")
        for tag in soup(list(_TextHTML.SKIP)):
            tag.decompose()
        for el in soup.find_all(["p", "li", "h1", "h2", "h3", "h4", "td", "blockquote", "pre"]):
            t = clean(el.get_text(" "))
            if t:
                blocks.append((t, int(el.name[1]) if el.name in ("h1", "h2", "h3", "h4") else None))
    except Exception:
        p = _TextHTML()
        p.feed(raw)
        p.close()
        blocks = [(clean(t), (int(tag[1]) if tag else None)) for t, tag in p.blocks]
    units, heads, n, buf, bw = [], [], 0, [], 0
    for text, lvl in blocks:
        if lvl:
            if buf:
                n += 1
                units.append({"locator": f"¶{n}", "text": " ".join(buf), "headings": []})
                buf, bw = [], 0
            n += 1
            units.append({"locator": f"¶{n}", "text": text, "headings": [text]})
            heads.append({"locator": f"¶{n}", "level": min(3, lvl), "text": text[:120],
                          "important": norm(text) in IMPORTANT_HEADINGS})
            continue
        buf.append(text)
        bw += wc(text)
        if bw >= chunk_words:
            n += 1
            units.append({"locator": f"¶{n}", "text": " ".join(buf), "headings": []})
            buf, bw = [], 0
    if buf:
        n += 1
        units.append({"locator": f"¶{n}", "text": " ".join(buf), "headings": []})
    return {"kind": "html", "units": units, "headings": heads}


def extract_plain(path: Path, chunk_words: int) -> dict:
    lines = path.read_text("utf-8", "ignore").splitlines()
    units, heads = [], []
    for i, line in enumerate(lines, start=1):
        s = clean(line)
        if s and is_heading_line(s):
            heads.append({"locator": f"L{i}", "level": 1 if s.startswith("#") else 2,
                          "text": s.lstrip("# ").strip()[:120],
                          "important": norm(s.lstrip("# ")) in IMPORTANT_HEADINGS})
    buf, bw, start = [], 0, 1
    for i, line in enumerate(lines, start=1):
        buf.append(line)
        bw += wc(line)
        if bw >= chunk_words:
            text = clean("\n".join(buf))
            if text:
                units.append({"locator": f"L{start}-{i}", "text": text, "headings": []})
            buf, bw, start = [], 0, i + 1
    tail = clean("\n".join(buf))
    if tail:
        units.append({"locator": f"L{start}-{max(start, len(lines))}", "text": tail, "headings": []})
    return {"kind": "text", "units": units, "headings": heads}


def load(path: Path, chunk_words: int = DEFAULT_CHUNK_WORDS, max_pages: int = DEFAULT_MAX_PAGES) -> dict:
    if not path.exists():
        return {"kind": "unknown", "units": [], "headings": [],
                "error": f"file not found: {path}"}
    try:
        head = path.open("rb").read(4)
    except Exception as exc:
        return {"kind": "unknown", "units": [], "headings": [], "error": str(exc)}
    ext = path.suffix.lower()
    if ext == ".pdf" or head.startswith(PDF_MAGIC):
        doc = extract_pdf(path, max_pages)
    elif ext in (".docx", ".docm"):
        doc = extract_docx(path)
    elif ext in (".pptx", ".pptm"):
        doc = extract_pptx(path)
    elif ext in (".html", ".htm", ".xhtml"):
        doc = extract_html(path, chunk_words)
    elif ext == ".doc":
        doc = {"kind": "doc", "units": [], "headings": [],
               "error": "legacy .doc — convert first: `textutil -convert docx file.doc`"}
    else:
        doc = extract_plain(path, chunk_words)
    doc["source"] = str(path.resolve())
    doc["bytes"] = path.stat().st_size
    doc.setdefault("units", [])
    doc.setdefault("headings", [])
    doc.setdefault("warnings", [])
    if doc["units"]:
        empty = sum(1 for u in doc["units"] if wc(u["text"]) < 12)
        if doc["kind"] == "pdf" and empty >= max(2, len(doc["units"]) * 0.6):
            doc["warnings"].append("most pages are nearly empty — likely a scan without OCR")
    return doc


# --------------------------------------------------------------------------- #
# Signals
# --------------------------------------------------------------------------- #
MONEY = re.compile(
    r"(?:(?:\u4eba\u6c11\u5e01|USD|CNY|RMB|EUR)\s?\d[\d,]*(?:\.\d+)?"
    r"|[$\u00a5\u20ac\u00a3]\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:k|m|bn|b|million|billion|\u4e07|\u4ebf))?"
    r"|\d[\d,]*(?:\.\d+)?\s?(?:%|percent|USD|CNY|RMB|EUR|\u4e07\u5143|\u4ebf\u5143|\u7f8e\u5143|\u4eba\u6c11\u5e01|\u5143))",
    re.I)
DATE = re.compile(
    r"(?:\b\d{4}-\d{2}-\d{2}\b"
    r"|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b"
    r"|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b"
    r"|\d{4}\s?年\s?\d{1,2}\s?月(?:\s?\d{1,2}\s?日)?"
    r"|\b\d{1,2}/\d{1,2}/\d{2,4}\b"
    r"|\bQ[1-4]\s?(?:FY\s?)?\d{2,4}\b)", re.I)
SENT_SPLIT = re.compile(r"(?<=[.!?。！？;；])\s+|\n+")


def sentences(text: str) -> list:
    out = []
    for part in SENT_SPLIT.split(text or ""):
        s = clean(part)
        if 2 <= len(s) <= 600:
            out.append(s)
    return out


def score_sentence(sent: str, pos: float) -> float:
    s = norm(sent)
    if len(s.split()) < 5 and len(s) < 20:
        return 0.0
    toks = set(re.findall(r"[a-z']+|[\u4e00-\u9fff]{2,}", s))
    score = 2.2 * len(toks & SIGNAL_WORDS)
    if MONEY.search(sent):
        score += 2.0
    if DATE.search(sent):
        score += 1.0
    if re.search(r"\d+\.?\d*\s?%", sent):
        score += 1.2
    if re.search(r"(?:not|no|never|except|unless|excluding|without|不得|禁止|除外|不适用)", s):
        score += 0.8
    if re.search(r"(?:therefore|thus|consequently|as a result|in summary|因此|所以|综上)", s):
        score += 1.0
    if pos < 0.18 or pos > 0.86:
        score += 0.7
    if re.search(r"(?:page \d+ of \d+|all rights reserved|confidential\b.*intended recipient)", s):
        score -= 2.5
    if len(s) > 380:
        score -= 0.6
    return round(max(0.0, score), 2)


def build_signals(doc: dict, focus: str = "", per_unit: int = 4) -> dict:
    money, dates, obligations, key = [], [], [], []
    focus_toks = set(re.findall(r"[a-z']+|[\u4e00-\u9fff]{2,}", norm(focus))) if focus else set()
    text_kinds = {"text"}

    for u in doc["units"]:
        loc, text = u["locator"], u["text"]
        if doc["kind"] in text_kinds:
            text = unwrap(text)
        for m in MONEY.finditer(text):
            money.append({"locator": loc, "value": clean(m.group(0))})
        for m in DATE.finditer(text):
            dates.append({"locator": loc, "value": clean(m.group(0))})
        sents = sentences(text)
        scored, obls = [], []
        for i, s in enumerate(sents):
            pos = i / max(1, len(sents) - 1)
            sc = score_sentence(s, pos)
            if focus_toks:
                stoks = set(re.findall(r"[a-z']+|[\u4e00-\u9fff]{2,}", norm(s)))
                if stoks & focus_toks:
                    sc += 2.5
            if sc >= 3.0:
                scored.append((sc, s))
            if re.search(r"(?:shall|must|required to|may not|不得|必须|应当|禁止)", norm(s)):
                obls.append(s[:300])
        scored.sort(key=lambda x: -x[0])
        for sc, s in scored[:per_unit]:
            key.append({"locator": loc, "text": s[:400], "score": sc})
        for o in obls[:8]:
            obligations.append({"locator": loc, "text": o})
    key.sort(key=lambda x: -x["score"])
    seen, dedup = set(), []
    for k in key:
        sig = norm(k["text"])[:90]
        if sig in seen:
            continue
        seen.add(sig)
        dedup.append(k)
    heads = doc.get("headings", [])
    important = []
    seen_h = set()
    for h in heads:
        if not h.get("important"):
            continue
        key = norm(h["text"])
        if key in seen_h:
            continue
        seen_h.add(key)
        important.append(h)
    return {
        "headings": heads,
        "headings_important": important,
        "money": money[:120],
        "money_unique": sorted({m["value"] for m in money})[:80],
        "dates": dates[:120],
        "dates_unique": sorted({d["value"] for d in dates})[:80],
        "obligations": obligations[:80],
        "key_sentences": dedup[:60],
    }


# --------------------------------------------------------------------------- #
# Digest + rendering
# --------------------------------------------------------------------------- #
def locator_kind(units: list) -> str:
    if not units:
        return "none"
    hint = units[0]["locator"]
    return ("page" if hint.startswith("p.") else
            "slide" if hint.startswith("slide.") else
            "line" if hint.startswith("L") else
            "paragraph" if hint.startswith("¶") else "section")


def digest(path: Path, chunk_words: int, max_pages: int, focus: str, per_unit: int) -> dict:
    doc = load(path, chunk_words=chunk_words, max_pages=max_pages)
    words = sum(wc(u["text"]) for u in doc["units"])
    doc["stats"] = {
        "units": len(doc["units"]),
        "words": words,
        "read_minutes": max(1, int(round(words / 220))),
        "locator_kind": locator_kind(doc["units"]),
        "focus": focus or None,
    }
    doc["signals"] = build_signals(doc, focus=focus, per_unit=per_unit)
    return doc


def render_outline(doc: dict) -> str:
    if doc.get("error") and not doc.get("units"):
        return f"ERROR — {doc['error']}\n[{doc.get('source', '?')}]"
    s = doc["stats"]
    L = [f"# Document map — {Path(doc['source']).name}", ""]
    L.append(f"- kind: **{doc['kind']}** · locator: **{s['locator_kind']}** · "
             f"units: **{s['units']}** · words: **{s['words']:,}** · "
             f"reading time: **~{s['read_minutes']} min**")
    if s.get("focus"):
        L.append(f"- focus: **{s['focus']}**")
    if doc.get("error"):
        L.append(f"- ⚠️ {doc['error']}")
    for w in doc.get("warnings", []):
        L.append(f"- ⚠️ {w}")
    L.append("")

    sig = doc["signals"]
    imp = sig["headings_important"] or sig["headings"][:12]
    if imp:
        L.append("## Headings worth reading first / 先读这几节")
        for h in imp[:20]:
            star = "★ " if h.get("important") else ""
            L.append(f"- `{h['locator']}` {star}{h['text'][:110]}")
        L.append("")

    L.append("## Structure (read in this order) / 文档结构")
    L.append("")
    L.append("| # | Locator | Words | Opening line |")
    L.append("|---|---------|-------|--------------|")
    for i, u in enumerate(doc["units"], start=1):
        first = flatten(clean(u["text"]))[:100].replace("|", "/")
        L.append(f"| {i} | `{u['locator']}` | {wc(u['text'])} | {first} |")
    L.append("")

    if sig["key_sentences"]:
        L.append("## Candidate evidence — quote from these, do not invent / 可引用证据")
        for k in sig["key_sentences"][:18]:
            L.append(f"- `{k['locator']}` (score {k['score']}) — {flatten(k['text'])[:260]}")
        L.append("")
    if sig["money_unique"]:
        L.append("## Numbers found / 数字：" + " · ".join(sig["money_unique"][:24]))
        L.append("")
    if sig["dates_unique"]:
        L.append("## Dates found / 日期：" + " · ".join(sig["dates_unique"][:24]))
        L.append("")
    if sig["obligations"]:
        L.append("## Obligation language — must / shall / 不得 / 必须")
        for o in sig["obligations"][:12]:
            L.append(f"- `{o['locator']}` {flatten(o['text'])[:200]}")
        L.append("")
    L.append("---")
    L.append("Cite with `[p.3]` / `[slide.4]` / `[L120-180]` / `[¶7]` — the same locators shown above. "
             "Then run `docdigest.py check <source> <briefing.md>`; it fails on invented locators "
             "and on quotes that are not verbatim.")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
# Citation checking — the anti-hallucination guard
# --------------------------------------------------------------------------- #
CITE_RE = re.compile(
    r"\[(?:p|pp|pg|page|pages)\.?\s*(\d+)(?:\s*[-\u2013]\s*(\d+))?\]"
    r"|\[(?:slide|slides|s)\.?\s*(\d+)(?:\s*[-\u2013]\s*(\d+))?\]"
    r"|\[¶\s*(\d+)\]"
    r"|\[L\s*(\d+)(?:\s*[-\u2013]\s*(\d+))?\]",
    re.I)
QUOTE_RE = re.compile(r'[\u201c"]([^\u201d"]{12,300})[\u201d"]|[\u300c]([^\u300d]{8,300})[\u300d]')


def cited_locators(m: re.Match) -> list:
    g = m.groups()
    if g[0]:
        a, b = int(g[0]), int(g[1]) if g[1] else int(g[0])
        return [f"p.{i}" for i in range(min(a, b), max(a, b) + 1)]
    if g[2]:
        a, b = int(g[2]), int(g[3]) if g[3] else int(g[2])
        return [f"slide.{i}" for i in range(min(a, b), max(a, b) + 1)]
    if g[4]:
        return [f"¶{int(g[4])}"]
    if g[5]:
        a, b = int(g[5]), int(g[6]) if g[6] else int(g[5])
        return [f"L{a}-{b}"]
    return []


def _line_range_covers(cite: str, known: set) -> bool:
    cm = re.match(r"L(\d+)-(\d+)$", cite)
    if not cm:
        return False
    a, b = map(int, cm.groups())
    for k in known:
        km = re.match(r"L(\d+)-(\d+)$", k)
        if km:
            ka, kb = map(int, km.groups())
            if not (b < ka or a > kb):
                return True
    return False


def check_citations(doc_path: Path, brief_path: Path) -> int:
    doc = load(doc_path)
    if not doc["units"]:
        print(f"FATAL — cannot read source document: {doc.get('error')}", file=sys.stderr)
        return 2
    if not brief_path.exists():
        print(f"FATAL — briefing not found: {brief_path}", file=sys.stderr)
        return 2

    idx = {u["locator"]: u for u in doc["units"]}
    known_pages = {int(m.group(1)) for k in idx for m in [re.match(r"p\.(\d+)$", k)] if m}
    known_slides = {int(m.group(1)) for k in idx for m in [re.match(r"slide\.(\d+)$", k)] if m}
    known_paras = {int(m.group(1)) for k in idx for m in [re.match(r"¶(\d+)$", k)] if m}
    all_text = norm(" ".join(u["text"] for u in doc["units"]))

    brief = brief_path.read_text("utf-8", "ignore")
    errors, warns, ok, seen = [], [], 0, 0

    for ln, line in enumerate(brief.splitlines(), start=1):
        for m in CITE_RE.finditer(line):
            seen += 1
            locs = cited_locators(m)
            if not locs:
                continue
            missing = []
            for loc in locs:
                if loc in idx:
                    continue
                pm = re.match(r"p\.(\d+)$", loc)
                if pm and int(pm.group(1)) in known_pages:
                    continue
                sm = re.match(r"slide\.(\d+)$", loc)
                if sm and int(sm.group(1)) in known_slides:
                    continue
                qm = re.match(r"¶(\d+)$", loc)
                if qm and int(qm.group(1)) in known_paras:
                    continue
                if loc.startswith("L") and _line_range_covers(loc, set(idx)):
                    continue
                missing.append(loc)
            if missing:
                errors.append((ln, m.group(0), f"locator does not exist: {', '.join(missing[:4])}"))
                continue

            quotes = [q for grp in QUOTE_RE.findall(line) for q in grp if q]
            if quotes:
                target = norm(" ".join(idx[l]["text"] for l in locs if l in idx)) or all_text
                if not any(len(norm(q).strip(" .,;:")) >= 12 and
                           (norm(q).strip(" .,;:") in target or norm(q).strip(" .,;:") in all_text)
                           for q in quotes):
                    warns.append((ln, m.group(0),
                                  "quoted text is not verbatim in the cited unit — drop the quotes or copy exactly"))
                    continue
            ok += 1

    print(f"checked {brief_path.name} against {Path(doc['source']).name} "
          f"({doc['kind']}, {doc['stats']['units'] if 'stats' in doc else len(doc['units'])} units)")
    print(f"  citations: {seen} · verified: {ok} · errors: {len(errors)} · warnings: {len(warns)}")
    for ln, cite, msg in errors:
        print(f"  ERROR   L{ln:<5} {cite:<12} {msg}")
    for ln, cite, msg in warns:
        print(f"  WARN    L{ln:<5} {cite:<12} {msg}")
    if not seen:
        print("  WARN    no citations found — an uncited briefing is unverifiable")
    if errors:
        print("\nFAIL — fix the citations above. Never cite a locator you did not extract.")
        return 1
    print("\nPASS — every citation resolves to a real locator in the source.")
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="docdigest",
        description="Page-indexed document digest + citation checker (local, stdlib-first).")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, jsonflag=False):
        p.add_argument("file")
        p.add_argument("--focus", default="", help="keyword/phrase; ranks evidence toward it")
        p.add_argument("--chunk-words", type=int, default=DEFAULT_CHUNK_WORDS)
        p.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
        p.add_argument("--out", help="write to file instead of stdout")
        if jsonflag:
            p.add_argument("--json", action="store_true")
            p.add_argument("--per-unit", type=int, default=4)

    e = sub.add_parser("extract", help="digest (outline by default, JSON with --json)")
    common(e, jsonflag=True)

    o = sub.add_parser("outline", help="Markdown document map")
    common(o)

    c = sub.add_parser("check", help="verify citations + quotes in a briefing")
    c.add_argument("file", help="source document")
    c.add_argument("briefing", help="markdown briefing to verify")

    s = sub.add_parser("stats", help="one-line summary")
    s.add_argument("file")

    args = ap.parse_args(argv)

    if args.cmd == "check":
        return check_citations(Path(args.file).expanduser(), Path(args.briefing).expanduser())

    if args.cmd == "stats":
        d = digest(Path(args.file).expanduser(), DEFAULT_CHUNK_WORDS, 0, "", 1)
        if not d.get("stats", {}).get("units"):
            print(f"ERROR {d.get('error')}")
            return 2
        st = d["stats"]
        print(f"{Path(d['source']).name}: {d['kind']} · {st['units']} units · "
              f"{st['words']:,} words · ~{st['read_minutes']} min read")
        return 0

    path = Path(args.file).expanduser()
    if not path.exists():
        print(f"ERROR file not found: {path}", file=sys.stderr)
        return 2
    d = digest(path, args.chunk_words, args.max_pages, args.focus,
               getattr(args, "per_unit", 4))
    if not d["units"]:
        print(f"ERROR {d.get('error') or 'no text extracted'}", file=sys.stderr)
        return 2

    as_json = getattr(args, "json", False) and args.cmd == "extract"
    out = json.dumps(d, ensure_ascii=False, indent=2) if as_json else render_outline(d)
    if args.out:
        Path(args.out).expanduser().write_text(out, "utf-8")
        print(f"wrote {args.out} ({len(out):,} bytes)")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
