from pymongo import MongoClient
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.mongodb import MongoDBSaver
from app.core.config import settings
from app.core.logger_config import logger
from typing import Literal

async def setup_persistence() -> tuple[Literal["MongoDBSaver", "MemorySaver"], MemorySaver | MongoDBSaver]:
    try:
        host = settings.mongodb_uri
        mongodb_client = MongoClient(host)
        mongodb_client.server_info()  # Check if the connection is successful
        checkpointer_type, checkpointer = "MongoDBSaver", MongoDBSaver(mongodb_client, ttl=settings.mongodb_ttl_seconds)
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        logger.info("Falling back to MemorySaver")
        checkpointer_type, checkpointer = "MemorySaver", MemorySaver()
    return checkpointer_type, checkpointer