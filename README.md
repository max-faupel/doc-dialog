# RAG-Demo: Fragen an die eigenen Dokumente

Minimales RAG-System mit FastAPI, ChromaDB und Ollama. Läuft komplett lokal, lässt sich per `.env` aber auch auf einen Cloud-Anbieter mit OpenAI-kompatibler API umstellen.

## Aufbau

| Datei | Aufgabe |
|---|---|
| `config.py` | Alle Einstellungen, überschreibbar per `.env` |
| `rag.py` | Embeddings, Ähnlichkeitssuche, Prompt und Antwort |
| `ingest.py` | Dokumente einlesen, in Abschnitte zerlegen, indexieren |
| `app.py` | REST-API mit `/ask` und `/health` |
| `docs/` | Hier kommen deine PDFs, `.txt`- und `.md`-Dateien hinein |

## Einrichtung

```bash
# 1. Modelle in Ollama laden
ollama pull nomic-embed-text
ollama pull llama3.1

# 2. Python-Umgebung
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 3. Dokumente nach docs/ kopieren, dann indexieren
python ingest.py

# 4. API starten
uvicorn app:app --reload
```

Danach unter http://localhost:8000/docs die Swagger-Oberfläche öffnen oder per curl testen:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Wie lange ist die Kündigungsfrist?"}'
```

Die Antwort enthält neben dem Text auch die verwendeten Abschnitte mit Quelle, Seite und Distanz, sodass du nachprüfen kannst, worauf sich das Modell stützt.

## Ideen zum Experimentieren

1. **Chunk-Größe:** `CHUNK_SIZE` auf 100 und auf 800 setzen, jeweils `python ingest.py --reset`, gleiche Fragen stellen und vergleichen.
2. **Anzahl Treffer:** `top_k` im Request zwischen 1 und 10 variieren. Wann fehlt Kontext, wann verwirrt zu viel?
3. **Halluzinationstest:** Fragen stellen, deren Antwort in keinem Dokument steht. Sagt das Modell ehrlich, dass es nichts findet?
4. **Distanzen beobachten:** Ab welchem `distance`-Wert sind Treffer irrelevant? Daraus lässt sich ein Schwellwert ableiten.
5. **Query-Präfixe:** `nomic-embed-text` liefert bessere Ergebnisse mit den Präfixen `search_document: ` beim Indexieren und `search_query: ` bei Fragen.
6. **Modelle vergleichen:** `CHAT_MODEL` auf `qwen2.5` oder `mistral` umstellen (kein Reset nötig, nur beim Embedding-Modell).

## Mögliche Erweiterungen

Streaming der Antwort per Server-Sent Events, API-Key-Schutz für die eigene API, Upload-Endpunkt für neue Dokumente, Hybrid-Suche (Vektor + Stichwort) oder Re-Ranking der Treffer.
