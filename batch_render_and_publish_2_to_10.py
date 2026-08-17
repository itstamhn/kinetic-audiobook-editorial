import os
import sys
import json
import subprocess
import time
import re

MANIFEST_PATH = "chapters_manifest.json"
GT_MANIFEST_PATH = "chapters_manifest_ground_truth.json"
VAULT_NOTE_PATH = "/Users/tamhn/Documents/tamhome/Notes/The Hitchhiker's Guide to the Galaxy - Kinetic Typography Audiobook Series.md"

# Descriptive subtitles for ground truth chapters
CHAPTER_TITLES = {
    0: "Prologue: Far Out in the Uncharted Backwaters",
    1: "Chapter 1: The House Stood on a Slight Rise",
    2: "Chapter 2: The Pan Galactic Gargle Blaster",
    3: "Chapter 3: Something Moving Quietly Through the Ionosphere",
    4: "Chapter 4: Damogran & The Heart of Gold",
    5: "Chapter 5: Prostetnic Vogon Jeltz & The Poetry",
    6: "Chapter 6: Inside the Vogon Air Lock",
    7: "Chapter 7: Vogon Poetry Appreciation & The Airlock",
    8: "Chapter 8: The Hitchhiker's Guide to the Galaxy",
    9: "Chapter 9: The Impossible Rescue",
    10: "Chapter 10: The Infinite Improbability Drive"
}

with open(GT_MANIFEST_PATH, "r") as f:
    gt_manifest = json.load(f)

# Load existing manifest to preserve existing uploaded URLs
existing_urls = {
    0: "https://youtu.be/KMeHv_b1HQ8",
    1: "https://youtu.be/I1UZTJdat3A",
    2: "https://youtu.be/XkZTA12y8oc"
}

for ch in gt_manifest:
    num = ch["chapter_num"]
    ch["descriptive_title"] = CHAPTER_TITLES.get(num, f"Chapter {num:02d}")
    if num in existing_urls:
        ch["youtube_url"] = existing_urls[num]
        ch["rendered"] = True

with open(MANIFEST_PATH, "w") as f:
    json.dump(gt_manifest, f, indent=2)

def update_obsidian_note(manifest):
    if not os.path.exists(VAULT_NOTE_PATH):
        return
    with open(VAULT_NOTE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Rebuild Markdown Table
    table_lines = [
        "| Chapter | Title | Duration | Status | YouTube Video Link |\n",
        "| :--- | :--- | :--- | :--- | :--- |\n"
    ]
    
    for ch in manifest:
        num = ch["chapter_num"]
        num_str = f"{num:02d}"
        t = ch.get("descriptive_title", f"Chapter {num_str}")
        dur = ch.get("duration_formatted", "")
        yt = ch.get("youtube_url")
        
        if yt:
            status = "✅ Published"
            link = f"[{yt}]({yt})"
        elif ch.get("rendering"):
            status = "⏳ Rendering..."
            link = "*In Progress*"
        else:
            status = "⏳ Queued"
            link = "*In Queue*"
            
        table_lines.append(f"| **{num_str}** | *{t}* | `{dur}` | {status} | {link} |\n")
        
    # Replace table section in note
    new_content = []
    in_table = False
    table_inserted = False
    
    for line in lines:
        if line.startswith("| Chapter |"):
            in_table = True
            if not table_inserted:
                new_content.extend(table_lines)
                table_inserted = True
            continue
        if in_table:
            if line.startswith("|"):
                continue
            else:
                in_table = False
                new_content.append(line)
        else:
            new_content.append(line)
            
    with open(VAULT_NOTE_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_content)
    print("📝 Obsidian Vault Note Updated!")

# Update note now with ground-truth table
update_obsidian_note(gt_manifest)

# Chapters to process: 3 to 10
target_chapters = [ch for ch in gt_manifest if 3 <= ch["chapter_num"] <= 10]

print(f"\n🚀 Starting Pipeline for Chapters 3 to 10 ({len(target_chapters)} chapters)...\n")

for ch in target_chapters:
    num = ch["chapter_num"]
    file_slug = f"chapter_{num:02d}"
    title = ch["descriptive_title"]
    dur = ch["duration_formatted"]
    dur_sec = ch["duration_seconds"]
    audio_file = ch["audio_file"]
    subtitles_file = ch["subtitles_file"]
    output_mp4 = f"out/chapters/{file_slug}_epub_exact_60fps.mp4"
    props_path = f"chapters_data/{file_slug}_props.json"
    
    print(f"\n==========================================")
    print(f"🎬 Processing Chapter {num:02d}: {title} ({dur})")
    print(f"==========================================")
    
    # 1. Load subtitles and save Props
    with open(subtitles_file, "r") as sf:
        subs = json.load(sf)
        
    props = {
        "headerTitle": f"DOUGLAS ADAMS • THE HITCHHIKER'S GUIDE TO THE GALAXY • CHAPTER {num}",
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
        
    ch["rendering"] = True
    update_obsidian_note(gt_manifest)
    
    # 2. Render Video
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
    render_time = time.time() - t0
    mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"✅ Rendered Chapter {num:02d} in {render_time:.1f}s ({mb:.1f} MB)!")
    
    # 3. Upload to YouTube as Unlisted
    print(f"📤 Uploading Chapter {num:02d} to YouTube (Unlisted)...")
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
    
    upload_res = subprocess.run(cmd_upload, check=True, text=True, capture_output=True)
    
    # Parse video URL / ID from output
    yt_url = None
    vid_match = re.search(r"https://youtu\.be/([a-zA-Z0-9_-]+)", upload_res.stdout)
    if vid_match:
        yt_url = vid_match.group(0)
        ch["video_id"] = vid_match.group(1)
    else:
        # Check JSON block
        json_match = re.search(r"\{.*\}", upload_res.stdout, re.DOTALL)
        if json_match:
            try:
                d = json.loads(json_match.group(0))
                yt_url = d.get("url")
                ch["video_id"] = d.get("video_id")
            except Exception:
                pass
                
    if not yt_url:
        print(f"⚠️ Raw upload output:\n{upload_res.stdout}")
        # Fallback regex
        raw_vid = re.search(r"video/([a-zA-Z0-9_-]+)", upload_res.stdout)
        if raw_vid:
            yt_url = f"https://youtu.be/{raw_vid.group(1)}"
            ch["video_id"] = raw_vid.group(1)
            
    print(f"🎉 Chapter {num:02d} Published: {yt_url}")
    
    ch["youtube_url"] = yt_url
    ch["rendered"] = True
    ch["rendering"] = False
    
    # Save manifest
    with open(MANIFEST_PATH, "w") as f:
        json.dump(gt_manifest, f, indent=2)
        
    # Update Obsidian Note
    update_obsidian_note(gt_manifest)
    print(f"✅ Finished Chapter {num:02d}!")

print("\n🎉🎉 ALL CHAPTERS 2 TO 10 SUCCESSFULLY RENDERED & PUBLISHED!")
