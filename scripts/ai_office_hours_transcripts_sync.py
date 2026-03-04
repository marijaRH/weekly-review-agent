#!/usr/bin/env python3
"""
Weekly sync: find calendar meetings matching "AI office hours", collect their
Recording/transcript attachments from Google Drive, and copy any new ones into
a target Drive folder. Tracks already-copied file IDs so each run only adds new
recordings.

Requires: Google Calendar API + Drive API, credentials (service account or OAuth).
Run weekly via cron or GitHub Actions. See ai-office-hours-sync.env.example and
README section for setup.
"""

import json
import os
import re
import sys
from pathlib import Path

# Optional: use existing venv or install google-api-python-client, google-auth
try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError as e:
    print("Install dependencies: pip install -r requirements-ai-office-hours-sync.txt", file=sys.stderr)
    sys.exit(1)

# Default target folder (user's requested folder)
DEFAULT_TARGET_FOLDER_ID = "1qWWkHcqefAS5RVCCUazcEjsRHesWfVo2"
SEARCH_QUERY = "AI office hours"
# Attachment title substring to treat as recording/transcript to copy
RECORDING_TITLE_KEYWORDS = ("Recording", "Transcript", "recording", "transcript")

# Env vars
ENV_CALENDAR_ID = "AI_OFFICE_HOURS_CALENDAR_ID"  # default 'primary'
ENV_TARGET_FOLDER_ID = "AI_OFFICE_HOURS_TARGET_FOLDER_ID"
ENV_CREDENTIALS_JSON = "GCP_SA_KEY"  # JSON string for service account
ENV_CREDENTIALS_PATH = "GOOGLE_APPLICATION_CREDENTIALS"  # path to JSON file
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


def _script_dir():
    return Path(__file__).resolve().parent


def _copied_log_path():
    return _script_dir() / ".ai-office-hours-copied.log"


def _get_credentials():
    """Build credentials from env: GCP_SA_KEY (JSON string) or GOOGLE_APPLICATION_CREDENTIALS (path)."""
    json_str = os.environ.get(ENV_CREDENTIALS_JSON)
    if json_str:
        try:
            info = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Invalid {ENV_CREDENTIALS_JSON}: {e}", file=sys.stderr)
            sys.exit(1)
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    path = os.environ.get(ENV_CREDENTIALS_PATH)
    if path and os.path.isfile(path):
        return service_account.Credentials.from_service_account_file(path, scopes=SCOPES)
    print(
        f"Set {ENV_CREDENTIALS_JSON} (JSON string) or {ENV_CREDENTIALS_PATH} (path to SA JSON).",
        file=sys.stderr,
    )
    sys.exit(1)


def _extract_drive_file_id(url_or_id: str) -> str | None:
    """Extract Drive file ID from a URL like https://drive.google.com/file/d/FILE_ID/view or open?id=FILE_ID."""
    if not url_or_id or not url_or_id.strip():
        return None
    s = url_or_id.strip()
    # drive.google.com/file/d/ID/view
    m = re.search(r"/file/d/([a-zA-Z0-9_-]+)", s)
    if m:
        return m.group(1)
    # drive.google.com/open?id=ID
    m = re.search(r"[?&]id=([a-zA-Z0-9_-]+)", s)
    if m:
        return m.group(1)
    # Assume raw ID if it looks like one (alphanumeric, dashes, underscores)
    if re.match(r"^[a-zA-Z0-9_-]+$", s):
        return s
    return None


def _load_copied_ids(log_path: Path) -> set[str]:
    """Load set of Drive file IDs we have already copied."""
    if not log_path.is_file():
        return set()
    seen = set()
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            fid = line.strip().split("\t")[0].strip()
            if fid:
                seen.add(fid)
    return seen


def _append_copied(log_path: Path, file_id: str, title: str):
    """Append a copied file ID to the log."""
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{file_id}\t{title}\n")


def _is_recording_attachment(attachment: dict) -> bool:
    title = (attachment.get("title") or "").strip()
    return any(kw in title for kw in RECORDING_TITLE_KEYWORDS)


def main():
    calendar_id = os.environ.get(ENV_CALENDAR_ID, "primary")
    target_folder_id = os.environ.get(ENV_TARGET_FOLDER_ID, DEFAULT_TARGET_FOLDER_ID)
    creds = _get_credentials()

    calendar = build("calendar", "v3", credentials=creds)
    drive = build("drive", "v3", credentials=creds)
    log_path = _copied_log_path()
    already_copied = _load_copied_ids(log_path)

    # Search events (past and future) matching "AI office hours"
    try:
        events_result = (
            calendar.events()
            .list(
                calendarId=calendar_id,
                q=SEARCH_QUERY,
                maxResults=100,
                singleEvents=True,
                orderBy="startTime",
                supportsAttachments=True,
            )
            .execute()
        )
    except HttpError as e:
        print(f"Calendar API error: {e}", file=sys.stderr)
        sys.exit(1)

    events = events_result.get("items", [])
    if not events:
        print("No events found matching 'AI office hours'.")
        return

    to_copy: list[tuple[str, str]] = []  # (file_id, title)
    seen_this_run: set[str] = set()
    for event in events:
        eid = event.get("id")
        if not eid:
            continue
        try:
            ev = calendar.events().get(calendarId=calendar_id, eventId=eid).execute()
        except HttpError:
            continue
        attachments = ev.get("attachments") or []
        for att in attachments:
            if not _is_recording_attachment(att):
                continue
            file_url = att.get("fileUrl") or att.get("fileId") or ""
            title = (att.get("title") or "Recording").strip()
            fid = _extract_drive_file_id(file_url)
            if fid and fid not in already_copied and fid not in seen_this_run:
                seen_this_run.add(fid)
                to_copy.append((fid, title))

    if not to_copy:
        print("No new recordings to copy.")
        return

    copied = 0
    for file_id, title in to_copy:
        try:
            drive.files().copy(
                fileId=file_id,
                body={"name": title, "parents": [target_folder_id]},
            ).execute()
            _append_copied(log_path, file_id, title)
            copied += 1
            print(f"Copied: {title}")
        except HttpError as e:
            print(f"Skip {file_id} ({title}): {e}", file=sys.stderr)
    print(f"Done. Copied {copied} file(s) to folder {target_folder_id}.")


if __name__ == "__main__":
    main()
