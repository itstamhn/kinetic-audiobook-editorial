import zipfile
import re
import json
import os
import subprocess

# 1. Load full audiobook words with Groq Whisper timestamps
with open("full_audiobook_words.json", "r") as f:
    audio_words = json.load(f)

# Normalize text helper
def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())

audio_tokens = [norm(w["text"]) for w in audio_words]

# 2. Extract chapters from EPUB
with zipfile.ZipFile("hitchhiker_guide.epub", "r") as z:
    raw0 = z.read("Douglas Adams - The Hitch Hikers Guide to Galaxy_split_000.htm").decode("utf-8", errors="ignore")
    raw1 = z.read("Douglas Adams - The Hitch Hikers Guide to Galaxy_split_001.htm").decode("utf-8", errors="ignore")

full_html = raw0 + "\n" + raw1

# Clean HTML tags into text tokens
def html_to_clean_text(html_fragment):
    clean = re.sub(r"<[^>]+>", " ", html_fragment)
    clean = re.sub(r"&[a-z]+;", " ", clean)
    words = clean.split()
    return words

# Locate all chapter positions in HTML
# Pattern for Chapter markers: <p ...>1</p> or <p ...><span>1</span></p>
chapter_splits = []

# Prologue start
prologue_pos = full_html.find("Far out in the uncharted backwaters")
chapter_splits.append((0, "Prologue", prologue_pos))

for ch_num in range(1, 36):
    # Regex to find chapter number
    patterns = [
        rf"<p[^>]*><span[^>]*>{ch_num}</span></p>",
        rf"<p[^>]*>{ch_num}</p>",
        rf">\s*{ch_num}\s*<"
    ]
    pos = -1
    for p in patterns:
        m = re.search(p, full_html[chapter_splits[-1][2]:])
        if m:
            pos = chapter_splits[-1][2] + m.end()
            break
    if pos != -1:
        chapter_splits.append((ch_num, f"Chapter {ch_num:02d}", pos))
    else:
        print(f"⚠️ Could not find Chapter {ch_num} marker in EPUB")

print(f"Found {len(chapter_splits)} chapter sections in EPUB.")

# Extract chapter texts
chapters_text = []
for idx, (num, name, start_pos) in enumerate(chapter_splits):
    end_pos = chapter_splits[idx + 1][2] if idx + 1 < len(chapter_splits) else len(full_html)
    raw_snippet = full_html[start_pos:end_pos]
    words = html_to_clean_text(raw_snippet)
    # Remove leading chapter numbers or noise
    while words and (words[0].isdigit() or len(words[0]) <= 1):
        words.pop(0)
    chapters_text.append({
        "num": num,
        "name": name,
        "words": words,
        "opening_text": " ".join(words[:12])
    })

# 3. Find exact start & end word in audio_words for each chapter
def find_subsequence(query_tokens, start_search_idx=0, max_search_window=3000):
    q = [norm(t) for t in query_tokens if norm(t)]
    if not q:
        return None
    
    best_idx = None
    best_score = 0
    
    end_search = min(len(audio_tokens), start_search_idx + max_search_window)
    
    for i in range(start_search_idx, end_search):
        score = 0
        for j in range(min(len(q), 10)):
            if i + j < len(audio_tokens) and audio_tokens[i + j] == q[j]:
                score += 1
            elif i + j < len(audio_tokens) and (audio_tokens[i+j] in q[j] or q[j] in audio_tokens[i+j]):
                score += 0.5
        if score > best_score and score >= 4:
            best_score = score
            best_idx = i
            if score >= 8:
                break
    return best_idx

# Align all chapters
current_audio_idx = 0
aligned_chapters = []

for ch in chapters_text:
    num = ch["num"]
    name = ch["name"]
    ep_words = ch["words"]
    
    match_idx = find_subsequence(ep_words[:15], start_search_idx=current_audio_idx, max_search_window=4000)
    
    if match_idx is not None:
        start_time = audio_words[match_idx]["start"]
        current_audio_idx = match_idx
        aligned_chapters.append({
            "num": num,
            "name": name,
            "audio_word_idx": match_idx,
            "start_time": start_time,
            "opening": " ".join(ep_words[:8]),
            "matched_audio": " ".join([audio_words[match_idx + k]["text"] for k in range(min(8, len(audio_words)-match_idx))])
        })
        mins = start_time / 60
        print(f"✅ {name:12s} at {mins:05.2f}m ({start_time:07.1f}s) | '{aligned_chapters[-1]['matched_audio']}'")
    else:
        print(f"❌ Failed to align {name}")

print(f"\nSuccessfully aligned {len(aligned_chapters)} / {len(chapters_text)} chapters with Ground Truth EPUB!")

# Save aligned Ground-Truth Manifest
final_manifest = []
total_audio_end = audio_words[-1]["end"]

for idx, ch in enumerate(aligned_chapters):
    start_t = ch["start_time"]
    end_t = aligned_chapters[idx + 1]["start_time"] if idx + 1 < len(aligned_chapters) else total_audio_end
    duration = end_t - start_t
    
    num = ch["num"]
    file_slug = f"chapter_{num:02d}" if num > 0 else "chapter_00_prologue"
    
    start_w = ch["audio_word_idx"]
    end_w = aligned_chapters[idx + 1]["audio_word_idx"] if idx + 1 < len(aligned_chapters) else len(audio_words)
    ch_words_count = end_w - start_w

    final_manifest.append({
        "chapter_num": num,
        "title": ch["name"],
        "start_time_seconds": round(start_t, 2),
        "end_time_seconds": round(end_t, 2),
        "duration_seconds": round(duration, 2),
        "duration_formatted": f"{int(duration//60)}m {int(duration%60):02d}s",
        "word_count": ch_words_count,
        "audio_file": f"chapters_audio/{file_slug}.mp3",
        "subtitles_file": f"chapters_data/{file_slug}.json",
        "video_file": f"out/chapters/{file_slug}_60fps.mp4",
        "opening_text": ch["opening"]
    })

with open("chapters_manifest_ground_truth.json", "w") as f:
    json.dump(final_manifest, f, indent=2)

print("\nSaved chapters_manifest_ground_truth.json!")
