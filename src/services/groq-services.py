import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

client = Groq(api_key=GROQ_API_KEY)


# Models are ordered by priority.
# If the primary model fails because of a retryable
# limit/error, the next model can be attempted.
MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]


SYSTEM_PROMPT = """
You are a helpful cybersecurity tutor.

Your job is to help the user understand cybersecurity questions
and concepts clearly.

When a verified answer from the application's dataset is provided,
treat that answer as the ground-truth answer.

Do not replace the verified answer with a different answer.

Explain why the verified answer is correct in a clear and
student-friendly way.

If the user asks a follow-up question, use the conversation
context to answer it naturally.

If the retrieved information does not contain a verified answer,
answer the user's question using your general knowledge while
clearly avoiding unsupported claims.
"""


def generate_answer(
    user_question: str,
    retrieved_question: str | None = None,
    correct_answer: str | None = None,
    conversation_history: list | None = None,
) -> str:

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    # Add previous conversation if it exists
    if conversation_history:
        messages.extend(conversation_history)

    # Build the current user message
    if retrieved_question and correct_answer:

        user_message = f"""
The user asked:

{user_question}

A relevant question was found in our verified dataset:

{retrieved_question}

The verified correct answer from the dataset is:

{correct_answer}

Explain this answer to the user.

Make the explanation clear and educational.
"""

    else:

        user_message = f"""
The user asked:

{user_question}

No verified answer for this question was found
in our dataset.

Answer the user's question using your knowledge.
"""

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    # Try the models in order
    for model in MODELS:

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
            )

            return response.choices[0].message.content

        except Exception as error:

            print(f"Model {model} failed: {error}")

            # Try the next model
            continue

    raise RuntimeError(
        "All configured Groq models failed."
    )