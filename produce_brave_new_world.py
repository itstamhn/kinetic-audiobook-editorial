import asyncio
import edge_tts
import whisper
import json
import os
import re
import difflib

# 1. Read Chapter 1 text
with open("book_chapters_md/brave_new_world_ch1.txt") as f:
    full_text = f.read().strip()

# Let's take the first 8 rich paragraphs (iconic opening of Brave New World, ~60-70 seconds)
paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
selected_paragraphs = paragraphs[:8]
sample_text = " ".join(selected_paragraphs)

# Clean quotes for natural TTS
tts_text = sample_text.replace("“", '"').replace("”", '"').replace("’", "'")

os.makedirs("public/chapters_audio", exist_ok=True)
os.makedirs("chapters_data", exist_ok=True)
audio_output = "public/chapters_audio/brave_new_world_ch1.mp3"

print("🎙️ Step 1: Synthesizing British Oxford Audiobook Narration (en-GB-RyanNeural)...")

async def generate_audio():
    # Rate -3% gives that deliberate, dignified literary pacing
    communicate = edge_tts.Communicate(tts_text, 'en-GB-RyanNeural', rate='-3%')
    with open(audio_output, 'wb') as f:
        async for chunk in communicate.stream():
            if chunk['type'] == 'audio':
                f.write(chunk['data'])

asyncio.run(generate_audio())
print(f"✅ Audio generated: {audio_output} ({os.path.getsize(audio_output)} bytes)")

print("\n⚡ Step 2: Transcribing with Local Whisper to extract word timestamps...")
model = whisper.load_model("base")
result = model.transcribe(audio_output, word_timestamps=True)

whisper_words = []
for seg in result['segments']:
    for w in seg.get('words', []):
        whisper_words.append({
            "word": w["word"].strip(),
            "start": round(w["start"], 3),
            "end": round(w["end"], 3)
        })

print(f"✅ Extracted {len(whisper_words)} spoken word timestamps.")

print("\n📖 Step 3: Aligning with EPUB Ground-Truth Text...")
epub_words = sample_text.split()

# Fuzzy alignment to map Whisper timestamps to original EPUB tokens
aligned_words = []
whisper_idx = 0

for ew in epub_words:
    clean_ew = re.sub(r'[^\w]', '', ew).lower()
    
    # Match against next few whisper words
    best_match_idx = None
    for j in range(whisper_idx, min(whisper_idx + 4, len(whisper_words))):
        clean_ww = re.sub(r'[^\w]', '', whisper_words[j]["word"]).lower()
        if clean_ww == clean_ew or clean_ew.startswith(clean_ww) or clean_ww.startswith(clean_ew):
            best_match_idx = j
            break
            
    if best_match_idx is not None:
        matched = whisper_words[best_match_idx]
        aligned_words.append({
            "text": ew,
            "start": matched["start"],
            "end": matched["end"]
        })
        whisper_idx = best_match_idx + 1
    else:
        # Fallback to previous word end
        prev_end = aligned_words[-1]["end"] if aligned_words else 0.0
        aligned_words.append({
            "text": ew,
            "start": prev_end,
            "end": round(prev_end + 0.35, 3)
        })

print(f"✅ Successfully aligned {len(aligned_words)} ground-truth words!")

print("\n📑 Step 4: Chunking into Balanced Multi-Line Honda-Style Pages...")
# Sentence-aware chunking: 16 to 22 words per slide
pages_words = []
current_chunk = []

for idx, w in enumerate(aligned_words):
    current_chunk.append(w)
    text = w["text"].strip()
    
    is_sentence_end = any(text.endswith(p) for p in [".", "!", "?", '."', '!"', '?"', "—", ";"])
    is_clause_end = text.endswith(",") or text.endswith('",')
    
    if len(current_chunk) >= 16 and is_sentence_end:
        pages_words.append(current_chunk)
        current_chunk = []
    elif len(current_chunk) >= 20 and is_clause_end:
        pages_words.append(current_chunk)
        current_chunk = []
    elif len(current_chunk) >= 24:
        pages_words.append(current_chunk)
        current_chunk = []

if current_chunk:
    if len(current_chunk) < 8 and len(pages_words) > 0:
        pages_words[-1].extend(current_chunk)
    else:
        pages_words.append(current_chunk)

# Build contiguous page timeframes
formatted_pages = []
for i, p_words in enumerate(pages_words):
    if i == 0:
        page_start = 0.0
    else:
        prev_end = pages_words[i - 1][-1]["end"]
        curr_start = p_words[0]["start"]
        pause = max(0.0, curr_start - prev_end)
        if pause > 0.4:
            page_start = round(prev_end + 0.25, 3)
        else:
            page_start = round(prev_end + pause / 2.0, 3)

    if i + 1 < len(pages_words):
        next_start = pages_words[i + 1][0]["start"]
        curr_end = p_words[-1]["end"]
        pause = max(0.0, next_start - curr_end)
        if pause > 0.4:
            page_end = round(curr_end + 0.25, 3)
        else:
            page_end = round(curr_end + pause / 2.0, 3)
    else:
        page_end = round(p_words[-1]["end"] + 1.0, 3)

    formatted_pages.append({
        "id": i + 1,
        "startTime": page_start,
        "endTime": page_end,
        "words": p_words
    })

# Guarantee seamless contiguous boundaries
for i in range(len(formatted_pages) - 1):
    formatted_pages[i]["endTime"] = formatted_pages[i + 1]["startTime"]

total_dur = formatted_pages[-1]["endTime"]

props = {
    "totalDurationSeconds": total_dur,
    "audioFile": "chapters_audio/brave_new_world_ch1.mp3",
    "pages": formatted_pages
}

props_file = "chapters_data/brave_new_world_ch1_props.json"
with open(props_file, "w") as f:
    json.dump(props, f, indent=2)

print(f"\n🎉 Generated {len(formatted_pages)} pages for Chapter 1 ({total_dur}s):")
for p in formatted_pages:
    w_sample = " ".join(w["text"] for w in p["words"])
    print(f"  • Page {p['id']} [{p['startTime']}s -> {p['endTime']}s] ({len(p['words'])} words): {w_sample[:65]}...")
