from fastapi import APIRouter, HTTPException, Request, Response

from src.db.history_service import (
    create_conversation,
    close_conversation,
)
from src.db.mongo_connection_test import check_mongo


router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"],
)


def _ensure_mongo():
    mongo_status = check_mongo()
    if mongo_status["status"] != "ok":
        raise HTTPException(
            status_code=503,
            detail=mongo_status["message"],
        )


@router.post("/new")
def new_conversation(
    request: Request,
    response: Response,
):
    _ensure_mongo()

    try:
        old_conversation_id = request.cookies.get("conversation_id")

        if old_conversation_id:
            close_conversation(old_conversation_id)

        new_conversation_id = create_conversation()

        response.set_cookie(
            key="conversation_id",
            value=new_conversation_id,
            httponly=True,
            samesite="lax",
        )

        return {
            "message": "New conversation created",
            "status": "active",
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Could not start chat: {error}",
        ) from error


@router.post("/end")
def end_conversation(
    request: Request,
    response: Response,
):
    _ensure_mongo()

    try:
        conversation_id = request.cookies.get("conversation_id")

        if conversation_id:
            close_conversation(conversation_id)

        response.delete_cookie("conversation_id")

        return {
            "message": "Conversation ended",
            "status": "closed",
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail=f"Could not end chat: {error}",
        ) from error
