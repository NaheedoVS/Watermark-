# (c) @AbirHasan2005 | Updated by GPT-5 (2025)
# Modern async MongoDB handler for Telegram Video Watermark Adder Bot

import datetime
import logging
from typing import Optional, AsyncIterator

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING

logger = logging.getLogger(__name__)


class Database:
    """Asynchronous MongoDB database manager using Motor (v3.6+)."""

    def __init__(self, uri: str, database_name: str = "watermark_bot"):
        try:
            self._client = AsyncIOMotorClient(
                uri,
                maxPoolSize=10,
                minPoolSize=1,
                connectTimeoutMS=10000,
                serverSelectionTimeoutMS=5000,
            )
            self.db = self._client[database_name]
            self.col = self.db.users
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise

    async def init_indexes(self):
        """Ensure indexes for faster user lookup."""
        try:
            await self.col.create_index([("id", ASCENDING)], unique=True)
            logger.info("✅ MongoDB indexes ensured.")
        except Exception as e:
            logger.error(f"⚠️ Failed to create indexes: {e}")

    # ────────────────────────────────
    # 👤 User Management
    # ────────────────────────────────
    @staticmethod
    def new_user(user_id: int) -> dict:
        """Return a new user document."""
        return {
            "id": int(user_id),
            "join_date": datetime.date.today().isoformat(),
            "watermark_position": "5:5",
            "watermark_size": "7"
        }

    async def add_user(self, user_id: int) -> bool:
        """Add a new user if not already exists."""
        try:
            if not await self.is_user_exist(user_id):
                await self.col.insert_one(self.new_user(user_id))
                logger.info(f"👤 Added new user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error adding user {user_id}: {e}")
            return False

    async def is_user_exist(self, user_id: int) -> bool:
        """Check if user exists in database."""
        return bool(await self.col.find_one({"id": int(user_id)}, {"_id": 1}))

    async def total_users_count(self) -> int:
        """Return total number of users."""
        return await self.col.count_documents({})

    async def get_all_users(self) -> AsyncIterator[dict]:
        """Asynchronous generator for all users."""
        async for user in self.col.find({}, {"_id": 0}):
            yield user

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user by ID."""
        result = await self.col.delete_many({"id": int(user_id)})
        return result.deleted_count > 0

    # ────────────────────────────────
    # ⚙️ User Settings
    # ────────────────────────────────
    async def set_position(self, user_id: int, position: str) -> None:
        await self.col.update_one(
            {"id": int(user_id)},
            {"$set": {"watermark_position": position}},
            upsert=True
        )

    async def get_position(self, user_id: int) -> str:
        user = await self.col.find_one({"id": int(user_id)}, {"watermark_position": 1})
        return user.get("watermark_position", "5:5") if user else "5:5"

    async def set_size(self, user_id: int, size: str) -> None:
        await self.col.update_one(
            {"id": int(user_id)},
            {"$set": {"watermark_size": size}},
            upsert=True
        )

    async def get_size(self, user_id: int) -> str:
        user = await self.col.find_one({"id": int(user_id)}, {"watermark_size": 1})
        return user.get("watermark_size", "7") if user else "7"

    # ────────────────────────────────
    # 🔒 Connection Management
    # ────────────────────────────────
    async def close(self):
        """Gracefully close the MongoDB connection."""
        self._client.close()
        logger.info("🔌 MongoDB connection closed.")
