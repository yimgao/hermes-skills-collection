#!/usr/bin/env python3
"""
gaps.py — Find what an insurance policy leaves you exposed to.

Compares a policy's actual limits against the *worst realistic case* for
your situation and reports the shortfall in dollars, not adjectives.

Usage:
    python3 gaps.py policy.json --scenario scenario.json
    python3 gaps.py policy.json --auto --value 22000 --mileage 12000
    python3 gaps.py --presets          # list built-in exposure scenarios
    python3 gaps.py --check policy.json   # CI-style: exit 1 if any gap is CRITICAL

Pure stdlib. Local-first, no upload.

POLICY SCHEMA: same as the quote objects consumed by compare.py.
SCENARIO SCHEMA: same as compare.py's --scenario file.

The core idea: an insurance policy is a set of promises capped at a number.
Most people never check whether the cap is above their actual exposure.
This script does the arithmetic for them.
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Exposure presets: the plausible worst cases, with rough cost anchors.
# ---------------------------------------------------------------------------

PRESETS: Dict[str, Dict[str, Any]] = {
    "auto_liability": {
        "label": "Auto — serious at-fault injury",
        "story": "You cause a crash. The other driver has a spinal injury, "
                 "needs surgery, and sues. Their car is wrecked too.",
        "product": "auto",
        "losses": {
            "liability_per_person": 250000,
            "liability_per_accident": 500000,
            "property_damage": 60000,
            "medical_pay": 15000,
        },
        "note": "Multi-vehicle pileup: the per-accident limit is what matters, "
                "not the per-person one.",
    },
    "auto_theft": {
        "label": "Auto — total theft",
        "story": "Your car is stolen and never recovered.",
        "product": "auto",
        "losses": {"comprehensive": 25000, "collision": 25000},
        "note": "Also check: is the theft of items *in* the car covered?",
    },
    "auto_weather": {
        "label": "Auto — total loss to weather",
        "story": "Hail or flood destroys the car beyond repair.",
        "product": "auto",
        "losses": {"comprehensive": 25000, "collision": 25000},
        "note": "Comprehensive, not collision. Confirm flood is not excluded.",
    },
    "home_fire": {
        "label": "Home — total loss to fire",
        "story": "A kitchen fire destroys the house.",
        "product": "home",
        "losses": {"property_damage": 450000, "loss_of_use": 60000,
                   "personal_property": 150000, "liability_per_person": 100000},
        "note": "Dwelling (A) must be replacement cost, not market value.",
    },
    "home_water": {
        "label": "Home — water damage",
        "story": "A supply line bursts while you're on a trip.",
        "product": "home",
        "losses": {"property_damage": 80000, "loss_of_use": 25000,
                   "personal_property": 40000},
        "note": "Often excluded if the home was vacant >30 days (water backup).",
    },
    "home_liability": {
        "label": "Home — guest is badly injured",
        "story": "A guest falls off a step and sues.",
        "product": "home",
        "losses": {"liability_per_person": 500000, "liability_per_accident": 1000000,
                   "medical_pay": 25000},
        "note": "This is the reason people buy an umbrella policy.",
    },
    "health_year": {
        "label": "Health — a bad year",
        "story": "One ER visit, one hospital stay, one specialist, four "
                 "prescriptions, monthly premiums.",
        "product": "health",
        "losses": {"emergency_room_copay": 1500, "hospital_admit_copay": 4000,
                   "specialist_copay": 600, "brand_rx": 2400,
                   "out_of_pocket_max": 12000},
        "note": "Compare your out-of-pocket max against a realistic annual "
                "cost, not the premium.",
    },
    "health_cancer": {
        "label": "Health — serious diagnosis",
        "story": "Cancer treatment: surgery, chemo, infusion, travel.",
        "product": "health",
        "losses": {"out_of_pocket_max": 40000, "brand_rx": 25000,
                   "hospital_admit_copay": 8000, "specialist_copay": 2000},
        "note": "Also: is your specialist in-network? Out-of-network cost "
                "bypasses the out-of-pocket max under many plans.",
    },
    "pet_surgery": {
        "label": "Pet — major surgery",
        "story": "ACL repair on a dog, plus a year of follow-ups.",
        "product": "pet",
        "losses": {"accident_limit": 8000, "annual_max": 16000, "deductible": 250},
        "note": "Check whether the annual max is per condition or per policy year.",
    },
    "disability": {
        "label": "Disability — two years unable to work",
        "story": "You can't work for 24 months after a back injury.",
        "product": "disability",
        "losses": {"monthly_benefit": 120000, "benefit_period": 1},
        "note": "The benefit period matters more than the monthly amount. "
                "'2 years' vs 'to age 65' is the whole game.",
    },
    "life_dependent": {
        "label": "Life — dependents left behind",
        "story": "Your partner and two children lose your income.",
        "product": "life",
        "losses": {"death_benefit": 700000},
        "note": "Common rule of thumb: 10x annual income, or 5x + largest "
                "liability (mortgage).",
    },
}

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "OK": 4}

# How far below the need is a "critical" gap vs a "low" gap.
SEVERITY_BANDS = [
    ("CRITICAL", 1.00),   # covers < 25% of the need
    ("HIGH", 0.60),       # covers < 50%
    ("MEDIUM", 0.25),     # covers < 75%
    ("LOW", 0.00),        # covers < 100%
]


def band_for(have: Optional[float], need: float) -> str:
    if have is None:
        return "CRITICAL"
    ratio = have / need if need else 1.0
    for name, threshold in SEVERITY_BANDS:
        if ratio < threshold:
            return name
    return "OK"


def money(v: Optional[float]) -> str:
    if v is None:
        return "none"
    return f"${v:,.0f}"


def run(policy: Dict[str, Any], scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
    limits = dict(policy.get("limits", {}) or {})
    if policy.get("deductible") is not None and "deductible" not in limits:
        limits["deductible"] = policy.get("deductible")
    features = policy.get("features", {}) or {}

    losses = scenario.get("losses", {}) or {}
    product = scenario.get("product", policy.get("product", "auto"))

    rows = []
    for field, need in losses.items():
        have = limits.get(field)
        if isinstance(have, bool):
            have = 1.0 if have else 0.0
        have_f = float(have) if have is not None else None
        shortfall = None
        if have_f is not None:
            shortfall = max(0.0, float(need) - have_f)
        rows.append({
            "field": field,
            "need": float(need),
            "have": have_f,
            "shortfall": shortfall,
            "severity": band_for(have_f, float(need)),
            "pct_covered": (have_f / float(need) * 100) if (have_f is not None and need) else 0.0,
        })
    rows.sort(key=lambda r: (SEVERITY_ORDER.get(r["severity"], 9), -(r["shortfall"] or 0)))
    return rows


def print_report(policy: Dict[str, Any], scenario: Dict[str, Any], rows: List[Dict[str, Any]]) -> None:
    name = policy.get("carrier") or policy.get("id") or "Policy"
    print("=" * 78)
    print(f"COVERAGE GAPS — {name}")
    print(f"Scenario: {scenario.get('label', '(unnamed)')}")
    print("=" * 78)
    if scenario.get("story"):
        print(f"  {scenario['story']}")
    if scenario.get("note"):
        print(f"  >> {scenario['note']}")
    print()

    hdr = f"  {'COVER':34s} {'NEED':>12s} {'HAVE':>12s} {'SHORT':>12s}  SEV"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for r in rows:
        sev = r["severity"]
        mark = {"CRITICAL": "!!", "HIGH": " !", "MEDIUM": " ~", "LOW": " .", "OK": ""}[sev]
        print(f"  {r['field']:34s} {money(r['need']):>12s} {money(r['have']):>12s} "
              f"{money(r['shortfall']):>12s}  {sev}{mark}")
    print()

    crit = [r for r in rows if r["severity"] == "CRITICAL"]
    highs = [r for r in rows if r["severity"] == "HIGH"]
    if crit:
        print("CRITICAL GAPS — you are exposed to the full amount.")
        for r in crit:
            print(f"  * {r['field']}: {money(r['shortfall'])} of a {money(r['need'])} loss "
                  f"is on you.")
        print()
    if highs:
        print("HIGH GAPS — mostly covered, but a serious event would still hurt.")
        for r in highs:
            print(f"  * {r['field']}: {money(r['shortfall'])} short.")
        print()

    total_short = sum(r["shortfall"] or 0 for r in rows if r["severity"] in ("CRITICAL", "HIGH"))
    if total_short:
        print(f"TOTAL EXPOSURE across the flagged items: {money(total_short)}")
        print()


def auto_scenario(policy: Dict[str, Any], value: float, mileage: int) -> Dict[str, Any]:
    """Build a rough auto scenario from vehicle value and annual mileage."""
    losses = {
        "liability_per_person": 250000,
        "liability_per_accident": 500000,
        "property_damage": 60000,
        "medical_pay": 15000,
        "comprehensive": value,
        "collision": value,
    }
    if mileage > 15000:
        losses["liability_per_accident"] = 1000000
    return {
        "label": f"Auto — 1 driver, ${value:,.0f} vehicle, {mileage:,} mi/yr",
        "story": "Baseline worst case: a serious at-fault injury plus a total loss of the vehicle.",
        "product": "auto",
        "losses": losses,
        "note": "Raise the liability numbers if you drive in a high-liability state "
                "(CA, NY, FL, MI) or carry passengers professionally.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Find what an insurance policy leaves you exposed to.")
    ap.add_argument("policy", nargs="?", help="Path to policy JSON (same schema as compare.py quotes)")
    ap.add_argument("--scenario", help="Path to scenario JSON")
    ap.add_argument("--preset", help=f"Use a built-in preset: {', '.join(PRESETS)}")
    ap.add_argument("--auto", action="store_true", help="Auto scenario: --value + --mileage")
    ap.add_argument("--value", type=float, default=25000, help="Vehicle value for --auto")
    ap.add_argument("--mileage", type=int, default=12000, help="Annual mileage for --auto")
    ap.add_argument("--presets", action="store_true", help="List built-in scenarios and exit")
    ap.add_argument("--check", action="store_true",
                    help="CI mode: exit 1 if any gap is CRITICAL or HIGH")
    args = ap.parse_args()

    if args.presets:
        print("BUILT-IN EXPOSURE SCENARIOS")
        for key, p in PRESETS.items():
            print(f"\n  {key}")
            print(f"    {p['label']}")
            print(f"    {p['story']}")
            for f, v in p["losses"].items():
                print(f"      {f:28s} {money(v)}")
            if p.get("note"):
                print(f"    note: {p['note']}")
        return 0

    if not args.policy:
        print("[ERROR] Pass a policy JSON path (see --help).", file=sys.stderr)
        return 2

    try:
        with open(args.policy, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as e:
        print(f"[ERROR] Cannot read {args.policy}: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {args.policy}: {e}", file=sys.stderr)
        return 2

    policy = data
    if isinstance(data, dict) and "quotes" in data:
        quotes = data["quotes"]
        policy = quotes[0] if quotes else {}
        print(f"[INFO] Using first of {len(quotes)} quotes in file.", file=sys.stderr)
    elif isinstance(data, list) and data:
        policy = data[0]

    scenario: Dict[str, Any]
    if args.preset:
        if args.preset not in PRESETS:
            print(f"[ERROR] Unknown preset '{args.preset}'. Use --presets to list.", file=sys.stderr)
            return 2
        scenario = PRESETS[args.preset]
    elif args.auto:
        scenario = auto_scenario(policy, args.value, args.mileage)
    elif args.scenario:
        try:
            with open(args.scenario, "r", encoding="utf-8") as fh:
                scenario = json.load(fh)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[ERROR] Cannot read scenario: {e}", file=sys.stderr)
            return 2
    else:
        print("[ERROR] Need one of --preset, --auto, or --scenario.", file=sys.stderr)
        return 2

    rows = run(policy, scenario)
    print_report(policy, scenario, rows)

    if args.check:
        bad = [r for r in rows if r["severity"] in ("CRITICAL", "HIGH")]
        if bad:
            print(f"[FAIL] {len(bad)} material coverage gap(s) found.")
            return 1
        print("[PASS] No critical or high coverage gaps in this scenario.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
