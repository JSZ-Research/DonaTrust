import whisper
from elevenlabs.client import ElevenLabs
from moviepy.editor import VideoFileClip, AudioFileClip
import os

# --- 1. Configuration (Using Rachel's Voice) ---
# Note: Keep your API Key secure. Consider using environment variables for production.
ELEVENLABS_API_KEY = "sk_f4b5b8896e27b6adae2639f527d327243f89e24e58f3c968"
client = ElevenLabs(api_key=ELEVENLABS_API_KEY.strip()) 

# Rachel is a pre-set voice available in the free tier
VOICE_ID = "21m00Tcm4TlvDq8ikWAM" 

INPUT_VIDEO_PATH = "/Users/kaius/Project/Language_Translate/your_video.mp4"
OUTPUT_VIDEO_PATH = "final_english_video.mp4"
TEMP_AUDIO_FILE = "temp_voice.mp3"

# --- 2. Transcription & Translation via Whisper ---
print("Starting transcription and translation...")
# Load the 'medium' model for a good balance between speed and accuracy
model = whisper.load_model("medium")

# Setting fp16=False to ensure stability on Mac (CPU/MPS)
result = model.transcribe(INPUT_VIDEO_PATH, task="translate", fp16=False)
translated_text = result["text"]

print(f"Transcription Result: {translated_text[:100]}...")

# --- 3. Speech Synthesis via ElevenLabs ---
print(f"[Status] Converting text to speech with Voice ID: {VOICE_ID}")

try:
    response = client.text_to_speech.convert(
        voice_id=VOICE_ID,
        text=translated_text,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128"
    )

    # Merge audio chunks into a single byte string
    audio_data = b"".join(response)

    with open(TEMP_AUDIO_FILE, "wb") as audio_file:
        audio_file.write(audio_data)
    print("✅ Audio file generated successfully.")

except Exception as error:
    print(f"❌ ElevenLabs Error: {error}")
    exit()

# --- 4. Video Composition ---
print("Merging audio and video tracks...")

video_clip = VideoFileClip(INPUT_VIDEO_PATH)
new_audio_clip = AudioFileClip(TEMP_AUDIO_FILE)

# Replace the original audio with the newly generated English dub
final_video = video_clip.set_audio(new_audio_clip)

# Export the final file (libx264 is highly compatible on macOS)
final_video.write_videofile(OUTPUT_VIDEO_PATH, codec="libx264", audio_codec="aac")

# Resource Cleanup
video_clip.close()
new_audio_clip.close()

if os.path.exists(TEMP_AUDIO_FILE):
    os.remove(TEMP_AUDIO_FILE)

print(f"\n✨ Process complete! Your file is ready at: {OUTPUT_VIDEO_PATH}")
