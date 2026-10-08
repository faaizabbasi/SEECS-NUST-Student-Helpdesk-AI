from app.config import RETRIEVER_K


def build_retriever(vector_db):
    return vector_db.as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVER_K}
    )