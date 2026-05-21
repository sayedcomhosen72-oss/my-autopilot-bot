import os
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from gtts import gTTS
from moviepy.editor import AudioFileClip, ImageClip
import numpy as np

app = FastAPI()
API_SECRET_KEY = "HomieBotSecret123"

class VideoRequest(BaseModel):
    title: str
    intro_script: str
    body_script: str

def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if authorization.split(" ")[1] != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/render-video")
async def render_video(request: VideoRequest, authorized: str = Depends(verify_token)):
    try:
        full_script = f"{request.intro_script}... {request.body_script}"
        full_script = full_script.replace("{", "").replace("}", "").replace('"', '').replace("'", "")
        
        audio_path, video_path = "output_voice.mp3", "final_output.mp4"
        
        # Unstoppable Desi gTTS Engine
        tts = gTTS(text=full_script, lang='hi', slow=False)
        tts.save(audio_path)
        
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            raise HTTPException(status_code=500, detail="Voice generation failed")
            
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        # 🔥 TUMHARA SMART LOGIC: Auto Detect Short vs Long
        # Agar poori kahani 250 shabdon se choti hai toh Shorts, nahi toh Long Video
        if len(full_script.split()) < 250:
            # Shorts Format: Vertical (Width: 1080, Height: 1920)
            width, height = 1080, 1920
            video_type = "Shorts (Vertical)"
        else:
            # Long Video Format: Horizontal (Width: 1920, Height: 1080)
            width, height = 1920, 1080
            video_type = "Long Video (Horizontal)"
            
        # Video Frame Generation based on above size
        img_clip = ImageClip(np.zeros((height, width, 3), dtype=np.uint8)).set_duration(duration)
        final_video = img_clip.set_audio(audio_clip)
        final_video.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac")
        
        audio_clip.close()
        final_video.close()
        
        return {
            "status": "success", 
            "detected_type": video_type,
            "video_url": f"Lifetime Autopilot {video_type} Generated Successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
