import subprocess
import json
import os

video_path = "out/lotr_fellowship_ch1_60fps.mp4"
thumbnail_path = "out/lotr_ch1_p1_refined.png"
title = "The Fellowship of the Ring - Book 1, Chapter 1 (Kinetic Audiobook & Vocabulary Gloss)"
description = """Full Book 1, Chapter 1 (A Long-expected Party) of The Fellowship of the Ring by J. R. R. Tolkien.

• Original narration by Rob Inglis
• 60 FPS calm kinetic typography (Max 3 lines per slide)
• Interlinear Vietnamese vocabulary gloss for C1/C2 advanced & literary words

Enjoy distraction-free reading!"""
tags = "the lord of the rings, fellowship of the ring, tolkien, audiobook, kinetic text, learn english, vocabulary gloss, jrr tolkien, a long expected party"

uploader_bin = os.path.expanduser("~/.local/bin/youtube-uploader")

upload_cmd = [
    uploader_bin,
    "upload",
    "--profile", "main",
    "--json",
    "--title", title,
    "--description", description,
    "--tags", tags,
    "--privacy", "unlisted",
    video_path
]

if os.path.exists(thumbnail_path):
    upload_cmd.extend(["--thumbnail", thumbnail_path])

print(f"🚀 Uploading LOTR Chapter 1 (Title len: {len(title)} chars)...", flush=True)
res = subprocess.run(upload_cmd, capture_output=True, text=True)

print("Output:", res.stdout, flush=True)
if res.stderr:
    print("Stderr:", res.stderr, flush=True)

try:
    data = json.loads(res.stdout)
    video_id = data.get("id") or data.get("video_id")
    if video_id:
        print(f"\n🎉 LIVE YouTube Video URL: https://youtu.be/{video_id}", flush=True)
except Exception as e:
    pass
