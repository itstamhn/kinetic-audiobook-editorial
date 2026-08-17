import os
import sys
import json
import subprocess
import time
from datetime import datetime

MANIFEST_PATH = "chapters_manifest.json"
VAULT_NOTE_PATH = "/Users/tamhn/Documents/tamhome/Notes/The Hitchhiker's Guide to the Galaxy - Kinetic Typography Audiobook Series.md"
OUT_VIDEO_DIR = "out/chapters"
os.makedirs(OUT_VIDEO_DIR, exist_ok=True)

def load_manifest():
    with open(MANIFEST_PATH, "r") as f:
        return json.load(f)

def save_manifest(manifest):
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

def update_obsidian_note(manifest):
    total_chapters = len(manifest)
    uploaded_count = sum(1 for c in manifest if c.get("youtube_url"))
    rendered_count = sum(1 for c in manifest if c.get("rendered"))

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    md = [
        "---",
        "title: \"The Hitchhiker's Guide to the Galaxy - Kinetic Typography Audiobook Series\"",
        "author: \"Douglas Adams\"",
        "narrator: \"Stephen Fry\"",
        f"updated: {now_str}",
        "tags:",
        "  - youtube",
        "  - audiobook",
        "  - kinetic-typography",
        "  - douglas-adams",
        "  - projects",
        "---",
        "",
        "# 🌌 The Hitchhiker's Guide to the Galaxy &bull; Kinetic Typography Video Series",
        "",
        "> [!INFO]",
        "> **Project:** Full 4.19-hour Douglas Adams audiobook converted into a 60 FPS 1080p kinetic typography video series.",
        f"> **Published to YouTube (Unlisted):** `{uploaded_count} / {total_chapters} Chapters`",
        f"> **Rendered Locally:** `{rendered_count} / {total_chapters} Videos`",
        "",
        "## 📺 Published YouTube Chapter Links",
        "",
        "| Chapter | Title | Duration | Status | YouTube Video Link |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]

    for ch in manifest:
        ch_num = ch["chapter_num"]
        title = ch["title"]
        dur = ch["duration_formatted"]
        yt_url = ch.get("youtube_url")

        if yt_url:
            status = "✅ Published"
            link = f"[{yt_url}]({yt_url})"
        elif ch.get("rendered"):
            status = "🎬 Rendered (Pending Upload)"
            link = "*Pending Upload*"
        else:
            status = "⏳ Rendering..."
            link = "*In Queue*"

        md.append(f"| **{ch_num:02d}** | *{title}* | `{dur}` | {status} | {link} |")

    md.extend([
        "",
        "---",
        "",
        "## 🛠️ Technical Specifications",
        "- **Resolution:** 1920 × 1080 (16:9 YouTube Widescreen)",
        "- **Framerate:** 60 FPS interpolated",
        "- **Typography:** *Playfair Display* (Editorial Serif) with dynamic RGB weight & color transitions",
        "- **Audio Alignment Engine:** Groq Whisper (`whisper-large-v3-turbo`) with word-level millisecond timestamps",
        "- **Rendering Stack:** Remotion 4.0 + Node.js + Python",
        "- **Uploader CLI:** `aryan877/youtube-uploader` (Google OAuth)",
        "",
        "## 📂 Local Files",
        "- **Studio Interface:** `file:///Users/tamhn/Documents/tamhome/kinetic-text-video/index.html`",
        "- **Rendered MP4s:** `/Users/tamhn/Documents/tamhome/kinetic-text-video/out/chapters/`",
        "- **Audio Slices:** `/Users/tamhn/Documents/tamhome/kinetic-text-video/chapters_audio/`",
        "- **Timestamp Data:** `/Users/tamhn/Documents/tamhome/kinetic-text-video/chapters_data/`"
    ])

    with open(VAULT_NOTE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"📝 Updated Obsidian Note: {VAULT_NOTE_PATH}")

def render_chapter(ch):
    ch_num = ch["chapter_num"]
    title = ch["title"]
    duration = ch["duration_seconds"]
    file_slug = f"chapter_{ch_num:02d}" if ch_num > 0 else "chapter_00_prologue"
    subtitles_path = f"chapters_data/{file_slug}.json"
    audio_file = f"chapters_audio/{file_slug}.mp3"
    output_mp4 = f"out/chapters/{file_slug}_60fps.mp4"

    if os.path.exists(output_mp4) and os.path.getsize(output_mp4) > 1024 * 1024:
        ch["rendered"] = True
        return output_mp4

    print(f"\n🎬 Rendering {title} ({ch['duration_formatted']})...")
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

    subprocess.run(cmd, check=True)
    ch["rendered"] = True
    return output_mp4

def upload_to_youtube(ch, video_path):
    title = ch["title"]
    yt_title = f"The Hitchhiker's Guide to the Galaxy - {title} [Audiobook Kinetic Typography]"
    if len(yt_title) > 95:
        yt_title = f"Hitchhiker's Guide to the Galaxy - {title}"[:95]

    description = (
        f"The Hitchhiker's Guide to the Galaxy by Douglas Adams (Narrated by Stephen Fry).\n"
        f"Section: {title}\n"
        f"Duration: {ch['duration_formatted']} | {ch['word_count']} words\n\n"
        f"Full 60 FPS kinetic typography visualization generated with Groq Whisper and Remotion.\n"
        f"Privacy: Unlisted"
    )

    tags = "audiobook,douglas adams,the hitchhikers guide to the galaxy,kinetic typography,stephen fry,sci-fi"

    cmd = [
        "youtube-uploader", "upload", video_path,
        "--profile", "main",
        "--title", yt_title,
        "--description", description,
        "--privacy", "unlisted",
        "--category", "27",
        "--tags", tags,
        "--chunk-size-mb", "64",
        "--json"
    ]

    print(f"📤 Uploading {title} to YouTube as Unlisted...")
    res = subprocess.run(cmd, check=True, text=True, capture_output=True)
    try:
        data = json.loads(res.stdout)
        yt_url = data.get("url")
        video_id = data.get("video_id")
        ch["youtube_url"] = yt_url
        ch["video_id"] = video_id
        print(f"  🎉 Uploaded: {yt_url}")
        return yt_url
    except Exception as e:
        print(f"  ⚠️ Could not parse upload JSON: {res.stdout}")
        return None

if __name__ == "__main__":
    # Add initial published videos from earlier upload
    known_uploads = {
        0: ("https://youtu.be/KMeHv_b1HQ8", "KMeHv_b1HQ8"),
        1: ("https://youtu.be/u6FFaEhsNqk", "u6FFaEhsNqk"),
        2: ("https://youtu.be/xw5K_SCqt0I", "xw5K_SCqt0I"),
        3: ("https://youtu.be/UXaB3Sn_6mA", "UXaB3Sn_6mA"),
        4: ("https://youtu.be/c1A3q091zY0", "c1A3q091zY0"),
        5: ("https://youtu.be/o7muKefGKdk", "o7muKefGKdk"),
    }

    manifest = load_manifest()
    for ch in manifest:
        ch_num = ch["chapter_num"]
        if ch_num in known_uploads:
            ch["youtube_url"] = known_uploads[ch_num][0]
            ch["video_id"] = known_uploads[ch_num][1]
            ch["rendered"] = True

    save_manifest(manifest)
    update_obsidian_note(manifest)

    # Process each chapter sequentially: render -> upload -> sync note
    for ch in manifest:
        ch_num = ch["chapter_num"]
        title = ch["title"]

        if ch.get("youtube_url"):
            print(f"⏩ Already on YouTube: {title} ({ch['youtube_url']})")
            continue

        try:
            video_path = render_chapter(ch)
            save_manifest(manifest)
            update_obsidian_note(manifest)

            upload_to_youtube(ch, video_path)
            save_manifest(manifest)
            update_obsidian_note(manifest)
        except Exception as e:
            print(f"❌ Error processing {title}: {e}")

    print("\n🎉 ALL CHAPTERS PROCESSED AND PUBLISHED TO YOUTUBE!")
    update_obsidian_note(manifest)
