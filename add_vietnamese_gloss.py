import json
import re

# Comprehensive literary dictionary for Chapter 1
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
    data = json.load(f)

annotated_count = 0
for page in data["pages"]:
    for word_info in page["words"]:
        raw_text = word_info["text"]
        clean_word = re.sub(r"[^\w\-]", "", raw_text).lower()
        
        # Check direct match or stem
        if clean_word in GLOSS_DICT:
            word_info["vn"] = GLOSS_DICT[clean_word]
            annotated_count += 1
        elif clean_word.rstrip("s") in GLOSS_DICT and len(clean_word) > 4:
            word_info["vn"] = GLOSS_DICT[clean_word.rstrip("s")]
            annotated_count += 1
        elif clean_word.rstrip("ed") in GLOSS_DICT and len(clean_word) > 5:
            word_info["vn"] = GLOSS_DICT[clean_word.rstrip("ed")]
            annotated_count += 1
        elif clean_word.rstrip("ing") in GLOSS_DICT and len(clean_word) > 5:
            word_info["vn"] = GLOSS_DICT[clean_word.rstrip("ing")]
            annotated_count += 1

with open("chapters_data/brave_new_world_ch1_props.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"✅ Annotated {annotated_count} difficult/literary words with Vietnamese translations!")
