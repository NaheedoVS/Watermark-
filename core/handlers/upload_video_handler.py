# (c) @AbirHasan2005 | Updated by GPT-5 (2025)
# Modern async video upload handler for Pyrogram 2.x

import time
import asyncio
import logging
from humanfriendly import format_timespan
from configs import Config
from core.display_progress import progress_for_pyrogram, humanbytes
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)


async def send_video_handler(
    bot,
    cmd,
    output_vid: str,
    video_thumbnail: str,
    duration: int,
    width: int,
    height: int,
    editable,
    logs_msg,
    file_size: int
):
    """
    Upload processed video to Telegram with live progress updates.
    Handles FloodWait, network errors, and retries safely.
    """
    c_time = time.time()

    caption = (
        f"🎬 **File Name:** `{output_vid.split('/')[-1]}`\n"
        f"🕒 **Duration:** `{format_timespan(duration)}`\n"
        f"📦 **File Size:** `{humanbytes(file_size)}`\n\n"
        f"{Config.CAPTION}"
    )

    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Dads_links_bot")],
            [InlineKeyboardButton("📢 Bots Channel", url="https://t.me/Dads_links")],
            [InlineKeyboardButton("💬 Support Group", url="https://t.me/Dads_links")]
        ]
    )

    try:
        sent_vid = await bot.send_video(
            chat_id=cmd.chat.id,
            video=output_vid,
            caption=caption,
            thumb=video_thumbnail,
            duration=duration,
            width=width,
            height=height,
            reply_to_message_id=cmd.id if hasattr(cmd, "id") else cmd.message_id,
            supports_streaming=True,
            reply_markup=buttons,
            progress=progress_for_pyrogram,
            progress_args=(
                0,  # current progress placeholder
                file_size,
                "Uploading Video ...",
                editable,
                logs_msg,
                c_time
            ),
        )
        return sent_vid

    except FloodWait as e:
        logger.warning(f"⏳ FloodWait: sleeping for {e.value}s during video upload.")
        await asyncio.sleep(e.value)
        return await send_video_handler(
            bot, cmd, output_vid, video_thumbnail, duration, width, height, editable, logs_msg, file_size
        )

    except RPCError as e:
        logger.error(f"❌ RPCError during video upload: {e}")
        await bot.send_message(
            cmd.chat.id,
            "⚠️ **Upload failed due to a Telegram network error. Please try again later.**",
            reply_to_message_id=cmd.id if hasattr(cmd, 'id') else cmd.message_id
        )
        return None

    except Exception as e:
        logger.exception(f"❌ Unexpected error in upload handler: {e}")
        await bot.send_message(
            cmd.chat.id,
            "❌ **Unexpected error occurred while uploading.**",
            reply_to_message_id=cmd.id if hasattr(cmd, 'id') else cmd.message_id
        )
        return None
