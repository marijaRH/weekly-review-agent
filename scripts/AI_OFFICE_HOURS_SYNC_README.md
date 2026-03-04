# AI Office Hours — Weekly Transcript Sync

Weekly job that finds calendar meetings whose title or description contains **"AI office hours"**, collects their **Recording** (and transcript) attachments from Google Drive, and **copies any new ones** into a fixed Drive folder. Already-copied file IDs are stored in `.ai-office-hours-copied.log` so each run only adds new recordings.

**Target folder (default):** `1qWWkHcqefAS5RVCCUazcEjsRHesWfVo2`

## Setup

### 1. Google Cloud project and Service Account

1. In [Google Cloud Console](https://console.cloud.google.com/), create or select a project.
2. Enable **Google Calendar API** and **Google Drive API** (APIs & Services → Library).
3. Create a **Service Account** (APIs & Services → Credentials → Create Credentials → Service account). Download its JSON key.
4. **Share with the SA:**
   - **Calendar:** In Google Calendar, share your calendar (Settings → your calendar → Share with specific people) with the **service account email** (e.g. `something@project.iam.gserviceaccount.com`) with “See all event details”.
   - **Drive folder:** Open the target folder in Drive, click Share, add the same service account email with **Editor** (so it can add copies).

### 2. Local / cron

1. Copy the env example and set credentials:
   ```bash
   cp scripts/ai-office-hours-sync.env.example scripts/ai-office-hours-sync.env
   ```
   In `ai-office-hours-sync.env` either:
   - Set `GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account.json`, or
   - Set `GCP_SA_KEY='{"type":"service_account",...}'` (full JSON as one line).

2. If using a shared calendar (not your default “primary”), set:
   ```bash
   AI_OFFICE_HOURS_CALENDAR_ID=your.email@example.com
   ```

3. Install dependencies and run:
   ```bash
   pip install -r scripts/requirements-ai-office-hours-sync.txt
   ./scripts/run-ai-office-hours-sync.sh
   ```

4. **Weekly cron (e.g. Mondays 9 AM CET):**
   ```bash
   crontab -e
   ```
   Add:
   ```cron
   0 8 * * 1 TZ=Europe/Paris /path/to/config/scripts/run-ai-office-hours-sync.sh
   ```

### 3. GitHub Actions (weekly)

1. In the repo: **Settings → Secrets and variables → Actions**.
2. Add secret **`GCP_SA_KEY`**: paste the **entire** contents of the service account JSON file (one line is fine).
3. Optional variables (or use defaults):
   - **`AI_OFFICE_HOURS_CALENDAR_ID`** — calendar to search (e.g. your email); required if the SA has no “primary” (use the shared calendar ID).
   - **`AI_OFFICE_HOURS_TARGET_FOLDER_ID`** — default is `1qWWkHcqefAS5RVCCUazcEjsRHesWfVo2`.

The workflow runs **Mondays 08:00 UTC** (9 AM CET) and can be triggered manually from the Actions tab (“AI Office Hours — Transcripts Sync” → Run workflow).

## Criteria

- **Calendar:** Events matching the query **"AI office hours"** (title/description).
- **Attachments:** Only those whose title contains “Recording” or “Transcript” are copied.
- **Deduplication:** Each source file ID is copied at most once; subsequent runs skip it using `.ai-office-hours-copied.log`.

## Files

| File | Purpose |
|------|--------|
| `scripts/ai_office_hours_transcripts_sync.py` | Main script |
| `scripts/run-ai-office-hours-sync.sh` | Runner (loads env, runs script) |
| `scripts/ai-office-hours-sync.env.example` | Env template |
| `scripts/.ai-office-hours-copied.log` | Log of already-copied Drive file IDs (persisted in CI) |
| `.github/workflows/ai-office-hours-transcripts.yml` | Weekly workflow |
