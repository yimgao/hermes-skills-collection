#!/usr/bin/env python3
"""
extract.py — Parse a raw insurance quote / policy document into structured JSON.

Insurance quotes arrive as PDFs, emails, or screenshot OCR text that is a
nightmare to read. This script pulls the numbers out with label-matching
patterns so you can drop the result straight into compare.py.

Usage:
    python3 extract.py quote.txt --product auto --out quotes.json
    python3 extract.py quote.txt --product auto --id q1 --carrier GEICO --out quotes.json
    cat quote.txt | python3 extract.py --product auto --out -
    python3 extract.py --patterns        # list every pattern this script knows

Pure stdlib. Works on plain text (paste from a PDF via `pbpaste`, `pdftotext`,
or OCR). No network, no upload.
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Limit extractors: (canonical_field, regex, cast)
# Each regex must expose named groups: `num` (the amount) and optionally `k`/`m`.
# ---------------------------------------------------------------------------

NUM = r"(?P<num>[\$€£]?\s*[\d,]+(?:\.\d+)?)\s*(?P<k>(?<![A-Za-z])(?:thousand|million|[km])(?![A-Za-z]))?"

# Separator between a label and its amount in a real quote:
#   "Bodily Injury Liability (per person) ....... $ 100,000"
#   "Bodily Injury Liability (per person): $100,000"
#   "Bodily Injury Liability (per person)    100,000"
SEP = r"[ \t]*(?:[:\-=]|\.{2,})?[ \t]*"

# Optional parenthetical qualifier after a label, e.g. " (per person)".
PARENS = r"(?:\s*\([^)]*\))?"


def _label_then(lbl: str, num: str = NUM) -> str:
    """Build a regex matching <label><optional parens><sep><amount>."""
    return rf"{lbl}{PARENS}{SEP}{num}"


# Parenthetical variants of the liability labels: the qualifier can sit inside
# the parens ("Bodily Injury Liability (per person)") or trail the label
# ("Bodily Injury Liability per person"). Match both.
_BI_PER_PERSON = r"bodily\s+injury\s+(?:liability\s+)?(?:\(\s*per\s+(?:person|each\s+person)\s*\)|per\s+(?:person|each\s+person))"
_BI_PER_ACCIDENT = r"bodily\s+injury\s+(?:liability\s+)?(?:\(\s*per\s+accident\s*\)|per\s+accident)"
_UM_UIM = (r"(?:uninsured\s*[/&]?\s*(?:motorist|underinsured)"
           r"(?:\s*[/,&-]?\s*(?:um[\s/-]*uim|uim)\s*)?"
           r"|um\s*/?\s*uim"
           r"|uninsured\s+underinsured)")

LIMIT_PATTERNS: List[Tuple[str, str, str]] = [
    # ---- auto ----
    ("liability_per_person", _label_then(_BI_PER_PERSON), "money"),
    ("liability_per_accident", _label_then(_BI_PER_ACCIDENT), "money"),
    ("property_damage", _label_then(r"(?:property\s+damage\s+liability|property\s+damage)"), "money"),
    ("medical_pay", _label_then(r"(?:medical\s+payments?(?:\s*/\s*medpay)?|medpay)"), "money"),
    ("uninsured_motorist", _label_then(_UM_UIM), "money"),
    ("collision", _label_then(r"collision\s*(?:coverage|d)?"), "money"),
    ("comprehensive", _label_then(r"comprehensive\s*(?:coverage|d)?"), "money"),

    # ---- home / renters ----
    ("loss_of_use", _label_then(r"(?:loss\s+of\s+use(?:d)?(?:\s+coverage)?|additional\s+living\s+expenses?)"), "money"),
    ("personal_property", _label_then(r"(?:personal\s+property(?:\s+coverage)?|contents\s+coverage)"), "money"),

    # ---- health ----
    ("out_of_pocket_max", _label_then(r"(?:out[- ]of[- ]pocket\s+(?:maximum|max)|oop\s+max)"), "money"),
    ("primary_care_copay", _label_then(r"(?:primary\s+care|office\s+visit|pcp)\s*(?:copay)?"), "money"),
    ("specialist_copay", _label_then(r"(?:specialist\s+visit|specialist)\s*(?:copay)?"), "money"),
    ("generic_rx", _label_then(r"generic\s*(?:drug|prescription|rx)s?"), "money"),
    ("brand_rx", _label_then(r"(?:brand[\s-]name|brand)\s*(?:drug|prescription|rx)s?"), "money"),
    ("coinsurance", _label_then(r"coinsurance"), "percent"),
    ("emergency_room_copay", _label_then(r"(?:emergency\s+room|er)\s*(?:copay|visit)"), "money"),
    ("hospital_admit_copay", _label_then(r"(?:hospital\s+(?:admission|admit|stay)|inpatient)\s*(?:copay)?"), "money"),

    # ---- life / disability ----
    ("death_benefit", _label_then(r"(?:death\s+benefit|benefit\s+amount|face\s+amount)"), "money"),
    ("monthly_benefit", _label_then(r"(?:monthly\s+benefit|disability\s+benefit)"), "money"),

    # ---- pet ----
    ("accident_limit", _label_then(r"accident\s+limit"), "money"),
    ("illness_limit", _label_then(r"illness\s+limit"), "money"),
    ("annual_max", _label_then(r"(?:annual\s+max(?:imum)?|annual\s+limit)"), "money"),
]

DEDUCTIBLE_PATTERNS = [
    _label_then(r"(?:collision\s+deductible|comprehensive\s+deductible|deductible)"),
    _label_then(r"(?:annual\s+deductible|individual\s+deductible|plan\s+deductible)"),
]

# Each premium pattern: (regex, multiplier-to-annual).
# A 6-month premium is x2 for the year; a monthly premium is x12.
# The optional "(for <plan>)" segment lets us pull a single plan out of a
# multi-plan comparison sheet.
PLAN_MIDDLE = r"(?:\s*(?:for|of|on)\s+[A-Za-z0-9][A-Za-z0-9 \-]{0,40}?)?"
PREMIUM_PATTERNS: List[Tuple[str, float]] = [
    (rf"(?:total\s+)?(?:annual|annualized)\s*(?:premium)?{PLAN_MIDDLE}\s*(?:amount|cost|total)?{SEP}\$?\s*([\d,]+(?:\.\d+)?)", 1.0),
    (rf"(?:twelve|12)\s*[- ]?month\s+premium{PLAN_MIDDLE}{SEP}\$?\s*([\d,]+(?:\.\d+)?)", 1.0),
    (rf"(?:six|6)\s*[- ]?month\s+premium{PLAN_MIDDLE}{SEP}\$?\s*([\d,]+(?:\.\d+)?)", 2.0),
    (rf"(?:monthly|premium\s+per\s+month|monthly\s+premium){PLAN_MIDDLE}\s*(?:amount|cost|total)?{SEP}\$?\s*([\d,]+(?:\.\d+)?)", 12.0),
    (rf"(?:premium|cost|price|rate){PLAN_MIDDLE}{SEP}\$?\s*([\d,]+(?:\.\d+)?)", 1.0),
    (rf"\$?\s*([\d,]+(?:\.\d+)?)\s*(?:per|/)\s*(?:month|mo\b)", 12.0),
    (rf"\$?\s*([\d,]+(?:\.\d+)?)\s*(?:per|/)\s*(?:yr|year|annually|ann)", 1.0),
]

FEATURE_PATTERNS = {
    "rental_reimbursement": [r"rental\s+(?:reimbursement|coverage)",
                             r"rental\s+car\s+(?:reimbursement|coverage)"],
    "roadside_assistance": [r"roadside\s+assistance", r"roadside\s+service"],
    "gap_cover": [r"gap\s+(?:coverage|cover|insurance)", r"gap\s+guarantee"],
    "accident_forgiveness": [r"accident\s+forgiveness", r"accident[\s-]?forgiv\w*\s+discount"],
    "new_car_replacement": [r"new\s+car\s+replacement"],
    "pet_injury_liability": [r"pet\s+(?:injury\s+)?liability", r"pet\s+damage\s+liability"],
    "waiver_of_premium": [r"waiver\s+of\s+premium"],
    "residual_benefit": [r"residual\s+benefit"],
    "rx_coverage": [r"prescription\s+(?:coverage|benefit)", r"rx\s+coverage"],
    "scheduled_equipment": [r"scheduled\s+equipment", r"scheduled\s+(?:gear|items?)"],
    "convertible": [r"convertible\s+to\s+permanent"],
    "preexisting_waiver": [r"pre[- ]?existing\s+condition\s+waiver"],
    "specialist_visits": [r"specialist\s+visits?", r"specialist\s+visits?\s*[:\-]"],
    "out_of_network": [r"out[- ]of[- ]network\s+(?:benefit|coverage)"],
    "telehealth": [r"telehealth", r"virtual\s+visit"],
    "hsa_eligible": [r"hsa[- ]eligible", r"hsa\s+eligible"],
}

# Feature values that are textual rather than boolean.
FEATURE_TEXT: Dict[str, str] = {
    "specialist_visits": "Unlimited",
}

# Explicit "present + value" phrasing marks a LIMIT; bare mentions of a
# feature often mean "not included". Heuristic: a feature counts as ON when
# it appears near "included", "yes", "coverage provided", or a dollar amount.
NEGATION_RE = re.compile(
    r"(?:not\s+included|not\s+covered|no\s+rental|no\s+roadside|"
    r"not\s+available|excluded|does\s+not\s+cover|optional|waiver\s+of\s+premium\s+premium)",
    re.IGNORECASE)

SCALE = {"k": 1_000, "thousand": 1_000, "m": 1_000_000, "million": 1_000_000}


def parse_amount(raw: str, scale: Optional[str] = None) -> Optional[float]:
    if raw is None:
        return None
    s = re.sub(r"[^\d.]", "", raw)
    if not s:
        return None
    try:
        val = float(s)
    except ValueError:
        return None
    if scale:
        val *= SCALE.get(scale.lower(), 1)
    return val


def find_first(text: str, patterns: List[str], kind: str = "money") -> Optional[Tuple[Optional[float], str]]:
    """Return (amount, matched_text) for the first pattern that hits."""
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if m:
            groups = m.groupdict()
            if "num" in groups and groups.get("num") is not None:
                val = parse_amount(groups["num"], groups.get("k"))
                if kind == "percent" and val is not None:
                    # "40%" -> 0.40 (a share), "40" without % -> 40.0
                    raw_txt = m.group(0)
                    if "%" not in raw_txt and val > 1:
                        val = val / 100.0
                    elif "%" in raw_txt:
                        val = val / 100.0
                return val, m.group(0)
            # fallback: first numeric-ish group
            for g in m.groups():
                if g and re.search(r"\d", g):
                    return parse_amount(g), m.group(0)
    return None


def extract_limits(text: str) -> Dict[str, Any]:
    limits: Dict[str, Any] = {}
    for field, pat, kind in LIMIT_PATTERNS:
        hit = find_first(text, [pat], kind)
        if hit and hit[0] is not None:
            limits[field] = hit[0]
    return limits


def extract_deductible(text: str) -> Optional[float]:
    for pat in DEDUCTIBLE_PATTERNS:
        hit = find_first(text, [pat])
        if hit:
            return hit[0]
    return None


def extract_premium(text: str) -> Tuple[Optional[float], str]:
    """Return (annual_premium, basis). Falls back to monthly x12."""
    for pat, mult in PREMIUM_PATTERNS:
        m = re.search(pat, text, re.IGNORECASE | re.DOTALL)
        if not m:
            continue
        val = parse_amount(m.group(1))
        if val is None:
            continue
        if mult == 1.0:
            return round(val, 2), "annual"
        if mult == 2.0:
            return round(val * 2, 2), "6-month x2"
        return round(val * 12, 2), "monthly x12"
    return None, "not found"


def extract_features(text: str) -> Dict[str, Any]:
    feats: Dict[str, Any] = {}
    for key, pats in FEATURE_PATTERNS.items():
        on = False
        for pat in pats:
            for m in re.finditer(pat, text, re.IGNORECASE):
                window = text[max(0, m.start() - 60): m.end() + 60]
                if NEGATION_RE.search(window):
                    continue
                on = True
                break
            if on:
                break
        feats[key] = on
    # A textual value ("Specialist Visits: Unlimited") beats the boolean.
    for key, textval in FEATURE_TEXT.items():
        pat = re.compile(rf"{re.escape(key.split('_')[0])}\s+{re.escape(key.split('_')[1])}s?"
                         rf"\s*[:\-]\s*([A-Za-z]+)", re.IGNORECASE)
        m = pat.search(text)
        if m:
            feats[key] = m.group(1).lower() in ("unlimited", "yes", "included", "covered")
    return feats


def isolate_section(text: str, section: str) -> Optional[str]:
    """
    Pull one plan block out of a multi-plan comparison sheet.

    Strategy: find the line naming the plan, then take everything from that
    line until the next *plan header*. A plan header is a short line that
    names something (contains a plan-ish keyword) but is NOT a data row —
    a data row has a "Label: value" shape with a number in it.
    """
    lines = text.splitlines()
    key = section.lower()

    header_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or len(s) > 80:
            continue
        if key in s.lower():
            header_idx = i
            break

    if header_idx is None:
        return None

    plan_words = (r"(?:plan|option|ppo|hmo|epo|hdhp|tier|bronze|silver|gold|platinum|"
                  r"policy|quote|summary|comparison|coverage)")
    next_re = re.compile(rf"^\s*[#\-=*]*\s*.{{0,70}}?(?:{plan_words}).{{0,50}}$", re.IGNORECASE)
    # A data row looks like "Label ....... $123" or "Label: 123".
    data_row_re = re.compile(r"[:.]+\s*\$?\s*[\d]", re.IGNORECASE)

    end = len(lines)
    for j in range(header_idx + 1, len(lines)):
        s = lines[j].strip()
        if not s:
            continue
        if len(s) <= 80 and not data_row_re.search(s) and next_re.match(s) \
                and key not in s.lower():
            end = j
            break

    return "\n".join(lines[header_idx:end])


def detect_redflags(text: str, limits: Dict[str, Any], product: str) -> List[str]:
    flags: List[str] = []
    low = text.lower()

    if product == "auto":
        li = limits.get("liability_per_person") or 0
        # Most states require >= 25k; anything <= 50k is a meaningful red flag.
        if li and li <= 50000:
            flags.append("below_state_minimum")
        if "uninsured" not in low and "um/uim" not in low and "uim" not in low:
            flags.append("no_ump")
        if re.search(r"actual\s+cash\s+value\s+only|acv\s+only", low):
            flags.append("replacement_cost_disabled")
        if re.search(r"unattended\s+vehicle", low) and re.search(r"not\s+covered|excluded", low):
            flags.append("excludes_theft_at_unattended_vehicle")
        if re.search(r"collision\s*[:\-]?\s*(?:not\s+included|none|excluded)", low):
            flags.append("no_collision")

    if product == "home":
        if re.search(r"actual\s+cash\s+value|acv\s+only|depreciated", low) and "replacement cost" not in low:
            flags.append("replacement_cost_disabled")

    if product in ("health", "life", "disability", "pet"):
        if re.search(r"pre[- ]?existing\s+conditions?\s+(?:are\s+)?(?:not\s+covered|excluded|not\s+covered)", low):
            flags.append("preexisting_conditions_excluded")

    if limits.get("liability_per_person") is None and limits.get("liability_per_accident") is None:
        if product in ("auto", "home", "umbrella", "renters"):
            flags.append("no_liability")

    return flags


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract structured data from an insurance quote.")
    ap.add_argument("source", nargs="?", help="Path to quote text file ('-' for stdin)")
    ap.add_argument("--product", default="auto",
                    help="auto|home|renters|health|life|disability|pet|umbrella|gear")
    ap.add_argument("--id", default="quote-1", help="Quote id")
    ap.add_argument("--carrier", default=None, help="Carrier name (auto-detected if omitted)")
    ap.add_argument("--out", default="-", help="Output JSON path ('-' for stdout)")
    ap.add_argument("--append", action="store_true",
                    help="Append to an existing --out file instead of replacing it")
    ap.add_argument("--section", metavar="PLAN_NAME", default=None,
                    help="Extract only the block for one plan (case-insensitive substring). "
                         "Use for multi-plan comparison sheets.")
    ap.add_argument("--patterns", action="store_true", help="List known limit patterns and exit")
    args = ap.parse_args()

    if args.patterns:
        print("LIMIT PATTERNS")
        for field, pat, _ in LIMIT_PATTERNS:
            print(f"  {field:26s} {pat}")
        print("\nFEATURE PATTERNS")
        for key, pats in FEATURE_PATTERNS.items():
            print(f"  {key:26s} {pats[0]}")
        return 0

    if args.source and args.source != "-":
        try:
            with open(args.source, "r", encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as e:
            print(f"[ERROR] Cannot read {args.source}: {e}", file=sys.stderr)
            return 2
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("[ERROR] Empty input. Paste the quote text or pass a file.", file=sys.stderr)
        return 2

    if args.section:
        section = isolate_section(text, args.section)
        if section is None:
            print(f"[ERROR] Could not find a section matching '{args.section}'.", file=sys.stderr)
            return 2
        full_text = text
        text = section
        print(f"[INFO] Isolated section '{args.section}' ({len(text)} chars)", file=sys.stderr)
    else:
        full_text = text

    # Carrier: first line that looks like a name, else arg
    carrier = args.carrier
    if not carrier:
        for line in text.splitlines():
            line = line.strip()
            if 2 < len(line) < 60 and re.match(r"^[A-Za-z0-9 .'\-&]+$", line) and not re.match(r"^\d", line):
                carrier = line
                break
        carrier = carrier or "Unknown Carrier"

    limits = extract_limits(text)
    deductible = extract_deductible(text)
    premium, basis = extract_premium(text)
    features = extract_features(text)
    flags = detect_redflags(text, limits, args.product)

    # If the section had no premium, look for one in the full document that
    # names this plan ("Annual premium for PPO Silver: $4,320").
    if premium is None and args.section:
        plan_words = [w for w in re.split(r"[^A-Za-z0-9]+", args.section) if len(w) > 2]
        for line in full_text.splitlines():
            low = line.lower()
            if "premium" not in low and "$" not in line:
                continue
            if not any(w.lower() in low for w in plan_words):
                continue
            hit = extract_premium(line)
            if hit[0] is not None:
                premium, basis = hit[0], hit[1] + " (from plan line)"
                break

    quote: Dict[str, Any] = {
        "id": args.id,
        "carrier": carrier,
        "product": args.product,
        "annual_premium": premium,
        "premium_basis": basis,
        "currency": "USD",
        "deductible": deductible,
        "limits": limits,
        "features": features,
        "redflags": flags,
        "notes": f"extracted via extract.py from {args.source if args.source != '-' else 'stdin'}",
    }

    if not limits and not premium:
        print("[WARN] Nothing extracted — the text may be scanned/image-based. "
              "Run OCR first (e.g. `ocrmypdf` or `pdftotext` for digital PDFs).",
              file=sys.stderr)

    # Always write the {"quotes": [...]} envelope when writing to a file, so
    # that --append can accumulate and compare.py can read it directly.
    payload: Any = quote
    if args.out != "-":
        existing: List[Any] = []
        if args.append:
            try:
                with open(args.out, "r", encoding="utf-8") as fh:
                    loaded = json.load(fh)
                if isinstance(loaded, dict):
                    if "quotes" in loaded:
                        existing = list(loaded.get("quotes") or [])
                    else:
                        # A bare single-quote object from an earlier run.
                        existing = [loaded]
                elif isinstance(loaded, list):
                    existing = list(loaded)
            except (OSError, json.JSONDecodeError):
                existing = []
        existing.append(quote)
        payload = {"quotes": existing}

    if args.out == "-":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"[OK] Wrote {args.id} -> {args.out}", file=sys.stderr)
        print(f"     premium={premium} ({basis})  limits_found={len(limits)}  "
              f"deductible={deductible}  redflags={flags}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
