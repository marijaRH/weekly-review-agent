#!/usr/bin/env python3
"""
Daily Quantum Computing Digest: top 3 news articles + LinkedIn post proposals.
Run at 9AM CET (e.g. via cron) to receive the digest by email.
"""

import html
import os
import re
import sys
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from time import mktime
from urllib.parse import urlparse

try:
    import feedparser
except ImportError:
    print("Install feedparser: pip install feedparser", file=sys.stderr)
    sys.exit(1)

# RSS feeds: quantum computing, physics, and IBM/Red Hat ecosystem
FEEDS = [
    "https://www.sciencedaily.com/rss/matter_energy/quantum_computing.xml",
    "https://www.quantamagazine.org/physics/feed/",
    "https://www.redhat.com/en/rss/blog",
]

RECIPIENT_ENV = "QUANTUM_DIGEST_RECIPIENT"
SENDER_ENV = "QUANTUM_DIGEST_SENDER"  # optional, defaults to recipient
# Optional: different topic/recipient for a second digest (use with alternate env file)
DIGEST_NAME_ENV = "DIGEST_NAME"  # e.g. "AI Digest" for subject line
DIGEST_FEEDS_ENV = "DIGEST_FEEDS"  # comma-separated URLs; overrides default FEEDS
DIGEST_TOPIC_KEYWORDS_ENV = "DIGEST_TOPIC_KEYWORDS"  # comma-separated; articles must match any
DIGEST_TOP_N_ENV = "DIGEST_TOP_N"  # number of articles (default 3)
# Gmail: use App Password (2FA required). Or set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
GMAIL_APP_PASSWORD_ENV = "GMAIL_APP_PASSWORD"
SMTP_HOST_ENV = "SMTP_HOST"
SMTP_PORT_ENV = "SMTP_PORT"
SMTP_USER_ENV = "SMTP_USER"
SMTP_PASSWORD_ENV = "SMTP_PASSWORD"
# Log of sent article URLs so we skip them (no repetition of news)
SENT_LOG_DAYS = 14  # skip articles sent in the last N days


def _get_sent_log_path():
    """Path to the sent-URLs log file (in script dir so it can be committed in CI)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, ".quantum-digest-sent.log")


def _load_recently_sent_urls(log_path, within_days=SENT_LOG_DAYS):
    """Return set of article URLs that were sent in the last within_days days."""
    if not os.path.isfile(log_path):
        return set()
    cutoff = (datetime.now(tz=timezone.utc) - timedelta(days=within_days)).date()
    seen = set()
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "\t" not in line:
                    continue
                date_str, url = line.split("\t", 1)
                try:
                    log_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if log_date >= cutoff:
                        seen.add(url.strip().rstrip("/"))
                except ValueError:
                    continue
    except OSError:
        pass
    return seen


def _append_sent_urls(log_path, urls):
    """Append today's sent URLs to the log. Trim old lines to keep file small."""
    if not urls:
        return
    now = datetime.now(tz=timezone.utc)
    today = now.strftime("%Y-%m-%d")
    cutoff = (now - timedelta(days=SENT_LOG_DAYS + 7)).strftime("%Y-%m-%d")
    lines_to_keep = []
    try:
        if os.path.isfile(log_path):
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "\t" in line and line.split("\t", 1)[0] >= cutoff:
                        lines_to_keep.append(line.rstrip("\n"))
    except OSError:
        pass
    with open(log_path, "w", encoding="utf-8") as f:
        for line in lines_to_keep:
            f.write(line + "\n")
        for url in urls:
            f.write(f"{today}\t{url.strip().rstrip('/')}\n")


def _get_feed_urls():
    """Feed list from env DIGEST_FEEDS (comma-separated) or default FEEDS."""
    raw = os.environ.get(DIGEST_FEEDS_ENV, "").strip()
    if raw:
        return [u.strip() for u in raw.split(",") if u.strip()]
    return FEEDS


def _get_topic_keywords():
    """Topic keywords from env, or default ['quantum']."""
    raw = os.environ.get(DIGEST_TOPIC_KEYWORDS_ENV, "").strip()
    if raw:
        return [k.strip().lower() for k in raw.split(",") if k.strip()]
    return ["quantum"]


def _get_top_n():
    """Number of articles from env (default 3)."""
    try:
        n = int(os.environ.get(DIGEST_TOP_N_ENV, "3").strip())
        return max(1, min(n, 20))
    except ValueError:
        return 3


def _matches_topic(entry, keywords):
    text = ((entry.get("title") or "") + " " + (entry.get("summary") or "")).lower()
    return any(kw in text for kw in keywords)


def fetch_entries(feed_urls=None):
    feed_urls = feed_urls or _get_feed_urls()
    entries = []
    for url in feed_urls:
        try:
            parsed = feedparser.parse(url)
            for e in parsed.entries:
                if not e:
                    continue
                title = (e.get("title") or "").strip()
                link = (e.get("link") or "").strip()
                summary = (e.get("summary") or e.get("description") or "").strip()
                # Strip HTML tags roughly
                if summary and "<" in summary:
                    summary = re.sub(r"<[^>]+>", " ", summary)
                    summary = " ".join(summary.split())
                published = e.get("published_parsed") or e.get("updated_parsed")
                if published:
                    try:
                        dt = datetime.fromtimestamp(mktime(published), tz=timezone.utc)
                    except Exception:
                        dt = datetime.now(timezone.utc)
                else:
                    dt = datetime.now(timezone.utc)
                if title and link:
                    entries.append({
                        "title": title,
                        "link": link,
                        "summary": (summary or "")[:500],
                        "published": dt,
                        "source": urlparse(url).netloc or url,
                    })
        except Exception as err:
            print(f"Warning: could not fetch {url}: {err}", file=sys.stderr)
    return entries


def _is_quantum_related(entry):
    text = (entry.get("title") or "") + " " + (entry.get("summary") or "")
    return "quantum" in text.lower()


def _topic_filter(entry):
    return _matches_topic(entry, _get_topic_keywords())


def _partnership_announcement_score(entry):
    """Higher = partnership / large announcement (vs pure R&D). Prefer deals, launches, enterprise."""
    text = ((entry.get("title") or "") + " " + (entry.get("summary") or "")).lower()
    score = 0
    # Strong signals: partnerships, deals, big announcements
    if any(w in text for w in ("partnership", "partners", "partners with", "collaboration", "collaborates")):
        score += 4
    if any(w in text for w in ("acquisition", "acquires", "acquired", "merger", "deal", "agreement", "signed")):
        score += 4
    if any(w in text for w in ("launches", "launch", "announces", "announced", "unveils", "unveil")):
        score += 3
    if any(w in text for w in ("strategic", "enterprise", "commercial", "deployment")):
        score += 2
    if any(w in text for w in ("funding", "investment", "invests", "billion", "million", "$")):
        score += 2
    # Slight down-rank for pure R&D phrasing (so partnership/announcement wins when close)
    if any(w in text for w in ("scientists discover", "research shows", "study finds", "paper published", "experiment shows")):
        score -= 1
    return max(0, score)


def _ibm_redhat_score(entry):
    """Higher = more relevant to IBM / Red Hat (prioritise pro-IBM/Red Hat news)."""
    text = ((entry.get("title") or "") + " " + (entry.get("summary") or "")).lower()
    score = 0
    if "ibm" in text or "qiskit" in text:
        score += 3
    if "red hat" in text or "redhat" in text or "rhel" in text or "openshift" in text:
        score += 3
    if "open source" in text or "open-source" in text:
        score += 1
    return score


def pick_top_n(entries, n=None):
    if n is None:
        n = _get_top_n()
    recently_sent = _load_recently_sent_urls(_get_sent_log_path())
    seen = set()
    unique = []
    for e in entries:
        key = (e["link"].rstrip("/"), e["title"][:80])
        if key in seen:
            continue
        url_norm = e["link"].strip().rstrip("/")
        if url_norm in recently_sent:
            continue  # skip so you get different news each day
        seen.add(key)
        unique.append(e)
    # Only topic-matching articles qualify; prefer partnership/large announcements, then IBM/Red Hat, then newest
    topic_matching = [e for e in unique if _topic_filter(e)]
    topic_matching.sort(
        key=lambda e: (
            _partnership_announcement_score(e),
            _ibm_redhat_score(e),
            e["published"],
        ),
        reverse=True,
    )
    return topic_matching[:n]


def _suggest_hashtags(article):
    """Suggest hashtags; add #IBMQuantum / #RedHat when relevant."""
    text = ((article.get("title") or "") + " " + (article.get("summary") or "")).lower()
    tags = ["#QuantumComputing"]
    if "ibm" in text or "qiskit" in text:
        tags.append("#IBMQuantum")
    if "red hat" in text or "redhat" in text or "rhel" in text or "openshift" in text:
        tags.append("#RedHat")
    return " ".join(tags)


def linkedin_proposal(article, index):
    """LinkedIn copy in Marija’s style: conversational, value-forward, hashtags, first person."""
    title = article["title"]
    link = article["link"]
    summary = article["summary"]
    hashtags = _suggest_hashtags(article)
    # Voice: first person, “Did you know” / value hook, short takeaway, personal CTA (matches Marija’s posts)
    hook_style = (
        f"Did you see this? {title}"
        if len(title) < 60
        else f"This one’s worth a read: {title[:55]}…"
    )
    takeaway = (summary[:260] + "…") if len(summary) > 260 else (summary or "—")
    cta = "Worth reading the full piece — link below. What would you add?"
    return f"""---
LinkedIn post #{index} (draft — your voice)
---
{hook_style}

{takeaway}

{cta}

{link}

{hashtags}
"""


def linkedin_proposal_html(article, index):
    """Same as linkedin_proposal but for inline HTML (single block)."""
    full = linkedin_proposal(article, index)
    lines = [l for l in full.splitlines() if not l.strip().startswith("---")]
    body_text = "\n".join(lines[1:])  # skip "LinkedIn post #N (draft...)"
    return html.escape(body_text).replace("\n", "<br>\n")


def _digest_title():
    return os.environ.get(DIGEST_NAME_ENV, "Quantum Digest").strip() or "Quantum Digest"


def build_email_html(articles):
    date_str = datetime.now().strftime("%A, %B %d, %Y")
    title = _digest_title()
    articles_html = []
    linkedin_section = []
    for i, a in enumerate(articles, 1):
        articles_html.append(
            f"""
            <div style="margin-bottom: 1.5em; padding-bottom: 1em; border-bottom: 1px solid #eee;">
              <h3 style="margin: 0 0 0.25em 0; font-size: 1.1em;">{i}. {a["title"]}</h3>
              <p style="margin: 0.25em 0; color: #444; font-size: 0.95em;">{a["summary"] or "—"}</p>
              <p style="margin: 0.5em 0 0 0;"><a href="{a["link"]}" style="color: #0066cc;">Read article</a></p>
            </div>
            """
        )
        draft_html = linkedin_proposal_html(a, i) if i <= 5 else ""
        if draft_html:
            linkedin_section.append(
                f"""
            <div style="margin-bottom: 1.2em; padding: 0.8em; background: #f8f9fa; border-radius: 6px;">
              <strong>Post #{i}</strong> — ready to paste
              <p style="margin: 0.5em 0 0 0; font-size: 0.95em; white-space: pre-wrap;">{draft_html}</p>
            </div>
            """
            )
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{title} — {date_str}</title></head>
<body style="font-family: system-ui, sans-serif; max-width: 600px; margin: 0 auto; padding: 1em;">
  <h1 style="font-size: 1.3em;">{title}</h1>
  <p style="color: #666;">{date_str} — Top {len(articles)} articles + LinkedIn post ideas</p>

  <h2 style="font-size: 1.1em;">Top {len(articles)} articles</h2>
  {"".join(articles_html)}

  <h2 style="font-size: 1.1em;">LinkedIn post proposals</h2>
  <p style="color: #555;">Drafts in your voice (conversational, value-forward). Prioritised: IBM &amp; Red Hat–friendly news.</p>
  {"".join(linkedin_section)}

  <p style="margin-top: 1.5em; font-size: 0.85em; color: #888;">{title}. Sources and topic set in digest config.</p>
</body>
</html>
"""


def build_email_plain(articles):
    date_str = datetime.now().strftime("%A, %B %d, %Y")
    title = _digest_title()
    lines = [
        f"{title} — {date_str}",
        "",
        f"TOP {len(articles)} ARTICLES",
        "---------------",
    ]
    for i, a in enumerate(articles, 1):
        lines.append(f"{i}. {a['title']}")
        lines.append(f"   {a['summary'] or '—'}")
        lines.append(f"   {a['link']}")
        lines.append("")
    lines.append("LINKEDIN POST PROPOSALS")
    lines.append("----------------------")
    for i, a in enumerate(articles[:5], 1):  # at most 5 LinkedIn drafts
        lines.append(linkedin_proposal(a, i))
    return "\n".join(lines)


def send_email(recipient, subject, body_html, body_plain, sender=None):
    sender = sender or recipient
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(body_plain, "plain", "utf-8"))
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    app_password = os.environ.get(GMAIL_APP_PASSWORD_ENV)
    smtp_host = os.environ.get(SMTP_HOST_ENV)
    smtp_port = int(os.environ.get(SMTP_PORT_ENV, "587"))
    smtp_user = os.environ.get(SMTP_USER_ENV)
    smtp_password = os.environ.get(SMTP_PASSWORD_ENV)

    if app_password:
        smtp_host = smtp_host or "smtp.gmail.com"
        smtp_port = smtp_port or 587
        smtp_user = smtp_user or sender
        smtp_password = smtp_password or app_password
    if not smtp_user or not smtp_password:
        print("Set GMAIL_APP_PASSWORD (or SMTP_USER + SMTP_PASSWORD) to send email.", file=sys.stderr)
        return False

    host = smtp_host or "smtp.gmail.com"
    port = smtp_port or 587
    context = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=context)
        server.login(smtp_user, smtp_password)
        server.sendmail(sender, [recipient], msg.as_string())
    return True


def main():
    recipient = os.environ.get(RECIPIENT_ENV)
    if not recipient:
        print(f"Set {RECIPIENT_ENV} to your email address.", file=sys.stderr)
        sys.exit(1)
    sender = os.environ.get(SENDER_ENV) or recipient

    entries = fetch_entries()
    top_n = _get_top_n()
    articles = pick_top_n(entries)
    if not articles:
        print("No articles found. Check RSS feeds and DIGEST_TOPIC_KEYWORDS.", file=sys.stderr)
        sys.exit(1)

    date_str = datetime.now().strftime("%Y-%m-%d")
    title = _digest_title()
    subject = f"{title} {date_str} — Top {len(articles)} + LinkedIn ideas"
    body_html = build_email_html(articles)
    body_plain = build_email_plain(articles)

    if send_email(recipient, subject, body_html, body_plain, sender):
        _append_sent_urls(_get_sent_log_path(), [a["link"] for a in articles])
        print(f"Digest sent to {recipient} ({len(articles)} articles).")
    else:
        # Write to stdout so user can pipe to mail or copy
        print("Sending skipped. Plain digest below:\n")
        print(body_plain)
        sys.exit(2)


if __name__ == "__main__":
    main()
