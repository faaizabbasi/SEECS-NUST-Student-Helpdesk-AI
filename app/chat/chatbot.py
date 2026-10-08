import json
import time

from app.chat.memory import add_ai, add_user, get_history
from app.general_chat.chain import general_answer
from app.help_request.chain import build_help_chain
from app.llm.model import build_llm
from app.rag.chain import rag_answer
from app.router.chain import build_router_chain
from app.vectorstore.build import load_or_build_vector_store
from app.vectorstore.retriever import build_retriever

vector_db = load_or_build_vector_store()
retriever = build_retriever(vector_db)
llm = build_llm()
router_chain = build_router_chain(llm)
help_chain = build_help_chain(llm)

RETRY_ATTEMPTS = 6
RETRY_DELAY = 2


def sse(payload):
    return f"data: {json.dumps(payload)}\n\n"


def invoke_with_retry(fn):
    for attempt in range(RETRY_ATTEMPTS):
        try:
            return fn()
        except Exception:
            if attempt == RETRY_ATTEMPTS - 1:
                raise
            time.sleep(RETRY_DELAY * (attempt + 1))


def stream_with_retry(make_stream):
    for attempt in range(RETRY_ATTEMPTS):
        started = False
        try:
            for chunk in make_stream():
                started = True
                yield chunk
            return
        except Exception:
            if started or attempt == RETRY_ATTEMPTS - 1:
                raise
            time.sleep(RETRY_DELAY * (attempt + 1))


def format_help_answer(structured):
    return (
        "I've drafted a help request for you:\n\n"
        f"Title: {structured.title}\n"
        f"Category: {structured.category}\n"
        f"Priority: {structured.priority}\n"
        f"Description: {structured.description}\n\n"
        "Let me know if you'd like to adjust anything before it's submitted."
    )


def build_sources(docs, answer):
    if "could not find this information" in answer.lower():
        return []

    seen = set()
    sources = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page")
        key = (source, page)
        if key in seen:
            continue
        seen.add(key)
        sources.append({"source": source, "page": page})

    return sources[:4]


def chat_stream(session_id, query):
    try:
        history = get_history(session_id)
        route = invoke_with_retry(lambda: router_chain.invoke({"query": query}))
        add_user(session_id, query)

        yield sse({"type": "intent", "intent": route.intent})

        if route.intent == "document_qa":
            docs = []

            def make_stream():
                nonlocal docs
                docs, stream = rag_answer(llm, retriever, query, history)
                return stream

            answer = ""
            for chunk in stream_with_retry(make_stream):
                if chunk.content:
                    answer += chunk.content
                    yield sse({"type": "token", "content": chunk.content})

            sources = build_sources(docs, answer)
            add_ai(session_id, answer)
            yield sse({"type": "done", "intent": "document_qa", "sources": sources})

        elif route.intent == "help_request":
            structured = invoke_with_retry(lambda: help_chain.invoke({"query": query}))
            answer = format_help_answer(structured)

            for word in answer.split(" "):
                yield sse({"type": "token", "content": word + " "})
                time.sleep(0.015)

            add_ai(session_id, answer)
            yield sse({
                "type": "done",
                "intent": "help_request",
                "help_request": structured.model_dump()
            })

        else:
            answer = ""
            for chunk in stream_with_retry(lambda: general_answer(llm, query, history)):
                if chunk.content:
                    answer += chunk.content
                    yield sse({"type": "token", "content": chunk.content})

            add_ai(session_id, answer)
            yield sse({"type": "done", "intent": "general_chat"})

    except Exception as e:
        yield sse({"type": "error", "message": str(e)})
