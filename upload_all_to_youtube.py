import os
import sys
import json
import subprocess
import time

MANIFEST_PATH = "chapters_manifest.json"

if not os.path.exists(MANIFEST_PATH):
    print("❌ chapters_manifest.json not found!")
    sys.exit(1)

with open(MANIFEST_PATH, "r") as f:
    manifest = json.load(f)

# Check client_secret.json
config_secret = os.path.expanduser("~/.config/youtube-uploader/client_secret.json")
if not os.path.exists(config_secret):
    print(f"⚠️ Warning: {config_secret} not found.")
    print("Please place your Google Cloud OAuth client secret JSON at:")
    print(f"  {config_secret}")
    print("\nThen run authorization once in your browser:")
    print("  youtube-uploader auth --profile main --select-account")
    print("-------------------------------------------------------")

def upload_chapter(ch, profile="main", privacy="unlisted"):
    ch_num = ch["chapter_num"]
    title = ch["title"]
    file_slug = f"chapter_{ch_num:02d}" if ch_num > 0 else "chapter_00_prologue"
    video_path = f"out/chapters/{file_slug}_60fps.mp4"

    # Fallback to single chapter render if full chapter 1 path
    if ch_num == 1 and not os.path.exists(video_path):
        if os.path.exists("out/hitchhiker_chapter1_complete_60fps.mp4"):
            video_path = "out/hitchhiker_chapter1_complete_60fps.mp4"

    if not os.path.exists(video_path):
        print(f"⏩ Video file not found for {title}: {video_path} (skipping)")
        return None

    yt_title = f"The Hitchhiker's Guide to the Galaxy - {title} [Audiobook Kinetic Typography]"
    # YouTube titles are max 100 characters
    if len(yt_title) > 95:
        yt_title = f"Hitchhiker's Guide to the Galaxy - {title}"[:95]

    description = (
        f"The Hitchhiker's Guide to the Galaxy by Douglas Adams\n"
        f"Narration: Stephen Fry\n"
        f"Section: {title}\n"
        f"Duration: {ch['duration_formatted']} | {ch['word_count']} words\n\n"
        f"Generated with 60 FPS Kinetic Typography Studio powered by Groq Whisper and Remotion.\n"
        f"Privacy: Unlisted"
    )

    tags = "audiobook,douglas adams,the hitchhikers guide to the galaxy,kinetic typography,stephen fry,sci-fi,groq whisper"

    cmd = [
        "youtube-uploader", "upload", video_path,
        "--profile", profile,
        "--title", yt_title,
        "--description", description,
        "--privacy", privacy,
        "--category", "27", # Education / Literature
        "--tags", tags,
        "--chunk-size-mb", "64"
    ]

    print(f"\n📤 Uploading '{title}' ({ch['duration_formatted']}) as {privacy.upper()}...")
    try:
        res = subprocess.run(cmd, check=True, text=True, capture_output=True)
        out = res.stdout
        print(out)
        return out
    except subprocess.CalledProcessError as e:
        print(f"❌ Upload failed: {e.stderr}")
        return None

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Upload rendered chapter videos to YouTube as unlisted")
    parser.add_argument("--profile", default="main", help="Auth profile name")
    parser.add_argument("--privacy", default="unlisted", choices=["unlisted", "private", "public"], help="Video privacy")
    parser.add_argument("--chapter", type=int, nargs="+", help="Specific chapter numbers to upload")
    parser.add_argument("--all", action="store_true", help="Upload all available rendered videos")
    args = parser.parse_args()

    targets = manifest
    if args.chapter is not None:
        targets = [c for c in manifest if c["chapter_num"] in args.chapter]

    print(f"🎬 Ready to upload {len(targets)} chapter videos to YouTube ({args.privacy})...\n")

    uploaded = []
    for ch in targets:
        res = upload_chapter(ch, profile=args.profile, privacy=args.privacy)
        if res:
            uploaded.append(ch["title"])

    print(f"\n🎉 Finished uploading {len(uploaded)} / {len(targets)} chapters!")
