#!/usr/bin/env python3
"""
tco.py — Total Cost of Ownership calculator for a purchase decision.

Compares 1..N candidate products on total cost over a horizon, not sticker price.

Subcommands:
  add      add / update a candidate product
  compare  score candidates, print a ranked TCO table with a verdict
  list     show all candidates in the current decision
  clear    reset the current decision file

All data is local JSON at ~/.hermes/data/purchase-advisor/decisions/<id>.json
Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime

DATA_ROOT = os.path.expanduser("~/.hermes/data/purchase-advisor/decisions")

# ---- recurring-cost fields ------------------------------------------------------
# (storage_key, rate_prefix, label)
#   storage_key : where the one-time / flat amount is stored
#   rate_prefix : prefix for the "_annual" / "_monthly" / "_years" rate fields
# e.g. warranty -> storage "warranty_cost", rates "warranty_annual" / "warranty_years"
RECUR_FIELDS = [
    ("warranty_cost", "warranty", "Warranty/extended plan"),
    ("insurance", "insurance", "Insurance"),
    ("subscription", "subscription", "Subscription"),
    ("consumables", "consumables", "Consumables (ink/bags/toner)"),
    ("maintenance", "maintenance", "Maintenance"),
    ("service_plan", "service_plan", "Service plan"),
]

# ---- one-time-cost fields beyond sticker price --------------------------------
ONETIME_FIELDS = [
    ("accessories_cost", "Required accessories"),
    ("shipping_cost", "Shipping"),
    ("tax_pct", "Sales tax %"),
    ("setup_cost", "Setup / migration cost"),
    ("disposal_cost", "Disposal of old unit"),
]

REQUIRED_SPECS = [
    "performance",
    "display",
    "battery",
    "build",
    "support",
    "ecosystem",
]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def decision_path(did: str) -> str:
    return os.path.join(DATA_ROOT, f"{did}.json")


def load(did: str) -> dict:
    p = decision_path(did)
    if not os.path.exists(p):
        return {
            "id": did,
            "title": "",
            "category": "",
            "horizon_years": 3,
            "currency": "USD",
            "created": now_iso(),
            "updated": now_iso(),
            "candidates": [],
        }
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save(did: str, data: dict) -> None:
    os.makedirs(DATA_ROOT, exist_ok=True)
    data["updated"] = now_iso()
    tmp = decision_path(did) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, decision_path(did))


def num(x) -> float:
    if x is None or x == "":
        return 0.0
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


# ------------------------------------------------------------------ tco math --
def tco(cand: dict, horizon_years: float) -> dict:
    """Return a breakdown dict for one candidate over `horizon_years`."""
    sticker = num(cand.get("price"))

    # tax on sticker + accessories
    tax_pct = num(cand.get("tax_pct")) / 100.0
    acc = num(cand.get("accessories_cost"))
    ship = num(cand.get("shipping_cost"))
    setup = num(cand.get("setup_cost"))
    disposal = num(cand.get("disposal_cost"))
    taxable = sticker + acc
    tax = round(taxable * num(cand.get("tax_pct")) / 100.0, 2)

    # recurring costs: explicit amount OR annual/monthly rate x years
    recurring_breakdown = {}
    recurring_total = 0.0
    for key, rate_prefix, label in RECUR_FIELDS:
        direct = num(cand.get(key))
        annual = num(cand.get(f"{rate_prefix}_annual"))
        monthly = num(cand.get(f"{rate_prefix}_monthly"))
        yrs = num(cand.get(f"{rate_prefix}_years")) or horizon_years
        mo = num(cand.get(f"{rate_prefix}_months")) or (yrs * 12)
        total = direct + annual * yrs + monthly * mo
        if total:
            recurring_breakdown[label] = round(total, 2)
            recurring_total += total

    # resale / residual value (subtract)
    resale = num(cand.get("resale_value"))

    total = sticker + acc + ship + tax + setup + disposal + recurring_total - resale
    per_year = total / horizon_years if horizon_years else total
    per_month = per_year / 12.0

    # break-even: months until running cost alone exceeds a competitor's total
    return {
        "sticker": round(sticker, 2),
        "tax": round(tax, 2),
        "accessories": round(acc, 2),
        "shipping": round(ship, 2),
        "setup": round(setup, 2),
        "disposal": round(disposal, 2),
        "recurring": round(recurring_total, 2),
        "recurring_detail": recurring_breakdown,
        "resale": round(resale, 2),
        "total": round(total, 2),
        "per_year": round(per_year, 2),
        "per_month": round(per_month, 2),
        "horizon_years": horizon_years,
    }


# ------------------------------------------------------------- spec scoring --
def spec_score(cand: dict, weights: dict) -> tuple:
    """Weighted spec score. Returns (score_0_to_10, covered, missing)."""
    scores = cand.get("specs", {}) or {}
    total_w = 0.0
    acc = 0.0
    covered = []
    missing = []
    for key in REQUIRED_SPECS:
        w = float(weights.get(key, 1.0))
        v = scores.get(key)
        if v is None:
            missing.append(key)
            continue
        covered.append(key)
        total_w += w
        acc += num(v) * w
    if total_w == 0:
        return (0.0, covered, missing)
    return (round(acc / total_w, 2), covered, missing)


def normalized_spec_score(cand: dict, weights: dict, best_by_spec: dict) -> float:
    """Spec score normalized against the best candidate per spec (0..1)."""
    scores = cand.get("specs", {}) or {}
    num_ = 0.0
    den = 0.0
    for key in REQUIRED_SPECS:
        w = float(weights.get(key, 1.0))
        best = best_by_spec.get(key)
        if best is None or best <= 0:
            continue
        v = scores.get(key)
        if v is None:
            continue
        num_ += min(num(v) / best, 1.0) * w
        den += w
    return round(num_ / den, 3) if den else 0.0


def price_score(cand_tco: dict, min_tco: float, max_tco: float) -> float:
    """Map TCO to 0..1 where lower is better.

    Min-max normalization is useless with few candidates (with 2 candidates the
    scores are always 1.00 vs 0.00, so the price weight becomes a tie-breaker
    rather than a real signal). Instead use a ratio against the cheapest option:
    the cheapest candidate scores 1.00, and each doubling of cost halves the
    score. This is scale-free and meaningful for any candidate count.
    """
    if min_tco <= 0:
        return 1.0
    ratio = cand_tco["total"] / min_tco
    if ratio <= 1.0:
        return 1.0
    return round(1.0 / ratio, 3)


def confidence_penalty(cand: dict) -> float:
    """Unknown specs and low-confidence prices reduce the score."""
    missing = len([k for k in REQUIRED_SPECS if not cand.get("specs", {}).get(k)])
    return min(0.30, missing * 0.06)


# ------------------------------------------------------------------- cmd: add --
def cmd_add(args) -> int:
    data = load(args.decision)
    if args.title and not data["title"]:
        data["title"] = args.title
    if args.category:
        data["category"] = args.category
    if args.horizon:
        data["horizon_years"] = args.horizon
    if args.currency:
        data["currency"] = args.currency

    cand = None
    for c in data["candidates"]:
        if c.get("name") == args.name:
            cand = c
            break
    if cand is None:
        cand = {"name": args.name, "specs": {}, "notes": ""}
        data["candidates"].append(cand)

    simple = [
        ("price", args.price),
        ("tax_pct", args.tax),
        ("accessories_cost", args.accessories),
        ("shipping_cost", args.shipping),
        ("setup_cost", args.setup),
        ("disposal_cost", args.disposal),
        ("resale_value", args.resale),
        ("warranty_cost", args.warranty),
        ("subscription_annual", args.subscription_annual),
        ("consumables_annual", args.consumables_annual),
        ("maintenance_annual", args.maintenance_annual),
        ("insurance_annual", args.insurance_annual),
        ("service_plan_annual", args.service_plan_annual),
        ("warranty_years", args.warranty_years),
        ("subscription_years", args.subscription_years),
        ("consumables_years", args.consumables_years),
        ("maintenance_years", args.maintenance_years),
        ("insurance_years", args.insurance_years),
        ("service_plan_years", args.service_plan_years),
    ]
    for k, v in simple:
        if v is not None:
            cand[k] = v

    for spec in args.spec or []:
        if ":" not in spec:
            print(f"[ERROR] --spec must be key:value, got {spec!r}", file=sys.stderr)
            return 2
        k, v = spec.split(":", 1)
        cand.setdefault("specs", {})[k.strip()] = num(v)
        if k.strip() not in REQUIRED_SPECS:
            print(f"[WARN] unknown spec key {k!r} (known: {', '.join(REQUIRED_SPECS)})")

    if args.note:
        cand["notes"] = (cand.get("notes", "") + " " + args.note).strip()
    if args.url:
        cand["url"] = args.url
    if args.source:
        cand["price_source"] = args.source

    save(args.decision, data)
    print(f"[OK] candidate '{args.name}' saved to decision '{args.decision}'")
    return 0


# -------------------------------------------------------------- cmd: compare --
def cmd_compare(args) -> int:
    data = load(args.decision)
    cands = data.get("candidates", [])
    if not cands:
        print(f"[ERROR] no candidates in decision '{args.decision}' — add some first", file=sys.stderr)
        return 1

    weights = {
        "performance": args.w_performance,
        "display": args.w_display,
        "battery": args.w_battery,
        "build": args.w_build,
        "support": args.w_support,
        "ecosystem": args.w_ecosystem,
    }
    horizon = float(args.horizon or data.get("horizon_years", 3))
    cur = data.get("currency", "USD")

    tcos = {c["name"]: tco(c, horizon) for c in cands}
    totals = [t["total"] for t in tcos.values()]
    min_tco, max_tco = min(totals), max(totals)

    best_by_spec = {}
    for key in REQUIRED_SPECS:
        vals = [num(c.get("specs", {}).get(key)) for c in cands if c.get("specs", {}).get(key) is not None]
        best_by_spec[key] = max(vals) if vals else None

    rows = []
    for c in cands:
        t = tcos[c["name"]]
        ps = price_score(t, min_tco, max_tco)
        ss = normalized_spec_score(c, weights, best_by_spec)
        coverage = len([k for k in REQUIRED_SPECS if c.get("specs", {}).get(k) is not None])
        conf_pen = confidence_penalty(c)
        final = round((ps * args.w_price + ss * args.w_specs) * (1.0 - conf_pen), 3)
        rows.append({
            "name": c["name"],
            "total": t["total"],
            "per_month": t["per_month"],
            "price_score": ps,
            "spec_score": ss,
            "coverage": coverage,
            "penalty": conf_pen,
            "final": final,
            "tco": t,
            "cand": c,
        })

    rows.sort(key=lambda r: (-r["final"], r["total"]))
    best = rows[0]
    runner: dict | None = rows[1] if len(rows) > 1 else None
    margin = round(best["final"] - runner["final"], 3) if runner is not None else None
    # Ratio-based closeness: how much cheaper is the runner-up than the winner,
    # as a fraction of the winner's total? This is meaningful regardless of how
    # many candidates there are (a normalized-score margin is not, because with
    # 2 candidates the price score is always 1.00 vs 0.00).
    # tco_gap_pct is SIGNED: positive = runner-up is cheaper by that much.
    tco_gap_pct = None
    if runner is not None and best["total"] > 0:
        tco_gap_pct = round((runner["total"] - best["total"]) / best["total"] * 100.0, 2)

    print()
    print(f"  Decision : {data.get('title') or args.decision}")
    if data.get("category"):
        print(f"  Category : {data['category']}")
    print(f"  Horizon  : {horizon:g} years   Currency: {cur}")
    print()
    hdr = f"  {'CANDIDATE':<26}{'TCO':>11}{'per/mo':>9}{'price':>7}{'specs':>7}{'cov':>5}{'FINAL':>8}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for r in rows:
        print(f"  {r['name'][:25]:<26}{r['total']:>11,.2f}{r['per_month']:>9,.2f}"
              f"{r['price_score']:>7.2f}{r['spec_score']:>7.2f}{r['coverage']:>5}{r['final']:>8.3f}")
    print()

    # verdict — evaluated worst-first so HOLD/CLOSE override BUY
    verdict, why = "BUY", []
    if best["coverage"] < len(REQUIRED_SPECS):
        verdict = "HOLD — research incomplete"
        missing = [k for k in REQUIRED_SPECS if not best["cand"].get("specs", {}).get(k)]
        why.append("missing specs for the leader: " + ", ".join(missing))
    if (tco_gap_pct is not None and abs(tco_gap_pct) < args.close_gap_pct):
        verdict = "CLOSE — too close to call"
        if tco_gap_pct >= 0:
            why.append(f"runner-up is only {tco_gap_pct:.1f}% cheaper in TCO — "
                       f"decide on non-price factors (warranty, ecosystem, feel)")
        else:
            why.append(f"leader is only {abs(tco_gap_pct):.1f}% more expensive in TCO — "
                       f"decide on non-price factors (warranty, ecosystem, feel)")
    if verdict == "BUY":
        # "Better value elsewhere": is there a candidate meaningfully cheaper than
        # the leader AND close in spec score? If so, the leader's premium is not
        # self-justifying — the user should at least look at the cheaper one.
        # This is checked against the CHEAPEST candidate (not the runner-up),
        # because the runner-up may itself be the expensive one.
        if runner is not None:
            cheapest = min(rows, key=lambda r: r["total"])
            if cheapest["total"] < best["total"] * 0.97:
                premium = best["total"] - cheapest["total"]
                spec_ratio = (cheapest["spec_score"] / best["spec_score"]
                              if best["spec_score"] else 0.0)
                if spec_ratio >= args.spec_floor:
                    verdict = "WAIT — better value elsewhere"
                    why.append(
                        f"{cheapest['name']} is {premium:,.2f} cheaper over {horizon:g}y "
                        f"({premium / best['total'] * 100:.0f}%) with comparable specs "
                        f"({cheapest['spec_score']:.2f} vs {best['spec_score']:.2f}) — "
                        f"confirm the premium buys something you actually need"
                    )
                else:
                    why.append(
                        f"{cheapest['name']} is cheaper but clearly weaker on specs "
                        f"({cheapest['spec_score']:.2f} vs {best['spec_score']:.2f}) — "
                        f"paying more for capability"
                    )
    if not why:
        why.append(f"{best['name']} leads by {margin:.3f} and is cheapest over {horizon:g}y"
                    if (runner is not None and margin is not None)
                    else f"only candidate: {best['name']}")

    print(f"  VERDICT  : {verdict}")
    for w in why:
        print(f"             - {w}")
    print()

    # TCO breakdown for the winner
    t = best["tco"]
    print(f"  TCO breakdown — {best['name']}")
    print(f"    sticker            {t['sticker']:>12,.2f}")
    print(f"    tax                {t['tax']:>12,.2f}")
    print(f"    accessories        {t['accessories']:>12,.2f}")
    print(f"    shipping           {t['shipping']:>12,.2f}")
    print(f"    setup              {t['setup']:>12,.2f}")
    print(f"    disposal           {t['disposal']:>12,.2f}")
    print(f"    recurring          {t['recurring']:>12,.2f}")
    for label, v in t["recurring_detail"].items():
        print(f"      - {label:<14}{v:>10,.2f}")
    print(f"    resale (credit)   -{t['resale']:>12,.2f}")
    print(f"    ------------------------------")
    print(f"    TOTAL {horizon:g}y        {t['total']:>12,.2f}   ({t['per_month']:,.2f}/mo)")
    print()
    return 0


# ---------------------------------------------------------------- cmd: list --
def cmd_list(args) -> int:
    data = load(args.decision)
    cands = data.get("candidates", [])
    print(f"decision '{args.decision}': {data.get('title') or '(untitled)'} "
          f"horizon={data.get('horizon_years')}y candidates={len(cands)}")
    for c in cands:
        specs = c.get("specs", {}) or {}
        cov = len([k for k in REQUIRED_SPECS if specs.get(k) is not None])
        print(f"  - {c['name']:<28} price={num(c.get('price')):>10,.2f}  specs {cov}/{len(REQUIRED_SPECS)}")
    return 0


def cmd_clear(args) -> int:
    p = decision_path(args.decision)
    if os.path.exists(p):
        os.remove(p)
        print(f"[OK] cleared decision '{args.decision}'")
    else:
        print(f"[OK] nothing to clear for '{args.decision}'")
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="tco.py", description="TCO calculator for purchase decisions")
    ap.add_argument("--decision", "-d", default="default", help="decision id (file name)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="add/update a candidate")
    a.add_argument("--name", required=True)
    a.add_argument("--price", type=float)
    a.add_argument("--tax", type=float, help="sales tax percent, e.g. 8.25")
    a.add_argument("--accessories", type=float)
    a.add_argument("--shipping", type=float)
    a.add_argument("--setup", type=float)
    a.add_argument("--disposal", type=float)
    a.add_argument("--resale", type=float, help="expected resale / trade-in credit")
    a.add_argument("--warranty", type=float, help="one-time warranty cost")
    a.add_argument("--warranty-years", type=float)
    a.add_argument("--subscription-annual", type=float)
    a.add_argument("--subscription-years", type=float)
    a.add_argument("--consumables-annual", type=float)
    a.add_argument("--consumables-years", type=float)
    a.add_argument("--maintenance-annual", type=float)
    a.add_argument("--maintenance-years", type=float)
    a.add_argument("--insurance-annual", type=float)
    a.add_argument("--insurance-years", type=float)
    a.add_argument("--service-plan-annual", type=float)
    a.add_argument("--service-plan-years", type=float)
    a.add_argument("--spec", action="append", help="key:value, repeatable")
    a.add_argument("--note")
    a.add_argument("--url")
    a.add_argument("--source", help="where the price came from")
    a.add_argument("--title", help="decision title (set once)")
    a.add_argument("--category")
    a.add_argument("--horizon", type=float)
    a.add_argument("--currency")
    a.set_defaults(func=cmd_add)

    c = sub.add_parser("compare", help="score and rank candidates")
    c.add_argument("--horizon", type=float)
    c.add_argument("--w-price", type=float, default=0.45, dest="w_price")
    c.add_argument("--w-specs", type=float, default=0.55, dest="w_specs")
    c.add_argument("--w-performance", type=float, default=1.0, dest="w_performance")
    c.add_argument("--w-display", type=float, default=1.0, dest="w_display")
    c.add_argument("--w-battery", type=float, default=1.0, dest="w_battery")
    c.add_argument("--w-build", type=float, default=1.0, dest="w_build")
    c.add_argument("--w-support", type=float, default=1.0, dest="w_support")
    c.add_argument("--w-ecosystem", type=float, default=1.0, dest="w_ecosystem")
    c.add_argument("--min-margin", type=float, default=0.08, dest="min_margin")
    c.add_argument("--close-gap-pct", type=float, default=5.0, dest="close_gap_pct",
                   help="if the runner-up is within this %% of the leader's TCO, "
                        "the call is 'too close to call' (default 5%%)")
    c.add_argument("--spec-floor", type=float, default=0.85, dest="spec_floor",
                   help="a cheaper option counts as 'comparable' if its spec score is at "
                        "least this fraction of the leader's")
    c.set_defaults(func=cmd_compare)

    l = sub.add_parser("list", help="list candidates")
    l.set_defaults(func=cmd_list)

    cl = sub.add_parser("clear", help="delete this decision file")
    cl.set_defaults(func=cmd_clear)

    return ap


def main(argv=None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())
