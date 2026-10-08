# SEECS/NUST Student Helpdesk AI

A RAG chatbot that answers student questions from official SEECS/NUST
handbooks and forms — citing the exact document and page for every
answer, and honestly saying so when something isn't covered rather
than guessing.

Ask it about admission policy, CGPA requirements, attendance rules,
thesis deadlines, course descriptions, or how to change an elective,
and it answers grounded in the actual source documents. Ask it to
help with a request (an elective change, a deadline extension) and
it drafts a structured, prioritized request instead. Ask it something
unrelated and it just chats.

## Features

- **Intent routing** — every message is classified as a document
  lookup, a help-request draft, or general conversation, and handled
  differently
- **Grounded answers with citations** — every document answer names
  the exact source file and page it came from
- **Streamed responses** — answers appear token by token over Server-
  Sent Events, not as one block after a delay
- **Markdown rendering** — tables, headings, and formatting in answers
  render properly in the chat UI, not as raw symbols
- **Automatic retry with backoff** — a transient upstream failure
  retries invisibly before ever surfacing an error to the user
- **Session memory** — follow-up questions ("what about for a PhD?")
  correctly use prior conversation context

## Tech stack

- **Backend** — FastAPI, LangChain
- **LLM** — Nemotron 3 Ultra, served via OpenRouter
- **Retrieval** — FAISS vector store, HuggingFace `sentence-transformers`
  embeddings
- **Frontend** — vanilla HTML/CSS/JS, Server-Sent Events for streaming,
  `marked` + `DOMPurify` for rendering markdown answers safely

## How it works

1. A message comes in and is classified by the router into one of
   three intents: `document_qa`, `help_request`, or `general_chat`.
2. **document_qa** retrieves the most relevant chunks from the FAISS
   index, tags each with its source file and page, and the LLM
   answers grounded only in that retrieved context.
3. **help_request** extracts the message into a structured request
   (title, category, priority, description) instead of answering it.
4. **general_chat** replies conversationally, with no document lookup.
5. The answer streams back token by token over Server-Sent Events and
   renders live in the chat UI, with source citations attached once
   the answer completes.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
echo "API_KEY=your_openrouter_api_key_here" > .env   # then edit in your real key
```

This repo doesn't bundle the source handbooks/forms (institutional
documents aren't ours to redistribute). Drop your own PDFs/.docx/.md
files into `data/raw/` before running. On first run, they're chunked,
embedded, and saved to `data/vectorstore/`; later runs reuse that
index unless the files in `data/raw/` change.

## Run

```bash
python chatbot.py
```

This starts the API and serves the frontend at `http://localhost:8000`.

## Project layout

- `app/loaders`, `app/embeddings`, `app/vectorstore` — build the knowledge base (Phase 1)
- `app/llm` — the LLM, served via OpenRouter (Phase 2)
- `app/router` — classifies each query as `document_qa`, `help_request`, or `general_chat` (Phase 3)
- `app/rag` — retrieval-augmented answers with source citations (Phase 4)
- `app/help_request` — turns a query into a structured help request (Phase 5)
- `app/general_chat` — plain conversational replies (Phase 6)
- `app/chat` — session memory and the engine that ties it all together, streamed as SSE (Phase 7)
- `app/main.py` — the FastAPI app (`/chat`, `/reset/{session_id}`, `/health`), also serving `frontend/`
- `frontend/` — the chat UI, consumes the `/chat` stream token by token

## API

- `POST /chat` — `{"message": "...", "session_id": "..."}`, responds with a
  `text/event-stream` of `{"type": "intent" | "token" | "done" | "error", ...}` events
- `POST /reset/{session_id}` — clears that session's conversation memory
- `GET /health` — liveness check
