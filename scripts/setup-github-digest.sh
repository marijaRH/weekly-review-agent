#!/usr/bin/env bash
# One-time setup: init git, commit the digest workflow, then show exact steps to push and add GitHub secrets.
# Run from repo root (config): ./scripts/setup-github-digest.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT"

# 1) Init git and first commit (if not already a repo)
if ! git rev-parse --is-inside-work-tree 2>/dev/null; then
  git init
  git branch -M main
fi

# Don't commit secrets
echo "scripts/quantum-digest.env" >> .gitignore 2>/dev/null || true
echo "scripts/digest-*.env" >> .gitignore 2>/dev/null || true
git add .gitignore .github scripts/quantum_daily_digest.py scripts/requirements-digest.txt \
  scripts/run-quantum-digest.sh scripts/quantum-digest.env.example scripts/digest-topic2.env.example \
  scripts/QUANTUM_DIGEST_README.md scripts/install-cron-job-digest.sh 2>/dev/null || true
git add scripts/digest-offshore.env.example 2>/dev/null || true
git status --short
if git diff --cached --quiet 2>/dev/null; then
  echo "Nothing new to commit (workflow already committed?)."
else
  git commit -m "Add GitHub Actions workflow for quantum digest at 8 AM CET"
fi

# 2) Recipient for copy-paste (from env if present)
RECIPIENT="mashka.zajka@gmail.com"
if [[ -f "$SCRIPT_DIR/quantum-digest.env" ]]; then
  R="$(grep -E '^QUANTUM_DIGEST_RECIPIENT=' "$SCRIPT_DIR/quantum-digest.env" | sed 's/.*=//;s/"//g;s/ .*//')"
  [[ -n "$R" ]] && RECIPIENT="$R"
fi

echo ""
echo "=============================================="
echo "  NEXT: Push to GitHub and add 2 secrets"
echo "=============================================="
echo ""
echo "1) Create a new repo on GitHub (e.g. calendar-assistant-config)."
echo "   https://github.com/new"
echo ""
echo "2) Push this folder (run from here):"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "   git push -u origin main"
echo ""
echo "3) Add repository secrets (Settings → Secrets and variables → Actions):"
echo "   https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions"
echo ""
echo "   Secret 1:  Name = QUANTUM_DIGEST_RECIPIENT"
echo "              Value = $RECIPIENT"
echo ""
echo "   Secret 2:  Name = GMAIL_APP_PASSWORD"
echo "              Value = (your 16-char Gmail App Password, NO SPACES)"
echo "              Get it from scripts/quantum-digest.env — remove spaces, e.g. gtpmabeahwxarxfm"
echo ""
echo "4) Test: Actions → Quantum Digest 8AM CET → Run workflow"
echo ""
