import uuid
from datetime import datetime, timezone

from src.db.mongo_connection_test import conversations_collection


def create_conversation() -> str:
    """Create a new active conversation."""

    conversation_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    conversations_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "messages": [],
        }
    )

    return conversation_id


def get_conversation(conversation_id: str):
    """Get a conversation by ID."""

    return conversations_collection.find_one(
        {"conversation_id": conversation_id}
    )


def close_conversation(conversation_id: str) -> bool:
    """Mark an active conversation as closed."""

    result = conversations_collection.update_one(
        {
            "conversation_id": conversation_id,
            "status": "active",
        },
        {
            "$set": {
                "status": "closed",
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return result.modified_count > 0


def build_chat_history(conversation_id: str) -> list[dict]:
    """Build history in Groq's role/content format."""

    conversation = get_conversation(conversation_id)

    if not conversation:
        return []

    history = []

    for message in conversation.get("messages", []):

        history.append(
            {
                "role": "user",
                "content": message["question"],
            }
        )

        history.append(
            {
                "role": "assistant",
                "content": message["answer"],
            }
        )

    return history


def save_message(
    conversation_id: str,
    question: str,
    answer: str,
    retrieved_documents: list[dict],
) -> None:
    """Save a question/answer exchange."""

    now = datetime.now(timezone.utc)

    conversations_collection.update_one(
        {
            "conversation_id": conversation_id,
            "status": "active",
        },
        {
            "$set": {
                "updated_at": now,
            },
            "$push": {
                "messages": {
                    "question": question,
                    "answer": answer,
                    "retrieved_documents": retrieved_documents,
                    "timestamp": now,
                }
            },
        },
    )