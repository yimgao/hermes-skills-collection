# Canvas Sections — 8-Section Spec

Every canvas has exactly these 8 sections, in this order. The validator enforces it.

---

## 1. `🎯 Goal`

**One sentence. One verifiable artifact.**

Bad:
- "Work on the launch deck"
- "Improve onboarding"

Good:
- "Ship Launch Deck v3 and get budget sign-off at the Q3 review."
- "Cut onboarding time-to-first-value from 11 min to under 3 min."

Why: if you can't write the Goal in one sentence, the project is actually a theme, not a project. Ask the user to split it.

---

## 2. `📐 Scope`

Three explicit sub-lists:

| Sub-list | Meaning | Example |
|---|---|---|
| **In** | What this project *will* do | "Redesign slide 7 with actuals" |
| **Out** | What it *could* do but won't | "No new animation system this quarter" |
| **Non-goals** | Explicitly not the project's job | "Not responsible for data cleanup — that's finance's track" |

Non-goals are the anti-scope-creep seatbelt. If a request can't find a home in **In**, it belongs in **Out** or **Non-goals** or a new canvas.

---

## 3. `🎯 Current Focus`

The heart of the canvas. **Two lines, both non-empty:**

```
> 当前在做：<verb + object>
> 下一动作：<verb + object + success criterion>
```

Rules:
- Exactly one verb per line. "Working on a bunch of things" → split.
- "Next move" must be doable in ≤ 90 minutes. If not, break it down.
- Update this multiple times a day. It is the answer to *"wait, where was I?"*

Bad next move: "Continue deck."
Good next move: "Draft slide 7 using Sarah's actuals from `actuals-2026-09.xlsx` — 30 min, then self-review."

---

## 4. `🔁 Open Loops`

Things you **opened but didn't close**. Usually things waiting on other people.

Format:

```
- [ ] [id#01] Ask Marcus for the pricing-tier copy — opened 2026-10-04
- [x] [id#02] Get finance's sign-off on the spend — opened 2026-09-28, closed 2026-10-02
```

Rules:
- `id#` must be **unique within the canvas**. Start at `01`, increment.
- 30 days open → forced triage: close, defer, or escalate.
- Closed loops stay in the list (marked `[x]`) for one week, then may be pruned.

---

## 5. `🧾 Decisions`

Append-only. Each entry links to a `decision-journal` file (or, if no journal exists yet, at least a date + one-line rationale).

Format:

```
- 2026-10-07 — Ship with naive retry (3x, exponential backoff) → `decision-journal/dec-2026-10-07-retry-strategy.md`
```

Rules:
- Never edit a past decision line. If reversed, append a new line: `- 2026-10-09 — REVISE: bump retry to 5x → `dec-2026-10-09-retry-revision.md``
- The canvas *points*; the journal *holds* the reasoning. Don't duplicate.
- If `decision-journal` doesn't exist, the agent offers to create it via that skill.

---

## 6. `🚧 Blockers`

Four fixed sub-headings. Nothing goes here that isn't actively blocking forward motion.

| Sub-heading | Meaning |
|---|---|
| **You** | You haven't done the thing you need to do |
| **Them** | Someone else owes you something |
| **Waiting** | Async — waiting on an external process/system |
| **Unclear** | You don't yet know what's blocking — treat as a research loop |

A blocker that's really an opinion or a risk belongs in the Parking Lot, not here.

---

## 7. `🅿️ Parking Lot`

Ideas, snippets, half-thoughts. Now-safe, later-unknown.

Format: `- [YYYY-MM-DD HH:MM] <text>`

Rules:
- Every entry gets a timestamp. No exceptions.
- Triage cadence: every 14 days, walk the lot. Each entry → **delete / promote to Open Loop / promote to Decisions / keep**.
- The Parking Lot is an input buffer, not storage. Anything sitting > 60 days is dead — delete it.

---

## 8. `📓 Log`

Diary. One `## YYYY-MM-DD` heading per day. Free-form bullets under each.

Format:

```markdown
## 2026-10-10
- 47-min focus block on the webhook retry backoff math
- ↩ switched to `alpha`
- ⚠ loop #03 now 31d old
```

Rules:
- **One-line entries.** If it needs 5 paragraphs, it's a meeting note → use `meeting-minutes-generator`, then link.
- Never rewrite a prior day's entry. Append as `- (edit) …` if correction needed.
- Weekly snapshot writes a `## Snapshot — week-of YYYY-MM-DD` block. Also append-only.

---

## Section Order (validator-enforced)

```
1. 🎯 Goal
2. 📐 Scope
3. 🎯 Current Focus
4. 🔁 Open Loops
5. 🧾 Decisions
6. 🚧 Blockers
7. 🅿️ Parking Lot
8. 📓 Log
```

Any canvas whose headings are out of order, missing, or duplicated fails `scripts/validate.py`.
