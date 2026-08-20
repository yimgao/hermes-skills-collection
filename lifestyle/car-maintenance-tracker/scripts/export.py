#!/usr/bin/env python3
"""export.py — Generate a dealer-ready service record (Markdown or HTML).

Usage:
    python scripts/export.py --car civic-2018 --format markdown --out civic-history.md
    python scripts/export.py --car civic-2018 --format html --out civic-history.html
    python scripts/export.py --car civic-2018 --format json --out civic-history.json
"""
from __future__ import annotations

import argparse
import html
import json
import statistics
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path("~/.hermes/cars").expanduser()


def _load(vid: str, fname: str) -> dict | None:
    p = ROOT / vid / fname
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    return data if isinstance(data, dict) else None


def _events(vid: str) -> list[dict]:
    p = ROOT / vid / "log.jsonl"
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def _ev_table(evs: list[dict]) -> str:
    rows = ["| Date | Odometer | Service | Vendor | Cost | Notes |",
            "|------|---------:|---------|--------|-----:|-------|"]
    for e in sorted(evs, key=lambda x: x.get("ts", "")):
        rows.append(
            f"| {e.get('ts', '')[:10]} | "
            f"{e.get('odometer', 0):,} | "
            f"{e.get('type', '')} | "
            f"{e.get('vendor', '—')} | "
            f"${e.get('total_cost', 0):.2f} | "
            f"{e.get('notes', '')} |"
        )
    return "\n".join(rows)


def _summary_stats(evs: list[dict]) -> dict:
    maint = sum(e.get("total_cost", 0) for e in evs
                if e.get("type") not in {"fuel", "fillup"})
    fuel = sum(e.get("total_cost", 0) for e in evs
               if e.get("type") in {"fuel", "fillup"})
    fills = [e for e in evs if e.get("type") in {"fuel", "fillup"}
             and "gallons" in e and "miles_since_last" in e]
    mpgs = [e["miles_since_last"] / e["gallons"] for e in fills]
    return {
        "total_events": len(evs),
        "maintenance_cost": maint,
        "fuel_cost": fuel,
        "fill_count": len(fills),
        "avg_mpg": statistics.mean(mpgs) if mpgs else 0,
        "min_mpg": min(mpgs) if mpgs else 0,
        "max_mpg": max(mpgs) if mpgs else 0,
    }


def export_markdown(vid: str) -> str:
    prof = _load(vid, "profile.json") or {}
    evs = _events(vid)
    stats = _summary_stats(evs)

    out = [
        f"# Vehicle Service Record — {prof.get('nickname', vid)}",
        "",
        f"_Generated: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "## Vehicle Information",
        "",
        f"- **Year / Make / Model:** {prof.get('year', '?')} {prof.get('make', '?')} {prof.get('model', '?')}",
        f"- **Trim:** {prof.get('trim', '—')}",
        f"- **VIN:** {prof.get('vin', '—')}",
        f"- **License plate:** {prof.get('plate', '—')}",
        f"- **Color:** {prof.get('color', '—')}",
        f"- **Purchase date:** {prof.get('purchase_date', '—')}",
        f"- **Purchase price:** ${prof.get('purchase_price', 0):,.2f}",
        f"- **Current odometer:** {prof.get('current_odometer', 0):,} {prof.get('odometer_unit', 'mi')}",
        f"- **Primary use:** {prof.get('primary_use', '—')}",
        f"- **Driving profile:** {prof.get('driving_profile', '—')}",
        "",
        "## Summary",
        "",
        f"- **Total events logged:** {stats['total_events']}",
        f"- **Maintenance spend:** ${stats['maintenance_cost']:,.2f}",
        f"- **Fuel spend:** ${stats['fuel_cost']:,.2f}",
        f"- **Fill-ups logged:** {stats['fill_count']}",
    ]
    if stats["avg_mpg"]:
        out.append(f"- **Avg MPG:** {stats['avg_mpg']:.1f} "
                   f"(min {stats['min_mpg']:.1f}, max {stats['max_mpg']:.1f})")

    out += [
        "",
        "## Service History",
        "",
        _ev_table(evs),
        "",
        "## Notes",
        "",
        prof.get("notes", "_No additional notes._"),
        "",
        "---",
        "",
        "_This document was generated from local records. "
        "The owner maintains these logs for personal reference. "
        "Shops may verify entries against corresponding receipts._",
    ]
    return "\n".join(out) + "\n"


def export_html(vid: str) -> str:
    md = export_markdown(vid)
    # Minimal: just wrap in a styled HTML page
    body = md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    body = body.replace("\n", "<br>")
    body = body.replace("**", "<strong>", 1)
    return f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>Vehicle Service Record — {html.escape(vid)}</title>
<style>
  body {{ font: 14px/1.5 -apple-system, sans-serif; max-width: 900px;
         margin: 40px auto; padding: 0 20px; color: #222; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; }}
  th {{ background: #f4f4f4; }}
  h1 {{ border-bottom: 2px solid #333; padding-bottom: 8px; }}
  h2 {{ margin-top: 2em; color: #333; }}
</style></head>
<body>
<pre style="white-space: pre-wrap; font-family: inherit;">{body}</pre>
</body></html>
"""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default="~/.hermes/cars")
    p.add_argument("--car", required=True)
    p.add_argument("--format", choices=["markdown", "html", "json"],
                   default="markdown")
    p.add_argument("--out", required=True, help="output file path")
    args = p.parse_args()

    global ROOT
    ROOT = Path(args.root).expanduser()

    if args.format == "markdown":
        content = export_markdown(args.car)
    elif args.format == "html":
        content = export_html(args.car)
    elif args.format == "json":
        prof = _load(args.car, "profile.json") or {}
        evs = _events(args.car)
        content = json.dumps({
            "profile": prof,
            "events": evs,
            "summary": _summary_stats(evs),
            "generated_at": datetime.now().isoformat(),
        }, indent=2)
    else:
        return 2

    out_path = Path(args.out).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content)
    print(f"  [OK] wrote {out_path}  ({len(content):,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())