# FEDIS-RAG-Cybersecurity (CYFEDIS)

CYFEDIS is a Retrieval-Augmented Generation (RAG) application for cybersecurity Q&A. It retrieves verified question–answer pairs from a vector database, generates answers with Groq, and saves chat history in MongoDB.

## What it does

1. **Retrieval** — Finds the top 3 most similar Q&A records from ChromaDB using embeddings.
2. **Generation** — Uses Groq (Llama) to produce a clear answer based on retrieved sources and chat history.
3. **Chat memory** — Stores conversations in MongoDB so follow-up questions keep context.

## Tech stack

| Component | Purpose |
|-----------|---------|
| **FastAPI** | Backend API and web server |
| **ChromaDB** | Vector database for cybersecurity Q&A |
| **Groq** | LLM for answer generation |
| **MongoDB Atlas** | Chat session and message history |
| **Sentence Transformers** | Embedding model (`BAAI/bge-large-en-v1.5`) |

## Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/)
- A [MongoDB Atlas](https://www.mongodb.com/atlas) cluster (free tier works)
- Git

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/shahdtalal/FEDIS-RAG-Cybersecurity.git
cd FEDIS-RAG-Cybersecurity
```

### 2. Create a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and fill in your values:

```bash
copy .env.example .env        # Windows
cp .env.example .env          # Linux / macOS
```

Edit `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here

MONGO_URI=mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=fedis_rag
MONGO_CONVERSATIONS_COLLECTION=conversations

CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=cybersecurity_qa
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
```

> **MongoDB Atlas setup:** In Atlas → Network Access, allow your IP (or `0.0.0.0/0` for testing). In Database Access, create a user and use those credentials in `MONGO_URI`.

> **Do not commit `.env`** — it contains secrets. Only `.env.example` belongs in git.

## How to run

Start the server from the project root:

```powershell
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

For development with auto-reload:

```powershell
uvicorn src.main:app --reload
```

Wait until you see:

```
Application startup complete.
```

The embedding model loads in the background on first startup (may take 1–2 minutes). Wait for **"Engine ready"** in the web UI header before sending your first question.

## Using the web app

Open in your browser:

| Page | URL |
|------|-----|
| **CYFEDIS frontend** | http://127.0.0.1:8000/ |
| **API docs (Swagger)** | http://127.0.0.1:8000/docs |
| **Health check** | http://127.0.0.1:8000/health |

### Chat flow

1. Click **Start Chat** — creates a new MongoDB conversation session.
2. Choose a mode:
   - **Full** — AI answer + retrieved sources
   - **Answer** — AI answer only
   - **Sources** — top 3 ChromaDB matches only
3. Type a question and click **Send**.
4. Click **End Chat** when finished — closes the session in MongoDB.

## API endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | CYFEDIS web frontend |
| `/docs` | GET | Swagger UI |
| `/health` | GET | Check ChromaDB, Groq, and MongoDB |
| `/warmup` | GET | Check embedding model load status |
| `/search` | POST | Search + generate answer (uses chat history) |
| `/search/answer` | POST | Generate answer only |
| `/search/results` | POST | Retrieve top 3 sources only |
| `/conversation/new` | POST | Start a new chat session |
| `/conversation/end` | POST | End the current chat session |

### Example: search request

```bash
curl -X POST http://127.0.0.1:8000/search \
  -H "Content-Type: application/json" \
  -d "{\"question\": \"What is phishing?\"}"
```

## Project structure

```
FEDIS-RAG-Cybersecurity/
├── frontend/              # CYFEDIS web UI (HTML, CSS, JS)
├── src/
│   ├── main.py            # FastAPI app entry point
│   ├── routes/            # API endpoints
│   ├── services/          # Groq integration
│   └── db/                # MongoDB connection and history
├── retrieval/
│   └── retriever.py       # ChromaDB search + embeddings
├── chroma_db/             # Pre-built vector database
├── data/                  # Raw and processed datasets
└── requirements.txt
```

## Notes for teammates

- Pull latest changes before starting work: `git pull origin main`
- Each developer needs their own `.env` with personal API keys.
- `chroma_db/` is included in the repo — no need to rebuild the vector database.
- The embedding model downloads automatically on first use (~1.3 GB, cached locally).
- First question after startup may be slow while the model loads; later questions are faster.
- Use `/health` to verify all services before testing.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Start Chat fails** | Check MongoDB Atlas is running and `MONGO_URI` in `.env` is correct. Verify Network Access in Atlas. |
| **Slow first response** | Wait for "Engine ready" in the header. The embedding model loads once on startup. |
| **`/docs` not loading** | Restart the server. Avoid multiple `--reload` restarts while the model is loading. |
| **Groq errors** | Verify `GROQ_API_KEY` is set in `.env`. |
| **ChromaDB errors** | Ensure `chroma_db/` folder exists in the project root. |
