from typing import Dict, Any, Literal
from langchain_core.messages import AIMessage, ToolMessage

END = "END"

def should_continue(state: Dict[str, Any]) -> Dict[str, Any]:
    """检查是否应该继续执行流程"""
    messages = state.get("messages", [])
    if not messages:
        return state
    
    last_message = messages[-1]
    
    # 如果上一条消息是工具调用
    if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call_names = [tc.get("name") for tc in last_message.tool_calls]
        if "selenium_quit" in tool_call_names:
            print("[should_continue] 检测到 selenium_quit，流程终止")
            state["should_stop"] = True
            return state
        print("[should_continue] continue (tool call)")
        return state

    # 如果上一条是工具的返回消息
    if isinstance(last_message, ToolMessage):
        print("[should_continue] continue (tool message)")
        return state

    # 如果失败标记
    if hasattr(last_message, "additional_kwargs"):
        if last_message.additional_kwargs.get("failed", False):
            print("[should_continue] 检测到失败标志，流程终止")
            state["should_stop"] = True
            return state

    # 如果文本里包含明显失败提示
    if hasattr(last_message, "content"):
        if "登录失败" in last_message.content or "等待超时" in last_message.content:
            print("[should_continue] 检测到失败内容，流程终止")
            state["should_stop"] = True
            return state

    # 默认终止（防止死循环）
    print("[should_continue] 默认终止")
    state["should_stop"] = True
    return state
