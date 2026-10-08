from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.chat.chatbot import chat_stream
from app.chat.memory import reset
from app.config import ALLOWED_ORIGINS, FRONTEND_DIR
from app.schemas import ChatRequest, ResetResponse

app = FastAPI(title="SEECS/NUST Student Helpdesk Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    return StreamingResponse(
        chat_stream(req.session_id, req.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/reset/{session_id}", response_model=ResetResponse)
def reset_session(session_id: str):
    reset(session_id)
    return ResetResponse()


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
