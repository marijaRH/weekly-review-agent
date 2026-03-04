#!/usr/bin/env bash
# Run a digest. Use from cron with 8AM CET (TZ=Europe/Paris).
# Usage: run-quantum-digest.sh [env-file]
#   No args → use scripts/quantum-digest.env (quantum digest)
#   With arg → use that env (e.g. scripts/digest-ai.env for a different topic/recipient)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -n "${1:-}" ]]; then
  if [[ "$1" == /* ]]; then
    ENV_FILE="$1"
  else
    ENV_FILE="${SCRIPT_DIR}/$1"
  fi
else
  ENV_FILE="${SCRIPT_DIR}/quantum-digest.env"
fi

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi

# So cron finds feedparser (installed in scripts/.venv-deps)
export PYTHONPATH="${SCRIPT_DIR}/.venv-deps:${PYTHONPATH:-}"

# Log when run from cron (so you can see if it ran and any errors)
LOG_FILE="${SCRIPT_DIR}/quantum-digest.log"
if [[ -t 0 ]]; then
  exec python3 "${SCRIPT_DIR}/quantum_daily_digest.py"
else
  echo "--- $(date -u +"%Y-%m-%dT%H:%M:%SZ") ---" >> "$LOG_FILE"
  python3 "${SCRIPT_DIR}/quantum_daily_digest.py" >> "$LOG_FILE" 2>&1
  echo "" >> "$LOG_FILE"
fi
