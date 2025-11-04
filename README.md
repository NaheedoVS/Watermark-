# 🎬 Telegram Video Watermark Adder Bot

A modern Telegram bot that adds custom image watermarks to your videos — built with **Pyrogram 2.x** and **FFmpeg**.  
Developed by [@Doctorstra](https://github.com/Doctorstra), updated for 2025 deployment compatibility.

---

## ✨ Features

- 🖼️ Save a custom watermark image (JPG/PNG)
- 📏 Automatically resizes watermark to video resolution
- ⚙️ Adjustable watermark **position** and **size**
- 💾 Remembers user settings
- 📡 Progress tracking for uploads/downloads
- 🚫 Cancel ongoing process anytime
- 🧩 Force subscription (optional)
- 🗂️ Logging and admin broadcast system
- ☁️ Uploads to [Streamtape](https://streamtape.com/) for large videos (>2GB)
- 🔧 Configurable FFmpeg encoding presets

---

## 🤖 Demo Bot

<a href="https://t.me/Dads_links_VideoWatermark_Bot"><img src="https://img.shields.io/badge/Try%20on-Telegram-blue?logo=telegram" alt="Demo Bot"></a>

---

## ⚙️ Environment Variables (Configs)

| Variable | Description |
|-----------|--------------|
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Telegram API hash from [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) |
| `BOT_USERNAME` | Your bot username (without `@`) |
| `OWNER_ID` | Telegram user ID of the bot owner |
| `LOG_CHANNEL` | Channel ID for logs |
| `DATABASE_URL` | MongoDB URI for saving user data |
| `UPDATES_CHANNEL` | (Optional) Force-subscription channel ID |
| `PRESET` | (Optional) FFmpeg preset (default: `ultrafast`) |
| `STREAMTAPE_API_USERNAME` | (Optional) Streamtape API username |
| `STREAMTAPE_API_PASS` | (Optional) Streamtape API password |
| `ALLOW_UPLOAD_TO_STREAMTAPE` | `True` / `False` to enable Streamtape uploads |
| `BROADCAST_AS_COPY` | `True` / `False` for broadcast behavior |

---

## 💬 BotFather Commands

:
```
start - start the bot
status - Show number of users in DB & Bot Status
broadcast - Broadcast replied message to DB Users
cancel - Cancel Current Task
settings - User Settings Panel
reset - Reset all settings to default
```

### Support Group:
<a href="https://t.me/Dads_links"><img src="https://img.shields.io/badge/Telegram-Join%20Telegram%20Group-blue.svg?logo=telegram"></a>


---

## 🚀 Deployment Options

### 🟣 **1. Deploy on Heroku (Recommended for Beginners)**

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Doctorstra/watermark-bot)

Make sure to:
- Set all **environment variables** properly.
- Use stack `heroku-24` (Python 3.12+).

---

### 🟩 **2. Deploy Locally / VPS**

```bash
git clone https://github.com/Doctorstra/watermark-bot
cd watermark-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 bot.py


### Follow on:
<p align="left">
<a href="https://github.com/Doctorstra"><img src="https://img.shields.io/badge/GitHub-Follow%20on%20GitHub-inactive.svg?logo=github"></a>
</p>
