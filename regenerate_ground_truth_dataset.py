import json
import os
import subprocess

with open("chapters_manifest_ground_truth.json", "r") as f:
    manifest = json.load(f)

with open("full_audiobook_words.json", "r") as f:
    words = json.load(f)

AUDIO_SRC = "hitchhiker_raw.webm"
OUT_AUDIO_DIR = "chapters_audio"
OUT_DATA_DIR = "chapters_data"
PUBLIC_AUDIO_DIR = "public/chapters_audio"

os.makedirs(OUT_AUDIO_DIR, exist_ok=True)
os.makedirs(OUT_DATA_DIR, exist_ok=True)
os.makedirs(PUBLIC_AUDIO_DIR, exist_ok=True)

MAX_WORDS = 9
MAX_DURATION = 3.8

total_book_end = words[-1]["end"]

print("⚡ Re-slicing 36 ground-truth chapters from EPUB alignment...")

for idx, ch in enumerate(manifest):
    num = ch["chapter_num"]
    title = ch["title"]
    start_t = ch["start_time_seconds"]
    end_t = ch["end_time_seconds"]
    duration = end_t - start_t
    
    file_slug = f"chapter_{num:02d}" if num > 0 else "chapter_00_prologue"
    audio_path = os.path.join(OUT_AUDIO_DIR, f"{file_slug}.mp3")
    public_audio_path = os.path.join(PUBLIC_AUDIO_DIR, f"{file_slug}.mp3")
    subtitles_path = os.path.join(OUT_DATA_DIR, f"{file_slug}.json")
    
    # 1. Re-slice audio with exact timestamps
    cmd = [
        "ffmpeg", "-y", "-ss", str(start_t), "-i", AUDIO_SRC,
        "-t", str(duration), "-c:a", "libmp3lame", "-q:a", "2",
        audio_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["cp", audio_path, public_audio_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Extract words falling inside this exact chapter range and re-base time to 0.0s
    ch_words = []
    for w in words:
        if start_t <= w["start"] < end_t:
            ch_words.append({
                "text": w["text"],
                "start": round(w["start"] - start_t, 3),
                "end": round(w["end"] - start_t, 3)
            })

    # Group into rhythmic visual cards
    pages = []
    page_id = 0
    current_words = []
    current_start = 0.0

    for w_info in ch_words:
        w_text = w_info["text"].strip()
        if not w_text:
            continue
        w_start = w_info["start"]
        w_end = w_info["end"]

        if not current_words:
            current_start = w_start
            
        current_words.append(w_info)
        
        has_period = any(p in w_text for p in [".", "?", "!", ";", "—", ":"])
        has_comma = "," in w_text
        card_dur = w_end - current_start
        
        should_break = False
        if has_period and len(current_words) >= 4:
            should_break = True
        elif has_comma and len(current_words) >= 7:
            should_break = True
        elif len(current_words) >= MAX_WORDS or card_dur >= MAX_DURATION:
            should_break = True
            
        if should_break:
            pages.append({
                "id": page_id,
                "startTime": current_start,
                "endTime": w_end,
                "fullText": " ".join([w["text"] for w in current_words]),
                "words": current_words
            })
            page_id += 1
            current_words = []

    if current_words:
        pages.append({
            "id": page_id,
            "startTime": current_start,
            "endTime": current_words[-1]["end"],
            "fullText": " ".join([w["text"] for w in current_words]),
            "words": current_words
        })

    with open(subtitles_path, "w") as f:
        json.dump(pages, f, indent=2)

    ch["card_count"] = len(pages)
    ch["word_count"] = len(ch_words)
    ch["rendered"] = False
    ch["public_audio"] = f"chapters_audio/{file_slug}.mp3"

    print(f"  ✅ {title:12s} | {ch['duration_formatted']} | {len(ch_words):5d} words | {len(pages):3d} cards | '{ch['opening_text'][:40]}...'")

# Overwrite chapters_manifest.json with Ground Truth
with open("chapters_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("\n🎉 Ground-Truth Chapter Dataset Ready!")
