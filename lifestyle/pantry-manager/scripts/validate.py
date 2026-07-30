#!/usr/bin/env python3
"""Validate pantry-manager JSON using only the Python standard library."""

import json
import sys
from pathlib import Path

ALLOWED_UNITS = {"g", "kg", "ml", "l", "count", "pack"}
ALLOWED_STATUS = {"active", "consumed", "spoiled", "discarded", "reserved"}
ALLOWED_DATE_TYPES = {"use_by", "best_before", "sell_by", "unknown"}
REQUIRED = {"id", "name", "quantity", "unit", "location", "status", "date_type", "expires_at", "estimated_expiry"}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) != 2:
        fail("usage: validate.py PATH_TO_PANTRY_JSON")
    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(str(exc))
        return

    if data.get("schema_version") != 1:
        fail("schema_version must be 1")
    batches = data.get("batches")
    if not isinstance(batches, list):
        fail("batches must be an array")

    seen = set()
    active = 0
    for index, batch in enumerate(batches):
        if not isinstance(batch, dict):
            fail(f"batches[{index}] must be an object")
        missing = REQUIRED - batch.keys()
        if missing:
            fail(f"batches[{index}] missing: {', '.join(sorted(missing))}")
        batch_id = batch["id"]
        if not isinstance(batch_id, str) or not batch_id:
            fail(f"batches[{index}].id must be a non-empty string")
        if batch_id in seen:
            fail(f"duplicate id: {batch_id}")
        seen.add(batch_id)
        quantity = batch["quantity"]
        if isinstance(quantity, bool) or not isinstance(quantity, (int, float)) or quantity < 0:
            fail(f"{batch_id}: quantity must be a non-negative number")
        if batch["unit"] not in ALLOWED_UNITS:
            fail(f"{batch_id}: unsupported unit {batch['unit']!r}")
        if batch["status"] not in ALLOWED_STATUS:
            fail(f"{batch_id}: unsupported status {batch['status']!r}")
        if batch["date_type"] not in ALLOWED_DATE_TYPES:
            fail(f"{batch_id}: unsupported date_type {batch['date_type']!r}")
        if not isinstance(batch["estimated_expiry"], bool):
            fail(f"{batch_id}: estimated_expiry must be boolean")
        expires = batch["expires_at"]
        if expires is not None:
            try:
                from datetime import date
                date.fromisoformat(expires)
            except (TypeError, ValueError):
                fail(f"{batch_id}: expires_at must be YYYY-MM-DD or null")
        if batch["status"] == "active":
            active += 1

    print(f"OK: {path.name} ({active} active batches)")


if __name__ == "__main__":
    main()
