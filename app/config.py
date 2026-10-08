import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "raw"
VECTORSTORE_DIR = ROOT_DIR / "data" / "vectorstore"
FRONTEND_DIR = ROOT_DIR / "frontend"

DATA_DIR.mkdir(parents=True, exist_ok=True)
VECTORSTORE_DIR.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv("API_KEY", "")

if not API_KEY:
    raise RuntimeError(
        "API_KEY is not set. Create a .env file in the project root "
        "containing API_KEY=your_key_here."
    )

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL = os.getenv("LLM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

RETRIEVER_K = int(os.getenv("RETRIEVER_K", "8"))
RETRIEVER_FETCH_K = int(os.getenv("RETRIEVER_FETCH_K", "20"))

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
