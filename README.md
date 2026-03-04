# Weekly Review Agent

Configuration and agent skills for **Friday weekly review**: aggregate calendar, Gmail, meeting transcripts, and WorkBoard OKRs into **Accomplished** and **To-Do** summary views. Uses MCP (calendar, Gmail, Drive, WorkBoard) from Cursor.

---

## What’s in this repo

| Component | Description |
|-----------|-------------|
| **Friday weekly review** | Cursor agent skill that pulls calendar events, emails, call transcripts (read and analysed for key points and action items), and WorkBoard OKRs. Produces two views: **Accomplished** and **To-Do**. See [FRIDAY_REVIEW_SKILL.md](FRIDAY_REVIEW_SKILL.md) and [scripts/FRIDAY_REVIEW_README.md](scripts/FRIDAY_REVIEW_README.md). |
| **MCP integration** | Designed to work with calendar-assistant, Gmail, Google Drive, and WorkBoard MCP servers (e.g. via `.cursor/mcp.json` or Cursor MCP settings). |

---

## Quick links

- **Run Friday weekly review** — In Cursor, ask *“Give me my weekly summary”* or *“Run my Friday review”* (uses [FRIDAY_REVIEW_SKILL.md](FRIDAY_REVIEW_SKILL.md)).
- **New repo on GitHub** — See [GITHUB_REPO_SETUP.md](GITHUB_REPO_SETUP.md) for creating the repo and pushing with a full description.

---

## Repository structure

```
.cursor/rules/
  friday-weekly-review.mdc   # Cursor rule: run skill when user asks for weekly summary
FRIDAY_REVIEW_SKILL.md       # Agent skill: steps to build the review
GITHUB_REPO_SETUP.md        # How to create GitHub repo and push
README.md                    # This file
scripts/
  FRIDAY_REVIEW_README.md   # Usage and data sources for the Friday review
```

---

## Licence and use

Use and modify as you like. No warranty.
