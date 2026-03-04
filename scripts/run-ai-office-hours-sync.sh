#!/usr/bin/env bash
# Run the weekly AI office hours transcript sync. Use from cron (e.g. Monday 9 AM CET).
# Usage: run-ai-office-hours-sync.sh [env-file]
#   No args → use scripts/ai-office-hours-sync.env
#   With arg → use that env file

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "${1:-}" ]]; then
  if [[ "$1" == /* ]]; then
    ENV_FILE="$1"
  else
    ENV_FILE="${SCRIPT_DIR}/$1"
  fi
else
  ENV_FILE="${SCRIPT_DIR}/ai-office-hours-sync.env"
fi

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi

exec python3 "${SCRIPT_DIR}/ai_office_hours_transcripts_sync.py"
