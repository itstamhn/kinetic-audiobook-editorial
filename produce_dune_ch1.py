import os
import re
import json
import zipfile
import asyncio
from bs4 import BeautifulSoup
import edge_tts
from wordfreq import zipf_frequency
from deep_translator import GoogleTranslator
import whisper

EPUB_PATH = "/Users/tamhn/Downloads/Dune (Frank Herbert) (z-library.sk, 1lib.sk, z-lib.sk).epub"
AUDIO_OUTPUT = "public/chapters_audio/dune_ch1_full.mp3"
WHISPER_OUTPUT = "chapters_data/dune_ch1_full_whisper.json"
PROPS_OUTPUT = "chapters_data/dune_ch1_full_props.json"
RAW_TEXT_PATH = "book_chapters_md/dune_ch1_full.txt"
KNOWN_WORDS_FILE = "user_known_words.txt"

os.makedirs("public/chapters_audio", exist_ok=True)
os.makedirs("chapters_data", exist_ok=True)
os.makedirs("book_chapters_md", exist_ok=True)
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

# 2. Extract Text from EPUB
print("📖 Extracting Chapter 1 from Dune EPUB...")
with zipfile.ZipFile(EPUB_PATH, "r") as z:
    html = z.read("OEBPS/xhtml/chapter001.xhtml").decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove chapter headers if redundant
    for h in soup.find_all(["h1", "h2", "h3"]):
        h.decompose()
        
    paragraphs = []
    for p in soup.find_all("p"):
        txt = p.get_text().strip()
        if txt:
            # Clean up excessive internal whitespace
            txt = re.sub(r'\s+', ' ', txt)
            paragraphs.append(txt)

full_chapter_text = "\n\n".join(paragraphs)
with open(RAW_TEXT_PATH, "w", encoding="utf-8") as f:
    f.write(full_chapter_text)

words_raw = full_chapter_text.split()
print(f"✅ Extracted {len(paragraphs)} paragraphs, {len(words_raw)} words.")

# 3. Text-to-Speech Synthesis with Edge-TTS (en-GB-RyanNeural) - Paragraph by Paragraph
async def generate_audio():
    if os.path.exists(AUDIO_OUTPUT) and os.path.getsize(AUDIO_OUTPUT) > 9000000:
        print(f"⚡ Full audio already exists: {AUDIO_OUTPUT} ({os.path.getsize(AUDIO_OUTPUT)} bytes)", flush=True)
        return
    print(f"🎙️ Synthesizing full audio ({len(paragraphs)} paragraphs) with Edge-TTS (en-GB-RyanNeural)...", flush=True)
    with open(AUDIO_OUTPUT, "wb") as out_f:
        for idx, p in enumerate(paragraphs):
            clean_p = p.replace("“", '"').replace("”", '"').replace("’", "'").replace("—", " — ")
            if not clean_p.strip():
                continue
            communicate = edge_tts.Communicate(clean_p, "en-GB-RyanNeural", rate="-3%")
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    out_f.write(chunk["data"])
            if (idx + 1) % 10 == 0 or idx == len(paragraphs) - 1:
                print(f"   Synthesized paragraph {idx + 1}/{len(paragraphs)}...", flush=True)
    print(f"✅ Audio generated successfully: {AUDIO_OUTPUT} ({os.path.getsize(AUDIO_OUTPUT)} bytes)", flush=True)

asyncio.run(generate_audio())

# 4. Transcribe with Whisper AI
if not os.path.exists(WHISPER_OUTPUT) or os.path.getsize(WHISPER_OUTPUT) < 1000:
    print("🤖 Transcribing audio with Whisper AI to get word-level timestamps...", flush=True)
    model = whisper.load_model("base.en")
    result = model.transcribe(AUDIO_OUTPUT, word_timestamps=True, verbose=False)
    
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

# Align with EPUB ground truth words
epub_words = full_chapter_text.split()
aligned_words = []
whisper_idx = 0

for ew in epub_words:
    clean_ew = re.sub(r"[^\w]", "", ew).lower()
    best_match_idx = None
    for j in range(whisper_idx, min(whisper_idx + 8, len(whisper_words))):
        clean_ww = re.sub(r"[^\w]", "", whisper_words[j]["word"]).lower()
        if clean_ww == clean_ew or (len(clean_ew) > 3 and (clean_ew.startswith(clean_ww) or clean_ww.startswith(clean_ew))):
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
        prev_end = aligned_words[-1]["end"] if aligned_words else 0.0
        aligned_words.append({
            "text": ew,
            "start": prev_end,
            "end": round(prev_end + 0.32, 3)
        })

print(f"✅ Aligned {len(aligned_words)} words with EPUB ground-truth text.", flush=True)

# 5. Smart Vocabulary Translation (C1/C2 Zipf <= 4.15 + Whitelist)
print("🧠 Analyzing vocabulary frequency & generating C1/C2 Vietnamese glosses...", flush=True)
translator = GoogleTranslator(source='en', target='vi')

# Filter common words
gloss_cache = {}
annotated_count = 0

def clean_word(w):
    return re.sub(r'[^a-zA-Z]', '', w).lower()

# Character names / Dune universe terms to skip
dune_universe_names = {
    "paul", "jessica", "atreides", "caladan", "arrakis", "dune", "muaddib", "shaddam", "bene", "gesserit",
    "reverend", "mother", "mohiam", "gaius", "helen", "gom", "jabbar", "kwisatz", "haderach", "mentat",
    "padishah", "emperor", "hawat", "thufir", "gurney", "halleck", "duncan", "idaho", "vladimir", "harkonnen",
    "sietch", "fremen", "sandworm", "melange", "spice", "crysknife", "stillsuit", "ornithopter", "thopter",
    "suspensor", "glowglobe", "plasteel", "piter", "de", "vries", "baron", "duke", "leto", "lady", "sir",
    "crone", "witch", "boy", "voice", "truthsay", "truthsaying", "test", "pain", "box", "hand", "death",
    "water", "desert", "sand", "planet", "room", "night", "house", "table", "chair", "door", "bed"
}

# Pre-identify difficult words
unique_rare_words = []
for item in aligned_words:
    raw_w = item["text"]
    clean_w = clean_word(raw_w)
    if not clean_w or len(clean_w) < 4:
        continue
    if clean_w in known_words or clean_w in dune_universe_names:
        continue
    freq = zipf_frequency(clean_w, 'en')
    if freq <= 4.15 and freq > 0:
        if clean_w not in gloss_cache and clean_w not in unique_rare_words:
            unique_rare_words.append(clean_w)

print(f"Translating {len(unique_rare_words)} rare words in parallel...", flush=True)
from concurrent.futures import ThreadPoolExecutor

def translate_single_word(w):
    try:
        t = GoogleTranslator(source='en', target='vi').translate(w)
        if t:
            t = t.strip().lower()
            t = re.sub(r'[.,;!?"\']', '', t)
            t_words = t.split()
            if len(t_words) > 2:
                t = " ".join(t_words[:2])
            return (w, t)
    except Exception:
        pass
    return (w, None)

with ThreadPoolExecutor(max_workers=20) as executor:
    results = executor.map(translate_single_word, unique_rare_words)
    for orig, trans in results:
        gloss_cache[orig] = trans
        if trans and annotated_count <= 25:
            annotated_count += 1
            freq = zipf_frequency(orig, 'en')
            print(f"   [C1/C2 Gloss] {orig} (Zipf: {freq:.2f}) -> {trans}", flush=True)

print(f"✅ Identified and glossed {len(gloss_cache)} advanced vocabulary words.", flush=True)

# 6. Chunking into 2-3 Lines Max Pages
print("📄 Chunking words into 2-3 lines max pages...", flush=True)
pages = []
current_words = []
MAX_WORDS_PER_PAGE = 18 # Guarantees max 2-3 lines at 88px font size

for idx, w_info in enumerate(aligned_words):
    raw_w = w_info["text"]
    clean_w = clean_word(raw_w)
    gloss = gloss_cache.get(clean_w, None)
    
    current_words.append({
        "text": raw_w,
        "start": w_info["start"],
        "end": w_info["end"],
        "vn": gloss
    })
    
    is_sentence_end = any(raw_w.endswith(punct) for punct in [".", "!", "?", "...", '."', '!"', '?"', "—", ";"])
    has_comma_split = any(raw_w.endswith(punct) for punct in [",", ',"']) and len(current_words) >= 12
    
    if len(current_words) >= MAX_WORDS_PER_PAGE or (len(current_words) >= 10 and is_sentence_end) or has_comma_split or idx == len(aligned_words) - 1:
        start_time = current_words[0]["start"]
        end_time = current_words[-1]["end"] + 0.25 # Clean breathing pause
        
        pages.append({
            "id": len(pages),
            "pageIndex": len(pages),
            "startTime": round(start_time, 3),
            "endTime": round(end_time, 3),
            "duration": round(end_time - start_time, 3),
            "words": current_words
        })
        current_words = []

# Compute full chapter stats
total_duration_sec = aligned_words[-1]["end"] + 1.0
total_duration_frames = int(total_duration_sec * 60)

final_props = {
    "chapterNumber": 1,
    "chapterTitle": "Chapter 1",
    "bookTitle": "Dune",
    "author": "Frank Herbert",
    "audioFile": "chapters_audio/dune_ch1_full.mp3",
    "totalDurationSeconds": round(total_duration_sec, 2),
    "totalFrames": total_duration_frames,
    "fps": 60,
    "pages": pages
}

with open(PROPS_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(final_props, f, ensure_ascii=False, indent=2)

print(f"\n🎉 Successfully created full Chapter 1 props!")
print(f"📊 Total Pages: {len(pages)}")
print(f"⏱️ Total Duration: {total_duration_sec/60:.2f} mins ({total_duration_frames} frames @ 60 FPS)")
print(f"💾 Saved to {PROPS_OUTPUT}")
