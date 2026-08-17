import subprocess
import time
import os
import sys
import json

video_path = "out/brave_new_world_ch1_full_60fps.mp4"
thumbnail_path = "out/full_ch1_p1.png"

title = "Brave New World - Chapter 1 (Full Audiobook & Interlinear Vocabulary Gloss)"
description = """Full Chapter 1 of Brave New World by Aldous Huxley.
• Oxford British literary narration
• 60 FPS calm kinetic typography (Max 3 lines per slide)
• Interlinear Vietnamese vocabulary gloss for C1/C2 advanced words

Enjoy distraction-free reading!"""

tags = "brave new world, audiobook, aldous huxley, kinetic text, english literature, learn english, tieng anh, tu vung tieng anh"

print("⏳ Monitoring video render completion...")

# Wait until video exists and is no longer being written
last_size = -1
while True:
    if os.path.exists(video_path):
        size = os.path.getsize(video_path)
        # Check if remotion render process is still active
        check_proc = subprocess.run(["pgrep", "-f", "brave_new_world_ch1_full_60fps"], capture_output=True, text=True)
        if not check_proc.stdout.strip() and size > 1000000 and size == last_size:
            print(f"🎉 Render verified complete! File size: {size / (1024*1024):.2f} MB")
            break
        last_size = size
    time.sleep(10)

print("\n🚀 Uploading to YouTube via youtube-uploader (--profile main)...")

upload_cmd = [
    "/Users/tamhn/.local/bin/youtube-uploader",
    "--profile", "main",
    "--json",
    "upload",
    "--title", title,
    "--description", description,
    "--tags", tags,
    "--privacy", "unlisted",
    "--thumbnail", thumbnail_path,
    video_path
]

res = subprocess.run(upload_cmd, capture_output=True, text=True)
print("Upload output:")
print(res.stdout)
if res.stderr:
    print("Stderr:", res.stderr)

try:
    data = json.loads(res.stdout)
    video_id = data.get("id") or data.get("video_id")
    if video_id:
        print(f"\n✨ YouTube Video Live URL: https://youtu.be/{video_id}")
except Exception as e:
    pass
