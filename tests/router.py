# router.py

from typing import TypedDict
from langchain_core.messages import BaseMessage
import re

class MessagesState(TypedDict):
    messages: list[BaseMessage]
    module: str

def route_to_module(state: MessagesState) -> MessagesState:
    last = state["messages"][-1].content.lower()
    if re.search(r"(打印|print|rayware)", last):
        state["module"] = "rayware"
    else:
        state["module"] = "unknown"
    return state
