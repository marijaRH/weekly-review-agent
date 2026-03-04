# Create GitHub repo and push with full description

Use this to create a **new repository** on GitHub and push this project there with a clear description.

---

## 1. Create the repository on GitHub

1. Go to **https://github.com/new** (or your organization’s “New repository” page).
2. Set:
   - **Repository name:** `calendar-assistant-config` (or e.g. `friday-review-agent` if you prefer).
   - **Description:** use the short description below (fits GitHub’s “About” field).
   - **Visibility:** Public or Private.
   - **Do not** initialize with a README, .gitignore, or license (this repo already has them).
3. Click **Create repository**.

### Short description (copy for GitHub “About”)

```
Config & agent skills for calendar workflows: Friday weekly review (calendar + email + transcripts + OKRs), daily/weekly digests (quantum, jobs), AI office hours transcript sync, MCP (WorkBoard, Gmail, Drive).
```

---

## 2. Alternative: create and push with GitHub CLI

If you have [GitHub CLI](https://cli.github.com/) (`gh`) installed and logged in:

```bash
gh repo create calendar-assistant-config --public --source=. --remote=origin --push --description "Config & agent skills for calendar workflows: Friday weekly review (calendar + email + transcripts + OKRs), daily/weekly digests (quantum, jobs), AI office hours transcript sync, MCP (WorkBoard, Gmail, Drive)."
```

Use `--private` instead of `--public` if you want a private repo. This creates the repo, sets `origin`, and pushes `main` in one step.

---

## 3. Push this project to the new repo (manual create)

From the root of this repo (e.g. `calendar-assistant/config`):

**If this is a fresh clone and you have no remote yet:**

```bash
git remote add origin https://github.com/YOUR_USERNAME/calendar-assistant-config.git
git branch -M main
git push -u origin main
```

**If you already have a different remote (e.g. `origin` points elsewhere):**

```bash
# Option A: Replace origin with the new repo
git remote set-url origin https://github.com/YOUR_USERNAME/calendar-assistant-config.git
git push -u origin main

# Option B: Add the new repo as a second remote and push there
git remote add github https://github.com/YOUR_USERNAME/calendar-assistant-config.git
git push -u github main
```

Use **SSH** if you prefer, e.g. `git@github.com:YOUR_USERNAME/calendar-assistant-config.git`.

---

## 4. Optional: add topics on GitHub

On the repo page → **About** (gear icon) → **Topics**, add e.g.:

`calendar`, `digest`, `cursor`, `mcp`, `workboard`, `automation`, `weekly-review`

---

## 5. Full description (longer, for docs or repo profile)

You can paste this into a “Full description” or docs if your host supports it:

**Calendar Assistant Config** — Configuration and automation for calendar-driven workflows:

- **Friday weekly review agent** — Cursor skill that builds weekly “Accomplished” and “To-Do” views from Google Calendar, Gmail, meeting transcripts (read and analysed for key points and action items), and WorkBoard OKRs. Trigger with “Give me my weekly summary” in Cursor.
- **Daily digest pipelines** — RSS-based email digests (quantum, offshore, or custom topics) with prioritisation, no repetition, and optional LinkedIn drafts; runs at 8 AM CET via GitHub Actions or cron.
- **Weekly job digest** — Filtered marketing/GTM/ecosystem job listings from remote job boards.
- **AI office hours transcript sync** — Weekly sync of AI office hours meeting recordings/transcripts from Calendar into a Google Drive folder.
- **MCP integration** — Calendar, Gmail, Google Drive, and WorkBoard MCP servers for use with Cursor or other MCP clients.

Requires: Google (Calendar, Gmail, Drive), optional WorkBoard API, and env files for secrets (not committed).
