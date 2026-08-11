from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

from retrieval.retriever import search_question

from src.db.history_service import (
    create_conversation,
    get_conversation,
    build_chat_history,
    save_message,
)

from src.services.groq_services import generate_answer


router = APIRouter(
    tags=["Search"]
)


class SearchRequest(BaseModel):
    question: str


@router.post("/search")
def search(
    request: Request,
    response: Response,
    body: SearchRequest,
):

    # ---------------------------------------
    # 1. Get conversation ID from cookie
    # ---------------------------------------

    conversation_id = request.cookies.get(
        "conversation_id"
    )

    # ---------------------------------------
    # 2. No cookie → create conversation
    # ---------------------------------------

    if not conversation_id:

        conversation_id = create_conversation()

        response.set_cookie(
            key="conversation_id",
            value=conversation_id,
            httponly=True,
            samesite="lax",
        )

    else:

        # ---------------------------------------
        # 3. Find conversation in MongoDB
        # ---------------------------------------

        conversation = get_conversation(
            conversation_id
        )

        # Conversation doesn't exist
        if not conversation:

            conversation_id = create_conversation()

            response.set_cookie(
                key="conversation_id",
                value=conversation_id,
                httponly=True,
                samesite="lax",
            )

        # Conversation exists but is closed
        elif conversation["status"] == "closed":

            conversation_id = create_conversation()

            response.set_cookie(
                key="conversation_id",
                value=conversation_id,
                httponly=True,
                samesite="lax",
            )

        # If active → do nothing.
        # We keep the same conversation ID.

    # ---------------------------------------
    # 4. Load conversation history
    # ---------------------------------------

    conversation_history = build_chat_history(
        conversation_id
    )

    # ---------------------------------------
    # 5. Retrieve top 3 ChromaDB results
    # ---------------------------------------

    retrieved_results = search_question(
        question=body.question,
        top_k=3,
    )

    # ---------------------------------------
    # 6. Ask Groq
    # ---------------------------------------

    answer = generate_answer(
        user_question=body.question,
        retrieved_results=retrieved_results,
        conversation_history=conversation_history,
    )

    # ---------------------------------------
    # 7. Save everything to MongoDB
    # ---------------------------------------

    save_message(
        conversation_id=conversation_id,
        question=body.question,
        answer=answer,
        retrieved_documents=retrieved_results,
    )

    # ---------------------------------------
    # 8. Return answer
    # ---------------------------------------

    return {
        "question": body.question,
        "answer": answer,
        "retrieved_results": retrieved_results,
    }