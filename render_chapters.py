import os
import sys
import json
import subprocess
import argparse
import time

with open("chapters_manifest.json", "r") as f:
    manifest = json.load(f)

parser = argparse.ArgumentParser(description="Render Hitchhiker Guide chapters as kinetic typography videos")
parser.add_argument("--all", action="store_true", help="Render all chapters in the book")
parser.add_argument("--chapter", type=int, nargs="+", help="Specific chapter numbers to render")
parser.add_argument("--start", type=int, default=0, help="Starting chapter index")
parser.add_argument("--end", type=int, default=35, help="Ending chapter index")
parser.add_argument("--concurrency", type=int, default=8, help="Remotion render concurrency")

args = parser.parse_args()

os.makedirs("out/chapters", exist_ok=True)

# Determine chapters to render
if args.chapter is not None:
    target_chapters = [c for c in manifest if c["chapter_num"] in args.chapter]
elif args.all:
    target_chapters = manifest
else:
    target_chapters = [c for c in manifest if args.start <= c["chapter_num"] <= args.end]

print(f"🎬 Queueing {len(target_chapters)} chapters for rendering...\n")

for idx, ch in enumerate(target_chapters):
    ch_num = ch["chapter_num"]
    title = ch["title"]
    duration = ch["duration_seconds"]
    file_slug = f"chapter_{ch_num:02d}" if ch_num > 0 else "chapter_00_prologue"
    subtitles_path = f"chapters_data/{file_slug}.json"
    audio_file = f"chapters_audio/{file_slug}.mp3"
    output_mp4 = f"out/chapters/{file_slug}_60fps.mp4"

    print(f"[{idx+1}/{len(target_chapters)}] 🚀 Rendering '{title}' ({ch['duration_formatted']})...")
    t0 = time.time()

    # Load chapter subtitles
    with open(subtitles_path, "r") as sf:
        ch_subtitles = json.load(sf)

    # Prepare props
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

    # Remotion render command
    cmd = [
        "npx", "remotion", "render",
        "src/index.ts",
        "Universal-Kinetic-Chapter",
        output_mp4,
        f"--props={props_json_file}",
        "--concurrency", str(args.concurrency)
    ]

    try:
        subprocess.run(cmd, check=True)
        elapsed = time.time() - t0
        file_size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
        print(f"  ✅ Completed in {elapsed:.1f}s | Output: {output_mp4} ({file_size_mb:.1f} MB)\n")
        ch["rendered"] = True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error rendering {title}: {e}\n")

with open("chapters_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("\n🎉 Batch rendering complete!")
