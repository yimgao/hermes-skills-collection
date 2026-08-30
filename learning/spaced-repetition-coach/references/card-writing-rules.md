# Card Writing Rules — Reference

A scheduler can only space what's written well. Most "I keep forgetting this
card" problems are **card-design bugs**, not memory failures. These rules come
from Piotr Wozniak's *20 rules of formulating knowledge* plus Anki community
practice, condensed to what the agent should actively enforce when creating or
repairing cards.

---

## The 6 rules the agent must enforce

### 1. One fact per card (minimum information principle)

The single highest-impact rule. Multi-fact cards produce partial recall, which
is ungradeable — you knew 3 of 5, so is that a 2 or a 4?

| ❌ Bad | ✅ Good |
|--------|---------|
| Q: List the 4 ACID properties | 4 separate cloze cards, one per property |
| Q: What are TCP's guarantees and UDP's tradeoffs? | Q: Does TCP guarantee ordering? / Q: Does UDP retransmit lost packets? |

**Enforcement:** if a card's answer contains a comma-separated list or a
numbered list of 3+ items, split it. This is the #1 cause of leeches.

### 2. Cloze deletion beats Q&A for facts in context

Cloze keeps the surrounding sentence as a retrieval cue, which is how the fact
will actually be needed.

```
❌ Q: What port does PostgreSQL use?   A: 5432
✅ PostgreSQL listens on port {{5432}} by default.
```

### 3. Avoid sets; prefer enumerations with cues

Unordered sets ("name the 5 X") have no retrieval cue, so recall order is
random and grading is noisy. If you must learn a set, give each item a distinct
hook or learn it as an ordered sequence with a mnemonic.

### 4. No "yes/no" cards

A binary question is 50% guessable, so a correct answer carries almost no
information about whether you actually know it.

```
❌ Q: Is Redis single-threaded?   A: Yes
✅ Q: How many threads execute Redis command processing?   A: One
```

### 5. Personalize and make it concrete

Cards tied to something you did are recalled far better than abstract
definitions. Prefer the example you hit in production over the textbook line.

```
❌ Q: What is a race condition?   A: When concurrent access order affects results
✅ Q: What bug made our webhook double-charge in March?   A: Two workers read
   the same unprocessed row before either marked it done — missing SELECT FOR UPDATE
```

### 6. Never memorize what you can derive or look up

Reference material (exact API signatures, full config schemas, rarely-used
flags) belongs in notes, not a review queue. Cards are for things you need
**instantly, from memory, repeatedly**.

**Rule of thumb:** if you'd happily `grep` for it mid-task, don't card it.

---

## Card-quality triage table

Use this when a card shows up as a leech (`sm2.py stats`):

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| You recall part of the answer every time | Multi-fact card | Split (rule 1) |
| "Correct" is ambiguous — you're unsure how to grade | Vague question | Rewrite with one unambiguous target |
| You know it in context but not on the card | No retrieval cue | Convert to cloze (rule 2) |
| Fact is arbitrary (a date, a port, a name) | No hook | Add mnemonic or etymology |
| Two cards keep interfering with each other | Similar cards, "interference" | Make the distinguishing feature explicit in both |
| You never actually need it | Shouldn't be a card | Suspend or delete (rule 6) |

**Interference** is the subtle one: near-identical cards (e.g. `SIGTERM=15` and
`SIGKILL=9`) cause each other's failures. The fix is to make each card's cue
carry the discriminating detail ("Which signal can a process trap?"), not to
review both harder.

---

## Deck structure

| Guideline | Why |
|-----------|-----|
| One deck per domain, not per source | You retrieve by topic, not by which book it came from |
| 20–200 cards per deck | Under 20, spacing is pointless; over ~200, split by subtopic |
| Add ≤10 new cards/day | Each new card generates ~8–10 future reviews; adding 50 today buys a 400-review day next month |
| Never bulk-import someone else's deck | Cards you didn't write have no personal cue and leech immediately (rule 5) |

The daily-limit setting in `cards.json` (`settings.daily_limit`) exists to
enforce the third row — it caps the *review* queue, but the agent should also
push back when a user tries to add 100 cards in one session.

---

## Sources

- Wozniak, "Effective learning: Twenty rules of formulating knowledge" (1999) —
  https://super-memory.com/articles/20rules.htm
- Anki Manual, "Editing and More" / "Leeches" — https://docs.ankiweb.net/
- Nielsen, "Augmenting Long-term Memory" (2018) — http://augmentingcognition.com/ltm.html

These are published pedagogical guidelines, not claims measured by this skill.
