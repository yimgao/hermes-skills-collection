#!/usr/bin/env python3
"""brag.py — local brag-doc / self-review / promotion-packet engine.

Data lives in ~/.hermes/data/perf-review/brag.json. Zero network calls.

Commands:
  add          log one win
  list         list wins (filter by period / axis / scope)
  stats        axis coverage, quarter distribution, gaps, data-quality flags
  rollup       markdown evidence table for a review period
  gaps         compare evidence against a target level
  feedback-ask generate a peer-feedback request template
  export       dump json or markdown
"""
import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

DEFAULT_DATA = Path.home() / ".hermes" / "data" / "perf-review" / "brag.json"

AXES = ["execution", "technical", "leadership", "collaboration", "business"]
SCOPES = ["self", "team", "org", "company"]
SCOPE_WEIGHT = {"self": 0.5, "team": 1.0, "org": 2.0, "company": 3.0}

# Generic ladder. Override with --levels JSON file; company ladders vary wildly.
LEVELS = {
    "entry":     {"org_min": 0, "team_min": 1,  "axes_min": 1},
    "mid":       {"org_min": 0, "team_min": 3,  "axes_min": 2},
    "senior":    {"org_min": 1, "team_min": 5,  "axes_min": 3},
    "staff":     {"org_min": 2, "team_min": 8,  "axes_min": 4},
    "principal": {"org_min": 4, "team_min": 10, "axes_min": 5},
}
ALIASES = {
    "entry": "entry", "junior": "entry", "l1": "entry", "l2": "entry",
    "mid": "mid", "midlevel": "mid", "l3": "mid", "l4": "mid", "ic3": "mid", "ic4": "mid",
    "senior": "senior", "sr": "senior", "l5": "senior", "ic5": "senior",
    "sde3": "senior", "p5": "senior",
    "staff": "staff", "lead": "staff", "l6": "staff", "ic6": "staff", "p6": "staff",
    "principal": "principal", "l7": "principal", "ic7": "principal", "p7": "principal",
}


# ---------------------------------------------------------------- storage
def data_path(args):
    return Path(os.path.expanduser(args.data)) if getattr(args, "data", None) else DEFAULT_DATA


def load(path):
    if not path.exists():
        return {"version": 1, "owner": None, "wins": [], "feedback": []}
    try:
        doc = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"[FATAL] {path} is not valid JSON: {e}")
    doc.setdefault("wins", [])
    doc.setdefault("feedback", [])
    return doc


def save(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")
    tmp.replace(path)


# ---------------------------------------------------------------- helpers
def parse_date(s):
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    sys.exit(f"[FATAL] bad date '{s}' — use YYYY-MM-DD")


def parse_period(spec):
    """2026 | 2026H2 | 2026Q4 | 2026-07-01:2026-12-31 | 90d | 12w"""
    if not spec:
        return None, None
    spec = spec.strip()
    m = __import__("re").fullmatch(r"(\d{4})", spec)
    if m:
        y = int(m.group(1))
        return dt.date(y, 1, 1), dt.date(y, 12, 31)
    m = __import__("re").fullmatch(r"(\d{4})[Hh]([12])", spec)
    if m:
        y, h = int(m.group(1)), int(m.group(2))
        return (dt.date(y, 1, 1), dt.date(y, 6, 30)) if h == 1 else (dt.date(y, 7, 1), dt.date(y, 12, 31))
    m = __import__("re").fullmatch(r"(\d{4})[Qq]([1-4])", spec)
    if m:
        y, q = int(m.group(1)), int(m.group(2))
        start = dt.date(y, 3 * q - 2, 1)
        end = (dt.date(y + (q == 4), [3, 6, 9, 12][q - 1] % 12 + 1, 1)) - dt.timedelta(days=1)
        return start, end
    if ":" in spec:
        a, b = spec.split(":", 1)
        return parse_date(a), parse_date(b)
    m = __import__("re").fullmatch(r"(\d+)([dw])", spec)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        end = dt.date.today()
        return end - dt.timedelta(days=n * (7 if unit == "w" else 1)), end
    sys.exit(f"[FATAL] bad period '{spec}' — try 2026, 2026H2, 2026Q4, 90d, or 2026-07-01:2026-12-31")


def in_period(win, period):
    start, end = parse_period(period) if period else (None, None)
    if start is None or end is None:
        return True
    d = parse_date(win.get("date", "1970-01-01"))
    return start <= d <= end


def compute_pct(before, after, direction):
    try:
        before, after = float(before), float(after)
    except (TypeError, ValueError):
        return None
    if before == 0:
        return None
    delta = (before - after) if direction == "down" else (after - before)
    return round(abs(delta) / abs(before) * 100, 1)


def impact_score(win):
    pct = win.get("impact_pct")
    if pct is None:
        return None
    return round(SCOPE_WEIGHT.get(win.get("scope"), 1.0) * min(float(pct), 100.0), 1)


def quality_flags(win):
    flags = []
    if win.get("impact_pct") is None and not win.get("qualitative"):
        flags.append("MISSING_METRIC")
    if not win.get("evidence"):
        flags.append("NO_EVIDENCE")
    if not win.get("axis"):
        flags.append("NO_AXIS")
    if win.get("scope") in (None, "self"):
        flags.append("SELF_SCOPE")
    return flags


def _num(v):
    """4200.0 -> '4200', 2.44 -> '2.44'"""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    return str(int(f)) if f.is_integer() else f"{f:g}"


def fmt_metric(win):
    if win.get("metric") and win.get("before") is not None:
        arrow = "→"
        return (f"{win['metric']} {_num(win['before'])}{arrow}{_num(win['after'])} "
                f"{win.get('unit','')}").strip()
    if win.get("impact_pct") is not None:
        return f"{_num(win['impact_pct'])}%"
    if win.get("qualitative"):
        return f"qualitative: {win['qualitative']}"
    return "—"


# ---------------------------------------------------------------- commands
def cmd_add(args):
    path = data_path(args)
    doc = load(path)
    if args.axis not in AXES:
        sys.exit(f"[FATAL] axis must be one of {AXES}")
    if args.scope not in SCOPES:
        sys.exit(f"[FATAL] scope must be one of {SCOPES}")
    d = parse_date(args.date) if args.date else dt.date.today()
    pct = args.impact_pct
    if pct is None and args.before is not None and args.after is not None:
        pct = compute_pct(args.before, args.after, args.direction)
    wid = f"w-{d.strftime('%Y%m%d')}-{len([w for w in doc['wins'] if w['date'] == d.isoformat()]) + 1:03d}"
    win = {
        "id": wid,
        "date": d.isoformat(),
        "title": args.title.strip(),
        "scope": args.scope,
        "axis": args.axis,
        "metric": args.metric,
        "before": args.before,
        "after": args.after,
        "unit": args.unit,
        "direction": args.direction,
        "impact_pct": pct,
        "qualitative": args.qualitative,
        "evidence": args.evidence or [],
        "stakeholders": args.stakeholder or [],
        "tags": args.tag or [],
        "status": args.status,
    }
    doc["wins"].append(win)
    save(path, doc)
    flags = quality_flags(win)
    print(f"[OK] {wid}  {win['title']}")
    print(f"     scope={win['scope']} axis={win['axis']} impact={fmt_metric(win)} score={impact_score(win)}")
    if flags:
        print(f"[WARN] incomplete: {', '.join(flags)} — patch it before review season:")
        print(f"       python3 {sys.argv[0]} patch {wid} --evidence URL --scope org")
    cov = axis_counts(doc["wins"])
    empty = [a for a in AXES if cov.get(a, 0) == 0]
    if empty:
        print(f"[INFO] axes with zero evidence: {', '.join(empty)}")


def cmd_list(args):
    doc = load(data_path(args))
    rows = [w for w in doc["wins"] if in_period(w, args.period)]
    if args.axis:
        rows = [w for w in rows if w.get("axis") == args.axis]
    if args.scope:
        rows = [w for w in rows if w.get("scope") == args.scope]
    if not rows:
        print("[INFO] no wins match.")
        return
    rows.sort(key=lambda w: (w["date"], w["id"]), reverse=True)
    for w in rows:
        s = impact_score(w)
        print(f"{w['date']}  {w['id']:<18} [{w['scope']:<7}/{w['axis']:<13}] "
              f"score={str(s):<6} {w['title']}")
        if w.get("evidence"):
            print(f"{'':12}evidence: {', '.join(w['evidence'][:2])}")
    print(f"\n{len(rows)} win(s).")


PATCHABLE = ["title", "scope", "axis", "metric", "before", "after", "unit",
             "direction", "impact_pct", "qualitative", "status"]


def cmd_patch(args):
    path = data_path(args)
    doc = load(path)
    hit = [w for w in doc["wins"] if w["id"] == args.id]
    if not hit:
        sys.exit(f"[FATAL] no win with id '{args.id}' — run `list` to get ids")
    win = hit[0]
    changed = []
    for f in PATCHABLE:
        v = getattr(args, f, None)
        if v is not None and v != win.get(f):
            win[f] = v
            changed.append(f)
    for f in ("evidence", "stakeholder", "tag"):
        v = getattr(args, f, None)
        if v:
            win[f] = sorted(set((win.get(f) or []) + v))
            changed.append(f)
    if win.get("before") is not None and win.get("after") is not None:
        win["impact_pct"] = compute_pct(win["before"], win["after"], win.get("direction", "down"))
    save(path, doc)
    print(f"[OK] patched {args.id}: {', '.join(changed) or 'nothing changed'}")
    flags = quality_flags(win)
    print(f"     flags: {', '.join(flags) if flags else 'clean'}")


def axis_counts(wins):
    out = {}
    for w in wins:
        out[w.get("axis", "?")] = out.get(w.get("axis", "?"), 0) + 1
    return out


def scope_counts(wins):
    out = {}
    for w in wins:
        out[w.get("scope", "?")] = out.get(w.get("scope", "?"), 0) + 1
    return out


def quarter_of(date_str):
    d = parse_date(date_str)
    return f"{d.year}Q{(d.month - 1) // 3 + 1}"


def cmd_stats(args):
    doc = load(data_path(args))
    wins = [w for w in doc["wins"] if in_period(w, args.period)]
    if not wins:
        print("[INFO] no wins in period.")
        return
    print(f"# Brag doc stats — {args.period or 'all time'}  ({len(wins)} wins)\n")
    print("## Axis coverage")
    ac = axis_counts(wins)
    for a in AXES:
        n = ac.get(a, 0)
        bar = "█" * min(n, 20)
        print(f"  {a:<14} {n:>3}  {bar}{'  ← GAP' if n == 0 else ''}")
    print("\n## Scope (impact radius)")
    sc = scope_counts(wins)
    for s in SCOPES:
        print(f"  {s:<10} {sc.get(s, 0):>3}")
    print("\n## By quarter")
    qs = {}
    for w in wins:
        qs[quarter_of(w["date"])] = qs.get(quarter_of(w["date"]), 0) + 1
    for q in sorted(qs):
        print(f"  {q}  {qs[q]:>3}  {'█' * qs[q]}")
    scored = [w for w in wins if impact_score(w) is not None]
    scored.sort(key=lambda w: impact_score(w) or 0.0, reverse=True)
    print("\n## Top 5 by impact score (scope × magnitude)")
    for w in scored[:5]:
        print(f"  {impact_score(w):>6}  {w['date']}  {w['title']}")
    for w in wins:
        if impact_score(w) is None and not w.get("qualitative"):
            print(f"\n[UNQUANTIFIED] {w['id']} {w['title']} — add before/after or mark --qualitative")
    print("\n## Data quality")
    flagged = [(w, quality_flags(w)) for w in wins]
    bad = [(w, f) for w, f in flagged if f]
    print(f"  complete: {len(wins) - len(bad)}/{len(wins)}")
    for w, f in bad:
        print(f"  {w['id']:<18} {', '.join(f)}")


def cmd_rollup(args):
    doc = load(data_path(args))
    wins = [w for w in doc["wins"] if in_period(w, args.period)]
    wins.sort(key=lambda w: (impact_score(w) or 0, w["date"]), reverse=True)
    if not wins:
        print(f"[INFO] no wins in {args.period}.")
        return
    print(f"### Evidence table — {args.period or 'all time'}\n")
    print("| Date | Win | Scope | Axis | Impact | Evidence |")
    print("|---|---|---|---|---|---|")
    for w in wins:
        ev = ", ".join(w.get("evidence") or []) or "**MISSING**"
        print(f"| {w['date']} | {w['title']} | {w['scope']} | {w['axis']} | {fmt_metric(w)} | {ev} |")
    ac = axis_counts(wins)
    print(f"\n**Coverage**: " + " · ".join(f"{a}={ac.get(a,0)}" for a in AXES))
    print(f"**Total**: {len(wins)} wins · org+ = {sum(1 for w in wins if w['scope'] in ('org','company'))}")


def normalize_level(raw):
    key = raw.strip().lower().replace("_", "").replace("-", "")
    if key in LEVELS:
        return key
    if key in ALIASES:
        return ALIASES[key]
    sys.exit(f"[FATAL] unknown level '{raw}'. Use: {', '.join(LEVELS)} (aliases: L5/IC5/P6...)")


def cmd_gaps(args):
    doc = load(data_path(args))
    wins = [w for w in doc["wins"] if in_period(w, args.period)]
    level = normalize_level(args.level)
    req = LEVELS[level]
    if args.levels:
        try:
            custom = json.loads(Path(os.path.expanduser(args.levels)).read_text())
            req = custom[level]
        except (OSError, KeyError, json.JSONDecodeError) as e:
            sys.exit(f"[FATAL] could not load levels file: {e}")
    team_level = [w for w in wins if w.get("scope") in ("team", "org", "company")]
    org_level = [w for w in wins if w.get("scope") in ("org", "company")]
    ac = axis_counts(wins)
    covered = [a for a in AXES if ac.get(a, 0) > 0]
    print(f"# Promotion gap analysis → {level.upper()}\n")
    print(f"Evidence window: {args.period or 'all time'} · {len(wins)} total wins\n")
    ok, partial, missing = [], [], []

    def check(label, have, need, target):
        if have >= need:
            ok.append(f"{label}: {have}/{need} ✅")
        elif have > 0:
            partial.append(f"{label}: {have}/{need} ⚠️  short by {need - have}")
        else:
            missing.append(f"{label}: 0/{need} ❌")

    check(f"Team-level+ wins (scope ≥ team)", len(team_level), req["team_min"], "team")
    check(f"Org-level+ wins (scope ≥ org)", len(org_level), req["org_min"], "org")
    check(f"Axis coverage ({', '.join(covered) or 'none'})", len(covered), req["axes_min"], "axes")

    if ok:
        print("## ✅ Supported by evidence")
        for x in ok:
            print(f"  - {x}")
    if partial:
        print("\n## ⚠️ Not enough evidence (you may have done it — just not recorded)")
        for x in partial:
            print(f"  - {x}")
    if missing:
        print("\n## ❌ Completely missing (real gap — build this or retarget)")
        for x in missing:
            print(f"  - {x}")
    empty_axes = [a for a in AXES if ac.get(a, 0) == 0]
    if empty_axes:
        print(f"\n**Empty axes**: {', '.join(empty_axes)}")
        print("  → one win per empty axis closes the gap faster than 10 more wins in a strong axis.")
    unquantified = [w for w in wins if w.get("impact_pct") is None and not w.get("qualitative")]
    if unquantified:
        print(f"\n**{len(unquantified)} unquantified win(s)** — committees discount these heavily:")
        for w in unquantified[:5]:
            print(f"  - {w['id']} {w['title']}")
    no_ev = [w for w in wins if not w.get("evidence")]
    if no_ev:
        print(f"\n**{len(no_ev)} win(s) with no evidence link** — attach PR/doc/dashboard:")
        for w in no_ev[:5]:
            print(f"  - {w['id']} {w['title']}")
    verdict = "READY" if not missing and not partial else ("CLOSE" if not missing else "NOT READY")
    print(f"\n**Verdict: {verdict}**")
    if verdict != "READY":
        print("Before submitting: ① quantify the ⚠️ items ② line up a witness per key win")
        print("③ brief your sponsor (no sponsor = no promotion, regardless of evidence)")


FEEDBACK_TEMPLATES = {
    "slack": (
        "Hey {to} — review season, and I'm asking a small group for input.\n"
        "Context: I worked on {about}{role}.\n\n"
        "Two questions, 2 minutes max — a sentence each is plenty:\n"
        "1. What specifically worked when we worked together on it?\n"
        "2. What's one thing I could do differently next time?\n\n"
        "No need to polish it — bullet fragments are perfect. Thanks."
    ),
    "email": (
        "Subject: Quick input for my review (2 min)\n\n"
        "Hi {to},\n\n"
        "I'm putting together my {period} self-review and your perspective would help.\n"
        "Context: {about}{role}.\n\n"
        "Two questions — one line each is more than enough:\n"
        "  1. What stood out about how I handled it?\n"
        "  2. What would you want me to do differently next time?\n\n"
        "No rush — end of next week is fine. Thanks,\n"
    ),
    "zh": (
        "嗨 {to}，评审季到了，想请你帮个小忙（2 分钟）。\n"
        "背景：我{period}主要在做{about}{role}。\n\n"
        "两个问题，一句话回答就行：\n"
        "1. 那次协作里，你觉得我哪一点做得比较到位？\n"
        "2. 有什么是我下次可以做得更好的？\n\n"
        "不用润色，碎片化的几句就够，谢谢！"
    ),
}


def cmd_feedback_ask(args):
    tpl = FEEDBACK_TEMPLATES.get(args.channel)
    if not tpl:
        sys.exit(f"[FATAL] channel must be one of {list(FEEDBACK_TEMPLATES)}")
    role = f"（你在其中的角色：{args.their_role}）" if args.their_role and args.channel == "zh" else (
        f" (you were on the {args.their_role} side)" if args.their_role else "")
    print(tpl.format(to=args.to, about=args.about, role=role, period=args.period or "this half"))
    print("\n---\n"
          "Rules that decide whether they reply:\n"
          "  • one positive + one improvement question (never 3+)\n"
          "  • give them the context so they don't have to remember\n"
          "  • say 'one line is fine' — lowers the cost of replying\n"
          "  • mention a soft deadline\n"
          "  • ask at most 4-5 people, and log who replied:\n"
          f"    python3 {sys.argv[0]} feedback-log --from '{args.to}' --text '...'")


def cmd_feedback_log(args):
    path = data_path(args)
    doc = load(path)
    doc["feedback"].append({
        "date": dt.date.today().isoformat(),
        "from": args.from_,
        "text": args.text,
        "about": args.about,
        "tone": "positive" if not args.negative else "improvement",
    })
    save(path, doc)
    print(f"[OK] feedback logged from {args.from_} (total {len(doc['feedback'])})")


def cmd_export(args):
    doc = load(data_path(args))
    wins = [w for w in doc["wins"] if in_period(w, args.period)]
    if args.format == "json":
        print(json.dumps({"period": args.period, "wins": wins, "feedback": doc["feedback"]},
                         ensure_ascii=False, indent=2))
    else:
        for w in sorted(wins, key=lambda x: x["date"]):
            print(f"- **{w['date']}** {w['title']} ({w['scope']}/{w['axis']}) — {fmt_metric(w)}")


def main():
    p = argparse.ArgumentParser(description="Brag doc / self-review / promo gap engine (local only)")
    p.add_argument("--data", help="override brag.json path")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="log one win")
    a.add_argument("--title", required=True)
    a.add_argument("--date")
    a.add_argument("--scope", default="team", choices=SCOPES)
    a.add_argument("--axis", required=True, choices=AXES)
    a.add_argument("--metric")
    a.add_argument("--before", type=float)
    a.add_argument("--after", type=float)
    a.add_argument("--unit", default="")
    a.add_argument("--direction", default="down", choices=["up", "down"])
    a.add_argument("--impact-pct", type=float)
    a.add_argument("--qualitative", help="use when no honest number exists")
    a.add_argument("--evidence", action="append")
    a.add_argument("--stakeholder", action="append")
    a.add_argument("--tag", action="append")
    a.add_argument("--status", default="shipped")
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list")
    l.add_argument("--period")
    l.add_argument("--axis", choices=AXES)
    l.add_argument("--scope", choices=SCOPES)
    l.set_defaults(func=cmd_list)

    pt = sub.add_parser("patch", help="fill in fields you skipped earlier")
    pt.add_argument("id")
    pt.add_argument("--title")
    pt.add_argument("--scope", choices=SCOPES)
    pt.add_argument("--axis", choices=AXES)
    pt.add_argument("--metric")
    pt.add_argument("--before", type=float)
    pt.add_argument("--after", type=float)
    pt.add_argument("--unit")
    pt.add_argument("--direction", choices=["up", "down"])
    pt.add_argument("--impact-pct", type=float)
    pt.add_argument("--qualitative")
    pt.add_argument("--evidence", action="append")
    pt.add_argument("--stakeholder", action="append")
    pt.add_argument("--tag", action="append")
    pt.add_argument("--status")
    pt.set_defaults(func=cmd_patch)

    s = sub.add_parser("stats")
    s.add_argument("--period")
    s.set_defaults(func=cmd_stats)

    r = sub.add_parser("rollup")
    r.add_argument("--period")
    r.set_defaults(func=cmd_rollup)

    g = sub.add_parser("gaps")
    g.add_argument("--level", required=True)
    g.add_argument("--period")
    g.add_argument("--levels", help="JSON file overriding LEVELS")
    g.set_defaults(func=cmd_gaps)

    f = sub.add_parser("feedback-ask")
    f.add_argument("--to", required=True)
    f.add_argument("--about", required=True)
    f.add_argument("--their-role")
    f.add_argument("--period")
    f.add_argument("--channel", default="slack", choices=list(FEEDBACK_TEMPLATES))
    f.set_defaults(func=cmd_feedback_ask)

    fl = sub.add_parser("feedback-log")
    fl.add_argument("--from", dest="from_", required=True)
    fl.add_argument("--text", required=True)
    fl.add_argument("--about")
    fl.add_argument("--negative", action="store_true")
    fl.set_defaults(func=cmd_feedback_log)

    e = sub.add_parser("export")
    e.add_argument("--period")
    e.add_argument("--format", default="md", choices=["md", "json"])
    e.set_defaults(func=cmd_export)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
