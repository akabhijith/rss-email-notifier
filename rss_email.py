#!/usr/bin/env python3


import feedparser
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASS")
YOUR_EMAIL = os.getenv("YOUR_EMAIL")  # Generate at myaccount.google.com/apppasswords
FEEDS = [
    'https://bughunters.google.com/feed/en',
    'https://engineering.fb.com/feed/',
]



SEEN_FILE = "seen.json" #storing seen items to make sure we only get new items

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f)

def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_USER
    msg["To"] = YOUR_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(GMAIL_USER, GMAIL_APP_PASS)
    server.sendmail(GMAIL_USER, YOUR_EMAIL, msg.as_string())
    server.quit()

def main():
    print("🔁 Checking feeds for NEW items...\n")
    seen = load_seen()
    changed = False

    for url in FEEDS:
        print(f"Feed: {url}")
        feed = feedparser.parse(url)
        title = getattr(feed.feed, "title", "No title")
        print(f"  Title: {title}")
        print(f"  Entries: {len(feed.entries)}")

        for entry in feed.entries:
            # Build a stable ID for each item
            entry_id = getattr(entry, "id", None) or getattr(entry, "link", None)
            if not entry_id:
                continue

            if entry_id in seen:
                continue  # already read so dont need the notif

            # Mark as seen BEFORE sending to avoid dupes on failure loops
            seen[entry_id] = True
            changed = True

            entry_title = getattr(entry, "title", "No title")
            summary = getattr(entry, "summary", "")[:500]

            body = f"{summary}\n\nRead more: {entry.link}"
            subject = f"[RSS] {entry_title}"

            print(f"  ✉️ New item -> emailing: {entry_title[:60]}...")
            try:
                send_email(subject, body)
                print(f"  ✅ Email sent")
            except Exception as e:
                print(f"  ❌ Email failed: {e}")

        print()

    if changed:
        save_seen(seen)
        print("✅ seen.json updated")
    else:
        print("No new items found.")

if __name__ == "__main__":
    main()
