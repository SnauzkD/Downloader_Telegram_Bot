from telegram import InlineKeyboardButton


class BotUtils:
    # handle responses
    def handle_response(self, text: str) -> str:
        if text.startswith(("http://", "https://")):
            return text
        else:
            return "❌ Incorrect Url"

    def get_platform(self, text: str) -> str:

        if "youtube.com" in text or "youtu.be" in text:
            return "Youtube"
        if "tiktok.com" in text or "tiktok" in text:
            return "TikTok"
        if "instagram.com" in text:
            return "Instagram"

        return "Unsupported"

    def get_available_qualities(self, info: dict) -> list[int]:
        qualities = set()

        for fmt in info.get("formats", []):
            width = fmt.get("width")
            height = fmt.get("height")
            vcodec = fmt.get("vcodec")

            if width is None or height is None:
                continue

            if vcodec == "none":
                continue

            quality = min(width, height)
            if quality in [360, 480, 720, 1080]:
                qualities.add(quality)
        return sorted(qualities)

    def create_keyboard(
        self, qualities: list[int], download_id: str
    ) -> list[list[InlineKeyboardButton]]:
        keyboard = []
        row = []
        if 360 in qualities:
            row.append(InlineKeyboardButton("360p", callback_data=f"360:{download_id}"))
        if 480 in qualities:
            row.append(InlineKeyboardButton("480p", callback_data=f"480:{download_id}"))
        if row:
            keyboard.append(row)
        row = []
        if 720 in qualities:
            row.append(InlineKeyboardButton("720p", callback_data=f"720:{download_id}"))
        if 1080 in qualities:
            row.append(
                InlineKeyboardButton("1080p", callback_data=f"1080:{download_id}")
            )
        if row:
            keyboard.append(row)
        return keyboard
