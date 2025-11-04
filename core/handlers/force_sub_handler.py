# (c) @AbirHasan2005 | Updated by GPT-5 (2025)
# Modern Force Subscription Handler for Pyrogram 2.x

import asyncio
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait, UserNotParticipant, ChatAdminRequired, RPCError
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from configs import Config

logger = logging.getLogger(__name__)


async def handle_force_subscribe(bot: Client, cmd):
    """
    Ensures the user is subscribed to the updates channel before using the bot.
    Works with both public and private channels.
    """

    if not Config.UPDATES_CHANNEL:
        return 200  # No restriction if channel not set

    channel_id = str(Config.UPDATES_CHANNEL)
    if channel_id.startswith("@"):
        channel_ref = channel_id
    else:
        try:
            channel_ref = int(channel_id)
        except ValueError:
            channel_ref = channel_id

    # Try to get or create an invite link for private channels
    try:
        invite_link = await bot.create_chat_invite_link(channel_ref)
        invite_url = invite_link.invite_link
    except ChatAdminRequired:
        logger.warning("Bot is not admin in the updates channel. Cannot enforce join.")
        return 200
    except FloodWait as e:
        logger.warning(f"FloodWait while generating invite link: {e.value}s")
        await asyncio.sleep(e.value)
        return 400
    except Exception as e:
        logger.error(f"Unexpected error while creating invite link: {e}")
        return 400

    # Check user membership
    try:
        user = await bot.get_chat_member(channel_ref, cmd.from_user.id)

        if user.status == "kicked":
            await bot.send_message(
                chat_id=cmd.from_user.id,
                text=(
                    "🚫 **Access Denied!**\n"
                    "You have been *banned* from using this bot.\n\n"
                    "If you think this is a mistake, contact support: [Support Group](https://t.me/Dads_links)"
                ),
                disable_web_page_preview=True
            )
            return 400

        # User is already a member or admin
        return 200

    except UserNotParticipant:
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text=(
                "**🔒 Access Restricted!**\n\n"
                "You must join our **Updates Channel** to use this bot.\n"
                "After joining, click **Refresh** below to continue."
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("📢 Join Updates Channel", url=invite_url)],
                    [InlineKeyboardButton("🔄 Refresh", callback_data="refreshmeh")]
                ]
            ),
            disable_web_page_preview=True
        )
        return 400

    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await handle_force_subscribe(bot, cmd)

    except RPCError as e:
        logger.error(f"RPCError while checking membership: {e}")
        return 400

    except Exception as e:
        logger.error(f"Unhandled error in force subscribe: {e}")
        await bot.send_message(
            chat_id=cmd.from_user.id,
            text=(
                "⚠️ **Something went wrong.**\n"
                "Please try again later or contact support: [Support Group](https://t.me/Dads_links)"
            ),
            disable_web_page_preview=True
        )
        return 400
