from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()

TOP_K = 3


class SearchRequest(BaseModel):
    question: str


def _retrieve(question: str):
    from retrieval.retriever import search_question

    return search_question(question=question, top_k=TOP_K)


@router.post("/search/answer")
def search_answer(request: SearchRequest):
    from src.services.groq_services import generate_answer

    retrieved_results = _retrieve(request.question)

    answer = generate_answer(
        user_question=request.question,
        retrieved_results=retrieved_results,
    )

    return {
        "question": request.question,
        "answer": answer,
    }


@router.post("/search/results")
def search_results(request: SearchRequest):
    retrieved_results = _retrieve(request.question)

    return {
        "question": request.question,
        "retrieved_results": retrieved_results,
    }
