import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
CONVERSATIONS_COLLECTION_NAME = os.getenv(
    "MONGO_CONVERSATIONS_COLLECTION",
    "conversations",
)


client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
conversations_collection = db[CONVERSATIONS_COLLECTION_NAME]


def check_connection() -> bool:
    """
    Ping the configured MongoDB server to verify connectivity.

    Returns True and prints the server version on success,
    or False and the error type on failure. Never prints the
    connection URI, since it may contain credentials.
    """

    try:
        client.admin.command("ping")
        server_info = client.server_info()
        print(f"MongoDB connection OK (version {server_info['version']})")
        return True

    except Exception as error:
        print(f"MongoDB connection FAILED: {type(error).__name__}")
        return False
