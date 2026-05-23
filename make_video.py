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

from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip

def get_reddit_images(reddit_url):
    print(f"[SCRAPER] Scanning Reddit: {reddit_url}")
    image_urls = []
    try:
        clean_url = reddit_url.split('?')[0].rstrip('/') + ".json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(clean_url, headers=headers, timeout=12)
        if response.status_code == 200:
            data = response.json()
            post_data = data[0]['data']['children'][0]['data']
            if 'media_metadata' in post_data:
                for item_id in post_data['media_metadata']:
                    img_url = post_data['media_metadata'][item_id]['s']['u'].replace('&amp;', '&')
                    image_urls.append(img_url)
            elif 'url' in post_data and re.search(r'\.(jpg|jpeg|png)', post_data['url'], re.IGNORECASE):
                image_urls.append(post_data['url'])
    except Exception:
        pass
    return image_urls

def process_anti_copyright_frame(img_path, output_path):
    try:
        with Image.open(img_path) as img:
            img = img.convert('RGB')
            bg = img.resize((1080, 1920)).filter(ImageFilter.GaussianBlur(radius=25))
            fw_width = 1000
            w_percent = (fw_width / float(img.size[0]))
            fh_size = int((float(img.size[1]) * float(w_percent)))
            if fh_size > 1500:
                fh_size = 1400
                fw_width = int((float(img.size[0]) * float(fh_size / float(img.size[1]))))
            fw = img.resize((fw_width, fh_size), Image.Resampling.LANCZOS)
            bg.paste(fw, ((1080 - fw_width) // 2, (1920 - fh_size) // 2))
            bg.save(output_path)
    except Exception:
        arr = np.zeros((1920, 1080, 3), dtype=np.uint8)
        arr[:, :] = [15, 15, 22]
        import imageio
        imageio.imwrite(output_path, arr)

def main():
    print("[ENGINE] Launching Video Masterpiece...")
    github_event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not github_event_path: return

    with open(github_event_path, "r") as f:
        event_data = json.load(f)

    payload = event_data.get("client_payload", {})
    title = payload.get("title", "Manga Update")
    intro = payload.get("intro_script", "").strip()
    body = payload.get("body_script", "").strip()
    reddit_url = payload.get("reddit_url", "https://www.reddit.com/r/lookismcomic/")

    raw_script = f"{intro} {body}".strip()
    clean_voiceover_text = re.sub(r'\[SOUND_EFFECT_\w+\]', '', raw_script)

    if len(clean_voiceover_text) < 10:
        clean_voiceover_text = f"Aaj hamara dimaag baat karega {title} ke baare mein. Ekdum bawaal leaks hain!"

    audio_path = "voiceover.mp3"
    tts = gTTS(text=clean_voiceover_text, lang='en', slow=False)
    tts.save(audio_path)
    
    main_audio = AudioFileClip(audio_path)
    total_duration = main_audio.duration

    sfx_path = "vine_boom.mp3"
    if not os.path.exists(sfx_path):
        os.system("curl -sL https://www.myinstants.com/media/sounds/vine-boom.mp3 -o vine_boom.mp3")

    audio_targets = [main_audio]
    words = raw_script.split()
    for index, word in enumerate(words):
        if "[SOUND_EFFECT_VINE_BOOM]" in word or "[SOUND_EFFECT_SWORD]" in word:
            try:
                progress_ratio = index / len(words)
                sfx_time = progress_ratio * total_duration
                sfx_clip = AudioFileClip(sfx_path).set_start(sfx_time).volumex(1.2)
                audio_targets.append(sfx_clip)
            except Exception:
                continue

    final_audio = CompositeAudioClip(audio_targets)
    img_urls = get_reddit_images(reddit_url)
    os.makedirs("processed_frames", exist_ok=True)
    downloaded_images = []

    if img_urls:
        for i, url in enumerate(img_urls):
            try:
                img_data = requests.get(url, timeout=10).content
                raw_p = f"processed_frames/raw_{i}.jpg"
                with open(raw_p, 'wb') as h: h.write(img_data)
                proc_p = f"processed_frames/frame_{i}.png"
                process_anti_copyright_frame(raw_p, proc_p)
                downloaded_images.append(proc_p)
            except Exception: continue

    if not downloaded_images:
        fallback = "processed_frames/fallback.jpg"
        arr = np.zeros((1920, 1080, 3), dtype=np.uint8)
        arr[:, :] = [15, 15, 22]
        import imageio
        imageio.imwrite(fallback, arr)
        downloaded_images.append(fallback)

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
        img_clip = img_clip.resize(lambda t: 1.0 + 0.07 * (t / clip_dur))
        clips.append(img_clip)
        current_time += clip_dur
        image_index += 1

    final_video = concatenate_videoclips(clips, method="compose")
    final_video = final_video.set_audio(final_audio)
    
    # FINAL RENDER: OUTPUT NAMED AS output.mp4
    output_name = "output.mp4"
    final_video.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    print(f"[COMPLETE] Masterpiece Rendered: {output_name}")

if __name__ == "__main__":
    main()
