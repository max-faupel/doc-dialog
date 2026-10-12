"""Smoke-Tests für die REST-API."""

from tests.conftest import add_chunk


def test_health_reports_empty_index(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["chunks_im_index"] == 0


def test_ask_rejects_too_short_question(client):
    res = client.post("/ask", json={"question": "a"})
    assert res.status_code == 422


def test_ask_rejects_top_k_out_of_range(client):
    res = client.post("/ask", json={"question": "Was steht drin?", "top_k": 0})
    assert res.status_code == 422


def test_ask_with_empty_index_returns_hint(client, fake_embed):
    res = client.post("/ask", json={"question": "Was steht drin?"})
    assert res.status_code == 200
    body = res.json()
    assert "Index ist leer" in body["answer"]
    assert body["sources"] == []


def test_ask_returns_answer_and_sources(client, fake_embed, fake_chat):
    add_chunk("Die Kündigungsfrist beträgt drei Monate.", source="vertrag.pdf", page=2)
    res = client.post("/ask", json={"question": "Wie lange ist die Kündigungsfrist?"})
    assert res.status_code == 200
    body = res.json()
    assert body["answer"] == "Antwort [1]"
    assert body["sources"][0]["source"] == "vertrag.pdf"
    assert body["sources"][0]["page"] == 2
    assert "Kündigungsfrist" in fake_chat[0]["messages"][1]["content"]


def test_ask_returns_502_when_llm_fails(client, monkeypatch):
    import rag

    def boom(texts):
        raise RuntimeError("Ollama nicht erreichbar")

    add_chunk("Irgendein Text.")
    monkeypatch.setattr(rag, "embed", boom)
    res = client.post("/ask", json={"question": "Was steht drin?"})
    assert res.status_code == 502
    assert "Ollama nicht erreichbar" in res.json()["detail"]
