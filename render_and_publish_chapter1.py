import os
import sys
import json
import subprocess
import time
import re

MANIFEST_PATH = "chapters_manifest.json"
VAULT_NOTE_PATH = "/Users/tamhn/Documents/tamhome/Notes/The Hitchhiker's Guide to the Galaxy - Kinetic Typography Audiobook Series.md"

with open(MANIFEST_PATH, "r") as f:
    manifest = json.load(f)

ch1 = next(c for c in manifest if c["chapter_num"] == 1)
title = ch1["title"]
dur = ch1["duration_formatted"]
output_mp4 = "out/chapters/chapter_01_epub_exact_60fps.mp4"

print(f"🎬 Starting Render of Complete Chapter 1 ({dur} | {ch1['word_count']} words)...")
t0 = time.time()

# 1. Render Video
cmd_render = [
    "npx", "remotion", "render",
    "src/index.ts",
    "Universal-Kinetic-Chapter",
    output_mp4,
    "--props=chapters_data/chapter_01_props.json",
    "--concurrency", "8"
]

subprocess.run(cmd_render, check=True)
render_time = time.time() - t0
mb = os.path.getsize(output_mp4) / (1024 * 1024)
print(f"✅ Rendered in {render_time:.1f}s ({mb:.1f} MB)!")

# 2. Upload to YouTube as Unlisted
print(f"📤 Uploading Chapter 1 to YouTube as Unlisted...")
yt_title = "The Hitchhiker's Guide to the Galaxy - Chapter 1: The House Stood on a Slight Rise"
description = (
    "The Hitchhiker's Guide to the Galaxy by Douglas Adams (Narrated by Stephen Fry).\n"
    "Chapter 1: The House Stood on a Slight Rise (19m 32s | 3,836 words)\n\n"
    "Complete ground-truth EPUB text alignment with 60 FPS kinetic typography visualization.\n"
    "Privacy: Unlisted"
)
tags = "audiobook,douglas adams,the hitchhikers guide to the galaxy,kinetic typography,stephen fry,chapter 1"

cmd_upload = [
    "youtube-uploader", "upload", output_mp4,
    "--profile", "main",
    "--title", yt_title,
    "--description", description,
    "--privacy", "unlisted",
    "--category", "27",
    "--tags", tags,
    "--chunk-size-mb", "64",
    "--json"
]

res = subprocess.run(cmd_upload, check=True, text=True, capture_output=True)
data = json.loads(res.stdout)
yt_url = data.get("url")
video_id = data.get("video_id")

print(f"🎉 Chapter 1 Published: {yt_url} (ID: {video_id})")

# 3. Update Manifest and Obsidian Note
ch1["youtube_url"] = yt_url
ch1["video_id"] = video_id
ch1["rendered"] = True
with open(MANIFEST_PATH, "w") as f:
    json.dump(manifest, f, indent=2)

# Update Obsidian note
with open(VAULT_NOTE_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Replace Chapter 1 line
old_line_pattern = r"\| \*\*01\*\* \|.*"
new_line = f"| **01** | *Chapter 1: The House Stood on a Slight Rise* | `{dur}` | ✅ Published | [{yt_url}]({yt_url}) |"
content = re.sub(old_line_pattern, new_line, content)

with open(VAULT_NOTE_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"📝 Updated Obsidian Note with Chapter 1 link!")
