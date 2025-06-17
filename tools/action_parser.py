from typing import Dict, Any, Optional
from langchain_core.messages import ToolMessage
import json
import logging

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def parse_action(action_str: str) -> Optional[Dict[str, Any]]:
    """解析动作字符串为工具调用"""
    try:
        # 尝试解析 JSON
        action = json.loads(action_str)
        
        # 检查必要字段
        if "action" not in action or "action_input" not in action:
            logger.warning("动作格式不正确，缺少必要字段")
            return None
        
        # 构建工具调用
        tool_call = {
            "id": f"call_{hash(action_str)}",
            "name": action["action"],
            "args": action["action_input"]
        }
        
        logger.info(f"✅ 动作解析成功: {action['action']}")
        return tool_call
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ 动作解析失败: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ 解析过程中发生错误: {e}")
        return None

def create_tool_message(result: Any, tool_call_id: str) -> ToolMessage:
    """创建工具消息"""
    try:
        # 确保结果是字符串格式
        if isinstance(result, dict):
            content = json.dumps(result, ensure_ascii=False)
        else:
            content = str(result)
        
        return ToolMessage(content=content, tool_call_id=tool_call_id)
        
    except Exception as e:
        logger.error(f"❌ 创建工具消息失败: {e}")
        return ToolMessage(content=f"工具消息创建失败: {str(e)}", tool_call_id=tool_call_id) 