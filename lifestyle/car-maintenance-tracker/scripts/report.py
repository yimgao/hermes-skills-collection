#!/usr/bin/env python3
"""report.py — Upcoming due dates, cost-per-mile, MPG, and warranty reports.

Pure stdlib. No external deps. Reads JSON from ~/.hermes/cars/<vehicle>/ and
emits a printable summary.

Examples:
    python scripts/report.py --upcoming --days 60
    python scripts/report.py --car civic-2018 --cost-per-mile
    python scripts/report.py --car civic-2018 --mpg-trend --last 6
    python scripts/report.py --warranty-watch --days 90
    python scripts/report.py --car civic-2018 --annual-cost 2026
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable

ROOT = Path("~/.hermes/cars").expanduser()
TODAY = date.today()


# ---------- helpers ----------

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


def _iso(d: date | datetime) -> str:
    return d.isoformat() if isinstance(d, date) else d.date().isoformat()


def _months(n: int) -> timedelta:
    return timedelta(days=int(n * 30.4375))


def _status(days: int, miles: int) -> str:
    if days < 0 or miles < 0:
        return "🔴 overdue"
    if days <= 30 or miles <= 1000:
        return "🟡 due_soon"
    return "🟢 upcoming"


# ---------- upcoming ----------

@dataclass
class DueItem:
    vehicle: str
    key: str
    label: str
    category: str
    due_date: date | None
    due_mileage: int | None
    days: int | None
    miles: int | None
    status: str
    state_specific: bool


def upcoming_for(vid: str, days: int, current_miles: int) -> list[DueItem]:
    prof = _load(vid, "profile.json") or {}
    sch = _load(vid, "schedule.json") or {}
    evs = _events(vid)
    last = current_miles or prof.get("current_odometer", 0)
    out: list[DueItem] = []

    for s in sch.get("services", []):
        # find last logged event of this type
        relevant = [
            e for e in evs
            if e.get("type") == s["key"] and "odometer" in e
        ]
        last_event = relevant[-1] if relevant else None

        # compute next due
        nd_date = None
        nd_miles = None
        last_date = None
        last_mile = None

        if last_event:
            try:
                last_date = datetime.fromisoformat(
                    last_event["ts"].replace("Z", "+00:00")
                ).date()
            except Exception:
                last_date = None
            last_mile = last_event.get("odometer")

        # also allow explicit due date overrides (e.g., registration paid)
        override_path = ROOT / vid / f"override_{s['key']}.json"
        if override_path.exists():
            ov = json.loads(override_path.read_text())
            if ov.get("due_date"):
                try:
                    nd_date = datetime.fromisoformat(ov["due_date"]).date()
                except Exception:
                    pass
            if ov.get("due_mileage"):
                nd_miles = int(ov["due_mileage"])

        # date-based cadence
        if nd_date is None and s["trigger"] in {"date", "mi-or-date"}:
            if last_date and s.get("every_months"):
                nd_date = last_date + _months(s["every_months"])

        # mileage-based cadence
        if nd_miles is None and s["trigger"] in {"mi", "mi-or-date"}:
            if last_mile is not None and s.get("every_miles"):
                nd_miles = int(last_mile + s["every_miles"])

        # bucket
        days_to_due = (nd_date - TODAY).days if nd_date else None
        miles_to_due = (nd_miles - last) if nd_miles else None
        status = _status(days_to_due if days_to_due is not None else 9999,
                         miles_to_due if miles_to_due is not None else 9999)

        # filter to within window
        if days_to_due is not None and days_to_due > days:
            continue
        if miles_to_due is not None and miles_to_due > 1000 and days_to_due is None:
            continue

        out.append(DueItem(
            vehicle=prof.get("nickname", vid),
            key=s["key"],
            label=s["label"],
            category=s.get("category", ""),
            due_date=nd_date,
            due_mileage=nd_miles,
            days=days_to_due,
            miles=miles_to_due,
            status=status,
            state_specific=s.get("state_specific", False),
        ))
    return out


def cmd_upcoming(args) -> int:
    vehicles = [args.car] if args.car else sorted(
        d.name for d in ROOT.iterdir() if d.is_dir()
    )
    items: list[DueItem] = []
    for vid in vehicles:
        try:
            items.extend(upcoming_for(vid, args.days, 0))
        except Exception as e:
            print(f"  [WARN] skipping {vid}: {e}", file=sys.stderr)

    items.sort(key=lambda i: (
        {"🔴 overdue": 0, "🟡 due_soon": 1, "🟢 upcoming": 2}[i.status],
        i.days if i.days is not None else 9999,
        i.miles if i.miles is not None else 999999,
    ))

    print(f"\nUpcoming in next {args.days} days across {len(vehicles)} vehicle(s):\n")
    if not items:
        print("  (none due in window — all clear)")
        return 0
    print(f"  {'Vehicle':<14} {'Item':<26} {'Due Date':<12} "
          f"{'Due Mi':>9}  {'Days':>6}  {'Status'}")
    print(f"  {'-' * 14} {'-' * 26} {'-' * 12} {'-' * 9}  {'-' * 6}  {'-' * 12}")
    for it in items:
        dd = it.due_date.isoformat() if it.due_date else "—"
        dm = f"{it.due_mileage:,}" if it.due_mileage else "—"
        dn = f"{it.days}" if it.days is not None else "—"
        flag = " ⚠" if it.state_specific else ""
        print(f"  {it.vehicle:<14} {it.label:<26} {dd:<12} {dm:>9}  "
              f"{dn:>6}  {it.status}{flag}")
    return 0


# ---------- cost per mile ----------

def cmd_cost_per_mile(args) -> int:
    vid = args.car
    if not vid:
        print("[ERROR] --car required", file=sys.stderr)
        return 2
    prof = _load(vid, "profile.json") or {}
    purchase = prof.get("purchase_price", 0)
    evs = _events(vid)
    current = prof.get("current_odometer", 0)
    # min odometer for lifetime miles
    odo_events = [e for e in evs if "odometer" in e]
    start = min((e["odometer"] for e in odo_events), default=current)
    miles = max(current - start, 1)
    maint_cost = sum(e.get("total_cost", 0) for e in evs
                     if e.get("type") not in {"fuel", "fillup"})
    fuel_cost = sum(e.get("total_cost", 0) for e in evs
                    if e.get("type") in {"fuel", "fillup"})
    total = purchase + maint_cost + fuel_cost
    cpm = total / miles
    print(f"\n  Vehicle: {prof.get('nickname', vid)} ({prof.get('year')} "
          f"{prof.get('make')} {prof.get('model')})")
    print(f"  Period:  {start:,} → {current:,} mi  ({miles:,} mi logged)")
    print(f"  ---")
    print(f"  Purchase:        ${purchase:>9,.2f}")
    print(f"  Maintenance:     ${maint_cost:>9,.2f}")
    print(f"  Fuel:            ${fuel_cost:>9,.2f}")
    print(f"  TOTAL:           ${total:>9,.2f}")
    print(f"  ---")
    print(f"  Cost / mile:     ${cpm:>9.4f}/mi")
    print(f"  Cost / month*:   ${(maint_cost + fuel_cost) / max(((date.today().year - prof.get('purchase_year', date.today().year)) * 12 + 1), 1):>9,.2f}/mo")
    print(f"\n  * Monthly figure = maint+fuel divided by months since purchase.")
    print(f"  For used vehicles with backfilled history, divide by logged years instead.")
    return 0


# ---------- MPG trend ----------

def cmd_mpg_trend(args) -> int:
    vid = args.car
    if not vid:
        print("[ERROR] --car required", file=sys.stderr)
        return 2
    prof = _load(vid, "profile.json") or {}
    evs = _events(vid)
    fills = [e for e in evs if e.get("type") in {"fuel", "fillup"}
             and "gallons" in e and "miles_since_last" in e]
    if not fills:
        print(f"  [WARN] no fill-up records found for {vid}; need type=fuel, "
              f"gallons, miles_since_last")
        return 1

    # last N fills
    n = args.last if args.last else len(fills)
    fills = fills[-n:]

    mpgs = [e["miles_since_last"] / e["gallons"] for e in fills]
    unit = prof.get("fuel_economy_unit", "mpg")

    print(f"\n  Vehicle: {prof.get('nickname', vid)}")
    print(f"  Window:  last {len(fills)} fill-ups")
    print(f"  ---")
    print(f"  Min MPG:    {min(mpgs):.1f} {unit}")
    print(f"  Avg MPG:    {statistics.mean(mpgs):.1f} {unit}")
    print(f"  Max MPG:    {max(mpgs):.1f} {unit}")
    if len(mpgs) >= 2:
        print(f"  Stddev:     {statistics.stdev(mpgs):.2f} {unit}")

    # anomaly detection: any single MPG drop > 15% vs trailing 5
    if len(mpgs) >= 6:
        anomalies = []
        for i in range(5, len(mpgs)):
            prev = statistics.mean(mpgs[i - 5:i])
            if mpgs[i] < prev * 0.85:
                anomalies.append((fills[i]["ts"], fills[i].get("gallons"),
                                  mpgs[i], prev))
        if anomalies:
            print(f"\n  ⚠ Anomalies detected (MPG drop >15% vs trailing 5-fill avg):")
            for a in anomalies:
                print(f"    {a[0]}: {a[2]:.1f} mpg  (avg before: {a[3]:.1f})")
        else:
            print(f"\n  ✓ No anomalies — fuel economy stable.")
    return 0


# ---------- annual cost ----------

def cmd_annual_cost(args) -> int:
    year = args.annual_cost
    vehicles = [args.car] if args.car else sorted(
        d.name for d in ROOT.iterdir() if d.is_dir()
    )

    by_cat: dict[str, float] = {}
    by_veh: dict[str, float] = {}
    total = 0.0

    for vid in vehicles:
        evs = _events(vid)
        v_total = 0.0
        for e in evs:
            try:
                ts_year = datetime.fromisoformat(
                    e["ts"].replace("Z", "+00:00")
                ).year
            except Exception:
                continue
            if ts_year != year:
                continue
            cat = e.get("category", "misc")
            cost = e.get("total_cost", 0)
            by_cat[cat] = by_cat.get(cat, 0) + cost
            v_total += cost
        by_veh[vid] = v_total
        total += v_total

    print(f"\n  Annual cost report — {year}")
    print(f"  ---")
    print(f"  By vehicle:")
    for v, c in sorted(by_veh.items(), key=lambda x: -x[1]):
        print(f"    {v:<24} ${c:>9,.2f}")
    print(f"\n  By category:")
    for c, amt in sorted(by_cat.items(), key=lambda x: -x[1]):
        print(f"    {c:<24} ${amt:>9,.2f}")
    print(f"  ---")
    print(f"  TOTAL: ${total:,.2f}")
    return 0


# ---------- warranty watch ----------

def cmd_warranty_watch(args) -> int:
    vehicles = [args.car] if args.car else sorted(
        d.name for d in ROOT.iterdir() if d.is_dir()
    )
    cutoff = TODAY + timedelta(days=args.days)
    print(f"\n  Warranties expiring within {args.days} days (before {cutoff}):\n")
    found = False
    for vid in vehicles:
        prof = _load(vid, "profile.json") or {}
        for w in prof.get("warranties", []):
            end = w.get("end_date")
            if not end:
                continue
            try:
                ed = datetime.fromisoformat(end).date()
            except Exception:
                continue
            if ed <= cutoff:
                days_left = (ed - TODAY).days
                flag = "🔴 EXPIRED" if days_left < 0 else "🟡"
                print(f"  {flag} {prof.get('nickname', vid):<14} "
                      f"{w.get('type', '?'):<24} expires {ed}  "
                      f"({days_left} d)")
                found = True
    if not found:
        print("  (none)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default="~/.hermes/cars",
                   help="car data root (default: ~/.hermes/cars)")
    p.add_argument("--car", help="single vehicle id")
    p.add_argument("--upcoming", action="store_true")
    p.add_argument("--days", type=int, default=60)
    p.add_argument("--cost-per-mile", action="store_true")
    p.add_argument("--mpg-trend", action="store_true")
    p.add_argument("--last", type=int, default=10,
                   help="last N fills for mpg trend")
    p.add_argument("--annual-cost", type=int, help="year for annual cost report")
    p.add_argument("--warranty-watch", action="store_true")
    args = p.parse_args()

    global ROOT
    ROOT = Path(args.root).expanduser()

    if args.upcoming:
        return cmd_upcoming(args)
    if args.cost_per_mile:
        return cmd_cost_per_mile(args)
    if args.mpg_trend:
        return cmd_mpg_trend(args)
    if args.annual_cost:
        return cmd_annual_cost(args)
    if args.warranty_watch:
        return cmd_warranty_watch(args)
    p.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())