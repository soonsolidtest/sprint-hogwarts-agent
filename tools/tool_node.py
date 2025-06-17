from typing import Dict, Any, List
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage
from state.types import MessagesState
from web_tools.web_toolkit import (
    selenium_get,
    selenium_sendkeys,
    selenium_click,
    selenium_wait_for_element,
    selenium_quit,
    PrintJobTool,
    auto_login,
    login_with_credentials,
    get_page_structure,
    get_page_structure,
    get_driver
)
from tools.action_parser import parse_action, create_tool_message
from tools.should_continue import should_continue
import json
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 注册工具
TOOLS = [
    selenium_get,
    selenium_sendkeys,
    selenium_click,
    selenium_wait_for_element,
    selenium_quit,
    PrintJobTool(),
    auto_login,
    login_with_credentials,
    get_page_structure
]

# 使用函数名作为工具名称
TOOLS_BY_NAME = {
    "selenium_get": selenium_get,
    "selenium_sendkeys": selenium_sendkeys,
    "selenium_click": selenium_click,
    "selenium_wait_for_element": selenium_wait_for_element,
    "selenium_quit": selenium_quit,
    "print_job": PrintJobTool(),
    "auto_login": auto_login,
    "login_with_credentials": login_with_credentials,
    "get_page_structure": get_page_structure
}

def invoke_tool(tool_name: str, tool_args: dict) -> dict:
    """调用工具并处理参数格式"""
    tool = TOOLS_BY_NAME.get(tool_name)
    if not tool:
        raise ValueError(f"未知工具: {tool_name}")
    
    # 处理 action_input 格式的参数
    if "action_input" in tool_args:
        tool_args = tool_args["action_input"]
    
    logger.info(f"🔧 调用工具 {tool_name}，参数: {tool_args}")
    
    try:
        # 确保浏览器已初始化
        driver = get_driver()
        if not driver:
            raise Exception("无法初始化浏览器")
        
        # 使用 invoke 方法调用工具
        if hasattr(tool, 'invoke'):
            result = tool.invoke(tool_args)
        else:
            result = tool(**tool_args)
        logger.info(f"✅ 工具执行成功: {result}")
        return result
    except Exception as e:
        logger.error(f"❌ 工具调用失败: {e}")
        raise e

logger.info(f"🔧 已注册工具: {list(TOOLS_BY_NAME.keys())}")

def tool_node(state: MessagesState) -> dict:
    """执行工具调用"""
    logger.info("📍 开始执行工具调用")
    
    last_msg = state["messages"][-1]
    results = []
    
    # 解析消息内容中的动作
    content = last_msg.content
    
    # 查找动作块
    start = content.find('```')
    if start != -1:
        end = content.find('```', start + 3)
        if end != -1:
            action_str = content[start + 3:end].strip()
            
            # 移除 "json" 标记
            if action_str.startswith('json'):
                action_str = action_str[4:].strip()
            
            # 解析动作
            tool_call = parse_action(action_str)
            if tool_call:
                tool_name = tool_call["name"]
                args = tool_call["args"]
                tool_call_id = tool_call["id"]
                
                logger.info(f"🔧 执行工具: {tool_name}")
                
                tool = TOOLS_BY_NAME.get(tool_name)
                if not tool:
                    logger.error(f"❌ 未知工具: {tool_name}")
                    results.append(ToolMessage(content=f"[未知工具]: {tool_name}", tool_call_id=tool_call_id))
            else:
                try:
                        obs = tool(**args)  # 使用解包参数的方式调用工具
                        logger.info(f"✅ 工具执行成功")
                        results.append(create_tool_message(obs, tool_call_id))
                except Exception as e:
                        logger.error(f"❌ 工具执行失败: {e}")
                        results.append(ToolMessage(content=f"[工具执行失败]: {e}", tool_call_id=tool_call_id))
    else:
        logger.warning("⚠️ 未找到动作块")
    
    new_state = {
        **state,
        "messages": state["messages"] + results
    }
    return new_state

def handle_confirmation(state: Dict[str, Any]) -> Dict[str, Any]:
    """处理用户确认"""
    messages = state.get("messages", [])
    if not messages:
        return state
    
    last_message = messages[-1]
    if not isinstance(last_message, HumanMessage):
        return state
    
    user_input = last_message.content.lower().strip()
    if user_input == "y":
        # 继续执行
        if state.get("last_failed_tool"):
            # 重试失败的工具
            tool_info = state["last_failed_tool"]
            messages.append(AIMessage(content=f"重试工具 {tool_info['name']}"))
            state["last_failed_tool"] = None
        else:
            # 继续下一步
            messages.append(AIMessage(content="继续执行下一步"))
        state["waiting_for_confirmation"] = False
    elif user_input == "n":
        # 停止执行
        messages.append(AIMessage(content="用户选择停止执行"))
        state["should_stop"] = True
    else:
        # 无效输入
        messages.append(AIMessage(content="请输入 y 或 n"))
    
    state["messages"] = messages
    return state
