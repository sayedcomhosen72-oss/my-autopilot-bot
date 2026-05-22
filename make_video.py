import os
from gtts import gTTS
# Advanced modular imports for MoviePy v2.x stability
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ColorClip

# Fetching real-time inputs injected via GitHub Action Environment from Make.com
title = os.getenv("TITLE", "Manga_Autopilot_Video")
intro_text = os.getenv("INTRO", "Namaskar dosto, swagat hai aapka.")
body_text = os.getenv("BODY", "Aaj ki kahani bohot dilchasp hone wali hai.")

full_script = f"{intro_text} {body_text}"

print("[ENGINE] Step 1: Generating Voiceover with gTTS...")
tts = gTTS(text=full_script, lang='hi', slow=False)
audio_path = "voiceover.mp3"
tts.save(audio_path)

print("[ENGINE] Step 2: Extracting Voice Timeline data...")
audio_clip = AudioFileClip(audio_path)
duration = audio_clip.duration
print(f"[ENGINE] Calculated Video Timeline Duration: {duration} seconds.")

print("[ENGINE] Step 3: Binding Canvas Layout with dynamic structure...")
# Generating a 1080x1920 portrait format black canvas for the video track
base_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
final_video = base_clip.with_audio(audio_clip)

output_path = "final_output.mp4"
print("[ENGINE] Step 4: Initiating High-Performance Video Rendering...")
final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

print(f"[SUCCESS] Automation Pipeline completed. File generated at: {output_path}")
