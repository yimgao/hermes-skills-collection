#!/usr/bin/env bash
# cron_audit.sh — Scheduled backup-coverage audit.
#
# Runs `backup_audit.py cover` on a schedule and writes a Markdown report to
# ~/.hermes/backup-audit/reports/. Exits non-zero when coverage has degraded,
# so cron/monitoring can alert on it.
#
# Usage:
#   ./cron_audit.sh              # write report, print summary
#   ./cron_audit.sh --quiet      # only print on failure
#
# Suggested crontab (weekly, Monday 09:12):
#   12 9 * * 1  /path/to/cron_audit.sh >> ~/.hermes/backup-audit/cron.log 2>&1

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT="$SCRIPT_DIR/backup_audit.py"
OUT_DIR="${HOME}/.hermes/backup-audit/reports"
QUIET=0
[[ "${1:-}" == "--quiet" ]] && QUIET=1

PY="$(command -v python3 || true)"
if [[ -z "$PY" ]]; then
  echo "[FATAL] python3 not found in PATH" >&2
  exit 127
fi
if [[ ! -f "$AUDIT" ]]; then
  echo "[FATAL] backup_audit.py not found at $AUDIT" >&2
  exit 127
fi

mkdir -p "$OUT_DIR"
STAMP="$(date +%Y-%m-%d)"
REPORT="$OUT_DIR/audit-$STAMP.md"

"$PY" "$AUDIT" report --out "$REPORT" >/dev/null 2>&1

# `cover` exits 1 when a dataset needs action.
"$PY" "$AUDIT" cover > "$OUT_DIR/latest.txt" 2>&1
COVER_RC=$?

SUMMARY="$(tail -n 1 "$OUT_DIR/latest.txt")"

if [[ "$COVER_RC" -eq 0 ]]; then
  if [[ "$QUIET" -eq 0 ]]; then
    echo "[OK] $SUMMARY"
    echo "     report: $REPORT"
  fi
  exit 0
else
  echo "[WARN] $SUMMARY" >&2
  echo "       report: $REPORT" >&2
  sed -n '1,40p' "$OUT_DIR/latest.txt" >&2
  exit "$COVER_RC"
fi
