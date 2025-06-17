from typing import Dict, Any, List, Optional, Callable
from state.state_manager import StateManager
from tools.message_handler import MessageHandler
import logging
import time
from functools import wraps
from dataclasses import dataclass
from datetime import datetime
from tools.tool_context import ToolContext

logger = logging.getLogger(__name__)

def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise
                    logger.warning(f"Retry {retries}/{max_retries} after error: {e}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@dataclass
class ToolContext:
    """工具执行上下文"""
    tool_name: str
    args: Dict[str, Any]
    start_time: float
    end_time: Optional[float] = None
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Any] = None
    error: Optional[Exception] = None

    def complete(self, result: Any = None) -> None:
        """完成工具执行"""
        self.end_time = datetime.now().timestamp()
        self.status = "completed"
        self.result = result

    def fail(self, error: Exception) -> None:
        """标记工具执行失败"""
        self.end_time = datetime.now().timestamp()
        self.status = "failed"
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "tool_name": self.tool_name,
            "args": self.args,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "result": self.result,
            "error": str(self.error) if self.error else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolContext':
        """从字典创建实例"""
        return cls(
            tool_name=data["tool_name"],
            args=data["args"],
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            status=data.get("status", "pending"),
            result=data.get("result"),
            error=Exception(data["error"]) if data.get("error") else None
        )

class ToolExecutor:
    """工具执行器"""
    
    def __init__(self, state_manager: StateManager, message_handler: MessageHandler):
        """初始化"""
        self.state_manager = state_manager
        self.message_handler = message_handler
        self.tools: Dict[str, Any] = {}
        self._register_tools()
    
    def _register_tools(self) -> None:
        """注册工具"""
        # 注册 Selenium 工具
        from tools.selenium_tools import (
            selenium_get,
            selenium_click,
            selenium_sendkeys,
            selenium_get_text,
            selenium_get_attribute,
            selenium_wait_for_element,
            selenium_wait_for_text,
            selenium_wait_for_attribute,
            selenium_wait_for_url,
            selenium_wait_for_title,
            selenium_wait_for_alert,
            selenium_accept_alert,
            selenium_dismiss_alert,
            selenium_get_alert_text,
            selenium_sendkeys_to_alert,
            selenium_get_cookies,
            selenium_add_cookie,
            selenium_delete_cookie,
            selenium_delete_all_cookies,
            selenium_get_screenshot,
            selenium_get_page_source,
            selenium_execute_script,
            selenium_get_window_handles,
            selenium_get_window_handle,
            selenium_switch_to_window,
            selenium_close_window,
            selenium_quit
        )
        
        self.tools.update({
            "selenium_get": selenium_get,
            "selenium_click": selenium_click,
            "selenium_sendkeys": selenium_sendkeys,
            "selenium_get_text": selenium_get_text,
            "selenium_get_attribute": selenium_get_attribute,
            "selenium_wait_for_element": selenium_wait_for_element,
            "selenium_wait_for_text": selenium_wait_for_text,
            "selenium_wait_for_attribute": selenium_wait_for_attribute,
            "selenium_wait_for_url": selenium_wait_for_url,
            "selenium_wait_for_title": selenium_wait_for_title,
            "selenium_wait_for_alert": selenium_wait_for_alert,
            "selenium_accept_alert": selenium_accept_alert,
            "selenium_dismiss_alert": selenium_dismiss_alert,
            "selenium_get_alert_text": selenium_get_alert_text,
            "selenium_sendkeys_to_alert": selenium_sendkeys_to_alert,
            "selenium_get_cookies": selenium_get_cookies,
            "selenium_add_cookie": selenium_add_cookie,
            "selenium_delete_cookie": selenium_delete_cookie,
            "selenium_delete_all_cookies": selenium_delete_all_cookies,
            "selenium_get_screenshot": selenium_get_screenshot,
            "selenium_get_page_source": selenium_get_page_source,
            "selenium_execute_script": selenium_execute_script,
            "selenium_get_window_handles": selenium_get_window_handles,
            "selenium_get_window_handle": selenium_get_window_handle,
            "selenium_switch_to_window": selenium_switch_to_window,
            "selenium_close_window": selenium_close_window,
            "selenium_quit": selenium_quit
        })
    
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        
        # 创建工具上下文
        tool_context = ToolContext(
            tool_name=tool_name,
            args=args,
            start_time=time.time()
        )
        
        try:
            # 更新状态
            state = self.state_manager.get_state()
            state["current_tool"] = tool_context.to_dict()
            self.state_manager.update(state)
            
            # 执行工具
            result = self.tools[tool_name](**args)
            
            # 完成工具执行
            tool_context.complete(result)
            state = self.state_manager.get_state()
            state["current_tool"] = tool_context.to_dict()
            self.state_manager.update(state)
            
            return result
            
        except Exception as e:
            # 记录工具执行失败
            tool_context.fail(e)
            state = self.state_manager.get_state()
            state["current_tool"] = tool_context.to_dict()
            self.state_manager.update(state)
            
            # 记录错误
            self.state_manager.record_error(e, {
                "tool_name": tool_name,
                "args": args,
                "tool_context": tool_context.to_dict()
            })
            
            raise
    
    def get_all_tools_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有工具状态"""
        status = {}
        for tool_name in self.tools:
            status[tool_name] = {
                "total_executions": 0,
                "success_count": 0,
                "failure_count": 0,
                "last_execution": None,
                "last_error": None
            }
        return status 