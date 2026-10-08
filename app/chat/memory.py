from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage

sessions = {}


def _session(session_id):
    if session_id not in sessions:
        sessions[session_id] = InMemoryChatMessageHistory()
    return sessions[session_id]


def get_history(session_id):
    history = ""
    for msg in _session(session_id).messages:
        history += f"{msg.type}: {msg.content}\n"
    return history


def add_user(session_id, content):
    _session(session_id).add_message(HumanMessage(content=content))


def add_ai(session_id, content):
    _session(session_id).add_message(AIMessage(content=content))


def reset(session_id):
    sessions.pop(session_id, None)
