"""Gemeinsame Fixtures. Tests laufen ohne Ollama und ohne echten Index."""

import os
import tempfile

# Muss vor dem Import von config/rag passieren: ChromaDB wird beim Import geöffnet
os.environ["DB_DIR"] = tempfile.mkdtemp(prefix="doc-dialog-test-")
os.environ["COLLECTION"] = "test"

from types import SimpleNamespace  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

import rag  # noqa: E402
from app import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def empty_index():
    """Jeder Test startet mit leerem Index."""
    rag.reset_collection()
    yield
    rag.reset_collection()


@pytest.fixture
def fake_embed(monkeypatch):
    """Ersetzt Embeddings durch einen festen Vektor (kein LLM-Aufruf)."""
    monkeypatch.setattr(rag, "embed", lambda texts: [[1.0, 0.0, 0.0] for _ in texts])


@pytest.fixture
def fake_chat(monkeypatch):
    """Ersetzt den Chat-Aufruf; liefert eine feste Antwort und merkt sich die Aufrufe."""
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Antwort [1]"))])

    monkeypatch.setattr(rag.client.chat.completions, "create", create)
    return calls


def add_chunk(text: str, source: str = "test.md", page: int | None = None):
    meta = {"source": source, **({"page": page} if page else {})}
    rag.get_collection().add(
        ids=[f"{source}|{page}|{text}"], documents=[text], embeddings=[[1.0, 0.0, 0.0]], metadatas=[meta]
    )
