from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage
from state.types import MessagesState
from tools.llm_call import llm_call
from tools.should_continue import should_continue
from graphs.unknown import unknown_graph

# 定义 Cloud Driver 子模块状态结构
class CloudDriverState(TypedDict):
    messages: List[BaseMessage]
    cloud_driver_intent: str
    error_count: int
    last_error: str
    test_config: Dict[str, Any]

def init_cloud_driver_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """初始化 Cloud Driver 状态"""
    if not isinstance(state, dict):
        state = {}
    
    state.setdefault("messages", [])
    state.setdefault("cloud_driver_intent", "")
    state.setdefault("error_count", 0)
    state.setdefault("last_error", "")
    state.setdefault("test_config", {})
    
    return state

def handle_cloud_driver_error(state: Dict[str, Any]) -> Dict[str, Any]:
    """处理 Cloud Driver 错误"""
    state = init_cloud_driver_state(state)
    state["error_count"] += 1
    state["last_error"] = "处理Cloud Driver操作时发生错误"
    return state

builder = StateGraph(MessagesState)

# 添加节点
builder.add_node("unknown", unknown_graph)
builder.add_node("handle_error", handle_cloud_driver_error)

# 起始点
builder.set_entry_point("unknown")

# 条件跳转
builder.add_conditional_edges(
    "unknown",
    lambda x: "error" if x.get("error_count", 0) > 0 else END,
    {
        "error": "handle_error",
        END: END
    }
)

# 设置完成点
builder.set_finish_point("unknown")
builder.set_finish_point("handle_error")

cloud_driver_module_graph = builder.compile() 