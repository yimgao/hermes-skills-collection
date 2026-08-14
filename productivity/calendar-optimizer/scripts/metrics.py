#!/usr/bin/env python3
"""
metrics.py — Calendar Optimizer metrics engine.

Usage:
    python3 metrics.py events.json > metrics.json
    python3 metrics.py events.json --report report.md

Reads a JSON event list (output of parse_ics.py) and computes:
  - daily breakdown (meeting %, fragmentation, focus blocks)
  - weekly rollup
  - day-of-week heat map
  - summary statistics

All output is in local time. Configure WORK_START_HOUR, WORK_END_HOUR
in your local profile.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


# Defaults — personalize via args or profile.json
WORK_START_HOUR = 9
WORK_END_HOUR = 18
DEEP_WORK_MIN = 90          # uninterrupted block threshold
BATCH_WINDOW_MIN = 30       # gaps ≤ N min count as fragmentation
NO_MEETING_THRESHOLD_PCT = 25  # < 25% meeting load = "focus day" candidate


def parse_events(events: list[dict]) -> list[dict]:
    """Re-hydrate ISO start/end into datetimes."""
    out = []
    for e in events:
        try:
            out.append({
                **e,
                "_start": datetime.fromisoformat(e["start"].replace("Z", "+00:00")),
                "_end":   datetime.fromisoformat(e["end"].replace("Z", "+00:00")),
                "_is_meeting": (not e.get("all_day", False)) and e["summary"] != "",
            })
        except (ValueError, KeyError):
            continue
    return out


def compute_metrics(events_raw: list[dict],
                    work_start_hour: int = WORK_START_HOUR,
                    work_end_hour: int = WORK_END_HOUR,
                    only_meetings: bool = True,
                    workdays_only: bool = True) -> dict:
    events = parse_events(events_raw)
    if only_meetings:
        events = [e for e in events if e["_is_meeting"]]

    by_day: dict = defaultdict(list)
    for e in events:
        local_start = e["_start"]
        if workdays_only and local_start.weekday() >= 5:
            continue
        by_day[local_start.date()].append(e)

    daily = []
    for day, evs in sorted(by_day.items()):
        evs.sort(key=lambda x: x["_start"])
        meeting_min = sum(e["duration_min"] for e in evs)

        # Fragmentation: small gaps between meetings
        gaps_small = 0
        gaps_large = []  # ≥90 min become focus-block candidates
        for i in range(len(evs) - 1):
            gap = (evs[i+1]["_start"] - evs[i]["_end"]).total_seconds() / 60
            if 0 < gap <= BATCH_WINDOW_MIN:
                gaps_small += 1
            if gap >= DEEP_WORK_MIN:
                gaps_large.append(gap)

        # Pre-work & post-work focus windows
        workday_start = evs[0]["_start"].replace(hour=work_start_hour, minute=0, second=0) if evs else None
        workday_end   = evs[0]["_start"].replace(hour=work_end_hour,   minute=0, second=0) if evs else None
        if evs and workday_start and evs[0]["_start"] > workday_start:
            pre = (evs[0]["_start"] - workday_start).total_seconds() / 60
            if pre >= DEEP_WORK_MIN:
                gaps_large.append(pre)
        if evs and workday_end and evs[-1]["_end"] < workday_end:
            post = (workday_end - evs[-1]["_end"]).total_seconds() / 60
            if post >= DEEP_WORK_MIN:
                gaps_large.append(post)

        work_day_min = (work_end_hour - work_start_hour) * 60
        meeting_pct = round(100 * meeting_min / work_day_min, 1) if work_day_min else 0
        daily.append({
            "date":              day.isoformat(),
            "weekday":           day.strftime("%A"),
            "n_meetings":        len(evs),
            "meeting_min":       meeting_min,
            "meeting_pct":       meeting_pct,
            "fragmentation":     gaps_small,
            "focus_blocks":      len(gaps_large),
            "focus_min_total":   int(sum(gaps_large)),
            "longest_focus_min": int(max(gaps_large)) if gaps_large else 0,
        })

    # Day-of-week heat map
    dow = defaultdict(lambda: {"meet_min": 0, "focus_min": 0, "n": 0})
    work_day_min = (work_end_hour - work_start_hour) * 60
    for d in daily:
        dow[d["weekday"]]["meet_min"]  += d["meeting_min"]
        dow[d["weekday"]]["focus_min"] += d["focus_min_total"]
        dow[d["weekday"]]["n"] += 1
    weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    heatmap = []
    for wd, v in dow.items():
        n = max(1, v["n"])
        heatmap.append({
            "weekday":         wd,
            "n_days":          v["n"],
            "avg_meeting_pct": round(100 * v["meet_min"] / (n * work_day_min), 1),
            "avg_focus_min":   round(v["focus_min"] / n, 1),
            "verdict":         _verdict(100 * v["meet_min"] / (n * work_day_min)),
        })
    heatmap.sort(key=lambda x: weekday_order.index(x["weekday"]))

    # Recurring meeting dedup → candidate time sinks
    # Heuristic: same summary + day_of_week + start_hour
    rec_keys = defaultdict(lambda: {"count": 0, "n_attendees": []})
    for e in events:
        if e["_is_meeting"] and e["_start"].weekday() < 5:
            key = (e["summary"], e["_start"].strftime("%A"), e["_start"].hour)
            rec_keys[key]["count"] += 1
            rec_keys[key]["n_attendees"].append(e["attendees"])
    time_sinks = []
    for (summary, day, hour), info in rec_keys.items():
        if info["count"] >= 3:  # recurring at least 3× in window
            avg_att = round(sum(info["n_attendees"]) / len(info["n_attendees"]), 1)
            has_agenda = any(kw in summary.lower() for kw in ("agenda", "review", "review:", "1:1", "1-1"))
            time_sinks.append({
                "summary":      summary,
                "weekday":      day,
                "hour":         hour,
                "occurrences":  info["count"],
                "avg_attendees": avg_att,
                "agenda_signal": has_agenda,
            })
    time_sinks.sort(key=lambda x: (x["avg_attendees"], -x["occurrences"]))

    # Weekly rollup (ISO week)
    by_week = defaultdict(list)
    for d in daily:
        iso_year, iso_week, _ = d["date"].split("-")[:3]
        # Simple Sunday-bucketed week — sufficient for trend
        week_key = _week_bucket(d["date"])
        by_week[week_key].append(d)
    weekly = []
    for wk, days in sorted(by_week.items()):
        weekly.append({
            "week_start":          wk,
            "workdays":            len(days),
            "total_meeting_min":   sum(d["meeting_min"] for d in days),
            "avg_meeting_pct":     round(sum(d["meeting_pct"] for d in days) / max(1, len(days)), 1),
            "avg_fragmentation":   round(sum(d["fragmentation"] for d in days) / max(1, len(days)), 1),
            "total_focus_min":     sum(d["focus_min_total"] for d in days),
            "no_meeting_days":     sum(1 for d in days if d["n_meetings"] == 0),
        })

    summary = {
        "total_events":        len(events_raw),
        "workdays_analyzed":   len(daily),
        "avg_meeting_pct":     round(sum(d["meeting_pct"] for d in daily) / max(1, len(daily)), 1),
        "avg_fragmentation":   round(sum(d["fragmentation"] for d in daily) / max(1, len(daily)), 1),
        "no_meeting_days":     sum(1 for d in daily if d["n_meetings"] == 0),
        "best_focus_weekday":  min(heatmap, key=lambda x: x["avg_meeting_pct"])["weekday"] if heatmap else None,
    }
    return {
        "summary":          summary,
        "daily":            daily,
        "weekly":           weekly,
        "weekday_heatmap":  heatmap,
        "recurring_time_sinks": time_sinks[:15],
    }


def _verdict(pct: float) -> str:
    if pct < NO_MEETING_THRESHOLD_PCT:
        return "focus-day"
    if pct >= 50:
        return "overloaded"
    return "mixed"


def _week_bucket(date_str: str) -> str:
    d = datetime.fromisoformat(date_str)
    monday = d - timedelta(days=d.weekday())
    return monday.date().isoformat()


def render_report(metrics: dict, period_label: str = "the analyzed window") -> str:
    """Render a Markdown report from the metrics dict."""
    s = metrics["summary"]
    h = metrics["weekday_heatmap"]
    ts = metrics.get("recurring_time_sinks", [])
    lines = []
    lines.append(f"# 📅 Calendar Optimizer Report — {period_label}\n")
    lines.append(f"- Workdays analyzed: **{s['workdays_analyzed']}**")
    lines.append(f"- Total events: **{s['total_events']}**")
    lines.append(f"- Avg % of work week in meetings: **{s['avg_meeting_pct']}%**")
    lines.append(f"- Avg fragmentation score: **{s['avg_fragmentation']}** context switches/day")
    lines.append(f"- No-meeting days found: **{s['no_meeting_days']}**")
    lines.append(f"- Best-focus weekday: **{s['best_focus_weekday']}**")
    lines.append("")
    lines.append("## Day-of-week heat map\n")
    lines.append("| Day | Avg Meeting % | Avg Focus min/day | Verdict |")
    lines.append("|-----|--------------:|------------------:|---------|")
    for row in h:
        lines.append(f"| {row['weekday']} | {row['avg_meeting_pct']}% | {row['avg_focus_min']} | {row['verdict']} |")
    lines.append("")
    if ts:
        lines.append("## Recurring meetings (potential time sinks)\n")
        lines.append("| Meeting | Weekday | Hour | Occurrences | Avg attendees | Agenda signal |")
        lines.append("|---------|---------|-----:|------------:|--------------:|---------------|")
        for m in ts:
            lines.append(f"| {m['summary'][:40]} | {m['weekday']} | {m['hour']:02d}:00 | {m['occurrences']} | {m['avg_attendees']} | {'yes' if m['agenda_signal'] else 'no'} |")
        lines.append("")
    lines.append("## Daily breakdown\n")
    lines.append("| Date | Weekday | Meetings | Meeting % | Fragmentation | Focus min |")
    lines.append("|------|---------|---------:|----------:|--------------:|----------:|")
    for d in metrics["daily"]:
        lines.append(f"| {d['date']} | {d['weekday']} | {d['n_meetings']} | {d['meeting_pct']}% | {d['fragmentation']} | {d['focus_min_total']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    p = argparse.ArgumentParser(description="Calendar Optimizer metrics")
    p.add_argument("events_json", help="Path to events JSON (output of parse_ics.py)")
    p.add_argument("--report", help="Write a Markdown report to this path")
    p.add_argument("--label", default="analyzed window", help="Period label for the report header")
    args = p.parse_args()

    raw = json.loads(Path(args.events_json).read_text(encoding="utf-8"))
    metrics = compute_metrics(raw)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    if args.report:
        md = render_report(metrics, period_label=args.label)
        Path(args.report).write_text(md, encoding="utf-8")
        print(f"\n[REPORT] {args.report}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
