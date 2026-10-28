#!/usr/bin/env python3
"""
compare.py — Compare insurance quotes / plans on equal footing.

Usage:
    python3 compare.py quotes.json [--scenario scenario.json] [--weights weights.json]
    python3 compare.py quotes.json --fields            # print the field dictionary
    python3 compare.py quotes.json --explain "plan A"

Pure stdlib. Reads JSON, prints a comparison table + normalized ranking.
No network. No upload.

QUOTE SCHEMA (one object per candidate):
{
  "id": "quote-geico-01",
  "carrier": "GEICO",
  "product": "auto",                 # auto | home | renters | health | life | disability | pet | umbrella | gear
  "annual_premium": 1420.00,
  "currency": "USD",
  "deductible": 500,                 # per claim (auto/home) or annual (health)
  "limits": {
    "liability_per_person": 100000,
    "liability_per_accident": 300000,
    "property_damage": 300000,
    "medical_pay": 5000,
    "collision": 25000,
    "comprehensive": 25000,
    "uninsured_motorist": 100000,
    "personal_property": 250000,
    "loss_of_use": 50000,
    "medical_payoff": 300000
  },
  "features": {
    "rental_reimbursement": true,
    "roadside_assistance": true,
    "gap_cover": true,
    "accident_forgiveness": false,
    "new_car_replacement": false,
    "pet_injury_liability": false
  },
  "deductibles_available": [250, 500, 1000],
  "notes": "paperless discount applied"
}

SCENARIO SCHEMA (optional, drives the "would this actually cover me" analysis):
{
  "label": "single driver, urban, 2021 Civic",
  "risk_profile": {
    "auto": {
      "drivers": 1,
      "vehicles": [{"value": 22000, "year": 2021, "use": "commute"}],
      "annual_miles": 12000,
      "at_fault_claims_last_5y": 0,
      "has_students": false
    },
    "home": {
      "home_value": 480000,
      "year_built": 1998,
      "roof_age_years": 12,
      "construction": "frame",
      "distance_to_fire_hydrant_ft": 400
    }
  },
  "worst_case_losses": [        # hypothetical claims to test against limits
    {"label": "rear-end, one injured other driver", "auto": {"liability_per_person": 250000, "property_damage": 60000, "medical_pay": 15000}},
    {"label": "kitchen fire, total loss of home", "home": {"property_damage": 480000, "loss_of_use": 80000}}
  ],
  "known_health_conditions": ["asthma"],
  "prescription_count": 2,
  "current_provider": "Blue Shield PPO"
}
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Canonical field registry — what matters per product, and how to score it.
# ---------------------------------------------------------------------------

FIELDS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "auto": {
        "liability_per_person": {"label": "Bodily Injury / Person", "higher_better": True, "ideal": 300000,
                                 "why": "Max payout per injured person. State minimums are far too low."},
        "liability_per_accident": {"label": "Bodily Injury / Accident", "higher_better": True, "ideal": 500000,
                                   "why": "Max payout per accident (multiple people)."},
        "property_damage": {"label": "Property Damage", "higher_better": True, "ideal": 300000,
                             "why": "Damage to the other driver's car/property."},
        "medical_pay": {"label": "Medical Payments (MedPay)", "higher_better": True, "ideal": 10000,
                        "why": "Your own medical bills, regardless of fault."},
        "uninsured_motorist": {"label": "UM / UIM", "higher_better": True, "ideal": 300000,
                               "why": "When the other driver is uninsured or underinsured."},
        "collision": {"label": "Collision", "higher_better": True, "ideal": 50000,
                      "why": "Damage to YOUR car from a crash you caused."},
        "comprehensive": {"label": "Comprehensive", "higher_better": True, "ideal": 50000,
                          "why": "Your car: theft, hail, glass, animal strike."},
        "rental_reimbursement": {"label": "Rental Reimbursement", "higher_better": True, "ideal": 1,
                                  "why": "Car rental while your car is in the shop."},
    },
    "home": {
        "property_damage": {"label": "Dwelling Coverage (A)", "higher_better": True, "ideal": 1.0,
                             "why": "Rebuild cost of the structure (not market value)."},
        "loss_of_use": {"label": "Loss of Use (C)", "higher_better": True, "ideal": 50000,
                        "why": "Living expenses while the home is uninhabitable."},
        "personal_property": {"label": "Personal Property (F)", "higher_better": True, "ideal": 250000,
                              "why": "Your belongings — actual cash value unless RC specified."},
        "medical_pay": {"label": "Medical Payments", "higher_better": True, "ideal": 10000,
                        "why": "Liability for injuries to others on your property."},
        "liability_per_person": {"label": "Personal Liability (E)", "higher_better": True, "ideal": 1000000,
                                 "why": "Liability for a guest being hurt at your home."},
        "liability_per_accident": {"label": "Personal Liability — per accident", "higher_better": True, "ideal": 1000000,
                                   "why": "Aggregate cap on personal liability claims."},
    },
    "health": {
        "deductible": {"label": "Deductible", "higher_better": False, "ideal": 500,
                       "why": "What you pay before the plan starts paying."},
        "out_of_pocket_max": {"label": "Out-of-Pocket Max", "higher_better": False, "ideal": 3500,
                               "why": "The most you can pay in a year. Caps your worst case."},
        "coinsurance": {"label": "Coinsurance", "higher_better": False, "ideal": 0.1,
                        "why": "Your share after the deductible."},
        "primary_care_copay": {"label": "Primary Care Copay", "higher_better": False, "ideal": 20,
                               "why": "Per-visit cost for routine care."},
        "specialist_copay": {"label": "Specialist Copay", "higher_better": False, "ideal": 40,
                             "why": "Per-visit cost for specialists."},
        "emergency_room_copay": {"label": "ER Copay", "higher_better": False, "ideal": 150,
                                 "why": "ER visits are the most common surprise bill."},
        "hospital_admit_copay": {"label": "Hospital Admit", "higher_better": False, "ideal": 200,
                                 "why": "Inpatient admission copay."},
        "generic_rx": {"label": "Generic Rx (30-day)", "higher_better": False, "ideal": 10,
                       "why": "Cost of a common generic prescription."},
        "brand_rx": {"label": "Brand Rx (30-day)", "higher_better": False, "ideal": 50,
                     "why": "Cost of brand-name drugs — can be catastrophic."},
        "specialist_visits": {"label": "Specialist Visits (per year)", "higher_better": True, "ideal": 1,
                              "why": "HMO/EPO often cap these at 0."},
    },
    "life": {
        "death_benefit": {"label": "Death Benefit", "higher_better": True, "ideal": 500000,
                          "why": "The amount your beneficiaries receive."},
        "term_length_years": {"label": "Term Length (yrs)", "higher_better": True, "ideal": 20,
                              "why": "How long coverage lasts. Re-prices at renewal."},
        "convertible": {"label": "Convertible to permanent", "higher_better": True, "ideal": 1,
                        "why": "Lets you lock in a conversion window without a life exam."},
        "waiver_of_premium": {"label": "Waiver of Premium", "higher_better": True, "ideal": 1,
                              "why": "Premiums waived if you become disabled."},
    },
    "disability": {
        "monthly_benefit": {"label": "Monthly Benefit", "higher_better": True, "ideal": 5000,
                            "why": "Monthly cash payment while you can't work."},
        "benefit_period": {"label": "Benefit Period", "higher_better": True, "ideal": 1,
                           "why": "How long benefits last. 'To age 65' vs '2 years' is a huge gap."},
        "waiting_period_days": {"label": "Waiting Period (days)", "higher_better": False, "ideal": 30,
                                "why": "Days of disability before benefits start."},
        "residual_benefit": {"label": "Residual Benefit", "higher_better": True, "ideal": 1,
                             "why": "Partial benefits if you return to work part-time."},
    },
    "pet": {
        "accident_limit": {"label": "Accident Limit", "higher_better": True, "ideal": 10000,
                           "why": "Max payout per accident. Vet bills for a broken leg can hit $5k+."},
        "illness_limit": {"label": "Illness Limit", "higher_better": True, "ideal": 10000,
                          "why": "Max payout per illness period. Chronic conditions hit this."},
        "annual_max": {"label": "Annual Maximum", "higher_better": True, "ideal": 20000,
                       "why": "Total yearly ceiling across everything."},
        "deductible": {"label": "Deductible", "higher_better": False, "ideal": 100,
                       "why": "Per-policy-year deductible, applied once."},
        "rx_coverage": {"label": "Prescription Coverage", "higher_better": True, "ideal": 1,
                        "why": "Whether medications are covered at all."},
    },
    "umbrella": {
        "liability_per_person": {"label": "Liability / Person", "higher_better": True, "ideal": 1000000,
                                 "why": "Extra liability above your auto/home limits."},
        "liability_per_accident": {"label": "Liability / Accident", "higher_better": True, "ideal": 1000000,
                                   "why": "Aggregate cap per accident."},
    },
    "renters": {
        "personal_property": {"label": "Personal Property", "higher_better": True, "ideal": 30000,
                              "why": "Your belongings at risk."},
        "liability_per_person": {"label": "Personal Liability", "higher_better": True, "ideal": 300000,
                                 "why": "Liability for damage you cause to the landlord's unit."},
    },
    "gear": {
        "scheduled_equipment": {"label": "Scheduled Equipment", "higher_better": True, "ideal": 1,
                                "why": "Whether specific items are individually listed and covered."},
        "accident_limit": {"label": "Accident Limit", "higher_better": True, "ideal": 10000,
                           "why": "Per-accident ceiling for gear."},
        "deductible": {"label": "Deductible", "higher_better": False, "ideal": 100,
                       "why": "Applied per claim or per occurrence."},
    },
}

# Features that are nice-to-have toggles rather than numeric limits.
FEATURE_LABELS = {
    "rental_reimbursement": "Rental reimbursement",
    "roadside_assistance": "Roadside assistance",
    "gap_cover": "Gap cover (loan car)",
    "accident_forgiveness": "Accident forgiveness",
    "new_car_replacement": "New car replacement",
    "pet_injury_liability": "Pet injury liability",
    "customs_covered": "Customs covered (international)",
    "convertible": "Convertible to permanent",
    "waiver_of_premium": "Waiver of premium",
    "residual_benefit": "Residual benefit",
    "rx_coverage": "Rx coverage",
    "scheduled_equipment": "Scheduled equipment",
    "accident_forgiveness_disabled": "Accident forgiveness",
    "preexisting_waiver": "Pre-existing condition waiver",
}

# Hard red flags — these are not "trade-offs", they are disqualifiers.
RED_FLAGS = {
    "preexisting_conditions_excluded": "Pre-existing conditions explicitly excluded",
    "no_collision": "No collision coverage",
    "no_liability": "No liability coverage (or below state minimum)",
    "replacement_cost_disabled": "Dwelling covered at depreciated value instead of replacement cost",
    "below_state_minimum": "Liability limit below state minimum requirement",
    "no_ump": "No uninsured/underinsured motorist coverage",
    "excludes_theft_at_unattended_vehicle": "Theft excluded from unattended vehicles",
}

# Coverage floors worth flagging even if the number is above zero.
MIN_GUIDES = {
    "auto": {"liability_per_person": 100000, "liability_per_accident": 300000,
             "property_damage": 100000, "uninsured_motorist": 100000},
    "home": {"liability_per_person": 100000, "loss_of_use": 20000, "personal_property": 10000},
    "pet": {"accident_limit": 3000, "annual_max": 5000},
    "umbrella": {"liability_per_person": 1000000},
    "life": {"death_benefit": 100000},
}


def money(v: Any) -> Optional[float]:
    try:
        if v is None:
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def norm(v: Any) -> Optional[float]:
    """Normalize a limit field to a 0..1 'adequacy' score against the ideal."""
    m = money(v)
    if m is None:
        return None
    ideal = IDEAL_OVERRIDE.get(v, None)
    return m


# Ideal values are stored per-field in FIELDS; this map is populated at import time.
IDEAL_OVERRIDE: Dict[int, float] = {}


def _build_ideal_map() -> None:
    for product_fields in FIELDS.values():
        for spec in product_fields.values():
            IDEAL_OVERRIDE[id(spec)] = spec["ideal"]


_build_ideal_map()


def adequacy(field_spec: Dict[str, Any], value: Any) -> Optional[float]:
    """Map a raw field value to 0..1 adequacy (1 = meets/exceeds ideal)."""
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, str):
        return None
    m = money(value)
    if m is None:
        return None
    ideal = field_spec.get("ideal")
    if not ideal:
        return None
    if field_spec.get("higher_better", True):
        if ideal <= 1.0:
            # boolean-ish (already handled), or ratio-style
            return min(1.0, m / ideal) if ideal else None
        return min(1.0, m / ideal)
    # lower is better (deductible, copay) — invert so higher score = better
    if ideal <= 0:
        return None
    if m == 0:
        return 1.0
    return max(0.0, min(1.0, 1.0 - (m - ideal) / (ideal * 6)))


def product_fields_for(product: str) -> Dict[str, Dict[str, Any]]:
    return FIELDS.get(product, {})


def price_for(quote: Dict[str, Any]) -> Optional[float]:
    p = money(quote.get("annual_premium"))
    if p is not None:
        return p
    # monthly quotes are common; normalize
    m = money(quote.get("monthly_premium"))
    if m is not None:
        return m * 12
    return None


def score_quote(quote: Dict[str, Any], weights: Dict[str, float]) -> Dict[str, Any]:
    product = quote.get("product", "auto")
    fields = product_fields_for(product)
    limits = dict(quote.get("limits", {}) or {})
    # The top-level "deductible" belongs in the table when the product has a
    # deductible field (health, pet, gear).
    if quote.get("deductible") is not None and "deductible" not in limits:
        limits["deductible"] = quote.get("deductible")
    features = quote.get("features", {}) or {}
    redflags = quote.get("redflags", []) or []

    field_scores: Dict[str, Dict[str, Any]] = {}
    for key, spec in fields.items():
        raw = limits.get(key, features.get(key))
        a = adequacy(spec, raw)
        field_scores[key] = {"score": a, "raw": raw, "label": spec["label"], "why": spec["why"]}

    # feature bonus: toggles that are meaningful for the product
    feature_scores: Dict[str, Dict[str, Any]] = {}
    for key, label in FEATURE_LABELS.items():
        if key not in features:
            continue
        feature_scores[key] = {"on": bool(features[key]), "label": label}

    # weighted coverage score
    wsum = 0.0
    acc = 0.0
    for key, w in weights.items():
        if key not in field_scores:
            continue
        s = field_scores[key]["score"]
        if s is None:
            continue
        wsum += abs(w)
        acc += abs(w) * s
    coverage = (acc / wsum) if wsum else 0.0

    # feature multipliers: each useful feature gives a small lift, capped
    feat_bonus = 0.0
    for key, info in feature_scores.items():
        if info["on"]:
            feat_bonus += 0.02
    feat_bonus = min(feat_bonus, 0.10)

    price = price_for(quote)
    price_score = None
    if price is not None and price > 0:
        # normalize across the comparison set later; here use a rough inverse
        price_score = 1.0 / (1.0 + price / 1000.0)

    combined = coverage * 0.70 + feat_bonus
    if price_score is not None:
        combined = combined * 0.65 + price_score * 0.35

    flags = []
    for f in redflags:
        flags.append({"severity": "RED", "msg": RED_FLAGS.get(f, f)})
    for key, spec in fields.items():
        raw = limits.get(key)
        floor = MIN_GUIDES.get(product, {}).get(key)
        if floor and isinstance(raw, (int, float)) and raw < floor:
            flags.append({"severity": "AMBER",
                          "msg": f"{spec['label']} ${raw:,.0f} is below the recommended floor ${floor:,.0f}"})
    if price_score is None:
        flags.append({"severity": "AMBER", "msg": "No premium in the quote — cannot score price"})

    return {
        "id": quote.get("id"),
        "carrier": quote.get("carrier"),
        "product": product,
        "price": price,
        "coverage_score": round(coverage, 4),
        "combined_score": round(combined, 4),
        "field_scores": field_scores,
        "features": feature_scores,
        "flags": flags,
        "notes": quote.get("notes"),
    }


def default_weights(product: str) -> Dict[str, float]:
    """Baseline weights: coverage limits dominate, price is handled separately."""
    base = {
        "liability_per_person": 3.0,
        "liability_per_accident": 2.0,
        "property_damage": 1.5,
        "uninsured_motorist": 2.0,
        "medical_pay": 1.0,
        "collision": 1.5,
        "comprehensive": 1.5,
        "personal_property": 2.0,
        "loss_of_use": 1.5,
        "death_benefit": 3.0,
        "monthly_benefit": 3.0,
        "benefit_period": 2.0,
        "accident_limit": 2.0,
        "illness_limit": 2.0,
        "annual_max": 1.5,
        "out_of_pocket_max": 2.0,
        "coinsurance": 1.5,
        "primary_care_copay": 1.0,
        "specialist_copay": 1.0,
        "brand_rx": 1.5,
        "generic_rx": 1.0,
        "specialist_visits": 1.5,
    }
    if product == "health":
        # For health, low copays and network breadth matter more than raw limits.
        return {
            "out_of_pocket_max": 3.0,
            "deductible": 2.0,
            "coinsurance": 2.0,
            "primary_care_copay": 1.5,
            "specialist_copay": 1.5,
            "brand_rx": 2.0,
            "generic_rx": 1.5,
            "specialist_visits": 2.0,
        }
    return base


def normalize_price_scores(scored: List[Dict[str, Any]]) -> None:
    prices = [s["price"] for s in scored if s.get("price")]
    if not prices:
        return
    lo, hi = min(prices), max(prices)
    for s in scored:
        p = s.get("price")
        if p is None:
            continue
        if hi == lo:
            s["price_score"] = 1.0
        else:
            # lower price -> higher score
            s["price_score"] = round((hi - p) / (hi - lo), 4)
    for s in scored:
        if s.get("price_score") is None:
            s["combined_score"] = round(s["coverage_score"] * 0.75, 4)
        else:
            s["combined_score"] = round(s["coverage_score"] * 0.70 + s["price_score"] * 0.30, 4)


def fmt(v: Any) -> str:
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float) and 0 < v < 1:
        return f"{v * 100:.0f}%"
    if isinstance(v, (int, float)):
        return f"${v:,.0f}"
    return str(v)


def print_table(rows: List[Dict[str, Any]], product: str) -> None:
    fields = product_fields_for(product)
    cols = list(fields.keys())
    if not cols:
        cols = list(rows[0]["field_scores"].keys()) if rows else []

    name_w = max([len(str(r.get("carrier") or r.get("id"))) for r in rows] + [8]) + 2
    headers = ["PLAN", "PREM/yr"] + [fields[c]["label"][:18] for c in cols]
    # Width must fit the widest rendered cell, including the " !" warning marker.
    widths = [name_w, 10]
    for c in cols:
        w = len(headers[2 + cols.index(c)])
        for r in rows:
            fs = r["field_scores"].get(c, {})
            raw = fs.get("raw")
            txt = fmt(raw)
            if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                sc = fs.get("score")
                if sc is not None and sc < 0.5:
                    txt += " !"
            w = max(w, len(txt))
        widths.append(w + 2)

    line = "  ".join("-" * w for w in widths)
    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print(line)
    for r in rows:
        cells = [str(r.get("carrier") or r.get("id")).ljust(name_w),
                 (fmt(r.get("price")) or "-").ljust(10)]
        for i, c in enumerate(cols):
            fs = r["field_scores"].get(c, {})
            raw = fs.get("raw")
            txt = fmt(raw)
            if isinstance(raw, (int, float)) and not isinstance(raw, bool):
                sc = fs.get("score")
                if sc is not None and sc < 0.5:
                    txt += " !"
            cells.append(txt.ljust(widths[2 + i]))
        print("  ".join(cells))
    print(line)


def run_scenario_check(quotes: List[Dict[str, Any]], scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Test each quote against hypothetical worst-case losses."""
    losses = scenario.get("worst_case_losses", []) or []
    results = []
    for q in quotes:
        product = q.get("product", "auto")
        limits = q.get("limits", {}) or {}
        uncovered = []
        for loss in losses:
            demands = loss.get(product)
            if not demands:
                continue
            for field, need in demands.items():
                have = money(limits.get(field))
                if have is None:
                    uncovered.append({"loss": loss.get("label"), "field": field,
                                      "need": need, "have": None})
                elif have < need:
                    uncovered.append({"loss": loss.get("label"), "field": field,
                                      "need": need, "have": have,
                                      "shortfall": need - have})
        results.append({
            "id": q.get("id"),
            "carrier": q.get("carrier"),
            "uncovered": uncovered,
            "passes": not uncovered,
        })
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Compare insurance quotes on equal footing.")
    ap.add_argument("quotes", help="Path to quotes JSON file")
    ap.add_argument("--scenario", help="Path to scenario JSON file")
    ap.add_argument("--weights", help="Path to weights JSON file")
    ap.add_argument("--fields", action="store_true", help="Print the field registry and exit")
    ap.add_argument("--explain", metavar="PLAN_ID", help="Explain one plan in detail")
    args = ap.parse_args()

    if args.fields:
        for product, flds in FIELDS.items():
            print(f"\n## {product}")
            for key, spec in flds.items():
                print(f"  {key:28s} {spec['label']:32s} ideal={spec['ideal']:<10} {spec['why']}")
        return 0

    try:
        with open(args.quotes, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"[ERROR] No such file: {args.quotes}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {args.quotes}: {e}", file=sys.stderr)
        return 2

    quotes = data.get("quotes") if isinstance(data, dict) and "quotes" in data else data
    if isinstance(quotes, dict):
        quotes = [quotes]
    if not isinstance(quotes, list) or not quotes:
        print("[ERROR] Expected a non-empty list of quotes (or {'quotes': [...]}, or a single quote object).",
              file=sys.stderr)
        return 2

    product = quotes[0].get("product", "auto")

    weights = default_weights(product)
    if args.weights:
        try:
            with open(args.weights, "r", encoding="utf-8") as fh:
                weights.update(json.load(fh))
        except (OSError, json.JSONDecodeError) as e:
            print(f"[WARN] Could not read weights ({e}); using defaults.", file=sys.stderr)

    scored = [score_quote(q, weights) for q in quotes]
    normalize_price_scores(scored)
    scored.sort(key=lambda s: s["combined_score"], reverse=True)

    print("=" * 78)
    print(f"INSURANCE QUOTE COMPARISON — product={product}  quotes={len(quotes)}")
    print("=" * 78)
    print()
    print_table(scored, product)
    print()

    print("RANKING")
    print("-" * 78)
    for i, s in enumerate(scored, 1):
        flagcount = len(s["flags"])
        print(f"  {i}. {str(s['carrier'] or s['id']):24s} score={s['combined_score']:.3f}  "
              f"coverage={s['coverage_score']:.3f}  price_score={s.get('price_score', 0):.3f}  "
              f"premium={fmt(s['price'])}/yr  flags={flagcount}")
    print()

    for s in scored:
        if s["flags"]:
            print(f"FLAGS — {s['carrier'] or s['id']}")
            for fl in s["flags"]:
                print(f"  [{fl['severity']}] {fl['msg']}")
            print()

    if args.explain:
        target = next((s for s in scored if s["id"] == args.explain), None)
        if target:
            print("=" * 78)
            print(f"DETAIL — {target['carrier']} ({target['id']})")
            print("=" * 78)
            print(f"  premium/yr      : {fmt(target['price'])}")
            print(f"  coverage score  : {target['coverage_score']:.3f}")
            print(f"  combined score  : {target['combined_score']:.3f}")
            print(f"  notes           : {target.get('notes') or '-'}")
            print()
            for key, fs in target["field_scores"].items():
                sc = fs["score"]
                pct = "n/a" if sc is None else f"{sc * 100:5.1f}%"
                print(f"  {fs['label']:34s} {fmt(fs['raw']):>14s}   adequacy {pct}")
                print(f"      -> {fs['why']}")
            print()
            if target["features"]:
                print("  FEATURES")
                for key, info in target["features"].items():
                    print(f"    {'[x]' if info['on'] else '[ ]'} {info['label']}")
            print()
        else:
            print(f"[WARN] No quote with id '{args.explain}'", file=sys.stderr)

    if args.scenario:
        try:
            with open(args.scenario, "r", encoding="utf-8") as fh:
                scenario = json.load(fh)
        except (OSError, json.JSONDecodeError) as e:
            print(f"[WARN] Could not read scenario ({e}); skipping scenario check.", file=sys.stderr)
            scenario = None
        if scenario:
            print("=" * 78)
            print(f"SCENARIO CHECK — {scenario.get('label', 'scenario')}")
            print("=" * 78)
            for res in run_scenario_check(quotes, scenario):
                status = "PASS" if res["passes"] else "FAILS"
                print(f"  {status:6s} {res['carrier'] or res['id']}")
                for u in res["uncovered"]:
                    have = fmt(u.get("have"))
                    need = fmt(u.get("need"))
                    short = fmt(u.get("shortfall")) if u.get("shortfall") else "-"
                    print(f"      • {u['loss']}: {u['field']} need {need}, have {have} (short {short})")
            print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
