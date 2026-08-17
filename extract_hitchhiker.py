import json
import whisper
import shutil
import os

print("Loading Whisper model...")
model = whisper.load_model("base.en")

audio_path = "chapter1_intro_clean.mp3"
print(f"Transcribing {audio_path} with word-level timestamps...")

result = model.transcribe(
    audio_path,
    word_timestamps=True,
    verbose=False,
    temperature=0.0
)

pages = []
page_id = 0

current_words = []
current_start = 0.0

MAX_WORDS = 9
MAX_DURATION = 3.8

for seg in result["segments"]:
    for word_info in seg.get("words", []):
        w_text = word_info["word"].strip()
        if not w_text:
            continue
        
        w_start = round(word_info["start"], 3)
        w_end = round(word_info["end"], 3)
        
        if not current_words:
            current_start = w_start
            
        current_words.append({
            "text": w_text,
            "start": w_start,
            "end": w_end
        })
        
        has_period = any(punct in w_text for punct in [".", "?", "!", ";", "—"])
        has_comma = "," in w_text
        duration = w_end - current_start
        
        # Break into readable rhythmic visual cards
        should_break = False
        if has_period and len(current_words) >= 4:
            should_break = True
        elif has_comma and len(current_words) >= 7:
            should_break = True
        elif len(current_words) >= MAX_WORDS or duration >= MAX_DURATION:
            should_break = True
            
        if should_break:
            full_text = " ".join([w["text"] for w in current_words])
            pages.append({
                "id": page_id,
                "startTime": current_start,
                "endTime": w_end,
                "fullText": full_text,
                "words": current_words
            })
            page_id += 1
            current_words = []

if current_words:
    full_text = " ".join([w["text"] for w in current_words])
    pages.append({
        "id": page_id,
        "startTime": current_start,
        "endTime": current_words[-1]["end"],
        "fullText": full_text,
        "words": current_words
    })

print(f"✅ Extracted {len(pages)} subtitle pages from {audio_path}")

with open("hitchhiker_subtitles.json", "w") as f:
    json.dump(pages, f, indent=2)

shutil.copy("hitchhiker_subtitles.json", "src/subtitles.json")
shutil.copy(audio_path, "public/audio_30s.mp3")
shutil.copy(audio_path, "public/audio_hitchhiker.mp3")

print("Saved hitchhiker_subtitles.json and updated public/ audio files!")
