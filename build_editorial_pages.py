import json

with open("chapters_data/chapter_00_prologue.json") as f:
    cards = json.load(f)

# Flatten words from first 16 cards (~41 seconds)
all_words = []
for c in cards[:16]:
    all_words.extend(c["words"])

# Chunk by sentences and major pauses (16-24 words per page)
pages_words = []
current_chunk = []

for idx, w in enumerate(all_words):
    current_chunk.append(w)
    text = w["text"].strip()
    
    is_sentence_end = text.endswith((".", "!", "?", "—", ";"))
    is_clause_end = text.endswith(",")
    
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

# Build formatted page boundaries
formatted_pages = []
for i, p_words in enumerate(pages_words):
    # Start time of page:
    if i == 0:
        page_start = 0.0
    else:
        # Cut over smoothly in the pause between previous sentence end and new sentence start
        prev_end = pages_words[i - 1][-1]["end"]
        curr_start = p_words[0]["start"]
        # Split point is 0.25s after previous sentence ends or halfway in between
        pause = curr_start - prev_end
        if pause > 0.4:
            page_start = round(prev_end + 0.25, 3)
        else:
            page_start = round(prev_end + pause / 2.0, 3)

    if i + 1 < len(pages_words):
        next_start = pages_words[i + 1][0]["start"]
        curr_end = p_words[-1]["end"]
        pause = next_start - curr_end
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

# Ensure continuous coverage with zero gaps
for i in range(len(formatted_pages) - 1):
    formatted_pages[i]["endTime"] = formatted_pages[i + 1]["startTime"]

total_dur = formatted_pages[-1]["endTime"]

props = {
    "totalDurationSeconds": total_dur,
    "audioFile": "chapters_audio/chapter_00_prologue.mp3",
    "pages": formatted_pages
}

with open("chapters_data/editorial_honda_props.json", "w") as f:
    json.dump(props, f, indent=2)

print(f"Generated {len(formatted_pages)} seamless pages ({total_dur}s):")
for p in formatted_pages:
    print(f"Page {p['id']} [{p['startTime']}s -> {p['endTime']}s] (First word speaks @ {p['words'][0]['start']}s, Last word ends @ {p['words'][-1]['end']}s)")
