# 🎵 Telegram Music Bot

A simple and easy-to-use Telegram bot that downloads music from YouTube and sends it to users as MP3 files.

## ✨ Features

- 🔍 Search songs by name
- ⬇️ Download music from YouTube
- 🎵 Send audio as MP3 files
- 🚀 Fast and reliable
- 💡 Simple and clean interface
- 🎧 High-quality audio (192kbps)

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and bot introduction |
| `/play <song name>` | Search and download a song |
| `/help` | Show all available commands |
| `/about` | Information about the bot |

## 🛠️ Tech Stack

- **Language:** Python 3.8+
- **Bot Library:** python-telegram-bot
- **Downloader:** yt-dlp
- **Audio Processing:** FFmpeg

## 📦 Installation

### Prerequisites

1. **Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)

2. **FFmpeg**
   - **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
   - **Linux:** `sudo apt install ffmpeg`
   - **Mac:** `brew install ffmpeg`

### Setup Steps

1. **Clone or download this repository**
   ```bash
   cd "Music TG Bot"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on Linux/Mac
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get your Bot Token**
   - Open Telegram and search for [@BotFather](https://t.me/BotFather)
   - Send `/newbot`
   - Follow the instructions to create your bot
   - Copy the bot token

5. **Configure the bot**
   
   **Option 1: Using environment variable (Recommended)**
   ```bash
   # Windows (PowerShell)
   $env:BOT_TOKEN="your_bot_token_here"
   
   # Windows (CMD)
   set BOT_TOKEN=your_bot_token_here
   
   # Linux/Mac
   export BOT_TOKEN="your_bot_token_here"
   ```
   
   **Option 2: Edit config.py**
   - Open `config.py`
   - Replace `YOUR_BOT_TOKEN_HERE` with your actual token
   - ⚠️ **Warning:** Don't share this file if you hardcode the token!

6. **Run the bot**
   ```bash
   python bot.py
   ```

7. **Test it!**
   - Open Telegram
   - Search for your bot
   - Send `/start`
   - Try `/play perfect ed sheeran`

## 📖 Usage Examples

```
/play shape of you
/play bohemian rhapsody
/play blinding lights
/play imagine dragons believer
```

## 🏗️ Project Structure

```
music_bot/
│
├── bot.py              # Main bot application
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .env.example       # Environment variable template
├── .gitignore         # Git ignore file
└── downloads/         # Temporary audio downloads (auto-created)
```

## ⚙️ Configuration

Edit `config.py` to customize:

- `MAX_DURATION`: Maximum song length (default: 10 minutes)
- `MAX_FILE_SIZE`: Maximum file size (default: 50MB)
- `DOWNLOAD_PATH`: Where to store temporary files

## 🚀 Deployment

### For 24/7 hosting, you can use:

1. **Railway** (Free tier available)
   - Sign up at [railway.app](https://railway.app)
   - Connect your GitHub repo
   - Add BOT_TOKEN environment variable
   - Deploy

2. **Render** (Free tier available)
   - Sign up at [render.com](https://render.com)
   - Create a new Web Service
   - Connect your repo
   - Add environment variables
   - Deploy

3. **VPS** (DigitalOcean, AWS, etc.)
   - Rent a server
   - Clone repo
   - Set up Python and dependencies
   - Run with `nohup python bot.py &`

## ⚠️ Important Notes

- This bot is for **educational and personal use only**
- Downloading copyrighted content may violate YouTube's Terms of Service
- Respect copyright laws and content creator rights
- Use responsibly and at your own risk
- Downloaded files are automatically deleted after sending

## 🐛 Troubleshooting

### Bot doesn't respond
- Check if your bot token is correct
- Ensure Python is running without errors
- Check internet connection

### "FFmpeg not found" error
- Install FFmpeg and add it to your system PATH
- Restart your terminal/computer after installation

### Download fails
- Some videos may be restricted or age-gated
- Try a different search query
- Check if the video is available in your region

### Bot crashes
- Check the console for error messages
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Make sure you have enough disk space

## 📚 Learning Concepts

This project demonstrates:
- ✅ Working with APIs (Telegram Bot API)
- ✅ File handling and management
- ✅ Network requests and downloads
- ✅ Asynchronous programming
- ✅ Error handling
- ✅ Command-line applications
- ✅ Third-party library integration

## 📝 Future Enhancements (Optional)

- [ ] Queue system for multiple songs
- [ ] Playlist support
- [ ] Voice chat music playback
- [ ] Favorites/bookmarks
- [ ] Song recommendations
- [ ] Admin panel
- [ ] Statistics tracking
- [ ] Inline search results

## 📄 License

This project is for educational purposes. Use responsibly and respect copyright laws.

## 🤝 Contributing

Feel free to fork this project and add your own features!

## 💬 Support

If you encounter any issues:
1. Check the troubleshooting section
2. Ensure all dependencies are installed
3. Verify FFmpeg is properly installed
4. Check Python version (3.8+)

## 🎓 Perfect for

- ⭐ College projects
- ⭐ Learning Python
- ⭐ Understanding bot development
- ⭐ API integration practice
- ⭐ Portfolio projects

---

**Made with ❤️ for music lovers!** 🎵

**Difficulty Level:** ⭐⭐☆☆☆ (Beginner-Friendly)
