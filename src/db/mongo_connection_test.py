import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


MONGO_URI = (
    os.getenv("MONGO_URI")
    or os.getenv("MONGODB_URI")
    or "mongodb://localhost:27017"
)
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME") or os.getenv("MONGODB_DB_NAME") or "fedis_rag"
CONVERSATIONS_COLLECTION_NAME = os.getenv(
    "MONGO_CONVERSATIONS_COLLECTION",
    "conversations",
)

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=5000,
)
db = client[MONGO_DB_NAME]
conversations_collection = db[CONVERSATIONS_COLLECTION_NAME]


def check_mongo() -> dict:
    try:
        client.admin.command("ping")
        return {"status": "ok"}
    except Exception as error:
        return {
            "status": "error",
            "message": f"MongoDB unavailable — is it running? ({type(error).__name__})",
        }


def check_connection() -> bool:
    return check_mongo()["status"] == "ok"
