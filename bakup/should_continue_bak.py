from langchain_core.messages import ToolMessage
from typing import Literal
from state.types import MessagesState

END = "__end__"

def should_continue(state: MessagesState) -> Literal["Action", END]:
    last_message = state["messages"][-1]
    print(last_message)

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call_names = [tc["name"] for tc in last_message.tool_calls]
        if "selenium_quit" in tool_call_names:
            print("[should_continue] 检测到 selenium_quit，流程终止")
            return END
        print("[should_continue] continue (tool call)")
        return "Action"

    if isinstance(last_message, ToolMessage):
        print("[should_continue] continue (tool message)")
        return "Action"

    if hasattr(last_message, "additional_kwargs"):
        if last_message.additional_kwargs.get("failed", False):
            print("[should_continue] 检测到失败标志，流程终止")
            return END

    if hasattr(last_message, "content"):
        if "登录失败" in last_message.content or "等待超时" in last_message.content:
            print("[should_continue] 检测到失败内容，流程终止")
            return END

    print("[should_continue] 默认终止")
    return END
