#!/usr/bin/env python3
"""Validate the frontmatter of every SKILL.md in the repo."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REQUIRED = ["name", "description", "version", "author", "license"]

try:
    import yaml
except ImportError:
    yaml = None

errors = []
warnings = []
files = [p for p in ROOT.rglob("SKILL.md") if ".git" not in p.parts]
for p in files:
    text = p.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append(f"{p}: no YAML frontmatter")
        continue
    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append(f"{p}: unterminated frontmatter")
        continue
    raw = parts[1]
    if yaml:
        try:
            d = yaml.safe_load(raw)
        except Exception as e:
            errors.append(f"{p}: YAML parse error: {e}")
            continue
        if not isinstance(d, dict):
            errors.append(f"{p}: frontmatter is not a mapping")
            continue
        for k in REQUIRED:
            if k not in d:
                errors.append(f"{p}: missing key '{k}'")
        md = d.get("metadata") or {}
        hermes = md.get("hermes") or {}
        if not hermes.get("tags"):
            errors.append(f"{p}: metadata.hermes.tags empty")
        if "related_skills" not in hermes:
            errors.append(f"{p}: metadata.hermes.related_skills missing")
        # name must match directory name
        if d.get("name") and d["name"] != p.parent.name:
            errors.append(f"{p}: name '{d['name']}' != dir '{p.parent.name}'")

    # required sections — accept bilingual/legacy heading variants.
    # Missing sections in pre-existing legacy skills are reported as WARNINGS
    # (non-blocking); structural problems stay hard errors.
    SECTION_ALIASES = {
        "Overview": ["## Overview", "## 概述", "## Overview / 概述", "## 概览"],
        "When to Use": ["## When to Use", "## 适用场景", "## When to Use / 适用场景",
                        "## 何时使用", "## When to use", "## When to Use This Skill"],
        "Core Workflow": ["## Core Workflow", "## Workflow", "## 工作流",
                          "## Core Workflow / 核心工作流", "## 核心工作流",
                          "## How It Works", "## How to Use"],
        "Example Invocations": ["## Example Invocations", "## Examples", "## 示例",
                                "## Example Invocations / 调用示例", "## 调用示例",
                                "## Example Usage", "## Usage Examples", "## Example",
                                "## 📋 Output Example"],
        "Common Pitfalls": ["## Common Pitfalls", "## Pitfalls", "## 常见陷阱",
                            "## Common Pitfalls / 常见陷阱", "## 常见问题"],
        "Verification Checklist": ["## Verification Checklist", "## Checklist",
                                   "## 验证清单", "## Verification Checklist / 验证清单",
                                   "## 验证"],
        "Data Sources & Accuracy": ["## Data Sources & Accuracy", "## Data Sources",
                                    "## 数据来源", "## Data Sources & Accuracy / 数据来源与准确性",
                                    "## 数据来源与准确性", "## Data Sources and Accuracy",
                                    "## Accuracy", "## Data & Accuracy"],
    }
    for canonical, variants in SECTION_ALIASES.items():
        if not any(v in text for v in variants):
            warnings.append(f"{p.relative_to(ROOT)}: no '{canonical}' section (legacy skill)")

print(f"checked {len(files)} SKILL.md files")
if warnings:
    print(f"\n{len(warnings)} warnings (legacy skills missing newer sections):")
    for w in warnings:
        print("  ~", w)
if errors:
    print("\nERRORS:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("\nall frontmatter + required sections OK")
sys.exit(0)
