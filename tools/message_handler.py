from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage
from state.state_manager import StateManager
import logging

logger = logging.getLogger(__name__)

class MessageHandler:
    """消息处理器"""
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
    
    def process_message(self, message: BaseMessage) -> Dict[str, Any]:
        """处理消息"""
        try:
            if isinstance(message, HumanMessage):
                return self._handle_human_message(message)
            elif isinstance(message, AIMessage):
                return self._handle_ai_message(message)
            elif isinstance(message, ToolMessage):
                return self._handle_tool_message(message)
            else:
                logger.warning(f"Unknown message type: {type(message)}")
                return self.state_manager.get_state()
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self.state_manager.record_error(e, {"message": str(message)})
            return self._handle_error(e)
    
    def _handle_human_message(self, message: HumanMessage) -> Dict[str, Any]:
        """处理用户消息"""
        # 更新用户交互时间
        self.state_manager.update_user_interaction()
        
        # 获取当前状态
        state = self.state_manager.get_state()
        
        # 如果正在等待确认
        if state.get("waiting_for_confirmation"):
            return self._handle_confirmation(message.content)
        
        # 添加消息到历史（避免重复）
        if not state["messages"] or state["messages"][-1] != message:
            state["messages"].append(message)
        
        self.state_manager.update(state)
        return state
    
    def _handle_ai_message(self, message: AIMessage) -> Dict[str, Any]:
        """处理AI消息"""
        state = self.state_manager.get_state()
        
        # 检查工具调用
        if hasattr(message, "tool_calls") and message.tool_calls:
            # 记录工具调用
            tool_call = message.tool_calls[0]
            if isinstance(tool_call, dict):
                self.state_manager.record_tool_execution(
                    tool_name=tool_call.get("name"),
                    args=tool_call.get("args", {})
                )
        
        # 添加消息到历史（避免重复）
        if not state["messages"] or state["messages"][-1] != message:
            state["messages"].append(message)
        
        self.state_manager.update(state)
        return state
    
    def _handle_tool_message(self, message: ToolMessage) -> Dict[str, Any]:
        """处理工具消息"""
        state = self.state_manager.get_state()
        
        try:
            # 解析工具消息内容
            content = message.content
            if isinstance(content, str):
                try:
                    import json
                    content = json.loads(content)
                except:
                    content = {"status": "success", "message": content}
            
            # 完成工具执行记录
            current_tool = state.get("current_tool")
            if current_tool:
                self.state_manager.complete_tool_execution(content)
            
            # 添加消息到历史（避免重复）
            if not state["messages"] or state["messages"][-1] != message:
                state["messages"].append(message)
            
            # 检查是否需要用户确认
            if current_tool and current_tool.tool_name in ["selenium_click", "selenium_sendkeys"]:
                state["waiting_for_confirmation"] = True
                state["messages"].append(AIMessage(
                    content=f"工具 {current_tool.tool_name} 执行{'成功' if content.get('status') == 'success' else '失败'}，是否继续？(y/n)"
                ))
            
            self.state_manager.update(state)
            return state
            
        except Exception as e:
            logger.error(f"Error handling tool message: {e}")
            self.state_manager.record_error(e, {"message": str(message)})
            return self._handle_error(e)
    
    def _handle_confirmation(self, content: str) -> Dict[str, Any]:
        """处理用户确认"""
        state = self.state_manager.get_state()
        content = content.lower().strip()
        
        if content == "y":
            # 继续执行
            if state.get("last_failed_tool"):
                # 重试失败的工具
                tool_info = state["last_failed_tool"]
                state["messages"].append(AIMessage(content=f"重试工具 {tool_info['name']}"))
                state["last_failed_tool"] = None
            else:
                # 继续下一步
                state["messages"].append(AIMessage(content="继续执行下一步"))
            state["waiting_for_confirmation"] = False
        elif content == "n":
            # 停止执行
            state["messages"].append(AIMessage(content="用户选择停止执行"))
            state["should_stop"] = True
        else:
            # 无效输入
            state["messages"].append(AIMessage(content="请输入 y 或 n"))
        
        self.state_manager.update(state)
        return state
    
    def _handle_error(self, error: Exception) -> Dict[str, Any]:
        """处理错误"""
        state = self.state_manager.get_state()
        
        # 检查是否应该重试
        if self.state_manager.should_retry(error):
            state["messages"].append(AIMessage(content=f"发生错误: {str(error)}，是否重试？(y/n)"))
            state["waiting_for_confirmation"] = True
            if state.get("current_tool"):
                state["last_failed_tool"] = {
                    "name": state["current_tool"].tool_name,
                    "args": state["current_tool"].args
                }
        else:
            state["messages"].append(AIMessage(content=f"发生错误: {str(error)}，无法继续执行"))
            state["should_stop"] = True
        
        self.state_manager.update(state)
        return state
    
    def validate_message(self, message: BaseMessage) -> bool:
        """验证消息"""
        if not message:
            return False
        
        if isinstance(message, HumanMessage):
            return bool(message.content.strip())
        elif isinstance(message, AIMessage):
            return bool(message.content.strip()) or bool(message.tool_calls)
        elif isinstance(message, ToolMessage):
            return bool(message.content.strip())
        
        return False
    
    def filter_messages(self, messages: List[BaseMessage], max_history: int = 10) -> List[BaseMessage]:
        """过滤消息历史"""
        if not messages:
            return []
        
        # 保留最近的N条消息
        recent_messages = messages[-max_history:]
        
        # 过滤掉空消息
        return [msg for msg in recent_messages if self.validate_message(msg)] 