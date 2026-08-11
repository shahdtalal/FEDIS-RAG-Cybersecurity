# from datetime import datetime, timezone

# from src.db.mongo_connection_test import conversations_collection


# def create_conversation(conversation_id: str) -> None:
#     """
#     Create a new active conversation.
#     """

#     now = datetime.now(timezone.utc)

#     conversations_collection.insert_one(
#         {
#             "conversation_id": conversation_id,
#             "created_at": now,
#             "updated_at": now,
#             "status": "active",
#             "messages": [],
#         }
#     )


# def get_conversation(conversation_id: str):
#     """
#     Get a conversation by its ID.
#     """

#     return conversations_collection.find_one(
#         {
#             "conversation_id": conversation_id
#         }
#     )


# def get_messages(conversation_id: str) -> list[dict]:
#     """
#     Return the stored messages for a conversation.
#     """

#     conversation = get_conversation(conversation_id)

#     if not conversation:
#         return []

#     return conversation.get("messages", [])


# def build_chat_history(conversation_id: str) -> list[dict]:
#     """
#     Convert stored messages into the format expected by Groq.
#     """

#     chat_history = []

#     for message in get_messages(conversation_id):

#         chat_history.append(
#             {
#                 "role": "user",
#                 "content": message["question"],
#             }
#         )

#         chat_history.append(
#             {
#                 "role": "assistant",
#                 "content": message["answer"],
#             }
#         )

#     return chat_history


# def save_message(
#     conversation_id: str,
#     question: str,
#     answer: str,
#     retrieved_documents: list[dict],
# ) -> None:
#     """
#     Append a question/answer exchange to an active conversation.

#     If the conversation does not exist, it is created automatically.
#     """

#     now = datetime.now(timezone.utc)

#     conversations_collection.update_one(
#         {
#             "conversation_id": conversation_id,
#             "status": "active",
#         },
#         {
#             "$setOnInsert": {
#                 "conversation_id": conversation_id,
#                 "created_at": now,
#                 "status": "active",
#             },
#             "$set": {
#                 "updated_at": now,
#             },
#             "$push": {
#                 "messages": {
#                     "question": question,
#                     "answer": answer,
#                     "retrieved_documents": retrieved_documents,
#                     "timestamp": now,
#                 }
#             },
#         },
#         upsert=True,
#     )


# def close_conversation(conversation_id: str) -> bool:
#     """
#     Mark a conversation as closed.
#     """

#     result = conversations_collection.update_one(
#         {
#             "conversation_id": conversation_id,
#             "status": "active",
#         },
#         {
#             "$set": {
#                 "status": "closed",
#                 "updated_at": datetime.now(timezone.utc),
#             }
#         },
#     )

#     return result.modified_count > 0












import uuid
from datetime import datetime, timezone

from src.db.mongo_connection_test import conversations_collection


def create_conversation() -> str:
    """
    Create a new conversation and return its generated ID.
    """

    conversation_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    conversations_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "messages": [],
        }
    )

    return conversation_id


def get_conversation(conversation_id: str):
    return conversations_collection.find_one(
        {"conversation_id": conversation_id}
    )


def get_or_create_conversation(
    conversation_id: str | None,
) -> str:
    """
    Determine which conversation the message belongs to.

    - No ID → create a new conversation.
    - Existing active ID → continue it.
    - Existing closed ID → create a new conversation.
    """

    # No conversation ID was supplied.
    if not conversation_id:
        return create_conversation()

    conversation = get_conversation(conversation_id)

    # ID doesn't exist in MongoDB.
    if not conversation:
        return create_conversation()

    # Existing conversation is active.
    if conversation["status"] == "active":
        return conversation_id

    # Existing conversation is closed.
    return create_conversation()


def build_chat_history(conversation_id: str) -> list[dict]:

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


def close_conversation(conversation_id: str) -> bool:

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