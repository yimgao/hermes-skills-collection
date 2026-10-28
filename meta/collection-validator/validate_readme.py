#!/usr/bin/env python3
"""Validate README.md: pipe-table integrity + skill count consistency."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"

errors = []
lines = README.read_text(encoding="utf-8").splitlines()

# --- 1. find all table blocks and check column counts
i = 0
tables = 0
while i < len(lines):
    if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1]):
        tables += 1
        header = lines[i]
        ncols = header.count("|") - 1
        sep = lines[i + 1]
        if sep.count("|") - 1 != ncols:
            errors.append(f"line {i+2}: separator has {sep.count('|')-1} cols, header has {ncols}")
        j = i + 2
        while j < len(lines) and lines[j].startswith("|"):
            c = lines[j].count("|") - 1
            if c != ncols:
                errors.append(f"line {j+1}: row has {c} cols, header has {ncols}: {lines[j][:80]}")
            j += 1
        i = j
    else:
        i += 1

print(f"tables checked: {tables}")

# --- 2. skill count in header
m = re.search(r"\*\*(\d+) skills · (\d+) categories\*\*", "\n".join(lines))
if not m:
    errors.append("header count line not found")
    claimed, claimed_cats = 0, 0
else:
    claimed, claimed_cats = int(m.group(1)), int(m.group(2))

# --- 3. count skill dirs on disk
skill_files = [p for p in ROOT.rglob("SKILL.md") if ".git" not in p.parts]
cats = {p.parent.parent for p in skill_files}
print(f"on disk: {len(skill_files)} skills in {len(cats)} categories")
print(f"claimed: {claimed} skills in {claimed_cats} categories")

if len(skill_files) != claimed:
    errors.append(f"skill count mismatch: disk={len(skill_files)} claimed={claimed}")
if len(cats) != claimed_cats:
    errors.append(f"category count mismatch: disk={len(cats)} claimed={claimed_cats}")

# --- 4. every install link points at an existing file
links = re.findall(r"https://raw\.githubusercontent\.com/yimgao/hermes-skills-collection/main/([^\s)]+)", "\n".join(lines))
for link in links:
    p = ROOT / link
    if not p.is_file():
        errors.append(f"install link points to missing file: {link}")
print(f"install links checked: {len(links)}")

# --- 5. every on-disk skill appears in the README
readme_text = "\n".join(lines)
missing = []
for p in skill_files:
    rel = p.parent.relative_to(ROOT)
    if str(rel) not in readme_text:
        missing.append(str(rel))
if missing:
    for m in missing:
        errors.append(f"skill on disk but missing from README: {m}")

# --- 6. category tree in Structure block matches disk
tree_block = "\n".join(lines)
for c in sorted(cats):
    if f"{c.name}/" not in tree_block:
        errors.append(f"category not in Structure tree: {c.name}")

if errors:
    print("\nERRORS:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("\nREADME OK")
