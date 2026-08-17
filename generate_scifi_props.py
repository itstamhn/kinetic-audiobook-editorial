import json

with open("chapters_data/chapter_00_prologue.json") as f:
    subs = json.load(f)

# Take first 5 cards (~15s)
demo_subs = subs[:5]

props = {
    "headerTitle": "THE HITCHHIKER'S GUIDE TO THE GALAXY • PROLOGUE",
    "totalDurationSeconds": 15.0,
    "audioFile": "chapters_audio/chapter_00_prologue.mp3",
    "subtitles": demo_subs,
    "themeColor": "#00f0ff",
    "accentColor": "#ffd700"
}

with open("chapters_data/scifi_demo_props.json", "w") as f:
    json.dump(props, f, indent=2)

print("Saved chapters_data/scifi_demo_props.json!")
