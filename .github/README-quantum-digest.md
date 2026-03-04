# Quantum digest at 8 AM CET (GitHub Actions)

The workflow in `workflows/quantum-digest.yml` runs **on GitHub’s servers** at 8 AM CET every day, so you get the digest even when your Mac is off.

## One-time setup

1. **Push this repo to GitHub** (if it isn’t already), so the workflow file is in the repo.

2. **Add two repository secrets**  
   In the repo: **Settings → Secrets and variables → Actions → New repository secret.**

   - **`QUANTUM_DIGEST_RECIPIENT`**  
     Your email, e.g. `mashka.zajka@gmail.com`
   - **`GMAIL_APP_PASSWORD`**  
     Your Gmail App Password (16-character, same as in `scripts/quantum-digest.env`).  
     No spaces in the secret (paste the 16 characters only).

3. **Done.** The scheduled run will use these secrets. No need to keep your Mac on at 8 AM.

## Test run

In the repo: **Actions → Quantum Digest 8AM CET → Run workflow.**  
This sends one digest immediately so you can confirm it works.

## If the repo root is the parent folder

If this `config` folder lives inside a larger repo (e.g. `calendar-assistant`), the workflow already switches into `config` when it finds `config/scripts/quantum_daily_digest.py`, so no change is needed.
