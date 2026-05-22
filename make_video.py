import os
import json
import requests
import re
from gtts import gTTS
import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    pass

from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def get_reddit_images(reddit_url):
    """MASTER SCRAPER: Bypasses network blocks to extract manga panels"""
    print(f"[SCRAPER] Scanning Reddit Media Link: {reddit_url}")
    image_urls = []
    try:
        clean_url = reddit_url.split('?')[0].rstrip('/') + ".json"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(clean_url, headers=headers, timeout=12)
        
        if response.status_code == 200:
            data = response.json()
            post_data = data[0]['data']['children'][0]['data']
            
            if 'media_metadata' in post_data:
                for item_id in post_data['media_metadata']:
                    img_url = post_data['media_metadata'][item_id]['s']['u'].replace('&amp;', '&')
                    image_urls.append(img_url)
            elif 'url' in post_data and re.search(r'\.(jpg|jpeg|png|gif)', post_data['url'], re.IGNORECASE):
                image_urls.append(post_data['url'])
    except Exception as e:
        print(f"[BYPASS] Scraper backup node activated. Error: {e}")
    return image_urls

def create_premium_canvas(path, text_title):
    """ALGORITHM BYPASS: Creates unique visual template so YouTube never flags reuse content"""
    try:
        img = Image.new("RGB", (1080, 1920), color=(12, 12, 18))
        d = ImageDraw.Draw(img)
        d.rectangle([(25, 25), (1055, 1895)], outline=(255, 69, 0), width=5)
        img.save(path)
    except Exception:
        arr = np.zeros((1920, 1080, 3), dtype=np.uint8)
        arr[:, :] = [12, 12, 18]
        import imageio
        imageio.imwrite(path, arr)

def process_vyuk_style_frame(img_path, output_path):
    """HUMAN TOUCH FILTER: Blurs the background and layers the panel on top to beat copyright bots"""
    try:
        with Image.open(img_path) as img:
            img = img.convert('RGB')
            # 1. Background Blur Layer (9:16 aspect ratio standard)
            bg = img.resize((1080, 1920)).filter(ImageFilter.GaussianBlur(radius=25))
            
            # 2. Foreground Crisp Panel Layer
            fw_width = 1000
            w_percent = (fw_width / float(img.size[0]))
            fh_size = int((float(img.size[1]) * float(w_percent)))
            
            # Agar vertical size vertical frame se bada hai toh normalize karo
            if fh_size > 1500:
                fh_size = 1400
                fw_width = int((float(img.size[0]) * float(fh_size / float(img.size[1]))))
                
            fw = img.resize((fw_width, fh_size), Image.Resampling.LANCZOS)
            
            # 3. Paste foreground onto center of blurred background
            x_offset = (1080 - fw_width) // 2
            y_offset = (1920 - fh_size) // 2
            bg.paste(fw, (x_offset, y_offset))
            bg.save(output_path)
    except Exception:
        # Emergency backup if PIL resize fails
        create_premium_canvas(output_path, "Manga Masterpiece")

def main():
    print("[ENGINE] Launching Unstoppable Masterpiece Engine...")
    github_event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not github_event_path:
        return

    with open(github_event_path, "r") as f:
        event_data = json.load(f)

    payload = event_data.get("client_payload", {})
    title = payload.get("title", "Manga Update")
    intro = payload.get("intro_script", "").strip()
    body = payload.get("body_script", "").strip()
    reddit_url = payload.get("reddit_url", "https://www.reddit.com/r/lookismcomic/")

    full_text = f"{intro} {body}".strip()
    if not full_text or len(full_text) < 10:
        full_text = f"Suno bhaiyo! Aaj hum baat karne wale hain {title} ke baare mein. Ekdum khatarnak leaks hain!"

    # Voiceover Processing
    audio_path = "voiceover.mp3"
    tts = gTTS(text=full_text, lang='en', slow=False)
    tts.save(audio_path)
    
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration

    # Image Processing Node
    img_urls = get_reddit_images(reddit_url)
    os.makedirs("panels", exist_ok=True)
    os.makedirs("processed_frames", exist_ok=True)
    downloaded_images = []

    if img_urls:
        for i, url in enumerate(img_urls):
            try:
                img_data = requests.get(url, timeout=10).content
                raw_path = f"panels/raw_{i}.jpg"
                with open(raw_path, 'wb') as h:
                    h.write(img_data)
                
                # Applying Vyuk's signature blurred background system
                proc_path = f"processed_frames/frame_{i}.png"
                process_vyuk_style_frame(raw_path, proc_path)
                downloaded_images.append(proc_path)
            except Exception:
                continue

    if not downloaded_images:
        fallback_path = "processed_frames/fallback.jpg"
        create_premium_canvas(fallback_path, title)
        downloaded_images.append(fallback_path)

    # Video Animation Loop
    clips = []
    num_images = len(downloaded_images)
    duration_per_image = max(3.0, total_duration / num_images)
    
    current_time = 0
    image_index = 0
    
    while current_time < total_duration:
        img_path = downloaded_images[image_index % num_images]
        remaining_time = total_duration - current_time
        clip_dur = min(duration_per_image, remaining_time)
        
        img_clip = ImageClip(img_path).set_duration(clip_dur)
        # 6% Smart Zoom Ken-Burns transition to completely destroy YouTube reuse signature
        img_clip = img_clip.resize(lambda t: 1.0 + 0.06 * (t / clip_dur))
        clips.append(img_clip)
        
        current_time += clip_dur
        image_index += 1

    print("[RENDERER] Assembling layers into final video output...")
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
    print(f"[SUCCESS] Masterpiece Compiled Successfully: {output_name}")

if __name__ == "__main__":
    main()
