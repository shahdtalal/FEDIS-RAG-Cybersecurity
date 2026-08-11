import os

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


def _get_resources():
    global _model, _collection

    if _collection is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(EMBEDDING_MODEL)
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        _collection = client.get_collection(name=COLLECTION_NAME)

    return _model, _collection


def search_question(
    question: str,
    top_k: int = 3,
):
    """
    Search ChromaDB for the top-k most similar
    question + answer records.

    Returns:
        A list containing the top matching records.
    """

    if not question or not question.strip():
        return []

    model, collection = _get_resources()

    # Generate an embedding for the user's question
    # using the same model used during ingestion.
    query_embedding = model.encode(
        [question],
        convert_to_numpy=True,
    )

    # Perform similarity search in ChromaDB.
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

    return matches
