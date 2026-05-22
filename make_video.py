import os
from gtts import gTTS
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ColorClip

# Fetching data and stripping spaces
intro_text = os.getenv("INTRO", "").strip()
body_text = os.getenv("BODY", "").strip()

# BACKUP LOGIC: Agar Make.com se text khali aaya, toh yeh auto-detect karke testing text daal dega
if not intro_text and not body_text:
    print("[WARNING] Make.com data was empty! Using local backup script for testing.")
    full_script = "Namaskar dosto! Hamara automated video engine ab bilkul sahi se kaam kar raha hai."
else:
    full_script = f"{intro_text} {body_text}".strip()

print("[ENGINE] Step 1: Generating Voiceover with gTTS...")
tts = gTTS(text=full_script, lang='hi', slow=False)
audio_path = "voiceover.mp3"
tts.save(audio_path)

print("[ENGINE] Step 2: Loading Audio Timeline...")
audio_clip = AudioFileClip(audio_path)
duration = audio_clip.duration
print(f"[ENGINE] Calculated Duration: {duration} seconds.")

print("[ENGINE] Step 3: Binding Canvas Layout...")
base_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=duration)
final_video = base_clip.with_audio(audio_clip)

output_path = "final_output.mp4"
print("[ENGINE] Step 4: Initiating Video Rendering...")
final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

print(f"[SUCCESS] Automation Pipeline completed! File generated at: {output_path}")
