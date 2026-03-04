---
name: friday-weekly-review
description: Produce a weekly Friday review by aggregating calendar events, emails, call transcripts, and tasks (WorkBoard OKRs) into summary views of things accomplished and to-do items. Use when the user asks for a Friday review, weekly summary, weekly recap, or what they did this week / what's left to do.
---

# Friday Weekly Review Agent

This skill defines how to build **summary views** for a weekly Friday review by pulling from:

- **Calendar** — meetings and events (past = accomplished, upcoming = to-do)
- **Gmail** — recent and important emails (handled vs. action needed)
- **Call transcripts** — meetings that had recordings/transcripts; **must be read and analysed** (key points, decisions, action items)
- **Tasks / OKRs** — WorkBoard objectives and key results (progress = accomplished, open = to-do)

You need these MCP servers: **user-calendar-assistant**, **user-gmail**, **user-gdrive-assistant**, **project-0-config-mcp-workboard**.

---

## 1. Define the review window

- **Review week**: Monday 00:00 through Friday 23:59 of the **current week** (user's local date).
- If the user says "last week", use the **previous** Monday–Friday instead.
- Use ISO 8601 for API calls, e.g. `2026-03-02T00:00:00` and `2026-03-06T23:59:59` for the week of 2–6 Mar 2026.

Compute:
- `time_min` = Monday 00:00 (local or UTC as required by the calendar API)
- `time_max` = Friday 23:59 or **today** if today is before Friday

---

## 2. Gather data (run in parallel where possible)

### 2.1 Calendar — events in the review window

- Call **`calendar_search`** with:
  - `query`: use a broad term so most events are included (e.g. `"meeting"` or `"a"`; avoid empty string if the API requires a value)
  - `time_min`: Monday 00:00 of the review week
  - `time_max`: Friday 23:59 (or end of today)
  - `calendar_id`: `"primary"` unless the user specified another
  - `max_results`: 100 or 50

Split results into:
- **Past** (start time &lt; now) → **Accomplished**
- **Upcoming** (start time ≥ now) → **To-Do**

For each event, keep: **title**, **start**, **end**, **calendar**, and whether it has **description** links to transcripts/recordings (e.g. "Transcript", "Recording", "docs.google.com").

### 2.2 Gmail — emails in the review week

- Call **`gmail_search`** with:
  - `query`: `after:YYYY/M/D` where the date is **Monday** of the review week (e.g. `after:2026/3/2`)
  - `num_results`: 30–50

Optionally call **`gmail_inbox`** with `unread_only: true` and `num_emails: 20` to capture **action items** (unread / priority).

Use message **subjects**, **senders**, and **snippet** (or a quick **`gmail_read`** on a few) to classify:
- **Handled / notable** → Accomplished (e.g. important threads you replied to or closed)
- **Unread or needs reply** → To-Do

### 2.3 Call transcripts — find, read, and analyse (required)

You **must** find transcript documents for the review week, read their content, and include a short **analysis** (key points, decisions, action items) in the review. Do not only list that a transcript exists.

**Step A — Find transcript sources**

1. Call **`calendar_search`** with `query`: `"AI office hours"` or `"transcript"` or `"recording"`, same `time_min` / `time_max`, `max_results`: 20.
2. For each matching event, call **`calendar_get_event`** and from the **description** (and any attachments) extract:
   - Google Doc URLs: `docs.google.com/document/d/{DOC_ID}` → the segment after `/d/` is the document ID for **`gdocs_read_markdown`**.
   - Any Drive file IDs if the API returns them.
3. Call **`gdrive_list`** on the **transcripts Drive folder** to find transcript files in the review window. Default folder ID (AI office hours sync): `1qWWkHcqefAS5RVCCUazcEjsRHesWfVo2`. If the user has specified a different folder (e.g. a Pod Transcripts folder), use that. For each file that is a Google Doc (or has a Doc export), note its **file ID** (Drive file ID = Doc ID for Google Docs).

**Step B — Read transcript content**

- For each document ID you collected, call **`gdocs_read_markdown`** with `doc_id` = that ID.
- If a "transcript" is a different type (e.g. PDF), use **`gdrive_download`** or available read tools only if the MCP supports it; otherwise note "Transcript available but not readable as Doc" and still list the meeting.

**Step C — Analyse and summarise**

For each transcript you successfully read, produce a short **analysis** to include in the review:

- **Key points** — 2–5 bullets: main topics, outcomes, or decisions.
- **Action items** — any clear next steps, owners, or deadlines mentioned (add these to **To-Do** if they are for the user).
- **Decisions** — any decisions or commitments noted.

Include this analysis in the **Accomplished** section under a **"Transcript analysis"** (or **"Meeting transcripts"**) subheading, one block per meeting with transcript.

### 2.4 Tasks / OKRs (WorkBoard)

- Call **`workboard_get_user_tool`** (no arguments) to get the current user.
- Call **`workboard_get_my_objectives_tool`** (no arguments, or with `objective_ids` if the user has given them) to get **objectives and key results**.

Classify:
- **Key results completed or on track** → Accomplished
- **Key results not done / at risk** → To-Do

---

## 3. Build the summary views

Produce **two sections** in one reply (or in a single markdown block the user can copy).

### 3.1 Accomplished (this week)

- **Meetings & events**: List past calendar events (title, date/time). Highlight any that had transcripts/recordings.
- **Transcript analysis** (required when transcripts exist): For each meeting transcript you read, include:
  - **Meeting**: [title], [date].
  - **Key points**: 2–5 bullets (topics, outcomes, decisions).
  - **Action items**: Any next steps or owners (also surface these in To-Do if they are for the user).
- **Email**: 2–3 bullets on notable threads handled or important received.
- **OKRs / tasks**: Progress on objectives and key results (e.g. "X% on KR …", "Completed …").

Keep each section short (bullets, 1 line per item unless the user asked for detail). If no transcripts were found or readable, say so under **Transcript analysis** and skip that block.

### 3.2 To-Do (for next week / carry-over)

- **Upcoming meetings**: Next week’s (or remaining) calendar events that need prep or follow-up.
- **Email**: Unread or action-needed items (subject + sender, link if possible).
- **OKRs / tasks**: Key results still open or at risk; suggested next actions if obvious.

---

## 4. Present the result

- Output a single **Friday Weekly Review** block in markdown with clear headings: **Accomplished** and **To-Do**.
- Optionally add a one-line **Summary** at the top (e.g. "X meetings, Y emails in scope, Z objectives; N items to do next week").
- If a data source failed (e.g. Gmail or WorkBoard unavailable), say so and still show what you have.

---

## 5. Optional: export or schedule

- If the user wants to **save** the review: offer to write it to a file (e.g. `friday-review-YYYY-MM-DD.md`) in the repo or a path they choose.
- If they want it **emailed**: they can use an external script or tool; the agent does not send email by default.

---

## Rules

- Always use the **review window** (current or last week) consistently across calendar, email, and transcripts.
- **Always analyse meeting transcripts** when present: find transcript docs (calendar descriptions, transcript Drive folder), read them with **`gdocs_read_markdown`**, and include key points, decisions, and action items in the review. Do not only list "transcript available".
- Prefer **parallel** MCP calls where there are no dependencies (e.g. calendar + Gmail + WorkBoard at once). Transcript reading depends on first having doc IDs from calendar or **`gdrive_list`**.
- Do not invent events or emails; only list what the APIs return.
- If the user asks for "daily" review, use the same structure but limit the window to **today** (and optionally yesterday).
