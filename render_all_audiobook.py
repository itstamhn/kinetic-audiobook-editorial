import os
import sys
import json
import subprocess
import time

MANIFEST_PATH = "chapters_manifest.json"
OUT_VIDEO_DIR = "out/chapters"
os.makedirs(OUT_VIDEO_DIR, exist_ok=True)

with open(MANIFEST_PATH, "r") as f:
    manifest = json.load(f)

total_chapters = len(manifest)
print(f"🎬 Starting Full Hitchhiker's Guide Audiobook Video Production ({total_chapters} chapters)...")

t_start_all = time.time()

for idx, ch in enumerate(manifest):
    ch_num = ch["chapter_num"]
    title = ch["title"]
    duration = ch["duration_seconds"]
    file_slug = f"chapter_{ch_num:02d}" if ch_num > 0 else "chapter_00_prologue"
    subtitles_path = f"chapters_data/{file_slug}.json"
    audio_file = f"chapters_audio/{file_slug}.mp3"
    output_mp4 = f"out/chapters/{file_slug}_60fps.mp4"

    # Check if already rendered and valid
    if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 1024 * 1024:
        print(f"[{idx+1}/{total_chapters}] ⏩ Already rendered: {title} ({os.path.getsize(output_mp4)/(1024*1024):.1f} MB)")
        ch["rendered"] = True
        continue

    print(f"\n[{idx+1}/{total_chapters}] 🎥 Rendering {title} ({ch['duration_formatted']} | {ch['word_count']} words)...")
    t0 = time.time()

    if not os.path.exists(subtitles_path):
        print(f"  ❌ Missing subtitles file: {subtitles_path}")
        continue

    with open(subtitles_path, "r") as sf:
        ch_subtitles = json.load(sf)

    props = {
        "headerTitle": f"DOUGLAS ADAMS • THE HITCHHIKER'S GUIDE TO THE GALAXY • {title.upper()}",
        "totalDurationSeconds": duration,
        "audioFile": audio_file,
        "subtitles": ch_subtitles,
        "primaryColor": "#111111",
        "mutedColor": "#c8c8c8",
        "backgroundColor": "#faf9f6",
        "fontFamily": "Playfair Display, Georgia, Garamond, serif",
        "mode": "cumulative"
    }

    props_json_file = f"chapters_data/{file_slug}_props.json"
    with open(props_json_file, "w") as pf:
        json.dump(props, pf)

    cmd = [
        "npx", "remotion", "render",
        "src/index.ts",
        "Universal-Kinetic-Chapter",
        output_mp4,
        f"--props={props_json_file}",
        "--concurrency", "8"
    ]

    try:
        subprocess.run(cmd, check=True)
        elapsed = time.time() - t0
        mb = os.path.getsize(output_mp4) / (1024 * 1024)
        ch["rendered"] = True
        print(f"  ✅ Finished {title} in {elapsed:.1f}s ({mb:.1f} MB)")
    except Exception as e:
        print(f"  ❌ Error rendering {title}: {e}")

    # Persist progress after each chapter
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

total_elapsed = (time.time() - t_start_all) / 60
print(f"\n🎉 FULL AUDIOBOOK VIDEO RENDER COMPLETED in {total_elapsed:.1f} minutes!")
