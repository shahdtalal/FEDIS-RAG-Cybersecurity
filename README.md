# FEDIS-RAG-Cybersecurity

FastAPI RAG API for cybersecurity Q&A using ChromaDB and Groq.

## Setup

1. Clone the repository and create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

2. Copy the environment file and add your Groq API key:

```bash
copy .env.example .env
```

3. Run the API:

```bash
uvicorn src.main:app --reload
```

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API status |
| `/health` | GET | Check ChromaDB and Groq connections |
| `/search` | POST | Search the dataset and generate an answer |
| `/docs` | GET | Swagger UI |

## Notes for teammates

- **Do not commit `.env`** — it contains your API key. Use `.env.example` as a template.
- **`/health` and `/docs` do not download the embedding model.** The Hugging Face model is only loaded when you call `/search`.
- **`chroma_db/`** is included in the repo so everyone can run the API without rebuilding the vector database.
- To download the embedding model separately (optional), run `python scripts/download_embedding_model.py`.
