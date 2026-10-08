from app.general_chat.prompts import GENERAL_PROMPT


def general_answer(llm, query, history):
    prompt_value = GENERAL_PROMPT.invoke({"query": query, "history": history})
    return llm.stream(prompt_value)
