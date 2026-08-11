# import uuid

# from fastapi import APIRouter
# from pydantic import BaseModel

# from src.db.history_service import (
#     build_chat_history,
#     save_message,
#     get_conversation,
# )
# from retrieval.retriever import search_question
# from src.services.groq_services import generate_answer


# router = APIRouter(
#     tags=["Search"],
# )


# class SearchRequest(BaseModel):
#     question: str
#     conversation_id: str | None = None


# @router.post("/search")
# def search(request: SearchRequest):

#     # --------------------------------------------------
#     # 1. Determine the conversation
#     # --------------------------------------------------

#     if request.conversation_id:

#         conversation_id = request.conversation_id

#         conversation = get_conversation(
#             conversation_id
#         )

#         # Conversation doesn't exist
#         if not conversation:
#             conversation_id = str(uuid.uuid4())

#         # Conversation was closed
#         elif conversation.get("status") == "closed":
#             conversation_id = str(uuid.uuid4())

#     else:

#         # No conversation ID means this is a new conversation
#         conversation_id = str(uuid.uuid4())

#     # --------------------------------------------------
#     # 2. Retrieve previous conversation history
#     # --------------------------------------------------

#     conversation_history = build_chat_history(
#         conversation_id
#     )

#     # --------------------------------------------------
#     # 3. Retrieve top 3 ChromaDB results
#     # --------------------------------------------------

#     retrieved_results = search_question(
#         question=request.question,
#         top_k=3,
#     )

#     # --------------------------------------------------
#     # 4. Send question + retrieval + history to Groq
#     # --------------------------------------------------

#     answer = generate_answer(
#         user_question=request.question,
#         retrieved_results=retrieved_results,
#         conversation_history=conversation_history,
#     )

#     # --------------------------------------------------
#     # 5. Save exchange to MongoDB
#     # --------------------------------------------------

#     save_message(
#         conversation_id=conversation_id,
#         question=request.question,
#         answer=answer,
#         retrieved_documents=retrieved_results,
#     )

#     # --------------------------------------------------
#     # 6. Return response
#     # --------------------------------------------------

#     return {
#         "conversation_id": conversation_id,
#         "question": request.question,
#         "answer": answer,
#         "retrieved_results": retrieved_results,
#     }













from fastapi import APIRouter
from pydantic import BaseModel

from retrieval.retriever import search_question

from src.db.history_service import (
    get_or_create_conversation,
    build_chat_history,
    save_message,
)

from src.services.groq_services import generate_answer


router = APIRouter(
    tags=["Search"]
)


class SearchRequest(BaseModel):
    question: str
    conversation_id: str | None = None


@router.post("/search")
def search(request: SearchRequest):

    # ---------------------------------------
    # 1. Get existing conversation OR create
    #    a new one automatically
    # ---------------------------------------

    conversation_id = get_or_create_conversation(
        request.conversation_id
    )

    # ---------------------------------------
    # 2. Get previous conversation history
    # ---------------------------------------

    conversation_history = build_chat_history(
        conversation_id
    )

    # ---------------------------------------
    # 3. Retrieve top 3 ChromaDB results
    # ---------------------------------------

    retrieved_results = search_question(
        question=request.question,
        top_k=3,
    )

    # ---------------------------------------
    # 4. Generate answer with Groq
    # ---------------------------------------

    answer = generate_answer(
        user_question=request.question,
        retrieved_results=retrieved_results,
        conversation_history=conversation_history,
    )

    # ---------------------------------------
    # 5. Store message in MongoDB
    # ---------------------------------------

    save_message(
        conversation_id=conversation_id,
        question=request.question,
        answer=answer,
        retrieved_documents=retrieved_results,
    )

    # ---------------------------------------
    # 6. Return response
    # ---------------------------------------

    return {
        "conversation_id": conversation_id,
        "question": request.question,
        "answer": answer,
        "retrieved_results": retrieved_results,
    }