class FormatSelector:
    def get_format(self, platform, quality):
        if platform == "Youtube":
            quality_format = {
                "360": "bestvideo[height<=360][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<=360]",
                "480": "bestvideo[height<=480][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<=480]",
                "720": "bestvideo[height<=720][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<=720]",
                "1080": "bestvideo[height<=1080][vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[height<=1080]",
            }
        else:
            quality_format = {
                "360": "bestvideo[width<=360]+bestaudio/best",
                "480": "bestvideo[width<=480]+bestaudio/best",
                "720": "bestvideo[width<=720]+bestaudio/best",
                "1080": "bestvideo[width<=1080]+bestaudio/best",
            }
        return quality_format.get(quality)
