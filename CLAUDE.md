# doc-dialog

RAG-System zum Befragen eigener Dokumente. Python-Backend (FastAPI + ChromaDB), Vue-3-Frontend. LLMs laufen lokal über Ollama oder in der Cloud über eine OpenAI-kompatible API.

## Struktur

- `backend/` – FastAPI-App, Indexierung, RAG-Logik
  - `config.py` – alle Einstellungen, überschreibbar per `.env`
  - `rag.py` – Embeddings, Ähnlichkeitssuche, Prompt, Antwort
  - `ingest.py` – Dokumente aus `docs/` einlesen und indexieren
  - `app.py` – REST-API (`POST /ask`, `GET /health`)
  - `docs/` – Quelldokumente (PDF, TXT, MD), Inhalt wird nicht committet
- `frontend/` – Vue 3 + Vite + TypeScript, Chat-Oberfläche

## Befehle

Backend (in `backend/`, mit aktivierter venv):
- `pip install -r requirements.txt`
- `python ingest.py` / `python ingest.py --reset`
- `uvicorn app:app --reload` (Port 8000)

Frontend (in `frontend/`):
- `npm install`
- `npm run dev` (Port 5173, `/api` wird per Vite-Proxy auf `http://localhost:8000` umgeleitet)
- `npm run build`, `npm run type-check`

Voraussetzung lokal: `ollama pull nomic-embed-text` und `ollama pull llama3.1`

## Konventionen

### Allgemein
- UI-Texte und Code-Kommentare auf Deutsch, Bezeichner (Variablen, Funktionen, Dateien) auf Englisch.
- Keine Secrets im Code. `.env`, `chroma_db/` und Inhalte von `backend/docs/` stehen in `.gitignore`.

### Backend
- LLM-Anbieter nie hart verdrahten: immer über den OpenAI-Client mit `LLM_BASE_URL`, `LLM_API_KEY` und Modellnamen aus `config.py`.
- Wird das Embedding-Modell oder die Chunk-Logik geändert, muss der Index mit `python ingest.py --reset` neu aufgebaut werden. Darauf hinweisen.
- Endpunkte mit synchronen Clients als `def` (nicht `async def`) deklarieren, damit FastAPI sie im Threadpool ausführt.
- Request- und Response-Modelle immer als Pydantic-Klassen. Änderungen an der API-Form auch im Frontend-Typ `frontend/src/types/api.ts` nachziehen.

### Frontend
- Vue 3 Composition API mit `<script setup lang="ts">`.
- API-Aufrufe ausschließlich über `frontend/src/api/client.ts`, immer relativ unter `/api`.
- Vorerst kein Router, kein Pinia, keine UI-Bibliothek. Erst einführen, wenn es wirklich gebraucht wird.
- Styling mit Scoped CSS und CSS-Variablen, helles und dunkles Theme über `prefers-color-scheme`.

## Arbeitsweise
- Nach Änderungen prüfen: Backend startet ohne Fehler, `npm run type-check` und `npm run build` laufen durch.
- Bei größeren Änderungen erst einen Plan vorschlagen, dann umsetzen.
