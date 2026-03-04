# Quantum Daily Digest — 8AM CET

Daily email with **top 3 quantum computing news articles** and **LinkedIn post proposals** so you can position yourself as a quantum expert.

## Easiest setup (Gmail only)

1. Open `scripts/quantum-digest.env` — recipient is already set to **mpetrova@redhat.com**.
2. Get a Gmail App Password: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (you need 2FA on first). Create one for “Mail”, copy the 16-character code.
3. In `quantum-digest.env`, paste it after `GMAIL_APP_PASSWORD=` (use any Gmail account you have; the digest will be sent *to* mpetrova@redhat.com).
4. Run once to test: `./scripts/run-quantum-digest.sh`. Schedule 8AM CET with cron (see below).

## Quick setup (full)

1. **Install dependency**
   ```bash
   pip install -r scripts/requirements-digest.txt
   ```

2. **Configure environment**
   - Copy `scripts/quantum-digest.env.example` and set at least:
     - `QUANTUM_DIGEST_RECIPIENT` — your email
     - `GMAIL_APP_PASSWORD` — Gmail App Password (2FA required), or use `SMTP_*` for another provider

3. **Create your env file** (not committed)
   ```bash
   cp scripts/quantum-digest.env.example scripts/quantum-digest.env
   # Edit scripts/quantum-digest.env and set your email + Gmail App Password
   ```

4. **Schedule at 8AM CET**
   - **macOS/Linux (cron):** run `crontab -e` and add (use your actual path):
     ```cron
     TZ=Europe/Paris
     0 8 * * * /Users/marijapetrova/Code/calendar-assistant/config/scripts/run-quantum-digest.sh
     ```
     The script loads `scripts/quantum-digest.env` automatically.
   - **Alternative:** use macOS launchd, GitHub Actions (scheduled workflow), or a cloud scheduler; run `run-quantum-digest.sh` or call `quantum_daily_digest.py` with env vars set.

## What you get

- **Email subject:** e.g. `Quantum Digest 2026-02-23 — Top 3 + LinkedIn ideas`
- **Body:** Top 3 articles (title, summary, link). **News is prioritised for IBM and Red Hat** (developments, announcements, open source). Sources: ScienceDaily, Quanta Magazine, Red Hat Blog.
- **LinkedIn drafts:** Written in your style (conversational, “Did you see this?”, value-forward, hashtags like #QuantumComputing, #IBMQuantum, #RedHat when relevant). Ready to paste and tweak.

## Run once (test)

```bash
cd /Users/marijapetrova/Code/calendar-assistant/config
# After creating scripts/quantum-digest.env:
./scripts/run-quantum-digest.sh
# Or with inline env:
QUANTUM_DIGEST_RECIPIENT=your@email.com GMAIL_APP_PASSWORD=xxxx python3 scripts/quantum_daily_digest.py
```

If you don’t set `GMAIL_APP_PASSWORD` (or SMTP credentials), the script prints the digest to stdout and exits with code 2 so you can inspect it or pipe to `mail`.

## Second digest: different topic, different email

You can run a second digest on another topic and send it to another address.

1. Copy the example and create your second env file:
   ```bash
   cp scripts/digest-topic2.env.example scripts/digest-ai.env
   ```
2. Edit `scripts/digest-ai.env`:
   - `QUANTUM_DIGEST_RECIPIENT` — email that should receive this digest
   - `DIGEST_TOPIC_KEYWORDS` — comma-separated keywords; only articles containing at least one are included (e.g. `ai,machine learning,llm` or `red hat,openshift`)
   - `DIGEST_NAME` — subject line (e.g. `AI Digest`)
   - Optionally `DIGEST_FEEDS` — comma-separated RSS URLs to use instead of the default feeds
   - `GMAIL_APP_PASSWORD` — same as main digest (or another Gmail App Password)
3. Test: `./scripts/run-quantum-digest.sh scripts/digest-ai.env`
4. Schedule daily (e.g. same 8AM): add a second cron line:
   ```cron
   0 8 * * * /Users/marijapetrova/Code/calendar-assistant/config/scripts/run-quantum-digest.sh /Users/marijapetrova/Code/calendar-assistant/config/scripts/digest-ai.env
   ```

## Sources

- ScienceDaily — Quantum Computing  
- Quanta Magazine — Physics  
- Red Hat Blog  

Articles mentioning IBM, Red Hat, Qiskit, RHEL, or OpenShift are ranked first. You can add or change feeds and scoring in `scripts/quantum_daily_digest.py`.
