# 快速入门指南

## 迁移后主要变化

### 1. 工具函数调用方式

**迁移前：**
```python
# 直接调用函数
result = smart_click("提交")
```

**迁移后：**
```python
# 直接导入调用（推荐）
from web_tools import smart_click
result = smart_click("提交")

# 或者通过图调用工具
from graphs.main_graph import main_graph
state = {
    "messages": [HumanMessage(content="点击提交按钮")],
    "input": "点击提交按钮"
}
result = main_graph.invoke(state)
```

### 2. 图调用方式

**基本调用：**
```python
from graphs.main_graph import main_graph
from langchain_core.messages import HumanMessage

# 创建状态
state = {
    "messages": [HumanMessage(content="你的指令")],
    "input": "你的指令",
    "rayware_intent": "",
    "module": "",
    "test_config": {}
}

# 调用图
result = main_graph.invoke(state)
```

**使用 MainGraph 类：**
```python
from graphs.main_graph import MainGraph

# 创建主图实例
main_graph_instance = MainGraph()

# 处理状态
result = main_graph_instance.process(state)
```

## 常用图调用示例

### 1. 自动登录
```python
from graphs.main_graph import main_graph
from langchain_core.messages import HumanMessage

state = {
    "messages": [HumanMessage(content="登录系统")],
    "input": "登录系统",
    "rayware_intent": "",
    "module": "",
    "test_config": {
        "username": "your_username",
        "password": "your_password"
    }
}

result = main_graph.invoke(state)
```

### 2. 创建打印任务
```python
state = {
    "messages": [HumanMessage(content="新建打印任务")],
    "input": "新建打印任务",
    "rayware_intent": "",
    "module": "",
    "test_config": {
        "patient_name": "张三",
        "indication": "感冒",
        "medication": "阿莫西林",
        "dosage": "0.5g",
        "frequency": "每日3次"
    }
}

result = main_graph.invoke(state)
```

### 3. 智能点击
```python
from web_tools import smart_click

# 直接调用工具函数
result = smart_click("提交按钮")
```

### 4. Selenium 操作
```python
from web_tools import selenium_click, selenium_set

# 直接调用工具函数
result = selenium_click("#submit-button")
result = selenium_set("#username", "test_user")
```

## 新建工具步骤

### 1. 创建工具文件
```python
# web_tools/my_tool.py
from typing import Dict, Any

def my_custom_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """自定义工具"""
    try:
        # 获取参数
        param1 = params.get("param1")
        
        # 执行逻辑
        result = do_something(param1)
        
        return {
            "success": True,
            "result": result,
            "message": "操作成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 2. 注册工具
在 `web_tools/__init__.py` 中添加：
```python
from .my_tool import my_custom_tool

__all__ = [
    # ... 现有工具
    "my_custom_tool"
]
```

### 3. 在图中使用
```python
# 在 main_graph.py 中添加工具调用逻辑
def custom_tool_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """自定义工具节点"""
    from web_tools import my_custom_tool
    
    # 调用工具
    result = my_custom_tool({
        "param1": "value1"
    })
    
    # 添加结果到消息
    state["messages"].append(AIMessage(content=f"工具执行结果: {result}"))
    return state
```

## 常用工具函数

### 基础 Selenium 操作
```python
from web_tools import selenium_click, selenium_set, selenium_get

# 点击元素
selenium_click("#button")

# 设置值
selenium_set("#input", "value")

# 获取值
text = selenium_get("#element")
```

### 智能操作
```python
from web_tools import smart_click, smart_select_and_choose

# 智能点击
smart_click("按钮文本")

# 智能选择
smart_select_and_choose("下拉框文本", "选项文本")
```

### 登录工具
```python
from web_tools import auto_login

# 自动登录
auto_login({
    "username": "user",
    "password": "pass"
})
```

### 打印任务工具
```python
from web_tools import create_new_print_job, select_printer, submit_print_job

# 创建打印任务
create_new_print_job({
    "patient_name": "患者名",
    "indication": "适应症",
    "medication": "药品"
})
```

## 运行方式

### 1. 交互式运行
```bash
python agent_runner_new.py
```

### 2. 直接调用图
```python
from graphs.main_graph import main_graph
from langchain_core.messages import HumanMessage

state = {
    "messages": [HumanMessage(content="你的指令")],
    "input": "你的指令",
    "rayware_intent": "",
    "module": "",
    "test_config": {}
}

result = main_graph.invoke(state)
```

### 3. 使用 MainGraph 类
```python
from graphs.main_graph import MainGraph

main_graph_instance = MainGraph()
result = main_graph_instance.process(state)
```

## 调试技巧

### 1. 启用详细日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 检查工具注册
```python
from web_tools import __all__
print(__all__)  # 查看所有可用工具
```

### 3. 参数验证
```python
# 检查参数格式
params = {
    "param1": "value1"  # 确保参数正确
}
```

### 4. 错误处理
```python
try:
    result = main_graph.invoke(state)
    print("成功")
except Exception as e:
    print(f"异常: {e}")
```

## 常见问题解决

### 1. 工具调用失败
- 检查工具是否正确注册
- 验证参数格式
- 查看错误日志

### 2. 图执行失败
- 检查图定义
- 验证节点配置
- 确认工具存在

### 3. Selenium 问题
- 检查元素是否存在
- 等待页面加载
- 验证选择器

## 下一步

1. 查看 `docs/usage_guide.md` 获取详细使用说明
2. 查看 `docs/practical_usage_examples.md` 获取实际示例
3. 查看 `docs/migration_summary.md` 了解迁移详情
4. 开始编写您的自动化流程！

这个快速入门指南涵盖了迁移后的主要使用方式。如有问题，请参考详细文档或联系技术支持。 