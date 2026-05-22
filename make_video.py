import os
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip
import numpy as np

title = os.getenv("TITLE", "Manga Video")
intro_script = os.getenv("INTRO", "")
body_script = os.getenv("BODY", "")

full_script = f"{intro_script}... {body_script}".replace("{", "").replace("}", "").replace('"', '').replace("'", "")

print(f"Processing Video Title: {title}")
audio_path = "output_voice.mp3"
video_path = "final_output.mp4"

# Fast Desi Voice Engine
tts = gTTS(text=full_script, lang='hi', slow=False)
tts.save(audio_path)

audio_clip = AudioFileClip(audio_path)
duration = audio_clip.duration

# Auto Detect: Shorts vs Long
if len(full_script.split()) < 250:
    width, height = 1080, 1920
    print("Auto-Detected Type: Shorts (Vertical)")
else:
    width, height = 1920, 1080
    print("Auto-Detected Type: Long Video (Horizontal)")

img_clip = ImageClip(np.zeros((height, width, 3), dtype=np.uint8)).set_duration(duration)
final_video = img_clip.set_audio(audio_clip)
final_video.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac")

audio_clip.close()
final_video.close()
print("🏁 SUCCESS: Video Rendered perfectly!")
