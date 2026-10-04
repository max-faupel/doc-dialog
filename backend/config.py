"""Zentrale Konfiguration. Alle Werte lassen sich über .env oder Umgebungsvariablen überschreiben."""
import os
from pathlib import Path

from dotenv import load_dotenv

# Basisverzeichnis des Backends: Pfade gelten unabhängig vom Arbeitsverzeichnis
BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

# LLM-Anbindung: Standard ist lokales Ollama über die OpenAI-kompatible Schnittstelle.
# Für die Cloud z. B. LLM_BASE_URL=https://api.openai.com/v1 und einen echten API-Key setzen.
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "ollama")  # Ollama ignoriert den Key
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.1")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# Daten und Index
# Relative Angaben werden relativ zu BASE_DIR aufgelöst
DOCS_DIR = str(BASE_DIR / os.getenv("DOCS_DIR", "docs"))
DB_DIR = str(BASE_DIR / os.getenv("DB_DIR", "chroma_db"))
COLLECTION = os.getenv("COLLECTION", "dokumente")

# Stellschrauben zum Experimentieren
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "300"))      # Wörter pro Abschnitt
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))  # Überlappung in Wörtern
TOP_K = int(os.getenv("TOP_K", "4"))                   # Abschnitte pro Frage

# Erlaubte Origins für CORS (kommagetrennt), Standard ist der Vite-Dev-Server
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
