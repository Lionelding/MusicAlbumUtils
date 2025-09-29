from yt_dlp import YoutubeDL


def download_youtube_video(url, output_path=".", audio_only=False):
    # Options for yt-dlp
    if audio_only:
        ydl_opts = {
            'format': 'bestaudio/best',  # Download the best audio quality available
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Save file with title as name
            'noplaylist': True,  # Ensure only a single video is downloaded
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',  # Best MP3 quality (320 kbps)
            }],
        }
    else:
        ydl_opts = {
            'format': 'best',  # Download the best quality available
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',  # Save file with title as name
            'noplaylist': True,  # Ensure only a single video is downloaded
        }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Download the video/audio
            info_dict = ydl.extract_info(url, download=True)
            video_title = info_dict.get('title', 'video')
            if audio_only:
                print(f"MP3 download complete: {video_title}")
            else:
                print(f"Download complete: {video_title}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # YouTube video URL
    video_url = input("Enter the YouTube video URL: ")

    # Output directory (optional, defaults to current directory)
    output_directory = input("Enter the output directory (leave blank for current directory): ").strip() or "."
    
    # Ask if user wants MP3 or video
    download_choice = input("Do you want to download as MP3 (audio only)? (y/n): ").strip().lower()
    audio_only = download_choice in ['y', 'yes']

    # Download the video or audio
    download_youtube_video(video_url, output_directory, audio_only)