#!/usr/bin/env bash
# Create weekly-review-agent on GitHub and push this repo. Run from this directory.
# Requires: GitHub CLI (gh) logged in, or create the repo at https://github.com/new first.

set -e
REPO_NAME="weekly-review-agent"
GITHUB_USER="marijaRH"
DESCRIPTION="Friday weekly review agent: calendar + email + meeting transcripts + WorkBoard OKRs → Accomplished & To-Do. Cursor skill + MCP (Gmail, Drive, WorkBoard)."

cd "$(dirname "$0")"

if command -v gh &>/dev/null; then
  echo "Creating repo ${GITHUB_USER}/${REPO_NAME} and pushing..."
  gh repo create "$REPO_NAME" --public --source=. --remote=origin --push --description "$DESCRIPTION"
  echo "Done. https://github.com/${GITHUB_USER}/${REPO_NAME}"
else
  echo "GitHub CLI (gh) not found. Create the repo manually:"
  echo "  1. Open https://github.com/new?name=${REPO_NAME}&description=$(echo "$DESCRIPTION" | sed 's/ /%20/g')"
  echo "  2. Click Create repository (do not add README/gitignore)."
  echo "  3. Run: git remote add origin git@github-marijaRH:${GITHUB_USER}/${REPO_NAME}.git && git push -u origin main"
  exit 1
fi
