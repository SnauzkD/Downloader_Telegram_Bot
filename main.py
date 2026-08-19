import yt_dlp
import asyncio
import uuid
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Final
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    ApplicationBuilder,
)
from downloader import VideoDownloader
from error_handler import ErrorHandler
from utils import BotUtils
from format import FormatSelector
from models import DownloadRequest
from request_manager import RequestManager
from progress import ProgressReporter
from cleanup import CleanUp
from database import DataBase

# global variables
download_semaphore = asyncio.Semaphore(1)
error_handler = ErrorHandler()
utils = BotUtils()
request_manager = RequestManager()
clean_manager = CleanUp()
database = DataBase()
database.create_table()
# Bot Info
load_dotenv()
TOKEN: Final = os.getenv("BOT_TOKEN")
USERNAME: Final = "@downloaderByUrl_bot"

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in .env")


# Commands
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    total_downloads = database.get_total_downloads(user_id)
    platform_stats = database.get_platform_downlads(user_id)

    message = f"📊 Your statistics\n\n" f"📥 Total downloads: {total_downloads}\n"

    for platform, count in platform_stats:
        message += f"{platform}: {count}\n"

    await update.message.reply_text(message)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n"
        "Send me a video URL from:\n"
        "• YouTube\n"
        "• Instagram\n"
        "• TikTok*\n"
        "I’ll download it for you.\n"
        "*TikTok availability may vary."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*How to use:"
        "Copy the url from video you want to download and send it to bot*"
    )


# history command
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    history = database.get_history(user_id)

    if not history:
        await update.message.reply_text("📭 Your download history is empty.")
        return

    message = "📥 Your recent downloads: \n\n"

    for platform, title, quality, duration, created_at in history:
        if duration is not None or duration == "Unknown":
            duration_text = "Unknown"
        else:
            duration = int(duration)
            duration_text = f"{duration // 60}:{duration % 60:02d}"

        message += (
            f"🎬 {platform}\n"
            f"📺 {title}\n"
            f"🎞️ Quality: {quality}\n"
            f"🕛 Duration: {duration}\n"
            f"📅 {created_at}\n\n"
        )

    await update.message.reply_text(message)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    quality, download_id = data.split(":", 1)
    progress_message = await query.message.reply_text("⏳ Downloading: 0%")
    last_update = 0
    loop = asyncio.get_running_loop()

    store_id = str(uuid.uuid4())
    user_folder = Path("downloads") / store_id
    user_folder.mkdir(parents=True, exist_ok=True)
    requests = context.user_data.get("requests", {})
    request = request_manager.get(requests, download_id)
    if request is None:
        await query.message.reply_text(
            "❌ This download request has expired. Send the URL again."
        )
        clean_manager.clean(user_folder)
        return
    url = request.url
    info = request.info
    platform = request.platform
    # quality format
    format_selector = FormatSelector()
    format_string = format_selector.get_format(platform, quality)
    file_path = None
    downloader = VideoDownloader(user_folder)
    progress = ProgressReporter(progress_message)
    try:
        async with download_semaphore:
            info, file_path = await asyncio.to_thread(
                downloader.download, url, format_string, progress.progress_hook
            )
    except yt_dlp.utils.DownloadError as e:
        logger.warning("Download failed: %s", e)
        await progress_message.edit_text("❌ Failed! Try again or later.")
        clean_manager.clean(user_folder)
        return
    await progress_message.edit_text("✅ Download complete! Sending video...")

    if file_path is None:
        return
    try:
        with open(file_path, "rb") as video:
            await query.message.reply_video(video=video)
    except Exception as e:
        message = error_handler.downloadErrorHandle(e)
        await query.message.reply_text(message)
        print(f"Telegram uploaded error: {e}")
        await progress_message.edit_text("❌ Failed! Try again or later.")
        clean_manager.clean(user_folder)
        return
    database.save_download(
        query.from_user.id,
        platform,
        info.get("title", "Unknown"),
        quality,
        info.get("duration", "Unknown"),
    )
    clean_manager.clean(user_folder)
    request_manager.delete(requests, download_id)


# handle message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    process_message = await update.message.reply_text("⏳ Processing...")
    handle_url = utils.handle_response(text)
    try:
        if handle_url == "❌ Incorrect Url":
            await update.message.reply_text("❌ Incorrect URL")
            return Exception
        platform: str = utils.get_platform(text)
        if platform == "Unsupported":
            await update.message.reply_text("❌ Unsupported URL")
            return Exception
    except Exception:
        await process_message.edit_text("❌ Canceled!\n Try again or later.")
        return
    try:
        with yt_dlp.YoutubeDL({}) as ydl:
            info = ydl.extract_info(text, download=False)
            qualities = utils.get_available_qualities(info)
    except yt_dlp.utils.DownloadError as e:
        message = error_handler.downloadErrorHandle(e)
        await update.message.reply_text(message)
        await process_message.edit_text("❌ Canceled!\n Try again or later.")
        logger.warning("Download failed: %s", e)
        return

    requests = context.user_data.setdefault("requests", {})
    request = DownloadRequest(url=text, info=info, platform=platform)
    download_id = request_manager.create(requests, request)
    print(qualities)
    duration = info.get("duration")
    if duration is None:
        duration_text = "Unknown"
    else:
        duration_text = f"{duration // 60}:{duration % 60:02d}"
    await process_message.edit_text("✅ Complete!")
    await update.message.reply_text(
        f"📺: {info.get("title")}\n" f"🕛: {duration_text} min"
    )
    # Buttons
    keyboard = utils.create_keyboard(qualities, download_id)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose quality:", reply_markup=reply_markup)


logger = logging.getLogger(__name__)


# handle errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error = context.error

    logger.error("Exception while handling and update", exc_info=error)

    message = error_handler.telegramErrorHandle(error)
    if update and update.effective_message:
        print(f"Unexcepted error: {error}")
        await update.effective_message.reply_text(message)


if __name__ == "__main__":
    print("starting")
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(60)
        .pool_timeout(60)
        .build()
    )
    # commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("stats", stats_command))

    # message
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # button
    app.add_handler(CallbackQueryHandler(button_handler))

    # error
    app.add_error_handler(error)

    print("polling")
    app.run_polling(poll_interval=3)
