from motor.motor_asyncio import AsyncIOMotorClient
import os, certifi
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

@asynccontextmanager
async def get_db():
    """Yield a fresh db client bound to the current event‑loop."""
    client = AsyncIOMotorClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5_000,
    )
    try:
        yield client["skillforge_database"]
    finally:
        client.close()
