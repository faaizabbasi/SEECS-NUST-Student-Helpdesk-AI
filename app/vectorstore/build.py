import hashlib
import json

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_DIR, VECTORSTORE_DIR
from app.embeddings.embedding_model import build_embeddings
from app.loaders.documents import load_documents

manifest_path = VECTORSTORE_DIR / "manifest.json"
index_path = VECTORSTORE_DIR / "faiss_index"


def hash_data_dir():
    hasher = hashlib.sha256()
    for path in sorted(DATA_DIR.glob("**/*")):
        if path.is_file():
            hasher.update(path.name.encode())
            hasher.update(str(path.stat().st_size).encode())
            hasher.update(str(path.stat().st_mtime).encode())
    return hasher.hexdigest()


def build_vector_store():
    docs = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(docs)

    embeddings = build_embeddings()
    vector_db = FAISS.from_documents(chunks, embeddings)

    vector_db.save_local(str(index_path))
    manifest_path.write_text(json.dumps({"data_hash": hash_data_dir()}))

    return vector_db


def load_or_build_vector_store():
    current_hash = hash_data_dir()

    if index_path.exists() and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())

        if manifest.get("data_hash") == current_hash:
            embeddings = build_embeddings()
            return FAISS.load_local(
                str(index_path),
                embeddings,
                allow_dangerous_deserialization=True
            )

    return build_vector_store()
