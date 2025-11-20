from __future__ import annotations

import os
from typing import Any, Optional
from pydantic_settings import BaseSettings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "appdb")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.database_url)
    return _client


def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        _db = get_client()[settings.database_name]
    return _db


async def create_document(collection_name: str, data: dict[str, Any]) -> str:
    db = get_db()
    result = await db[collection_name].insert_one({**data})
    return str(result.inserted_id)


async def get_documents(collection_name: str, filter_dict: dict[str, Any] | None = None, limit: int = 50) -> list[dict[str, Any]]:
    db = get_db()
    cursor = db[collection_name].find(filter_dict or {}).limit(limit)
    docs: list[dict[str, Any]] = []
    async for d in cursor:
        d["_id"] = str(d["_id"])  # stringify ObjectId for JSON safety
        docs.append(d)
    return docs
