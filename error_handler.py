from telegram.error import NetworkError, TimedOut, BadRequest, TelegramError
import yt_dlp


class ErrorHandler:
    def downloadErrorHandle(self, error):
        error_text = str(error)
        if "Sign in to confirm you're not a bot" in error_text:
            return (
                "🤖 YouTube is blocking this request right now.\n"
                "Please try again later."
            )
        elif " HTTP Error 429" in error_text:
            return (
                "⏳ YouTube is temporarily rate-limiting requests.\n"
                "Please try again later."
            )
        else:
            return "❌ Couldn't download this video."

    def telegramErrorHandle(self, error):
        if isinstance(error, TimedOut):
            return "❌ Oops! Request timed out."
        elif isinstance(error, NetworkError):
            return "❌ Oops! Network error."
        elif isinstance(error, BadRequest):
            return "❌ Telegram rejected the request"
        elif isinstance(error, TelegramError):
            return "❌ Telegram error"
        elif isinstance(error, yt_dlp.utils.DownloadError):
            return "❌ yt-dlp download error"
        return "❌ Something went wrong. Please try again."
