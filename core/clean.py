# (c) @AbirHasan2005 | Updated by GPT-5 (2025)
# Modern cleanup utilities for Telegram Video Watermark Bot

import os
import shutil
import asyncio
from pathlib import Path
from configs import Config


async def delete_trash(file_path: str):
    """
    Safely delete a single file or folder asynchronously.
    Logs errors instead of failing silently.
    """
    try:
        path = Path(file_path)
        if path.exists():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            print(f"🗑️ Deleted: {path}")
        else:
            print(f"⚠️ Skipped: {path} (not found)")
    except Exception as e:
        print(f"❌ Error deleting {file_path}: {e}")


async def delete_all():
    """
    Deletes all temporary download and watermark data safely.
    """
    try:
        root_dir = Path(Config.DOWN_PATH) / "WatermarkAdder"
        if root_dir.exists():
            shutil.rmtree(root_dir)
            print(f"✅ Cleaned: {root_dir}")
        else:
            print(f"⚠️ Nothing to clean: {root_dir}")
    except Exception as e:
        print(f"❌ Error cleaning {root_dir}: {e}")


async def scheduled_cleanup(interval: int = 3600):
    """
    Optional background cleanup coroutine.
    Periodically clears temporary folders every X seconds (default 1 hour).
    """
    while True:
        await asyncio.sleep(interval)
        await delete_all()
