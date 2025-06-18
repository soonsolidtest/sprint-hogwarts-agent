from dataclasses import dataclass
from typing import Dict, Any, Optional
import time

@dataclass
class ToolContext:
    """工具执行上下文"""
    tool_name: str
    args: Dict[str, Any]
    start_time: float
    end_time: Optional[float] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "tool_name": self.tool_name,
            "args": self.args,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "result": self.result,
            "retry_count": self.retry_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolContext":
        """从字典创建实例"""
        return cls(**data)
    
    def complete(self, result: Dict[str, Any]) -> None:
        """完成工具执行"""
        self.end_time = time.time()
        self.status = result.get("status", "unknown")
        self.result = result
    
    def fail(self, error: Exception) -> None:
        """记录工具执行失败"""
        self.end_time = time.time()
        self.status = "failed"
        self.result = {
            "error": str(error),
            "type": error.__class__.__name__
        }
        self.retry_count += 1 