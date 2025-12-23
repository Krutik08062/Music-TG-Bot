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

# Setup logging first
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Try to import from config_vc.py (local development)
# If not available, use environment variables (production/Render)
try:
    from config_vc import API_ID, API_HASH, BOT_TOKEN, DOWNLOAD_PATH
    logger.info("Using local config_vc.py")
except ImportError:
    # Running on production (Render) - use environment variables
    API_ID = int(os.getenv('API_ID'))
    API_HASH = os.getenv('API_HASH')
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    DOWNLOAD_PATH = os.path.join(Path(__file__).parent, 'downloads')
    
    # Debug: Log loaded values (hide sensitive parts)
    logger.info(f"Using environment variables:")
    logger.info(f"API_ID: {API_ID}")
    logger.info(f"API_HASH: {API_HASH[:8]}..." if API_HASH else "API_HASH: None")
    logger.info(f"BOT_TOKEN: {BOT_TOKEN[:15]}..." if BOT_TOKEN else "BOT_TOKEN: None")

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
    """Download audio from YouTube with retry logic"""
    logger.info(f"[DOWNLOAD] Starting download for query: {query}")
    
    # Enhanced options for bot detection bypass
    base_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_PATH, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'nocheckcertificate': True,
        'prefer_insecure': False,
        'age_limit': None,
        'geo_bypass': True,
        'socket_timeout': 30,
        'retries': 5,
        'fragment_retries': 5,
        'extractor_retries': 5,
        'file_access_retries': 5,
        'extractor_args': {
            'youtube': {
                'skip': ['hls', 'dash', 'translated_subs'],
                'player_client': ['android'],
                'player_skip': ['configs', 'webpage'],
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'X-YouTube-Client-Name': '3',
            'X-YouTube-Client-Version': '17.36.4',
        },
    }
    
    # Check for manual cookies from environment
    youtube_cookies = os.getenv('YOUTUBE_COOKIES')
    cookie_file_path = None
    if youtube_cookies:
        logger.info("[DOWNLOAD] Using cookies from YOUTUBE_COOKIES environment variable")
        # Save cookies to temporary file with proper format
        import tempfile
        cookie_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8')
        cookie_file.write(youtube_cookies)
        cookie_file.close()
        cookie_file_path = cookie_file.name
        base_opts['cookiefile'] = cookie_file_path
        logger.info(f"[DOWNLOAD] Cookie file created at: {cookie_file_path}")
    else:
        logger.warning("[DOWNLOAD] No YouTube cookies found in environment")
    
    # Try multiple strategies with delays between attempts
    strategies = [
        # Strategy 1: Android client with cookies (most reliable)
        lambda opts: {**opts, 'extractor_args': {'youtube': {'player_client': ['android']}}, 'verbose': True, 'quiet': False},
        # Strategy 2: iOS client
        lambda opts: {**opts, 'extractor_args': {'youtube': {'player_client': ['ios']}}, 'verbose': True, 'quiet': False},
        # Strategy 3: Web client with cookies
        lambda opts: {**opts, 'extractor_args': {'youtube': {'player_client': ['web']}}, 'format': 'ba[ext=m4a]/ba', 'verbose': True, 'quiet': False},
    ]
    
    for attempt, strategy in enumerate(strategies, 1):
        try:
            if attempt > 1:
                # Add delay between retries (exponential backoff)
                wait_time = 2 ** (attempt - 1)
                logger.info(f"Attempt {attempt}: Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
            
            ydl_opts = strategy(base_opts)
            
            logger.info(f"[DOWNLOAD] Attempt {attempt}: Trying with {ydl_opts.get('extractor_args', {}).get('youtube', {}).get('player_client', ['unknown'])[0]} client")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)
                
                # Check if search returned any results
                if not info or 'entries' not in info or len(info['entries']) == 0:
                    logger.error(f"[DOWNLOAD] Attempt {attempt}: Search returned 0 results for query: {query}")
                    if attempt == len(strategies):
                        # On last attempt, return None with specific error
                        logger.error("[DOWNLOAD] No search results found after all attempts")
                        if cookie_file_path:
                            try:
                                import os as os_module
                                os_module.remove(cookie_file_path)
                            except:
                                pass
                        return None
                    continue
                
                if info and 'entries' in info and len(info['entries']) > 0:
                    video = info['entries'][0]
                    filename = ydl.prepare_filename(video)
                    
                    logger.info(f"Successfully downloaded: {video['title']}")
                    return {
                        'file': filename,
                        'title': video['title'],
                        'duration': video.get('duration', 0),
                        'url': video['webpage_url'],
                        'thumbnail': video.get('thumbnail'),
                        'requested_by': msg.from_user.mention
                    }
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            # Log full error for debugging
            logger.error(f"[DOWNLOAD] Attempt {attempt} failed: {error_type}")
            logger.error(f"[DOWNLOAD] Error message: {error_msg[:300]}")
            
            if 'could not find chrome cookies' in error_msg.lower():
                logger.debug(f"Attempt {attempt}: No Chrome cookies available, trying next strategy")
                continue
            elif 'sign in to confirm' in error_msg.lower() or 'bot' in error_msg.lower():
                logger.warning(f"Attempt {attempt}: Bot detection triggered, trying next strategy")
                continue
            elif 'private' in error_msg.lower() or 'unavailable' in error_msg.lower():
                logger.warning(f"Attempt {attempt}: Video unavailable or private")
                continue
            else:
                logger.error(f"Attempt {attempt}: Unhandled error, trying next strategy")
                if attempt == len(strategies):
                    # Cleanup temp cookie file if exists
                    if cookie_file_path:
                        try:
                            import os as os_module
                            os_module.remove(cookie_file_path)
                        except:
                            pass
                    return None
                continue
    
    # Cleanup temp cookie file if exists
    if cookie_file_path:
        try:
            import os as os_module
            os_module.remove(cookie_file_path)
            logger.info("[DOWNLOAD] Cleaned up temporary cookie file")
        except Exception as cleanup_error:
            logger.warning(f"[DOWNLOAD] Failed to cleanup cookie file: {cleanup_error}")
    
    logger.error("[DOWNLOAD] All download strategies failed after trying all methods")
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
    logger.info(f"[PLAY] Command received from {message.from_user.id} in chat {message.chat.id}")
    
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
        try:
            await msg.edit_text(
                "❌ **No results found!**\n\n"
                "YouTube search returned no results for this query.\n\n"
                "**Try these:**\n"
                "• Add artist name: `/play tum ho rockstar`\n"
                "• Be more specific: `/play tum ho toh rockstar arjit singh`\n"
                "• Try different song\n\n"
                "_Tip: More specific queries work better!_"
            )
        except:
            await message.reply_text(
                "❌ **No results found!**\n\n"
                "YouTube search returned no results for this query.\n\n"
                "**Try these:**\n"
                "• Add artist name: `/play tum ho rockstar`\n"
                "• Be more specific: `/play tum ho toh rockstar arjit singh`\n"
                "• Try different song\n\n"
                "_Tip: More specific queries work better!_"
            )
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
    
    # Enhanced options for bot detection bypass
    base_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
        'quiet': True,
        'nocheckcertificate': True,
        'socket_timeout': 30,
        'retries': 3,
        'extractor_args': {
            'youtube': {
                'skip': ['hls', 'dash'],
                'player_client': ['android', 'web'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'DNT': '1',
        },
        'age_limit': None,
        'geo_bypass': True,
    }
    
    # Try multiple times with delay
    ydl_opts = base_opts.copy()
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            
            if not info or 'entries' not in info:
                try:
                    await msg.edit_text(
                        "❌ **Download failed!**\n\n"
                        "YouTube is blocking automated downloads.\n"
                        "Try a different song or wait a few minutes."
                    )
                except:
                    await message.reply_text(
                        "❌ **Download failed!**\n\n"
                        "YouTube is blocking automated downloads.\n"
                        "Try a different song or wait a few minutes."
                    )
                return
            
            video = info['entries'][0]
            title = video['title']
            duration = video.get('duration', 0)
            
            if duration > 600:
                try:
                    await msg.edit_text("❌ **Song too long!** (Max 10 minutes)")
                except:
                    await message.reply_text("❌ **Song too long!** (Max 10 minutes)")
                return
            
            try:
                await msg.edit_text("⬇️ **Downloading...**")
            except:
                msg = await message.reply_text("⬇️ **Downloading...**")
            
            filename = ydl.prepare_filename(video)
            mp3_file = os.path.splitext(filename)[0] + '.mp3'
            
            try:
                await msg.edit_text("📤 **Uploading...**")
            except:
                msg = await message.reply_text("📤 **Uploading...**")
            
            await message.reply_audio(
                audio=mp3_file,
                title=title,
                duration=duration,
                caption=f"🎵 {title}"
            )
            
            try:
                await msg.delete()
            except:
                pass
            await message.reply_text("✅ **Download complete!**")
            
            # Cleanup
            os.remove(mp3_file)
            
    except Exception as e:
        logger.error(f"Download error: {e}")
        try:
            await msg.edit_text(
                "❌ **An error occurred!**\n\n"
                "YouTube may be blocking downloads.\n"
                "Try again later or with a different song."
            )
        except:
            await message.reply_text(
                "❌ **An error occurred!**\n\n"
                "YouTube may be blocking downloads.\n"
                "Try again later or with a different song."
            )


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
