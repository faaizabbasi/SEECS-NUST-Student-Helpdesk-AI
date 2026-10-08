from app.router.prompts import ROUTER_PROMPT
from app.router.schemas import Router


def build_router_chain(llm):
    return ROUTER_PROMPT | llm.with_structured_output(Router)
