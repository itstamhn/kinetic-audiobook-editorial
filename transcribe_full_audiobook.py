import os
import sys
import subprocess
import requests
import json
import concurrent.futures

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found!")

RAW_AUDIO = "hitchhiker_raw.webm"
CHUNK_DIR = "audio_chunks"
CHUNK_DURATION = 900 # 15 minutes = 900 seconds
TOTAL_DURATION = 15081.5 # ~251.4 minutes

os.makedirs(CHUNK_DIR, exist_ok=True)
num_chunks = int(TOTAL_DURATION // CHUNK_DURATION) + 1

print(f"📦 Slicing 4.19h audio into {num_chunks} chunks of {CHUNK_DURATION}s each...")

def create_chunk(i):
    start_sec = i * CHUNK_DURATION
    chunk_path = os.path.join(CHUNK_DIR, f"chunk_{i:02d}.mp3")
    if not os.path.exists(chunk_path) or os.path.getsize(chunk_path) < 1000:
        cmd = [
            "ffmpeg", "-y", "-ss", str(start_sec), "-i", RAW_AUDIO,
            "-t", str(CHUNK_DURATION), "-c:a", "libmp3lame", "-q:a", "3",
            chunk_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return i, chunk_path, start_sec

chunks_info = []
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(create_chunk, i) for i in range(num_chunks)]
    for f in concurrent.futures.as_completed(futures):
        chunks_info.append(f.result())

chunks_info.sort(key=lambda x: x[0])
print(f"✅ All {len(chunks_info)} chunks created!")

def transcribe_chunk(chunk_tuple):
    i, chunk_path, offset = chunk_tuple
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    
    with open(chunk_path, "rb") as f:
        files = {"file": (os.path.basename(chunk_path), f, "audio/mpeg")}
        data = {
            "model": "whisper-large-v3-turbo",
            "response_format": "verbose_json",
            "timestamp_granularities[]": ["word", "segment"]
        }
        res = requests.post(url, headers=headers, files=files, data=data, timeout=90)
        
    if res.status_code != 200:
        print(f"❌ Error in chunk {i}: {res.status_code} {res.text}")
        return i, offset, []
        
    data = res.json()
    words = data.get("words", [])
    # Adjust timestamps by chunk offset
    adjusted_words = []
    for w in words:
        w_text = w["word"].strip()
        if w_text:
            adjusted_words.append({
                "text": w_text,
                "start": round(w["start"] + offset, 3),
                "end": round(w["end"] + offset, 3)
            })
    print(f"  ⚡ Chunk {i:02d} ({offset/60:.1f}m - {(offset+CHUNK_DURATION)/60:.1f}m): {len(adjusted_words)} words")
    return i, offset, adjusted_words

print("\n🚀 Transcribing all chunks with Groq Whisper in parallel...")
all_transcriptions = []
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(transcribe_chunk, c) for c in chunks_info]
    for f in concurrent.futures.as_completed(futures):
        all_transcriptions.append(f.result())

all_transcriptions.sort(key=lambda x: x[0])

all_words = []
for i, offset, words in all_transcriptions:
    all_words.extend(words)

print(f"\n🎉 Completed full book transcription! Total words: {len(all_words)}")

with open("full_audiobook_words.json", "w") as f:
    json.dump(all_words, f, indent=2)

print("Saved full_audiobook_words.json!")
