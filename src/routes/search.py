from fastapi import APIRouter
from pydantic import BaseModel

from retrieval.retriever import search_question
from src.services.groq_services import generate_answer


router = APIRouter()


class SearchRequest(BaseModel):
    question: str


@router.post("/search")
def search(request: SearchRequest):

    retrieved_results = search_question(
        question=request.question,
        top_k=3,
    )

    answer = generate_answer(
        user_question=request.question,
        retrieved_results=retrieved_results,
    )

    return {
        "question": request.question,
        "answer": answer,
        "retrieved_results": retrieved_results,
    }