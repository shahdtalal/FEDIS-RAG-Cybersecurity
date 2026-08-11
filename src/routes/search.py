import uuid

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class SearchRequest(BaseModel):
    question: str
    conversation_id: str | None = None


@router.post("/search")
def search(request: SearchRequest):
    from retrieval.retriever import search_question
    from src.db.history_service import build_chat_history, save_message
    from src.services.groq_services import generate_answer

    conversation_id = request.conversation_id or str(uuid.uuid4())

    conversation_history = build_chat_history(conversation_id)

    retrieved_results = search_question(
        question=request.question,
        top_k=3,
    )

    answer = generate_answer(
        user_question=request.question,
        retrieved_results=retrieved_results,
        conversation_history=conversation_history,
    )

    save_message(
        conversation_id=conversation_id,
        question=request.question,
        answer=answer,
        retrieved_documents=retrieved_results,
    )

    return {
        "conversation_id": conversation_id,
        "question": request.question,
        "answer": answer,
        "retrieved_results": retrieved_results,
    }
