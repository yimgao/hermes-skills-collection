#!/usr/bin/env python3
"""
validate.py — enforce the deep-work-canvas 8-section contract.

Usage:
    python3 validate.py <canvas.md> [<canvas.md> ...]
    python3 validate.py ~/.hermes/data/deep-work-canvas/*.md

Exit codes:
    0  all OK
    1  at least one validation error
    2  usage / file error

Checks:
    1. Exactly the 8 required sections, in order (ignoring emoji mismatches is NOT allowed).
    2. Each section has non-empty content (Parking Lot may hold a placeholder).
    3. `## Current Focus` contains both `当前在做` and `下一动作`.
    4. Every `[id#NN]` in Open Loops is unique within the file.
    5. No obvious secrets (heuristic scan).
"""

import re
import sys
from pathlib import Path

# Order matters. Match on the trailing ASCII keyword so emoji drift never breaks us.
REQUIRED = [
    "Goal",
    "Scope",
    "Current Focus",
    "Open Loops",
    "Decisions",
    "Blockers",
    "Parking Lot",
    "Log",
]

# Heuristics for secret leakage. Tuned to be noisy-but-useful, not paranoid.
SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),                       # AWS access key id
    re.compile(r"ghp_[A-Za-z0-9]{36}"),                    # GitHub PAT (classic)
    re.compile(r"github_pat_[A-Za-z0-9_]{60,}"),           # GitHub PAT (fine-grained)
    re.compile(r"sk-[A-Za-z0-9]{20,}"),                    # OpenAI-style key
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),           # Slack token
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|secret|password|passwd|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
]


def headings(lines):
    """Return list of (line_no, text) for top-level H2 headings."""
    out = []
    in_code = False
    for i, raw in enumerate(lines, start=1):
        if raw.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = re.match(r"^##\s+(.+?)\s*$", raw)
        if m:
            out.append((i, m.group(1)))
    return out


def section_body(lines, start_idx, end_idx):
    """Body text between two heading indices (exclusive)."""
    return [ln for ln in lines[start_idx:end_idx] if ln.strip()]


def strip_emoji_etc(text):
    """Reduce a heading like '🎯 Current Focus' to 'current focus'."""
    return re.sub(r"[^\w\s]", "", text, flags=re.UNICODE).strip().lower()


def validate(path: Path) -> list[str]:
    errs = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return [f"{path}: cannot read ({e})"]

    lines = text.splitlines()
    hs = headings(lines)

    # --- 1. section names, order, count ---
    found = [strip_emoji_etc(h) for _, h in hs]
    expected = [strip_emoji_etc(r) for r in REQUIRED]

    # Log section legitimately contains nested `## YYYY-MM-DD` day headings,
    # plus weekly `## Snapshot — week-of …` blocks. Drop those before comparing.
    # NOTE: match on the RAW heading — strip_emoji_etc() would eat the hyphens
    # in a date and turn "2026-10-10" into "20261010".
    day_re = re.compile(
        r"^\s*\d{4}-\d{2}-\d{2}\s*$"          # ## 2026-10-10
        r"|^\s*(?:[\U0001F300-\U0001FAFF\u2600-\u27BF]\s*)?snapshot\b",
        re.IGNORECASE,
    )
    filtered = [(ln, h) for ln, h in hs if not day_re.match(h)]

    fnames = [strip_emoji_etc(h) for _, h in filtered]
    if fnames != expected:
        errs.append(
            f"{path.name}: section list mismatch.\n"
            f"    expected: {expected}\n"
            f"    found:    {fnames}"
        )

    # --- 2. non-empty bodies ---
    idxs = [ln for ln, _ in filtered]
    for i, (ln, name) in enumerate(filtered):
        start = ln  # 0-based slice start; heading is lines[ln-1]
        end = idxs[i + 1] - 1 if i + 1 < len(idxs) else len(lines)
        body = section_body(lines, start, end)
        # allow placeholder markers
        content = "\n".join(body)
        if "_(none yet)_" in content or "_(还没有)_" in content or "_(第一次记录时删除这一行)_" in content:
            continue
        if not body:
            errs.append(f"{path.name}: section '{name}' is empty.")

    # --- 3. Current Focus schema ---
    body_all = "\n".join(lines)
    if "Current Focus" in [strip_emoji_etc(r) for r in REQUIRED]:
        cf_start = None
        cf_end = None
        for i, (ln, h) in enumerate(filtered):
            if strip_emoji_etc(h) == "current focus":
                cf_start = ln
                cf_end = idxs[i + 1] - 1 if i + 1 < len(idxs) else len(lines)
                break
        if cf_start is not None:
            cf_body = "\n".join(section_body(lines, cf_start, cf_end))
            if "当前在做" not in cf_body:
                errs.append(f"{path.name}: '## Current Focus' missing '当前在做' line.")
            if "下一动作" not in cf_body:
                errs.append(f"{path.name}: '## Current Focus' missing '下一动作' line.")
            # next-move must not be a bare placeholder
            m = re.search(r"下一动作[：:]\s*(.+)", cf_body)
            if m:
                nm = m.group(1).strip().strip("*_")
                if not nm or nm in {"TBD", "todo", "待定"}:
                    errs.append(f"{path.name}: '下一动作' is empty or a placeholder ('{nm}').")

    # --- 4. unique loop ids ---
    ids = re.findall(r"\[id#([0-9]+)\]", text)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        errs.append(f"{path.name}: duplicate Open Loop id(s): {', '.join('id#' + d for d in dupes)}")

    # --- 5. secret heuristics ---
    for pat in SECRET_PATTERNS:
        m = pat.search(text)
        if m:
            snippet = m.group(0)[:12] + "…"
            errs.append(f"{path.name}: possible secret leaked ({pat.pattern[:30]}… → '{snippet}')")
            break

    return errs


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2

    all_errs: list[str] = []
    checked = 0
    for a in argv[1:]:
        p = Path(a).expanduser()
        if not p.exists():
            print(f"skip: {a} (not found)")
            continue
        if p.is_dir():
            continue
        checked += 1
        all_errs.extend(validate(p))

    if all_errs:
        for e in all_errs:
            print("FAIL:", e)
        print(f"\n{len(all_errs)} error(s) across {checked} file(s).")
        return 1

    print(f"OK — {checked} canvas file(s) validated.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
