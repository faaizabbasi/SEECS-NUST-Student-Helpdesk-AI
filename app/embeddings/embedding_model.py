from langchain_huggingface import HuggingFaceEmbeddings

from app.config import EMBEDDING_MODEL


def build_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
