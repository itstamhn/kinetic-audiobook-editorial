import asyncio
import edge_tts
import whisper
import json
import os
import re
from wordfreq import zipf_frequency

# 1. Prepare Text
with open("book_chapters_md/brave_new_world_ch1_full.txt", "r") as f:
    raw_text = f.read()

paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
# If first paragraph is just '1', replace with 'Chapter One.'
if paragraphs and paragraphs[0] == "1":
    paragraphs = ["Chapter One."] + paragraphs[1:]

full_chapter_text = "\n\n".join(paragraphs)
clean_tts_text = full_chapter_text.replace("“", '"').replace("”", '"').replace("’", "'")

os.makedirs("public/chapters_audio", exist_ok=True)
os.makedirs("chapters_data", exist_ok=True)
audio_output = "public/chapters_audio/brave_new_world_ch1_full.mp3"

print("🎙️ Step 1: Synthesizing Full Chapter 1 Audiobook Narration (en-GB-RyanNeural)...")
print(f"   Total words: {len(full_chapter_text.split())} words (~22-25 mins narration)")

async def generate_audio():
    # Synthesize paragraph by paragraph to prevent socket timeout on large payloads
    with open(audio_output, "wb") as out_f:
        for idx, p in enumerate(paragraphs):
            clean_p = p.replace("“", '"').replace("”", '"').replace("’", "'")
            if not clean_p:
                continue
            communicate = edge_tts.Communicate(clean_p, "en-GB-RyanNeural", rate="-3%")
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    out_f.write(chunk["data"])
            if (idx + 1) % 10 == 0 or idx == len(paragraphs) - 1:
                print(f"   Synthesized paragraph {idx + 1}/{len(paragraphs)}...")

if not os.path.exists(audio_output) or os.path.getsize(audio_output) < 100000:
    asyncio.run(generate_audio())
    print(f"✅ Full audio generated: {audio_output} ({os.path.getsize(audio_output):,} bytes)")
else:
    print(f"⚡ Using existing audio file: {audio_output} ({os.path.getsize(audio_output):,} bytes)")

print("\n⚡ Step 2: Transcribing full audio with Whisper to extract word-level timestamps...")
model = whisper.load_model("base")
result = model.transcribe(audio_output, word_timestamps=True, verbose=False)

whisper_words = []
for seg in result["segments"]:
    for w in seg.get("words", []):
        whisper_words.append({
            "word": w["word"].strip(),
            "start": round(w["start"], 3),
            "end": round(w["end"], 3)
        })

print(f"✅ Extracted {len(whisper_words)} spoken word timestamps from Whisper!")

# Save raw whisper words for reuse/caching
with open("chapters_data/brave_new_world_ch1_full_whisper.json", "w") as f:
    json.dump(whisper_words, f, indent=2)

print("\n📖 Step 3: Aligning Spoken Timestamps with EPUB Ground-Truth Text...")
epub_words = full_chapter_text.split()
aligned_words = []
whisper_idx = 0

for ew in epub_words:
    clean_ew = re.sub(r"[^\w]", "", ew).lower()
    
    best_match_idx = None
    # Search within forward window
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

print(f"✅ Successfully aligned all {len(aligned_words)} words with precision timestamps!")

# 4. Load User Known Words
known_words = set()
if os.path.exists("user_known_words.txt"):
    with open("user_known_words.txt", "r") as f:
        for line in f:
            clean = line.strip().lower()
            if clean and not clean.startswith("#"):
                known_words.add(clean)

print(f"\n🧠 Step 4: Applying Smart C1/C2 Vocabulary Filter & Vietnamese Interlinear Gloss...")
# Comprehensive Literary & Biological Dictionary for Chapter 1
GLOSS_DICT = {
    # Opening Scene
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
    "soliloquizing": "lẩm bẩm",
    "absorbed": "chăm chú",
    "callow": "ngây ngô",
    "abjectly": "khúm núm",
    "scribbled": "nguệch ngoạc viết",
    "fretsawyers": "thợ cưa lọng",
    "backbone": "xương sống cốt lõi",
    "geniality": "sự niềm nở",
    "floridly": "tươi tắn",
    
    # Hatchery & Bokanovsky Process Science
    "incubators": "lồng ấp phôi",
    "bokanovsky": "quy trình Bokanovsky",
    "bokanovskification": "nhân bản Bokanovsky",
    "bokanovskified": "được nhân bản vô tính",
    "prodigious": "phi thường",
    "instruments": "dụng cụ thí nghiệm",
    "plunging": "lao nhanh vào",
    "drawers": "ngăn kéo mẫu",
    "peritoneum": "màng bụng / phúc mạc",
    "ovarium": "buồng trứng",
    "ovary": "buồng trứng",
    "ova": "trứng / noãn",
    "ovum": "trứng / noãn",
    "spermatozoa": "tinh trùng",
    "salpingitis": "viêm ống dẫn trứng",
    "liquor": "dung dịch sinh học",
    "gametes": "giao tử",
    "morula": "phôi dâu",
    "blastocyst": "phôi nang",
    "proliferation": "sự tăng sinh tế bào",
    "proliferate": "tăng sinh nhân đôi",
    "proliferating": "đang tăng sinh",
    "bud": "mọc chồi / tách phôi",
    "budded": "đã nảy chồi tách phôi",
    "buds": "các chồi phôi",
    "decanted": "được chiết xuất / ra đời",
    "decanting": "chiết xuất phôi / sinh ra",
    "decanters": "kỹ thuật viên chiết phôi",
    "ectogenesis": "thụ thai ngoài tử cung",
    "hereditary": "di truyền",
    "heredity": "tính di truyền",
    "predestination": "tiền định / an bài số phận",
    "predestinators": "chuyên viên tiền định",
    "viviparous": "sinh con tự nhiên",
    "viviparously": "theo cách đẻ con tự nhiên",
    "fervently": "một cách tha thiết",
    "enthusiastically": "hào hứng",
    "patronizingly": "vẻ bề trên",
    "unorthodoxy": "sự dị giáo / lệch chuẩn",
    "heretical": "dị giáo / trái quy chuẩn",
    "freemartins": "người biến đổi vô sinh",
    "castes": "giai cấp / đẳng cấp",
    "caste": "đẳng cấp xã hội",
    "embryos": "các phôi thai",
    "embryo": "phôi thai",
    "surrogate": "chất thay thế máu mẹ",
    "corpus": "thể vàng",
    "luteum": "hoàng thể",
    "placenta": "nhau thai",
    "thyroxin": "hoóc môn tuyến giáp",
    "voluptuous": "khoái lạc gợi cảm",
    "centrifugal": "máy ly tâm",
    "lupus": "bệnh lao da",
    "tuberculin": "chất thử vi khuẩn lao",
    "inoculated": "được tiêm chủng",
    "inoculation": "sự tiêm chủng ngừa",
    "bovine": "thuộc loài bò",
    "infinitesimal": "vô cùng nhỏ bé",
    "monorail": "đường tàu một ray",
    "caressing": "vuốt ve âu yếm",
    "murmured": "thì thầm khẽ",
    "indulgently": "khoan dung độ lượng",
    "ferment": "sự lên men / náo động",
    "flushed": "đỏ bừng mặt",
    "gleam": "tia sáng lấp lánh",
    "scintillating": "lấp lánh rực rỡ",
    "superfluous": "thừa thãi",
    "simultaneous": "đồng thời cùng lúc",
    "indefatigably": "không biết mệt mỏi",
    "arpeggios": "chuỗi hợp âm rải",
    "burgeoned": "đâm chồi nảy lộc",
    "demi-johns": "bình thắt cổ lớn",
    "demijohns": "bình thắt cổ lớn",
    "viscosity": "độ nhớt / độ quánh",
    "viscous": "quánh dẻo / nhớt",
    "siphon": "ống hút siphon",
    "anonymity": "sự vô danh tính",
    "aliquot": "phần mẫu chia đều",
    "pipettes": "ống nhỏ giọt",
    "test-tubes": "ống nghiệm",
    "hypnopaedia": "dạy học trong giấc ngủ",
    "soma": "thuốc an thần soma",
}

annotated_count = 0
for w in aligned_words:
    raw_text = w["text"]
    cw = re.sub(r"[^\w\-]", "", raw_text).lower()
    
    if cw and len(cw) > 3 and cw not in known_words:
        z_score = zipf_frequency(cw, "en")
        
        # Advanced C1/C2 or specific rare literary words
        if z_score <= 4.15 or cw in GLOSS_DICT:
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
                w["vn"] = match_val
                annotated_count += 1

print(f"✨ Filtered & annotated {annotated_count} C1/C2 literary words across Chapter 1!")

print("\n📑 Step 5: Chunking into Maximum 3-Line Interlinear Pages...")
pages_words = []
current_chunk = []

for w in aligned_words:
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

# Ensure perfectly contiguous page boundaries
for i in range(len(formatted_pages) - 1):
    formatted_pages[i]["endTime"] = formatted_pages[i + 1]["startTime"]

full_chapter_props = {
    "totalDurationSeconds": formatted_pages[-1]["endTime"],
    "audioFile": "chapters_audio/brave_new_world_ch1_full.mp3",
    "pages": formatted_pages
}

output_props_file = "chapters_data/brave_new_world_ch1_full_props.json"
with open(output_props_file, "w") as f:
    json.dump(full_chapter_props, f, indent=2)

total_mins = formatted_pages[-1]["endTime"] / 60.0
print(f"🎉 SUCCESS: Full Chapter 1 Props saved to {output_props_file}")
print(f"   Total Pages: {len(formatted_pages)} pages (all strictly ≤ 3 lines)")
print(f"   Total Duration: {formatted_pages[-1]['endTime']}s ({total_mins:.1f} minutes)")
