from app.help_request.prompts import HELP_PROMPT
from app.help_request.schemas import HelpRequest


def build_help_chain(llm):
    return HELP_PROMPT | llm.with_structured_output(HelpRequest)
