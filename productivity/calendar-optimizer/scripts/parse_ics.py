#!/usr/bin/env python3
"""
parse_ics.py — RFC 5545 iCalendar parser for Calendar Optimizer.

Usage:
    python3 parse_ics.py <path/to/calendar.ics> [--json]

Outputs a list of events with start, end, summary, organizer, attendees.
Pure stdlib (no dependencies). Handles line-folding (RFC 5545 §3.1),
all-day events (VALUE=DATE), and timezone offsets (Z suffix).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path


def unfold(text: str) -> str:
    """Unfold RFC 5545 line continuations (lines starting with space/tab)."""
    lines = text.splitlines()
    out = []
    for line in lines:
        if line.startswith((" ", "\t")) and out:
            out[-1] += line[1:]
        else:
            out.append(line)
    return "\n".join(out)


def parse_dt(raw: str) -> datetime | None:
    """Parse DTSTART/DTEND value. Supports all-day dates and Z-suffixed UTC."""
    if not raw:
        return None
    raw = raw.strip()
    if "VALUE=DATE" in raw or (len(raw) == 8 and raw.isdigit()):
        # All-day event: YYYYMMDD
        try:
            return datetime.strptime(raw, "%Y%m%d")
        except ValueError:
            return None
    # Date-time forms: 20250813T140000Z or 20250813T140000
    raw = raw.replace("Z", "+00:00")
    for fmt in ("%Y%m%dT%H%M%S%z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    return None


def parse_ics(path: str) -> list[dict]:
    """Parse ICS file → list of event dicts."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    unfolded = unfold(text)
    events = []
    for block in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", unfolded, re.S):
        def get(field: str) -> str:
            # Field may have parameters: SUMMARY;LANGUAGE=en:Hello
            m = re.search(rf"^{re.escape(field)}(?:;[^\n:]*)?[;:](.*)$", block, re.M)
            return m.group(1).strip() if m else ""

        dtstart = parse_dt(get("DTSTART"))
        dtend = parse_dt(get("DTEND"))
        if dtstart is None:
            continue

        # All-day events: only DTSTART, no DTEND
        if dtend is None:
            dtend = dtstart + timedelta(days=1)
        elif dtend == dtstart and len(get("DTSTART")) == 8:
            dtend = dtstart + timedelta(days=1)

        duration_min = int((dtend - dtstart).total_seconds() / 60)
        all_day = len(get("DTSTART")) == 8

        # Attendees: ATTENDEE:mailto:a@b.com (one per line)
        attendee_lines = re.findall(r"^ATTENDEE[;:]", block, re.M)
        attendees = len(attendee_lines) if attendee_lines else 0

        # RRULE for recurring events (we capture but don't expand)
        rrule = get("RRULE")

        events.append({
            "uid":          get("UID"),
            "summary":      get("SUMMARY"),
            "description":  get("DESCRIPTION")[:200],
            "organizer":    get("ORGANIZER").replace("mailto:", ""),
            "location":     get("LOCATION"),
            "start":        dtstart.isoformat(),
            "end":          dtend.isoformat(),
            "duration_min": duration_min,
            "attendees":    attendees,
            "all_day":      all_day,
            "recurring":    bool(rrule),
        })
    return events


def main() -> int:
    p = argparse.ArgumentParser(description="Parse ICS calendar export")
    p.add_argument("path", help="Path to .ics file")
    p.add_argument("--json", action="store_true", help="Output JSON")
    p.add_argument("--from", dest="start", help="Filter from date YYYY-MM-DD")
    p.add_argument("--to", dest="end", help="Filter to date YYYY-MM-DD")
    args = p.parse_args()

    events = parse_ics(args.path)

    if args.start:
        start_dt = datetime.fromisoformat(args.start)
        events = [ev for ev in events if datetime.fromisoformat(ev["start"]) >= start_dt]
    if args.end:
        end_dt = datetime.fromisoformat(args.end)
        events = [ev for ev in events if datetime.fromisoformat(ev["start"]) <= end_dt]

    if args.json:
        print(json.dumps(events, indent=2, ensure_ascii=False))
    else:
        print(f"Parsed {len(events)} events from {args.path}")
        for ev in events[:20]:
            tag = "[ALLDAY]" if ev["all_day"] else "[---]   "
            rec = "[RECUR]" if ev["recurring"] else "       "
            print(f"{tag} {rec} {ev['start'][:16]}  {ev['duration_min']:>4} min  "
                  f"({ev['attendees']} ppl)  {ev['summary'][:50]}")
        if len(events) > 20:
            print(f"... and {len(events) - 20} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
