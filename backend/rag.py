"""RAG-Kernlogik: Embeddings berechnen, ähnliche Abschnitte suchen, Antwort generieren."""
import chromadb
from openai import OpenAI

import config

client = OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY)
_db = chromadb.PersistentClient(path=config.DB_DIR)

SYSTEM_PROMPT = """Du beantwortest Fragen ausschließlich auf Grundlage der bereitgestellten Textauszüge.
- Wenn die Auszüge die Antwort nicht enthalten, sage das ehrlich und rate nicht.
- Belege jede Aussage mit der Nummer des Auszugs in eckigen Klammern, z. B. [2].
- Antworte in der Sprache der Frage."""


def get_collection():
    # Kosinus-Distanz: 0 = identisch, 2 = gegensätzlich
    return _db.get_or_create_collection(config.COLLECTION, metadata={"hnsw:space": "cosine"})


def reset_collection():
    try:
        _db.delete_collection(config.COLLECTION)
    except Exception:
        pass  # existierte noch nicht


def embed(texts: list[str]) -> list[list[float]]:
    resp = client.embeddings.create(model=config.EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def retrieve(question: str, top_k: int = config.TOP_K) -> list[dict]:
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    res = collection.query(query_embeddings=embed([question]), n_results=min(top_k, count))
    hits = []
    for text, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({
            "source": meta["source"],
            "page": meta.get("page"),
            "distance": round(dist, 3),
            "text": text,
        })
    return hits


def build_context(hits: list[dict]) -> str:
    parts = []
    for i, h in enumerate(hits, 1):
        label = h["source"] + (f", S. {h['page']}" if h["page"] else "")
        parts.append(f"[{i}] ({label})\n{h['text']}")
    return "\n\n".join(parts)


def answer(question: str, top_k: int = config.TOP_K) -> dict:
    hits = retrieve(question, top_k)
    if not hits:
        return {"answer": "Der Index ist leer. Bitte zuerst `python ingest.py` ausführen.", "sources": []}

    resp = client.chat.completions.create(
        model=config.CHAT_MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Auszüge:\n\n{build_context(hits)}\n\nFrage: {question}"},
        ],
    )
    return {"answer": resp.choices[0].message.content, "sources": hits}
