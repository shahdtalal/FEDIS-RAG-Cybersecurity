from fastapi import FastAPI

from src.routes.health import router as health_router
from src.routes.search import router as search_router

app = FastAPI(title="FEDIS RAG Cybersecurity API")

app.include_router(health_router)
app.include_router(search_router)


@app.get("/")
def root():
    return {"message": "FEDIS RAG API is running"}
