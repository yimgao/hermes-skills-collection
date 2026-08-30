# Review Session — {{DATE}}

**Deck:** {{DECK}}  ·  **Reviewed:** {{N}} cards  ·  **Duration:** {{MINUTES}} min

---

## Session Result

| Metric | Value |
|--------|-------|
| Cards reviewed | {{N}} |
| Correct (q≥3) | {{N_CORRECT}} ({{SESSION_RETENTION}}%) |
| Lapsed (q<3) | {{N_LAPSED}} |
| Avg grade | {{AVG_Q}} |
| New leeches flagged | {{N_NEW_LEECHES}} |

## Grade Distribution

```
q5 ████████ {{N_Q5}}
q4 █████    {{N_Q4}}
q3 ███      {{N_Q3}}
q2 █        {{N_Q2}}
q1          {{N_Q1}}
q0          {{N_Q0}}
```

## Lapsed Cards — Review These Tomorrow

| Card | Front | Lapses | Diagnosis |
|------|-------|--------|-----------|
| {{ID}} | {{FRONT}} | {{LAPSES}} | {{WHY_ITS_FAILING}} |

## ⚠ Leeches — Fix the Card, Don't Grind It

| Card | Front | Lapses | Recommended action |
|------|-------|--------|--------------------|
| {{ID}} | {{FRONT}} | {{LAPSES}} | {{split / rewrite / add mnemonic / suspend}} |

## Upcoming Workload

```
{{DATE+1}}  ████ {{N}}
{{DATE+2}}  ██   {{N}}
{{DATE+3}}  ████████ {{N}}   ← spike, consider spreading new cards
```

## Coach Notes

- **Retention:** {{RETENTION}}% lifetime vs {{TARGET}}% target → {{verdict}}
- **Grading honesty check:** {{flag if >70% of grades are 5}}
- **Next action:** {{one concrete thing to do before the next session}}

---

*Data: `~/.hermes/data/srs/cards.json` · Scheduler: SM-2 · All local, no cloud.*
