import os
import requests
import json
import shutil
import math

def transcribe_with_groq(audio_path: str, output_json_path: str = "src/subtitles.json", model: str = "whisper-large-v3-turbo"):
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment or Sigillo!")

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}

    print(f"⚡ Transcribing '{audio_path}' via Groq ({model})...")

    with open(audio_path, "rb") as f:
        files = {"file": (os.path.basename(audio_path), f, "audio/mpeg")}
        data = {
            "model": model,
            "response_format": "verbose_json",
            "timestamp_granularities[]": ["word", "segment"]
        }
        res = requests.post(url, headers=headers, files=files, data=data, timeout=60)

    if res.status_code != 200:
        raise RuntimeError(f"Groq API Error ({res.status_code}): {res.text}")

    result = res.json()
    words_data = result.get("words", [])
    print(f"✅ Groq transcribed {len(words_data)} words in ~1-2 seconds!")

    # Format into visual sentence cards
    pages = []
    page_id = 0
    current_words = []
    current_start = 0.0

    MAX_WORDS = 9
    MAX_DURATION = 3.8

    for word_info in words_data:
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

    with open(output_json_path, "w") as f:
        json.dump(pages, f, indent=2)

    with open("hitchhiker_subtitles.json", "w") as f:
        json.dump(pages, f, indent=2)

    print(f"💾 Saved {len(pages)} subtitle pages to {output_json_path}")
    return pages

if __name__ == "__main__":
    import sys
    audio_file = sys.argv[1] if len(sys.argv) > 1 else "chapter1_intro_clean.mp3"
    transcribe_with_groq(audio_file)
