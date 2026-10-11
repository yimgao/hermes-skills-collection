#!/usr/bin/env python3
"""
weekly-snapshot.py — summarize every canvas's last 7 days and append a
`## Snapshot — week-of YYYY-MM-DD` block to each canvas's Log.

Usage:
    python3 weekly-snapshot.py                       # scans default dir
    python3 weekly-snapshot.py --dir ~/custom/path
    python3 weekly-snapshot.py --days 7
    python3 weekly-snapshot.py --dry-run             # print, don't write

Outputs (stdout):
    Per-canvas summary table:
        slug | focus-lines | loops-opened | loops-closed | decisions | blockers
    Plus a grand total.

Never rewrites prior content — snapshot block is appended.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

DEFAULT_DIR = Path.home() / ".hermes" / "data" / "deep-work-canvas"


def parse_canvas(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    # sections by heading
    cur = None
    buckets: dict[str, list[str]] = {}
    for raw in lines:
        m = re.match(r"^##\s+(.+?)\s*$", raw)
        if m and not re.match(r"^\d{4}-\d{2}-\d{2}", m.group(1).strip()) \
                and "snapshot" not in m.group(1).lower():
            cur = re.sub(r"[^\w\s]", "", m.group(1)).strip().lower()
            buckets.setdefault(cur, [])
            continue
        if cur is not None:
            buckets[cur].append(raw)
    return buckets


def count_within(lines, since: datetime) -> int:
    """Count lines carrying an ISO date >= since."""
    n = 0
    for ln in lines:
        for d in re.findall(r"(20\d{2}-\d{2}-\d{2})", ln):
            try:
                dt = datetime.fromisoformat(d).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if dt >= since:
                n += 1
                break
    return n


def summarize(path: Path, since: datetime):
    b = parse_canvas(path)
    focus = count_within(b.get("current focus", []), since)
    opened = len(re.findall(r"^\s*-\s*\[ \]\s*\[id#\d+\].*", "\n".join(b.get("open loops", [])), re.M))
    closed = len(re.findall(r"^\s*-\s*\[x\]\s*\[id#\d+\].*", "\n".join(b.get("open loops", [])), re.M))
    decisions = count_within(b.get("decisions", []), since)
    blockers = sum(
        1 for ln in b.get("blockers", [])
        if ln.strip().startswith("- ") and "_(还没有)_" not in ln
    )
    return {
        "slug": path.stem,
        "focus_lines": focus,
        "loops_open": opened,
        "loops_closed": closed,
        "decisions": decisions,
        "blockers": blockers,
    }


def render_row(r) -> str:
    return (
        f"| `{r['slug']}` | {r['focus_lines']} | {r['loops_open']} | "
        f"{r['loops_closed']} | {r['decisions']} | {r['blockers']} |"
    )


def build_block(week_of: str, rows) -> str:
    header = (
        f"\n## Snapshot — week-of {week_of}\n\n"
        "| Canvas | Focus-lines | Loops opened | Loops closed | Decisions | Blockers |\n"
        "|---|---:|---:|---:|---:|---:|\n"
    )
    body = "\n".join(render_row(r) for r in rows)
    total = (
        f"\n_Totals: {sum(r['focus_lines'] for r in rows)} focus-lines, "
        f"{sum(r['loops_closed'] for r in rows)} loops closed, "
        f"{sum(r['decisions'] for r in rows)} decisions._\n"
    )
    return header + body + total


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(DEFAULT_DIR))
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    d = Path(args.dir).expanduser()
    if not d.is_dir():
        print(f"error: directory not found: {d}", file=sys.stderr)
        return 2

    now = datetime.now(timezone.utc)
    since = now - timedelta(days=args.days)
    week_of = since.date().isoformat()

    canvases = sorted(p for p in d.glob("*.md") if not p.name.startswith("."))
    if not canvases:
        print(f"no canvases in {d}")
        return 0

    rows = [summarize(p, since) for p in canvases]

    # print readable table
    print(f"Deep Work Canvas — week of {week_of}\n")
    print("| Canvas | Focus-lines | Loops opened | Loops closed | Decisions | Blockers |")
    print("|---|---:|---:|---:|---:|---:|")
    for r in rows:
        print(render_row(r))
    print(
        f"\nTotals: {sum(r['focus_lines'] for r in rows)} focus-lines · "
        f"{sum(r['loops_closed'] for r in rows)} loops closed · "
        f"{sum(r['decisions'] for r in rows)} decisions"
    )

    if args.dry_run:
        print("\n(dry-run: nothing written)")
        return 0

    block = build_block(week_of, rows)
    for p in canvases:
        with p.open("a", encoding="utf-8") as fh:
            fh.write(block)
    print(f"\nAppended snapshot to {len(canvases)} canvas file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
