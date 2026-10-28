#!/usr/bin/env python3
"""
brief.py — Render a purchase decision into a pasteable brief.

Reads the decision JSON written by tco.py and emits a Markdown brief:
the verdict, the ranked table, the TCO math, the risk notes, and the
"what would change my mind" section.

Subcommands:
  render   print the brief as Markdown to stdout
  save     write the brief to a file

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date

DATA_ROOT = os.path.expanduser("~/.hermes/data/purchase-advisor/decisions")

REQUIRED_SPECS = [
    ("performance", "Performance"),
    ("display", "Display / screen"),
    ("battery", "Battery / endurance"),
    ("build", "Build / materials"),
    ("support", "Support / warranty"),
    ("ecosystem", "Ecosystem / compatibility"),
]

# risk flags keyed by data field -> (label, threshold multiplier of sticker)
RISK_RULES = [
    ("subscription_annual", "Recurring subscription", 0.10),
    ("insurance_annual", "Insurance required", 0.08),
    ("maintenance_annual", "Recurring maintenance", 0.05),
    ("consumables_annual", "Consumables cost", 0.04),
]


def num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def load(did: str) -> dict:
    p = os.path.join(DATA_ROOT, f"{did}.json")
    if not os.path.exists(p):
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def tco_of(cand: dict, horizon: float) -> dict:
    sticker = num(cand.get("price"))
    tax = round((sticker + num(cand.get("accessories_cost"))) * num(cand.get("tax_pct")) / 100.0, 2)
    one = round(num(cand.get("accessories_cost")) + num(cand.get("shipping_cost"))
                + num(cand.get("setup_cost")) + num(cand.get("disposal_cost")) + tax, 2)
    rec = 0.0
    detail = {}
    # Key names must match tco.py's RECUR_FIELDS exactly:
    #   warranty -> warranty_cost, others use the bare field name.
    for field, key in (("warranty_cost", "warranty"), ("subscription", "subscription"),
                       ("consumables", "consumables"), ("maintenance", "maintenance"),
                       ("insurance", "insurance"), ("service_plan", "service_plan")):
        yrs = num(cand.get(f"{key}_years")) or horizon
        mo = num(cand.get(f"{key}_months")) or yrs * 12
        # one-time amount (warranty_cost 199) AND rate-based (subscription_annual 120/yr)
        total = (num(cand.get(field))
                 + num(cand.get(f"{key}_annual")) * yrs
                 + num(cand.get(f"{key}_monthly")) * mo)
        if total:
            detail[key] = round(total, 2)
            rec += total
    resale = num(cand.get("resale_value"))
    total = round(sticker + round(one, 2) + round(rec, 2) - resale, 2)
    return {
        "sticker": sticker, "tax": tax, "one": one, "rec": rec, "detail": detail,
        "resale": resale, "total": round(total, 2),
        "per_month": round(total / horizon / 12.0, 2) if horizon else 0.0,
    }


def risks_for(cand: dict, t: dict) -> list:
    out = []
    for field, label, mult in RISK_RULES:
        v = num(cand.get(f"{field}_annual"))
        if v and v >= t["sticker"] * mult and t["sticker"] > 0:
            out.append(f"⚠️ {label}: {v:,.2f}/yr — {v / t['sticker'] * 100:.0f}% of sticker price")
    if num(cand.get("resale_value")) and num(cand.get("resale_value")) > t["sticker"] * 0.5:
        out.append("⚠️ Resale assumption is unusually optimistic — verify with a real trade-in quote")
    if t["rec"] > t["sticker"] * 0.25:
        out.append(f"⚠️ Recurring costs are {t['rec'] / t['sticker'] * 100:.0f}% of sticker — "
                   f"this is a lease in disguise")
    if num(cand.get("setup_cost")) > t["sticker"] * 0.05:
        out.append(f"⚠️ Setup/migration cost is significant: {num(cand.get('setup_cost')):,.2f}")
    return out


def cmd_render(args) -> int:
    data = load(args.decision)
    if not data or not data.get("candidates"):
        print(f"[ERROR] decision '{args.decision}' not found or empty. "
              f"Run tco.py add first.", file=sys.stderr)
        return 1

    horizon = float(args.horizon or data.get("horizon_years", 3))
    cur = data.get("currency", "USD")
    cands = data["candidates"]

    rows = []
    for c in cands:
        t = tco_of(c, horizon)
        specs = c.get("specs", {}) or {}
        cov = sum(1 for k, _ in REQUIRED_SPECS if specs.get(k) is not None)
        rows.append({"c": c, "t": t, "cov": cov,
                     "spec_sum": sum(num(specs.get(k)) for k, _ in REQUIRED_SPECS)})

    # --- weighted scoring, identical in spirit to tco.py compare -------------
    totals = [r["t"]["total"] for r in rows]
    min_tco, max_tco = min(totals), max(totals)
    best_by_spec = {}
    for key, _ in REQUIRED_SPECS:
        vals = [num(r["c"].get("specs", {}).get(key)) for r in rows
                if r["c"].get("specs", {}).get(key) is not None]
        best_by_spec[key] = max(vals) if vals else None
    w_price, w_specs = 0.45, 0.55
    for r in rows:
        specs = r["c"].get("specs", {}) or {}
        # ratio-based price score: cheapest = 1.00, each doubling of cost halves it.
        # (min-max normalization would always give 1.00 vs 0.00 with 2 candidates)
        if min_tco <= 0:
            p_score = 1.0
        else:
            ratio = r["t"]["total"] / min_tco
            p_score = 1.0 if ratio <= 1.0 else round(1.0 / ratio, 3)
        num_ = den = 0.0
        for key, _ in REQUIRED_SPECS:
            b = best_by_spec.get(key)
            v = specs.get(key)
            if not b or v is None:
                continue
            num_ += min(num(v) / b, 1.0)
            den += 1.0
        s_score = (num_ / den) if den else 0.0
        missing = sum(1 for k, _ in REQUIRED_SPECS if specs.get(k) is None)
        penalty = min(0.30, missing * 0.06)
        r["p_score"] = p_score
        r["s_score"] = s_score
        r["final"] = (p_score * w_price + s_score * w_specs) * (1.0 - penalty)

    rows.sort(key=lambda r: (-r["final"], r["t"]["total"]))
    best = rows[0]
    winner = best["c"]["name"]
    title = data.get("title") or args.decision
    cheaper = [r for r in rows if r["t"]["total"] < best["t"]["total"] * 0.97]

    L = []
    L.append(f"# 购买决策简报 · Purchase Decision Brief")
    L.append("")
    L.append(f"**决策 / Decision:** {title}")
    L.append(f"**品类 / Category:** {data.get('category') or '—'}")
    L.append(f"**评估周期 / Horizon:** {horizon:g} years  ·  **币种:** {cur}")
    L.append(f"**生成日期 / Date:** {date.today().isoformat()}")
    L.append("")
    L.append("---")
    L.append("")

    # 1. verdict
    L.append("## 1. 结论 · Verdict")
    L.append("")
    L.append(f"**推荐 / Recommendation: {winner}**")
    L.append("")
    if cheaper:
        alt = cheaper[0]
        L.append(f"> 备选 / Alternative: **{alt['c']['name']}** — "
                 f"TCO 低 {best['t']['total'] - alt['t']['total']:,.2f} {cur} over {horizon:g}y "
                 f"(规格分 {alt['s_score']:.2f} vs {best['s_score']:.2f}，综合分 "
                 f"{alt['final']:.3f} vs {best['final']:.3f})。"
                 f"若差价可接受且核心需求满足，可直接选备选。")
    else:
        L.append("> 无更便宜的实质替代 —— 在给定的候选集中这是唯一的最优解。")
    L.append("")
    L.append("**什么会改变这个结论 / What would change this mind:**")
    L.append("")
    L.append("- 核心需求权重变化（如果你更看重续航/生态而非性能，排序可能翻转）")
    L.append("- 出现新的价格（促销、返现、开学季/黑五）")
    L.append("- 现有设备提前故障，或需求提前改变")
    L.append("- 价格跌破你的目标价（见第 4 节）")
    L.append("")

    # 2. ranked table
    L.append("## 2. 候选排序 · Ranked Candidates")
    L.append("")
    L.append("| 候选 | 到手价 | TCO | 每月 | 规格覆盖 | 价格分 | 规格分 | 综合 | 状态 |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        name = r["c"]["name"]
        price = num(r["c"].get("price"))
        status = "✅ 推荐" if name == winner else ("🔁 备选" if r in cheaper else "❌ 不选")
        L.append(f"| {name} | {price:,.2f} | {r['t']['total']:,.2f} | "
                 f"{r['t']['per_month']:,.2f} | {r['cov']}/{len(REQUIRED_SPECS)} | "
                 f"{r['p_score']:.2f} | {r['s_score']:.2f} | **{r['final']:.3f}** | {status} |")
    L.append("")
    L.append("> 综合分 = 价格分 × 0.45 + 规格分 × 0.55，再按调研完整度扣分（每缺 1 项 −6%，上限 −30%）。")
    L.append("")

    # 3. TCO math
    L.append("## 3. 总拥有成本 · Total Cost of Ownership")
    L.append("")
    L.append(f"### {winner}")
    L.append("")
    L.append("| 项目 | 金额 | 说明 |")
    L.append("|---|---|---|")
    L.append(f"| 标价 Sticker | {best['t']['sticker']:,.2f} | 官网/零售价 |")
    if best["t"]["tax"]:
        L.append(f"| 税费 Tax | {best['t']['tax']:,.2f} | 按 {num(best['c'].get('tax_pct'))}% 计算 |")
    acc = num(best["c"].get("accessories_cost"))
    if acc:
        L.append(f"| 必需配件 Accessories | {acc:,.2f} | 不算就是低估 |")
    ship = num(best["c"].get("shipping_cost"))
    if ship:
        L.append(f"| 运费 Shipping | {ship:,.2f} | |")
    setup = num(best["c"].get("setup_cost"))
    if setup:
        L.append(f"| 部署/迁移 Setup | {setup:,.2f} | 迁移/学习成本也是钱 |")
    disp = num(best["c"].get("disposal_cost"))
    if disp:
        L.append(f"| 旧机处理 Disposal | {disp:,.2f} | |")
    for field, total in sorted(best["t"]["detail"].items()):
        L.append(f"| {field} | {total:,.2f} | {horizon:g} 年累计 |")
    if best["t"]["resale"]:
        L.append(f"| 残值抵扣 Resale | -{best['t']['resale']:,.2f} | 转售/回收抵扣 |")
    L.append(f"| **合计 TOTAL ({horizon:g}y)** | **{best['t']['total']:,.2f}** | "
             f"= {best['t']['per_month']:,.2f} {cur}/月 |")
    L.append("")
    L.append("> 口径说明：TCO 只包含**你这笔决策直接产生的成本**。已有的沉没成本不计入。")
    L.append("")

    # 4. risks
    L.append("## 4. 风险与隐藏成本 · Risks & Hidden Costs")
    L.append("")
    all_risks = []
    for r in rows:
        for x in risks_for(r["c"], r["t"]):
            all_risks.append(f"**{r['c']['name']}** — {x}")
    if all_risks:
        for x in all_risks:
            L.append(f"- {x}")
    else:
        L.append("- 未发现结构性隐藏成本。")
    L.append("")
    L.append("**通用提醒 / Always check:**")
    L.append("")
    L.append("- 标价是否含税？是否需要会员/附加才能用到全部功能？")
    L.append("- 商家实际保修 vs 厂家保修？延保由谁承担？")
    L.append("- 二手残值是真实成交价还是挂牌价？")
    L.append("- 是否有「限时优惠」制造紧迫感？（用 `pricecheck.py check` 验证）")
    L.append("")

    # 5. spec matrix
    L.append("## 5. 规格对照 · Spec Matrix")
    L.append("")
    L.append("| 维度 | " + " | ".join(r["c"]["name"][:20] for r in rows) + " |")
    L.append("|---|" + "---|" * len(rows))
    for key, label in REQUIRED_SPECS:
        cells = []
        for r in rows:
            v = (r["c"].get("specs", {}) or {}).get(key)
            cells.append(f"{num(v):.0f}" if v is not None else "—")
        L.append(f"| {label} | " + " | ".join(cells) + " |")
    L.append("")
    L.append("评分 0–10，为你的主观打分；`—` 表示尚未研究。")
    L.append("")

    # 6. gaps
    L.append("## 6. 调研缺口 · Research Gaps")
    L.append("")
    gaps = []
    for r in rows:
        miss = [label for key, label in REQUIRED_SPECS if not (r["c"].get("specs", {}) or {}).get(key)]
        if miss:
            gaps.append(f"- **{r['c']['name']}**: " + ", ".join(miss))
    if gaps:
        L.extend(gaps)
        L.append("")
        L.append("> 补齐这些项之前，不要把结论当成终局。")
    else:
        L.append("- 所有候选的规格项均已评分。")
    L.append("")

    # 7. next actions
    L.append("## 7. 下一步 · Next Actions")
    L.append("")
    L.append("- [ ] 补齐第 6 节的调研缺口")
    L.append(f"- [ ] 用 `pricecheck.py log` 记录 {winner} 当前报价，建立价格基线")
    L.append("- [ ] 设目标价：`pricecheck.py target --product \"<名称>\" --target <价格>`")
    L.append("- [ ] 若本期不买，设定复查日期（促销季/返现周期）")
    L.append("- [ ] 下单后用 `receipt-vault` 归档收据与保修卡")
    L.append("")

    out = "\n".join(L)
    if args.out:
        p = os.path.expanduser(args.out)
        os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(out + "\n")
        print(f"[OK] brief written to {p}")
    else:
        print(out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="brief.py", description="Render a purchase decision brief")
    ap.add_argument("--decision", "-d", default="default")
    ap.add_argument("--horizon", type=float)
    ap.add_argument("--out", help="write to this path instead of stdout")
    return ap


def main(argv=None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    try:
        return cmd_render(args)
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    sys.exit(main())
