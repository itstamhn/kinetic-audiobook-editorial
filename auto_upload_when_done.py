import subprocess
import time
import os
import sys
import json

video_path = sys.argv[1] if len(sys.argv) > 1 else "out/brave_new_world_ch1_full_60fps.mp4"
thumbnail_path = sys.argv[2] if len(sys.argv) > 2 else "out/full_ch1_p1.png"
title = sys.argv[3] if len(sys.argv) > 3 else "Audiobook - Chapter 1 (Full Audiobook & Interlinear Vocabulary Gloss)"
description = sys.argv[4] if len(sys.argv) > 4 else """Full Chapter 1 with synchronized narration, 60 FPS calm kinetic typography (Max 3 lines per slide), and interlinear Vietnamese vocabulary gloss for C1/C2 advanced words.

Enjoy distraction-free reading!"""
tags = sys.argv[5] if len(sys.argv) > 5 else "audiobook, kinetic text, english literature, learn english, tieng anh, tu vung tieng anh"

print(f"⏳ Monitoring video render completion for: {video_path}...", flush=True)

# Wait until video exists and is no longer being written
last_size = -1
while True:
    if os.path.exists(video_path):
        size = os.path.getsize(video_path)
        # Check if remotion render process is still active
        props_name = os.path.basename(video_path).replace(".mp4", "")
        check_proc = subprocess.run(["pgrep", "-f", "remotion render"], capture_output=True, text=True)
        if not check_proc.stdout.strip() and size > 1000000 and size == last_size:
            print(f"🎉 Render verified complete! File size: {size / (1024*1024):.2f} MB", flush=True)
            break
        last_size = size
    time.sleep(10)

uploader_bin = os.path.expanduser("~/.local/bin/youtube-uploader")

upload_cmd = [
    uploader_bin,
    "--profile", "main",
    "--json",
    "upload",
    "--title", title,
    "--description", description,
    "--tags", tags,
    "--privacy", "unlisted",
    video_path
]

if os.path.exists(thumbnail_path):
    upload_cmd.extend(["--thumbnail", thumbnail_path])

res = subprocess.run(upload_cmd, capture_output=True, text=True)
print("Upload output:", flush=True)
print(res.stdout, flush=True)
if res.stderr:
    print("Stderr:", res.stderr, flush=True)

try:
    data = json.loads(res.stdout)
    video_id = data.get("id") or data.get("video_id")
    if video_id:
        print(f"\n✨ YouTube Video Live URL: https://youtu.be/{video_id}", flush=True)
except Exception as e:
    pass
