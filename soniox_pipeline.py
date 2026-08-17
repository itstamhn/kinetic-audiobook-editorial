import os
import sys
import json
import subprocess
import requests
from groq_whisper import transcribe_with_groq

SONIOX_API_KEY = os.environ.get("SONIOX_API_KEY", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

def generate_soniox_tts(
    text: str,
    output_path: str = "public/audio_30s.mp3",
    voice: str = "Adrian",
    model: str = "tts-rt-v2",
    speed: float = 1.0,
    reduce_silence: bool = False
):
    """
    Generate speech using Soniox Text-to-Speech REST API v2.
    """
    if not SONIOX_API_KEY:
        print("❌ Error: SONIOX_API_KEY environment variable not found.")
        print("Run this script with Sigillo:")
        print("   sigillo run -- python3 soniox_pipeline.py \"your text here\"")
        return False

    url = "https://tts-rt.soniox.com/tts"
    headers = {
        "Authorization": f"Bearer {SONIOX_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "text": text,
        "model": model,
        "language": "en",
        "voice": voice,
        "audio_format": "mp3",
        "speed": speed,
        "reduce_silence": reduce_silence
    }

    print(f"🎙️ Generating Soniox TTS ({model}, voice='{voice}', speed={speed})...")
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Soniox audio saved to: {output_path} ({len(response.content)} bytes)")
        return True
    else:
        print(f"❌ Soniox API Error {response.status_code}: {response.text}")
        return False

def extract_timestamps(audio_file: str = "public/audio_30s.mp3", output_json: str = "src/subtitles.json"):
    """
    Extracts word-level timestamps with Groq Whisper (whisper-large-v3-turbo).
    """
    if GROQ_API_KEY:
        return transcribe_with_groq(audio_file, output_json)
    else:
        # Fallback to local whisper if Groq API key is missing
        print("⚠️ Groq API key not found, using local Whisper...")
        import whisper
        model = whisper.load_model("base.en")
        result = model.transcribe(audio_file, word_timestamps=True)
        # format and save
        pages = []
        for idx, seg in enumerate(result["segments"]):
            words = [{"text": w["word"].strip(), "start": round(w["start"], 3), "end": round(w["end"], 3)} for w in seg.get("words", []) if w["word"].strip()]
            if words:
                pages.append({"id": idx, "startTime": words[0]["start"], "endTime": words[-1]["end"], "fullText": " ".join([w["text"] for w in words]), "words": words})
        with open(output_json, "w") as f:
            json.dump(pages, f, indent=2)
        return pages

def render_video(composition_id: str = "Hitchhiker-Highlight-60s", output_video: str = "out/output_video_60fps.mp4"):
    """
    Renders 60 FPS 16:9 YouTube video using Remotion.
    """
    print(f"🎬 Rendering 60 FPS 16:9 YouTube video with Remotion ({composition_id})...")
    subprocess.run([
        "npx", "remotion", "render",
        "src/index.ts",
        composition_id,
        output_video,
        "--concurrency", "8"
    ], check=True)
    print(f"🎉 Final 60fps Video Ready: {output_video}")

if __name__ == "__main__":
    script_text = (
        "Today we are going to be doing a day in the life running a dental marketing agency. "
        "In the morning I have got a couple of client calls and our daily morning team huddle. "
        "We essentially just go through what we have planned for the day and any blockers. "
        "I have got a creative strategy call with a client alongside our creative strategist."
    )

    if len(sys.argv) > 1:
        script_text = " ".join(sys.argv[1:])

    print("==================================================")
    print(" Soniox TTS v2 -> Groq Whisper -> Remotion 60FPS ")
    print("==================================================")

    success = generate_soniox_tts(script_text, "public/audio_30s.mp3", voice="Adrian")
    if success:
        subprocess.run(["cp", "public/audio_30s.mp3", "audio_30s.mp3"])
        extract_timestamps("public/audio_30s.mp3")
        render_video("KineticTypography-YouTube-16x9", "out/soniox_groq_video_60fps.mp4")
