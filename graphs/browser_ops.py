from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from state.types import MessagesState
from tools.llm_call import llm_call
from tools.should_continue import should_continue
from web_tools.web_toolkit import (
    smart_select_open,
    smart_select_and_choose,
    selenium_click,
    selenium_sendkeys,
    selenium_wait_for_element,
    selenium_quit
)

# 定义浏览器操作状态
class BrowserState(TypedDict):
    messages: list
    url: str
    username: str
    password: str
    browser_opened: bool
    logged_in: bool
    current_page: str

# 构建工具列表
BROWSER_TOOLS = [
    smart_select_open,
    smart_select_and_choose,
    selenium_click,
    selenium_sendkeys,
    selenium_wait_for_element,
    selenium_quit,
]

tool_node = ToolNode(BROWSER_TOOLS)

def init_browser_state(state: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(state, dict):
        state = {}
    # 尝试从外层state获取test_config
    if "test_config" not in state or not state["test_config"]:
        # 兼容外层state
        import copy
        if "_parent_state" in state and "test_config" in state["_parent_state"]:
            state["test_config"] = copy.deepcopy(state["_parent_state"]["test_config"])
        else:
            state["test_config"] = {}
    state.setdefault("browser_opened", False)
    state.setdefault("logged_in", False)
    state.setdefault("current_page", "")
    return state

def mock_browser_ops(state: Dict[str, Any]) -> Dict[str, Any]:
    """模拟浏览器操作"""
    print(f"[mock_browser_ops] test_config: {state.get('test_config', {})}")
    
    # 获取配置信息
    test_config = state.get("test_config", {})
    url = test_config.get("url", "")
    username = test_config.get("username", "")
    
    # 模拟浏览器操作
    if not state.get("browser_opened"):
        print(f"Mock打开浏览器，访问URL: {url}")
        state["browser_opened"] = True
        state["current_page"] = "login"
    
    if state.get("browser_opened") and not state.get("logged_in"):
        print(f"Mock登录，用户名: {username}")
        state["logged_in"] = True
        state["current_page"] = "dashboard"
    
    return state

def check_browser_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """检查浏览器状态"""
    print(f"[check_browser_state] 输入state: {state}")
    
    # 确保test_config存在
    if "test_config" not in state:
        state["test_config"] = {}
    
    # 执行mock浏览器操作
    state = mock_browser_ops(state)
    print(f"[check_browser_state] mock后state: {state}")
    
    # 检查浏览器状态
    if state.get("browser_opened") and state.get("logged_in"):
        print("浏览器已准备就绪")
        return {"next": "ready", "state": state}
    else:
        return {"next": "check_state", "state": state}

def handle_browser_error(state: Dict[str, Any]) -> Dict[str, Any]:
    """处理浏览器操作错误"""
    messages = state.get("messages", [])
    messages.append({
        "role": "assistant",
        "content": "浏览器操作遇到问题，请检查网络连接和浏览器状态。"
    })
    return {"messages": messages, "browser_opened": False, "logged_in": False}

def tools(state: dict) -> dict:
    print("进入tools占位节点，直接返回state")
    return {"next": "check_state", "state": state}

# 构建浏览器操作图
builder = StateGraph(MessagesState)

# 添加节点
builder.add_node("llm_call", llm_call)
# builder.add_node("tools", tools)  # 移除tools节点
builder.add_node("check_state", check_browser_state)
builder.add_node("handle_error", handle_browser_error)

# 设置入口点
builder.set_entry_point("check_state")

# 添加条件边
builder.add_conditional_edges(
    "check_state",
    lambda x: x["next"],
    {
        "error": "handle_error",
        "open_browser": "llm_call",
        "login": "llm_call",
        "navigate": "llm_call",
        "ready": END,
        "check_state": "check_state"
    }
)

builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "Action": "check_state",
        END: END
    }
)

# builder.add_edge("tools", "check_state")  # 移除与tools相关的边
builder.add_edge("handle_error", "llm_call")

builder.set_finish_point("check_state")

browser_ops_graph = builder.compile() 