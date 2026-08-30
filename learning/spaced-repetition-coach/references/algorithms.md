# Spaced Repetition Algorithms — Reference

Condensed math + decision rules behind `scripts/sm2.py`. Read this instead of
re-deriving from the SKILL.md when you need to change one formula.

---

## 1. Why spacing works

The **spacing effect** (Ebbinghaus, 1885) — review at expanding intervals beats
massed repetition. The **forgetting curve** predicts retrievability decays
roughly exponentially with time since last recall:

```
R(t) = e^(-t/S)
```

- `R` = probability of recall
- `t` = days since last review
- `S` = memory stability (grows each successful review)

The scheduler's whole job: **review each card at the moment `R` is about to
drop below your target retention** (usually 0.90). Earlier = wasted time.
Later = relearn from scratch.

---

## 2. SM-2 (implemented in `sm2.py`)

SuperMemo 2, Wozniak 1987. Still the best accuracy-per-line-of-code option
and the default in Anki for 30+ years.

### State per card

| Field | Meaning | Init |
|-------|---------|------|
| `ef` | Ease factor — how "easy" this card is | `2.5` |
| `interval` | Days until next review | `0` |
| `reps` | Consecutive successful reviews | `0` |
| `lapses` | Lifetime count of failures | `0` |

### Grading scale (0–5)

| q | Meaning | Effect |
|---|---------|--------|
| 0 | Total blackout | lapse |
| 1 | Wrong; answer felt familiar | lapse |
| 2 | Wrong; answer was on the tip of the tongue | lapse |
| 3 | Correct, but with serious difficulty | pass, EF drops |
| 4 | Correct after hesitation | pass, EF ~flat |
| 5 | Instant, perfect recall | pass, EF rises |

**The 3/4 boundary is the one that matters.** Users who grade everything 5
get intervals that outrun their actual memory; users who grade honest 3s get
a schedule that tracks reality. Coach for honesty over optimism.

### Interval progression

```
if q < 3:                    # lapse
    reps = 0
    interval = 1             # relearn tomorrow
    lapses += 1
    # EF deliberately NOT decremented — see note below
else:
    EF = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
    EF = clamp(EF, 1.3, 2.7)
    interval = 1   if reps == 0
             = 6   if reps == 1
             = round(interval * EF)   otherwise
    interval = min(interval, MAX_INTERVAL)
    reps += 1
```

EF deltas from the formula:

| q | ΔEF |
|---|-----|
| 3 | −0.14 |
| 4 | 0.00 |
| 5 | +0.10 |

### Three non-obvious implementation rules

1. **`MAX_INTERVAL` is mandatory, not cosmetic.** Without a cap, ~30
   consecutive q=5 grades produce an interval beyond `datetime.date.max` and
   `sm2.py` raises `OverflowError: date value out of range`. This was caught
   by `test_sm2.py` T6 during authoring. 3650 days (10y) is the ship default.
2. **Don't punish EF on a lapse.** Classic SM-2 resets the repetition count,
   which is punishment enough. Implementations that *also* subtract from EF
   drive it to the 1.3 floor after two bad days and it never recovers — the
   card then reviews daily forever.
3. **EF floor of 1.3 is load-bearing.** Below it, intervals stop growing
   meaningfully (1.3× per rep) and the deck becomes a treadmill. A card
   pinned at 1.3 is a signal to **rewrite the card**, not to keep grinding.

---

## 3. Leeches

A **leech** is a card you keep failing — it consumes review time and returns
nothing. Anki's default threshold is 8 lapses; `sm2.py` matches it.

**Fix the card, don't grind it.** Four remedies, in order of preference:

| Remedy | When |
|--------|------|
| **Split** | Card asks for 2+ facts at once ("List all 5 X") → make 5 cards |
| **Rewrite** | Question is ambiguous, so "correct" is unclear |
| **Add a mnemonic/context** | Fact is arbitrary (dates, names, port numbers) |
| **Suspend / delete** | You don't actually need it — be honest |

---

## 4. FSRS (the modern alternative)

Free Spaced Repetition Scheduler — the default in Anki 23.10+. Replaces SM-2's
single `ef` with a 3-component memory model (**D**ifficulty, **S**tability,
**R**etrievability) and 17+ weights fit to review history.

| | SM-2 | FSRS |
|---|------|------|
| State per card | 1 value (`ef`) | 3 values (D, S, R) |
| Params | 0 (fixed formula) | 17+ (fit per user) |
| Needs training data | No | Yes — ~1000 reviews |
| Reviews to hit 90% retention | baseline | ~20–30% fewer |
| Implementable in ~80 lines | Yes | No |

**Why this skill ships SM-2:** FSRS's advantage only materializes after ~1000
graded reviews to fit weights against. A user starting a deck today gets
identical scheduling from both for the first several weeks, and SM-2 needs no
training data, no optimizer, and no dependencies. Migrate to FSRS (via Anki
proper) once a deck has real history — the `history[]` array in `cards.json`
preserves the `(date, quality)` pairs FSRS needs, so no data is lost.

---

## 5. Target retention tuning

| Target | Effect | Good for |
|--------|--------|----------|
| 0.80 | Fewer reviews, more forgetting | Large low-stakes decks (trivia, vocab breadth) |
| 0.90 | Default; balanced | Most study goals |
| 0.95 | Many more reviews per card | Exam in <30 days, licensing, high-stakes |

Higher retention costs superlinearly — going 0.90 → 0.95 roughly doubles daily
reviews for a ~5pp accuracy gain. Only buy it near a hard deadline.

---

## Sources

- Ebbinghaus, *Über das Gedächtnis* (1885) — forgetting curve
- Wozniak & Gorzelanczyk, "Optimization of repetition spacing" (1994) — SM-2
- SuperMemo, "Algorithm SM-2" — https://super-memory.com/english/ol/sm2.htm
- Anki Manual, "Leeches" & "FSRS" — https://docs.ankiweb.net/
- open-spaced-repetition/fsrs4anki — FSRS reference implementation

All formulas above are reproduced from published algorithm descriptions, not
measured by this skill. Interval numbers in SKILL.md examples come from actual
`scripts/test_sm2.py` runs.
