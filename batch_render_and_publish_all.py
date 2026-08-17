import os
import sys
import json
import subprocess
import time
import re

MANIFEST_PATH = "chapters_manifest.json"
GT_MANIFEST_PATH = "chapters_manifest_ground_truth.json"
VAULT_NOTE_PATH = "/Users/tamhn/Documents/tamhome/Notes/The Hitchhiker's Guide to the Galaxy - Kinetic Typography Audiobook Series.md"

with open(GT_MANIFEST_PATH, "r") as f:
    manifest = json.load(f)

# Load already published URLs from manifest if present
if os.path.exists(MANIFEST_PATH):
    try:
        with open(MANIFEST_PATH, "r") as mf:
            old = json.load(mf)
            for old_ch in old:
                num = old_ch["chapter_num"]
                if old_ch.get("youtube_url"):
                    target = next((c for c in manifest if c["chapter_num"] == num), None)
                    if target:
                        target["youtube_url"] = old_ch["youtube_url"]
                        target["rendered"] = True
    except Exception as e:
        print(f"Note: {e}")

def update_manifest():
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

update_manifest()

# Process all un-rendered chapters
remaining = [ch for ch in manifest if not ch.get("youtube_url")]

print(f"🎬 Found {len(remaining)} chapters remaining to render & publish!")

for ch in remaining:
    num = ch["chapter_num"]
    file_slug = f"chapter_{num:02d}" if num > 0 else "chapter_00_prologue"
    title = ch.get("title", f"Chapter {num:02d}")
    dur = ch["duration_formatted"]
    dur_sec = ch["duration_seconds"]
    audio_file = ch["audio_file"]
    subtitles_file = ch["subtitles_file"]
    output_mp4 = f"out/chapters/{file_slug}_epub_exact_60fps.mp4"
    props_path = f"chapters_data/{file_slug}_props.json"
    
    print(f"\n==========================================")
    print(f"🎬 Starting {title} ({dur} | {ch['word_count']} words)...")
    print(f"==========================================")
    
    with open(subtitles_file, "r") as sf:
        subs = json.load(sf)
        
    props = {
        "headerTitle": f"DOUGLAS ADAMS • THE HITCHHIKER'S GUIDE TO THE GALAXY • {title.upper()}",
        "totalDurationSeconds": dur_sec,
        "audioFile": audio_file,
        "subtitles": subs,
        "primaryColor": "#111111",
        "mutedColor": "#c8c8c8",
        "backgroundColor": "#faf9f6",
        "fontFamily": "Playfair Display, Georgia, Garamond, serif",
        "mode": "cumulative"
    }
    
    with open(props_path, "w") as pf:
        json.dump(props, pf)
        
    # Render
    t0 = time.time()
    cmd_render = [
        "npx", "remotion", "render",
        "src/index.ts",
        "Universal-Kinetic-Chapter",
        output_mp4,
        f"--props={props_path}",
        "--concurrency", "8"
    ]
    
    print(f"⏳ Rendering {output_mp4} at 60 FPS 1080p...")
    subprocess.run(cmd_render, check=True)
    mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"✅ Rendered in {time.time()-t0:.1f}s ({mb:.1f} MB)!")
    
    # Upload
    print(f"📤 Uploading to YouTube (Unlisted)...")
    yt_title = f"The Hitchhiker's Guide to the Galaxy - {title} [Kinetic Typography]"
    description = (
        f"The Hitchhiker's Guide to the Galaxy by Douglas Adams (Narrated by Stephen Fry).\n"
        f"{title} ({dur} | {ch['word_count']} words).\n\n"
        f"Ground-truth EPUB text alignment with 60 FPS kinetic typography visualization.\n"
        f"Privacy: Unlisted"
    )
    tags = f"audiobook,douglas adams,the hitchhikers guide to the galaxy,kinetic typography,stephen fry,chapter {num}"
    
    cmd_upload = [
        "youtube-uploader", "upload", output_mp4,
        "--profile", "main",
        "--title", yt_title,
        "--description", description,
        "--privacy", "unlisted",
        "--category", "27",
        "--tags", tags,
        "--chunk-size-mb", "64"
    ]
    
    res = subprocess.run(cmd_upload, check=True, text=True, capture_output=True)
    vid_match = re.search(r"https://youtu\.be/([a-zA-Z0-9_-]+)", res.stdout)
    if vid_match:
        yt_url = vid_match.group(0)
    else:
        raw_vid = re.search(r"video/([a-zA-Z0-9_-]+)", res.stdout)
        yt_url = f"https://youtu.be/{raw_vid.group(1)}" if raw_vid else "Uploaded"
        
    print(f"🎉 Published: {yt_url}")
    ch["youtube_url"] = yt_url
    ch["rendered"] = True
    update_manifest()
    
    # Try updating obsidian note if on same filesystem
    if os.path.exists(VAULT_NOTE_PATH):
        try:
            with open(VAULT_NOTE_PATH, "r", encoding="utf-8") as f:
                c = f.read()
            old_pattern = rf"\| \*\*{num:02d}\*\* \|.*"
            new_line = f"| **{num:02d}** | *{title}* | `{dur}` | ✅ Published | [{yt_url}]({yt_url}) |"
            c = re.sub(old_pattern, new_line, c)
            with open(VAULT_NOTE_PATH, "w", encoding="utf-8") as f:
                f.write(c)
        except Exception:
            pass

print("\n🎉 COMPLETE AUDIOBOOK PUBLISHED TO YOUTUBE!")
