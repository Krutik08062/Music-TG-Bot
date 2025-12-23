"""
Configuration for Voice Chat Music Bot
"""

import os
from pathlib import Path

# Telegram API credentials (get from https://my.telegram.org)
API_ID = int(os.getenv('API_ID', '24561470'))  # Your API ID
API_HASH = os.getenv('API_HASH', '1e2d3c0c1fd09ae41a710d2daea8374b')  # Your API Hash

# Bot token from @BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN', '8503288812:AAGrHMRJ-tda_r95h4GVOxTsM3Kvr4bPrxk')

# Download path
DOWNLOAD_PATH = os.path.join(Path(__file__).parent, 'downloads')

# Maximum song duration (seconds)
MAX_DURATION = 600  # 10 minutes

# Audio quality settings
AUDIO_BITRATE = 192000  # 192 kbps
