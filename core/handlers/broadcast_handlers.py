# (c) @AbirHasan2005 | Updated by GPT-5 (2025)
# Modern async broadcast handler for Pyrogram 2.x

import os
import time
import string
import random
import asyncio
import datetime
import aiofiles
import traceback
from typing import Tuple, Optional

from configs import Config
from core.handlers.main_db_handler import db
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import (
    FloodWait,
    InputUserDeactivated,
    UserIsBlocked,
    PeerIdInvalid,
    RPCError,
)

# Global state for active broadcasts
broadcast_ids = {}


# ────────────────────────────────
# ✉️ Message Sending Helper
# ────────────────────────────────
async def send_msg(user_id: int, message: Message) -> Tuple[int, Optional[str]]:
    """
    Send a broadcast message to a single user.
    Returns (status_code, error_message)
    """
    try:
        if Config.BROADCAST_AS_COPY:
            await message.copy(chat_id=user_id)
        else:
            await message.forward(chat_id=user_id)
        return 200, None

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except InputUserDeactivated:
        return 400, f"{user_id}: deactivated\n"
    except UserIsBlocked:
        return 400, f"{user_id}: blocked the bot\n"
    except PeerIdInvalid:
        return 400, f"{user_id}: invalid user ID\n"
    except RPCError as e:
        return 500, f"{user_id}: RPCError - {str(e)}\n"
    except Exception:
        return 500, f"{user_id}: {traceback.format_exc()}\n"


# ────────────────────────────────
# 📣 Broadcast Handler
# ────────────────────────────────
async def broadcast_handler(c: Client, m: Message):
    """
    Broadcast a replied message to all users asynchronously.
    Compatible with Pyrogram 2.x & Python 3.12+
    """
    broadcast_msg = m.reply_to_message
    if not broadcast_msg:
        return await m.reply_text("⚠️ Reply to a message to broadcast it.")

    # Generate unique broadcast ID
    while True:
        broadcast_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        if broadcast_id not in broadcast_ids:
            break

    start_time = time.time()
    total_users = await db.total_users_count()

    # Initialize broadcast state
    broadcast_ids[broadcast_id] = {
        "total": total_users,
        "current": 0,
        "failed": 0,
        "success": 0,
    }

    log_file = "broadcast_log.txt"
    out = await m.reply_text("📢 Broadcast started... Please wait!")

    success, failed, done = 0, 0, 0
    start_dt = datetime.datetime.now()

    async with aiofiles.open(log_file, "w") as log:
        async for user in db.get_all_users():
            if broadcast_id not in broadcast_ids:
                break

            sts, err = await send_msg(int(user["id"]), broadcast_msg)
            if err:
                await log.write(err)

            if sts == 200:
                success += 1
            else:
                failed += 1
                if sts == 400:
                    await db.delete_user(user["id"])

            done += 1
            broadcast_ids[broadcast_id].update(
                {"current": done, "failed": failed, "success": success}
            )

            # Update progress every 50 users
            if done % 50 == 0 or done == total_users:
                try:
                    await out.edit_text(
                        f"📤 **Broadcast Progress:**\n"
                        f"👥 Total: `{total_users}`\n"
                        f"✅ Success: `{success}`\n"
                        f"⚠️ Failed: `{failed}`\n"
                        f"📈 Done: `{done}`\n"
                        f"🕒 Elapsed: `{str(datetime.timedelta(seconds=int(time.time() - start_time)))}`"
                    )
                except Exception:
                    pass

            # Prevent hitting flood limits
            await asyncio.sleep(0.05)

    # Remove from active broadcasts
    broadcast_ids.pop(broadcast_id, None)
    duration = datetime.timedelta(seconds=int(time.time() - start_time))

    await out.delete()
    summary = (
        f"✅ **Broadcast Completed**\n\n"
        f"🕒 Duration: `{duration}`\n"
        f"👥 Total: `{total_users}`\n"
        f"✅ Success: `{success}`\n"
        f"⚠️ Failed: `{failed}`"
    )

    # Send summary with log file (if any errors)
    if failed > 0:
        await m.reply_document(
            document=log_file,
            caption=summary,
            quote=True,
        )
    else:
        await m.reply_text(summary, quote=True)

    if os.path.exists(log_file):
        os.remove(log_file)
