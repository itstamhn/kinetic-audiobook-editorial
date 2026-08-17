import os
import requests

key = os.environ.get("SONIOX_API_KEY", "")
url = "https://tts-rt.soniox.com/tts"
headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

text = (
    "Today we are going to be doing a day in the life. "
    "In the morning I have got a couple of calls. "
    "We have got our morning huddle of course, which is how we start every single day. "
    "We essentially just go through what we have planned for the day and any blockers. "
    "I have got a creative strategy call with a client alongside Vivian, our creative strategist."
)

voices = [
    ("Daniel", "Male - Clear, confident narrative"),
    ("Adrian", "Male - Natural, warm editorial tone"),
    ("Miles", "Male - Casual, conversational creator"),
    ("Emma", "Female - Articulate, modern voiceover"),
    ("Nora", "Female - Calm, elegant storytelling"),
    ("Owen", "Male - Energetic, engaging pacing")
]

os.makedirs("soniox_voices", exist_ok=True)

for voice_id, desc in voices:
    payload = {
        "model": "tts-rt-v2",
        "language": "en",
        "voice": voice_id,
        "audio_format": "mp3",
        "text": text,
        "sample_rate": 24000,
        "speed": 1.0,
        "reduce_silence": False
    }
    
    print(f"Generating {voice_id} ({desc})...")
    res = requests.post(url, headers=headers, json=payload, timeout=20)
    
    if res.status_code == 200:
        filename = f"soniox_voices/soniox_v2_{voice_id.lower()}.mp3"
        with open(filename, "wb") as f:
            f.write(res.content)
        print(f"  ✅ Saved: {filename} ({len(res.content)} bytes)")
    else:
        print(f"  ❌ Failed {voice_id}: {res.status_code} {res.text}")

print("\n🎉 All Soniox TTS v2 voices generated!")
