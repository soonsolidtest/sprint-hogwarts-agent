# 迁移后使用指南

## 1. 图调用方式

### 1.1 基本图调用

```python
from agent_runner import AgentRunner

# 创建运行器实例
runner = AgentRunner()

# 调用图
result = runner.run_graph("your_graph_name", {
    "param1": "value1",
    "param2": "value2"
})
```

### 1.2 带配置的图调用

```python
from agent_runner import AgentRunner

# 创建运行器实例
runner = AgentRunner()

# 调用图并传入配置
result = runner.run_graph("your_graph_name", {
    "param1": "value1",
    "param2": "value2"
}, config={
    "max_iterations": 10,
    "timeout": 300
})
```

### 1.3 异步图调用

```python
import asyncio
from agent_runner import AgentRunner

async def main():
    runner = AgentRunner()
    
    # 异步调用图
    result = await runner.run_graph_async("your_graph_name", {
        "param1": "value1",
        "param2": "value2"
    })
    
    print(result)

# 运行异步函数
asyncio.run(main())
```

### 1.4 图调用示例

```python
# 调用自动登录图
result = runner.run_graph("auto_login", {
    "username": "your_username",
    "password": "your_password"
})

# 调用创建打印任务图
result = runner.run_graph("create_print_job", {
    "patient_name": "张三",
    "indication": "感冒",
    "medication": "阿莫西林"
})
```

## 2. 新建工具编写指南

### 2.1 工具函数基本结构

```python
from typing import Dict, Any
from web_tools.base_tool import BaseTool

class MyCustomTool(BaseTool):
    """自定义工具类"""
    
    def __init__(self):
        super().__init__()
        self.name = "my_custom_tool"
        self.description = "这是一个自定义工具的描述"
    
    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        工具的主要执行逻辑
        
        Args:
            params: 输入参数字典
            
        Returns:
            执行结果字典
        """
        try:
            # 获取参数
            param1 = params.get("param1")
            param2 = params.get("param2")
            
            # 执行具体逻辑
            result = self._do_something(param1, param2)
            
            return {
                "success": True,
                "result": result,
                "message": "操作成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "操作失败"
            }
    
    def _do_something(self, param1, param2):
        """具体的业务逻辑"""
        # 实现你的具体功能
        pass
```

### 2.2 Selenium 工具编写

```python
from typing import Dict, Any
from web_tools.selenium_tool import SeleniumTool

class MySeleniumTool(SeleniumTool):
    """Selenium 相关工具"""
    
    def __init__(self):
        super().__init__()
        self.name = "my_selenium_tool"
        self.description = "Selenium 操作工具"
    
    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 获取参数
            selector = params.get("selector")
            action = params.get("action", "click")
            
            # 执行 Selenium 操作
            if action == "click":
                result = self.selenium_click(selector)
            elif action == "set":
                value = params.get("value")
                result = self.selenium_set(selector, value)
            elif action == "get":
                result = self.selenium_get(selector)
            else:
                raise ValueError(f"不支持的操作: {action}")
            
            return {
                "success": True,
                "result": result,
                "message": f"{action} 操作成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Selenium 操作失败"
            }
```

### 2.3 智能工具编写

```python
from typing import Dict, Any
from web_tools.smart_tool import SmartTool

class MySmartTool(SmartTool):
    """智能工具类"""
    
    def __init__(self):
        super().__init__()
        self.name = "my_smart_tool"
        self.description = "智能操作工具"
    
    def invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 获取参数
            text = params.get("text")
            action = params.get("action", "click")
            
            # 执行智能操作
            if action == "click":
                result = self.smart_click(text)
            elif action == "set":
                value = params.get("value")
                result = self.smart_set(text, value)
            elif action == "get":
                result = self.smart_get(text)
            else:
                raise ValueError(f"不支持的操作: {action}")
            
            return {
                "success": True,
                "result": result,
                "message": f"智能 {action} 操作成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "智能操作失败"
            }
```

### 2.4 工具注册

在 `web_tools/__init__.py` 中注册新工具：

```python
from .my_custom_tool import MyCustomTool
from .my_selenium_tool import MySeleniumTool
from .my_smart_tool import MySmartTool

# 注册工具
TOOLS = {
    "my_custom_tool": MyCustomTool(),
    "my_selenium_tool": MySeleniumTool(),
    "my_smart_tool": MySmartTool(),
    # ... 其他工具
}
```

### 2.5 工具使用示例

```python
# 在图中使用新工具
{
    "name": "使用自定义工具",
    "tool": "my_custom_tool",
    "params": {
        "param1": "value1",
        "param2": "value2"
    }
}

# 在图中使用 Selenium 工具
{
    "name": "点击按钮",
    "tool": "my_selenium_tool",
    "params": {
        "selector": "#submit-button",
        "action": "click"
    }
}

# 在图中使用智能工具
{
    "name": "智能点击",
    "tool": "my_smart_tool",
    "params": {
        "text": "提交",
        "action": "click"
    }
}
```

## 3. 图定义示例

### 3.1 基本图结构

```python
# 图定义
graph = {
    "name": "my_graph",
    "description": "我的自定义图",
    "nodes": [
        {
            "name": "步骤1",
            "tool": "my_custom_tool",
            "params": {
                "param1": "value1"
            }
        },
        {
            "name": "步骤2",
            "tool": "my_selenium_tool",
            "params": {
                "selector": "#button",
                "action": "click"
            }
        },
        {
            "name": "步骤3",
            "tool": "my_smart_tool",
            "params": {
                "text": "确认",
                "action": "click"
            }
        }
    ]
}
```

### 3.2 条件分支图

```python
graph = {
    "name": "conditional_graph",
    "description": "条件分支图",
    "nodes": [
        {
            "name": "检查状态",
            "tool": "check_status",
            "params": {
                "element": "#status"
            }
        },
        {
            "name": "如果成功",
            "condition": "{{check_status.success}}",
            "tool": "success_action",
            "params": {}
        },
        {
            "name": "如果失败",
            "condition": "{{!check_status.success}}",
            "tool": "error_action",
            "params": {}
        }
    ]
}
```

## 4. 最佳实践

### 4.1 工具编写建议

1. **错误处理**: 始终包含 try-catch 块
2. **参数验证**: 验证必要参数是否存在
3. **返回值**: 使用统一的返回格式
4. **日志记录**: 添加适当的日志信息
5. **文档注释**: 详细描述工具功能和使用方法

### 4.2 图设计建议

1. **模块化**: 将复杂流程拆分为多个小图
2. **可重用**: 设计可重用的图组件
3. **错误处理**: 添加错误处理节点
4. **超时设置**: 为长时间操作设置超时
5. **测试**: 为每个图编写测试用例

### 4.3 调试技巧

1. **启用详细日志**: 设置日志级别为 DEBUG
2. **使用断点**: 在关键节点添加断点
3. **参数检查**: 验证传入参数的正确性
4. **状态检查**: 检查页面元素状态
5. **截图调试**: 在失败时保存截图

## 5. 常见问题

### 5.1 工具调用失败

```python
# 检查工具是否正确注册
from web_tools import TOOLS
print(TOOLS.keys())

# 检查参数格式
params = {
    "param1": "value1"  # 确保参数格式正确
}
```

### 5.2 图执行失败

```python
# 检查图定义
print(graph["nodes"])

# 检查节点配置
for node in graph["nodes"]:
    print(f"节点: {node['name']}")
    print(f"工具: {node['tool']}")
    print(f"参数: {node['params']}")
```

### 5.3 Selenium 相关问题

```python
# 检查元素是否存在
result = selenium_tool.selenium_get("#element-id")
if not result:
    print("元素不存在")

# 等待元素加载
import time
time.sleep(2)  # 等待页面加载
```

这个文档涵盖了迁移后的主要使用方式，包括图调用和工具编写的详细说明。如果您需要更具体的示例或有其他问题，请告诉我！ 