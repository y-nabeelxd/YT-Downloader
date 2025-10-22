import os
from yt_dlp import YoutubeDL
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_available_resolutions(video_url):
    """Fetch available video resolutions."""
    ydl_opts = {
        'no_proxy': True,
        'logger': logger,
        'proxy': None,
        'quiet': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36',
        },
    }
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)

        if 'entries' in info_dict:
            first_video = info_dict['entries'][0]
            video_formats = first_video.get('formats', [])
            resolutions = {fmt['format_id']: f"{fmt['height']}p" for fmt in video_formats if 'height' in fmt}
        else:
            formats = info_dict.get('formats', [])
            resolutions = {fmt['format_id']: f"{fmt['height']}p" for fmt in formats if 'height' in fmt}

        return resolutions


def download_video_with_ytdlp(video_url, selected_resolution, folder_name):
    """Download video at or below selected resolution."""
    ydl_opts = {
        'no_proxy': True,
        'format': f'bestvideo[height<={selected_resolution[:-1]}]+bestaudio/best'
                  if selected_resolution.endswith('p') else 'bv*+ba/b',
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
        'outtmpl': os.path.join(folder_name, '%(title)s.%(ext)s') if folder_name else '%(title)s.%(ext)s',
        'logger': logger,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36',
        },
        'verbose': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def download_audio_as_mp3(video_url, folder_name):
    """Download only audio as MP3."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(folder_name, '%(title)s.%(ext)s') if folder_name else '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'progress_hooks': [progress_hook],
        'logger': logger,
        'verbose': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0 Safari/537.36',
        },
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def progress_hook(d):
    """Show progress information."""
    if d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} of {d['filename']} at {d['_speed_str']}")
    elif d['status'] == 'finished':
        print(f"✅ Download completed: {d['filename']}")


def get_folder_name():
    """Ask user to create a folder if needed."""
    while True:
        folder_name = input("Provide a new folder name to save the files: ").strip()
        if not folder_name:
            print("Folder name cannot be empty. Please try again.")
        elif os.path.exists(folder_name):
            print(f"The folder '{folder_name}' already exists. Please choose a different name.")
        else:
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' created successfully.")
            return folder_name


def main():
    video_url = input("Enter the YouTube video or playlist URL: ").strip()

    if "youtube.com/shorts/" in video_url:
        video_url = video_url.replace("youtube.com/shorts/", "youtube.com/watch?v=")

    download_type = input("Do you want to download video or mp3? (video/mp3): ").strip().lower()
    save_in_folder = input("Do you want to save in a folder? (y/n): ").strip().lower()
    folder_name = get_folder_name() if save_in_folder == 'y' else None

    with YoutubeDL() as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        is_playlist = 'entries' in info_dict

    if download_type == 'mp3':
        if is_playlist:
            print("🎵 Downloading playlist as MP3...")
            for entry in info_dict['entries']:
                print(f"Downloading: {entry['title']}")
                download_audio_as_mp3(entry['webpage_url'], folder_name)
        else:
            download_audio_as_mp3(video_url, folder_name)

    elif download_type == 'video':
        resolutions = get_available_resolutions(video_url)
        print("\nAvailable video resolutions:")
        for fmt, height in sorted(resolutions.items(), key=lambda x: x[1], reverse=True):
            print(f"{fmt}: {height}")

        attempts = 3
        selected_resolution = None

        while attempts > 0:
            selected_resolution = input("Enter the resolution (e.g., '720p', '1080p', '480p'): ").strip()
            if any(height == selected_resolution for height in resolutions.values()):
                break
            else:
                attempts -= 1
                print(f"Invalid resolution. {attempts} {'attempt' if attempts == 1 else 'attempts'} left.")
                if attempts > 0:
                    print("Please choose one of the resolutions listed above.")

        if selected_resolution:
            if is_playlist:
                print("🎬 Downloading playlist in selected resolution...")
                for entry in info_dict['entries']:
                    print(f"Downloading: {entry['title']}")
                    download_video_with_ytdlp(entry['webpage_url'], selected_resolution, folder_name)
            else:
                download_video_with_ytdlp(video_url, selected_resolution, folder_name)
        else:
            print("❌ Too many invalid attempts. Exiting.")

    else:
        print("❌ Invalid download type. Please run the program again.")


if __name__ == "__main__":
    main()
