#!/usr/bin/env python3
"""harvest.py — pull review evidence out of git, OKR files, and work canvases.

Produces CANDIDATE wins with a confidence rating. It never invents metrics:
if a candidate has no number, it says so and leaves the number blank for you.

Usage:
  python3 harvest.py --since 2026-07-01 --repo ~/dev/acme/api --out ~/perf/candidates.md
  python3 harvest.py --since 2026-07-01 --scan ~/dev/acme --author me@acme.com
  python3 harvest.py --since 2026-07-01 --repo . --json
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

CONVENTIONAL = ("feat", "fix", "perf", "refactor", "docs", "test", "chore", "build", "ci", "style", "revert")
HIGH_VALUE = {"feat", "perf", "fix", "refactor"}
PERF_WORDS = re.compile(r"\b(p95|p99|p50|latency|throughput|qps|rps|faster|slower|memory|cpu|cost|"
                        r"bundle|size|startup|timeout|retry|reduce|cut|optimi[sz])\b", re.I)
SCALE_WORDS = re.compile(r"\b(migrat|rollout|launch|shipp?ed|release|rearchitect|redesign|"
                         r"rewrite|cutover|onboard|incident|outage|postmortem)\b", re.I)
PR_RE = re.compile(r"(?:#|pull/|PR[ -]?)(\d{2,6})\b")


def run(cmd, cwd=None):
    try:
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120).stdout
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"[WARN] {' '.join(cmd)}: {e}", file=sys.stderr)
        return ""


def is_git_repo(p):
    return (Path(p) / ".git").exists()


def discover(root):
    root = Path(os.path.expanduser(root))
    if is_git_repo(root):
        return [root]
    found = []
    for child in sorted(root.iterdir()) if root.exists() else []:
        if child.is_dir() and is_git_repo(child):
            found.append(child)
    return found


FIELDS = ("%H", "%ad", "%s", "%b")
SEP = "\x1f"


def git_commits(repo, since, author, until=None):
    fmt = SEP.join(FIELDS) + "\x1e"
    cmd = ["git", "log", f"--since={since}", "--date=short",
           f"--pretty=format:{fmt}", "--no-merges"]
    if until:
        cmd.insert(2, f"--until={until}")
    if author:
        cmd.insert(2, f"--author={author}")
    out = run(cmd, cwd=repo)
    commits = []
    for chunk in out.split("\x1e"):
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        parts = chunk.split(SEP)
        if len(parts) < 3:
            continue
        sha, adate, subject = parts[0], parts[1], parts[2]
        body = parts[3] if len(parts) > 3 else ""
        d = parse_any_date(adate)
        if d is None:
            continue
        commits.append({"sha": sha[:8], "date": d, "subject": subject, "body": body})
    return commits


def parse_any_date(s):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%a %b %d %H:%M:%S %Y %z"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def numstat(repo, shas):
    """Return {sha: (insertions, deletions, [files])} in one git call."""
    if not shas:
        return {}
    out = run(["git", "show", "--numstat", "--format=%x01%H"] + shas, cwd=repo)
    stats, cur = {}, None
    for line in out.splitlines():
        if line.startswith("\x01"):
            cur = line[1:].strip()[:8]
            stats[cur] = [0, 0, []]
            continue
        if cur and line.strip():
            p = line.split("\t")
            if len(p) < 3:
                continue
            try:
                stats[cur][0] += int(p[0])
                stats[cur][1] += int(p[1])
            except ValueError:
                pass  # binary file
            stats[cur][2].append(p[2])
    return stats


def classify(subject):
    m = re.match(r"^(\w+)(?:\([^)]*\))?!?:", subject)
    if m and m.group(1).lower() in CONVENTIONAL:
        return m.group(1).lower()
    return "other"


def cluster(commits, stats):
    """Group commits into candidate themes by conventional prefix + shared area."""
    groups = defaultdict(list)
    for c in commits:
        typ = classify(c["subject"])
        files = stats.get(c["sha"], [0, 0, []])[2]
        area = "root"
        if files:
            firsts = Counter(f.split("/")[0] for f in files if "/" in f)
            if firsts:
                area = firsts.most_common(1)[0][0]
        key = (typ, area)
        groups[key].append(c)
    return groups


def confidence(typ, n, ins, keywords_hit, prs):
    if prs and (keywords_hit or typ in ("perf", "feat")):
        return "high"
    if typ in HIGH_VALUE and n >= 3:
        return "medium"
    if n >= 8:
        return "medium"  # volume cluster — almost certainly a real theme
    if keywords_hit:
        return "medium"
    return "low"


def harvest_repo(repo, since, author, until=None):
    commits = git_commits(repo, since, author, until)
    if not commits:
        return []
    stats = numstat(repo, [c["sha"] for c in commits])
    by_sha = {c["sha"]: c for c in commits}
    out = []
    for (typ, area), group in cluster(commits, stats).items():
        ins = sum(stats.get(c["sha"], [0, 0, []])[0] for c in group)
        dele = sum(stats.get(c["sha"], [0, 0, []])[1] for c in group)
        files = set()
        for c in group:
            files.update(stats.get(c["sha"], [0, 0, []])[2])
        text = " ".join(c["subject"] + " " + c["body"] for c in group)
        prs = sorted(set(PR_RE.findall(text)))
        kw = bool(PERF_WORDS.search(text))
        scale = bool(SCALE_WORDS.search(text))
        subjects = sorted(group, key=lambda c: c["date"])
        out.append({
            "repo": repo.name,
            "theme": f"{area if area != '*' else 'mixed'}/{typ}",
            "type": typ,
            "area": area,
            "commits": len(group),
            "insertions": ins,
            "deletions": dele,
            "files": len(files),
            "first": subjects[0]["date"].isoformat(),
            "last": subjects[-1]["date"].isoformat(),
            "samples": [c["subject"] for c in subjects[:3]],
            "prs": prs[:5],
            "perf_words": kw,
            "scale_words": scale,
            "confidence": confidence(typ, len(group), ins, kw or scale, prs),
            "metric": None,
        })
    return out


def harvest_okr():
    out = []
    for p in sorted(Path.home().glob(".hermes/goals/*.json")):
        try:
            doc = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for obj in doc.get("objectives", []):
            krs = obj.get("krs", [])
            done = [k for k in krs if (k.get("progress") or 0) >= 0.9]
            if not krs:
                continue
            avg = sum((k.get("progress") or 0) for k in krs) / len(krs)
            out.append({
                "period": p.stem,
                "title": obj.get("title", "?"),
                "progress": round(avg, 2),
                "status": obj.get("status", "?"),
                "krs_total": len(krs),
                "krs_done": len(done),
                "confidence": "high" if avg >= 0.8 else "medium" if avg >= 0.4 else "low",
            })
    return out


DONE_RE = re.compile(r"^\s*[-*]?\s*(?:done|完成)\s*[::]\s*(.+)$", re.I)


def harvest_canvas():
    out = []
    base = Path.home() / ".hermes/data/deep-work-canvas"
    for p in sorted(base.glob("*.md")):
        try:
            lines = p.read_text(errors="ignore").splitlines()
        except OSError:
            continue
        items = [m.group(1).strip() for m in (DONE_RE.match(l) for l in lines) if m]
        if items:
            out.append({"project": p.stem, "done_items": len(items),
                        "samples": items[-4:], "confidence": "medium"})
    return out


def render_md(repo_rows, okr_rows, canvas_rows, since, author):
    L = [f"# Review evidence candidates — since {since}"
         f"{f' · author {author}' if author else ''}", ""]
    L.append("> Candidates only. Add a number + impact radius before they enter your brag doc.")
    L.append("> Anything with `metric: MISSING` needs you to supply the number.\n")

    if repo_rows:
        L.append("## Git evidence\n")
        L.append("| Conf | Repo | Theme | Commits | +/− | Period | What happened | Metric |")
        L.append("|---|---|---|---|---|---|---|---|")
        order = {"high": 0, "medium": 1, "low": 2}
        for r in sorted(repo_rows, key=lambda x: (order[x["confidence"]], -x["commits"])):
            sample = "; ".join(s[:60] for s in r["samples"][:2])
            pr = f" PR#{','.join(r['prs'][:2])}" if r["prs"] else ""
            L.append(f"| {r['confidence']} | {r['repo']} | `{r['theme']}` | {r['commits']} | "
                     f"+{r['insertions']}/−{r['deletions']} | {r['first']}→{r['last']} | "
                     f"{sample}{pr} | MISSING |")
        L.append("")
        low = [r for r in repo_rows if r["confidence"] == "low"]
        if low:
            L.append(f"**{len(low)} low-confidence group(s)** — chore/docs/style or a single "
                     "unfamiliar commit. Usually not review material. Ignore unless you "
                     "remember why it mattered.\n")

    if okr_rows:
        L.append("## OKR progress\n")
        L.append("| Period | Objective | Progress | Status | KRs done | Conf |")
        L.append("|---|---|---|---|---|---|")
        for o in okr_rows:
            L.append(f"| {o['period']} | {o['title'][:70]} | {int(o['progress']*100)}% | "
                     f"{o['status']} | {o['krs_done']}/{o['krs_total']} | {o['confidence']} |")
        L.append("")

    if canvas_rows:
        L.append("## Work-canvas `done:` items\n")
        for c in canvas_rows:
            L.append(f"- **{c['project']}** ({c['done_items']} done)")
            for s in c["samples"]:
                L.append(f"  - {s}")
        L.append("")

    if not (repo_rows or okr_rows or canvas_rows):
        L.append("_No evidence found. Check `--since`, `--author`, and that the paths are git repos._")

    L.append("---\n## Next step\n")
    L.append("For each row you keep, run:\n")
    L.append("```bash")
    L.append("python3 brag.py add --title '<verb + number>' --scope team|org --axis technical \\")
    L.append("  --metric '<name>' --before N --after M --unit ms --evidence '<PR url>'")
    L.append("```")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description="Harvest review evidence from local repos + trackers")
    ap.add_argument("--since", required=True, help="YYYY-MM-DD (or 90d / 3m)")
    ap.add_argument("--until")
    ap.add_argument("--repo", action="append", default=[], help="repo path (repeatable)")
    ap.add_argument("--scan", help="directory whose child folders are git repos")
    ap.add_argument("--author", help="git author filter (default: git config user.email)")
    ap.add_argument("--out", help="write markdown here")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--no-okr", action="store_true")
    ap.add_argument("--no-canvas", action="store_true")
    args = ap.parse_args()

    since = args.since
    m = re.fullmatch(r"(\d+)\s*([dm])", since)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        since = (date.today() - __import__("datetime").timedelta(days=n * (30 if unit == "m" else 1))).isoformat()

    author = args.author
    if not author:
        author = run(["git", "config", "user.email"]).strip() or None

    repos = [Path(os.path.expanduser(r)).resolve() for r in args.repo]
    if args.scan:
        repos += [p.resolve() for p in discover(args.scan)]
    repos = [r for r in repos if r.exists()]
    if not repos and not args.json:
        print("[WARN] no repos given — pass --repo or --scan", file=sys.stderr)

    repo_rows = []
    for r in repos:
        rows = harvest_repo(r, since, author, args.until)
        repo_rows.extend(rows)
        print(f"[INFO] {r.name}: {len(rows)} candidate theme(s)", file=sys.stderr)

    okr_rows = [] if args.no_okr else harvest_okr()
    canvas_rows = [] if args.no_canvas else harvest_canvas()

    if args.json:
        print(json.dumps({"since": since, "author": author, "git": repo_rows,
                          "okr": okr_rows, "canvas": canvas_rows}, ensure_ascii=False, indent=2))
        return

    md = render_md(repo_rows, okr_rows, canvas_rows, since, author)
    if args.out:
        p = Path(os.path.expanduser(args.out))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(md + "\n")
        print(f"[OK] wrote {p} ({len(md)} bytes, {len(repo_rows)} git candidates)")
    else:
        print(md)


if __name__ == "__main__":
    main()
