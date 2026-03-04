#!/usr/bin/env bash
# Install cron so the job digest runs daily at 9:00 CET.
# Run from the config repo root: ./scripts/install-cron-job-digest.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
CRON_LINE="0 9 * * * TZ=Europe/Paris ${SCRIPT_DIR}/run-job-digest.sh"

echo "Add this line to your crontab for a daily job digest at 9:00 CET:"
echo ""
echo "  $CRON_LINE"
echo ""
echo "To install:"
echo "  1. Run:  crontab -e"
echo "  2. Paste the line above, save and exit."
echo ""
echo "To install automatically (append to existing crontab):"
echo "  (crontab -l 2>/dev/null; echo \"$CRON_LINE\") | crontab -"
echo ""

read -r -p "Append this line to your crontab now? [y/N] " reply
case "${reply}" in
  [yY][eE][sS]|[yY])
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
    echo "Done. Verify with: crontab -l"
    ;;
  *)
    echo "Skipped. Add the line manually with: crontab -e"
    ;;
esac
