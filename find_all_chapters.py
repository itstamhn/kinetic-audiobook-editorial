import json
import re

with open("full_audiobook_words.json", "r") as f:
    words = json.load(f)

# Reconstruct text with word indices
tokens = [w["text"].strip() for w in words]
full_text = " ".join(tokens)

# Known iconic chapter opening markers
chapter_markers = [
    ("Prologue", "Far out in the uncharted backwaters"),
    ("Chapter 01", "The house stood on a slight rise"),
    ("Chapter 02", "By a curious coincidence"),
    ("Chapter 03", "Human beings are great adapters"),
    ("Chapter 04", "The Vogon Constructor Fleet coasted away"),
    ("Chapter 05", "Prostetnic Vogon Jeltz was not a pleasant sight"),
    ("Chapter 06", "Somewhere in a small dark cabin"),
    ("Chapter 07", "Prostetnic Vogon Jeltz heaved his unpleasant"),
    ("Chapter 08", "The Hitchhiker's Guide to the Galaxy is a wholly remarkable book"),
    ("Chapter 09", "A computer chatted to itself"),
    ("Chapter 10", "The Infinite Improbability Drive is a wonderful new method"),
    ("Chapter 11", "The improbability proof control cabin"),
    ("Chapter 12", "The Encyclopedia Galactica defines a robot"),
    ("Chapter 13", "A loud clatter of gunk music"),
    ("Chapter 14", "Zaphod looked about him at Ford"),
    ("Chapter 15", "Far back in the midst of ancient time"),
    ("Chapter 16", "Arthur awoke to the sound of argument"),
    ("Chapter 17", "More of the planet was unfolding beneath them"),
    ("Chapter 18", "Stress and nervous tension are now serious social problems"),
    ("Chapter 19", "At which point a strange and inexplicable sound"),
    ("Chapter 20", "This time the fanfare was quite perfunctory"),
    ("Chapter 21", "The image of the missiles on the screen became larger"),
    ("Chapter 22", "Another thing that got forgotten"),
    ("Chapter 23", "Good afternoon, boys"),
    ("Chapter 24", "Five figures wandered slowly over the blighted land"),
    ("Chapter 25", "Zaphod marched quickly down the passageway"),
    ("Chapter 26", "The Hitchhiker's Guide to the Galaxy is a very unevenly edited book"),
    ("Chapter 27", "Arthur practically walked into the old man"),
    ("Chapter 28", "It is an important and popular fact that things are not always what they seem"),
    ("Chapter 29", "The air car shot forward straight into the circle of light"),
    ("Chapter 30", "Deep Thought was a computer"),
    ("Chapter 31", "There was a long silence on the bridge"),
    ("Chapter 32", "The Answer to the Great Question"),
    ("Chapter 33", "The air car coasted on"),
    ("Chapter 34", "Arthur Dent sat at a small table"),
    ("Chapter 35", "The mice were not pleased")
]

print("Searching for chapter boundaries in 46,641 words...")

found_chapters = []

for ch_name, marker in chapter_markers:
    marker_words = marker.lower().split()
    first_w = marker_words[0]
    
    match_idx = None
    for i in range(len(tokens) - len(marker_words)):
        if tokens[i].lower().replace("'", "").replace('"', '') == first_w.replace("'", ""):
            # Check subsequence match
            sub = " ".join([tokens[i+j].lower().replace("'", "").replace('"', '').replace(",", "").replace(".", "") for j in range(len(marker_words))])
            target = " ".join([mw.lower().replace("'", "").replace('"', '').replace(",", "").replace(".", "") for mw in marker_words])
            if target in sub:
                match_idx = i
                break
                
    if match_idx is not None:
        start_time = words[match_idx]["start"]
        found_chapters.append({
            "name": ch_name,
            "word_index": match_idx,
            "start_time": start_time,
            "marker": marker
        })
        mins = start_time / 60
        print(f"✅ {ch_name:12s} at {mins:05.2f}m ({start_time:07.1f}s) -> '{marker}'")
    else:
        print(f"⚠️ {ch_name:12s} marker not found: '{marker}'")

print(f"\nFound {len(found_chapters)} / {len(chapter_markers)} chapters!")

# Calculate start and end times
manifest = []
for idx, ch in enumerate(found_chapters):
    start_t = ch["start_time"]
    end_t = found_chapters[idx + 1]["start_time"] if idx + 1 < len(found_chapters) else words[-1]["end"]
    duration = end_t - start_t
    
    start_w_idx = ch["word_index"]
    end_w_idx = found_chapters[idx + 1]["word_index"] if idx + 1 < len(found_chapters) else len(words)
    ch_words = words[start_w_idx:end_w_idx]
    
    manifest.append({
        "chapter_index": idx,
        "name": ch["name"],
        "start_time": round(start_t, 2),
        "end_time": round(end_t, 2),
        "duration_seconds": round(duration, 2),
        "duration_minutes": round(duration / 60, 2),
        "word_count": len(ch_words),
        "marker": ch["marker"]
    })

with open("chapters_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("\nSaved chapters_manifest.json!")
