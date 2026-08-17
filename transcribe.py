import json
import subprocess
import whisper

# Trim first 35s
subprocess.run(["ffmpeg", "-y", "-i", "audio_raw.mp3", "-ss", "00:00:00", "-t", "35", "audio_35s.mp3"], check=True)

model = whisper.load_model("small")
result = model.transcribe("audio_35s.mp3", word_timestamps=True, no_speech_threshold=0.6, condition_on_previous_text=False)

clean_segments = []
for seg in result["segments"]:
    words = []
    for w in seg.get("words", []):
        word_text = w["word"].strip()
        if word_text and word_text.lower() not in ["please.", "oh.", "please", "you.", "you", "thank you.", "thank you"]:
            words.append({
                "word": word_text,
                "start": round(w["start"], 3),
                "end": round(w["end"], 3)
            })
    if words:
        clean_segments.append({
            "start": words[0]["start"],
            "end": words[-1]["end"],
            "text": " ".join([w["word"] for w in words]),
            "words": words
        })

with open("transcript_clean.json", "w") as f:
    json.dump(clean_segments, f, indent=2)

print(f"Extracted {len(clean_segments)} clean segments:")
for s in clean_segments:
    print(f"[{s['start']}s -> {s['end']}s]: {s['text']}")
