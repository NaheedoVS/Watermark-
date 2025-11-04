# (c) @AbirHasan2005 | Updated by GPT-5 (2025)
# Modern FFmpeg integration for Telegram Video Watermark Bot

import asyncio
import math
import os
import re
import json
import time
from pathlib import Path
from typing import Optional
from configs import Config
from humanfriendly import format_timespan
from core.display_progress import TimeFormatter
from pyrogram.errors import FloodWait


async def vidmark(
    the_media: str,
    message,
    working_dir: str,
    watermark_path: str,
    output_vid: str,
    total_time: float,
    logs_msg,
    status_path: str,
    preset: str,
    position: str,
    size: str
) -> Optional[str]:
    """
    Add watermark to a video asynchronously using FFmpeg.
    Modernized for async I/O and safe progress handling.
    """

    progress_file = Path(working_dir) / "progress.txt"
    if progress_file.exists():
        progress_file.unlink()

    command = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-loglevel", "error",
        "-progress", str(progress_file),
        "-i", the_media,
        "-i", watermark_path,
        "-filter_complex",
        f"[1][0]scale2ref=w='iw*{size}/100':h='ow/mdar'[wm][vid];[vid][wm]overlay={position}",
        "-c:v", "libx264",
        "-preset", preset,
        "-tune", "film",
        "-c:a", "copy",
        output_vid
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    # Write process ID to status.json
    try:
        with open(status_path, "w") as f:
            json.dump({"pid": process.pid}, f, indent=2)
    except Exception:
        pass

    start_time = time.time()
    last_update = 0

    # Periodically read progress updates from FFmpeg
    while True:
        await asyncio.sleep(3)
        if not progress_file.exists():
            continue

        try:
            text = progress_file.read_text()
            out_time_ms = _extract_value(text, r"out_time_ms=(\d+)")
            progress = _extract_value(text, r"progress=(\w+)") or "continue"
            speed = float(_extract_value(text, r"speed=(\d+\.?\d*)") or 1.0)

            elapsed_sec = int(out_time_ms) / 1_000_000
            percentage = min(100, (elapsed_sec / total_time) * 100)
            remaining = max(0, total_time - elapsed_sec)
            eta = TimeFormatter(remaining / speed * 1000)

            # Progress bar visualization
            filled = "▓" * int(percentage // 10)
            empty = "░" * (10 - int(percentage // 10))
            progress_bar = f"[{filled}{empty}]"

            stats = (
                f"📦 **Adding Watermark [Preset: `{preset}`]**\n\n"
                f"{progress_bar} `{percentage:.2f}%`\n"
                f"⏰ **ETA:** `{eta}`\n"
                f"🎞 **Position:** `{position}`\n"
                f"⚙️ **PID:** `{process.pid}`\n"
                f"🕒 **Duration:** `{format_timespan(total_time)}`"
            )

            # Throttle message edits
            if time.time() - last_update > 3:
                await _safe_edit(message, stats)
                await _safe_edit(logs_msg, stats)
                last_update = time.time()

            if progress == "end":
                break

        except Exception as e:
            print(f"⚠️ FFmpeg progress read error: {e}")

        if process.returncode is not None:
            break

    # Wait for process completion
    await process.wait()
    stdout, stderr = await process.communicate()

    if Path(output_vid).exists():
        print(f"✅ FFmpeg completed successfully: {output_vid}")
        return output_vid
    else:
        print(f"❌ FFmpeg failed: {stderr.decode()}")
        return None


async def take_screen_shot(video_file: str, output_directory: str, ttl: int) -> Optional[str]:
    """Capture a frame at given timestamp."""
    output_path = Path(output_directory) / f"{int(time.time())}.jpg"

    command = [
        "ffmpeg",
        "-ss", str(ttl),
        "-i", video_file,
        "-frames:v", "1",
        "-q:v", "2",
        str(output_path)
    ]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await process.wait()

    if output_path.exists():
        return str(output_path)
    return None


# ────────────────────────────────
# 🔧 Helper Functions
# ────────────────────────────────
def _extract_value(text: str, pattern: str) -> Optional[str]:
    """Extract value from FFmpeg progress log using regex."""
    match = re.findall(pattern, text)
    return match[-1] if match else None


async def _safe_edit(msg, text: str):
    """Edit Telegram messages safely to avoid flood errors."""
    if not msg:
        return
    try:
        await msg.edit_text(text, disable_web_page_preview=True)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception:
        pass
            except FloodWait as e:
                await asyncio.sleep(e.x)
                pass
            except:
                pass
        
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    print(e_response)
    print(t_response)
    if os.path.lexists(output_vid):
        return output_vid
    else:
        return None

async def take_screen_shot(video_file, output_directory, ttl):
    # https://stackoverflow.com/a/13891070/4723940
    out_put_file_name = output_directory + \
        "/" + str(time.time()) + ".jpg"
    file_genertor_command = [
        "ffmpeg",
        "-ss",
        str(ttl),
        "-i",
        video_file,
        "-vframes",
        "1",
        out_put_file_name
    ]
    # width = "90"
    process = await asyncio.create_subprocess_exec(
        *file_genertor_command,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    if os.path.lexists(out_put_file_name):
        return out_put_file_name
    else:
        return None
