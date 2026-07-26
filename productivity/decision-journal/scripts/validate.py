#!/usr/bin/env python3
"""Validate Decision Journal Markdown frontmatter using only Python stdlib."""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

REQUIRED = {
    "title",
    "date",
    "status",
    "owner",
    "review_date",
    "reversibility",
    "confidence",
}
STATUSES = {"open", "decided", "reviewed", "superseded"}
REVERSIBILITY = {"one-way", "two-way"}
REQUIRED_SECTIONS = ("## Options", "## Evidence Available at Decision Time", "## Decision", "## Review")


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("file must start with YAML frontmatter delimiter ---")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("closing YAML frontmatter delimiter not found")
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)", line)
        if not match:
            raise ValueError(f"unsupported frontmatter line: {line!r}")
        key, value = match.groups()
        values[key] = value.strip().strip('"').strip("'")
    return values


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
        data = parse_frontmatter(text)
    except (OSError, UnicodeError, ValueError) as exc:
        return [str(exc)]

    missing = sorted(REQUIRED - data.keys())
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if data.get("status") not in STATUSES:
        errors.append("status must be one of: " + ", ".join(sorted(STATUSES)))
    if data.get("reversibility") not in REVERSIBILITY:
        errors.append("reversibility must be one-way or two-way")

    try:
        confidence = int(data.get("confidence", ""))
        if not 0 <= confidence <= 100:
            errors.append("confidence must be between 0 and 100")
    except ValueError:
        errors.append("confidence must be an integer")

    parsed_dates: dict[str, date] = {}
    for key in ("date", "review_date"):
        try:
            parsed_dates[key] = date.fromisoformat(data.get(key, ""))
        except ValueError:
            errors.append(f"{key} must use YYYY-MM-DD")
    if set(parsed_dates) == {"date", "review_date"} and parsed_dates["review_date"] < parsed_dates["date"]:
        errors.append("review_date cannot be before date")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"missing section: {section}")
    return errors


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: validate.py FILE.md [FILE.md ...]", file=sys.stderr)
        return 2
    failed = False
    for raw in argv:
        path = Path(raw).expanduser()
        errors = validate(path)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK   {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
