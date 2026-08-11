from datetime import datetime, timezone

from src.db.mongo_client import conversations_collection


def get_messages(conversation_id: str) -> list[dict]:
    """
    Return the stored messages for a conversation,
    or an empty list if the conversation does not exist yet.
    """

    conversation = conversations_collection.find_one(
        {"conversation_id": conversation_id}
    )

    return conversation["messages"] if conversation else []


def build_chat_history(conversation_id: str) -> list[dict]:
    """
    Convert the stored question/answer messages into the
    role/content format expected by generate_answer.
    """

    chat_history = []

    for message in get_messages(conversation_id):
        chat_history.append(
            {"role": "user", "content": message["question"]}
        )
        chat_history.append(
            {"role": "assistant", "content": message["answer"]}
        )

    return chat_history


def save_message(
    conversation_id: str,
    question: str,
    answer: str,
    retrieved_documents: list[dict],
) -> None:
    """
    Append a question/answer exchange to the conversation,
    creating the conversation document if it does not exist yet.
    """

    now = datetime.now(timezone.utc)

    conversations_collection.update_one(
        {"conversation_id": conversation_id},
        {
            "$setOnInsert": {
                "conversation_id": conversation_id,
                "created_at": now,
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
        upsert=True,
    )
