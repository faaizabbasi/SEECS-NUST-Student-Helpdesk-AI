from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's message")
    session_id: str = Field(..., description="Stable id identifying the browser session")


class ResetResponse(BaseModel):
    status: Literal["ok"] = "ok"
