"""
Web server for keeping the bot alive on Render.com free tier
This prevents the bot from sleeping due to inactivity
"""

import os
from aiohttp import web
import asyncio
import aiohttp
import logging

log = logging.getLogger(__name__)

# Your Render URL - Update this after deploying!
# Format: https://your-bot-name.onrender.com/
WEB_URL = os.getenv('WEB_URL', 'https://your-music-bot.onrender.com/')

# Ping interval - 3 minutes (180 seconds)
WEB_SLEEP = 3 * 60

routes = web.RouteTableDef()


@routes.get('/', allow_head=True)
async def root_handler(request):
    """Root endpoint - responds to health checks"""
    return web.Response(text="🎵 Music Bot is alive!")


@routes.get('/health', allow_head=True)
async def health_handler(request):
    """Health check endpoint"""
    return web.Response(text="OK")


@routes.get('/status', allow_head=True)
async def status_handler(request):
    """Status endpoint"""
    return web.json_response({
        'status': 'running',
        'bot': 'music_bot',
        'version': '2.0'
    })


def web_server():
    """Create and configure the web server"""
    app = web.Application()
    app.add_routes(routes)
    return app


async def keep_alive():
    """
    Keep-alive task that pings the bot every 3 minutes
    This prevents Render.com from shutting down the free tier bot
    """
    if WEB_URL:
        log.info(f"🔄 Keep-alive system started! Pinging {WEB_URL} every {WEB_SLEEP // 60} minutes")
        
        while True:
            await asyncio.sleep(WEB_SLEEP)
            
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as session:
                    async with session.get(WEB_URL) as resp:
                        log.info(
                            f"✅ Pinged {WEB_URL} - Status: {resp.status}"
                        )
            except asyncio.TimeoutError:
                log.warning("⚠️ Keep-alive ping timeout")
            except Exception as e:
                log.error(f"❌ Keep-alive error: {e}")
