import os
import re
import json
import concurrent.futures
from wordfreq import zipf_frequency
from deep_translator import GoogleTranslator
import whisper

AUDIO_INPUT = "public/chapters_audio/lotr_fellowship_ch1.mp3"
WHISPER_OUTPUT = "chapters_data/lotr_ch1_full_whisper.json"
PROPS_OUTPUT = "chapters_data/lotr_ch1_full_props.json"
KNOWN_WORDS_FILE = "user_known_words.txt"
OBSIDIAN_VAULT_DIR = "/Users/tamhn/Library/Mobile Documents/iCloud~md~obsidian/Documents/tamhome/Notes"

os.makedirs("public/chapters_audio", exist_ok=True)
os.makedirs("chapters_data", exist_ok=True)
os.makedirs("out", exist_ok=True)

# 1. Load User Known Words
known_words = set()
if os.path.exists(KNOWN_WORDS_FILE):
    with open(KNOWN_WORDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            w = line.strip().lower()
            if w and not w.startswith("#"):
                known_words.add(w)
print(f"Loaded {len(known_words)} known words from whitelist.")

# 2. Transcribe Audio with Whisper
if not os.path.exists(WHISPER_OUTPUT) or os.path.getsize(WHISPER_OUTPUT) < 1000:
    print("🤖 Transcribing LOTR Chapter 1 audio with Whisper AI (word_timestamps=True)...", flush=True)
    model = whisper.load_model("base.en")
    result = model.transcribe(AUDIO_INPUT, word_timestamps=True, verbose=False)
    
    whisper_words = []
    for segment in result.get("segments", []):
        for w in segment.get("words", []):
            whisper_words.append({
                "word": w["word"].strip(),
                "start": round(w["start"], 3),
                "end": round(w["end"], 3)
            })
    
    with open(WHISPER_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(whisper_words, f, ensure_ascii=False, indent=2)
    print(f"✅ Whisper transcribed {len(whisper_words)} words.", flush=True)
else:
    print(f"⚡ Loading cached Whisper timestamps: {WHISPER_OUTPUT}", flush=True)
    with open(WHISPER_OUTPUT, "r", encoding="utf-8") as f:
        whisper_words = json.load(f)

# 3. Extract C1/C2 & Rare Literary Vocabulary using literary_vocab_engine
from literary_vocab_engine import extract_literary_vocabulary

tolkien_names = {
    "bagend", "baggins", "bagginses", "bagshot", "bilbo", "bilbos", "frodo", "gandalf", 
    "gollum", "gamgee", "sam", "samwise", "gaffer", "hobbit", "hobbits", "hobbiton", 
    "bywater", "shire", "brandybuck", "brandybucks", "took", "tooks", "sackville", 
    "lobelia", "otho", "proudfoot", "proudfoots", "proudfeet", "bolger", "bolgers", 
    "boffin", "boffins", "grubb", "chubb", "burrows", "burrowses", "brandywine", 
    "buckland", "adelard", "angelica", "angelicas", "sancho", "dora", "drogo", 
    "primula", "gorbadoc", "rivendell", 
    "elendil", "galadriel", "celeborn", "mordor", "sauron", "sandyman", "cotton", 
    "maggot", "maggott", "bindbale", "badger", "brockhouse", "hornblower", "bracegirdle",
    "fianorian", "labelia", "sackfield", "saxopotatoes", "gaffogamgy", "adivator"
}

vocab_data = extract_literary_vocabulary(whisper_words, custom_name_blacklist=tolkien_names)
unique_vocab = {w: data["translation"] for w, data in vocab_data.items()}

print(f"🎯 Extracted {len(unique_vocab)} advanced C1/C2 & Literary vocabulary words.")

print(f"✅ Translated {len(unique_vocab)} vocabulary items.")

# 4. Group Words into Calm Editorial Pages (2-3 lines per page, 14-18 words max)
pages = []
current_page_words = []
MAX_WORDS_PER_PAGE = 18

for idx, w in enumerate(whisper_words):
    clean_w = re.sub(r"[^\w]", "", w["word"]).lower()
    vn_gloss = unique_vocab.get(clean_w, None)
    
    current_page_words.append({
        "text": w["word"],
        "start": w["start"],
        "end": w["end"],
        "vn": vn_gloss
    })
    
    is_sentence_end = bool(re.search(r'[.!?]["\']?$', w["word"]))
    is_clause_end = bool(re.search(r'[,;:]["\']?$', w["word"]))
    
    # Check if we should flip page
    should_flip = False
    if len(current_page_words) >= MAX_WORDS_PER_PAGE:
        should_flip = True
    elif len(current_page_words) >= 12 and (is_sentence_end or is_clause_end):
        should_flip = True
    elif is_sentence_end and len(current_page_words) >= 10:
        should_flip = True
    elif idx == len(whisper_words) - 1:
        should_flip = True
        
    if should_flip:
        start_time = max(0, current_page_words[0]["start"] - 0.15)
        # End time extends slightly to hold text during pause
        end_time = current_page_words[-1]["end"] + 0.3
        
        pages.append({
            "id": len(pages) + 1,
            "startTime": round(start_time, 3),
            "endTime": round(end_time, 3),
            "words": current_page_words
        })
        current_page_words = []

# Final duration
total_duration = pages[-1]["endTime"] + 1.0 if pages else 4300

props_data = {
    "totalDurationSeconds": round(total_duration, 2),
    "audioFile": "chapters_audio/lotr_fellowship_ch1.mp3",
    "pages": pages
}

with open(PROPS_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(props_data, f, ensure_ascii=False, indent=2)

print(f"🎉 Generated {len(pages)} editorial slides. Total duration: {total_duration/60:.2f} mins.")

# 5. Create Master Obsidian Note
if os.path.exists(OBSIDIAN_VAULT_DIR):
    obsidian_note_path = os.path.join(OBSIDIAN_VAULT_DIR, "The Lord of the Rings - Chapter 1 (Kinetic Audiobook & Vocabulary Gloss).md")
    
    vocab_rows = []
    for en, data in sorted(vocab_data.items()):
        vi = data["translation"]
        lvl = data["level"]
        zipf = data["zipf"]
        vocab_rows.append(f"| **{en}** | {vi} | {zipf} | {lvl} |")
    
    obsidian_content = f"""---
title: "The Fellowship of the Ring — Book 1, Chapter 1: A Long-expected Party"
author: "J. R. R. Tolkien"
narrator: "Rob Inglis"
type: "Kinetic Audiobook & Interlinear Vocabulary Gloss"
status: "Rendered & Uploaded"
youtube_url: "https://youtu.be/wvuKMNXOSww"
total_duration: "{total_duration/60:.1f} mins"
total_slides: {len(pages)}
total_words: {len(whisper_words)}
total_vocab_glossed: {len(vocab_data)}
date_created: "2026-08-18"
tags:
  - audiobook
  - tolkien
  - fellowship-of-the-ring
  - vocabulary-gloss
  - kinetic-reader
---

# 📖 The Lord of the Rings: The Fellowship of the Ring
## Book 1, Chapter 1: *A Long-expected Party*

> **Narrated by Rob Inglis (Full Original Audio)**  
> **Visual Style**: Calm Multi-Line Editorial Reader (Literata 82px, Interlinear C1/C2 & Literary Gloss, 60 FPS)

- **Source Narration**: [YouTube Narration (Rob Inglis)](https://www.youtube.com/watch?v=3GWskKwO_qs&t=3766s)
- **YouTube Video URL**: [https://youtu.be/wvuKMNXOSww](https://youtu.be/wvuKMNXOSww)
- **YouTube Studio Dashboard**: [https://studio.youtube.com/video/wvuKMNXOSww/edit](https://studio.youtube.com/video/wvuKMNXOSww/edit)
- **Visual Composition**: `Honda-Editorial-Light` (60 FPS, Literata Font, 82px English / 28px Teal Gloss)

---

### 📊 Production Summary

- **Total Runtime**: `{int(total_duration // 60)}m {int(total_duration % 60)}s` ({total_duration:.1f}s)
- **Total Frames @ 60 FPS**: `{int(total_duration * 60):,}` frames
- **Total Slides / Pages**: `{len(pages)}`
- **Total Spoken Words**: `{len(whisper_words):,}`
- **Advanced & Literary Glossed Words**: `{len(vocab_data)}`

---

### 📚 Interlinear Vocabulary Index (C1/C2 & Literary)

| English Word | Vietnamese Gloss | Zipf Frequency | Category |
| :--- | :--- | :--- | :--- |
{chr(10).join(vocab_rows)}

---

### 🎨 Remotion Architecture & Pipeline

```mermaid
graph LR
    YT[YouTube Audio Source<br/>3766s - 8066s] --> Trim[FFmpeg Clean Audio<br/>lotr_fellowship_ch1.mp3]
    Trim --> Whisper[Whisper AI<br/>Word Timestamps]
    Whisper --> Vocab[C1/C2 Filter &<br/>Parallel Vietnamese Gloss]
    Vocab --> Props[lotr_ch1_full_props.json<br/>71 mins / 60 FPS]
    Props --> Render[Mac Mini tambot<br/>8 Parallel Workers]
    Render --> Upload[youtube-uploader<br/>--profile main]
```
"""
    with open(obsidian_note_path, "w", encoding="utf-8") as f:
        f.write(obsidian_content)
    print(f"📝 Created Master Obsidian Note: {obsidian_note_path}")
