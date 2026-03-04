# Friday Weekly Review — Agent & Data Sources

An **agent** (Cursor + MCP) that reviews your calendar, email, call transcripts, and WorkBoard OKRs to produce **summary views** for a weekly Friday review: **Accomplished** and **To-Do**.

## How to run the agent

1. **In Cursor**: Open this project and ask in chat, for example:
   - *"Run my Friday weekly review"*
   - *"Give me my weekly summary — accomplished and to-do"*
   - *"What did I do this week and what's left?"*

2. **Use the skill**: The agent follows **`FRIDAY_REVIEW_SKILL.md`** (in the repo root). For best results, you can say:
   - *"Follow FRIDAY_REVIEW_SKILL and run my Friday review"*
   - Or add a Cursor rule (see below) so the agent automatically uses that skill when you mention "Friday review" or "weekly summary".

3. **Save the output**: Ask the agent to write the review to a file, e.g. *"Save this review as `friday-review-2026-03-06.md`"*.

## What the agent uses (MCP)

| Source | MCP server | What’s pulled |
|--------|------------|----------------|
| **Calendar** | user-calendar-assistant | Events in the review week (Mon–Fri). Past → Accomplished; upcoming → To-Do. |
| **Gmail** | user-gmail | Emails after Monday of the week; optional unread/inbox for action items. |
| **Call transcripts** | user-calendar-assistant + user-gdrive-assistant | Calendar events with "AI office hours" / "transcript"; transcript folder in Drive. **Transcripts are read and analysed** (key points, decisions, action items). |
| **Tasks / OKRs** | project-0-config-mcp-workboard | Your WorkBoard objectives and key results → progress (accomplished) vs open (to-do). |

## Review window

- **Default**: Monday 00:00 → Friday 23:59 of the **current week** (based on your local date).
- **"Last week"**: Same structure for the **previous** Monday–Friday.
- **"Daily"**: You can ask for a daily recap (today only).

## Prerequisites

- **MCP servers** enabled in Cursor: calendar-assistant, gmail, gdrive-assistant, mcp-workboard (see `.cursor/mcp.json` or Cursor MCP settings).
- **Auth**: Each server must be signed in so the agent can call calendar, Gmail, Drive, and WorkBoard.

## Optional: Cursor rule so the agent auto-uses the skill

Create a rule that tells the agent to use the Friday review skill when you ask for a weekly recap. Example:

**`.cursor/rules/friday-review.mdc`** (or in your global Cursor rules):

```markdown
---
description: When the user asks for Friday review, weekly summary, or weekly recap
globs:
alwaysApply: false
---

When the user asks for a "Friday review", "weekly summary", "weekly recap", "what I did this week", or "what's left to do this week", read and follow the instructions in **FRIDAY_REVIEW_SKILL.md** in this project. Use the MCP tools (calendar, Gmail, Drive, WorkBoard) to gather data and produce the Accomplished and To-Do summary views.
```

Then the agent will use the skill whenever you mention those phrases.

## Files

| File | Purpose |
|------|--------|
| `FRIDAY_REVIEW_SKILL.md` (repo root) | Agent skill: step-by-step instructions for the Friday review. |
| `scripts/FRIDAY_REVIEW_README.md` | This file — usage and data sources. |

## Transcripts folder (optional)

The skill can list and read transcript docs from a Google Drive folder. It uses folder ID `1qWWkHcqefAS5RVCCUazcEjsRHesWfVo2` by default (or one you set in the skill). If your transcripts live in a different folder, tell the agent: *"Use Drive folder ID … for transcripts."*
