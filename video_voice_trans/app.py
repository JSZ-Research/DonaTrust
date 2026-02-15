import os
import uuid
import whisper
from flask import Flask, request, send_file, jsonify, render_template
from flask_cors import CORS
from elevenlabs.client import ElevenLabs
from moviepy.editor import VideoFileClip, AudioFileClip

app = Flask(__name__)
CORS(app)

# --- 1. 配置 ---
ELEVENLABS_KEY = "sk_f4b5b8896e27b6adae2639f527d327243f89e24e58f3c968"
client = ElevenLabs(api_key=ELEVENLABS_KEY.strip())
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# 确保文件夹存在
os.makedirs("uploads", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

# 预加载模型（启动时加载）
print("Loading Whisper model (base)...")
model = whisper.load_model("base") 

@app.route('/')
def home():
    # Flask 会自动去 templates 文件夹寻找 index.html
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file uploaded"}), 400

    video_file = request.files['video']
    task_id = str(uuid.uuid4())
    input_path = os.path.join("uploads", f"{task_id}_in.mp4")
    output_path = os.path.join("outputs", f"{task_id}_out.mp4")
    temp_audio = f"{task_id}_voice.mp3"

    try:
        # 保存上传的文件
        video_file.save(input_path)

        # 1. Whisper 识别并翻译
        print(f"[{task_id}] Step 1: Transcribing...")
        result = model.transcribe(input_path, task="translate", fp16=False)
        full_english_text = result["text"]

        # 2. ElevenLabs 生成英语配音
        print(f"[{task_id}] Step 2: Generating voice...")
        response = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            text=full_english_text,
            model_id="eleven_multilingual_v2"
        )
        audio_bytes = b"".join(response)
        with open(temp_audio, "wb") as f:
            f.write(audio_bytes)

        # 3. 合成最终视频
        print(f"[{task_id}] Step 3: Merging audio and video...")
        video_clip = VideoFileClip(input_path)
        new_audio_clip = AudioFileClip(temp_audio)
        
        final_video = video_clip.set_audio(new_audio_clip)
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac", logger=None)

        # 关闭释放文件资源
        video_clip.close()
        new_audio_clip.close()
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

        # 返回处理好的文件
        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 启动服务器
    app.run(debug=True, port=5000)
