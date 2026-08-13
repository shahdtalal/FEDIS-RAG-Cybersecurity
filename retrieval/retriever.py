import os

import chromadb
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()


CHROMA_DB_PATH = os.getenv(
    "CHROMA_DB_PATH",
    "./chroma_db",
)

COLLECTION_NAME = os.getenv(
    "CHROMA_COLLECTION_NAME",
    "cybersecurity_qa",
)

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-large-en-v1.5",
)


_model = None
_collection = None
_query_cache = {}


def start_warmup() -> str:
    """
    Load the embedding model and ChromaDB collection once.
    """

    global _model, _collection

    # Already loaded
    if _model is not None and _collection is not None:
        return "ready"

    print("Loading embedding model...")

    _model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    print("Embedding model loaded.")

    print("Connecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path=CHROMA_DB_PATH
    )

    _collection = client.get_collection(
        name=COLLECTION_NAME
    )

    print(
        f"ChromaDB collection '{COLLECTION_NAME}' loaded."
    )

    return "ready"


def is_ready() -> bool:
    """
    Return True when the embedding model and
    ChromaDB collection are ready.
    """

    return (
        _model is not None
        and _collection is not None
    )


def _get_resources():
    """
    Return the already-loaded model and collection.
    """

    if not is_ready():
        start_warmup()

    return _model, _collection


def search_question(
    question: str,
    top_k: int = 3,
):
    """
    Search ChromaDB for the top-k most similar
    cybersecurity Q&A records.
    """

    if not question or not question.strip():
        return []

    cache_key = (
        question.strip().lower(),
        top_k,
    )

    if cache_key in _query_cache:
        return _query_cache[cache_key]

    model, collection = _get_resources()

    # Generate embedding for the user's question
    query_embedding = model.encode(
        [question],
        convert_to_numpy=True,
    )

    # Search ChromaDB
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