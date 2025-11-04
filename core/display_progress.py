# (c) @AbirHasan2005 | Updated by GPT-5 (2025)
# Modern async progress display utility for Pyrogram 2.x

import math
import time
import asyncio
from configs import Config
from pyrogram.types import Message


async def progress_for_pyrogram(
    current: int,
    total: int,
    action: str,
    message: Message,
    logs_msg: Message,
    start_time: float
):
    """
    Display real-time upload/download progress in Telegram.
    Uses adaptive rate limiting to prevent flood errors.
    """
    now = time.time()
    diff = now - start_time

    # Update message every ~3 seconds or on completion
    if current == total or diff - getattr(progress_for_pyrogram, "_last_update", 0) >= 3:
        setattr(progress_for_pyrogram, "_last_update", diff)

        if total == 0:
            return

        try:
            percentage = (current / total) * 100
            speed = current / diff if diff > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0

            elapsed_time = TimeFormatter(diff)
            eta_formatted = TimeFormatter(eta)

            # Build visual progress bar
            filled = "●" * math.floor(percentage / 5)
            empty = "○" * (20 - math.floor(percentage / 5))
            bar = f"[{filled}{empty}]"

            text = (
                f"**{action}**\n\n"
                f"{bar}\n"
                f"**Progress:** `{percentage:.2f}%`\n"
                f"**Done:** `{humanbytes(current)} / {humanbytes(total)}`\n"
                f"**Speed:** `{humanbytes(speed)}/s`\n"
                f"**Elapsed:** `{elapsed_time}` | **ETA:** `{eta_formatted}`"
            )

            # Send progress updates (rate-limited)
            await asyncio.gather(
                _safe_edit(message, text),
                _safe_edit(logs_msg, text)
            )

        except Exception as e:
            print(f"⚠️ Progress update error: {e}")


async def _safe_edit(msg: Message, text: str):
    """Safely edit Telegram messages, ignoring rate limits."""
    try:
        if msg:
            await msg.edit_text(text, parse_mode="markdown")
    except Exception:
        # FloodWait and message not modified errors are ignored
        await asyncio.sleep(0.1)


def humanbytes(size: int) -> str:
    """Convert bytes to human-readable size."""
    if not size:
        return "0 B"
    power = 2 ** 10
    n = 0
    dic_powerN = {0: "B", 1: "KiB", 2: "MiB", 3: "GiB", 4: "TiB"}
    while size >= power and n < 4:
        size /= power
        n += 1
    return f"{size:.2f} {dic_powerN[n]}"


def TimeFormatter(seconds: float) -> str:
    """Format seconds into a readable duration string."""
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds:
        parts.append(f"{seconds}s")
    return " ".join(parts) if parts else "0s"
