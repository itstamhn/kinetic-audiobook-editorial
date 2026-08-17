import json
import os
import subprocess

with open("full_audiobook_words.json", "r") as f:
    words = json.load(f)

# Complete chapter start timestamps (in seconds)
CHAPTERS = [
    {"num": 0, "title": "Prologue: Far Out in the Uncharted Backwaters", "start": 7.0},
    {"num": 1, "title": "Chapter 1: The House Stood on a Slight Rise", "start": 189.9},
    {"num": 2, "title": "Chapter 2: None at All", "start": 661.7},
    {"num": 3, "title": "Chapter 3: Human Beings are Great Adapters", "start": 851.7},
    {"num": 4, "title": "Chapter 4: Zaphod Beeblebrox", "start": 2542.2},
    {"num": 5, "title": "Chapter 5: Prostetnic Vogon Jeltz", "start": 3225.4},
    {"num": 6, "title": "Chapter 6: Inside the Vogon Flagship", "start": 3371.5},
    {"num": 7, "title": "Chapter 7: Vogon Poetry Appreciation", "start": 3620.2},
    {"num": 8, "title": "Chapter 8: The Hitchhiker's Guide to the Galaxy", "start": 5479.8},
    {"num": 9, "title": "Chapter 9: The Impossible Rescue", "start": 5632.7},
    {"num": 10, "title": "Chapter 10: The Infinite Improbability Drive", "start": 6106.3},
    {"num": 11, "title": "Chapter 11: Inside the Heart of Gold", "start": 6228.2},
    {"num": 12, "title": "Chapter 12: Genuine People Personalities", "start": 6585.9},
    {"num": 13, "title": "Chapter 13: Sub-Etha Radio Waves", "start": 6927.9},
    {"num": 14, "title": "Chapter 14: Sector ZZ9 Plural Z Alpha", "start": 7769.4},
    {"num": 15, "title": "Chapter 15: The Legend of Magrathea", "start": 8080.1},
    {"num": 16, "title": "Chapter 16: Binary Sunrise Over Magrathea", "start": 8204.4},
    {"num": 17, "title": "Chapter 17: Descent onto the Dead Planet", "start": 8442.0},
    {"num": 18, "title": "Chapter 18: The Automated Defence System", "start": 8566.4},
    {"num": 19, "title": "Chapter 19: The Ancient Recording", "start": 8688.4},
    {"num": 20, "title": "Chapter 20: Guided Nuclear Missiles", "start": 8814.0},
    {"num": 21, "title": "Chapter 21: Evasive Action", "start": 8902.0},
    {"num": 22, "title": "Chapter 22: The Sperm Whale & Bowl of Petunias", "start": 9376.1},
    {"num": 23, "title": "Chapter 23: Landing on Magrathea", "start": 9599.6},
    {"num": 24, "title": "Chapter 24: The Barren Tundra", "start": 9738.4},
    {"num": 25, "title": "Chapter 25: The Cauterized Synapses", "start": 10030.3},
    {"num": 26, "title": "Chapter 26: The Ballpoint Pen Planet", "start": 10352.1},
    {"num": 27, "title": "Chapter 27: Slartibartfast", "start": 10587.6},
    {"num": 28, "title": "Chapter 28: Dolphins and White Mice", "start": 10952.7},
    {"num": 29, "title": "Chapter 29: The Factory Floor of Magrathea", "start": 11203.6},
    {"num": 30, "title": "Chapter 30: Deep Thought", "start": 11713.7},
    {"num": 31, "title": "Chapter 31: Seven and a Half Million Years", "start": 12131.6},
    {"num": 32, "title": "Chapter 32: The Ultimate Answer: 42", "start": 12496.9},
    {"num": 33, "title": "Chapter 33: The Ultimate Question", "start": 12900.0},
    {"num": 34, "title": "Chapter 34: The Mouse Consortium", "start": 13613.0},
    {"num": 35, "title": "Chapter 35: The Restaurant at the End of the Universe", "start": 14901.2},
]

AUDIO_SRC = "hitchhiker_raw.webm"
OUT_AUDIO_DIR = "chapters_audio"
OUT_DATA_DIR = "chapters_data"
OUT_VIDEO_DIR = "out/chapters"
PUBLIC_AUDIO_DIR = "public/chapters_audio"

os.makedirs(OUT_AUDIO_DIR, exist_ok=True)
os.makedirs(OUT_DATA_DIR, exist_ok=True)
os.makedirs(OUT_VIDEO_DIR, exist_ok=True)
os.makedirs(PUBLIC_AUDIO_DIR, exist_ok=True)

manifest = []

MAX_WORDS = 9
MAX_DURATION = 3.8

total_book_end = words[-1]["end"]

for idx, ch in enumerate(CHAPTERS):
    start_t = ch["start"]
    end_t = CHAPTERS[idx + 1]["start"] if idx + 1 < len(CHAPTERS) else total_book_end
    duration = end_t - start_t
    
    ch_num = ch["num"]
    file_slug = f"chapter_{ch_num:02d}" if ch_num > 0 else "chapter_00_prologue"
    audio_path = os.path.join(OUT_AUDIO_DIR, f"{file_slug}.mp3")
    public_audio_path = os.path.join(PUBLIC_AUDIO_DIR, f"{file_slug}.mp3")
    subtitles_path = os.path.join(OUT_DATA_DIR, f"{file_slug}.json")
    video_path = os.path.join(OUT_VIDEO_DIR, f"{file_slug}_60fps.mp4")

    # 1. Extract audio slice if not exists
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 1000:
        cmd = [
            "ffmpeg", "-y", "-ss", str(start_t), "-i", AUDIO_SRC,
            "-t", str(duration), "-c:a", "libmp3lame", "-q:a", "2",
            audio_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["cp", audio_path, public_audio_path])
    
    # 2. Extract words falling inside this chapter range and re-base time to 0.0s
    ch_words = []
    for w in words:
        if start_t <= w["start"] < end_t:
            ch_words.append({
                "text": w["text"],
                "start": round(w["start"] - start_t, 3),
                "end": round(w["end"] - start_t, 3)
            })

    # Group into visual cards
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
        
        has_period = any(p in w_text for p in [".", "?", "!", ";", "—"])
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

    manifest.append({
        "chapter_num": ch_num,
        "title": ch["title"],
        "start_time_seconds": round(start_t, 2),
        "end_time_seconds": round(end_t, 2),
        "duration_seconds": round(duration, 2),
        "duration_formatted": f"{int(duration//60)}m {int(duration%60):02d}s",
        "word_count": len(ch_words),
        "card_count": len(pages),
        "audio_file": audio_path,
        "public_audio": f"chapters_audio/{file_slug}.mp3",
        "subtitles_file": subtitles_path,
        "video_file": video_path,
        "rendered": os.path.exists(video_path)
    })

    print(f"✅ {ch['title'][:45]:45s} | {int(duration//60):02d}m {int(duration%60):02d}s | {len(ch_words):5d} words | {len(pages):3d} cards")

with open("chapters_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("\n🎉 Generated complete chapters dataset and audio slices for all 35 chapters!")
