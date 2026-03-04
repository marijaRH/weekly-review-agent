# Create GitHub repo and push with full description

This is a **standalone** repo (not part of calendar-assistant). Use these steps to put it in its own new GitHub repository with a full description.

---

## 0. Move this folder out of calendar-assistant (if needed)

If this folder is still inside `calendar-assistant/config/weekly-review-agent`, move it to its own location so it’s not inside the calendar-assistant repo:

```bash
mv /path/to/calendar-assistant/config/weekly-review-agent ~/Code/weekly-review-agent
cd ~/Code/weekly-review-agent
```

Then continue below from the folder you’ll push from (e.g. `~/Code/weekly-review-agent`).

---

## 1. Create the repository on GitHub

1. Go to **https://github.com/new** (or your organization’s “New repository” page).
2. Set:
   - **Repository name:** `weekly-review-agent` (or e.g. `calendar-assistant-config` if you prefer).
   - **Description:** use the short description below (fits GitHub’s “About” field).
   - **Visibility:** Public or Private.
   - **Do not** initialize with a README, .gitignore, or license (this repo already has them).
3. Click **Create repository**.

### Short description (copy for GitHub “About”)

```
Friday weekly review agent: calendar + email + meeting transcripts + WorkBoard OKRs → Accomplished & To-Do. Cursor skill + MCP (Gmail, Drive, WorkBoard).
```

---

## 2. Alternative: create and push with GitHub CLI

If you have [GitHub CLI](https://cli.github.com/) (`gh`) installed and logged in:

```bash
gh repo create weekly-review-agent --public --source=. --remote=origin --push --description "Friday weekly review agent: calendar + email + meeting transcripts + WorkBoard OKRs → Accomplished & To-Do. Cursor skill + MCP (Gmail, Drive, WorkBoard)."
```

Use `--private` instead of `--public` if you want a private repo. This creates the repo, sets `origin`, and pushes `main` in one step.

---

## 3. Push this project to the new repo (manual create)

From the root of this repo (e.g. `~/Code/weekly-review-agent`):

**Add the new GitHub repo as origin and push:**

```bash
git remote add origin https://github.com/YOUR_USERNAME/weekly-review-agent.git
git branch -M main
git push -u origin main
```

Use **SSH** if you prefer, e.g. `git@github.com:YOUR_USERNAME/weekly-review-agent.git`.

---

## 4. Optional: add topics on GitHub

On the repo page → **About** (gear icon) → **Topics**, add e.g.:

`calendar`, `cursor`, `mcp`, `workboard`, `automation`, `weekly-review`

---

## 5. Full description (longer, for docs or repo profile)

You can paste this into a “Full description” or docs if your host supports it:

**Weekly Review Agent** — Cursor agent skill for Friday weekly review:

- Builds **Accomplished** and **To-Do** views from Google Calendar, Gmail, meeting transcripts (read and analysed for key points and action items), and WorkBoard OKRs.
- Trigger in Cursor with “Give me my weekly summary” or “Run my Friday review”.
- Uses MCP: calendar-assistant, Gmail, Google Drive, WorkBoard.

Requires: Google (Calendar, Gmail, Drive), optional WorkBoard API.
