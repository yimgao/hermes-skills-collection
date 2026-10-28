#!/usr/bin/env bash
# ingest-history.sh — refresh the command journal's shell-history index.
#
# Safe to run from cron: read-only on the history files, idempotent,
# and writes a temp file then renames so a crash never corrupts the journal.
#
# Install as a cron job:
#   crontab -e
#   0 * * * * /path/to/ingest-history.sh >> ~/command-journal-ingest.log 2>&1

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PYTHON:-python3}"

"$PY" "$HERE/journal.py" history "$@"
"$PY" "$HERE/journal.py" stats
