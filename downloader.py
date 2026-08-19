import yt_dlp


class VideoDownloader:
    def __init__(self, download_folder):
        self.download_folder = download_folder

    def download(self, url, format_string, progress_hook):
        options = {
            "format": format_string,
            "merge_output_format": "mp4",
            "outtmpl": str(self.download_folder / "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)

        files = list(self.download_folder.iterdir())

        return info, files[0]
