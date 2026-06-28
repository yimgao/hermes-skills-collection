---
name: web-clipper
description: "Save, organize, search, and retrieve web bookmarks with tags, descriptions, and page metadata. All data stored locally in JSON."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [utility, bookmark, web-clipper, knowledge-management, productivity, organization]
    related_skills: [file-organizer, format-converter, disk-cleanup-advisor, content-repurposer]
---

# 📎 Web Clipper — 网页剪藏与书签管理

> Save, organize, search, and retrieve web bookmarks with titles, descriptions, tags, and page metadata. All data stored locally as JSON under `~/.hermes/clipper/`. 保存、整理、搜索和提取网页书签，附带标题、描述、标签和页面元数据。所有数据本地存储。

---

## Overview

This skill turns Hermes into a personal web clipper / bookmark manager. When you find an interesting page, tell Hermes to save it. Later, search by keyword, tag, or domain. Get curated lists. Export bookmarks to standard formats (HTML bookmarks, Markdown, JSON).

| Capability | Description |
|------------|-------------|
| **Quick save** | Save a URL with auto-fetched title and description |
| **Rich metadata** | Title, description, domain, tags, notes, screenshot path |
| **Tag-based organization** | Add, search, and filter by tags |
| **Full-text search** | Search across titles, descriptions, notes, and domains |
| **Collections** | Group bookmarks into named collections (e.g. "AI Tools", "Startup Ideas") |
| **List & export** | List by tag, collection, or recent; export to HTML bookmarks, Markdown, or JSON |
| **Deduplication** | Detect and warn about duplicate saves |
| **Local persistence** | All data in `~/.hermes/clipper/bookmarks.json` |

---

## When to Use

- *"Save this page: https://example.com — tagged ai-tools, productivity"*
- *"Show me all my bookmarks tagged ai-tools"*
- *"Search my bookmarks for 'RAG' "*
- *"Export my bookmarks to HTML"*
- *"I want to organize my bookmarks into a collection called 'LLM Papers'"*
- *"Remove the bookmark for https://old-link.com"*
- *"帮我保存这个网页，标签是 技术/AI"*
- *"List my 10 most recent bookmarks"*

---

## Core Workflow

### Step 1: Initialize Storage

On first use, create the directory and JSON file:

```bash
mkdir -p ~/.hermes/clipper
```

The schema for `bookmarks.json`:

```json
{
  "bookmarks": [
    {
      "id": "clip_001",
      "url": "https://example.com",
      "title": "Example Domain",
      "description": "This domain is for use in illustrative examples...",
      "domain": "example.com",
      "tags": ["reference", "example"],
      "collection": "default",
      "notes": "Official example domain for docs",
      "screenshot_path": null,
      "created_at": "2026-06-27T08:00:00Z",
      "updated_at": "2026-06-27T08:00:00Z"
    }
  ],
  "collections": {
    "default": {"name": "默认收藏", "description": "Default collection for general bookmarks"},
    "ai-tools": {"name": "AI 工具", "description": "AI tools and services"}
  },
  "metadata": {
    "version": 1,
    "total_bookmarks": 0,
    "last_updated": "2026-06-27T08:00:00Z"
  }
}
```

### Step 2: Save a Bookmark

When the user says "save this page" or "bookmark this URL":

**1. Extract URL** — Parse the URL from the user's message. If they give a plain URL, use it. If they give a title + URL, use both.

**2. Fetch metadata** — Use `curl -sI` to get the page title and description:

```bash
# Fetch page title from HTML
curl -sL "$URL" | sed -n 's/.*<title>\(.*\)<\/title>.*/\1/p' | head -1

# Fetch meta description
curl -sL "$URL" | sed -n 's/.*<meta name="description" content="\([^"]*\)".*/\1/p' | head -1

# Extract domain
echo "$URL" | sed -E 's#https?://([^/]+).*#\1#'
```

If the page is unreachable (timeout, 404, etc.), still save the bookmark but mark `"fetch_status": "unreachable"` and use whatever info the user provided.

**3. Check for duplicates** — Before saving, check if the URL already exists:

```bash
jq --arg url "$URL" '[.bookmarks[] | select(.url == $url) | .id] | length' ~/.hermes/clipper/bookmarks.json
```

If found, warn: *"This URL is already saved (ID: clip_003, saved on 2026-06-26). Overwrite or skip?"*

**4. Add the bookmark** — Use `jq` to append:

```bash
ID="clip_$(date +%s)"
TITLE="..."
DOMAIN="..."
TAGS=$(printf '%s\n' "$TAGS" | jq -R -s -c 'split("\n") | map(select(length > 0))')
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

jq \
  --arg id "$ID" \
  --arg url "$URL" \
  --arg title "$TITLE" \
  --arg description "$DESC" \
  --arg domain "$DOMAIN" \
  --argjson tags "$TAGS" \
  --arg now "$NOW" \
  '.bookmarks += [{
    "id": $id,
    "url": $url,
    "title": $title,
    "description": $description,
    "domain": $domain,
    "tags": $tags,
    "collection": "default",
    "notes": "",
    "screenshot_path": null,
    "created_at": $now,
    "updated_at": $now
  }] | .metadata.total_bookmarks += 1 | .metadata.last_updated = $now' \
  ~/.hermes/clipper/bookmarks.json > /tmp/clipper_tmp.json && mv /tmp/clipper_tmp.json ~/.hermes/clipper/bookmarks.json
```

**5. Confirm** — Print a summary:

```
📎 Saved: Example Domain
  URL:      https://example.com
  Domain:   example.com
  Tags:     reference, example
  ID:       clip_1719388800
  📊 Total bookmarks: 12
```

### Step 3: Search & Organize

**Search by keyword** — Search across title, description, notes, and domain:

```bash
KEYWORD="rag"
jq --arg kw "$KEYWORD" '[.bookmarks[] | select(
  (.title | test($kw; "i")) or
  (.description | test($kw; "i")) or
  (.notes | test($kw; "i")) or
  (.domain | test($kw; "i"))
)] | sort_by(.created_at) | reverse' ~/.hermes/clipper/bookmarks.json
```

**Filter by tag**:

```bash
TAG="ai-tools"
jq --arg tag "$TAG" '[.bookmarks[] | select(.tags | index($tag))] | sort_by(.created_at) | reverse' ~/.hermes/clipper/bookmarks.json
```

**List by collection**:

```bash
jq -r --arg col "ai-tools" '.bookmarks[] | select(.collection == $col) | [.id, .title, .domain, (.tags | join(","))] | @tsv' ~/.hermes/clipper/bookmarks.json | column -t -s $'\t'
```

**List recent bookmarks** (last N, default 10):

```bash
jq -r '.bookmarks | sort_by(.created_at) | reverse[:10][] | [.id, .title, .domain, .created_at[0:10]] | @tsv' ~/.hermes/clipper/bookmarks.json | column -t -s $'\t'
```

### Step 4: Export

**Export to HTML bookmarks** (compatible with Chrome/Firefox):

```python
python3 -c "
import json, sys
with open('$HOME/.hermes/clipper/bookmarks.json') as f:
    data = json.load(f)
print('<!DOCTYPE NETSCAPE-Bookmark-file-1>')
print('<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">')
print('<TITLE>Bookmarks</TITLE>')
print('<H1>Bookmarks</H1>')
print('<DL><p>')
for b in sorted(data['bookmarks'], key=lambda x: x['created_at'], reverse=True):
    tags = '+'.join(b['tags']) if b['tags'] else ''
    print(f'    <DT><A HREF=\"{b[\"url\"]}\" TAGS=\"{tags}\">{b[\"title\"]}</A>')
    if b.get('description'):
        print(f'    <DD>{b[\"description\"]}')
print('</DL><p>')
"
```

**Export to Markdown**:

```
# My Bookmarks (exported 2026-06-27)

## AI Tools
- [ChatGPT](https://chat.openai.com) — OpenAI's conversational AI. Tags: ai, chatbot
- [Claude](https://claude.ai) — Anthropic's assistant. Tags: ai, assistant

## Reference
...
```

**Export to JSON** (raw data):

```bash
cp ~/.hermes/clipper/bookmarks.json ~/bookmarks_export_$(date +%Y%m%d).json
```

### Step 5: Manage Collections

**Create a collection**:

```bash
jq --arg name "llm-papers" --arg desc "LLM research papers worth revisiting" \
  '.collections[$name] = {"name": $name, "description": $desc}' \
  ~/.hermes/clipper/bookmarks.json > /tmp/clipper_tmp.json && mv /tmp/clipper_tmp.json ~/.hermes/clipper/bookmarks.json
```

**Move bookmarks between collections**:

```bash
jq --arg id "clip_005" --arg col "llm-papers" \
  '(.bookmarks[] | select(.id == $id) | .collection) = $col' \
  ~/.hermes/clipper/bookmarks.json > /tmp/clipper_tmp.json && mv /tmp/clipper_tmp.json ~/.hermes/clipper/bookmarks.json
```

**Delete a bookmark**:

```bash
jq --arg id "clip_005" \
  'del(.bookmarks[] | select(.id == $id)) | .metadata.total_bookmarks -= 1' \
  ~/.hermes/clipper/bookmarks.json > /tmp/clipper_tmp.json && mv /tmp/clipper_tmp.json ~/.hermes/clipper/bookmarks.json
```

---

## Example Invocations

### Example 1: Saving a page with tags

**User:**
> Save this page: https://github.com/features/copilot — tags: ai-tools, coding, productivity — notes: GitHub Copilot features page

**Agent:**
```
[FETCH] Fetching metadata from https://github.com/features/copilot...
📎 Saved: GitHub Copilot · Your AI pair programmer
  URL:      https://github.com/features/copilot
  Domain:   github.com
  Tags:     ai-tools, coding, productivity
  Notes:    GitHub Copilot features page
  ID:       clip_1719388800
  📊 Total bookmarks: 15
```

### Example 2: Searching and browsing bookmarks

**User:**
> Show me all my bookmarks tagged "ai-tools"

**Agent:**
```
🔍 Bookmarks tagged: ai-tools (5 results)
──────────────────────────────────────────
clip_010 | GitHub Copilot | github.com | 2026-06-27
clip_008 | Claude.ai      | claude.ai  | 2026-06-25
clip_005 | ChatGPT         | chat.openai.com | 2026-06-22
clip_003 | Perplexity AI   | perplexity.ai   | 2026-06-20
clip_001 | Hugging Face    | huggingface.co  | 2026-06-18

Tip: Use "show details for clip_010" to see full info.
```

**User:**
> Show details for clip_008

**Agent:**
```
📄 Bookmark Details: Claude.ai
──────────────────────────────────────────
  URL:        https://claude.ai
  Domain:     claude.ai
  Tags:       ai-tools, assistant
  Collection: default
  Notes:      Anthropic's AI assistant — great for coding help
  Created:    2026-06-25
```

### Example 3: Export and organization

**User:**
> Create a collection called "LLM Papers" and move all bookmarks with the tag "llm" into it. Then export to HTML.

**Agent:**
```
📁 Created collection "LLM Papers"
  Description: LLM research papers worth revisiting

📦 Moved 3 bookmarks to "LLM Papers"
  - clip_004 | Attention Is All You Need
  - clip_007 | RLHF paper
  - clip_009 | GPT-4 technical report

📤 Exported to ~/bookmarks_export_20260627.html
  (compatible with Chrome, Firefox, Edge — open File → Import Bookmarks)
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| URL is malformed or missing protocol | Auto-prepend `https://` if missing; validate with `python3 -c "from urllib.parse import urlparse; u=urlparse('...'); assert u.scheme and u.netloc"` |
| Page fetch fails (timeout/404) | Still save the bookmark with `"fetch_status": "unreachable"` and use user-provided info; note in response: "Page unreachable — saved with your description only" |
| User saves the same URL multiple times | Before saving, check for existing URL; warn and ask to overwrite or skip |
| Tags with spaces or special chars | Normalize: lowercase, replace spaces with hyphens, strip special chars; e.g. "AI Tools" → "ai-tools" |
| Too many bookmarks slow down jq | Suggest archiving old/unused bookmarks into a separate archive file (`bookmarks_archive.json`); the main file should stay under 500 entries |
| User says "save this" without providing a URL | Ask: "Please provide the URL you'd like to save" |
| Timezone muddles sorting | Always use UTC ISO 8601 timestamps; display dates in user's local time on output |
| Accidental deletion | Keep a backup: `cp bookmarks.json bookmarks.json.bak` before destructive operations |

---

## Verification Checklist

- [ ] `~/.hermes/clipper/bookmarks.json` is created on first use with valid schema
- [ ] Saving a URL auto-fetches title and description from the page
- [ ] Duplicate URL detection warns before saving
- [ ] Search by keyword returns matches from title, description, notes, and domain
- [ ] Tag filtering works with single and multiple tags
- [ ] Bookmarks can be moved between collections
- [ ] Export to HTML produces valid Netscape bookmark format (importable by Chrome/Firefox)
- [ ] Export to Markdown produces readable output with organized sections
- [ ] Deleting a bookmark removes it and updates the total count
- [ ] Unreachable pages are saved with a warning and no metadata

---

## Data Sources & Accuracy

- **User-provided URLs** — The skill depends entirely on the URLs the user provides. Link rot (dead links) is detected at save time but not proactively rechecked.
- **Metadata fetching** — Title and description are fetched via `curl -sL` + HTML parsing. Accuracy depends on the page's `<title>` and `<meta name="description">` tags. Sites behind login walls or JS-rendered content (SPAs) may return empty metadata — the user can provide manual descriptions in such cases.
- **All data is local** — Stored at `~/.hermes/clipper/bookmarks.json`. No data is sent to any external service.
- **Deduplication** — Based on exact URL match. The same URL with different tracking parameters (`?utm_source=...`) is treated as a different URL unless the user explicitly normalizes.
- **Backup** — Before any destructive operation (delete, batch move), a backup is created at `bookmarks.json.bak`.
