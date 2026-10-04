"""REST-API für Fragen an die eigenen Dokumente.

Start:  uvicorn app:app --reload
Test:   http://localhost:8000/docs
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import config
import rag

app = FastAPI(title="doc-dialog", description="Fragen an eigene Dokumente, lokal mit Ollama oder in der Cloud")

# Erlaubt direkte Aufrufe vom Frontend (im Dev-Betrieb läuft es zusätzlich über den Vite-Proxy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class Question(BaseModel):
    question: str = Field(min_length=3, examples=["Wie lange ist die Kündigungsfrist?"])
    top_k: int = Field(default=config.TOP_K, ge=1, le=20)


class Source(BaseModel):
    source: str
    page: int | None = None
    distance: float
    text: str


class Answer(BaseModel):
    answer: str
    sources: list[Source]


# Bewusst "def" statt "async def": die Clients sind synchron,
# FastAPI führt den Endpunkt dann in einem Threadpool aus und blockiert nicht.
@app.post("/ask", response_model=Answer)
def ask(q: Question):
    try:
        return rag.answer(q.question, q.top_k)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM-Aufruf fehlgeschlagen: {e}")


@app.get("/health")
def health():
    return {
        "chunks_im_index": rag.get_collection().count(),
        "llm_base_url": config.LLM_BASE_URL,
        "chat_model": config.CHAT_MODEL,
        "embed_model": config.EMBED_MODEL,
    }
