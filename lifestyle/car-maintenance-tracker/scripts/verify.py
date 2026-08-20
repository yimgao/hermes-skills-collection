#!/usr/bin/env python3
"""verify.py — Sanity-check the car-maintenance-tracker data tree.

Walks every vehicle directory under --root, validates profile.json, schedule.json,
and log.jsonl. Reports missing files, malformed JSON, schema violations, and
likely-data issues (negative odometer, odometer rollback, etc).

Exit code 0 = clean, 1 = warnings only, 2 = errors found.

Usage:
    python scripts/verify.py --root ~/.hermes/cars
    python scripts/verify.py --root ~/.hermes/cars --car civic-2018
    python scripts/verify.py --root ~/.hermes/cars --strict
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

REQUIRED_PROFILE_FIELDS = {"vehicle_id", "year", "make", "model", "current_odometer"}
REQUIRED_LOG_FIELDS = {"ts", "type", "odometer"}

CATEGORY_KEYS = {
    "fluids", "tires", "brakes", "filters", "ignition",
    "electrical", "consumables", "calendar", "repairs",
}


def err(msg: str) -> None:
    print(f"  [ERROR] {msg}")


def warn(msg: str) -> None:
    print(f"  [WARN]  {msg}")


def ok(msg: str) -> None:
    print(f"  [OK]    {msg}")


def verify_profile(profile: dict, path: Path) -> list[str]:
    issues = []
    missing = REQUIRED_PROFILE_FIELDS - profile.keys()
    if missing:
        issues.append(f"missing required fields: {sorted(missing)}")
    if profile.get("year", 0) < 1900 or profile.get("year", 0) > date.today().year + 1:
        issues.append(f"year looks wrong: {profile.get('year')}")
    odo = profile.get("current_odometer", 0)
    if not isinstance(odo, (int, float)) or odo < 0:
        issues.append(f"current_odometer invalid: {odo}")
    if profile.get("vehicle_id") != path.parent.name:
        issues.append(
            f"vehicle_id '{profile.get('vehicle_id')}' doesn't match directory "
            f"'{path.parent.name}'"
        )
    return issues


def verify_schedule(schedule: dict, path: Path) -> list[str]:
    issues = []
    if "services" not in schedule:
        issues.append("missing 'services' array")
        return issues
    for s in schedule["services"]:
        if "key" not in s or "trigger" not in s:
            issues.append(f"service missing key/trigger: {s}")
            continue
        trig = s["trigger"]
        if trig not in {"mi", "date", "mi-or-date"}:
            issues.append(f"service {s.get('key')}: invalid trigger '{trig}'")
        if trig in {"mi", "mi-or-date"} and not s.get("every_miles"):
            issues.append(f"service {s.get('key')}: mi-trigger but no every_miles")
        if trig in {"date", "mi-or-date"} and not s.get("every_months"):
            issues.append(f"service {s.get('key')}: date-trigger but no every_months")
        if s.get("category") not in CATEGORY_KEYS:
            issues.append(
                f"service {s.get('key')}: unknown category '{s.get('category')}'"
            )
    return issues


def verify_log(log_path: Path) -> list[str]:
    issues = []
    if not log_path.exists():
        issues.append("log.jsonl missing (vehicle has no logged events yet)")
        return issues
    seen_ts = []
    seen_odo = []
    for lineno, line in enumerate(log_path.read_text().splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError as e:
            issues.append(f"line {lineno}: invalid JSON ({e.msg})")
            continue
        missing = REQUIRED_LOG_FIELDS - ev.keys()
        if missing:
            issues.append(f"line {lineno}: missing required fields {sorted(missing)}")
        if "odometer" in ev and not isinstance(ev["odometer"], (int, float)):
            issues.append(f"line {lineno}: odometer must be numeric")
        try:
            datetime.fromisoformat(ev.get("ts", "").replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            issues.append(f"line {lineno}: ts not ISO-8601: {ev.get('ts')}")
        seen_ts.append(ev.get("ts"))
        seen_odo.append(ev.get("odometer", 0))
    # Check for odometer rollback
    for i in range(1, len(seen_odo)):
        if seen_odo[i] < seen_odo[i - 1] - 100:
            issues.append(
                f"odometer rollback at line {i + 1}: "
                f"{seen_odo[i - 1]} -> {seen_odo[i]}"
            )
    # Check for future timestamps
    today = datetime.now().isoformat()
    for i, ts in enumerate(seen_ts):
        if ts and ts > today:
            issues.append(f"line {i + 1}: future timestamp {ts}")
    return issues


def verify_vehicle(root: Path, vehicle_id: str, strict: bool) -> int:
    print(f"\nVehicle: {vehicle_id}")
    vroot = root / vehicle_id
    if not vroot.is_dir():
        err(f"directory not found: {vroot}")
        return 1

    profile_path = vroot / "profile.json"
    schedule_path = vroot / "schedule.json"
    log_path = vroot / "log.jsonl"

    errors = 0
    warnings = 0

    if not profile_path.exists():
        err(f"profile.json missing at {profile_path}")
        errors += 1
    else:
        try:
            prof = json.loads(profile_path.read_text())
            issues = verify_profile(prof, profile_path)
            if issues:
                for i in issues:
                    if strict:
                        err(i); errors += 1
                    else:
                        warn(i); warnings += 1
            else:
                ok("profile.json valid")
        except json.JSONDecodeError as e:
            err(f"profile.json malformed: {e}")
            errors += 1

    if not schedule_path.exists():
        warn("schedule.json missing — using default intervals from references/")
        warnings += 1
    else:
        try:
            sch = json.loads(schedule_path.read_text())
            issues = verify_schedule(sch, schedule_path)
            if issues:
                for i in issues:
                    if strict:
                        err(i); errors += 1
                    else:
                        warn(i); warnings += 1
            else:
                ok(f"schedule.json valid ({len(sch.get('services', []))} services)")
        except json.JSONDecodeError as e:
            err(f"schedule.json malformed: {e}")
            errors += 1

    issues = verify_log(log_path)
    if issues:
        for i in issues:
            if "missing" in i.lower() and not strict:
                warn(i); warnings += 1
            else:
                err(i); errors += 1
    else:
        if log_path.exists():
            line_count = sum(1 for _ in log_path.open())
            ok(f"log.jsonl valid ({line_count} events)")
        else:
            warn("log.jsonl missing (no events yet)")

    if errors:
        err(f"{vehicle_id}: {errors} error(s), {warnings} warning(s)")
    elif warnings:
        warn(f"{vehicle_id}: {warnings} warning(s)")
    else:
        ok(f"{vehicle_id}: clean")
    return errors


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default="~/.hermes/cars", help="car data root")
    p.add_argument("--car", help="verify only this vehicle id")
    p.add_argument("--strict", action="store_true",
                   help="treat warnings as errors")
    args = p.parse_args()

    root = Path(args.root).expanduser()
    if not root.is_dir():
        err(f"root not found: {root}")
        return 2

    if args.car:
        vehicles = [args.car]
    else:
        vehicles = sorted(d.name for d in root.iterdir() if d.is_dir())

    if not vehicles:
        warn(f"no vehicles registered under {root}")
        return 1

    total_errors = 0
    for vid in vehicles:
        total_errors += verify_vehicle(root, vid, args.strict)

    print()
    if total_errors:
        err(f"TOTAL: {total_errors} error(s) across {len(vehicles)} vehicle(s)")
        return 2
    ok(f"ALL CLEAN: {len(vehicles)} vehicle(s) verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())