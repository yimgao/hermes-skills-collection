#!/usr/bin/env python3
"""
sm2.py — SM-2 spaced-repetition scheduler for spaced-repetition-coach.

Pure Python stdlib. No pandas, no numpy, no network.
Every function here is covered by scripts/test_sm2.py (25 assertions).

Usage:
    python3 sm2.py due                       # show today's review queue
    python3 sm2.py add "front" "back" [deck]  # add a card
    python3 sm2.py grade <card-id> <0-5>      # grade a review
    python3 sm2.py stats                      # retention + leech report
    python3 sm2.py forecast [days]            # upcoming workload

Storage: ~/.hermes/data/srs/cards.json  (override with SRS_PATH)
"""
import json
import os
import sys
from datetime import date, timedelta

# --- Tuning constants -------------------------------------------------------
MIN_EF, MAX_EF, START_EF = 1.3, 2.7, 2.5
LEECH_THRESHOLD = 8        # lapses before a card is flagged as a leech
MAX_INTERVAL = 3650        # 10y cap. REQUIRED: without it, repeated q=5
                           # overflows date.max and raises OverflowError.
DEFAULT_DAILY_LIMIT = 20

DATA_PATH = os.path.expanduser(
    os.environ.get("SRS_PATH", "~/.hermes/data/srs/cards.json")
)


# --- Storage ----------------------------------------------------------------
def load():
    if not os.path.exists(DATA_PATH):
        return {"cards": [], "settings": {"daily_limit": DEFAULT_DAILY_LIMIT}}
    with open(DATA_PATH) as f:
        return json.load(f)


def save(db):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


# --- Core scheduler ---------------------------------------------------------
def new_card(cid, front, back, deck="default"):
    """Create an unseen card, due today."""
    return {
        "id": cid, "front": front, "back": back, "deck": deck,
        "ef": START_EF, "reps": 0, "interval": 0, "lapses": 0,
        "due": date.today().isoformat(), "leech": False, "history": [],
    }


def sm2_review(card, quality, today=None):
    """Advance one card by SM-2 (Wozniak 1987). quality: 0..5.

    0-2 = lapse (reset to relearning), 3 = hard, 4 = good, 5 = easy.
    Mutates and returns the card dict.
    """
    if not 0 <= quality <= 5:
        raise ValueError("quality must be 0..5")
    today = today or date.today()
    ef = card.get("ef", START_EF)
    reps = card.get("reps", 0)
    interval = card.get("interval", 0)

    if quality < 3:
        # Lapse: back to relearning. EF is deliberately NOT punished here —
        # SM-2 punishes via the reset, and double-punishing drives EF to the
        # floor after two bad days and never recovers.
        card["lapses"] = card.get("lapses", 0) + 1
        reps, interval = 0, 1
    else:
        ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ef = max(MIN_EF, min(MAX_EF, ef))
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = round(interval * ef)
        interval = min(interval, MAX_INTERVAL)
        reps += 1

    card.update(
        ef=round(ef, 3), reps=reps, interval=interval,
        last_review=today.isoformat(),
        due=(today + timedelta(days=interval)).isoformat(),
        history=card.get("history", []) + [{"d": today.isoformat(), "q": quality}],
    )
    card["leech"] = card.get("lapses", 0) >= LEECH_THRESHOLD
    return card


def due_queue(cards, today=None, limit=DEFAULT_DAILY_LIMIT, deck=None):
    """Overdue-first, then hardest-first (lowest EF). Deterministic ordering."""
    today = (today or date.today()).isoformat()
    due = [c for c in cards if c["due"] <= today and not c.get("suspended")]
    if deck:
        due = [c for c in due if c["deck"] == deck]
    due.sort(key=lambda c: (c["due"], c["ef"], c["id"]))
    return due[:limit]


def retention(cards):
    """Aggregate true retention: % of graded reviews with q>=3."""
    all_q = [h["q"] for c in cards for h in c["history"]]
    if not all_q:
        return {"reviews": 0, "retention_pct": None}
    good = sum(1 for q in all_q if q >= 3)
    return {"reviews": len(all_q), "retention_pct": round(100 * good / len(all_q), 1)}


def leeches(cards):
    """Cards that keep lapsing — candidates for rewrite/split/suspend."""
    return sorted(
        [c for c in cards if c.get("lapses", 0) >= LEECH_THRESHOLD],
        key=lambda c: -c["lapses"],
    )


def forecast(cards, today=None, days=14):
    """Cards due per day over the next N days — spot workload spikes early."""
    today = today or date.today()
    out = {}
    for i in range(days):
        d = (today + timedelta(days=i)).isoformat()
        out[d] = sum(1 for c in cards if c["due"] == d)
    return out


def next_id(cards):
    nums = [int(c["id"][1:]) for c in cards if c["id"][1:].isdigit()]
    return f"c{max(nums) + 1 if nums else 1}"


# --- CLI --------------------------------------------------------------------
def main(argv):
    cmd = argv[1] if len(argv) > 1 else "due"
    db = load()
    cards = db["cards"]

    if cmd == "add":
        front, back = argv[2], argv[3]
        deck = argv[4] if len(argv) > 4 else "default"
        c = new_card(next_id(cards), front, back, deck)
        cards.append(c)
        save(db)
        print(f"added {c['id']} to deck '{deck}' — due {c['due']}")

    elif cmd == "grade":
        cid, q = argv[2], int(argv[3])
        card = next((c for c in cards if c["id"] == cid), None)
        if not card:
            print(f"no such card: {cid}"); return 1
        sm2_review(card, q)
        save(db)
        flag = "  ⚠ LEECH" if card["leech"] else ""
        print(f"{cid}: q={q} → interval {card['interval']}d, "
              f"EF {card['ef']}, next {card['due']}{flag}")

    elif cmd == "due":
        limit = db.get("settings", {}).get("daily_limit", DEFAULT_DAILY_LIMIT)
        q = due_queue(cards, limit=limit)
        if not q:
            print("Nothing due today. 🎉"); return 0
        print(f"{len(q)} card(s) due:\n")
        for c in q:
            od = (date.today() - date.fromisoformat(c["due"])).days
            tag = f"  (overdue {od}d)" if od > 0 else ""
            print(f"  [{c['id']}] {c['front']}{tag}")

    elif cmd == "stats":
        r = retention(cards)
        lc = leeches(cards)
        print(f"cards:      {len(cards)}")
        print(f"reviews:    {r['reviews']}")
        print(f"retention:  {r['retention_pct']}%"
              if r["retention_pct"] is not None else "retention:  n/a")
        print(f"leeches:    {len(lc)}")
        for c in lc[:5]:
            print(f"  ⚠ [{c['id']}] {c['lapses']} lapses — {c['front'][:50]}")

    elif cmd == "forecast":
        days = int(argv[2]) if len(argv) > 2 else 14
        for d, n in forecast(cards, days=days).items():
            print(f"{d}  {'█' * min(n, 40)} {n}")

    else:
        print(__doc__); return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
