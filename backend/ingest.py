"""Liest Dokumente aus DOCS_DIR, zerlegt sie in Abschnitte und speichert sie mit Embeddings in ChromaDB.

Aufruf:
    uv run python ingest.py          # neue/geänderte Abschnitte hinzufügen bzw. aktualisieren
    uv run python ingest.py --reset  # Index komplett neu aufbauen (z. B. nach Änderung der Chunk-Größe)
"""

import argparse
import hashlib
from pathlib import Path

from pypdf import PdfReader

import config
import rag

SUPPORTED = {".pdf", ".txt", ".md"}
BATCH_SIZE = 32


def read_file(path: Path):
    """Liefert (seitennummer, text). Bei PDFs pro Seite, sonst einmal mit Seite None."""
    if path.suffix.lower() == ".pdf":
        for i, page in enumerate(PdfReader(path).pages, 1):
            yield i, page.extract_text() or ""
    else:
        yield None, path.read_text(encoding="utf-8", errors="ignore")


def chunk_words(text: str, size: int, overlap: int):
    words = text.split()
    step = max(1, size - overlap)
    for start in range(0, len(words), step):
        yield " ".join(words[start : start + size])
        if start + size >= len(words):
            break


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Index vorher löschen")
    args = parser.parse_args()

    if args.reset:
        rag.reset_collection()
        print("Index gelöscht.")

    docs_dir = Path(config.DOCS_DIR)
    files = [p for p in sorted(docs_dir.rglob("*")) if p.suffix.lower() in SUPPORTED]
    if not files:
        print(f"Keine Dateien ({', '.join(SUPPORTED)}) in '{docs_dir}' gefunden.")
        return

    ids, texts, metas = [], [], []
    for path in files:
        rel = str(path.relative_to(docs_dir))
        n = 0
        for page, text in read_file(path):
            for j, chunk in enumerate(chunk_words(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)):
                ids.append(hashlib.sha1(f"{rel}|{page}|{j}".encode()).hexdigest())
                texts.append(chunk)
                metas.append({"source": rel, **({"page": page} if page else {})})
                n += 1
        print(f"  {rel}: {n} Abschnitte")

    collection = rag.get_collection()
    for i in range(0, len(texts), BATCH_SIZE):
        collection.upsert(
            ids=ids[i : i + BATCH_SIZE],
            documents=texts[i : i + BATCH_SIZE],
            embeddings=rag.embed(texts[i : i + BATCH_SIZE]),
            metadatas=metas[i : i + BATCH_SIZE],
        )
        print(f"  Embeddings: {min(i + BATCH_SIZE, len(texts))}/{len(texts)}")

    print(f"Fertig. {collection.count()} Abschnitte im Index.")


if __name__ == "__main__":
    main()
