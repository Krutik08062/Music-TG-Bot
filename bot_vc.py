"""
🎵 Telegram Music Bot with Voice Chat Support
Download music OR stream in voice chats!
"""

import os
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
try:
    import yt_dlp
except ImportError:
    import youtube_dl as yt_dlp
from collections import deque
from pathlib import Path

# Try to import from config_vc.py (local development)
# If not available, use environment variables (production/Render)
try:
    from config_vc import API_ID, API_HASH, BOT_TOKEN, DOWNLOAD_PATH
except ImportError:
    # Running on production (Render) - use environment variables
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DOWNLOAD_PATH = os.path.join(Path(__file__).parent, 'downloads')

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create downloads directory
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

# Initialize Pyrogram client
app = Client(
    "music_bot_v2",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Initialize PyTgCalls
pytgcalls = PyTgCalls(app)

# Queue system for each chat
queues = {}


class Queue:
    def __init__(self):
        self.items = deque()
    
    def add(self, item):
        self.items.append(item)
    
    def remove(self):
        if self.items:
            return self.items.popleft()
        return None
    
    def clear(self):
        self.items.clear()
    
    def is_empty(self):
        return len(self.items) == 0
    
    def get_list(self):
        return list(self.items)


def get_queue(chat_id):
    """Get or create queue for a chat"""
    if chat_id not in queues:
        queues[chat_id] = Queue()
    return queues[chat_id]


async def download_audio(query: str, msg: Message):
    """Download audio from YouTube"""
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(id)s.%(ext)s'),
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            if not info or 'entries' not in info:
                return None
            
            video = info['entries'][0]
            filename = ydl.prepare_filename(video)
            
            return {
                'file': filename,
                'title': video['title'],
                'duration': video.get('duration', 0),
                'url': video['webpage_url'],
                'thumbnail': video.get('thumbnail'),
                'requested_by': msg.from_user.mention
            }
    except Exception as e:
        logger.error(f"Download error: {e}")
        return None


async def play_next(chat_id: int):
    """Play next song in queue"""
    queue = get_queue(chat_id)
    
    if queue.is_empty():
        try:
            await pytgcalls.leave_call(chat_id)
        except:
            pass
        return
    
    next_song = queue.remove()
    
    try:
        await pytgcalls.play(
            chat_id,
            MediaStream(next_song['file'])
        )
    except Exception as e:
        logger.error(f"Play error: {e}")
        await play_next(chat_id)


@pytgcalls.on_update()
async def on_update_handler(client, update):
    """Auto-play next song when current ends"""
    # Check if it's a stream ended event
    if hasattr(update, 'chat_id'):
        chat_id = update.chat_id
        await play_next(chat_id)


@app.on_message(filters.command("start"))
async def start(client, message: Message):
    """Welcome message"""
    await message.reply_text(
        "🎵 **Welcome to Music Bot!** 🎵\n\n"
        "I can download music OR play in voice chats!\n\n"
        "**Download Commands:**\n"
        "• `/download <song>` - Download MP3\n\n"
        "**Voice Chat Commands:**\n"
        "• `/play <song>` - Play in voice chat\n"
        "• `/pause` - Pause playback\n"
        "• `/resume` - Resume playback\n"
        "• `/skip` - Skip current song\n"
        "• `/stop` - Stop & leave voice chat\n"
        "• `/queue` - Show queue\n"
        "• `/current` - Current playing song\n\n"
        "**Other Commands:**\n"
        "• `/help` - Show all commands\n"
        "• `/about` - About this bot\n\n"
        "🎧 **Example:**\n"
        "`/play perfect ed sheeran`"
    )


@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    """Help message"""
    await message.reply_text(
        "📚 **Music Bot Commands**\n\n"
        "**🎵 Voice Chat:**\n"
        "• `/play <song>` - Play song in VC\n"
        "• `/pause` - Pause music\n"
        "• `/resume` - Resume music\n"
        "• `/skip` - Skip to next song\n"
        "• `/stop` - Stop & leave VC\n"
        "• `/queue` - View queue\n"
        "• `/current` - Now playing\n\n"
        "**⬇️ Download:**\n"
        "• `/download <song>` - Get MP3 file\n\n"
        "**ℹ️ Info:**\n"
        "• `/start` - Start bot\n"
        "• `/help` - This message\n"
        "• `/about` - About bot\n\n"
        "**💡 Tips:**\n"
        "• Add me to group & make admin\n"
        "• Start a voice chat first\n"
        "• Use `/play` to add songs\n"
        "• Queue multiple songs!"
    )


@app.on_message(filters.command("about"))
async def about(client, message: Message):
    """About bot"""
    await message.reply_text(
        "ℹ️ **About Music Bot**\n\n"
        "🎵 Version: 2.0.0 (Voice Chat Edition)\n"
        "👨‍💻 Developer: College Project\n\n"
        "**Features:**\n"
        "✅ Voice chat streaming\n"
        "✅ Queue management\n"
        "✅ Playback controls\n"
        "✅ MP3 downloads\n"
        "✅ High-quality audio\n\n"
        "**Tech Stack:**\n"
        "• Pyrogram\n"
        "• PyTgCalls\n"
        "• yt-dlp\n"
        "• FFmpeg\n\n"
        "⚠️ **Disclaimer:**\n"
        "For educational use only.\n"
        "Respect copyright laws.\n\n"
        "Made with ❤️ for music lovers!"
    )


@app.on_message(filters.command("play"))
async def play(client, message: Message):
    """Play music in voice chat"""
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **Usage:** `/play <song name>`\n\n"
            "**Example:** `/play perfect ed sheeran`"
        )
        return
    
    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    
    msg = await message.reply_text(f"🔍 **Searching:** `{query}`...")
    
    # Download audio
    song = await download_audio(query, message)
    
    if not song:
        await msg.edit_text("❌ **Not found!** Try different keywords.")
        return
    
    queue = get_queue(chat_id)
    
    # Check if already playing
    try:
        # Check if queue is empty (nothing playing)
        is_first_song = queue.is_empty()
        
        # Add to queue
        queue.add(song)
        
        # Play if this is the first song
        if is_first_song:
            await msg.edit_text(f"🎵 **Playing now...**")
            await play_next(chat_id)
            
            await message.reply_text(
                f"🎵 **Now Playing**\n\n"
                f"**Title:** {song['title']}\n"
                f"**Duration:** {song['duration'] // 60}:{song['duration'] % 60:02d}\n"
                f"**Requested by:** {song['requested_by']}"
            )
        else:
            queue_position = len(queue.get_list())
            await msg.edit_text(
                f"✅ **Added to queue!**\n\n"
                f"🎵 **Title:** {song['title']}\n"
                f"⏱ **Duration:** {song['duration'] // 60}:{song['duration'] % 60:02d}\n"
                f"📝 **Position:** {queue_position}\n"
                f"👤 **Requested by:** {song['requested_by']}"
            )
    except Exception as e:
        logger.error(f"Play error: {e}")
        await msg.edit_text(f"❌ **Error:** {str(e)}")


@app.on_message(filters.command("pause"))
async def pause(client, message: Message):
    """Pause playback"""
    chat_id = message.chat.id
    
    try:
        await pytgcalls.pause_stream(chat_id)
        await message.reply_text("⏸ **Paused!**")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")


@app.on_message(filters.command("resume"))
async def resume(client, message: Message):
    """Resume playback"""
    chat_id = message.chat.id
    
    try:
        await pytgcalls.resume_stream(chat_id)
        await message.reply_text("▶️ **Resumed!**")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")


@app.on_message(filters.command("skip"))
async def skip(client, message: Message):
    """Skip current song"""
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    
    if queue.is_empty():
        await message.reply_text("❌ **Queue is empty!**")
        return
    
    await message.reply_text("⏭ **Skipped!**")
    await play_next(chat_id)


@app.on_message(filters.command("stop"))
async def stop(client, message: Message):
    """Stop and leave voice chat"""
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    
    try:
        await pytgcalls.leave_call(chat_id)
        queue.clear()
        await message.reply_text("⏹ **Stopped!** Left voice chat.")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {str(e)}")


@app.on_message(filters.command("queue"))
async def show_queue(client, message: Message):
    """Show current queue"""
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    
    if queue.is_empty():
        await message.reply_text("📭 **Queue is empty!**")
        return
    
    text = "📝 **Current Queue:**\n\n"
    for i, song in enumerate(queue.get_list(), 1):
        text += f"{i}. {song['title']}\n"
        text += f"   ⏱ {song['duration'] // 60}:{song['duration'] % 60:02d} | 👤 {song['requested_by']}\n\n"
    
    await message.reply_text(text)


@app.on_message(filters.command("current"))
async def current(client, message: Message):
    """Show currently playing song"""
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    
    try:
        if not queue.is_empty():
            current = queue.get_list()[0] if queue.get_list() else None
            if current:
                await message.reply_text(
                    f"🎵 **Currently playing...**\n\n"
                    f"**Title:** {current['title']}\n"
                    f"**Duration:** {current['duration'] // 60}:{current['duration'] % 60:02d}\n"
                    f"**Requested by:** {current['requested_by']}"
                )
            else:
                await message.reply_text("❌ **Nothing is playing!**")
        else:
            await message.reply_text("❌ **Nothing is playing!**")
    except:
        await message.reply_text("❌ **Nothing is playing!**")


@app.on_message(filters.command("download"))
async def download(client, message: Message):
    """Download song as MP3 file"""
    if len(message.command) < 2:
        await message.reply_text(
            "❌ **Usage:** `/download <song name>`\n\n"
            "**Example:** `/download perfect ed sheeran`"
        )
        return
    
    query = " ".join(message.command[1:])
    msg = await message.reply_text(f"🔍 **Searching:** `{query}`...")
    
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            
            if not info or 'entries' not in info:
                await msg.edit_text("❌ **Not found!**")
                return
            
            video = info['entries'][0]
            title = video['title']
            duration = video.get('duration', 0)
            
            if duration > 600:
                await msg.edit_text("❌ **Song too long!** (Max 10 minutes)")
                return
            
            await msg.edit_text("⬇️ **Downloading...**")
            
            filename = ydl.prepare_filename(video)
            mp3_file = os.path.splitext(filename)[0] + '.mp3'
            
            await msg.edit_text("📤 **Uploading...**")
            
            await message.reply_audio(
                audio=mp3_file,
                title=title,
                duration=duration,
                caption=f"🎵 {title}"
            )
            
            await msg.delete()
            await message.reply_text("✅ **Download complete!**")
            
            # Cleanup
            os.remove(mp3_file)
            
    except Exception as e:
        logger.error(f"Download error: {e}")
        await msg.edit_text("❌ **An error occurred!**")


async def main():
    """Start the bot with web server for 24/7 hosting"""
    # Start PyTgCalls (this also starts the Pyrogram client)
    await pytgcalls.start()
    
    logger.info("🎵 Music Bot started with voice chat support!")
    print("🎵 Bot is running! Press Ctrl+C to stop.")
    
    # Import web server
    try:
        from web import web_server, keep_alive
        from aiohttp import web as aiohttp_web
        
        # Get port from environment (for Render deployment)
        PORT = int(os.getenv('PORT', 8080))
        
        # Create web server
        web_app = web_server()
        runner = aiohttp_web.AppRunner(web_app)
        await runner.setup()
        
        # Start web server
        site = aiohttp_web.TCPSite(runner, '0.0.0.0', PORT)
        await site.start()
        
        logger.info(f"🌐 Web server started on port {PORT}")
        print(f"🌐 Web server: http://0.0.0.0:{PORT}")
        
        # Start keep-alive task
        asyncio.create_task(keep_alive())
        logger.info("🔄 Keep-alive system activated!")
        
    except ImportError:
        logger.info("⚠️ Web server not available (web.py not found)")
        print("⚠️ Running without web server - OK for local testing")
    except Exception as e:
        logger.error(f"⚠️ Web server error: {e}")
        print(f"⚠️ Web server failed to start: {e}")
    
    # Keep bot running
    await asyncio.Event().wait()


if __name__ == "__main__":
    app.run(main())
