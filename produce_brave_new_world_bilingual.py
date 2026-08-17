import json
import re

GLOSS_DICT = {
    # Page 1-5
    "squat": "thấp bè",
    "stories": "tầng lầu",
    "entrance": "lối vào",
    "hatchery": "lò ấp phôi",
    "conditioning": "điều kiện hóa",
    "shield": "chiếc khiên",
    "motto": "khẩu hiệu",
    "community": "cộng đồng",
    "identity": "đồng nhất",
    "stability": "ổn định",
    "enormous": "khổng lồ",
    "panes": "ô kính",
    "tropical": "nhiệt đới",
    
    # Page 6-10
    "harsh": "gay gắt",
    "glared": "chói lòa",
    "hungrily": "thèm thuồng",
    "seeking": "tìm kiếm",
    "draped": "phủ rèm",
    "lay": "người mẫu nộm",
    "pallid": "tái nhợt",
    "academic": "hàn lâm",
    "goose-flesh": "nổi gai ốc",
    "nickel": "kim loại kền",
    "bleakly": "lạnh lẽo",
    "porcelain": "men sứ",
    "laboratory": "phòng thí nghiệm",
    "wintriness": "giá lạnh",
    "overalls": "bộ bảo hộ",
    "gloved": "đeo găng",
    "corpse-coloured": "trắng bệch",
    
    # Page 11-15
    "frozen": "băng giá",
    "ghost": "bóng ma",
    "barrels": "ống kính",
    "microscopes": "kính hiển vi",
    "substance": "chất liệu",
    "polished": "bóng loáng",
    "tubes": "ống nghiệm",
    "streak": "vệt óng",
    "luscious": "mỡ màng",
    "recession": "thụt lùi xa",
    "director": "giám đốc",
    "fertilizing": "thụ tinh",
    
    # Page 16-20
    "instruments": "thiết bị",
    "fertilizers": "kỹ thuật viên thụ tinh",
    "plunged": "chìm đắm",
    "scarcely": "hầu như không",
    "soliloquizing": "lẩm bẩm",
    "absorbed": "chăm chú",
    "concentration": "tập trung",
    "troop": "đoàn",
    "callow": "ngây ngô",
    "abjectly": "khúm núm",
    "heels": "gót chân",
    
    # Page 21-25
    "notebook": "sổ tay",
    "desperately": "cuống cuồng",
    "scribbled": "ghi chép",
    "privilege": "đặc ân",
    "departments": "phòng ban",
    "conducting": "dẫn đường",
    
    # Page 26-30
    "intelligently": "thấu đáo",
    "society": "xã hội",
    "particulars": "chi tiết cụ thể",
    "virtue": "đức hạnh",
    "happiness": "hạnh phúc",
    "generalities": "khái niệm chung",
    "intellectually": "trí tuệ",
    "evils": "điều xấu",
    "philosophers": "triết gia",
    "fretsawyers": "thợ cưa lọng",
    "collectors": "người sưu tầm",
    "backbone": "xương sống",
    
    # Page 31-35
    "menacing": "đầy đe dọa",
    "geniality": "sự niềm nở",
    "settling": "bắt tay vào",
    "meanwhile": "trong lúc đó",
    "upright": "thẳng thắn",
    "advanced": "tiến bước",
    
    # Page 36-41
    "prominent": "nhô ra",
    "floridly": "tươi tắn",
    "occur": "nghĩ đến",
}

with open("chapters_data/brave_new_world_ch1_props.json", "r") as f:
    orig = json.load(f)

# Flatten all words
all_words = []
for p in orig["pages"]:
    for w in p["words"]:
        # Clean copy
        clean_w = {
            "text": w["text"],
            "start": w["start"],
            "end": w["end"]
        }
        
        # Check translation
        raw_text = w["text"]
        cw = re.sub(r"[^\w\-]", "", raw_text).lower()
        if cw in GLOSS_DICT:
            clean_w["vn"] = GLOSS_DICT[cw]
        elif cw.rstrip("s") in GLOSS_DICT and len(cw) > 4:
            clean_w["vn"] = GLOSS_DICT[cw.rstrip("s")]
        elif cw.rstrip("ed") in GLOSS_DICT and len(cw) > 5:
            clean_w["vn"] = GLOSS_DICT[cw.rstrip("ed")]
        elif cw.rstrip("ing") in GLOSS_DICT and len(cw) > 5:
            clean_w["vn"] = GLOSS_DICT[cw.rstrip("ing")]
            
        all_words.append(clean_w)

# Re-chunk with tight boundaries for maximum 3 lines
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

print(f"🎉 Generated {len(formatted_pages)} bilingual pages (max 3 lines) to {output_file}!")
