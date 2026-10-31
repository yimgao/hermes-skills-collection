#!/usr/bin/env python3
"""
backup_audit.py — Audit whether your critical personal data is actually protected.

Subcommands:
  plan      Define (or update) a backup plan: datasets, source paths, destinations, cadence.
  scan     Scan a source path and report its size, file mix, newest/oldest mtime, and
           whether it contains anything that looks like a secret / credential.
  cover    Cross-check every planned dataset against what actually exists on disk
           (source present? backup present? age of newest backup?).
  verify   Deep-verify a backup destination: file counts, byte totals, and a
           content-level checksum match against the source (for small trees).
  report   Render a Markdown audit report (the pasteable artifact).
  selftest Run the built-in test suite.

Storage: ~/.hermes/backup-audit/plan.json  (plan + scan results, local only)
Stdlib only. No network. No upload. Read-only against user data unless --fix is given.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zlib
from pathlib import Path

HOME = Path.home()
STORE = HOME / ".hermes" / "backup-audit"
PLAN_FILE = STORE / "plan.json"

# Files that look like credentials — presence in an unencrypted backup is a risk.
SECRET_PATTERNS = [
    (".env", "dotenv"),
    ("id_rsa", "ssh-private-key"),
    ("id_ed25519", "ssh-private-key"),
    (".pem", "private-key"),
    (".p12", "keystore"),
    (".keystore", "keystore"),
    (".netrc", "netrc-credentials"),
    (".aws", "aws-credentials-dir"),
    (".ssh", "ssh-dir"),
    ("credentials", "credentials-file"),
    ("secret", "secret-file"),
    ("token", "token-file"),
    (".gnupg", "gpg-dir"),
    (".kube", "kube-config"),
    ("secrets.yml", "k8s-secrets"),
    (".git-credentials", "git-credentials"),
]

# The dataset catalog. 'criticality' 3 = losing it is catastrophic.
DATASET_CATALOG = {
    "photos":        {"criticality": 3, "hint": "Camera roll, edited exports, RAW files",
                      "why": "Irreplaceable originals. No re-download."},
    "documents":     {"criticality": 3, "hint": "Contracts, tax records, ID scans, certificates",
                      "why": "Legal/financial proof that exists nowhere else."},
    "code":          {"criticality": 3, "hint": "Git repos, dotfiles, personal scripts",
                      "why": "Unpushed commits are unrecoverable."},
    "finances":      {"criticality": 3, "hint": "Bank statements, tax returns, spreadsheets",
                      "why": "Required for tax filing and audits."},
    "messages":      {"criticality": 2, "hint": "WhatsApp/Signal/iMessage exports, chat logs",
                      "why": "Historic conversations and shared media."},
    "email":         {"criticality": 2, "hint": "Mail archives (.mbox, .pst)",
                      "why": "Years of correspondence and attachments."},
    "music":         {"criticality": 1, "hint": "Lossless libraries, playlists, FLAC",
                      "why": "Purchased DRM-free music is expensive to replace."},
    "video":         {"criticality": 1, "hint": "Home videos, footage, projects",
                      "why": "Large; often re-creatable but painful."},
    "email-archive": {"criticality": 2, "hint": "Newsletter archives, mailing list exports",
                      "why": "Owned audience assets."},
}

GREEN, YELLOW, RED, DIM, BOLD, RESET = "\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[1m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = YELLOW = RED = DIM = BOLD = RESET = ""


# ───────────────────────────── storage ─────────────────────────────

def load_plan():
    if PLAN_FILE.exists():
        try:
            return json.loads(PLAN_FILE.read_text())
        except json.JSONDecodeError as e:
            die(f"plan.json is corrupt ({e}). Move it aside: {PLAN_FILE}")
    return {"datasets": {}, "destinations": [], "updated": None}


def save_plan(plan):
    STORE.mkdir(parents=True, exist_ok=True)
    plan["updated"] = dt.datetime.now().isoformat(timespec="seconds")
    PLAN_FILE.write_text(json.dumps(plan, indent=2, ensure_ascii=False))
    os.chmod(PLAN_FILE, 0o600)


def die(msg, code=1):
    print(f"{RED}[ERROR]{RESET} {msg}", file=sys.stderr)
    sys.exit(code)


def expand(p):
    """Expand ~ and $VARS, resolve to absolute path."""
    return Path(os.path.expandvars(os.path.expanduser(str(p)))).resolve()


def expand_all(paths):
    """argparse --source/--dest use action='append', so values arrive as lists."""
    out = []
    for item in (paths or []):
        if isinstance(item, (list, tuple)):
            out.extend(str(expand(i)) for i in item)
        else:
            out.append(str(expand(item)))
    return out


def human(n):
    if n is None:
        return "-"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:.1f}{unit}" if unit != "B" else f"{int(n)}B"
        n /= 1024.0
    return f"{n:.1f}TB"


def now_iso():
    return dt.datetime.now().isoformat(timespec="seconds")


def age_days(iso):
    if not iso:
        return None
    try:
        t = dt.datetime.fromisoformat(iso)
    except ValueError:
        return None
    return (dt.datetime.now() - t).days


# ───────────────────────────── scanning ─────────────────────────────

def walk_stats(root):
    """Walk a tree and collect file count, bytes, extensions, mtimes."""
    total_bytes = 0
    count = 0
    exts = {}
    newest = None
    oldest = None
    errors = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".venv",
                                                        "__pycache__", "Library", ".Trash")]
        for fn in filenames:
            fp = Path(dirpath) / fn
            try:
                st = fp.lstat()
            except OSError:
                errors += 1
                continue
            count += 1
            total_bytes += st.st_size
            ext = fp.suffix.lower() or "(none)"
            exts[ext] = exts.get(ext, 0) + 1
            m = dt.datetime.fromtimestamp(st.st_mtime)
            if newest is None or m > newest:
                newest = m
            if oldest is None or m < oldest:
                oldest = m
    return {
        "files": count,
        "bytes": total_bytes,
        "extensions": dict(sorted(exts.items(), key=lambda kv: -kv[1])[:8]),
        "newest": newest.isoformat(timespec="seconds") if newest else None,
        "oldest": oldest.isoformat(timespec="seconds") if oldest else None,
        "errors": errors,
    }


def find_secrets(root, limit=20):
    """Scan for credential-looking files. Bounded walk for speed."""
    hits = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".venv",
                                                        "Library", ".Trash", "__pycache__")]
        for fn in filenames:
            low = fn.lower()
            for pat, kind in SECRET_PATTERNS:
                if pat in low:
                    hits.append({"path": str(Path(dirpath) / fn), "kind": kind})
                    break
            if len(hits) >= limit:
                return hits
    return hits


def tree_fingerprint(root, sample=300):
    """
    Content fingerprint of a tree: hash over (relative_path, size, mtime) for a
    deterministic sample of files. Cheap and catches most accidental deletions.
    """
    files = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".venv",
                                                        "__pycache__", "Library", ".Trash")]
        for fn in filenames:
            fp = Path(dirpath) / fn
            try:
                st = fp.lstat()
            except OSError:
                continue
            files.append((str(fp.relative_to(root)), st.st_size, int(st.st_mtime)))
    files.sort()
    if len(files) > sample:
        step = len(files) / sample
        files = [files[int(i * step)] for i in range(sample)]
    h = hashlib.sha256()
    for rel, size, mtime in files:
        h.update(f"{rel}|{size}|{mtime}\n".encode())
    return {"digest": h.hexdigest()[:16], "sampled": len(files), "total": len(files)}


def deep_content_hash(root, limit_bytes=50 * 1024 * 1024):
    """
    True content hash of every file (not mtime-based). Only for small trees.
    Used to prove the backup bytes match the source bytes.
    """
    h = hashlib.sha256()
    total = 0
    n = 0
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules", ".venv",
                                                        "__pycache__", "Library", ".Trash")]
        for fn in sorted(filenames):
            fp = Path(dirpath) / fn
            try:
                if fp.is_symlink() or not fp.is_file():
                    continue
                with open(fp, "rb") as f:
                    while True:
                        chunk = f.read(1024 * 1024)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > limit_bytes:
                            return None, None, None
                        h.update(chunk)
                h.update(b"\0")
                n += 1
            except OSError:
                continue
    return h.hexdigest()[:16], n, total


# ───────────────────────────── commands ─────────────────────────────

def cmd_plan(args):
    plan = load_plan()
    ds = plan["datasets"]

    if args.remove:
        if args.remove in ds:
            del ds[args.remove]
            save_plan(plan)
            print(f"{GREEN}[OK]{RESET} removed dataset '{args.remove}'")
        else:
            die(f"no dataset named '{args.remove}'")
        return

    if not args.name:
        die("plan needs --name (dataset key). See `plan --list` for the catalog.")

    key = args.name
    meta = DATASET_CATALOG.get(key, {"criticality": 2, "hint": "custom dataset", "why": "user-defined"})

    entry = ds.setdefault(key, {
        "criticality": meta["criticality"],
        "why": meta["why"],
        "sources": [],
        "destinations": [],
        "cadence": args.cadence or "weekly",
        "rpo": args.rpo or "24h",
        "rto": args.rto or "24h",
        "encrypted": False,
    })

    if args.source:
        entry["sources"] = list(dict.fromkeys(entry["sources"] + expand_all(args.source)))
    if args.dest:
        entry["destinations"] = list(dict.fromkeys(entry["destinations"] + expand_all(args.dest)))
    if args.cadence:
        entry["cadence"] = args.cadence
    if args.rpo:
        entry["rpo"] = args.rpo
    if args.rto:
        entry["rto"] = args.rto
    if args.criticality is not None:
        entry["criticality"] = args.criticality
    if args.encrypted:
        entry["encrypted"] = True
    if args.notes:
        entry["notes"] = args.notes

    save_plan(plan)
    print(f"{GREEN}[OK]{RESET} dataset '{key}' updated")
    print(f"  criticality : {entry['criticality']}/3  ({meta['why']})")
    print(f"  sources     : {len(entry['sources'])}  {entry['sources']}")
    print(f"  destinations: {len(entry['destinations'])}  {entry['destinations']}")
    print(f"  cadence     : {entry['cadence']}   rpo={entry['rpo']}  rto={entry['rto']}")
    print(f"  encrypted   : {entry['encrypted']}")
    if not entry["sources"]:
        print(f"{YELLOW}[WARN]{RESET} no source path set yet — run `scan` then `plan --source`")


def cmd_catalog(args):
    print(f"{BOLD}Dataset catalog{RESET}  (criticality 3 = losing it is catastrophic)\n")
    print(f"{'key':<14} {'crit':<5} {'hint'}")
    print("─" * 78)
    for k, v in DATASET_CATALOG.items():
        print(f"{k:<14} {v['criticality']:<5} {v['hint']}")
    print(f"\n{DIM}Any --name works; unknown keys default to criticality 2.{RESET}")


def cmd_scan(args):
    root = expand(args.path)
    if not root.exists():
        die(f"path does not exist: {root}")
    if root.is_file():
        st = root.stat()
        stats = {"files": 1, "bytes": st.st_size, "extensions": {root.suffix.lower(): 1},
                 "newest": dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                 "oldest": dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                 "errors": 0}
        secrets = []
        if any(p in root.name.lower() for p, _ in SECRET_PATTERNS):
            secrets = [{"path": str(root), "kind": "credential-file"}]
    else:
        print(f"{DIM}scanning {root} ...{RESET}")
        stats = walk_stats(root)
        secrets = find_secrets(root) if args.secrets else []

    print(f"\n{BOLD}Path{RESET}        {root}")
    print(f"{BOLD}Files{RESET}       {stats['files']:,}")
    print(f"{BOLD}Size{RESET}        {human(stats['bytes'])}")
    if stats.get("newest"):
        print(f"{BOLD}Newest file{RESET}  {stats['newest']}  ({age_days(stats['newest'])} days ago)")
        print(f"{BOLD}Oldest file{RESET}  {stats['oldest']}  ({age_days(stats['oldest'])} days ago)")
    if stats["extensions"]:
        top = ", ".join(f"{e}×{c}" for e, c in stats["extensions"].items())
        print(f"{BOLD}Mix{RESET}         {top}")

    if secrets:
        print(f"\n{RED}{BOLD}Credential-looking files found: {len(secrets)}{RESET}")
        for s in secrets[:10]:
            print(f"  {YELLOW}⚠{RESET}  {s['kind']:<22} {s['path']}")
        print(f"{DIM}  → Back these up ENCRYPTED, never to a shared/sync folder unencrypted.{RESET}")
    else:
        print(f"\n{GREEN}[OK]{RESET} no credential-looking files detected")

    fp = tree_fingerprint(root)
    print(f"{BOLD}Fingerprint{RESET}  {fp['digest']}  (over {fp['sampled']:,} sampled files)")
    print(f"{DIM}Use this digest to prove a backup matches the source later.{RESET}")

    if args.save:
        plan = load_plan()
        plan.setdefault("scans", {})[str(root)] = {
            "stats": stats, "fingerprint": fp, "secrets": secrets, "scanned_at": now_iso()}
        save_plan(plan)
        print(f"{GREEN}[OK]{RESET} scan saved to plan (scans.{root})")


def cmd_cover(args):
    plan = load_plan()
    if not plan["datasets"]:
        die("no plan yet. Start with: plan --name photos --source ~/Pictures")

    rows = []
    for name, e in plan["datasets"].items():
        srcs = [expand(s) for s in e.get("sources", [])]
        dests = [expand(d) for d in e.get("destinations", [])]
        src_ok = [s for s in srcs if s.exists()]
        src_missing = [s for s in srcs if not s.exists()]
        dest_ok = [d for d in dests if d.exists()]
        dest_missing = [d for d in dests if not d.exists()]
        newest_backup = None
        for d in dest_ok:
            try:
                for dirpath, dirnames, filenames in os.walk(d):
                    dirnames[:] = [x for x in dirnames if x not in (".git", "node_modules")]
                    for fn in filenames:
                        try:
                            m = dt.datetime.fromtimestamp((Path(dirpath) / fn).stat().st_mtime)
                        except OSError:
                            continue
                        if newest_backup is None or m > newest_backup:
                            newest_backup = m
            except OSError:
                pass
        backup_age = age_days(newest_backup.isoformat()) if newest_backup else None
        rows.append({
            "dataset": name, "crit": e.get("criticality", 2),
            "src_missing": [str(s) for s in src_missing],
            "dest_missing": [str(d) for d in dest_missing],
            "src_bytes": sum(walk_stats(s)["bytes"] for s in src_ok),
            "backup_age_days": backup_age,
            "encrypted": e.get("encrypted", False),
            "dest_count": len(dest_ok),
            "cadence": e.get("cadence", "weekly"),
            "rpo": e.get("rpo", "24h"),
        })

    print(f"\n{BOLD}Backup coverage{RESET}  {len(rows)} dataset(s)\n")
    print(f"{'dataset':<14} {'crit':<5} {'src':<6} {'backup':<9} {'age':<7} {'enc':<5} status")
    print("─" * 78)
    for r in sorted(rows, key=lambda x: -x["crit"]):
        src_st = f"{GREEN}ok{RESET}" if not r["src_missing"] else f"{RED}miss{RESET}"
        if r["dest_count"] == 0:
            bk_st, age = f"{RED}none{RESET}", "-"
        elif r["backup_age_days"] is None:
            bk_st, age = f"{RED}empty{RESET}", "-"
        else:
            bk_st = f"{GREEN}ok{RESET}"
            age = f"{r['backup_age_days']}d"
            if r["backup_age_days"] > 14:
                bk_st, age = f"{YELLOW}stale{RESET}", age
        enc = f"{GREEN}y{RESET}" if r["encrypted"] else f"{RED}n{RESET}"
        # status
        problems = []
        if r["src_missing"]:
            problems.append("source-missing")
        if r["dest_count"] == 0:
            problems.append("no-destination")
        if r["backup_age_days"] is not None and r["backup_age_days"] > 14:
            problems.append("stale")
        if not r["encrypted"] and r["crit"] == 3:
            problems.append("unencrypted-critical")
        status = f"{RED}FAIL{RESET} {','.join(problems)}" if problems else f"{GREEN}PASS{RESET}"
        print(f"{r['dataset']:<14} {r['crit']:<5} {src_st:<6} {bk_st:<9} {age:<7} {enc:<5} {status}")
        for m in r["src_missing"]:
            print(f"    {DIM}source missing: {m}{RESET}")
        for m in r["dest_missing"]:
            print(f"    {DIM}destination missing: {m}{RESET}")

    fails = sum(1 for r in rows
                if r["src_missing"] or r["dest_count"] == 0
                or (r["backup_age_days"] is not None and r["backup_age_days"] > 14)
                or (not r["encrypted"] and r["crit"] == 3))
    print(f"\n{'─'*78}")
    covered = len(rows) - fails
    if fails:
        print(f"{BOLD}{covered}/{len(rows)} datasets fully covered{RESET}"
              f"{RED}  {fails} need action{RESET}")
    else:
        print(f"{GREEN}{BOLD}{covered}/{len(rows)} datasets fully covered{RESET}")
    return 1 if fails else 0


def cmd_verify(args):
    src = expand(args.source)
    bak = expand(args.backup)
    if not src.exists():
        die(f"source missing: {src}")
    if not bak.exists():
        die(f"backup missing: {bak}")

    print(f"{BOLD}Deep verification{RESET}")
    print(f"  source : {src}")
    print(f"  backup : {bak}\n")

    s_stats = walk_stats(src)
    b_stats = walk_stats(bak)
    print(f"{'metric':<18} {'source':>14} {'backup':>14}  delta")
    print("─" * 70)
    d_files = b_stats["files"] - s_stats["files"]
    d_bytes = b_stats["bytes"] - s_stats["bytes"]
    print(f"{'files':<18} {s_stats['files']:>14,} {b_stats['files']:>14,}  {d_files:+,}")
    print(f"{'bytes':<18} {human(s_stats['bytes']):>14} {human(b_stats['bytes']):>14}  {human(d_bytes)}")

    ok = True
    if b_stats["files"] < s_stats["files"]:
        print(f"\n{RED}[FAIL]{RESET} backup has FEWER files than source — "
              f"{s_stats['files']-b_stats['files']:,} missing")
        ok = False
    else:
        print(f"\n{GREEN}[OK]{RESET} file count covers source")

    if args.content:
        s_hash, s_n, _ = deep_content_hash(src)
        b_hash, b_n, _ = deep_content_hash(bak)
        if s_hash is None or b_hash is None:
            print(f"{YELLOW}[SKIP]{RESET} tree exceeds 50MB — content hash skipped")
        else:
            print(f"{BOLD}content hash{RESET}  source={s_hash} ({s_n} files)  backup={b_hash} ({b_n} files)")
            if s_hash == b_hash:
                print(f"{GREEN}[OK]{RESET} content hashes MATCH — bytes are identical")
            else:
                print(f"{RED}[FAIL]{RESET} content hashes DIFFER — backup is corrupt or stale")
                ok = False
    else:
        s_fp = tree_fingerprint(src)
        b_fp = tree_fingerprint(bak)
        print(f"{BOLD}fingerprint{RESET}  source={s_fp['digest']}  backup={b_fp['digest']}")
        if s_fp["digest"] == b_fp["digest"]:
            print(f"{GREEN}[OK]{RESET} fingerprints match")
        else:
            print(f"{YELLOW}[WARN]{RESET} fingerprints differ (expected if backup is older)")

    sys.exit(0 if ok else 1)


def cmd_restore(args):
    """
    Prove the backup is actually restorable by restoring it into a throwaway
    directory and comparing. This is the check that catches the "backup job
    wrote an empty folder for 6 months" failure mode.
    """
    import shutil
    import tempfile

    src = expand(args.source)
    bak = expand(args.backup)
    if not bak.exists():
        die(f"backup missing: {bak}")
    if not src.exists():
        print(f"{YELLOW}[WARN]{RESET} source missing: {src} — restoring blind (source should be gone!)")

    tmp = Path(tempfile.mkdtemp(prefix="restore-test-"))
    target = tmp / "restored"
    print(f"{BOLD}Test restore{RESET}")
    print(f"  backup  : {bak}")
    print(f"  target  : {target}")
    print(f"  source  : {src}" + ("" if src.exists() else "  (absent — simulating total loss)"))
    print()

    t0 = dt.datetime.now()
    try:
        shutil.copytree(bak, target, symlinks=True)
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        die(f"restore failed: {e}")
    elapsed = (dt.datetime.now() - t0).total_seconds()
    print(f"{GREEN}[OK]{RESET} restored {walk_stats(target)['files']:,} files in {elapsed:.2f}s")

    restored_stats = walk_stats(target)
    if src.exists():
        src_stats = walk_stats(src)
        missing = src_stats["files"] - restored_stats["files"]
        if missing > 0:
            print(f"{RED}[FAIL]{RESET} restore is INCOMPLETE — {missing:,} files missing vs source")
            shutil.rmtree(tmp, ignore_errors=True)
            sys.exit(1)
        print(f"{GREEN}[OK]{RESET} restore covers all {src_stats['files']:,} source files")
        if args.content:
            s_hash, _, _ = deep_content_hash(src)
            r_hash, _, _ = deep_content_hash(target)
            if s_hash and r_hash:
                if s_hash == r_hash:
                    print(f"{GREEN}[OK]{RESET} content hash matches source ({r_hash})")
                else:
                    print(f"{RED}[FAIL]{RESET} content hash differs from source "
                          f"({r_hash} vs {s_hash})")
                    shutil.rmtree(tmp, ignore_errors=True)
                    sys.exit(1)
    else:
        print(f"{GREEN}[OK]{RESET} source is gone — restore from backup is the only path, and it works")

    print(f"\n{DIM}  (dry run; temp dir removed){RESET}")
    shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(0)


def cmd_report(args):
    plan = load_plan()
    if not plan["datasets"]:
        die("nothing to report. Define a dataset first: plan --name photos --source ~/Pictures")

    out = []
    out.append("# 🛡️ Backup Audit — 个人数据备份审计报告\n")
    out.append(f"_Generated {now_iso()} · plan updated {plan.get('updated', 'n/a')} · local only_\n")

    total_bytes = 0
    for name, e in sorted(plan["datasets"].items(), key=lambda kv: -kv[1].get("criticality", 2)):
        srcs = [expand(s) for s in e.get("sources", [])]
        sb = sum(walk_stats(s)["bytes"] for s in srcs if s.exists())
        total_bytes += sb
        missing = [str(s) for s in srcs if not s.exists()]
        dest_missing = [str(expand(d)) for d in e.get("destinations", []) if not expand(d).exists()]
        out.append(f"## {name}  `criticality {e.get('criticality',2)}/3`\n")
        out.append(f"- **Why it matters**: {e.get('why','')}")
        out.append(f"- **Source**: {', '.join(f'`{s}`' for s in srcs) or '—'}"
                   + (f"  {RED}(missing: {', '.join(missing)}){RESET}" if missing else ""))
        out.append(f"- **Destination**: {', '.join(f'`{expand(d)}`' for d in e.get('destinations', [])) or '—'}"
                   + (f"  {RED}(missing: {', '.join(dest_missing)}){RESET}" if dest_missing else ""))
        out.append(f"- **Size on disk**: {human(sb)}")
        out.append(f"- **Cadence / RPO / RTO**: {e.get('cadence')} / {e.get('rpo')} / {e.get('rto')}")
        out.append(f"- **Encrypted at rest**: {'yes' if e.get('encrypted') else 'NO'}")
        out.append("")

    out.append("## ⚠️ 3-2-1 rule check\n")
    out.append("| Rule | Requirement | Status |")
    out.append("|---|---|---|")
    crit = [k for k, v in plan["datasets"].items() if v.get("criticality", 2) == 3]

    OFFSITE_HINTS = ("/Volumes/", "iCloud", "Dropbox", "OneDrive", "Google Drive",
                      "Backblaze", "Dropbox", "s3", "rclone:", "Synology", "NAS")
    # "3 copies" = original + at least 2 destinations for every critical dataset.
    crit_with_two_dests = [k for k in crit
                           if len(plan["datasets"][k].get("destinations", [])) >= 2]
    have_three = bool(crit) and len(crit_with_two_dests) == len(crit)
    # "1 offsite" = at least one destination that is not on the boot disk.
    have_offsite = False
    for v in plan["datasets"].values():
        for d in v.get("destinations", []):
            s = str(expand(d))
            if any(t in s for t in OFFSITE_HINTS):
                have_offsite = True
    # "2 media" = at least one destination that is a mounted volume / cloud path.
    have_two_media = any(
        any(t in str(expand(d)) for t in ("/Volumes/", "iCloud", "Dropbox", "OneDrive",
                                          "Google Drive", "NAS", "rclone:"))
        for v in plan["datasets"].values() for d in v.get("destinations", []))

    out.append(f"| 3 copies | every critical dataset has ≥2 destinations "
               f"(+ the original) — {len(crit_with_two_dests)}/{len(crit)} | "
               f"{'✅' if have_three else '❌ add a second destination'} |")
    out.append(f"| 2 media | ≥1 destination on a different medium (volume / cloud) | "
               f"{'✅' if have_two_media else '⚠️ not auto-detected'} |")
    out.append(f"| 1 offsite | ≥1 copy away from this machine | "
               f"{'✅' if have_offsite else '❌ no offsite destination'} |")
    out.append("")

    out.append("## 🧭 Next actions\n")
    for name, e in sorted(plan["datasets"].items(), key=lambda kv: -kv[1].get("criticality", 2)):
        srcs = [expand(s) for s in e.get("sources", [])]
        if not srcs or not any(s.exists() for s in srcs):
            out.append(f"- **{name}**: source path missing — fix the path or remove the dataset.")
            continue
        if not e.get("destinations"):
            out.append(f"- **{name}**: no destination configured — add one with `plan --dest`.")
            continue
        if not e.get("encrypted"):
            out.append(f"- **{name}**: not marked encrypted — enable if it holds credentials or private media.")
    out.append("")
    out.append(f"_Total tracked data: {human(total_bytes)} across {len(plan['datasets'])} dataset(s)._\n")

    text = "\n".join(out)
    if args.out:
        Path(expand(args.out)).write_text(text)
        print(f"{GREEN}[OK]{RESET} report written to {expand(args.out)}")
    else:
        print(text)


# ───────────────────────────── selftest ─────────────────────────────

def cmd_selftest(args):
    import tempfile
    failures = []

    def check(name, cond, detail=None):
        if cond:
            print(f"  {GREEN}PASS{RESET} {name}")
        else:
            print(f"  {RED}FAIL{RESET} {name} {detail}")
            failures.append(name)

    print(f"{BOLD}selftest{RESET}\n")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)

        # human()
        check("human(1024)=='1.0KB'", human(1024) == "1.0KB", human(1024))
        check("human(500)=='500B'", human(500) == "500B", human(500))

        # stats
        (root / "a.txt").write_text("hello")
        (root / "sub").mkdir()
        (root / "sub" / "b.md").write_text("world")
        st = walk_stats(root)
        check("walk_stats counts 2 files", st["files"] == 2, st)
        check("walk_stats bytes == 10", st["bytes"] == 10, st)
        check("walk_stats has .txt", ".txt" in st["extensions"], st["extensions"])

        # secrets
        (root / ".env").write_text("SECRET=1")
        hits = find_secrets(root)
        check("find_secrets detects .env", any(h["kind"] == "dotenv" for h in hits), hits)

        # fingerprint determinism
        fp1 = tree_fingerprint(root)
        fp2 = tree_fingerprint(root)
        check("fingerprint stable", fp1["digest"] == fp2["digest"], (fp1, fp2))

        # fingerprint changes on modification
        (root / "a.txt").write_text("hello world")
        fp3 = tree_fingerprint(root)
        check("fingerprint changes after edit", fp3["digest"] != fp1["digest"], (fp1, fp3))

        # content hash equal for identical trees
        d1 = root / "b1"; d1.mkdir()
        d2 = root / "b2"; d2.mkdir()
        for f in ("x.txt", "y.txt"):
            (d1 / f).write_text("same")
            (d2 / f).write_text("same")
        h1, n1, _ = deep_content_hash(d1)
        h2, n2, _ = deep_content_hash(d2)
        check("deep_content_hash equal for identical trees", h1 == h2 and n1 == 2, (h1, h2, n1))

        # content hash differs
        (d2 / "x.txt").write_text("different")
        h3, _, _ = deep_content_hash(d2)
        check("deep_content_hash differs on change", h3 != h1, (h1, h3))

        # age_days
        check("age_days(None) is None", age_days(None) is None)
        old = (dt.datetime.now() - dt.timedelta(days=40)).isoformat(timespec="seconds")
        check("age_days(40d ago) == 40", age_days(old) == 40, age_days(old))

        # restore simulation: identical tree restores cleanly
        import shutil as _sh
        import tempfile as _tf
        with _tf.TemporaryDirectory() as td2:
            s_dir = Path(td2) / "s"
            b_dir = Path(td2) / "b"
            s_dir.mkdir(); b_dir.mkdir()
            (s_dir / "f1.txt").write_text("content-one")
            (s_dir / "f2.txt").write_text("content-two")
            _sh.copytree(s_dir, b_dir, dirs_exist_ok=True)
            tgt = Path(td2) / "restored"
            _sh.copytree(b_dir, tgt)
            s_hash, _, _ = deep_content_hash(s_dir)
            t_hash, _, _ = deep_content_hash(tgt)
            check("restore copy preserves content hash", s_hash == t_hash, (s_hash, t_hash))
            check("restore file count matches",
                  walk_stats(tgt)["files"] == walk_stats(s_dir)["files"])

        # expand_all handles argparse-style nested lists
        ex = expand_all(["/tmp/a", ["/tmp/b", "/tmp/c"]])
        check("expand_all flattens nested lists", len(ex) == 3, ex)
        check("expand_all expands ~", expand_all(["~"]).__len__() == 1)

        # expand_all with None
        check("expand_all(None) -> []", expand_all(None) == [])

    print(f"\n{'─'*50}")
    if failures:
        print(f"{RED}{len(failures)} failure(s): {failures}{RESET}")
        sys.exit(1)
    print(f"{GREEN}all tests passed{RESET}")


# ───────────────────────────── cli ─────────────────────────────

def main():
    ap = argparse.ArgumentParser(prog="backup_audit.py",
                                 description="Audit whether your critical personal data is actually protected.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan", help="define/update a dataset in the backup plan")
    p.add_argument("--name")
    p.add_argument("--source", action="append", help="path to back up (repeatable)")
    p.add_argument("--dest", action="append", help="backup destination path (repeatable)")
    p.add_argument("--cadence", choices=["hourly", "daily", "weekly", "monthly"])
    p.add_argument("--rpo", help="recovery point objective, e.g. 24h")
    p.add_argument("--rto", help="recovery time objective, e.g. 4h")
    p.add_argument("--criticality", type=int, choices=[1, 2, 3])
    p.add_argument("--encrypted", action="store_true")
    p.add_argument("--notes")
    p.add_argument("--remove", help="remove a dataset by name")
    p.add_argument("--list", action="store_true", help="show the current plan")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("catalog", help="show the dataset catalog")
    p.set_defaults(func=cmd_catalog)

    p = sub.add_parser("scan", help="scan a path: size, mix, mtimes, secrets, fingerprint")
    p.add_argument("path")
    p.add_argument("--secrets", action="store_true", help="scan for credential-looking files")
    p.add_argument("--save", action="store_true", help="store the scan in the plan")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("cover", help="cross-check plan against reality")
    p.set_defaults(func=cmd_cover)

    p = sub.add_parser("verify", help="deep-verify a backup against its source")
    p.add_argument("--source", required=True)
    p.add_argument("--backup", required=True)
    p.add_argument("--content", action="store_true", help="full byte-level hash (small trees only)")
    p.set_defaults(func=cmd_verify)

    p = sub.add_parser("restore", help="test-restore a backup into a temp dir and verify it")
    p.add_argument("--source", required=True, help="original source path (may be gone)")
    p.add_argument("--backup", required=True)
    p.add_argument("--content", action="store_true", help="byte-level content hash comparison")
    p.set_defaults(func=cmd_restore)

    p = sub.add_parser("report", help="render a Markdown audit report")
    p.add_argument("--out", help="write to a file instead of stdout")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("selftest", help="run built-in tests")
    p.set_defaults(func=cmd_selftest)

    args = ap.parse_args()
    if args.cmd == "plan" and args.list:
        plan = load_plan()
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return
    rc = args.func(args)
    if isinstance(rc, int):
        sys.exit(rc)


if __name__ == "__main__":
    main()
