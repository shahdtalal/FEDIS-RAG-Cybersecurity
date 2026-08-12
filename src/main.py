from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.routes.conversation import router as conversation_router
from src.routes.health import router as health_router
from src.routes.search import router as search_router
from src.routes.search_split import router as search_split_router

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="FEDIS RAG Cybersecurity API")

app.include_router(health_router)
app.include_router(search_router)
app.include_router(search_split_router)
app.include_router(conversation_router)

app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")


@app.on_event("startup")
def startup_warmup():
    from retrieval.retriever import start_warmup

    start_warmup()


@app.get("/")
def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api")
def api_status():
    return {"message": "FEDIS RAG API is running"}
