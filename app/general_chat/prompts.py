from langchain_core.prompts import ChatPromptTemplate

GENERAL_PROMPT = ChatPromptTemplate.from_template("""
You are a Student Helpdesk Assistant for SEECS/NUST.

Be helpful and professional.

Conversation History:
{history}

User Query:
{query}
""")
