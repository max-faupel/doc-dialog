# doc-dialog

Fragen an die eigenen Dokumente stellen: ein RAG-System mit FastAPI, ChromaDB und einer Chat-Oberfläche in Vue 3. Die Sprachmodelle laufen lokal über Ollama oder in der Cloud über eine OpenAI-kompatible API, umschaltbar per `.env`.

Jede Antwort nennt ihre Belege als Nummern wie `[2]`. Unter der Antwort stehen die verwendeten Textauszüge mit Datei, Seite und Distanz. Ein Klick auf eine Belegnummer klappt den passenden Auszug auf.

## Aufbau

```
doc-dialog/
├── backend/                FastAPI-App, Indexierung, RAG-Logik
│   ├── config.py           Alle Einstellungen, überschreibbar per .env
│   ├── rag.py              Embeddings, Ähnlichkeitssuche, Prompt und Antwort
│   ├── ingest.py           Dokumente einlesen, in Abschnitte zerlegen, indexieren
│   ├── app.py              REST-API: POST /ask, GET /health
│   └── docs/               Deine PDFs, .txt- und .md-Dateien (werden nicht committet)
└── frontend/               Vue 3 + Vite + TypeScript
    └── src/
        ├── api/client.ts   Alle API-Aufrufe
        ├── types/api.ts    Typen passend zu den Pydantic-Modellen
        └── components/     Chat-Eingabe, Nachricht, Quellenliste
```

## Voraussetzungen

- Python 3.10+
- Node.js 22.18+ oder 24.12+
- [Ollama](https://ollama.com) mit den Modellen für Embeddings und Chat:

  ```bash
  ollama pull nomic-embed-text
  ollama pull llama3.1
  ```

## Einrichtung Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt   # nur Betrieb: requirements.txt
pytest                             # Tests (ohne Ollama)
cp .env.example .env               # bei Bedarf anpassen

# Dokumente nach backend/docs/ kopieren, dann indexieren
python ingest.py

# API starten (Port 8000)
uvicorn app:app --reload
```

Unter http://localhost:8000/docs gibt es die Swagger-Oberfläche. Test per curl:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Wie lange ist die Kündigungsfrist?"}'
```

Alle Pfade in `config.py` gelten relativ zu `backend/`. `ingest.py` und `uvicorn` funktionieren deshalb unabhängig vom Arbeitsverzeichnis.

## Einrichtung Frontend

```bash
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

Der Vite-Dev-Server leitet `/api/*` an `http://localhost:8000/*` weiter. Das Backend muss dafür laufen. Ist es nicht erreichbar, zeigt die Oberfläche einen Hinweis statt einer Antwort.

Weitere Befehle: `npm run test:unit`, `npm run lint`, `npm run format`, `npm run type-check`, `npm run build` (Ergebnis in `frontend/dist/`).

## Konfiguration

Alle Einstellungen stehen in `backend/.env` (Vorlage: `backend/.env.example`):

| Variable | Standard | Bedeutung |
|---|---|---|
| `LLM_BASE_URL` | `http://localhost:11434/v1` | OpenAI-kompatibler Endpunkt (Ollama oder Cloud) |
| `LLM_API_KEY` | `ollama` | API-Key, wird von Ollama ignoriert |
| `CHAT_MODEL` | `llama3.1` | Modell für die Antworten |
| `EMBED_MODEL` | `nomic-embed-text` | Modell für die Embeddings |
| `CHUNK_SIZE` / `CHUNK_OVERLAP` | `300` / `50` | Wörter pro Abschnitt und Überlappung |
| `TOP_K` | `4` | Abschnitte pro Frage |
| `CORS_ORIGINS` | `http://localhost:5173` | Erlaubte Origins, kommagetrennt |

**Wichtig:** Nach jeder Änderung von `EMBED_MODEL`, `CHUNK_SIZE` oder `CHUNK_OVERLAP` den Index neu aufbauen:

```bash
python ingest.py --reset
```

Der Modellname muss genau so lauten wie in `ollama list`. Ist dort zum Beispiel nur `llama3.1:8b` installiert, gehört `CHAT_MODEL=llama3.1:8b` in die `.env`.

### Ollama unter Windows, Backend in WSL

Im Standard-Netzwerkmodus von WSL2 (NAT) erreicht `localhost` in WSL nicht den Windows-Host. Es gibt zwei Wege:

1. **Mirrored Networking (empfohlen):** In `%UserProfile%\.wslconfig` eintragen:

   ```ini
   [wsl2]
   networkingMode=mirrored
   ```

   Danach `wsl --shutdown` in PowerShell ausführen. `localhost:11434` funktioniert dann aus WSL heraus, an der `.env` muss nichts geändert werden.

2. **Host-IP verwenden:** In Windows die Umgebungsvariable `OLLAMA_HOST=0.0.0.0` setzen und Ollama neu starten. In `backend/.env` dann die Host-IP eintragen, die `ip route show default | awk '{print $3}'` liefert, z. B. `LLM_BASE_URL=http://172.20.80.1:11434/v1`. Die IP kann sich nach einem Neustart ändern. Unter Umständen muss die Windows-Firewall Port 11434 freigeben. Ollama ist damit auch im lokalen Netz erreichbar.

## Weiterentwicklung mit Claude Code

Für die agentische Weiterentwicklung gibt es Subagents und die Skills `/feature`, `/spec` und `/review`. Wie sie zusammenspielen, beschreibt [docs/agentic-workflow.md](docs/agentic-workflow.md).

## Ideen zum Experimentieren

1. **Chunk-Größe:** `CHUNK_SIZE` auf 100 und auf 800 setzen, jeweils `python ingest.py --reset`, gleiche Fragen stellen und vergleichen.
2. **Anzahl Treffer:** `top_k` im Request zwischen 1 und 10 variieren. Wann fehlt Kontext, wann verwirrt zu viel?
3. **Halluzinationstest:** Fragen stellen, deren Antwort in keinem Dokument steht. Sagt das Modell ehrlich, dass es nichts findet?
4. **Distanzen beobachten:** Ab welchem `distance`-Wert sind Treffer irrelevant? Daraus lässt sich ein Schwellwert ableiten.
5. **Query-Präfixe:** `nomic-embed-text` liefert bessere Ergebnisse mit den Präfixen `search_document: ` beim Indexieren und `search_query: ` bei Fragen (danach `--reset`).
6. **Modelle vergleichen:** `CHAT_MODEL` auf `qwen2.5` oder `mistral` umstellen. Ein Reset ist nur beim Embedding-Modell nötig.

## Mögliche Erweiterungen

Streaming der Antwort per Server-Sent Events, Auswahl von `top_k` in der Oberfläche, API-Key-Schutz für die eigene API, Upload-Endpunkt für neue Dokumente, Hybrid-Suche (Vektor + Stichwort) oder Re-Ranking der Treffer.
