from app.rag.prompts import RAG_PROMPT


def format_context(docs):
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page")
        label = f"{source}, page {page + 1}" if page is not None else source
        parts.append(f"[Source: {label}]\n{doc.page_content}")
    return "\n\n".join(parts)


def rag_answer(llm, retriever, question, history):
    docs = retriever.invoke(question)
    prompt_value = RAG_PROMPT.invoke({
        "context": format_context(docs),
        "question": question,
        "history": history
    })
    return docs, llm.stream(prompt_value)
