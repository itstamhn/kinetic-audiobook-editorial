import json
import re
import os
import subprocess

with open("full_audiobook_words.json", "r") as f:
    words = json.load(f)

print(f"Loaded {len(words)} words.")

# Let us find where "Chapter" occurs or locate chapter breaks
chapter_hits = []

for idx, w in enumerate(words):
    text = w["text"].strip().lower()
    # Check if word is "chapter"
    if "chapter" in text or text == "chapter":
        next_words = " ".join([words[j]["text"] for j in range(idx, min(idx + 5, len(words)))])
        chapter_hits.append({
            "index": idx,
            "start": w["start"],
            "snippet": next_words
        })

print(f"\nFound {len(chapter_hits)} potential chapter mentions:")
for ch in chapter_hits[:40]:
    mins = ch['start'] / 60
    print(f"  [{mins:05.2f}m / {ch['start']:.1f}s] {ch['snippet']}")

