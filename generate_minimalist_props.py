import json

with open("chapters_data/chapter_00_prologue.json") as f:
    subs = json.load(f)

demo_subs = subs[:10]
total_duration = round(demo_subs[-1]["endTime"], 2)

# Mode 1: Continuous Ink Fill (Silky smooth syllable gradient wipe)
props_continuous_light = {
    "theme": "light-paper",
    "mode": "continuous-ink",
    "headerTitle": "Douglas Adams • The Hitchhiker's Guide to the Galaxy",
    "totalDurationSeconds": total_duration,
    "audioFile": "chapters_audio/chapter_00_prologue.mp3",
    "subtitles": demo_subs
}

# Mode 2: Continuous Ink Fill on Dark Charcoal
props_continuous_dark = {
    "theme": "dark-charcoal",
    "mode": "continuous-ink",
    "headerTitle": "Douglas Adams • The Hitchhiker's Guide to the Galaxy",
    "totalDurationSeconds": total_duration,
    "audioFile": "chapters_audio/chapter_00_prologue.mp3",
    "subtitles": demo_subs
}

# Mode 3: Crisp Word Solid Ink (Zero lag firm reveal)
props_crisp_light = {
    "theme": "light-paper",
    "mode": "crisp-word",
    "headerTitle": "Douglas Adams • The Hitchhiker's Guide to the Galaxy",
    "totalDurationSeconds": total_duration,
    "audioFile": "chapters_audio/chapter_00_prologue.mp3",
    "subtitles": demo_subs
}

with open("chapters_data/props_continuous_light.json", "w") as f:
    json.dump(props_continuous_light, f, indent=2)

with open("chapters_data/props_continuous_dark.json", "w") as f:
    json.dump(props_continuous_dark, f, indent=2)

with open("chapters_data/props_crisp_light.json", "w") as f:
    json.dump(props_crisp_light, f, indent=2)

print("Saved updated props!")
