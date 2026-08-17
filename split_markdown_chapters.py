import os
import re
import json

with open("hitchhiker_guide/1-Douglas_Adams_-_The_Hitch_Hikers_Guide_to_Galaxy_split_000.md", "r") as f:
    md0 = f.read()

with open("hitchhiker_guide/2-Douglas_Adams_-_The_Hitch_Hikers_Guide_to_Galaxy_split_001.md", "r") as f:
    md1 = f.read()

full_md = md0 + "\n\n" + md1
OUT_MD_DIR = "book_chapters_md"
os.makedirs(OUT_MD_DIR, exist_ok=True)

# Find all chapter splits
# Prologue
pro_idx = full_md.find("Far out in the uncharted backwaters")
prologue_text = full_md[pro_idx:]

# Find where chapters are formatted
pattern = r"\n\s*(\d{1,2})\s*\n"
splits = list(re.finditer(pattern, prologue_text))

print(f"Found {len(splits)} chapter breaks in Markdown:")

chapters_md = []

# Prologue
p_end = splits[0].start()
p_body = prologue_text[:p_end].strip()
chapters_md.append({
    "num": 0,
    "name": "Prologue",
    "filename": "chapter_00_prologue.md",
    "text": p_body
})

for idx, sp in enumerate(splits):
    ch_num = int(sp.group(1))
    start_p = sp.end()
    end_p = splits[idx + 1].start() if idx + 1 < len(splits) else len(prologue_text)
    ch_body = prologue_text[start_p:end_p].strip()
    chapters_md.append({
        "num": ch_num,
        "name": f"Chapter {ch_num:02d}",
        "filename": f"chapter_{ch_num:02d}.md",
        "text": ch_body
    })

for ch in chapters_md:
    path = os.path.join(OUT_MD_DIR, ch["filename"])
    with open(path, "w") as f:
        f.write(f"# {ch['name']}\n\n{ch['text']}\n")
    first_line = ch["text"].splitlines()[0] if ch["text"].splitlines() else ""
    print(f"  📝 Saved {ch['filename']} ({len(ch['text'])} chars) | '{first_line[:50]}...'")

print(f"\n🎉 Saved all {len(chapters_md)} clean Markdown chapters to {OUT_MD_DIR}/")
