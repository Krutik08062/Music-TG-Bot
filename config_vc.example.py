"""
Configuration for Voice Chat Music Bot
IMPORTANT: This file is ignored by git for security
On Render, all values come from environment variables
"""

import os
from pathlib import Path

# Telegram API credentials (get from https://my.telegram.org)
# These MUST be set as environment variables on Render
API_ID = int(os.getenv('API_ID'))  # Set this on Render
API_HASH = os.getenv('API_HASH')  # Set this on Render

# Bot token from @BotFather
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Set this on Render

# Download path
DOWNLOAD_PATH = os.path.join(Path(__file__).parent, 'downloads')

# Maximum song duration (seconds)
MAX_DURATION = 600  # 10 minutes

# Audio quality settings
AUDIO_BITRATE = 192000  # 192 kbps
