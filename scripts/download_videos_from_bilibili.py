import yt_dlp


def download_bilibili_video(url):
    # Configure options
    ydl_opts = {
        'referer': 'https://www.bilibili.com/',  # Required for Bilibili
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'outtmpl': '%(title)s.%(ext)s',         # Output template
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("Download completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    video_url = input("Enter Bilibili video URL: ")
    download_bilibili_video(video_url)