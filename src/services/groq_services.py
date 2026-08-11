import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

_client = None


def _get_client() -> Groq:
    global _client

    if _client is None:

        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set in the environment variables."
            )

        _client = Groq(
            api_key=GROQ_API_KEY
        )

    return _client


# Models are ordered by priority.
# If the first model fails, the next model is attempted.
MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]


SYSTEM_PROMPT = """
You are a helpful cybersecurity tutor.

Your job is to help the user understand cybersecurity questions
and concepts clearly.

The application retrieves up to three potentially relevant
question-and-answer pairs from a verified cybersecurity dataset.

When a retrieved result is relevant to the user's question,
treat its "Verified Answer" as the authoritative answer for
that specific question.

If one retrieved result directly answers the user's question,
use that verified answer as the ground-truth answer.

Do not change a verified dataset answer into a different answer.

You may explain the verified answer in your own words so that
the user can understand why it is correct.

If multiple retrieved results are relevant and consistent,
use them together to provide the clearest explanation.

If retrieved results contain conflicting answers, prefer the
result that most directly matches the user's question.

If none of the retrieved results actually answers the user's
question, answer using your general knowledge.

If the user asks a follow-up question, use the conversation
history to understand the context and answer naturally.

Do not mention the retrieval process, similarity distances,
ChromaDB, MongoDB, or other internal implementation details
to the user.
"""


def generate_answer(
    user_question: str,
    retrieved_results: list | None = None,
    conversation_history: list | None = None,
) -> str:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    # --------------------------------------------------
    # Add previous conversation history
    # --------------------------------------------------

    if conversation_history:
        messages.extend(
            conversation_history
        )

    # --------------------------------------------------
    # Build the current user message
    # --------------------------------------------------

    if retrieved_results:

        retrieved_context = ""

        for index, result in enumerate(
            retrieved_results,
            start=1,
        ):

            retrieved_context += f"""
Result {index}:

Question:
{result["question"]}

Verified Answer:
{result["answer"]}
"""

        user_message = f"""
The user asked:

{user_question}

Here are the top retrieved results from the verified
cybersecurity dataset:

{retrieved_context}

Determine which retrieved result or results are relevant
to the user's question.

If a retrieved result directly answers the question,
use its verified answer as the ground-truth answer.

Then provide a clear and educational explanation for the user.

If none of the retrieved results is relevant, answer the
question using your general knowledge.
"""

    else:

        user_message = f"""
The user asked:

{user_question}

No relevant verified answer was retrieved from the dataset.

Answer the user's question using your general knowledge
and provide a clear educational explanation.
"""

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # --------------------------------------------------
    # Get Groq client
    # --------------------------------------------------

    client = _get_client()

    # --------------------------------------------------
    # Try models in priority order
    # --------------------------------------------------

    for model in MODELS:

        try:

            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )

            return response.choices[0].message.content

        except Exception as error:

            print(
                f"Model {model} failed: {error}"
            )

            continue

    raise RuntimeError(
        "All configured Groq models failed."
    )