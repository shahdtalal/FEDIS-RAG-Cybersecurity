import os

import chromadb
from dotenv import load_dotenv
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from groq import Groq

from src.db.mongo_connection_test import check_mongo

load_dotenv()

router = APIRouter()

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "cybersecurity_qa")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def check_chroma() -> dict:
    try:
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_collection(name=COLLECTION_NAME)
        return {
            "status": "ok",
            "collection": COLLECTION_NAME,
            "document_count": collection.count(),
        }
    except Exception as error:
        return {"status": "error", "message": str(error)}


def check_groq() -> dict:
    if not GROQ_API_KEY:
        return {"status": "error", "message": "GROQ_API_KEY is not set"}

    try:
        client = Groq(api_key=GROQ_API_KEY)
        client.models.list()
        return {"status": "ok"}
    except Exception as error:
        return {"status": "error", "message": str(error)}


@router.get("/health")
def health():
    chroma_status = check_chroma()
    groq_status = check_groq()
    mongo_status = check_mongo()

    all_ok = (
        chroma_status["status"] == "ok"
        and groq_status["status"] == "ok"
        and mongo_status["status"] == "ok"
    )

    payload = {
        "status": "ok" if all_ok else "degraded",
        "services": {
            "chroma": chroma_status,
            "groq": groq_status,
            "mongo": mongo_status,
        },
    }

    status_code = 200 if all_ok else 503
    return JSONResponse(content=payload, status_code=status_code)


@router.get("/warmup")
def warmup():
    from retrieval.retriever import is_ready, start_warmup

    status = start_warmup()

    if status == "ready" or is_ready():
        return {"status": "ready", "message": "Embedding model loaded"}

    return {
        "status": "loading",
        "message": "Embedding model is loading in background",
    }
