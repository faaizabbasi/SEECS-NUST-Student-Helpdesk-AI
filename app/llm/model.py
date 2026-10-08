from langchain_openai import ChatOpenAI

from app.config import API_KEY, LLM_MODEL, OPENROUTER_BASE_URL


def build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=LLM_MODEL,
        api_key=API_KEY,
        base_url=OPENROUTER_BASE_URL,
        temperature=0,
    )
