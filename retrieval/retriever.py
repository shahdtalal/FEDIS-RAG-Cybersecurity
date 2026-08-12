import os
import threading

import chromadb
from dotenv import load_dotenv

load_dotenv()


CHROMA_DB_PATH = os.getenv(
    "CHROMA_DB_PATH",
    "./chroma_db"
)

COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "cybersecurity_qa"
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-large-en-v1.5"
)


_model = None
_collection = None
_query_cache = {}
_ready = False
_loading = False
_load_lock = threading.Lock()


def is_ready() -> bool:
    return _ready


def start_warmup() -> str:
    global _loading

    if _ready:
        return "ready"

    with _load_lock:
        if _ready:
            return "ready"
        if _loading:
            return "loading"

        _loading = True
        threading.Thread(
            target=_load_resources,
            daemon=True,
        ).start()
        return "loading"


def _load_resources():
    global _model, _collection, _ready, _loading

    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_collection(name=COLLECTION_NAME)

        with _load_lock:
            _model = model
            _collection = collection
            _ready = True
    finally:
        with _load_lock:
            _loading = False


def _get_resources():
    if _ready:
        return _model, _collection

    start_warmup()

    with _load_lock:
        if _ready:
            return _model, _collection

    _load_resources()
    return _model, _collection


def search_question(
    question: str,
    top_k: int = 3,
):
    if not question or not question.strip():
        return []

    cache_key = (question.strip().lower(), top_k)
    if cache_key in _query_cache:
        return _query_cache[cache_key]

    model, collection = _get_resources()

    query_embedding = model.encode(
        [question],
        convert_to_numpy=True,
    )

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k,
        include=[
            "metadatas",
            "documents",
            "distances",
        ],
    )

    if not results["ids"] or not results["ids"][0]:
        return []

    matches = []

    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]

        matches.append(
            {
                "id": metadata["id"],
                "question": metadata["question"],
                "answer": metadata["answer"],
                "distance": results["distances"][0][i],
            }
        )

    _query_cache[cache_key] = matches
    return matches
