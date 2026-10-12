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

Backend (in `backend/`, mit aktivierter venv `.venv`):
- `pip install -r requirements-dev.txt` (enthält `requirements.txt` plus pytest, ruff)
- `pytest` – Tests, LLM und Index werden gemockt (`tests/conftest.py`)
- `ruff check .` / `ruff format .`
- `python ingest.py` / `python ingest.py --reset`
- `uvicorn app:app --reload` (Port 8000)

Frontend (in `frontend/`):
- `npm install`
- `npm run dev` (Port 5173, `/api` wird per Vite-Proxy auf `http://localhost:8000` umgeleitet)
- `npm run test:unit` (Vitest, Tests in `src/**/__tests__/*.spec.ts`)
- `npm run lint` (ESLint mit `--fix`), `npm run format` (Prettier)
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
- Nach Änderungen prüfen: Backend startet ohne Fehler, `pytest` und `ruff check .` sind grün; im Frontend laufen `test:unit`, `lint`, `type-check` und `build` durch.
- Bei größeren Änderungen erst einen Plan vorschlagen, dann umsetzen.

## Agentic Workflow
Ausführliche Anleitung: `docs/agentic-workflow.md`
- Specs liegen in `docs/features/<slug>.md` (Status `draft` → `approved` → `done`), API-Vertrag und Akzeptanzkriterien darin sind verbindlich.
- Subagents in `.claude/agents/`: `feature-analyst` (Spec, schreibt nur `docs/features/`), `backend-dev` (nur `backend/`), `frontend-dev` (nur `frontend/`), `reviewer` (read-only, Findings blocker / should-fix / nit).
- `/feature <Idee|Spec-Pfad>`: Spec → Freigabe durch den Nutzer → Branch `feature/<slug>` von `main` → Backend → Frontend → Review → max. 2 Fix-Runden → Spec `done` und Commit-Vorschlag. Die Orchestrierung liegt beim Hauptagent. Subagents bekommen Spec-Pfad und Auftrag explizit.
- `/spec <Idee>` nur Spec, `/review` nur Review des aktuellen Diffs.
- Commit, Push, PR und Merge nur nach Freigabe durch den Nutzer. Integration per PR gegen `main`.
- Ein PostToolUse-Hook formatiert bearbeitete Dateien automatisch (ruff bzw. prettier, `.claude/hooks/format.sh`).
