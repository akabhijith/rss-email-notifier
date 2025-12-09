import feedparser
import json

FEEDS = [
    "https://bughunters.google.com/feed/en",
    "https://engineering.fb.com/feed/",
    "https://feeds.feedburner.com/NetflixTechBlog",
]

print("🔍 Scanning feeds to prime seen.json...")
seen = {}

for url in FEEDS:
    print(f"Scanning {url}...")
    feed = feedparser.parse(url)
    count = 0
    for entry in feed.entries:
        entry_id = getattr(entry, "id", None) or getattr(entry, "link", None)
        if entry_id:
            seen[entry_id] = True
            count += 1
    print(f"  Marked {count} existing posts as seen")

# Save
with open("seen.json", "w") as f:
    json.dump(seen, f)

print(f"✅ Created seen.json with {len(seen)} posts. Future posts only now!")
