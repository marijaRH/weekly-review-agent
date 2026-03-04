# Calendar Assistant Config

Configuration, scripts, and agent skills for **calendar-driven workflows**: daily and weekly email digests, **Friday weekly review** (calendar + email + meeting transcripts + OKRs), AI office hours transcript sync, job digests, and MCP (WorkBoard, calendar, Gmail, Drive) integration.

---

## What’s in this repo

| Component | Description |
|-----------|-------------|
| **Friday weekly review** | Cursor agent skill that aggregates calendar, Gmail, call transcripts, and WorkBoard OKRs into **Accomplished** and **To-Do** summary views. Transcripts are read and analysed (key points, decisions, action items). See [FRIDAY_REVIEW_SKILL.md](FRIDAY_REVIEW_SKILL.md) and [scripts/FRIDAY_REVIEW_README.md](scripts/FRIDAY_REVIEW_README.md). |
| **Daily digest pipelines** | Topic-based email digests from RSS: quantum, offshore, or custom topics; prioritisation, no repetition (14-day), optional LinkedIn drafts. Runs via GitHub Actions or cron. |
| **Weekly job digest** | Marketing/GTM/ecosystem job listings from remote job feeds, filtered and ranked. See [scripts/JOBS_DIGEST_README.md](scripts/JOBS_DIGEST_README.md). |
| **AI office hours transcript sync** | Weekly copy of “AI office hours” meeting recordings/transcripts from Calendar into a Drive folder. See [scripts/AI_OFFICE_HOURS_SYNC_README.md](scripts/AI_OFFICE_HOURS_SYNC_README.md). |
| **MCP / WorkBoard** | Config and scripts for calendar-assistant, Gmail, Drive, and WorkBoard MCP servers (e.g. `.cursor/mcp.json`). |

---

## Quick links

- **Run Friday weekly review** — In Cursor: ask *“Give me my weekly summary”* or *“Run my Friday review”* (uses [FRIDAY_REVIEW_SKILL.md](FRIDAY_REVIEW_SKILL.md)).
- **Quantum digest (8 AM CET)** — [Quick start below](#quick-start-quantum-digest-8-am-cet-github-actions) or [.github/workflows/](.github/workflows/).
- **New repo on GitHub** — See [GITHUB_REPO_SETUP.md](GITHUB_REPO_SETUP.md) for creating the repo and pushing with a full description.

---

## Daily digest pipelines — quantum, offshore, and custom topics

Automated daily (or weekly) email digests: **top N articles** from RSS feeds, **prioritised** (e.g. partnerships & announcements over R&D), **no repetition** (same article not sent again within 14 days), plus **LinkedIn post drafts** in your voice.

Use cases:

- **Quantum digest** — Top 3 quantum computing articles at 8 AM CET, prioritising IBM/Red Hat and partnership/announcement news.
- **Other topics** — Same engine for other themes (e.g. offshore oil & gas, AI) and recipients via separate env files.

---

## How it works (process overview)

1. **RSS feeds** — The script fetches articles from configurable RSS URLs (default: ScienceDaily Quantum, Quanta Magazine Physics, Red Hat Blog).
2. **Filter by topic** — Only articles whose title/summary contain your topic keywords (e.g. `quantum`, or `offshore,oil,gas` for another digest).
3. **No repetition** — A log file (`.quantum-digest-sent.log`) stores every article URL already sent. Any URL sent in the **last 14 days** is skipped so you get different news each day.
4. **Prioritisation** — Among matching articles, the script ranks by:
   - **Partnership / large announcements first** (partnerships, deals, acquisitions, launches, enterprise, funding).
   - **Then** IBM/Red Hat–relevant content (IBM, Qiskit, Red Hat, RHEL, OpenShift).
   - **Then** newest first.
5. **Top N** — It picks the top N (default 3; configurable via `DIGEST_TOP_N`).
6. **Email** — Builds HTML + plain email with article titles, summaries, links, and **LinkedIn post drafts** (hook, takeaway, CTA, hashtags).
7. **Send** — Sends via Gmail (App Password) or SMTP. When run from **GitHub Actions**, the workflow runs at 8 AM CET and commits the sent-log back to the repo so the next run sees it.

---

## Repository structure

```
.github/
  workflows/
    quantum-digest.yml    # Runs at 8 AM CET, sends digest, commits sent-log
  README-quantum-digest.md
scripts/
  quantum_daily_digest.py # Main script: fetch, score, pick, email
  run-quantum-digest.sh   # Loads env and runs script (for cron or CI)
  quantum-digest.env      # Your config (recipient, Gmail App Password) — not committed
  quantum-digest.env.example
  digest-topic2.env.example
  digest-offshore.env     # Example: weekly offshore digest — not committed
  .quantum-digest-sent.log # Log of sent URLs (committed so CI sees it)
  requirements-digest.txt
  QUANTUM_DIGEST_README.md
.gitignore
README.md                 # This file
```

---

## Quick start: quantum digest 8 AM CET (GitHub Actions)

1. **Clone or use this repo** on GitHub (e.g. `marijaRH/calendar-assistant-config`).

2. **Add two repository secrets** (Settings → Secrets and variables → Actions):
   - `QUANTUM_DIGEST_RECIPIENT` — Email that receives the digest (e.g. `you@gmail.com`).
   - `GMAIL_APP_PASSWORD` — Gmail App Password (16 characters, no spaces). Create at [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2FA).

3. **Run the workflow** — Actions → “Quantum Digest 8AM CET” → Run workflow. Check your inbox.

4. **Schedule** — The workflow is scheduled for 07:00 UTC (= 8 AM CET). No further action needed; it runs every day on GitHub’s servers.

---

## Running locally (cron or one-off)

1. **Install dependency**
   ```bash
   pip install -r scripts/requirements-digest.txt
   ```

2. **Configure**
   ```bash
   cp scripts/quantum-digest.env.example scripts/quantum-digest.env
   # Edit: QUANTUM_DIGEST_RECIPIENT, GMAIL_APP_PASSWORD="your-16-char-no-spaces"
   ```

3. **Test**
   ```bash
   ./scripts/run-quantum-digest.sh
   ```

4. **Schedule (e.g. 8 AM CET)**  
   Add to crontab (`crontab -e`):
   ```cron
   TZ=Europe/Paris
   0 8 * * * /absolute/path/to/config/scripts/run-quantum-digest.sh
   ```
   Note: cron only runs when the machine is on. For “always on” use GitHub Actions.

---

## Second digest: different topic, different recipient

You can run another digest (e.g. offshore oil & gas, AI) to a different email:

1. Copy an example and create an env file:
   ```bash
   cp scripts/digest-topic2.env.example scripts/digest-offshore.env
   ```

2. Set in that file:
   - `QUANTUM_DIGEST_RECIPIENT` — recipient email
   - `QUANTUM_DIGEST_SENDER` — Gmail address (for sending)
   - `DIGEST_NAME` — e.g. `"Offshore Oil & Gas Digest"`
   - `DIGEST_TOP_N` — e.g. `5`
   - `DIGEST_TOPIC_KEYWORDS` — e.g. `offshore,oil,gas,FPSO,drilling`
   - `DIGEST_FEEDS` — comma-separated RSS URLs (optional)
   - `GMAIL_APP_PASSWORD` — same or another App Password

3. Run with that env:
   ```bash
   ./scripts/run-quantum-digest.sh digest-offshore.env
   ```

4. Schedule (e.g. weekly Monday): add a cron line or a second workflow that runs the script with that env.

---

## Prioritisation and no-repetition (details)

- **Partnership / large announcements** — Articles mentioning partnerships, collaborations, acquisitions, deals, launches, enterprise, funding get a higher score than pure R&D phrasing (“scientists discover”, “study finds”), so they appear first when available.
- **IBM / Red Hat** — Among those, articles mentioning IBM, Qiskit, Red Hat, RHEL, OpenShift are ranked higher.
- **No repetition** — Every sent article URL is written to `scripts/.quantum-digest-sent.log` with the send date. Articles in that log from the **last 14 days** are excluded from the next run. When using GitHub Actions, the workflow commits this file so the next day’s run sees the same history.

---

## Environment variables reference

| Variable | Required | Description |
|----------|----------|-------------|
| `QUANTUM_DIGEST_RECIPIENT` | Yes | Email that receives the digest |
| `GMAIL_APP_PASSWORD` | Yes (or SMTP_*) | Gmail App Password (16 chars, no spaces) |
| `QUANTUM_DIGEST_SENDER` | No | Sender email (default: same as recipient) |
| `DIGEST_NAME` | No | Subject line prefix (default: Quantum Digest) |
| `DIGEST_TOP_N` | No | Number of articles (default: 3) |
| `DIGEST_TOPIC_KEYWORDS` | No | Comma-separated; only articles matching any (default: quantum) |
| `DIGEST_FEEDS` | No | Comma-separated RSS URLs; overrides default feeds |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | No | Use instead of Gmail when needed |

---

## Licence and use

Use and modify as you like. No warranty. Keep `quantum-digest.env` and any `digest-*.env` with secrets out of version control (they are in `.gitignore`).
