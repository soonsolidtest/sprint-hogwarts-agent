# state/types.py
from typing import List, Dict, Any, Set, TypedDict
from langchain_core.messages import BaseMessage

class MessagesState(TypedDict, total=False):
    """状态类型定义 - 使用 TypedDict 以支持 .get() 方法"""
    messages: List[BaseMessage]          # 消息历史
    input: str                          # 用户输入
    rayware_intent: str                 # Rayware意图
    module: str                         # 当前模块
    test_config: Dict[str, Any]         # 测试配置
    error_count: int                    # 错误计数
    last_error: str                     # 最后一次错误
    collected_fields: Set               # 已收集的字段
    # 新增字段
    should_stop: bool                   # 是否应该停止
    waiting_for_confirmation: bool      # 是否等待确认
    current_tool: str                   # 当前工具
    last_failed_tool: str              # 最后失败的工具
    user_input: str                     # 用户输入（别名）
    print_job_data: Dict[str, Any]      # 打印任务数据
    current_page: str                   # 当前页面
    logged_in: bool                     # 是否已登录


