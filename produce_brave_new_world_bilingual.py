import json
import re
import os
from wordfreq import zipf_frequency

# 1. Load User Known Words
known_words = set()
if os.path.exists("user_known_words.txt"):
    with open("user_known_words.txt", "r") as f:
        for line in f:
            clean = line.strip().lower()
            if clean and not clean.startswith("#"):
                known_words.add(clean)

print(f"📖 Loaded {len(known_words)} words from personal known words list.")

# 2. Literary Dictionary for Rare/Advanced C1/C2 Words
GLOSS_DICT = {
    # High-value C1/C2 and literary vocabulary
    "squat": "thấp bè",
    "hatchery": "lò ấp phôi",
    "conditioning": "điều kiện hóa",
    "motto": "khẩu hiệu",
    "panes": "ô kính",
    "harsh": "gay gắt",
    "glared": "chói lòa",
    "draped": "phủ rèm",
    "lay": "người mẫu nộm",
    "pallid": "tái nhợt",
    "goose-flesh": "nổi gai ốc",
    "nickel": "kim loại kền",
    "bleakly": "lạnh lẽo",
    "porcelain": "men sứ",
    "wintriness": "giá lạnh",
    "overalls": "bộ bảo hộ",
    "corpse-coloured": "trắng bệch",
    "barrels": "ống kính",
    "microscopes": "kính hiển vi",
    "streak": "vệt óng",
    "luscious": "mỡ màng",
    "recession": "thụt lùi xa",
    "fertilizing": "thụ tinh nhân tạo",
    "fertilizers": "kỹ thuật viên thụ tinh",
    "plunged": "chìm đắm",
    "scarcely": "hầu như không",
    "soliloquizing": "lẩm bẩm độc thoại",
    "absorbed": "chăm chú",
    "callow": "ngây ngô non nớt",
    "abjectly": "khúm núm",
    "scribbled": "nguệch ngoạc viết",
    "fretsawyers": "thợ cưa lọng",
    "backbone": "xương sống cốt lõi",
    "geniality": "sự niềm nở",
    "floridly": "tươi tắn phây phây",
}

# 3. Read Original Timestamped Words
with open("chapters_data/brave_new_world_ch1_props.json", "r") as f:
    orig = json.load(f)

# Flatten words
all_words = []
annotated_count = 0

for p in orig["pages"]:
    for w in p["words"]:
        clean_w = {
            "text": w["text"],
            "start": w["start"],
            "end": w["end"]
        }
        
        raw_text = w["text"]
        cw = re.sub(r"[^\w\-]", "", raw_text).lower()
        
        if cw and len(cw) > 3 and cw not in known_words:
            z_score = zipf_frequency(cw, "en")
            
            # C1/C2 threshold: Zipf <= 4.10 AND in glossary
            if z_score <= 4.15:
                # Check exact or stem
                match_val = None
                if cw in GLOSS_DICT:
                    match_val = GLOSS_DICT[cw]
                elif cw.rstrip("s") in GLOSS_DICT and len(cw) > 4:
                    match_val = GLOSS_DICT[cw.rstrip("s")]
                elif cw.rstrip("ed") in GLOSS_DICT and len(cw) > 5:
                    match_val = GLOSS_DICT[cw.rstrip("ed")]
                elif cw.rstrip("ing") in GLOSS_DICT and len(cw) > 5:
                    match_val = GLOSS_DICT[cw.rstrip("ing")]
                    
                if match_val:
                    clean_w["vn"] = match_val
                    annotated_count += 1
                    
        all_words.append(clean_w)

print(f"✨ Filtered & annotated {annotated_count} strictly ADVANCED/C1/C2 words!")

# 4. Re-chunk with tight boundaries for maximum 3 lines
pages_words = []
current_chunk = []

for w in all_words:
    current_chunk.append(w)
    text = w["text"].strip()
    
    is_sentence_end = any(text.endswith(p) for p in [".", "!", "?", '."', '!"', '?"', "—", ";", ":"])
    is_clause_end = text.endswith(",") or text.endswith('",')
    
    if len(current_chunk) >= 5 and is_sentence_end:
        pages_words.append(current_chunk)
        current_chunk = []
    elif len(current_chunk) >= 7 and is_clause_end:
        pages_words.append(current_chunk)
        current_chunk = []
    elif len(current_chunk) >= 9:
        pages_words.append(current_chunk)
        current_chunk = []

if current_chunk:
    if len(current_chunk) < 4 and len(pages_words) > 0:
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

bilingual_props = {
    "totalDurationSeconds": formatted_pages[-1]["endTime"],
    "audioFile": "chapters_audio/brave_new_world_ch1.mp3",
    "pages": formatted_pages
}

output_file = "chapters_data/brave_new_world_ch1_props.json"
with open(output_file, "w") as f:
    json.dump(bilingual_props, f, indent=2)

print(f"🎉 Generated {len(formatted_pages)} personalized bilingual pages to {output_file}!")
