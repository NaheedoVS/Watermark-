# (c) @AbirHasan2005 | Updated by GPT-5
# Telegram Video Watermark Adder Bot Configuration
# Compatible with Python 3.12+, Heroku-24, and latest Pyrogram versions

import os


class Config:
    """Bot configuration variables loaded from environment."""

    # --- Telegram API Credentials ---
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    API_ID = int(os.getenv("API_ID", 12345))
    API_HASH = os.getenv("API_HASH")

    # --- Owner / Admin ---
    OWNER_ID = int(os.getenv("OWNER_ID", 1445283714))
    BOT_USERNAME = os.getenv("BOT_USERNAME", "VideoWatermark_Bot")

    # --- Database ---
    DATABASE_URL = os.getenv("DATABASE_URL")  # MongoDB URI

    # --- Logging & Updates ---
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))
    UPDATES_CHANNEL = os.getenv("UPDATES_CHANNEL")

    # --- Storage & Encoding ---
    DOWN_PATH = os.getenv("DOWN_PATH", "./downloads")
    PRESET = os.getenv("PRESET", "ultrafast")

    # --- Streamtape Upload (optional) ---
    STREAMTAPE_API_USERNAME = os.getenv("STREAMTAPE_API_USERNAME", "NoNeed")
    STREAMTAPE_API_PASS = os.getenv("STREAMTAPE_API_PASS", "NoNeed")
    ALLOW_UPLOAD_TO_STREAMTAPE = os.getenv("ALLOW_UPLOAD_TO_STREAMTAPE", "True").lower() == "true"

    # --- Broadcast Settings ---
    BROADCAST_AS_COPY = os.getenv("BROADCAST_AS_COPY", "False").lower() == "true"

    # --- Caption / Branding ---
    CAPTION = os.getenv("CAPTION", "By @AHToolsBot")

    # --- Help / Usage Message ---
    USAGE_WATERMARK_ADDER = """
👋 **Hi, I'm the Telegram Video Watermark Adder Bot!**

🎞️ **How to Add a Watermark:**
1. Send me any JPG or PNG image — this will be used as your watermark/logo.
2. Then send me any MP4 or MKV video.
3. I’ll add your watermark automatically and return the result!

⚙️ **Notes:**
- Only one video can be processed at a time.
- Performance may vary depending on the server load.
- If you face any issue, please report it in the [Support Group](https://t.me/Dads_links).

🧑‍💻 **Developer:** @Dads_links
"""

    # --- Progress Template ---
    PROGRESS = """<b>
╭━━━━❰ Progress Bar ❱━➣
┣⪼ 📊 Percentage: {0}%
┣⪼ ✅ Done: {1}
┣⪼ 🚀 Speed: {3}/s
┣⪼ ⏰ ETA: {4}
╰━━━━━━━━━━━━━━━➣
</b>"""
