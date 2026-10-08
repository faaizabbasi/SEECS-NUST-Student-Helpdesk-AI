from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader

from app.config import DATA_DIR


def load_documents():
    docs = []

    for path in DATA_DIR.glob("*.pdf"):
        pdf_docs = PyPDFLoader(str(path)).load()
        for d in pdf_docs:
            d.metadata["source"] = path.name
        docs.extend(pdf_docs)

    for path in DATA_DIR.glob("*.docx"):
        docx_docs = Docx2txtLoader(str(path)).load()
        for d in docx_docs:
            d.metadata["source"] = path.name
        docs.extend(docx_docs)

    for path in list(DATA_DIR.glob("*.md")) + list(DATA_DIR.glob("*.txt")):
        text_docs = TextLoader(str(path)).load()
        for d in text_docs:
            d.metadata["source"] = path.name
        docs.extend(text_docs)

    return docs
