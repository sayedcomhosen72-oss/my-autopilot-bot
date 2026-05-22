import os
import json
import requests
import re
from gtts import gTTS
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

def get_reddit_images(reddit_url):
    """Hardcore Reddit Scraper: Extracts all image panels from single or gallery posts"""
    print(f"[SCRAPER] Scanning Reddit Link: {reddit_url}")
    image_urls = []
    try:
        # Converting normal link to JSON endpoint for clean scraping
        clean_url = reddit_url.split('?')[0].rstrip('/') + ".json"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(clean_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            post_data = data[0]['data']['children'][0]['data']
            
            # Case 1: If it's a Multi-Image Gallery Post
            if 'media_metadata' in post_data:
                for item_id in post_data['media_metadata']:
                    img_url = post_data['media_metadata'][item_id]['s']['u'].replace('&amp;', '&')
                    image_urls.append(img_url)
            # Case 2: Single Image Post
            elif 'url' in post_data and re.search(r'\.(jpg|jpeg|png|gif)', post_data['url'], re.IGNORECASE):
                image_urls.append(post_data['url'])
    except Exception as e:
        print(f"[WARNING] Reddit scraping failed: {str(e)}. Using fallback system.")
    
    return image_urls

def main():
    print("[ENGINE] Starting Vyuk Style Video Generator...")
    
    # 1. Fetch data from Make.com GitHub Event Payload
    github_event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not github_event_path:
        print("[ERROR] No GitHub Event Path found!")
        return

    with open(github_event_path, "r") as f:
        event_data = json.load(f)

    payload = event_data.get("client_payload", {})
    title = payload.get("title", "Manga Video")
    intro = payload.get("intro_script", "").strip()
    body = payload.get("body_script", "").strip()
    
    # We will grab the Reddit URL from payload (Make sure your workflow passes it)
    reddit_url = payload.get("reddit_url", "https://www.reddit.com/r/lookismcomic/")

    # 2. Hardcore Text Check to bypass TTS Error
    full_text = f"{intro} {body}".strip()
    if not full_text or len(full_text) < 10:
        print("[WARNING] Script was empty or too short. Activating backup script...")
        full_text = f"What's up homies! Today we are looking at the latest leaks of {title}. The panels look absolutely crazy!"

    # 3. Generate Audio Voiceover (TTS)
    audio_path = "voiceover.mp3"
    print("[AUDIO] Generating voiceover layers...")
    tts = gTTS(text=full_text, lang='en', slow=False)
    tts.save(audio_path)
    
    audio_clip = AudioFileClip(audio_path)
    total_duration = audio_clip.duration
    print(f"[SUCCESS] Voiceover created. Total Duration: {total_duration} seconds")

    # 4. Image Fetching & Panel Downloading
    img_urls = get_reddit_images(reddit_url)
    os.makedirs("panels", exist_ok=True)
    downloaded_images = []

    if img_urls:
        print(f"[DOWNLOADER] Found {len(img_urls)} manga panels. Starting download...")
        for i, url in enumerate(img_urls):
            try:
                img_data = requests.get(url, timeout=10).content
                img_path = f"panels/panel_{i}.jpg"
                with open(img_path, 'wb') as handler:
                    handler.write(img_data)
                downloaded_images.append(img_path)
            except Exception as e:
                print(f"[SKIP] Failed downloading panel {i}: {e}")
    
    # Fallback: If no images found, create a placeholder so video engine never crashes
    if not downloaded_images:
        print("[WARNING] No images found. Creating a generic dummy background...")
        # (This avoids error by putting a default image if internet fails)
        os.system("curl -s https://picsum.photos/1080/1920 -o panels/default.jpg")
        downloaded_images.append("panels/default.jpg")

    # 5. Vyuk Style Video Compilation Engine (Continuous Transition Logic)
    print("[VIDEO ENGINE] Sequencing manga panels with dynamic duration...")
    clips = []
    num_images = len(downloaded_images)
    
    # Calculate how much screen time each panel gets based on voiceover length
    duration_per_image = max(3.0, total_duration / num_images)
    
    current_time = 0
    image_index = 0
    
    while current_time < total_duration:
        img_path = downloaded_images[image_index % num_images]
        
        # Calculate exactly how much time is left for this specific loop
        remaining_time = total_duration - current_time
        clip_dur = min(duration_per_image, remaining_time)
        
        # Creating image clip layer
        img_clip = ImageClip(img_path).set_duration(clip_dur)
        
        # Vyuk Style Punch-In Zoom Effect Logic (Using MoviePy resizing over time)
        # It slightly zooms the image by 10% smoothly to break YouTube Reused content algorithm
        img_clip = img_clip.resize(lambda t: 1.0 + 0.05 * (t / clip_dur))
        
        clips.append(img_clip)
        current_time += clip_dur
        image_index += 1

    # Final Sync: Binding Image clips together and overlaying the Voiceover
    print("[RENDERER] Compiling final video layers...")
    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(audio_clip)
    
    # Output file settings for high-quality Shorts (1080x1920)
    output_path = "final_output.mp4"
    final_video.write_videofile(
        output_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        preset="ultrafast"  # Keeps GitHub Actions rendering blazing fast and free
    )
    
    print(f"[COMPLETE] Boom! Video is fully rendered at: {output_path}")

if __name__ == "__main__":
    main()
