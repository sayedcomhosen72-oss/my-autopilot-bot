import os
import json
import requests
import re
from gtts import gTTS
import numpy as np

# Emergency Bypass Backends setup safely
try:
    from PIL import Image, ImageDraw
except ImportError:
    pass

from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def get_reddit_images(reddit_url):
    """BYPASS LAYER 1: Hardcore Reddit Media Scraper"""
    print(f"[SCRAPER] Scanning Reddit Link: {reddit_url}")
    image_urls = []
    try:
        clean_url = reddit_url.split('?')[0].rstrip('/') + ".json"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(clean_url, headers=headers, timeout=12)
        
        if response.status_code == 200:
            data = response.json()
            post_data = data[0]['data']['children'][0]['data']
            
            # Agar gallery post hai (Multiple panels)
            if 'media_metadata' in post_data:
                for item_id in post_data['media_metadata']:
                    img_url = post_data['media_metadata'][item_id]['s']['u'].replace('&amp;', '&')
                    image_urls.append(img_url)
            # Agar single image post hai
            elif 'url' in post_data and re.search(r'\.(jpg|jpeg|png|gif)', post_data['url'], re.IGNORECASE):
                image_urls.append(post_data['url'])
    except Exception as e:
        print(f"[BYPASS WARNING] Scraper layout changed or blocked: {e}")
    
    return image_urls

def create_emergency_canvas(path, text_title):
    """BYPASS LAYER 3: Creates high quality dynamic placeholder if zero images found"""
    print("[EMERGENCY-ENGINE] No images found. Crafting unique canvas to bypass reuse content policy...")
    try:
        # 1080x1920 Premium Dark Anime Aesthetic Canvas
        img = Image.new("RGB", (1080, 1920), color=(15, 15, 22))
        d = ImageDraw.Draw(img)
        d.rectangle([(30, 30), (1050, 1890)], outline=(255, 69, 0), width=6)
        img.save(path)
    except Exception:
        arr = np.zeros((1920, 1080, 3), dtype=np.uint8)
        arr[:, :] = [15, 15, 22]
        import imageio
        imageio.imwrite(path, arr)

def main():
    print("[ENGINE] Starting Vyuk Style Unstoppable Video Generator...")
    
    # 1. Fetch data from GitHub Environment Safely
    github_event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not github_event_path:
        print("[ERROR] GitHub Event Path missing!")
        return

    with open(github_event_path, "r") as f:
        event_data = json.load(f)

    payload = event_data.get("client_payload", {})
    title = payload.get("title", "Manga Video")
    intro = payload.get("intro_script", "").strip()
    body = payload.get("body_script", "").strip()
    reddit_url = payload.get("reddit_url", "https://www.reddit.com/r/lookismcomic/")

    full_text = f"{intro} {body}".strip()
    if not full_text or len(full_text) < 10:
        print("[WARNING] Empty script. Triggering dynamic narrator script...")
        full_text = f"Suno bhaiyo! Aaj hum baat karne wale hain {title} ke baare mein. Yeh leaks sach mein ekdum bawaal hain!"

    print(f"[AUDIO] Generating Desi Launda Voiceover: {full_text[:60]}...")
    
    # 2. Render Audio Voiceover Layer
    audio_path = "voiceover.mp3"
    tts = gTTS(text=full_text, lang='en', slow=False)
    tts.save(audio_path)
    
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration
    print(f"[SUCCESS] Voiceover Ready. Duration: {total_duration}s")

    # 3. Handle Panels & Downloading with active Bypasses
    img_urls = get_reddit_images(reddit_url)
    os.makedirs("panels", exist_ok=True)
    downloaded_images = []

    if img_urls:
        print(f"[DOWNLOADER] Found {len(img_urls)} active links. Extracting panels...")
        for i, url in enumerate(img_urls):
            try:
                img_data = requests.get(url, timeout=10).content
                img_path = f"panels/panel_{i}.jpg"
                with open(img_path, 'wb') as handler:
                    handler.write(img_data)
                downloaded_images.append(img_path)
            except Exception:
                continue

    # BYPASS LAYER 2 TRIGGER: Agar ek bhi photo nahi mili
    if not downloaded_images:
        print("[BYPASS ACTIVATED] Zero images retrieved. Activating automatic canvas node...")
        fallback_img = "panels/fallback_default.jpg"
        create_emergency_canvas(fallback_img, title)
        downloaded_images.append(fallback_img)

    # 4. Multi-Backend Rendering Grid (Bypasses the moviepy.editor imageio issue)
    print("[VIDEO ENGINE] Timeline composition in progress...")
    clips = []
    num_images = len(downloaded_images)
    duration_per_image = max(3.0, total_duration / num_images)
    
    current_time = 0
    image_index = 0
    
    while current_time < total_duration:
        img_path = downloaded_images[image_index % num_images]
        remaining_time = total_duration - current_time
        clip_dur = min(duration_per_image, remaining_time)
        
        # Pillow Backend Conversion Loop to standardize any jpg/png format
        try:
            with Image.open(img_path) as PIL_raw:
                clean_path = f"panels/clean_frame_{image_index}.png"
                PIL_raw.convert('RGB').save(clean_path)
                img_clip = ImageClip(clean_path).set_duration(clip_dur)
        except Exception:
            print(f"[RECOVERY BYPASS] Corrupted image caught at index {image_index}. Standardizing...")
            emergency_path = f"panels/emergency_frame_{image_index}.jpg"
            create_emergency_canvas(emergency_path, title)
            img_clip = ImageClip(emergency_path).set_duration(clip_dur)

        # Vyuk Bhai Style Punch-In Ken Burns Animation (Zooming 6% over timeline)
        img_clip = img_clip.resize(lambda t: 1.0 + 0.06 * (t / clip_dur))
        clips.append(img_clip)
        
        current_time += clip_dur
        image_index += 1

    # 5. Compile and Output High Quality Video Layer
    print("[RENDERER] Joining video clips with audio tracks...")
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(audio_clip)
    
    output_name = "final_output.mp4"
    final_video.write_videofile(
        output_name, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        preset="ultrafast"
    )
    print(f"[COMPLETE] System green! Video saved at: {output_name}")

if __name__ == "__main__":
    main()
