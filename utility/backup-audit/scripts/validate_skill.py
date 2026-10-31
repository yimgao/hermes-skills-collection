#!/usr/bin/env python3
"""Validate this skill's SKILL.md structure and frontmatter."""
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "SKILL.md"
t = SKILL.read_text()

m = re.match(r"^---\n(.*?)\n---\n", t, re.S)
if not m:
    print("FAIL: no YAML frontmatter")
    sys.exit(1)
fm = m.group(1)

required = ["name:", "description:", "version:", "author:", "license:",
            "tags:", "related_skills:"]
missing = [k for k in required if k not in fm]
if missing:
    print("FAIL: missing frontmatter keys:", missing)
    sys.exit(1)
print("OK  frontmatter has all required keys")

# name must match directory
nm = re.search(r"^name:\s*(\S+)", fm, re.M)
assert nm, "FAIL: could not parse name"
name = nm.group(1)
d = SKILL.parent.name
if name != d:
    print(f"FAIL: name '{name}' != directory '{d}'")
    sys.exit(1)
print(f"OK  name matches directory ({name})")

sections = ["## Overview", "## When to Use", "## Core Workflow",
            "## Example Invocations", "## Common Pitfalls",
            "## Verification Checklist", "## Data Sources"]
bad = [s for s in sections if s not in t]
if bad:
    print("FAIL: missing sections:", bad)
    sys.exit(1)
for s in sections:
    print(f"OK  section {s}")

# tag / related_skill sanity
tags = re.search(r"tags:\s*\[(.*?)\]", fm, re.S)
assert tags, "FAIL: could not parse tags"
if len(tags.group(1).split(",")) < 5:
    print("FAIL: too few tags")
    sys.exit(1)
print(f"OK  {len(tags.group(1).split(','))} tags")

rel = re.search(r"related_skills:\s*\[(.*?)\]", fm, re.S)
assert rel, "FAIL: could not parse related_skills"
if len(rel.group(1).split(",")) < 3:
    print("FAIL: too few related_skills")
    sys.exit(1)
print(f"OK  {len(rel.group(1).split(','))} related_skills")

# no unresolved placeholders
for bad_tok in ("TODO", "FIXME", "XXX", "<placeholder>"):
    if bad_tok in t:
        print(f"FAIL: placeholder {bad_tok} present")
        sys.exit(1)
print("OK  no placeholders")

print(f"\nPASS — {SKILL} ({len(t):,} bytes)")
