from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
import os
from dotenv import load_dotenv

load_dotenv()  # Local dev only – Vercel uses env panel

@lru_cache()
def get_mongo_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(
        os.environ["MONGO_URI"],  # Set this in Vercel → Settings
        tlsCAFile=certifi.where(),  # Atlas certs – avoids x509 issues
        serverSelectionTimeoutMS=5_000,  # Fail fast instead of hanging
    )

client = get_mongo_client()
db = client["skillforge_database"]