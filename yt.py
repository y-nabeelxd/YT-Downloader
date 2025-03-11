import os
from yt_dlp import YoutubeDL
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_available_resolutions(video_url):
    ydl_opts = {
        'no_proxy': True,
        'logger': logger,
        'proxy': None,
        'verbose': True,
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

def download_video_with_ytdlp(video_url, format_id, folder_name):
    ydl_opts = {
        'no_proxy': True,
        'format': f"{format_id}+bestaudio/best",
        'progress_hooks': [progress_hook],
        'outtmpl': os.path.join(folder_name, '%(title)s.%(ext)s') if folder_name else '%(title)s.%(ext)s',
        'logger': logger,
        'verbose': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"Downloading: {d['_percent_str']} of {d['filename']} at {d['_speed_str']}")
    elif d['status'] == 'finished':
        print(f"Downloaded: {d['filename']}")

def get_folder_name():
    while True:
        folder_name = input("Provide a new folder name to save the videos: ").strip()
        if not folder_name:
            print("Folder name cannot be empty. Please try again.")
        elif os.path.exists(folder_name):
            print(f"Sorry, the folder name '{folder_name}' already exists. Please choose a different name.")
        else:
            os.makedirs(folder_name)
            print(f"Folder '{folder_name}' created successfully.")
            return folder_name

def main():
    video_url = input("Enter the YouTube video URL or Playlist URL: ")
    resolutions = get_available_resolutions(video_url)

    print("Available resolutions:")
    for fmt, height in sorted(resolutions.items(), key=lambda x: x[1], reverse=True):
        print(f"{fmt}: {height}")

    attempts = 3
    selected_format = None

    while attempts > 0:
        selected_resolution = input("Enter the resolution (e.g., '720p', '1080p', '480p'): ")
        
        selected_format = next((fmt for fmt, height in resolutions.items() if height == selected_resolution), None)
        
        if selected_format:
            break
        else:
            attempts -= 1
            print(f"Invalid resolution selected. You have {attempts} {'attempt' if attempts == 1 else 'attempts'} left.")
            if attempts > 0:
                print("Please enter one of the available resolutions shown above.")

    if selected_format:
        save_in_folder = input("Do you want to save in a folder? (y/n): ").strip().lower()
        folder_name = None
        if save_in_folder == 'y':
            folder_name = get_folder_name()

        with YoutubeDL() as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            if 'entries' in info_dict:
                print("Downloading playlist...")
                for entry in info_dict['entries']:
                    print(f"Downloading: {entry['title']}")
                    download_video_with_ytdlp(entry['webpage_url'], selected_format, folder_name)
            else:
                download_video_with_ytdlp(video_url, selected_format, folder_name)
    else:
        print("Too many invalid attempts. Exiting the program.")

if __name__ == "__main__":
    main()