#!/usr/bin/env python3
"""
test_sm2.py — verification harness for scripts/sm2.py (Step 3.5).

Run:  python3 scripts/test_sm2.py
Exits 0 on success, 1 on any failure. 25 assertions, no network, no deps.

This imports the SHIPPED sm2.py — so a passing run proves the code in the
skill actually works, not a copy of it that drifted.
"""
import json
import os
import sys
import tempfile
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sm2 import (MAX_INTERVAL, MIN_EF, due_queue, forecast, leeches,  # noqa: E402
                 new_card, retention, sm2_review)

fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    if not ok:
        fails += 1
    print(f"{'PASS' if ok else 'FAIL'} {label}: got={got} want={want}")


t0 = date(2026, 8, 29)

# T1 — fresh card, perfect recall
c = new_card("c1", "What is SM-2?", "A spaced repetition scheduling algorithm")
sm2_review(c, 5, t0)
check("T1 first-rep interval", c["interval"], 1)
check("T1 first-rep due", c["due"], "2026-08-30")
check("T1 ef rises on q=5", c["ef"], 2.6)

# T2 — second success uses SM-2's fixed 6-day step
sm2_review(c, 4, t0 + timedelta(days=1))
check("T2 second-rep interval", c["interval"], 6)
check("T2 reps", c["reps"], 2)

# T3 — third rep multiplies by EF
ef_before = c["ef"]
sm2_review(c, 4, t0 + timedelta(days=7))
check("T3 third interval == round(6*ef)", c["interval"], round(6 * ef_before))

# T4 — lapse resets scheduling, increments lapse counter
sm2_review(c, 1, t0 + timedelta(days=20))
check("T4 lapse interval reset", c["interval"], 1)
check("T4 lapse reps reset", c["reps"], 0)
check("T4 lapses counted", c["lapses"], 1)

# T5 — EF floor holds under sustained "hard but passing"
h = new_card("c2", "hard", "card")
for i in range(30):
    sm2_review(h, 3, t0 + timedelta(days=i))
check("T5 ef floor 1.3", h["ef"], 1.3)
check("T5 ef never below floor", h["ef"] >= MIN_EF, True)

# T6 — EF ceiling AND interval cap (regression: OverflowError on date.max)
e = new_card("c3", "easy", "card")
for i in range(30):
    sm2_review(e, 5, t0 + timedelta(days=i))
check("T6 ef ceiling 2.7", e["ef"], 2.7)
check("T6 interval capped at MAX_INTERVAL", e["interval"], MAX_INTERVAL)
check("T6 due date valid (no overflow)", e["due"] > "2026-08-29", True)

# T7 — leech detection at threshold
L = new_card("c4", "leech", "card")
for i in range(8):
    sm2_review(L, 0, t0 + timedelta(days=i))
check("T7 leech lapses", L["lapses"], 8)
check("T7 leech flagged", L["leech"], True)
check("T7 leeches() finds it", [x["id"] for x in leeches([c, h, L])], ["c4"])

# T8 — queue ordering: overdue-first, then hardest-first, limit honored
cards = [
    dict(new_card("a", "a", "a"), due="2026-08-20", ef=2.5),
    dict(new_card("b", "b", "b"), due="2026-08-20", ef=1.6),
    dict(new_card("c", "c", "c"), due="2026-08-29"),
    dict(new_card("d", "d", "d"), due="2026-09-15"),
]
q = due_queue(cards, t0, limit=10)
check("T8 future cards excluded", len(q), 3)
check("T8 hardest-first within same due date", [x["id"] for x in q], ["b", "a", "c"])
check("T8 limit honored", len(due_queue(cards, t0, limit=2)), 2)

# T9 — retention math
r = retention([c, h, L])
check("T9 retention is a percentage", 0 <= r["retention_pct"] <= 100, True)
print(f"     (reviews={r['reviews']}, retention={r['retention_pct']}%)")
check("T9 unreviewed deck → None", retention([new_card("z", "z", "z")])["retention_pct"], None)

# T10 — input validation
try:
    sm2_review(new_card("x", "x", "x"), 9, t0)
    check("T10 rejects q=9", "no-raise", "ValueError")
except ValueError:
    check("T10 rejects q=9", "ValueError", "ValueError")

# T11 — JSON persistence round-trip
with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, "cards.json")
    with open(p, "w") as f:
        json.dump({"cards": cards}, f, indent=2)
    with open(p) as f:
        back = json.load(f)
    check("T11 json round-trip", len(back["cards"]), 4)

# T12 — workload forecast
f = forecast(cards, t0)
check("T12 forecast day0 count", f["2026-08-29"], 1)
check("T12 forecast horizon len", len(f), 14)

print("\n" + ("ALL TESTS PASSED" if fails == 0 else f"{fails} FAILURES"))
sys.exit(1 if fails else 0)
