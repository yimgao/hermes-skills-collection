#!/usr/bin/env python3
"""
pricecheck.py — Price history + "is this a good deal?" analyzer.

Logs observed prices for a product over time, then tells you:
  - where today's price sits vs. the historical band (percentile)
  - whether it is a genuine sale or a fake-discounted "was" price
  - a BUY / FAIR / WAIT / SKIP verdict against your own target price

Subcommands:
  log      record a price observation
  check    analyze the latest price for a product
  list     show tracked products
  target   set a target / max price for a product

Data: ~/.hermes/data/purchase-advisor/prices/<slug>.json
Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime

DATA_ROOT = os.path.expanduser("~/.hermes/data/purchase-advisor/prices")


def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "product"


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def path_for(slug: str) -> str:
    return os.path.join(DATA_ROOT, f"{slug}.json")


def load(slug: str) -> dict:
    p = path_for(slug)
    if not os.path.exists(p):
        return {"slug": slug, "name": "", "target_price": None, "max_price": None,
                "list_price": None, "observations": []}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def save(slug: str, data: dict) -> None:
    os.makedirs(DATA_ROOT, exist_ok=True)
    tmp = path_for(slug) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path_for(slug))


def num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def percentile(values: list, p: float) -> float:
    """Linear-interpolated percentile of value p (0..100) within values."""
    if not values:
        return 0.0
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    k = (len(s) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def cmd_log(args) -> int:
    slug = slugify(args.product)
    data = load(slug)
    if args.name:
        data["name"] = args.name
    if args.list_price is not None:
        data["list_price"] = args.list_price
    data["observations"].append({
        "date": args.date or date.today().isoformat(),
        "price": args.price,
        "source": args.source or "unknown",
        "note": args.note or "",
        "list_price": args.list_price,
        "logged": now_iso(),
    })
    save(slug, data)
    n = len(data["observations"])
    print(f"[OK] logged {args.price:,.2f} for '{slug}' ({n} observation{'s' if n != 1 else ''})")
    return 0


def cmd_target(args) -> int:
    slug = slugify(args.product)
    data = load(slug)
    if args.name:
        data["name"] = args.name
    if args.target is not None:
        data["target_price"] = args.target
    if args.max is not None:
        data["max_price"] = args.max
    if args.list_price is not None:
        data["list_price"] = args.list_price
    save(slug, data)
    t = data.get("target_price")
    m = data.get("max_price")
    print(f"[OK] target for '{slug}':"
          + (f" target={t:,.2f}" if t else "")
          + (f" max={m:,.2f}" if m else "")
          + ("" if (t or m) else " (nothing set — pass --target or --max)"))
    return 0


def cmd_list(args) -> int:
    if not os.path.isdir(DATA_ROOT):
        print("(no price history yet)")
        return 0
    files = sorted(f for f in os.listdir(DATA_ROOT) if f.endswith(".json"))
    if not files:
        print("(no price history yet)")
        return 0
    for fn in files:
        with open(os.path.join(DATA_ROOT, fn), "r", encoding="utf-8") as f:
            d = json.load(f)
        obs = d.get("observations", [])
        last = obs[-1]["price"] if obs else None
        lo = min((o["price"] for o in obs), default=None)
        hi = max((o["price"] for o in obs), default=None)
        print(f"  {d['slug']:<34} n={len(obs):<3} last={last if last is None else format(last, ',.2f'):>10}"
              f"  range={lo if lo is None else format(lo, ',.2f')}-{hi if hi is None else format(hi, ',.2f')}"
              f"  target={d.get('target_price')}")
    return 0


def cmd_check(args) -> int:
    slug = slugify(args.product)
    data = load(slug)
    obs = data.get("observations", [])
    if not obs:
        print(f"[ERROR] no price observations for '{slug}'. Log one first:", file=sys.stderr)
        print(f"        python3 pricecheck.py log --product \"{args.product}\" --price 1299", file=sys.stderr)
        return 1

    prices = [num(o["price"]) for o in obs]
    cur = num(obs[-1]["price"])
    lo, hi = min(prices), max(prices)
    med = percentile(prices, 50)
    p10 = percentile(prices, 10)
    p90 = percentile(prices, 90)
    # "cheapness rank": 100% = cheapest ever seen, 0% = most expensive ever seen.
    # A low price means a HIGH rank, so count observations that are MORE expensive.
    above = sum(1 for p in prices if p > cur)
    rank = 100.0 * above / len(prices) if len(prices) > 1 else 100.0

    # fake discount detection: today's price vs a recorded list/"was" price
    list_price = num(data.get("list_price")) or 0.0
    if not list_price:
        list_prices = [num(o.get("list_price")) for o in obs if o.get("list_price")]
        list_price = max(list_prices) if list_prices else 0.0
    discount = ((list_price - cur) / list_price * 100.0) if list_price else 0.0

    target = data.get("target_price")
    maxp = data.get("max_price")

    print()
    print(f"  Product : {data.get('name') or slug}")
    print(f"  Slug    : {slug}")
    print(f"  Samples : {len(prices)}  (latest {obs[-1]['date']} @ {cur:,.2f} from {obs[-1].get('source','?')})")
    print()
    print(f"    observed low      {lo:>12,.2f}")
    print(f"    10th percentile   {p10:>12,.2f}")
    print(f"    median            {med:>12,.2f}")
    print(f"    90th percentile   {p90:>12,.2f}")
    print(f"    observed high     {hi:>12,.2f}")
    print(f"    current percentile rank   {rank:>6.1f}%   (100% = cheapest ever seen)")
    if list_price:
        print(f"    list price        {list_price:>12,.2f}   claimed discount {discount:>5.1f}%")
    print()

    # verdict
    verdict, reasons = "FAIR", []
    if rank >= 90:
        verdict = "BUY NOW"
        reasons.append(f"price is at the {rank:.0f}th percentile of everything seen — near the floor")
    elif rank <= 20:
        verdict = "SKIP / WAIT"
        reasons.append(f"price is at the {rank:.0f}th percentile — near the ceiling, wait for a drop")

    if target is not None:
        if cur <= target:
            verdict = "BUY NOW"
            reasons.append(f"at or below your target price ({target:,.2f})")
        else:
            if verdict == "BUY NOW":
                verdict = "FAIR"
            reasons.append(f"above your target price of {target:,.2f} by {cur - target:,.2f}")
    if maxp is not None and cur > maxp:
        verdict = "SKIP / WAIT"
        reasons.append(f"above your hard max of {maxp:,.2f}")
    if list_price and discount < 10:
        reasons.append(f"claimed discount is only {discount:.1f}% — likely a fake 'sale' price")
    if list_price and discount >= 50:
        reasons.append(f"claimed discount {discount:.0f}% — verify it is a genuine sale, not a "
                       f"never-real list price")
    if list_price and cur >= list_price:
        reasons.append(f"current price {cur:,.2f} is at or above the 'was' price {list_price:,.2f} "
                       f"— no discount at all")
    if len(prices) < 4:
        reasons.append(f"only {len(prices)} sample(s) — log more before treating the band as reliable")

    print(f"  VERDICT : {verdict}")
    for r in reasons:
        print(f"            - {r}")
    print()
    print(f"  Suggested next action: "
          + {
              "BUY NOW": "buy it now if the budget allows — this is a good price",
              "FAIR": "this is a normal price; buy if you need it now, otherwise wait for a sale",
              "SKIP / WAIT": "do not buy at this price; set a price alert and check back",
          }[verdict])
    print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="pricecheck.py",
                                 description="Price history + deal-quality analyzer")
    sub = ap.add_subparsers(dest="cmd", required=True)

    l = sub.add_parser("log", help="record a price observation")
    l.add_argument("--product", required=True)
    l.add_argument("--name", help="display name")
    l.add_argument("--price", type=float, required=True)
    l.add_argument("--date", help="YYYY-MM-DD (default today)")
    l.add_argument("--source", help="retailer / site")
    l.add_argument("--note")
    l.add_argument("--list-price", type=float, dest="list_price",
                   help="the 'was' price for fake-discount detection")
    l.set_defaults(func=cmd_log)

    t = sub.add_parser("target", help="set your target / max price")
    t.add_argument("--product", required=True)
    t.add_argument("--name")
    t.add_argument("--target", type=float, help="price you want to hit")
    t.add_argument("--max", type=float, help="hard ceiling")
    t.add_argument("--list-price", type=float, dest="list_price")
    t.set_defaults(func=cmd_target)

    c = sub.add_parser("check", help="analyze the latest price")
    c.add_argument("--product", required=True)
    c.set_defaults(func=cmd_check)

    li = sub.add_parser("list", help="list tracked products")
    li.set_defaults(func=cmd_list)

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
