from langchain_core.prompts import ChatPromptTemplate

HELP_PROMPT = ChatPromptTemplate.from_template("""
Convert this into a structured help request:

Query:
{query}
""")
