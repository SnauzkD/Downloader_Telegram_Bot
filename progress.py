import time
import asyncio


class ProgressReporter:
    def __init__(self, message):
        self.message = message
        self.last_update = 0
        self.loop = asyncio.get_running_loop()

    def progress_hook(self, data):
        if data["status"] == "downloading":
            download = data.get("downloaded_bytes", 0)
            total = data.get("total_bytes") or data.get("total_bytes_estimate")

            if total:
                percent = download / total * 100
                now = time.time()
                if now - self.last_update >= 1:
                    self.last_update = now
                    asyncio.run_coroutine_threadsafe(
                        self.message.edit_text(f"⏳ Downloading: {percent:.1f}%"),
                        self.loop,
                    )
