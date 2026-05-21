import os
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import pyttiktok
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
    token = authorization.split(" ")[1]
    if token != API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")

@app.post("/render-video")
async def render_video(request: VideoRequest, authorized: str = Depends(verify_token)):
    try:
        full_script = f"{request.intro_script} {request.body_script}"
        audio_path = "output_voice.mp3"
        video_path = "final_output.mp4"
        
        # 100% Free & Super Natural Human-like Voice
        # 'en_us_006' is the famous crispy story-teller voice
        pyttiktok.save_audio(full_script, 'en_us_006', audio_path)
        
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Voice generation failed")
            
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        img_clip = ImageClip(np.zeros((1080, 1920, 3), dtype=np.uint8)).set_duration(duration)
        final_video = img_clip.set_audio(audio_clip)
        final_video.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac")
        
        audio_clip.close()
        final_video.close()
        
        return {"status": "success", "video_url": "Super Natural Video Generated Successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
