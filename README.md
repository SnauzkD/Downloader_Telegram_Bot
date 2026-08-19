# Telegram Downloader Bot
A Telegram bot that downloads videos from supported platform, lets users choose quality,
reports download progress, and stores download history using SQLite
## Demo
[▶️ Watch Demo](media/demo.gif)
- `/start` command
- `/help` command
- Send URL
- Metedata appears
- Choose quality
- Progress updates
- Video arrives
- `/history` command
- `/stats` command

## Features
- Supports Youtube,Instagram and Tiktok URLs
- Extracts video metadata before downloading
- Dynamically detects available video qualities
- Quality selection through Telegram buttons
- Video and audio format selection with yt-dlp
- FFmpeg-based MP4 merging
- Real-time download progress updates
- Multiple requests from the same user without mixing URLs
- Concurrent download limiting with asyncio.Semaphore
- Personal download statistics
- SQLite download history
- Error handling for download,Telegram,timeout and rate-limit errors
- Automatic cleanup of temporary download folders

## Technologies
Python  
python-telegram-bot  
yt-dlp  
FFmpeg  
SQLite  
asyncio  
dataclasses  
python-dotenv  

yt-dlp -> downloading video and extracting video information  
asyncio -> keep Telegram bot responsive while blocking downloads run  
FFmpeg -> merge Video/Audio and convert to mp4  
SQlite -> store download history and statistics  


## Architecture
main.py  
|--- Telegram handlers and commands  
VideoDownloader  
|---yt-dlp download logic  
FormatSelector  
|---platform-specific format selection  
RequestManager  
|---request storage  
DownloadRequest  
|---request data  
ProgressReporter  
|---progress updates  
ErrorHandler  
|---user-friendly errors  
Cleanup  
|---removes temporary files,folders, and completed requests  
Database  
|---SQLite history/statistics  

## How it works
1.Telegram user sends URL from available platform  
and then it check for correct URL and platform  
if it's true continue if not send an error  
2. Yt-dlp extract info from video before downloading  
3. Check available qualities in video and create inline buttons of quality in Telegram  
4. Each request reveives a unique ID, which stored in the button callback data. This prevents  
multiple URLs from the same user from being mixed together  
5. After choosing quality, yt-dlp send request to download if it success  
we send video back to user and  
6. After succesful sending delete the request and folder where video was stored  

## Challanges I solved
1.Initially, I stored the current URL directly in context.user_data["url"].  
When the same user sent multiple URLs, the newest URL replaced the previous one.  
I solved this by assigning every request a unique ID and storing each request separately.  
2. Second problem it was with different platform formats  
Youtube and Instagram expose media formats differently, so i created platform specific format selection  
3.yt-dlp performs blocking download operations,  
so I used asyncio.to_thread() to run the download without blocking the Telegram bot's event loop.  
4.Different error conditions  
YouTube and other platforms can return errors such as 403, 429, bot verification, unavailable formats, and timeouts.  
I added separate error handling to give users readable messages instead of raw exceptions.  

## What i learned
how to pass the selected format between handlers,
then learned callback data, request IDs,async,thread interaction,
SQLite how to store history in one file and get them from file,
refactoring 

## How to run

```bash
git clone <repository>
cd <repository>

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

python main.py
```
Create a .env file 
BOT_TOKEN=your_bot_token_here

