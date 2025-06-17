from typing import Callable, Type
from langchain_core.messages import BaseMessage
from state.types import MessagesState

def manual_append_message(message_type: Type[BaseMessage]) -> Callable[[MessagesState], MessagesState]:
    """创建一个函数来手动添加消息到状态"""
    def append_message(state: MessagesState) -> MessagesState:
        """将消息添加到状态"""
        messages = state.get("messages", [])
        input_text = state.get("input", "")
        
        # 创建新消息
        new_message = message_type(content=input_text)
        
        # 更新状态
        return {
            **state,
            "messages": messages + [new_message]
        }
    
    return append_message 