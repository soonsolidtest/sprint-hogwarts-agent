# 实用使用示例

## 1. 图调用实际示例

### 1.1 调用自动登录图

```python
from agent_runner import AgentRunner

# 创建运行器
runner = AgentRunner()

# 调用自动登录
result = runner.run_graph("auto_login", {
    "username": "your_username",
    "password": "your_password"
})

print(f"登录结果: {result}")
```

### 1.2 调用创建打印任务图

```python
# 调用创建打印任务
result = runner.run_graph("create_print_job", {
    "patient_name": "张三",
    "indication": "感冒",
    "medication": "阿莫西林胶囊",
    "dosage": "0.5g",
    "frequency": "每日3次"
})

print(f"创建打印任务结果: {result}")
```

### 1.3 调用 Rayware 相关图

```python
# 调用 Rayware 登录
result = runner.run_graph("rayware_login", {
    "username": "rayware_user",
    "password": "rayware_pass"
})

# 调用 Rayware 操作
result = runner.run_graph("rayware_operation", {
    "operation": "create_job",
    "parameters": {
        "job_type": "print",
        "priority": "high"
    }
})
```

## 2. 工具函数直接调用

### 2.1 基础 Selenium 操作

```python
from web_tools import selenium_click, selenium_set, selenium_get

# 点击元素
result = selenium_click("#submit-button")
print(f"点击结果: {result}")

# 设置输入框值
result = selenium_set("#username", "test_user")
print(f"设置值结果: {result}")

# 获取元素文本
result = selenium_get("#status-message")
print(f"获取文本: {result}")
```

### 2.2 智能操作

```python
from web_tools import smart_click, smart_select_and_choose

# 智能点击（通过文本查找）
result = smart_click("提交")
print(f"智能点击结果: {result}")

# 智能选择下拉框
result = smart_select_and_choose("适应症", "感冒")
print(f"智能选择结果: {result}")
```

### 2.3 登录工具

```python
from web_tools import auto_login

# 自动登录
result = auto_login({
    "username": "test_user",
    "password": "test_pass"
})
print(f"自动登录结果: {result}")
```

### 2.4 打印任务工具

```python
from web_tools import create_new_print_job, select_printer, submit_print_job

# 创建新打印任务
result = create_new_print_job({
    "patient_name": "李四",
    "indication": "发烧",
    "medication": "布洛芬",
    "dosage": "0.4g",
    "frequency": "每日2次"
})
print(f"创建打印任务结果: {result}")

# 选择打印机
result = select_printer("HP LaserJet Pro")
print(f"选择打印机结果: {result}")

# 提交打印任务
result = submit_print_job()
print(f"提交打印任务结果: {result}")
```

## 3. 新建工具实际示例

### 3.1 创建自定义页面操作工具

```python
# 在 web_tools/custom_tools.py 中创建
from typing import Dict, Any
from .basic_operations import selenium_click, selenium_set, selenium_get

def custom_page_operation(params: Dict[str, Any]) -> Dict[str, Any]:
    """自定义页面操作工具"""
    try:
        operation = params.get("operation")
        
        if operation == "fill_form":
            # 填写表单
            selenium_set("#name", params.get("name", ""))
            selenium_set("#email", params.get("email", ""))
            selenium_set("#phone", params.get("phone", ""))
            
            return {
                "success": True,
                "message": "表单填写成功"
            }
            
        elif operation == "submit_form":
            # 提交表单
            result = selenium_click("#submit")
            
            return {
                "success": True,
                "message": "表单提交成功",
                "result": result
            }
            
        elif operation == "check_status":
            # 检查状态
            status = selenium_get("#status")
            
            return {
                "success": True,
                "status": status,
                "message": "状态检查完成"
            }
            
        else:
            return {
                "success": False,
                "error": f"不支持的操作: {operation}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 3.2 创建数据验证工具

```python
# 在 web_tools/validation_tools.py 中创建
from typing import Dict, Any
from .basic_operations import selenium_get

def validate_page_data(params: Dict[str, Any]) -> Dict[str, Any]:
    """页面数据验证工具"""
    try:
        validation_type = params.get("type")
        
        if validation_type == "patient_info":
            # 验证患者信息
            name = selenium_get("#patient-name")
            age = selenium_get("#patient-age")
            gender = selenium_get("#patient-gender")
            
            # 验证逻辑
            if not name or name.strip() == "":
                return {
                    "success": False,
                    "error": "患者姓名不能为空"
                }
            
            if not age or not age.isdigit():
                return {
                    "success": False,
                    "error": "患者年龄格式不正确"
                }
            
            return {
                "success": True,
                "data": {
                    "name": name,
                    "age": age,
                    "gender": gender
                },
                "message": "患者信息验证通过"
            }
            
        elif validation_type == "medication_info":
            # 验证药品信息
            medication = selenium_get("#medication-name")
            dosage = selenium_get("#dosage")
            
            if not medication:
                return {
                    "success": False,
                    "error": "药品名称不能为空"
                }
            
            return {
                "success": True,
                "data": {
                    "medication": medication,
                    "dosage": dosage
                },
                "message": "药品信息验证通过"
            }
            
        else:
            return {
                "success": False,
                "error": f"不支持的验证类型: {validation_type}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### 3.3 注册新工具

在 `web_tools/__init__.py` 中添加：

```python
from .custom_tools import custom_page_operation
from .validation_tools import validate_page_data

# 添加到 __all__ 列表
__all__ = [
    # ... 现有工具
    "custom_page_operation",
    "validate_page_data"
]
```

## 4. 图定义实际示例

### 4.1 完整的打印任务创建图

```python
# 在 graphs/print_job_graph.py 中定义
print_job_graph = {
    "name": "create_print_job",
    "description": "创建打印任务完整流程",
    "nodes": [
        {
            "name": "验证患者信息",
            "tool": "validate_page_data",
            "params": {
                "type": "patient_info"
            }
        },
        {
            "name": "填写患者信息",
            "tool": "custom_page_operation",
            "params": {
                "operation": "fill_form",
                "name": "{{patient_name}}",
                "age": "{{patient_age}}",
                "gender": "{{patient_gender}}"
            }
        },
        {
            "name": "选择适应症",
            "tool": "smart_select_and_choose",
            "params": {
                "text": "适应症",
                "choice": "{{indication}}"
            }
        },
        {
            "name": "填写药品信息",
            "tool": "custom_page_operation",
            "params": {
                "operation": "fill_medication",
                "medication": "{{medication}}",
                "dosage": "{{dosage}}",
                "frequency": "{{frequency}}"
            }
        },
        {
            "name": "验证药品信息",
            "tool": "validate_page_data",
            "params": {
                "type": "medication_info"
            }
        },
        {
            "name": "提交打印任务",
            "tool": "submit_print_job",
            "params": {}
        }
    ]
}
```

### 4.2 条件分支图示例

```python
# 在 graphs/conditional_graph.py 中定义
conditional_graph = {
    "name": "smart_workflow",
    "description": "智能工作流程",
    "nodes": [
        {
            "name": "检查登录状态",
            "tool": "check_login_status",
            "params": {}
        },
        {
            "name": "如果未登录则登录",
            "condition": "{{!check_login_status.logged_in}}",
            "tool": "auto_login",
            "params": {
                "username": "{{username}}",
                "password": "{{password}}"
            }
        },
        {
            "name": "执行主要任务",
            "tool": "main_task",
            "params": {
                "task_type": "{{task_type}}"
            }
        },
        {
            "name": "如果任务成功则保存",
            "condition": "{{main_task.success}}",
            "tool": "save_result",
            "params": {
                "result": "{{main_task.result}}"
            }
        },
        {
            "name": "如果任务失败则重试",
            "condition": "{{!main_task.success}}",
            "tool": "retry_task",
            "params": {
                "max_retries": 3
            }
        }
    ]
}
```

## 5. 实际使用场景

### 5.1 批量处理场景

```python
# 批量创建打印任务
patients = [
    {"name": "张三", "indication": "感冒", "medication": "阿莫西林"},
    {"name": "李四", "indication": "发烧", "medication": "布洛芬"},
    {"name": "王五", "indication": "头痛", "medication": "对乙酰氨基酚"}
]

runner = AgentRunner()

for patient in patients:
    result = runner.run_graph("create_print_job", {
        "patient_name": patient["name"],
        "indication": patient["indication"],
        "medication": patient["medication"]
    })
    
    print(f"患者 {patient['name']} 的打印任务创建结果: {result}")
```

### 5.2 错误处理场景

```python
# 带错误处理的图调用
try:
    result = runner.run_graph("create_print_job", {
        "patient_name": "张三",
        "indication": "感冒"
    })
    
    if result.get("success"):
        print("任务执行成功")
    else:
        print(f"任务执行失败: {result.get('error')}")
        
except Exception as e:
    print(f"图执行异常: {e}")
```

### 5.3 配置化场景

```python
# 使用配置文件
import yaml

# 加载配置
with open("config/print_job_config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 使用配置调用图
result = runner.run_graph("create_print_job", config["default_params"], 
                         config=config["graph_config"])
```

这些示例展示了迁移后的实际使用方法，包括图调用、工具函数使用、新建工具和实际应用场景。您可以根据这些示例来开发自己的自动化流程！ 