import os
import whisper
from flask import Flask, render_template, request, send_file
from elevenlabs.client import ElevenLabs
from moviepy.editor import VideoFileClip, AudioFileClip

app = Flask(__name__)

# --- 配置 ---
# 使用 .strip() 防止复制时带入不可见的空格或换行
ELEVENLABS_KEY = "sk_f4b5b8896e27b6adae2639f527d327243f89e24e58f3c968".strip()
client = ElevenLabs(api_key=ELEVENLABS_KEY)

# 预加载模型（建议在全局加载，避免每次上传都重新下载）
print("正在加载 Whisper 模型...")
model = whisper.load_model("base") # 如果内存充裕可改为 "medium"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        return "未选择视频文件", 400
    
    video_file = request.files['video']
    voice_id = request.form.get('voice', '21m00Tcm4TlvDq8ikWAM')

    # 定义固定的临时文件名，避免中文路径编码问题
    input_path = "input_temp.mp4"
    temp_audio = "temp_voice.mp3"
    output_path = "final_output.mp4"

    try:
        # 1. 保存上传文件
        video_file.save(input_path)
        print(f"文件已保存至: {input_path}")

        # 2. Whisper 识别并翻译
        print("正在识别并翻译文本...")
        result = model.transcribe(input_path, task="translate", fp16=False)
        full_text = result["text"].strip()
        
        if not full_text:
            return "未能识别到有效文本", 400
        print(f"翻译文本预览: {full_text[:50]}...")

        # 3. ElevenLabs 生成配音
        print(f"正在请求 ElevenLabs 配音 (Voice ID: {voice_id})...")
        response = client.text_to_speech.convert(
            voice_id=voice_id,
            text=full_text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )

        # 合并数据流并写入文件
        audio_chunks = b"".join(response)
        with open(temp_audio, "wb") as f:
            f.write(audio_chunks)

        # 检查音频文件是否真实存在且不为空
        if not os.path.exists(temp_audio) or os.path.getsize(temp_audio) == 0:
            return "配音生成失败，请检查 API 额度", 500

        # 4. MoviePy 合成视频
        print("正在合成视频轨道...")
        video_clip = VideoFileClip(input_path)
        new_audio_clip = AudioFileClip(temp_audio)

        # 确保音频时长适配
        final_video = video_clip.set_audio(new_audio_clip)

        # 核心修复：明确指定 audio_codec 并添加 temp_audiofile 避免写入冲突
        final_video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            fps=video_clip.fps
        )

        # 关闭句柄释放文件
        video_clip.close()
        new_audio_clip.close()

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        print(f"发生错误: {str(e)}")
        return f"处理失败: {str(e)}", 500
    
    finally:
        # 清理临时文件（可选，建议保留 output 供下载）
        for f in [input_path, temp_audio]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except:
                    pass

if __name__ == '__main__':
    # 启用 threaded=False 解决某些系统下 MoviePy 的线程安全问题
    app.run(debug=True, port=5001, threaded=False)
