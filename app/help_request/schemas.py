from typing import Literal

from pydantic import BaseModel


class HelpRequest(BaseModel):
    title: str
    category: str
    priority: Literal["Low", "Medium", "High"]
    description: str
