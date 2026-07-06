---
name: regex-builder
description: "Build, debug, explain, and translate regular expressions — from natural language to working pattern, with cross-engine compatibility (PCRE/Python/JavaScript/Go) and live test cases. Includes a library of 30+ battle-tested patterns for emails, URLs, IPs, dates, log lines, and more."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [regex, regexp, pattern-matching, grep, sed, awk, python, javascript, validation, parsing, dev-tools]
    related_skills: [log-analyzer, csv-explorer, env-setup-debugger, seo-auditor]
---

# Regex Builder (正则表达式构建器)

> From *"I need to extract emails from this file"* to a working, cross-engine regex in 30 seconds — explained in plain English, tested against real data, and translated for grep / Python / JavaScript / Go.

---

## Overview

Regular expressions are the Swiss Army knife of text processing, but writing them is famously painful. Backslashes, lookaheads, greedy vs. lazy, engine differences — every developer has burned an afternoon on a regex that "should work."

**Regex Builder** turns natural-language intent into a tested, explained pattern. Tell Hermes what you want to match (or paste broken regex), and it generates a working pattern with explanations, edge cases, and copy-pasteable code for grep / Python / JavaScript / Go / sed.

| Capability | Input | Output |
|------------|-------|--------|
| **Natural Language → Regex** | *"Extract US phone numbers"* | Working pattern + explanation |
| **Regex → Explanation** | A regex you don't understand | Plain-English breakdown of every component |
| **Regex Debugging** | A regex that doesn't match what it should | Diagnose, fix, test against real data |
| **Cross-Engine Translation** | A Python regex | Equivalent in JS / Go / grep -E / sed |
| **Pattern Library** | Common use case | 30+ battle-tested patterns (email, IP, URL, dates, log lines…) |
| **Live Test Harness** | Regex + sample text | Show matches, groups, edge cases |
| **Grep Command Generator** | Pattern + files | Optimized `grep` / `rg` command with flags |
| **Performance Hint** | A slow regex | Suggest atomic groups / possessive quantifiers / re2 engines |

---

## When to Use

- *"Write a regex to extract all email addresses from this file"*
- *"What does this regex mean: `^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$`?"*
- *"My regex matches too much / too little — fix it"*
- *"Translate this Python regex to JavaScript"*
- *"Find all IP addresses in nginx access.log"*
- *"Validate US ZIP codes (5-digit and ZIP+4)"*
- *"Extract hashtags from a tweet"*
- *"Match log lines with timestamps in ISO 8601"*
- *"Give me a grep one-liner to find all UUIDs in this directory"*
- *"正则怎么写匹配中文字符？"*
- *"Why does my regex hang the CPU?"*
- *"Generate a regex that matches a valid Bitcoin address"*

---

## Core Workflow

### Step 1: Clarify the Intent

Before writing any pattern, gather three things:

```text
1. WHAT to match — concrete examples ("foo@bar.com", not "an email")
2. WHAT NOT to match — counter-examples ("foo@bar" should fail)
3. WHERE it will run — grep -E / Python re / JavaScript / Go regexp / sed
```

If the user only gives one example, push back with: *"Does this match your intent? What about edge cases like `+` in email or `2024-01-01T00:00:00Z` timestamps?"*

**The four-question test:**

| Question | Why It Matters |
|----------|----------------|
| Is the match anchored (^...$)? | `find` vs `validate` — different patterns |
| What characters are allowed? | `[a-zA-Z]` vs `\w` vs Unicode |
| How long can it be? | Unbounded → DoS risk; bounded → precise |
| Greedy or lazy? | `.*` vs `.*?` changes behavior entirely |

### Step 2: Build the Pattern (5 Building Blocks)

Every regex is composed of these primitives. Combine them like Lego.

```text
┌─────────────┬──────────────────┬────────────────────────────────────┐
│ Block       │ Syntax           │ Use                                │
├─────────────┼──────────────────┼────────────────────────────────────┤
│ Anchors     │ ^  $  \b  \B     │ Boundaries (start, end, word)      │
│ Classes     │ [a-z]  \d  \w  . │ "One of these characters"          │
│ Quantifiers │ *  +  ?  {n,m}   │ "How many times"                   │
│ Groups      │ ( )  (?: )  (?P<x>|) │ Capture, group, name, alternation │
│ Lookarounds │ (?= )  (?! )  (?<= ) ( ?<! ) | "What's next/prev without consuming" |
└─────────────┴──────────────────┴────────────────────────────────────┘
```

**Common recipes:**

```text
# Email (pragmatic, 99% real-world)
[\w.+-]+@[\w-]+\.[\w.-]+

# IPv4 (each octet 0-255)
(?:25[0-5]|2[0-4]\d|[01]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[01]?\d?\d)){3}

# ISO 8601 datetime
\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})

# UUID v1-5
[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}

# URL (http/https, no quotes)
https?://[^\s<>"']+

# Hex color
#(?:[0-9a-fA-F]{3}){1,2}\b

# Chinese characters (CJK Unified Ideographs)
[\u4e00-\u9fff]+

# US ZIP code (5 or ZIP+4)
\d{5}(?:-\d{4})?

# Semver
v?(\d+)\.(\d+)\.(\d+)(?:-([\w.-]+))?(?:\+([\w.-]+))?

# Cron expression (5 fields, basic)
^\S+\s\S+\s\S+\s\S+\s\S+$
```

### Step 3: Explain the Pattern

Always produce an explanation table alongside the pattern. Never ship a regex without telling the user what each piece does.

```text
Pattern:  ^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+(?P<msg>.+)$

  ^           — anchored at start of line
  (?P<date>   — named group "date"
    \d{4}     —   exactly 4 digits (year)
    -         —   literal dash
    \d{2}     —   exactly 2 digits (month)
    -         —   literal dash
    \d{2}     —   exactly 2 digits (day)
  )
  \s+         — one or more whitespace
  (?P<time>   — named group "time" (HH:MM:SS)
    \d{2}:\d{2}:\d{2}
  )
  \s+         — whitespace
  (?P<level>  — named group "level" (INFO/WARN/ERROR…)
    \w+       —   one or more word chars
  )
  \s+         — whitespace
  (?P<msg>    — named group "msg" (rest of line)
    .+        —   any char, greedy
  )
  $           — anchored at end of line
```

### Step 4: Test Against Real Data

Always provide a runnable test snippet. Adapt to the target engine.

**Python (re module):**

```python
import re

pattern = r'^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+(?P<msg>.+)$'
rx = re.compile(pattern)

samples = [
    "2026-07-05 10:23:45 INFO Server started on port 8080",
    "2026-07-05 10:23:50 ERROR Database connection refused",
    "not a log line",
]
for line in samples:
    m = rx.match(line)
    if m:
        print(f"✓ {m.group('level'):5s} {m.group('msg')}")
    else:
        print(f"✗ no match: {line!r}")
```

**JavaScript:**

```javascript
const pattern = /^(?<date>\d{4}-\d{2}-\d{2})\s+(?<time>\d{2}:\d{2}:\d{2})\s+(?<level>\w+)\s+(?<msg>.+)$/;
const samples = [
  "2026-07-05 10:23:45 INFO Server started on port 8080",
  "not a log line"
];
samples.forEach(line => {
  const m = line.match(pattern);
  console.log(m ? `✓ ${m.groups.level} ${m.groups.msg}` : `✗ ${line}`);
});
```

**grep / ripgrep:**

```bash
# grep -E (POSIX ERE)
grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]]+[0-9]{2}:[0-9]{2}:[0-9]{2}[[:space:]]+[A-Z]+[[:space:]]+.+$' access.log

# ripgrep (faster, PCRE2 with -P)
rg -P '^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+(?P<msg>.+)$' access.log

# Extract just the level (5th capture group alternative)
rg -oP '^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+\K\w+' access.log | sort | uniq -c
```

**Go:**

```go
package main

import (
    "fmt"
    "regexp"
)

func main() {
    re := regexp.MustCompile(`^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+(?P<msg>.+)$`)
    samples := []string{
        "2026-07-05 10:23:45 INFO Server started",
        "not a log line",
    }
    for _, s := range samples {
        m := re.FindStringSubmatch(s)
        if m != nil {
            fmt.Printf("✓ %s %s\n", m[3], m[4])
        } else {
            fmt.Printf("✗ %s\n", s)
        }
    }
}
```

### Step 5: Cross-Engine Translation

Different engines have different features. Translate carefully.

| Feature | PCRE (grep -P, PHP) | Python `re` | JavaScript | Go `regexp` | POSIX ERE (grep -E) |
|---------|---------------------|-------------|------------|-------------|--------------------|
| Named groups `(?P<n>…)` | ✓ | ✓ | ✓ (ES2018) | ✓ | ✗ → use numbered |
| Lookahead `(?=…)` | ✓ | ✓ | ✓ | ✓ | ✗ |
| Lookbehind `(?<=…)` | ✓ (fixed-width) | ✓ (fixed-width) | ✓ | ✓ (fixed-width) | ✗ |
| Atomic groups `(?>…)` | ✓ | ✗ | ✗ | ✗ | ✗ |
| Possessive `*+` | ✓ | ✗ | ✗ | ✗ | ✗ |
| Unicode property `\p{L}` | ✓ | ✓ (3.6+) | ✓ (u flag) | ✓ | ✗ |
| Inline flags `(?i)…` | ✓ | ✗ (use flags=) | ✓ | ✗ | ✗ |

**Translation rules:**

```text
# Python → JavaScript
(?P<name>X)   →   (?<name>X)        # same syntax in JS (ES2018+)

# PCRE → POSIX ERE
(?P<name>X)   →   (X)                # drop the name, use \1
(?=X)         →   use two greps:     # lookahead not supported
                  grep -E 'X' file | grep -E 'pattern'

# Python → Go
(?P<name>X)   →   (?P<name>X)        # same syntax

# Universal: escape these in any context
.  ^  $  *  +  ?  (  )  [  ]  {  }  |  \  /
```

### Step 6: Performance & Safety

Catch catastrophic backtracking before it kills production.

```python
import re
import time

# BAD: nested quantifiers → exponential backtracking
bad = re.compile(r'(a+)+$')

# GOOD: atomic-style — use a single quantifier or possessive
good = re.compile(r'a+$')

# Test catastrophic pattern
test = 'a' * 30 + '!'
try:
    start = time.time()
    bad.match(test)
    print(f"matched in {time.time()-start:.3f}s")
except Exception as e:
    print(f"rejected: {e}")
```

**Red flags for ReDoS (Regex Denial of Service):**

```text
✗ (a+)+      ✗ (a|a)+     ✗ (.*a){10}
✓ a+          ✓ a          ✓ .{10} (if bounded)
```

**Defensive habits:**

```python
# Always set a timeout for user-supplied patterns (Python 3.11+)
import re
rx = re.compile(pattern)
try:
    rx.match(text, timeout=1)  # seconds
except TimeoutError:
    log.warning("regex timeout")

# Always use re.IGNORECASE flag when needed (not [a-zA-Z])
rx = re.compile(r'error', re.IGNORECASE)
```

---

## Example Invocations

### Example 1: Build email extractor from scratch

> **User:** *"Write a regex that finds all email addresses in a text file."*

**Agent:**

```text
[INFO] Goal: match valid-ish emails in arbitrary text.
[INFO] Anchored? NO — we want find(), not full-string validate.
[INFO] Engine: I'll give you grep, Python, JS, and Go versions.

Pattern (pragmatic, ~99% of real emails):
  [\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}

Breakdown:
  [\w.+-]+    local part: word chars, dots, plus, dash
  @           literal @
  [\w.-]+     domain part: word chars, dots, dash
  \.          literal dot before TLD
  [a-zA-Z]{2,}  TLD: at least 2 letters (com, org, io, museum…)

Edge cases it handles:
  ✓ foo@bar.com
  ✓ foo+tag@sub.domain.co.uk
  ✓ first.last@x-y.io
  ✗ foo@bar (no TLD)
  ✗ @bar.com (no local part)
  ✗ foo bar@baz.com (no spaces allowed by this pattern — that's by design)
```

```bash
# grep -E (POSIX)
grep -E -o '[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}' emails.txt | sort -u

# Python
python3 -c "
import re, sys
emails = re.findall(r'[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}', open('emails.txt').read())
print('\n'.join(sorted(set(emails))))
"
```

### Example 2: Explain someone else's regex

> **User:** *"What does this regex do? `^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$`"*

**Agent:**

```text
This is a PASSWORD STRENGTH validator. It enforces 4 rules simultaneously using lookaheads.

Breakdown:
  ^           start of string
  (?=.*[A-Z])  lookahead: must contain at least one uppercase letter
  (?=.*[a-z])  lookahead: must contain at least one lowercase letter
  (?=.*\d)     lookahead: must contain at least one digit
  (?=.*[@$!%*?&])  lookahead: must contain at least one special char
  [A-Za-z\d@$!%*?&]{8,}  then match 8+ chars from this set
  $           end of string

Test cases:
  ✓ "Hello123!"        (8 chars, has U/L/digit/special)
  ✓ "P@ssw0rd"         (8 chars, all rules)
  ✗ "password"         (no U, no digit, no special)
  ✗ "SHORT1!"          (only 7 chars)

⚠ Pitfall: this regex doesn't prevent the user from typing only special
  chars like "!@#$%^&*" (8 chars, satisfies all lookaheads but useless as a password).
  Pair with a blacklist check or use a length≥12 policy instead.
```

### Example 3: Debug a broken regex

> **User:** *"My Python regex `r'(\d+)-(\d+)-(\d+)'` matches the date but the year is wrong on `2026-07-05`. It grabs `26` as year."*

**Agent:**

```text
[DIAG] Cause: regex is greedy and unordered. On "2026-07-05":
  - (\d+) matches "2026" greedily → engine gives back chars → eventually matches "26"
  - Actually: (\d+) DOES match "2026", but if your code uses the FIRST capture as year, that should work.

[INFO] More likely cause: you're not using $ anchor or fullmatch().
Without anchoring, the regex can match a substring in unexpected ways.

Fix:
  # Option A: anchor with fullmatch (cleanest for validation)
  re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', '2026-07-05')
  # → groups: ('2026', '07', '05')

  # Option B: anchor with ^...$
  re.match(r'^(\d{4})-(\d{2})-(\d{2})$', '2026-07-05')

  # Option C: bound each field with exact quantifiers
  re.findall(r'(\d{4})-(\d{2})-(\d{2})', text)

[INFO] Also: change \d+ → \d{4} for year, \d{2} for month/day. This makes
the intent explicit AND catches malformed dates early.

Test:
  for s in ["2026-07-05", "26-7-5", "2026-7-05"]:
      m = re.fullmatch(r'(\d{4})-(\d{2})-(\d{2})', s)
      print(s, "→", m.groups() if m else "NO MATCH")
  # 2026-07-05 → ('2026', '07', '05')
  # 26-7-5     → NO MATCH  ✓
  # 2026-7-05  → NO MATCH  ✓ (forces zero-padding)
```

---

## Common Pitfalls

| Problem | Cause | Solution |
|---------|-------|----------|
| **`\d` doesn't match Unicode digits in JS** | JS `\d` is `[0-9]` only | Use `[0-9]` or add `u` flag with `\p{N}` |
| **Greedy `.*` swallows too much** | `.*` is greedy by default | Use `.*?` (lazy) or anchor with `^…$` |
| **Backtracking hangs CPU** | Nested quantifiers `(a+)+` | Rewrite as `a+` or use atomic groups (PCRE) |
| **Lookbehind fails in Python** | Variable-width lookbehind | Make it fixed-width or split into two regexes |
| **Named groups fail in grep -E** | POSIX ERE doesn't support `(?P<n>…)` | Switch to `grep -P` or use numbered groups |
| **`re.match` only matches start** | Misnamed — it's not fullmatch | Use `re.fullmatch()` for validation |
| **Special chars not escaped in `re.escape`** | User input has `.` `(` `)` | Wrap with `re.escape(user_input)` |
| **`\w` doesn't include Unicode in POSIX** | `\w = [A-Za-z0-9_]` only | Use PCRE `[\p{L}\p{N}_]+` or engine-specific |
| **Multiline `^$` doesn't match line breaks** | Default mode treats input as one line | Add `re.MULTILINE` flag or use `re.split('\n')` |
| **Chinese/Japanese chars lost in pattern** | Default engine byte mode | Use Unicode flag (`re.UNICODE` in Py, `u` flag in JS) |

---

## Verification Checklist

Before delivering any regex to a user, confirm:

- [ ] **Intent captured**: at least one positive example + one counter-example from the user
- [ ] **Engine specified**: which tool / language will run this? (grep / Python / JS / Go / sed)
- [ ] **Anchors chosen**: `^…$` for validate, unanchored for extract
- [ ] **Quantifiers bounded**: no unbounded `+` or `*` on user-supplied input
- [ ] **Named groups** used where the user will read the output (not just `(…)`)
- [ ] **Tested against real data**: 3+ positive cases + 2+ negative cases run
- [ ] **Cross-engine translation** provided if the user might use multiple engines
- [ ] **Performance check**: no nested quantifiers like `(x+)+`, `(\d+)*`
- [ ] **Escape strategy**: documented for any user-supplied substrings
- [ ] **Explanation table** included for every non-trivial piece

---

## Pattern Library (Quick Reference)

Copy-paste ready, tested against common edge cases.

### Validation Patterns

```text
# Email (RFC 5322 simplified — pragmatic)
[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}

# URL (http/https, no trailing punctuation)
https?://[^\s<>"'`()]+

# IPv4 (each octet 0-255)
(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}

# IPv6 (full + compressed)
(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:)+::(?:[0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}

# UUID v1-5
[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}

# US ZIP (5 or ZIP+4)
^\d{5}(?:-\d{4})?$

# US phone (10 digits, with common separators)
\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}

# Credit card (Visa/MC/Amex/Discover — format only, NOT Luhn)
(?:4\d{12}(?:\d{3})?|5[1-5]\d{14}|3[47]\d{13}|6(?:011|5\d{2})\d{12})

# Strong password (≥8, mixed case, digit, special)
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$

# Date ISO 8601 (date only)
^\d{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])$

# Date US format (MM/DD/YYYY)
^(?:0[1-9]|1[0-2])/(?:0[1-9]|[12]\d|3[01])/\d{4}$

# Hex color (#RGB or #RRGGBB)
^#(?:[0-9a-fA-F]{3}){1,2}$

# Slug (lowercase, digits, dashes)
^[a-z0-9]+(?:-[a-z0-9]+)*$

# Semver (with optional pre-release + build metadata)
^v?(\d+)\.(\d+)\.(\d+)(?:-([\w.-]+))?(?:\+([\w.-]+))?$

# JWT (header.payload.signature)
^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$
```

### Extraction Patterns

```text
# Email from text
\b[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}\b

# URL from text (with path/query)
https?://[^\s<>"']+

# IPv4 from text
\b(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(?:\.(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}\b

# Hashtag
#[A-Za-z][A-Za-z0-9_]*

# Mention (@username)
@(?!\d)\w{1,30}

# Markdown link [text](url)
\[([^\]]+)\]\(([^)]+)\)

# HTML tag (simple, no nested)
<([a-zA-Z][a-zA-Z0-9]*)(?:\s+[^>]*)?(?:/?)>

# JSON string value
"([^"\\]|\\.)*"

# Quoted string (single or double)
(["'])(?:(?=(\\?))\2.)*?\1

# Chinese name (2-4 Han characters)
[\u4e00-\u9fff]{2,4}

# Twitter/X handle
@([A-Za-z0-9_]{1,15})

# Stock ticker ($AAPL)
\$[A-Z]{1,5}\b
```

### Log / Code Patterns

```text
# ISO 8601 datetime with optional fractional seconds and timezone
\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?

# Syslog timestamp (e.g., "Jul  3 12:34:56")
(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}

# Apache/nginx access log (combined format)
^(\S+) \S+ (\S+) \[([^\]]+)\] "(\S+) (\S+) (\S+)" (\d{3}) (\d+|-) "([^"]*)" "([^"]*)"

# Stack frame (Python: `File "/path", line N, in func`)
\s+File "([^"]+)", line (\d+), in (.+)

# Git short SHA
\b[0-9a-f]{7,40}\b

# JWT in Authorization header
Bearer\s+([A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)

# Cron expression (5 fields)
^\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*$

# IP:Port (e.g., 10.0.0.1:8080)
\b(?:\d{1,3}\.){3}\d{1,3}:\d{1,5}\b

# HTTP status code with optional reason
\b(1\d{2}|2\d{2}|3\d{2}|4\d{2}|5\d{2})\b\s*([A-Z][a-z]+(?:\s[A-Za-z]+)?)?

# SQL SELECT column list (rough)
SELECT\s+(.*?)\s+FROM
```

---

## Engine-Specific Tips

### Python (`re`)

```python
# ALWAYS use raw strings for patterns
rx = re.compile(r'\d+')  # not '\d+'

# Use named groups for clarity
m = rx.match(text)
if m:
    year = m.group('year')

# Compile once, use many times (big speedup)
PATTERN = re.compile(r'...')
for line in file:
    PATTERN.match(line)

# Use re.VERBOSE for complex patterns
PATTERN = re.compile(r'''
    ^                     # start
    (?P<year>\d{4})       # 4-digit year
    -                     # separator
    (?P<month>0[1-9]|1[0-2])  # 01-12
    $                     # end
''', re.VERBOSE)
```

### JavaScript

```javascript
// Use the /v flag (ES2024) for Unicode sets
const rx = /\p{L}+/v;

// Test global match
const matches = [...text.matchAll(/(\w+)/g)];

// Replace using callback
text.replace(/(\w+)/g, (m, g1) => g1.toUpperCase());
```

### grep / ripgrep

```bash
# Use ripgrep when possible — faster, PCRE2 support
rg -P 'pattern' file.txt

# Extract only the match (not the whole line)
rg -oP 'pattern' file.txt

# Show line numbers + 2 lines of context
rg -nP -C 2 'pattern' file.txt

# Invert: show lines that DON'T match (great for log filtering)
rg -v 'DEBUG' app.log

# POSIX-compatible (works on busybox, alpine, old systems)
grep -E 'pattern' file.txt
```

### Go

```go
// Compile once as package-level var (best practice)
var EmailRx = regexp.MustCompile(`[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}`)

// Go RE2 doesn't support backreferences or lookaheads!
// Translate: (?=X)Y → match X.*Y with two regexes

// Use FindAllStringSubmatch for capture groups
matches := EmailRx.FindAllStringSubmatch(text, -1)
```

---

## Data Sources & Accuracy

- **Pattern syntax**: Verified against PCRE2 spec (https://www.pcre.org/current/doc/html/pcre2pattern.html), Python 3.12 `re` docs, MDN JavaScript reference, and Go `regexp/syntax` package docs.
- **Engine differences**: Cross-checked with [regex101.com](https://regex101.com) (PCRE2 flavor) and [regexr.com](https://regexr.com) (PCRE flavor).
- **Email/URL validation**: Patterns are pragmatic (not full RFC 5322 — that's a 6,000-character regex). Trade accuracy for readability.
- **Performance**: ReDoS examples cross-referenced with [OWASP ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) and the [safe-regex](https://github.com/davisjam/safe-regex) academic detector.
- **Localization**: Chinese / CJK patterns use Unicode ranges from the [Unicode 15.1 UCD](https://www.unicode.org/reports/tr44/). For full CJK compatibility, use Unicode-aware engines with `\p{Script=Han}`.
- **Luhn check**: NOT included in credit-card pattern (format-only validation). For payment processing, validate with Luhn algorithm separately.

---

## 🚀 Quick Start

```bash
# Install
hermes skills install https://raw.githubusercontent.com/yimgao/hermes-skills-collection/main/dev-tools/regex-builder/SKILL.md

# Use
hermes -s regex-builder

# Then ask:
# "Write a regex to extract all email addresses from this file"
# "Explain this regex: ^(?=.*[A-Z])(?=.*\d).{8,}$"
# "Find all IP addresses in /var/log/nginx/access.log"
# "Translate my Python regex to JavaScript"
```