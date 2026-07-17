---
name: bookshelf
description: "Track everything you read — books, articles, papers, audiobooks, longform. Log by natural language, capture quotes & notes, rate, see reading streaks & stats, get a yearly reading recap. All data local in JSON, zero cloud."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lifestyle, reading, books, knowledge-management, notes, quotes, learning, lifelong-learning, journal]
    related_skills: [habit-tracker, personal-crm, flashcard-generator, arxiv-paper-summarizer, web-clipper]
---

# 📚 Bookshelf — 个人阅读追踪器

> Track every book, article, paper, and longform you read. Log a book in plain English, capture quotes and notes, build a personal knowledge archive, see your reading streaks, and end the year with a beautiful recap. 把读过的书、读一半的书、想读的书、随手存的文章全部装进你的私人书架。

---

## Overview

Most people forget 90% of what they read within a month. **Bookshelf** turns Hermes into a private reading companion that remembers every book, every quote, every insight — and helps you actually revisit and apply what you've read.

Unlike Goodreads (owned by Amazon, public by default, algorithm-driven) or Readwise ($8/mo, cloud-only), this skill is **personal, private, and local**. Your reading history is yours.

| Capability | Description |
|------------|-------------|
| **Add by NL** | "Add *Project Hail Mary* by Andy Weir, started today" — parsed automatically |
| **Multi-format** | Books, articles, papers, Substack posts, blog series, audiobooks, comics |
| **Status tracking** | `to-read` / `reading` / `finished` / `abandoned` / `re-reading` |
| **Quotes & notes** | Capture memorable passages + free-form notes per book |
| **Rating** | 1–5 stars + tag system (fiction/non-fiction, topic, mood) |
| **Reading sessions** | Log start/end dates, page counts, daily minutes |
| **Streaks & stats** | Current/longest reading streak, books/year, pages/year, pace |
| **Yearly recap** | "Your 2026 in books" — auto-generated December summary |
| **Discovery** | "What should I read next?" — surface old `to-read` items + gap analysis |
| **Re-read reminders** | Surface books from N years ago to re-engage |
| **Quote search** | Find that one passage you remember but can't place |
| **Local-only** | All data at `~/.hermes/bookshelf/` — JSON + Markdown notes |

---

## When to Use

- *"Add Project Hail Mary to my shelf — I just started it"*
- *"I finished Atomic Habits today, 4 stars, non-fiction"*
- *"I just read this article: https://paulgraham.com/do.html — save it"*
- *"Log a quote from page 87 of Sapiens: 'You can't reason with a lie'"*
- *"How many books have I read this year?"*
- *"Show my reading streak"*
- *"What's still on my to-read list?"*
- *"Find me that quote about compound interest from one of my books"*
- *"I haven't read anything in 2 weeks — give me a 1-hour recommendation from my to-read list"*
- *"Generate my 2026 year-end reading recap"*
- *"What books did I abandon and why?"*
- *"Show me all the books I read in 2024 that were 5 stars"*
- *"I want to read 24 books this year — am I on pace?"*
- *"Surface one quote from my shelf every morning"*

---

## Core Workflow

### Step 1: Initialize the Local Database

The first time the user mentions reading/books/articles, ensure the data directory exists:

```bash
mkdir -p ~/.hermes/bookshelf
mkdir -p ~/.hermes/bookshelf/quotes
mkdir -p ~/.hermes/bookshelf/recaps
```

**`books.json` schema:**

```json
{
  "books": [
    {
      "id": "bk_001",
      "title": "Project Hail Mary",
      "subtitle": null,
      "authors": ["Andy Weir"],
      "format": "book",
      "isbn": "978-0593135204",
      "cover_url": null,
      "language": "en",
      "page_count": 478,
      "year_published": 2021,
      "status": "finished",
      "rating": 5,
      "tags": ["fiction", "sci-fi", "space", "problem-solving"],
      "topics": ["physics", "first-contact", "engineering"],
      "started_at": "2026-07-01",
      "finished_at": "2026-07-09",
      "sessions": [
        {"date": "2026-07-01", "minutes": 45, "pages": 38},
        {"date": "2026-07-02", "minutes": 30, "pages": 25}
      ],
      "minutes_total": 540,
      "pages_read": 478,
      "source": "physical",
      "purchase_price_usd": null,
      "added_at": "2026-07-01T08:00:00Z",
      "updated_at": "2026-07-09T22:00:00Z",
      "notes_summary": "Brilliant first-contact problem-solving. Loved the scientific optimism.",
      "re_read_count": 0,
      "last_re_read": null
    }
  ],
  "metadata": {
    "version": 1,
    "created_at": "2026-07-01T08:00:00Z",
    "total_books": 1,
    "annual_goal": 24,
    "goal_year": 2026
  }
}
```

**`quotes.json` schema (one entry per quote, with FK to book):**

```json
{
  "quotes": [
    {
      "id": "qt_001",
      "book_id": "bk_001",
      "book_title": "Project Hail Mary",
      "author": "Andy Weir",
      "text": "Science is the best idea humans have ever had.",
      "page": 87,
      "captured_at": "2026-07-05T19:30:00Z",
      "tags": ["epistemics", "rationality"],
      "personal_note": "Reminds me why I started this whole research thing."
    }
  ]
}
```

### Step 2: Add a Book — Natural Language Parsing

When the user says "Add *X* to my shelf" or "I just started *X*", parse and confirm:

| NL Phrase | Parsed |
|-----------|--------|
| "Add Project Hail Mary by Andy Weir" | title + author, status=`to-read` |
| "Started Sapiens yesterday" | status=`reading`, started_at=yesterday |
| "Finished Atomic Habits today, 4 stars" | status=`finished`, finished_at=today, rating=4 |
| "Save this article: {url}" | format=`article`, status=`finished`, capture URL |
| "I'm reading Range by Epstein, nonfiction" | status=`reading`, tags=[non-fiction] |
| "Add Snow Crash to my to-read list" | status=`to-read` |
| "DNF The Alchemist, boring" | status=`abandoned`, note: boring |

If metadata is missing, use a `lookup` step:

```bash
# Try Open Library by ISBN
curl -s "https://openlibrary.org/api/books?bibkeys=ISBN:$ISBN&format=json&jscmd=data"

# Or by title/author
curl -s "https://openlibrary.org/search.json?title=$TITLE&author=$AUTHOR"
```

Always show the parsed result and ask for confirmation before writing:

```
[PARSE]
  Title:     Project Hail Mary
  Author:    Andy Weir
  Format:    book (auto)
  Status:    to-read
  Year:      2021 (auto from lookup)
  Pages:     478 (auto)
  Tags:      none
  Source:    ?
[CONFIRM] Save? (y/n) or correct any field
```

### Step 3: Capture Quotes & Notes

Two ways:

**Inline:** "Log a quote from Project Hail Mary: 'Science is the best idea humans have ever had.' page 87"

```
[FOUND] Project Hail Mary (bk_001), status: finished
[QUOTE] Saved qt_024
  Book:    Project Hail Mary
  Author:  Andy Weir
  Page:    87
  Text:    "Science is the best idea humans have ever had."
[ASK] Add a personal note? (y/n)
```

**Bulk:** Paste a list of quotes from your Kindle highlights (one per line) and Hermes will deduplicate and batch-import.

**Markdown notes per book** (optional, for deep-dives): `~/.hermes/bookshelf/notes/{book_id}-{slug}.md` — opens up to free-form essay-style notes.

### Step 4: Reading Sessions

When the user says "I read for 30 minutes today" or "50 pages of Sapiens", log a session. This powers streaks and pace calculations.

### Step 5: Statistics & Recaps

**Streak logic:**
- A "reading day" = at least one session logged, OR status changed to `finished` that day, OR a quote captured.
- Current streak = consecutive reading days from today backwards.
- Longest streak = max over all time.

**Pace toward annual goal:**
- `books_read_ytd / annual_goal` = % progress
- `books_behind_pace = (today.day_of_year / 365 * goal) - books_read_ytd`
- Auto-suggest books to finish to get back on pace.

**Year-end recap** (run in December or on demand):
- Top genres/tags by count
- Average rating given
- Longest & shortest book
- Most-quoted author
- Total pages, total minutes, total days with reading
- "Best of" — top 3 by rating
- "DNF rate" — % abandoned
- Visual ASCII bar chart of books by month

### Step 6: Re-Read & Discovery

- **Re-read reminders:** Once a year, surface books from your shelf that are exactly 1, 2, 3, 5 years old — invite a re-read.
- **Triage `to-read`:** If `to-read` > 30 items, suggest a "shadow library" cleanup: archive ones that no longer interest you.
- **Gap analysis:** "You read 14 business books and 0 novels in 2026 — diversify?"

---

## Example Invocations

### Example 1: Logging a Finished Book

**User:** *"I just finished Tomorrow, and Tomorrow, and Tomorrow by Gabrielle Zevin. Loved it, 5 stars. Fiction, about game design and friendship."*

**Agent:**

```
[PARSE]
  Title:     Tomorrow, and Tomorrow, and Tomorrow
  Author:    Gabrielle Zevin
  Format:    book
  Status:    finished (today, 2026-07-16)
  Rating:    ★★★★★
  Tags:      fiction, game-design, friendship
  Pages:     416 (auto from Open Library)
[CONFIRM] Save? (y/n)

> y

[OK] bk_042 added to your shelf
[STREAK] Reading day 14 in a row 🔥
[STATS] 2026 progress: 18/24 books (75%, 6 ahead of pace)
[RECAP] You've read 9 fiction and 9 non-fiction this year — perfect balance.
```

### Example 2: Capturing a Quote Mid-Read

**User:** *"Quote from Meditations by Marcus Aurelius, page 42: 'You have power over your mind — not outside events. Realize this, and you will find strength.' Tag: stoicism"*

**Agent:**

```
[FOUND] Meditations (bk_017), status: reading
[QUOTE] Saved qt_089
  Book:    Meditations
  Author:  Marcus Aurelius
  Page:    42
  Text:    "You have power over your mind — not outside events. Realize this, and you will find strength."
  Tags:    [stoicism]
[ASK] Personal note? (y/n)
> y
> Reminder for tough weeks

[NOTE] Saved.
[STREAK] Reading day 14 🔥
[BOOK] Page 42/254 — 17% to go.
```

### Example 3: Year-End Recap

**User:** *"Generate my 2026 reading recap"*

**Agent:**

```
[RECAP] 2026 Year in Books
━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Headline numbers
  Books finished:    24 / 24 goal (100%) 🎯
  Pages turned:      8,142
  Reading days:      287 / 365 (79%)
  Longest streak:    47 days (Mar–May)
  Average rating:    4.0 / 5
  DNF rate:          3/29 started (10%)

📚 By format
  Physical books    ████████████  14
  Audiobooks        ████           5
  Articles/papers   ████           4
  eBooks            ▏              1

🏷 Top tags
  fiction, sci-fi, biography, history, tech, philosophy

🌟 Top 3
  1. Tomorrow, and Tomorrow, and Tomorrow — Gabrielle Zevin ★★★★★
  2. Project Hail Mary — Andy Weir                ★★★★★
  3. Meditations — Marcus Aurelius                ★★★★★

💬 Most-quoted author: Marcus Aurelius (12 quotes)

📅 Books by month
  Jan ██  Feb ███  Mar ████  Apr ██  May █  Jun ██
  Jul ███  Aug ██  Sep ███  Oct ██  Nov ██  Dec ██

📖 Re-reads: 2 (Meditations, Atomic Habits)

[SAVED] ~/.hermes/bookshelf/recaps/recap-2026.md
```

### Example 4: Triage the To-Read List

**User:** *"My to-read list is overwhelming — clean it up"*

**Agent:**

```
[TRIAGE] 47 books in to-read

  Added in 2024 (oldest first):
    1. "The Stand" — Stephen King              (added 814 days ago)
    2. "Thinking, Fast and Slow" — Kahneman     (added 793 days ago)
    ...
    8. "Antifragile" — Taleb                   (added 540 days ago)

  Added 2026 (recent):
    22. "The Mountain in the Sea" — Ray Nayler
    ...

[STALE] 12 books added > 1 year ago, never started:
  - Likely candidates to drop unless still relevant

[ASK] Want me to:
  (a) Auto-archive any book > 2 years old in to-read
  (b) Show me 12 oldest and let me decide each
  (c) Keep everything, just sort by oldest
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Title ambiguity ("Meditation" could be 200 books) | Confirm author; if still ambiguous, ask user to disambiguate or show top 3 candidates from Open Library lookup |
| User adds article URL but expects book format | Detect URL → format=`article`; confirm; auto-fetch title from `<title>` tag and estimated read time from word count |
| Re-reading a book: should this create a new entry or update? | **Update** the existing entry: increment `re_read_count`, set `last_re_read`, append to sessions as a new period — preserves quote history |
| Conflicting "finished" + "started" dates (impossible) | If `finished_at < started_at`, flag and ask user to re-confirm |
| User forgets to log a book, then mentions "that book I read last month" | Look for `added_at` in last 60 days with title matching loosely; offer to backdate `started_at` and `finished_at` |
| Massive quote paste from Kindle — duplicates | Normalize text (strip whitespace, lowercase, remove punctuation for matching); show dedup count before import |
| ISBN lookup returns nothing (rare/foreign books) | Fall back to title/author search; if still nothing, ask user for year + page count + language |
| Annual goal of 50 books but only reading 3/month | Suggest either (a) bumping goal to realistic 36, (b) adding more audiobooks/articles, (c) focus on shorter books — not a moral judgment |
| User wants public Goodreads-style export | Support export to CSV with all fields, plus Markdown for quotes — user can manually upload to Goodreads if desired |
| Confusing books with same title (e.g., "Meditation" by multiple authors) | Always disambiguate by author on first save; once in shelf, use book_id as source of truth |
| Session dates in the future | Reject; ask user to re-confirm |
| Books in languages user doesn't read | Tag with language; surface in stats if unusual; never auto-translate (privacy) |

---

## Verification Checklist

Before claiming an "add" or "finish" was successful, verify:

- [ ] `books.json` is valid JSON (run `jq . ~/.hermes/bookshelf/books.json`)
- [ ] Book entry has unique `id` (format: `bk_NNN`)
- [ ] `status` ∈ {`to-read`, `reading`, `finished`, `abandoned`, `re-reading`}
- [ ] If `status=finished`: both `started_at` and `finished_at` are present
- [ ] `rating` (if present) is integer 1–5
- [ ] `authors` is a non-empty array
- [ ] `added_at` and `updated_at` are ISO 8601 timestamps
- [ ] Quote (if logged) has matching `book_id` in `books.json`
- [ ] No duplicate quote text within same book (case-insensitive trim)
- [ ] Session dates are in the past or today
- [ ] Annual goal progress shown to user with `%` and `behind/ahead` indicator

For statistics, verify:

- [ ] Streak counter excludes days with 0 sessions, 0 status changes, 0 quotes
- [ ] Year-end recap filters by `finished_at` year, not `added_at`
- [ ] DNF rate = `abandoned` / (`finished` + `abandoned`)
- [ ] Pages read total = sum of `pages_read` for finished books, not partial

---

## Data Sources & Accuracy

| Data Point | Source | Reliability | Privacy |
|-----------|--------|-------------|---------|
| Book metadata (title, author, pages, year) | [Open Library](https://openlibrary.org) API | High — community-edited, has ISBN-grade data | Sends title/author only, no personal data |
| ISBN → book lookup | Open Library `api/books` endpoint | High | Public API, no auth |
| Article title from URL | HTML `<title>` tag (one fetch) | High | Sends User-Agent, no tracking beyond server logs |
| Reading time estimate (articles) | Word count ÷ 200 wpm | Medium — varies by reader | n/a (calculated locally) |
| Cover images | Open Library Covers API | Medium — not all books have covers | Optional, only fetched on user request |
| User data (books, quotes, sessions) | Local JSON in `~/.hermes/bookshelf/` | **Your data, your control** | Never leaves your machine unless you export |

**Privacy guarantees:**
- All personal reading history is stored locally in `~/.hermes/bookshelf/`.
- Open Library requests only contain book title/author/ISBN — no user identifiers.
- No analytics, no telemetry, no cloud sync.
- Export at any time to CSV (full) and Markdown (quotes).
- You can `rm -rf ~/.hermes/bookshelf` to delete everything.

**Accuracy notes:**
- Open Library is community-edited — page counts and years may be wrong for obscure books. Always show the auto-filled value and let the user correct.
- Streak math is strict: if you read but forget to log, the streak breaks. Encourage daily micro-logs ("log a 5-min session") rather than batch updates.
- Annual goal % is computed against the calendar year of the system clock, not "12 months from goal set date".
