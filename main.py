import os
import asyncio
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import edge_tts
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

async def generate_edge_voice(text, output_path):
    # Fixed Connection Settings for Edge TTS
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="+10%")
    await communicate.save(output_path)

@app.post("/render-video")
async def render_video(request: VideoRequest, authorized: str = Depends(verify_token)):
    try:
        full_script = f"{request.intro_script}. {request.body_script}"
        
        # Script cleaning
        full_script = full_script.replace("{", "").replace("}", "").replace('"', '').replace("'", "")
        
        audio_path = "output_voice.mp3"
        video_path = "final_output.mp4"
        
        # Running async voice function
        loop = asyncio.get_event_loop()
        await generate_edge_voice(full_script, audio_path)
        
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            raise HTTPException(status_code=500, detail="Desi Voice generation failed")
            
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        img_clip = ImageClip(np.zeros((1080, 1920, 3), dtype=np.uint8)).set_duration(duration)
        final_video = img_clip.set_audio(audio_clip)
        final_video.write_videofile(video_path, fps=24, codec="libx264", audio_codec="aac")
        
        audio_clip.close()
        final_video.close()
        
        return {"status": "success", "video_url": "Desi Video Generated Successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
