# bot.py
# (c) @AbirHasan2005 — Cleaned, optimized, and compression-enabled

import os
import time
import json
import random
import asyncio
import aiohttp
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image
from core.ffmpeg import vidmark, compress_video
from core.clean import delete_all, delete_trash
from pyrogram import Client, filters
from configs import Config
from core.handlers.main_db_handler import db
from core.display_progress import progress_for_pyrogram, humanbytes
from core.handlers.force_sub_handler import handle_force_subscribe
from core.handlers.upload_video_handler import send_video_handler
from core.handlers.broadcast_handlers import broadcast_handler
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait

# Initialize bot client
AHBot = Client(
    Config.BOT_USERNAME,
    bot_token=Config.BOT_TOKEN,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH
)

# Temporary in-memory compression settings
COMP_SETTINGS = {}


def get_user_comp_settings(user_id: int):
    if user_id not in COMP_SETTINGS:
        COMP_SETTINGS[user_id] = {"enabled": True, "crf": 18}
    return COMP_SETTINGS[user_id]


# --- Start / Help ---
@AHBot.on_message(filters.command(["start", "help"]) & filters.private)
async def start_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)
        await bot.send_message(
            Config.LOG_CHANNEL,
            f"#NEW_USER: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started @{Config.BOT_USERNAME}"
        )

    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, message)
        if fsub == 400:
            return

    await message.reply_text(
        Config.USAGE_WATERMARK_ADDER,
        parse_mode="Markdown",
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Developer", url="https://t.me/Dads_links"),
             InlineKeyboardButton("Support", url="https://t.me/Dads_links")],
            [InlineKeyboardButton("Channel", url="https://t.me/Dads_links")],
            [InlineKeyboardButton("Source Code", url="https://github.com/Doctorstra")]
        ])
    )


# --- Reset ---
@AHBot.on_message(filters.command("reset") & filters.private)
async def reset_handler(bot, message):
    await db.delete_user(message.from_user.id)
    await db.add_user(message.from_user.id)
    COMP_SETTINGS.pop(message.from_user.id, None)
    await message.reply_text("✅ Settings reset successfully.")


# --- Settings ---
@AHBot.on_message(filters.command("settings") & filters.private)
async def settings_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)

    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, message)
        if fsub == 400:
            return

    pos = await db.get_position(message.from_user.id)
    size = await db.get_size(message.from_user.id)
    user_cfg = get_user_comp_settings(message.from_user.id)

    position_map = {
        "5:main_h-overlay_h": "Bottom Left",
        "main_w-overlay_w-5:main_h-overlay_h-5": "Bottom Right",
        "main_w-overlay_w-5:5": "Top Right",
        "5:5": "Top Left"
    }
    pos_tag = position_map.get(pos, "Top Left")
    size_tag = f"{size}%"
    comp_tag = "Enabled" if user_cfg["enabled"] else "Disabled"
    crf_tag = user_cfg["crf"]

    await message.reply_text(
        f"⚙️ **Your Settings:**\n\n"
        f"📍 Position: {pos_tag}\n"
        f"📏 Size: {size_tag}\n\n"
        f"🎞️ Compression: {comp_tag}\n"
        f"🧮 CRF: {crf_tag}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Toggle Compression ({comp_tag})", callback_data="togglecompress")],
            [InlineKeyboardButton("Set CRF 18", callback_data="crf_18"),
             InlineKeyboardButton("Set CRF 23", callback_data="crf_23"),
             InlineKeyboardButton("Set CRF 28", callback_data="crf_28")],
            [InlineKeyboardButton("Reset", callback_data="reset")]
        ])
    )


# --- Callback Query Handler ---
@AHBot.on_callback_query()
async def callback_handler(bot, query: CallbackQuery):
    data = query.data

    if data == "togglecompress":
        cfg = get_user_comp_settings(query.from_user.id)
        cfg["enabled"] = not cfg["enabled"]
        await query.answer(f"Compression {'Enabled' if cfg['enabled'] else 'Disabled'}")
        await settings_handler(bot, query.message)
        return

    if data.startswith("crf_"):
        try:
            crf_val = int(data.split("_")[1])
            if not 10 <= crf_val <= 51:
                raise ValueError
        except ValueError:
            await query.answer("❌ Invalid CRF value!", show_alert=True)
            return

        cfg = get_user_comp_settings(query.from_user.id)
        cfg["crf"] = crf_val
        await query.answer(f"CRF set to {crf_val}")
        await settings_handler(bot, query.message)
        return

    if data == "reset":
        await reset_handler(bot, query.message)
        return


# --- Main Video/Photo Handler ---
@AHBot.on_message((filters.video | filters.document | filters.photo) & filters.private)
async def video_handler(bot, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id)

    if Config.UPDATES_CHANNEL:
        fsub = await handle_force_subscribe(bot, message)
        if fsub == 400:
            return

    # Handle watermark image
    if message.photo or (message.document and message.document.mime_type.startswith("image/")):
        editable = await message.reply_text("📥 Downloading watermark image...")
        user_dir = os.path.join(Config.DOWN_PATH, str(message.from_user.id))
        os.makedirs(user_dir, exist_ok=True)
        watermark_path = os.path.join(user_dir, "thumb.jpg")
        await bot.download_media(message, file_name=watermark_path)
        await editable.edit("✅ Watermark image saved!\nNow send a video to apply it.")
        return

    # Handle video
    if not (message.video or (message.document and message.document.mime_type.startswith("video/"))):
        await message.reply_text("❌ Please send a valid video file.")
        return

    work_dir = os.path.join(Config.DOWN_PATH, "WatermarkAdder", str(message.from_user.id))
    os.makedirs(work_dir, exist_ok=True)
    status_file = os.path.join(work_dir, "status.json")

    if os.path.exists(status_file):
        await message.reply_text("⚠️ I’m busy with another task. Try again later.")
        return

    watermark_path = os.path.join(Config.DOWN_PATH, str(message.from_user.id), "thumb.jpg")
    if not os.path.exists(watermark_path):
        await message.reply_text("⚠️ You haven’t set any watermark yet!\nPlease send an image first.")
        return

    editable = await message.reply_text("📥 Downloading video...")
    try:
        downloaded = await bot.download_media(
            message=message,
            file_name=work_dir,
            progress=progress_for_pyrogram,
            progress_args=("Downloading video...", editable, time.time())
        )
    except Exception as e:
        await editable.edit(f"❌ Failed to download.\nError: `{e}`")
        return

    pos = await db.get_position(message.from_user.id)
    size = await db.get_size(message.from_user.id)
    preset = Config.PRESET or "ultrafast"
    await editable.edit("✨ Adding watermark, please wait...")

    try:
        output_vid = await vidmark(
            downloaded,
            editable,
            os.path.join(work_dir, "progress.txt"),
            watermark_path,
            f"output_{int(time.time())}.mp4",
            0,
            None,
            status_file,
            preset,
            pos,
            size
        )
    except Exception as e:
        await editable.edit(f"❌ Watermarking failed.\nError: `{e}`")
        await delete_all()
        return

    if not output_vid or not os.path.exists(output_vid):
        await editable.edit("❌ Something went wrong.")
        return

    # Compression Logic
    cfg = get_user_comp_settings(message.from_user.id)
    if cfg.get("enabled", True):
        await editable.edit("🎞️ Compression enabled. Compressing video...")
        compressed_out = os.path.splitext(output_vid)[0] + "_compressed.mp4"
        try:
            compressed = await compress_video(
                output_vid,
                editable,
                os.path.join(work_dir, "progress.txt"),
                compressed_out,
                0,
                None,
                status_file,
                crf=cfg.get("crf", 18)
            )
            if compressed:
                output_vid = compressed
                await editable.edit("✅ Compression done! Uploading...")
            else:
                await editable.edit("⚠️ Compression skipped. Uploading original...")
        except Exception as e:
            await editable.edit(f"⚠️ Compression failed. Using original. Error: `{e}`")

    else:
        await editable.edit("📤 Compression disabled. Uploading original...")

    # Upload
    try:
        await send_video_handler(
            bot,
            message,
            output_vid,
            None,
            0,
            0,
            0,
            editable,
            None,
            os.path.getsize(output_vid)
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await send_video_handler(
            bot,
            message,
            output_vid,
            None,
            0,
            0,
            0,
            editable,
            None,
            os.path.getsize(output_vid)
        )
    except Exception as e:
        await editable.edit(f"❌ Upload failed.\nError: `{e}`")
    finally:
        await delete_all()


# --- Broadcast ---
@AHBot.on_message(filters.private & filters.command("broadcast") & filters.user(Config.OWNER_ID) & filters.reply)
async def broadcast_cmd(bot, message):
    await broadcast_handler(c=bot, m=message)


# --- Status ---
@AHBot.on_message(filters.command("status") & filters.private)
async def status_cmd(_, message):
    status_file = os.path.join(Config.DOWN_PATH, "WatermarkAdder", "status.json")
    busy = os.path.exists(status_file)
    text = "🚦 I'm busy right now." if busy else "✅ I'm free! Send me a video."
    if int(message.from_user.id) == Config.OWNER_ID:
        total_users = await db.total_users_count()
        text += f"\n\n👥 Total Users: `{total_users}`"
    await message.reply_text(text, parse_mode="Markdown")


# --- Run Bot ---
if __name__ == "__main__":
    print("✅ Bot is running with compression support...")
    AHBot.run()
