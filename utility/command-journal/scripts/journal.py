#!/usr/bin/env python3
"""
command-journal — a searchable memory for the commands you actually run.

Subcommands:
  add       Save a recipe / command / note into the journal.
  search    Full-text search across recipes + ingested shell history.
  history   Ingest shell history files into the journal (idempotent).
  list      List recipes, newest first.
  show      Print one recipe in full.
  forget    Delete a recipe by id.
  stats     Frequency report: top commands, tools, history health.
  export    Dump the journal as Markdown / JSON.

Storage:  ~/.hermes/command-journal/journal.json   (single JSON file, atomic writes)
           ~/.hermes/command-journal/history.json   (ingested history cache)

Stdlib only. No network. Nothing leaves the machine.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

HOME = Path.home()
BASE = Path(os.environ.get("COMMAND_JOURNAL_HOME", HOME / ".hermes" / "command-journal"))
JOURNAL = BASE / "journal.json"
HISTORY = BASE / "history.json"
SCHEMA = 1

# ---------------------------------------------------------------- utilities

NOISY = {
    "ls", "cd", "pwd", "clear", "exit", "vim", "vi", "nano", "code", "open",
    "cat", "head", "tail", "less", "more", "echo", "which", "whoami", "date",
    "man", "sudo", "brew", "git", "tmux", "history", "top", "htop",
}

# Commands worth indexing for "how did I do X again" recall.
INTERESTING = re.compile(
    r"^(sudo\s+)?("
    r"docker|kubectl|helm|terraform|ansible|vagrant|aws|gcloud|az|"
    r"psql|mysql|mongosh|redis-cli|sqlite3|"
    r"ffmpeg|convert|magick|rsync|scp|ssh|tar|zip|unzip|"
    r"jq|yq|curl|wget|openssl|gpg|"
    r"npm|pnpm|yarn|pip|pipx|uv|poetry|poe|uvx|cargo|go|rustc|"
    r"python3?|node|deno|bun|ruby|perl|"
    r"make|cmake|gradle|mvn|mvnw|pytest|jest|vitest|eslint|prettier|"
    r"gh|glab|systemctl|launchctl|"
    r"defaults|"
    r"a-zA-Z0-9_-]+"
    r")(\s|$)"
)


def now() -> float:
    return time.time()


def iso(ts: float | None = None) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(ts or now()))


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.chmod(0o700)  # recipes may contain hostnames, paths, maybe credentials
    except OSError:
        pass
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        tmp.chmod(0o600)
    except OSError:
        pass
    tmp.replace(path)


def load_journal() -> dict:
    data = read_json(JOURNAL, {})
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        data = {"schema": SCHEMA, "recipes": [], "created": iso()}
    data.setdefault("recipes", [])
    return data


def save_journal(data: dict) -> None:
    write_json(JOURNAL, data)


def new_id(data: dict) -> str:
    n = sum(1 for r in data["recipes"] if str(r.get("id", "")).startswith("cj-"))
    return f"cj-{n + 1:04d}"


# ------------------------------------------------------------ shell history

HISTORY_FILES = [
    HOME / ".zsh_history",
    HOME / ".bash_history",
    HOME / ".local" / "share" / "fish" / "fish_history",
]


def parse_history_line(line: str) -> tuple[str, float | None]:
    """Return (command, timestamp). Handles zsh extended history format."""
    ts = None
    # zsh: ": 1699999999:0;ls -la"
    m = re.match(r"^:\s*(\d+):\d+;(.*)$", line)
    if m:
        ts = float(m.group(1))
        return m.group(2).strip(), ts
    # bash with timestamps: "#1699999999"
    m = re.match(r"^#(\d{9,})$", line)
    if m:
        return "", float(m.group(1))
    return line.strip(), ts


def iter_history_files(paths: Iterable[str] | None) -> list[Path]:
    if paths:
        return [Path(p).expanduser() for p in paths]
    return [p for p in HISTORY_FILES if p.exists()]


def read_history_files(paths: Iterable[str] | None) -> list[tuple[str, float | None, str]]:
    """-> list of (command, timestamp, source)"""
    out: list[tuple[str, float | None, str]] = []
    for p in iter_history_files(paths):
        try:
            raw = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        pending_ts: float | None = None
        for line in raw.splitlines():
            if not line.strip():
                continue
            cmd, ts = parse_history_line(line)
            if ts is not None and not cmd:
                pending_ts = ts
                continue
            if not cmd:
                continue
            out.append((cmd, ts or pending_ts, p.name))
            pending_ts = None
    return out


def normalize_command(cmd: str) -> str:
    return re.sub(r"\s+", " ", cmd.strip().rstrip(";"))


def head_token(cmd: str) -> str:
    """First meaningful token of a command (handles sudo/env/assignments)."""
    try:
        parts = shlex.split(cmd)
    except ValueError:
        parts = cmd.split()
    for tok in parts:
        if tok.startswith("-"):
            continue
        if tok in {"sudo", "env", "command", "nohup", "time", "nice", "xargs"}:
            continue
        if "=" in tok and not tok.startswith("=") and "/" not in tok:
            continue
        return tok
    return ""


def is_useful(cmd: str) -> bool:
    c = normalize_command(cmd)
    if len(c) < 6 or len(c) > 2000:
        return False
    low = c.lower()
    if low in NOISY:
        return False
    if low.startswith(("cd ", "ls", "git status", "code ", "open ", "man ")):
        return False
    if not INTERESTING.match(c):
        return False
    # must contain at least one flag or a subcommand-ish token
    if "-" not in c and not re.search(r"\s\w", c):
        return False
    return True


# ------------------------------------------------------------------ scoring

STOP = {
    "the", "a", "an", "and", "or", "to", "for", "of", "in", "on", "with",
    "how", "do", "i", "my", "me", "again", "was", "did", "it", "that",
    "this", "cmd", "command", "commands", "shell", "bash", "zsh", "run",
}


def tokenize(text: str) -> list[str]:
    raw = re.findall(r"[A-Za-z0-9_\-./:]+", text.lower())
    return [t for t in raw if t not in STOP and len(t) > 1]


def score(recipe: dict, terms: list[str]) -> float:
    """Weighted match: title > tags > note > command. Returns 0 if nothing matched."""
    if not terms:
        return 0.0
    title = (recipe.get("title") or "").lower()
    tags = " ".join(recipe.get("tags") or []).lower()
    note = (recipe.get("note") or "").lower()
    cmd = (recipe.get("command") or "").lower()
    total = 0.0
    matched = 0
    for t in terms:
        w = 0.0
        if t in title:
            w += 5.0
            matched += 1
        if t in tags:
            w += 3.0
            matched += 1
        if t in note:
            w += 2.0
            matched += 1
        if t in cmd:
            w += 1.5
            matched += 1
        if t in title.split():
            w += 2.0
        total += w
    if matched == 0:
        return 0.0
    # exact command match is a strong signal
    if recipe.get("command") and normalize_command(recipe["command"]).lower() == " ".join(terms):
        total += 20.0
    # recency boost — only for recipes that actually matched something
    age_days = max(0.0, (now() - float(recipe.get("ts", now()))) / 86400.0)
    total += max(0.0, 2.0 - age_days / 90.0)
    return total


# --------------------------------------------------------------- subcommands


def cmd_add(args: argparse.Namespace) -> int:
    data = load_journal()
    cmd = normalize_command(args.command)
    if not cmd:
        print("ERROR: empty command", file=sys.stderr)
        return 2
    rid = new_id(data)
    recipe = {
        "id": rid,
        "title": args.title or cmd[:60],
        "command": cmd,
        "note": args.note or "",
        "tags": sorted({t.strip().lower() for t in (args.tags or "").split(",") if t.strip()}),
        "cwd": args.cwd or os.getcwd(),
        "ts": now(),
        "created": iso(),
        "source": "manual",
    }
    if args.run:
        recipe["last_run"] = iso()
        recipe["run_count"] = 1
    data["recipes"].append(recipe)
    save_journal(data)
    print(f"saved {rid}: {recipe['title']}")
    if args.run:
        print("marked as just-run (this skill records commands, it never executes them)")
    return 0


def cmd_history(args: argparse.Namespace) -> int:
    entries = read_history_files(args.file)
    if not entries:
        print("no history files found (looked for ~/.zsh_history, ~/.bash_history, fish_history)")
        return 1
    cache = read_json(HISTORY, {"schema": SCHEMA, "commands": []})
    known = cache.get("commands", [])
    seen = {c["command"] for c in known}
    added = 0
    useful_only = not args.all
    for raw, ts, src in entries:
        c = normalize_command(raw)
        if not c or c in seen:
            continue
        if useful_only and not is_useful(c):
            continue
        seen.add(c)
        known.append({
            "command": c,
            "ts": ts or 0,
            "source": src,
            "tool": head_token(c),
        })
        added += 1
    known.sort(key=lambda x: -float(x.get("ts") or 0))
    cache["commands"] = known
    cache["updated"] = iso()
    write_json(HISTORY, cache)
    total = len(known)
    print(f"history: +{added} new, {total} total indexed (from {len(entries)} raw lines)")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    data = load_journal()
    terms = tokenize(" ".join(args.query))
    if not terms:
        print("ERROR: query has no searchable terms", file=sys.stderr)
        return 2

    hits: list[tuple[float, dict, str]] = []
    for r in data["recipes"]:
        s = score(r, terms)
        if s > 0:
            hits.append((s, r, "recipe"))

    hist = read_json(HISTORY, {"commands": []})
    for c in hist.get("commands", []):
        cmd = c.get("command", "")
        s = 0.0
        low = cmd.lower()
        for t in terms:
            if t in low:
                s += 1.0
        if s > 0:
            pseudo = {
                "id": f"h:{abs(hash(cmd)) % 10**8}",
                "title": cmd[:70],
                "command": cmd,
                "note": "",
                "tags": [],
                "ts": c.get("ts") or 0,
                "source": "history",
                "tool": c.get("tool", ""),
            }
            hits.append((s, pseudo, "history"))

    hits.sort(key=lambda x: -x[0])
    if args.limit:
        hits = hits[: args.limit]

    if not hits:
        print(f"no matches for: {args.query!r}")
        print("hint: run `journal.py history` to index your shell history first")
        return 1

    if args.json:
        print(json.dumps([h[1] for h in hits], ensure_ascii=False, indent=2))
        return 0

    for i, (s, r, kind) in enumerate(hits, 1):
        badge = "RECIPE" if kind == "recipe" else "HISTORY"
        print(f"{i}. [{badge}] {r['title']}")
        if r.get("note"):
            print(f"   note: {r['note']}")
        if r.get("tags"):
            print(f"   tags: {', '.join(r['tags'])}")
        print(f"   $ {r['command']}")
        if kind == "recipe":
            print(f"   id: {r['id']}   score: {s:.1f}")
        else:
            ts = r.get("ts") or 0
            if ts:
                print(f"   last used: {iso(ts)}")
        print()
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    data = load_journal()
    recipes = sorted(data["recipes"], key=lambda r: -float(r.get("ts", 0)))
    if args.tag:
        recipes = [r for r in recipes if args.tag.lower() in (r.get("tags") or [])]
    if args.limit:
        recipes = recipes[: args.limit]
    if not recipes:
        print("journal is empty — add your first recipe with `journal.py add`")
        return 1
    for r in recipes:
        tags = ",".join(r.get("tags") or [])
        print(f"{r['id']}  {r.get('created', '')}  {r['title']}")
        print(f"      $ {r['command']}")
        if tags:
            print(f"      tags: {tags}")
    print(f"\n{len(recipes)} recipe(s)")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    data = load_journal()
    for r in data["recipes"]:
        if r["id"] == args.id:
            print(json.dumps(r, ensure_ascii=False, indent=2))
            return 0
    print(f"no recipe with id {args.id}", file=sys.stderr)
    return 1


def cmd_forget(args: argparse.Namespace) -> int:
    data = load_journal()
    before = len(data["recipes"])
    data["recipes"] = [r for r in data["recipes"] if r["id"] != args.id]
    if len(data["recipes"]) == before:
        print(f"no recipe with id {args.id}", file=sys.stderr)
        return 1
    save_journal(data)
    print(f"forgot {args.id}")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    data = load_journal()
    recipes = data["recipes"]
    hist = read_json(HISTORY, {"commands": []}).get("commands", [])
    print(f"recipes        : {len(recipes)}")
    print(f"history indexed: {len(hist)}")
    tools = Counter((r.get("tags") or ["untagged"])[0] for r in recipes)
    if tools:
        print("\ntop tags:")
        for t, c in tools.most_common(8):
            print(f"  {c:>3}  {t}")
    hist_tools = Counter(c.get("tool", "") for c in hist if c.get("tool"))
    if hist_tools:
        print("\ntop history tools:")
        for t, c in hist_tools.most_common(10):
            print(f"  {c:>4}  {t}")
    # stale: recipes unused for a long time
    if recipes:
        cutoff = now() - 180 * 86400
        stale = [r for r in recipes if float(r.get("ts", 0)) < cutoff]
        if stale:
            print(f"\nstale (>180d, never re-run): {len(stale)}")
            for r in stale[:5]:
                print(f"  {r['id']}  {r['title']}")
    print(f"\njournal file: {JOURNAL}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    data = load_journal()
    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    lines = ["# Command Journal", "", f"_exported {iso()}_", ""]
    for r in sorted(data["recipes"], key=lambda x: -float(x.get("ts", 0))):
        lines.append(f"## {r['title']}")
        lines.append("")
        lines.append("```bash")
        lines.append(r["command"])
        lines.append("```")
        if r.get("note"):
            lines += ["", r["note"]]
        if r.get("tags"):
            lines += ["", f"tags: {', '.join(r['tags'])}"]
        lines += ["", f"`{r['id']}` · {r.get('created', '')}", ""]
    text = "\n".join(lines)
    if args.out:
        Path(args.out).expanduser().write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


# ---------------------------------------------------------------------- CLI


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="journal.py", description="Searchable memory for your own commands and recipes.")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="save a recipe")
    a.add_argument("command", help="the command (quote it)")
    a.add_argument("--title", default="")
    a.add_argument("--note", default="")
    a.add_argument("--tags", default="", help="comma-separated")
    a.add_argument("--cwd", default="")
    a.add_argument("--run", action="store_true", help="acknowledge you just ran it (records last_run)")
    a.set_defaults(func=cmd_add)

    h = sub.add_parser("history", help="ingest shell history into the journal")
    h.add_argument("--file", action="append", help="extra history file (repeatable)")
    h.add_argument("--all", action="store_true", help="index everything, not just useful commands")
    h.set_defaults(func=cmd_history, useful_only=True)

    s = sub.add_parser("search", help="full-text search")
    s.add_argument("query", nargs="+")
    s.add_argument("--limit", type=int, default=10)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_search)

    l = sub.add_parser("list", help="list recipes")
    l.add_argument("--tag", default="")
    l.add_argument("--limit", type=int, default=0)
    l.set_defaults(func=cmd_list)

    sh = sub.add_parser("show", help="print one recipe as JSON")
    sh.add_argument("id")
    sh.set_defaults(func=cmd_show)

    f = sub.add_parser("forget", help="delete a recipe")
    f.add_argument("id")
    f.set_defaults(func=cmd_forget)

    st = sub.add_parser("stats", help="frequency report")
    st.set_defaults(func=cmd_stats)

    e = sub.add_parser("export", help="export journal")
    e.add_argument("--format", choices=["md", "json"], default="md")
    e.add_argument("--out", default="")
    e.set_defaults(func=cmd_export)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
