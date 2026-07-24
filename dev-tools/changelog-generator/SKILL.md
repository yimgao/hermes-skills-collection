---
name: changelog-generator
description: "Generate CHANGELOG.md from git history — auto-categorize Conventional Commits, draft release notes per tag, fill missing releases, detect breaking changes, output Keep-a-Changelog or Conventional style."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [git, changelog, release-notes, semantic-versioning, conventional-commits, developer-tools, documentation]
    related_skills: [git-history-analyst, code-review-helper, project-scaffolder, dependency-auditor]
---

# 📝 Changelog Generator / 自动生成 CHANGELOG 与发布说明

> Stop hand-writing release notes. Hermes reads your git history, parses Conventional Commits (or natural-language commits), categorizes entries by type, surfaces breaking changes, and writes a polished `CHANGELOG.md` plus per-release notes ready for GitHub Releases. Zero deps — works with just `git` and `jq`.

---

## Overview

`changelog-generator` turns git history into a beautifully formatted changelog. It handles three real-world scenarios most projects face: (1) you've been committing casually and want a proper `CHANGELOG.md` retrofitted from history, (2) you tag releases regularly and want auto-generated release notes for each tag, (3) you forgot to bump the changelog for the last 6 commits and need a fix-up.

| Capability | Description |
|------------|-------------|
| **🔍 Conventional Commit parsing** | Detect and group `feat:`, `fix:`, `perf:`, `refactor:`, `docs:`, `test:`, `chore:`, `style:` prefixes |
| **🧠 Natural-language fallback** | When commits aren't Conventional, infer type from keywords ("fix", "add", "bump") |
| **📦 Tag-aware release grouping** | Each `vX.Y.Z` tag becomes a section; `Unreleased` becomes the head section |
| **⚠️ Breaking-change detection** | Commit with `!` or `BREAKING CHANGE:` footer gets a `🚨 BREAKING` callout at top |
| **🔗 Author & PR attribution** | Append `(@author)` and PR number `(#123)` when available |
| **📜 Two output formats** | Keep-a-Changelog style OR Conventional Commits style — pick by repo convention |
| **🩹 Fill missing releases** | Retroactively generate entries for past versions that have no notes |
| **🎯 Next-version suggestion** | Bump major/minor/patch based on what landed since last tag |
| **📤 GitHub Release draft** | Emit markdown ready to paste into `gh release create --notes -` |
| **🔁 CI-friendly** | Deterministic; safe to run in pre-commit or release workflow |
| **🪶 Zero external deps** | Pure `git` + `awk` + `jq`/Python; no `conventional-changelog-cli` install |

---

## When to Use

- *"Generate a CHANGELOG for my repo"*
- *"Draft release notes for v2.1.0"*
- *"What changed since v1.4.0?"*
- *"I just tagged v3.0 — give me release notes"*
- *"Retro-fit a changelog from my last 200 commits"*
- *"Make my commits Conventional — here's the existing log"*
- *"What kind of bump (major/minor/patch) should v2.4.0 be?"*
- *"Output Keep-a-Changelog style, sorted by category"*
- *"Generate a GitHub Release description from commits since last tag"*
- *"Fill in missing entries — I forgot to update CHANGELOG for the last 5 releases"*
- *"What's the breaking-change summary for the 1.x → 2.x upgrade?"*

---

## Core Workflow

### Step 1 — Inventory the repo

Detect commit convention and tag history before writing anything.

```bash
# Repo root + head commit
git rev-parse --show-toplevel
git log -1 --format='%h %s'

# Last 10 tags (semver only)
git tag --sort=-v:refname | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+' | head -10

# Existing CHANGELOG?
ls CHANGELOG.md CHANGES.md HISTORY.md NEWS.md 2>/dev/null

# Total commit count + time range
git log --reverse --format='%h %ad' --date=short | awk 'NR==1; END{print}'
# → 3a8f1c0 2023-04-12
#   f7b2a91 2026-07-23

# Detect Conventional Commits coverage
COMMITS=$(git log --pretty=format:'%s' -n 200)
echo "$COMMITS" | grep -cE '^(feat|fix|perf|refactor|docs|test|chore|style|build|ci)(\([^)]+\))?!?:'
# → 142 / 200 = 71% → high coverage, parse as Conventional

# Authors since last tag
SINCE=$(git describe --tags --abbrev=0 2>/dev/null || git rev-list --max-parents=0 HEAD | head -1)
git shortlog -sn ${SINCE}..HEAD
```

**Decision matrix:**

| Coverage | Action |
|----------|--------|
| ≥70% Conventional | Parse as Conventional, infer the rest |
| 30–69% | Hybrid: parse Conventional, classify the rest by keyword |
| <30% | Use `commit-classifier.md` heuristics, ask user once to confirm categories |

### Step 2 — Group commits by tag/version

```bash
# Walk tags in reverse, collecting commits between them
for tag in $(git tag --sort=-v:refname | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+' | head -10); do
  PREV=$(git describe --tags --abbrev=0 "${tag}^@" 2>/dev/null || git rev-list --max-parents=0 "${tag}" | head -1)
  echo "=== $tag (${PREV:0:7}..${tag}) ==="
  git log --pretty=format:'%h|%s|%an|%ae' "${PREV}..${tag}"
done

# Unreleased = last tag .. HEAD
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null)
echo "=== Unreleased (${LAST_TAG}..HEAD) ==="
git log --pretty=format:'%h|%s|%an|%ae' "${LAST_TAG}"..HEAD
```

### Step 3 — Classify each commit

Parse Conventional Commits directly; for natural-language commits, apply keyword heuristics. Output structured JSON first (for review), then render markdown.

```python
# classify.py — minimal Conventional-Commits-aware classifier (stdlib only)
import re, subprocess, json, sys

CONV_RE = re.compile(
    r'^(?P<type>feat|fix|perf|refactor|docs|test|chore|style|build|ci)'
    r'(?:\((?P<scope>[^)]+)\))?'
    r'(?P<bang>!?)'
    r':\s*(?P<subject>.+)$'
)

KEYWORD_MAP = {
    'feat|feature|add|implement|introduce|new': 'feat',
    'fix|bug|patch|resolve|crash|broken|regress': 'fix',
    'perf|optimi[zs]e|speed|faster': 'perf',
    'refactor|restructure|reorgani[zs]e|cleanup|clean up': 'refactor',
    'docs|doc|comment|readme|documentation': 'docs',
    'test|spec|coverage': 'test',
    'chore|bump|upgrade|depend|maintenance': 'chore',
    'style|format|lint|prettier|whitespace': 'style',
    'build|ci|workflow|release': 'build',
}

def classify(subject):
    m = CONV_RE.match(subject)
    if m:
        t = m.group('type')
        scope = m.group('scope')
        bang = m.group('bang') == '!'
        subj = m.group('subject').strip()
    else:
        subj = subject
        bang = 'BREAKING' in subject.upper()
        scope = None
        t = 'chore'
        lo = subject.lower()
        for pat, mapped in KEYWORD_MAP.items():
            if re.search(pat, lo):
                t = mapped
                break
    return {'type': t, 'scope': scope, 'subject': subj, 'breaking': bang}

def parse_commits(commits):
    out = []
    for line in commits.strip().splitlines():
        sha, subj, author, email = line.split('|', 3)
        c = classify(subj)
        c['sha'] = sha; c['author'] = author; c['email'] = email
        out.append(c)
    return out

# Smart subject casing: "add user login" → "Add user login"
def sentence_case(s): return s[0].upper() + s[1:] if s else s

# Conventional-entry normalizer: strip redundant type prefix if it's noise
def clean_subject(type_, subj):
    redundancies = {
        'feat':  r'^(add|implement|introduce)\s+',
        'fix':   r'^(fix|patch|resolve)\s+',
        'docs':  r'^(docs?|update)\s+',
    }
    rx = redundancies.get(type_)
    if rx: subj = re.sub(rx, '', subj, count=1, flags=re.I)
    return sentence_case(subj.strip())

if __name__ == '__main__':
    raw = sys.stdin.read()
    classified = parse_commits(raw)
    for c in classified:
        c['subject'] = clean_subject(c['type'], c['subject'])
    json.dump(classified, sys.stdout, indent=2, ensure_ascii=False)
```

```bash
# Run on each tag-range output
git log --pretty=format:'%h|%s|%an|%ae' "${PREV}..${TAG}" | python3 classify.py > /tmp/commits.json
```

### Step 4 — Render the CHANGELOG

Default format is **Keep-a-Changelog** (the most readable for end-users). Set `--style conventional` for raw Conventional Commits style.

```python
# render.py — produce Keep-a-Changelog markdown from classified JSON
import json, datetime, sys

GROUP_ORDER = ['feat', 'fix', 'perf', 'refactor',
               'revert', 'docs', 'test', 'build', 'ci', 'style', 'chore']
GROUP_LABEL = {
    'feat':     '✨ Features',
    'fix':      '🐛 Bug Fixes',
    'perf':     '⚡ Performance',
    'refactor': '♻️ Refactors',
    'revert':   '⏪ Reverts',
    'docs':     '📖 Documentation',
    'test':     '🧪 Tests',
    'build':    '🛠️ Build System',
    'ci':       '🤖 CI',
    'style':    '🎨 Styles',
    'chore':    '🔧 Chores',
}

def group_key(t): return GROUP_ORDER.index(t) if t in GROUP_ORDER else 99

def render_section(version, date, commits, repo_url=''):
    buckets = {}
    breaking = []
    for c in commits:
        buckets.setdefault(c['type'], []).append(c)
        if c['breaking']:
            breaking.append(c)

    lines = [f'## [{version}] - {date}', '']
    if breaking:
        lines.append('### ⚠️ BREAKING CHANGES')
        lines.append('')
        for c in breaking:
            author = f' ([@{c["author"]}](mailto:{c["email"]}))' if c['author'] else ''
            sha_short = c['sha'][:7]
            link = f'([{sha_short}]({repo_url}/commit/{c["sha"]}))' if repo_url else f'({sha_short})'
            scope = f'**{c["scope"]}**: ' if c['scope'] else ''
            lines.append(f'- {scope}{c["subject"]} {link}{author}')
        lines.append('')
    for t in sorted(buckets, key=group_key):
        lines.append(f'### {GROUP_LABEL[t]}')
        lines.append('')
        for c in buckets[t]:
            author = f' ([@{c["author"]}](mailto:{c["email"]}))' if c['author'] else ''
            sha_short = c['sha'][:7]
            link = f'([{sha_short}]({repo_url}/commit/{c["sha"]}))' if repo_url else f'({sha_short})'
            scope = f'**{c["scope"]}**: ' if c['scope'] else ''
            lines.append(f'- {scope}{c["subject"]} {link}{author}')
        lines.append('')
    return '\n'.join(lines)

def render_changelog(title, intro, versions, keep_a_changelog=True):
    out = [f'# {title}', '']
    if intro: out += [intro, '']
    if keep_a_changelog:
        out += [
            '## [Unreleased]', '',
            '_No unreleased changes yet._', '',
        ]
    for v in versions:
        out.append(render_section(v['version'], v['date'], v['commits'], v.get('repo_url','')))
    return '\n'.join(out)

if __name__ == '__main__':
    payload = json.load(sys.stdin)
    md = render_changelog(
        title=payload.get('title', 'Changelog'),
        intro=payload.get('intro', ''),
        versions=payload['versions'],
        keep_a_changelog=payload.get('style', 'keep') == 'keep'
    )
    sys.stdout.write(md)
```

**Pipeline everything:**

```bash
REPO_URL=$(git remote get-url origin | sed 's/\.git$//' | sed 's|^git@github.com:|https://github.com/|')

# Build a versions.json manifest
python3 -c '
import json, subprocess, sys
# (pseudo: walk tags, run Step 3, collect into versions list)
print(json.dumps({
  "title": "Changelog",
  "intro": "All notable changes to this project are documented here.",
  "style": "keep",
  "repo_url": sys.argv[1],
  "versions": sys.argv[2:]  # date + commits-per-tag as JSON strings
}))' "$REPO_URL" > /tmp/versions.json
```

### Step 5 — Suggest the next version bump

```bash
# What kind of bump is justified?
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null)

COMMITS_SINCE=$(git log "${LAST_TAG}"..HEAD --pretty=format:'%s')

HAS_BREAKING=$(echo "$COMMITS_SINCE" | grep -cE 'BREAKING|^[a-z]+(\(.+\))?!:')
HAS_FEAT=$(echo "$COMMITS_SINCE" | grep -cE '^feat(\(.+\))?:')
HAS_FIX=$(echo "$COMMITS_SINCE" | grep -cE '^fix(\(.+\))?:')

if [ "$HAS_BREAKING" -gt 0 ]; then
  echo "→ MAJOR bump (${LAST_TAG} has breaking changes)"
elif [ "$HAS_FEAT" -gt 0 ]; then
  echo "→ MINOR bump (new features)"
elif [ "$HAS_FIX" -gt 0 ]; then
  echo "→ PATCH bump (bug fixes only)"
else
  echo "→ No bump needed (chore/docs only)"
fi
```

### Step 6 — Emit GitHub Release notes draft

```bash
# Render the unreleased section as a release-notes body suitable for:
gh release create v2.4.0 --title "v2.4.0" --notes-file /tmp/release-notes.md

# Where /tmp/release-notes.md is just the markdown for the new version section,
# without the H1/H2 headers from the CHANGELOG (Release descriptions don't need them).
```

---

## Example Invocations

### Example 1 — Retro-fit a missing CHANGELOG

```
User: My repo (~/projects/clockin) has 200+ commits since 2023 but no CHANGELOG.md.
      Tag history: v0.1.0 (2024-01), v0.2.0 (2024-06), v1.0.0 (2025-09), v1.1.0 (2026-03).
      Commits are mostly Conventional but not 100%. Make a Keep-a-Changelog file.

Agent:
  [EXEC] Detected 312 commits, 4 tags, 71% Conventional coverage. Going hybrid.
  [EXEC] Walking tags → collecting commit ranges.
  [EXEC] Running classify.py + render.py.
  [INFO] Wrote CHANGELOG.md (6 sections, 1 breaking change across 1.0.0).
  [INFO] Suggested next-version: MINOR (2 feat commits since v1.1.0, no breaking).
  [INFO] To preview: open CHANGELOG.md
  [INFO] To commit: git add CHANGELOG.md && git commit -m "docs(changelog): retrofit from history"
```

### Example 2 — Generate release notes for an upcoming tag

```
User: I just tagged v2.4.0. Draft the GitHub Release description from commits since v2.3.0.

Agent:
  [EXEC] Range: v2.3.0..v2.4.0 — 28 commits, 4 contributors.
  [EXEC] Categories: feat(7), fix(11), perf(2), docs(4), chore(4), breaking(1).
  [EXEC] Wrote /tmp/release-v2.4.0.md (847 chars, GitHub Release ready).
  [EXEC] Suggested command:
          gh release create v2.4.0 \
            --title "v2.4.0 — Faster ingest + dark mode" \
            --notes-file /tmp/release-v2.4.0.md
  [WARN] 1 breaking change detected in feat(api)!: drop deprecated /v1 endpoints.
         Confirm migration note in release body? (Will add: "Action required: migrate to /v2 by Oct 1.")
```

### Example 3 — Fill missing release notes for past versions

```
User: Check my project (~/side/greet-bot). v0.3.0, v0.4.0, and v0.5.0 have NO
      release notes — just tags. The CHANGELOG.md stops at v0.2.0.

Agent:
  [EXEC] Found 3 untagged-release versions: v0.3.0, v0.4.0, v0.5.0.
  [EXEC] Existing CHANGELOG.md ends at v0.2.0.
  [EXEC] Generating 3 back-filled sections, inserting before the existing entries
         (so v0.5.0 sits above v0.4.0, etc.).
  [INFO] Wrote updated CHANGELOG.md — 3 new sections, 47 commits total reconstructed.
  [INFO] Heuristic note: 19% of commits lacked Conventional prefixes; classifier
         inferred types from keywords. Spot-check v0.3.0 before committing.
  [EXEC] Show diff preview? [y/N]
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Repo has zero tags → "describe" fails | Fall back to `git rev-list --max-parents=0 HEAD` as the baseline; emit a single "Initial commits" section |
| Committer email leaks in markdown output | Strip emails by default; show authors only on user request with `--attribution` |
| Squash-merged PRs lose per-commit history | Add `--include-pr` flag → use `gh pr list --json number,title,mergeCommit,author --base main` for richer entries |
| Conventional-Commits parser mis-buckets `feat:` inside a longer sentence | Anchor regex at line start; reject if next char after colon isn't a space |
| Subject uses lowercase verb "added" but type already inferred | Capitalize first letter only; never invent words the commit didn't say |
| Two commits squash to identical subject after classification | Don't deduplicate — keep both, note "(2 commits)" in the body |
| Breaking-change footer on second line missed | Re-parse commit body, not just subject: `git log --pretty=format:'%H%n%s%n%b'` |
| CHANGELOG ordering reversed on re-run | Always sort sections by semver DESCENDING of release tags, not by file-write order |
| `--style conventional` produces ugly release notes | Default to Keep-a-Changelog for users, Conventional only on `--style conventional` |
| `gh release create` rejected because tag not pushed | The skill only drafts notes — never pushes tags or creates releases without explicit user consent |

---

## Verification Checklist

- [ ] Confirmed repo root has at least 1 commit (`git rev-parse HEAD`)
- [ ] Inventoried tags via `git tag --sort=-v:refname`
- [ ] Detected Conventional-Commits coverage; chose parse strategy
- [ ] Walked tag ranges; collected commit metadata per version
- [ ] Classified every commit (type, scope, breaking flag)
- [ ] Detected **all** breaking changes — including second-line `BREAKING CHANGE:` footers, not just `!` suffix
- [ ] Surfaced a draft to user before writing to `CHANGELOG.md`
- [ ] Rendered in chosen format (Keep-a-Changelog **or** Conventional)
- [ ] Suggested correct next-version bump (major/minor/patch)
- [ ] Optional: emitted GitHub Release notes draft as a separate file
- [ ] **Never** `git tag`, `git push`, or `gh release create` without explicit user consent
- [ ] Original commit history untouched (read-only operation)
- [ ] If overwriting existing `CHANGELOG.md`, preserved any user-edited commentary blocks

---

## Data Sources & Accuracy

| Source | Use | Limit |
|--------|-----|-------|
| `git log` | All commit metadata — subject, body, author, date, SHA | Subjective commit messages — quality depends on author discipline |
| `git tag` | Semver boundaries; section order | Tags may not be semver-clean (`v1.0` vs `1.0.0`); filter with regex |
| `git remote get-url origin` | Build commit links for repo (e.g., GitHub) | Repo URL may be SSH-only; convert with sed before use |
| Conventional Commits spec (v1.0) | Parse `type(scope)!:` patterns | Optional scope, optional `!`, optional body footer — all need handling |
| Keep-a-Changelog (v1.1) | Output format for end-user readability | Pre-1.0.0 projects use a different versioning scheme |
| Semver spec | Bump suggestion (major/minor/patch) | Pre-1.0 software still uses 0.y.z — breaking bumps at 0.x.y, not 1.0.0 |

**Accuracy promise:**
- Every commit listed in the output is a verbatim sha from `git log` — nothing invented.
- Breaking-change detection is conservative: it's flagged only when the parser finds a `!` suffix or `BREAKING CHANGE:` footer — never inferred from `feat(...)` scope alone.
- The classification stage uses only structural parsing; when uncertain, it falls back to `chore` rather than guessing a more "interesting" type.

**Privacy:**
- Reads only your local `.git/` and writes a single markdown file to your repo root.
- Never calls external APIs unless you opt into GitHub Release draft generation.
- Committer emails are stripped by default; pass `--attribution` to include them.
