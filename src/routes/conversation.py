import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.db.history_service import (
    create_conversation,
    close_conversation,
    get_conversation,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


class ConversationResponse(BaseModel):
    conversation_id: str
    status: str


@router.post("", response_model=ConversationResponse)
def start_conversation():

    conversation_id = str(uuid.uuid4())

    create_conversation(conversation_id)

    return {
        "conversation_id": conversation_id,
        "status": "active",
    }


@router.post(
    "/{conversation_id}/close",
    response_model=ConversationResponse,
)
def close_chat(conversation_id: str):

    conversation = get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    if conversation.get("status") == "closed":
        return {
            "conversation_id": conversation_id,
            "status": "closed",
        }

    closed = close_conversation(conversation_id)

    if not closed:
        raise HTTPException(
            status_code=500,
            detail="Failed to close conversation.",
        )

    return {
        "conversation_id": conversation_id,
        "status": "closed",
    }