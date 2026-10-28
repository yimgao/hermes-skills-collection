#!/usr/bin/env python3
"""
Self-test for the command-journal skill.

Runs the CLI against a throwaway journal directory and asserts the
behaviours the skill promises. Exits non-zero on failure.

Usage:  python3 selftest.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLI = HERE / "journal.py"

PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name}" + (f"  -- {detail}" if detail else ""))


def run(home: Path, *args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["COMMAND_JOURNAL_HOME"] = str(home)
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True, text=True, env=env,
    )


def first_id(out: str) -> str:
    """Extract the id of the first search result, whichever line it lands on."""
    import re as _re
    m = _re.search(r"id: (cj-\d+)", out)
    return m.group(1) if m else ""


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="cj-selftest-"))
    home = tmp / "journal"

    print("[1] add / list / show")
    r = run(home, "add", "kubectl --namespace prod rollout restart deployment/api-gateway",
            "--title", "restart api gateway in prod", "--note", "scale to zero first",
            "--tags", "k8s,prod,deploy", "--run")
    check("add returns 0", r.returncode == 0, r.stderr)
    check("add prints id", "cj-0001" in r.stdout, r.stdout)

    r = run(home, "add", "aws s3 cp ./build.tar.gz s3://my-bucket/releases/build.tar.gz --storage-class STANDARD_IA",
            "--title", "upload build to s3", "--tags", "aws,s3,deploy")
    check("second add ok", r.returncode == 0, r.stderr)

    r = run(home, "add", "ffmpeg -i input.mov -c:v libx264 -crf 23 -preset slow -c:a aac output.mp4",
            "--title", "compress video for web", "--tags", "video,ffmpeg")
    check("third add ok", r.returncode == 0, r.stderr)

    r = run(home, "list")
    check("list shows 3 recipes", "3 recipe(s)" in r.stdout, r.stdout)
    check("list shows command", "kubectl" in r.stdout, r.stdout)

    r = run(home, "list", "--tag", "k8s")
    check("tag filter works", "cj-0001" in r.stdout and "cj-0002" not in r.stdout, r.stdout)

    r = run(home, "show", "cj-0001")
    check("show returns json", r.returncode == 0 and json.loads(r.stdout)["id"] == "cj-0001", r.stderr)

    print("[2] search relevance")
    r = run(home, "search", "restart", "gateway")
    check("search finds the right recipe first", first_id(r.stdout) == "cj-0001", r.stdout)
    check("search marks RECIPE", "[RECIPE]" in r.stdout, r.stdout)

    r = run(home, "search", "s3", "upload")
    check("search by s3 upload", first_id(r.stdout) == "cj-0002", r.stdout)

    r = run(home, "search", "zzzqqqxyzzy")
    check("no-match search returns 1", r.returncode == 1, f"rc={r.returncode}")
    check("no-match search says no matches", "no matches" in r.stdout, r.stdout)
    check("no-match search does NOT list recipes", "cj-0001" not in r.stdout, r.stdout)

    r = run(home, "search", "kubectl")
    check("search by tool name", "cj-0001" in r.stdout, r.stdout)

    r = run(home, "search", "compress", "--json")
    check("search --json parses", r.returncode == 0 and isinstance(json.loads(r.stdout), list), r.stderr)

    print("[3] history ingestion")
    hist = tmp / "fake_history"
    hist.write_text(
        ": 1699999999:0;kubectl get pods -n prod\n"
        ": 1699999999:5;docker build -t myapp:latest .\n"
        "ls\n"
        "cd ..\n"
        "\n"
        "#1700000000\n"
        "python3 -m venv .venv\n",
        encoding="utf-8",
    )
    r = run(home, "history", "--file", str(hist))
    check("history ok", r.returncode == 0, r.stderr)
    check("history indexed something", "new" in r.stdout and "total indexed" in r.stdout, r.stdout)

    r = run(home, "history", "--file", str(hist))
    check("history is idempotent", "+0 new" in r.stdout, r.stdout)

    r = run(home, "search", "docker", "build")
    check("history hits surface in search", "[HISTORY]" in r.stdout, r.stdout)
    check("history hit shows the command", "docker build" in r.stdout, r.stdout)

    r = run(home, "search", "venv")
    check("bash-style history parsed", "venv" in r.stdout, r.stdout)

    print("[4] stats / export / forget")
    r = run(home, "stats")
    check("stats ok", r.returncode == 0 and "recipes" in r.stdout, r.stderr)
    check("stats shows history count", "history indexed" in r.stdout, r.stdout)

    r = run(home, "export", "--format", "md")
    check("export md ok", r.returncode == 0 and "# Command Journal" in r.stdout, r.stderr)

    r = run(home, "export", "--format", "json")
    check("export json parses", r.returncode == 0 and "recipes" in json.loads(r.stdout), r.stderr)

    out = tmp / "export.md"
    r = run(home, "export", "--out", str(out))
    check("export --out writes file", out.exists() and "kubectl" in out.read_text(encoding="utf-8"), r.stdout)

    r = run(home, "forget", "cj-0003")
    check("forget ok", r.returncode == 0 and "forgot cj-0003" in r.stdout, r.stdout)
    r = run(home, "forget", "cj-9999")
    check("forget missing returns 1", r.returncode == 1, f"rc={r.returncode}")

    print("[5] edge cases")
    r = run(home, "add", "")
    check("empty command rejected", r.returncode == 2, f"rc={r.returncode}")

    r = run(home, "search", "the", "and")
    check("stopword-only query rejected", r.returncode == 2, f"rc={r.returncode}")

    r = run(home, "show", "nope")
    check("show missing returns 1", r.returncode == 1, f"rc={r.returncode}")

    r = run(home, "history", "--file", str(tmp / "does-not-exist"))
    check("missing history file handled", r.returncode == 0 or r.returncode == 1, f"rc={r.returncode}")

    # corrupted journal must not crash the tool
    (home / "journal.json").write_text("{not json", encoding="utf-8")
    r = run(home, "list")
    check("corrupt journal does not crash", r.returncode in (0, 1), f"rc={r.returncode} {r.stderr}")

    print(f"\n{PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
