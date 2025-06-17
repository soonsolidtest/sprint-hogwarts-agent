# graphs/unknown.py

from typing import TypedDict, List
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph
from tools.retry_llm_intent_guess import retry_llm_intent_guess_node

class UnknownState(TypedDict):
    messages: List[BaseMessage]

# 构建子图
builder = StateGraph(UnknownState)
builder.add_node("guess_intent", retry_llm_intent_guess_node)  # 使用工具
builder.set_entry_point("guess_intent")
builder.set_finish_point("guess_intent")

unknown_graph = builder.compile()
