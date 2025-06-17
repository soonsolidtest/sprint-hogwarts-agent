from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import time
import logging
import json

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ErrorRecord:
    """错误记录"""
    time: float
    error: str
    context: Dict[str, Any]
    retry_count: int = 0

@dataclass
class State:
    """状态数据类"""
    messages: List[Any] = None
    rayware_intent: str = ""       # Rayware意图
    input: str = ""               # 用户输入
    module: str = ""              # 当前模块
    test_config: Dict[str, Any] = None  # 测试配置
    error_count: int = 0          # 错误计数
    last_error: str = ""          # 最后一次错误
    collected_fields: set = None   # 已收集的字段
    should_stop: bool = False      # 是否停止
    waiting_for_confirmation: bool = False  # 是否等待确认
    browser_opened: bool = False   # 浏览器是否打开
    logged_in: bool = False       # 是否已登录
    current_page: str = ""        # 当前页面
    last_user_interaction: float = 0.0  # 最后用户交互时间
    interaction_timeout: int = 300  # 交互超时时间（5分钟）
    current_tool: Optional[Dict[str, Any]] = None  # 当前工具
    print_job_data: Dict[str, Any] = None  # 打印任务数据
    
    def __post_init__(self):
        """初始化后处理"""
        if self.messages is None:
            self.messages = []
        if self.collected_fields is None:
            self.collected_fields = set()
        if self.test_config is None:
            self.test_config = {}
        if self.print_job_data is None:
            self.print_job_data = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        state_dict = asdict(self)
        # 转换 set 为 list
        state_dict["collected_fields"] = list(self.collected_fields)
        return state_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "State":
        """从字典创建状态"""
        # 转换 list 为 set
        if "collected_fields" in data:
            data["collected_fields"] = set(data["collected_fields"])
        return cls(**data)

class StateManager:
    """状态管理器"""
    
    def __init__(self):
        """初始化"""
        self._state = State()
        self._history: List[State] = []
        self._max_history = 10
    
    def update(self, new_state: Dict[str, Any]) -> None:
        """更新状态"""
        # 保存当前状态到历史
        self._history.append(self._state)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        
        # 更新状态
        self._state = State.from_dict(new_state)
        logger.debug(f"State updated: {json.dumps(self._state.to_dict(), default=str)}")
    
    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return self._state.to_dict()
    
    def rollback(self) -> None:
        """回滚到上一个状态"""
        if self._history:
            self._state = self._history.pop()
            logger.info("State rolled back to previous state")
    
    def check_user_interaction_timeout(self) -> bool:
        """检查用户交互是否超时"""
        if not self._state.last_user_interaction:
            return False
        
        elapsed = time.time() - self._state.last_user_interaction
        if elapsed > self._state.interaction_timeout:
            logger.warning(f"User interaction timeout after {elapsed:.1f} seconds")
            return True
        
        return False
    
    def record_error(self, error: Exception, context: Dict[str, Any]) -> None:
        """记录错误"""
        error_info = {
            "type": error.__class__.__name__,
            "message": str(error),
            "context": context,
            "timestamp": time.time()
        }
        self._state.last_error = str(error)
        self._state.error_count += 1
        logger.error(f"Error recorded: {json.dumps(error_info, default=str)}")
    
    def clear_error(self) -> None:
        """清除错误"""
        self._state.last_error = ""
        logger.info("Error cleared")
    
    def get_error(self) -> Optional[str]:
        """获取错误信息"""
        return self._state.last_error
    
    def should_retry(self, error: Exception) -> bool:
        """检查是否应该重试"""
        if not self._state.last_error:
            return True
        
        if time.time() - self._state.last_user_interaction > 300:  # 5分钟内的错误
            return False
        
        return self._state.error_count < 3  # 最多重试3次
    
    def update_user_interaction(self) -> None:
        """更新用户交互时间"""
        self._state.last_user_interaction = time.time() 