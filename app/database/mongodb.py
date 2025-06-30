from fastapi import FastAPI
from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient
import certifi, os, time, logging
from dotenv import load_dotenv

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not found in env")

@lru_cache()
def get_mongo_client():
    client = AsyncIOMotorClient(
        MONGO_URI,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5_000,
    )
    # Ping once so we fail fast if URI/IP is wrong
    for _ in range(2):
        try:
            client.admin.command("ping")
            break
        except Exception as e:
            logging.error("Mongo ping failed: %s", e)
            time.sleep(2)
    return client

client = get_mongo_client()
db = client["skillforge_database"]
