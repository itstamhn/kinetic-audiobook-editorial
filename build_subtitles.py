import json

with open("transcript_clean.json", "r") as f:
    raw_segments = json.load(f)

# Structure into refined pages/sentences
refined_pages = []

for seg in raw_segments:
    words = seg["words"]
    if not words:
        continue
    
    # Filter and fix word names if needed
    cleaned_words = []
    for w in words:
        word_text = w["word"]
        if "Thivina" in word_text:
            word_text = word_text.replace("Thivina,", "Vivian,")
        cleaned_words.append({
            "text": word_text,
            "start": w["start"],
            "end": w["end"]
        })
    
    if cleaned_words:
        # Check if the sentence is within 30s
        start_time = cleaned_words[0]["start"]
        end_time = cleaned_words[-1]["end"]
        
        if start_time < 30.0:
            refined_pages.append({
                "id": len(refined_pages) + 1,
                "startTime": start_time,
                "endTime": min(end_time + 0.5, 30.0),
                "fullText": " ".join([w["text"] for w in cleaned_words]),
                "words": cleaned_words
            })

# Ensure directory src exists
import os
os.makedirs("src", exist_ok=True)

with open("src/subtitles.json", "w") as f:
    json.dump(refined_pages, f, indent=2)

print(f"Generated {len(refined_pages)} subtitle pages in src/subtitles.json")
for p in refined_pages:
    print(f"Page {p['id']} [{p['startTime']}s -> {p['endTime']}s]: {p['fullText']}")
