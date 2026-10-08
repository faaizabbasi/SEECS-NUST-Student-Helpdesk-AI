from typing import Literal

from pydantic import BaseModel


class Router(BaseModel):
    intent: Literal["document_qa", "help_request", "general_chat"]
