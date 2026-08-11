from fastapi import APIRouter, Request, Response

from src.db.history_service import (
    create_conversation,
    close_conversation,
)


router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"],
)


@router.post("/new")
def new_conversation(
    request: Request,
    response: Response,
):
    """
    Close the current conversation, if one exists,
    then create a new conversation.
    """

    old_conversation_id = request.cookies.get(
        "conversation_id"
    )

    # Close the old conversation
    if old_conversation_id:
        close_conversation(old_conversation_id)

    # Create a new conversation
    new_conversation_id = create_conversation()

    # Store the new ID in the browser cookie
    response.set_cookie(
        key="conversation_id",
        value=new_conversation_id,
        httponly=True,
        samesite="lax",
    )

    return {
        "message": "New conversation created",
    }


@router.post("/end")
def end_conversation(
    request: Request,
    response: Response,
):
    """
    Close the current conversation, if one exists,
    and clear the conversation cookie.
    """

    conversation_id = request.cookies.get(
        "conversation_id"
    )

    if conversation_id:
        close_conversation(conversation_id)

    response.delete_cookie("conversation_id")

    return {
        "message": "Conversation ended",
    }