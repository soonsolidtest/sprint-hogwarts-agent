# 登录后调用 Rayware 图进行新建打印任务

本文档说明如何使用框架实现登录后自动调用 rayware 图进行新建打印任务的功能。

## 🎯 功能概述

框架支持以下完整流程：
1. **用户登录** - 使用配置的账号自动登录
2. **意图识别** - 自动识别用户要执行的操作
3. **调用 Rayware 图** - 登录成功后自动调用相应的业务图
4. **执行业务操作** - 在 Rayware 系统中执行具体操作

## 📋 支持的指令格式

### 登录 + 新建打印任务
```
用wangyili登录并新建打印任务
请用user1登录然后创建一个新的打印任务
用wangyili登录，我要新建打印任务
wangyili登录后新建打印任务
```

### 登录 + 查看历史
```
用wangyili登录并查看打印历史
请用user1登录然后查看最近的打印任务
用wangyili登录，我要查看历史
```

## 🔧 技术实现

### 1. 数据流转图

```
用户输入 → 主图处理 → LLM解析 → 登录工具执行 → 登录成功检查 → Rayware图调用 → 业务操作执行
```

### 2. 关键组件

#### 主图 (main_graph.py)
- 负责整体流程控制
- 检测登录成功后的后续操作意图
- 自动调用 rayware 图

#### Rayware 图 (rayware_graph.py)
- 专门处理 Rayware 系统的业务操作
- 支持新建打印任务、查看历史等功能
- 包含完整的页面导航和表单填写逻辑

#### 登录工具 (web_toolkit.py)
- `auto_login()` - 根据用户描述自动登录
- `login_with_credentials()` - 使用具体凭据登录

### 3. 核心代码逻辑

#### 主图中的登录后处理逻辑
```python
# 检查是否是登录成功
if tool_call["name"] in ["auto_login", "login_with_credentials"]:
    if isinstance(result, dict) and result.get("status") == "success":
        # 检查用户输入是否包含后续操作意图
        user_input = state.get("input", "")
        if any(keyword in user_input for keyword in ['新建', '打印任务', '创建', '新增']):
            # 调用 rayware 图
            rayware_result = rayware_module_graph.invoke(state)
```

#### Rayware 图的业务流程
```python
# 意图分类 → 导航到Rayware → 创建打印任务 → 提交任务
classify_intent → navigate_to_rayware → create_new_print_job → submit_print_job
```

## 🚀 使用方法

### 方法1: 直接运行主程序
```bash
python agent_runner_new.py
```
然后输入指令：
```
> 用wangyili登录并新建打印任务
```

### 方法2: 使用示例脚本
```bash
python examples/login_and_create_print_job.py
```

### 方法3: 编程调用
```python
from langchain_core.messages import HumanMessage
from graphs.main_graph import main_graph

# 创建状态
state = {
    "messages": [HumanMessage(content="用wangyili登录并新建打印任务")],
    "input": "用wangyili登录并新建打印任务",
    # ... 其他状态字段
}

# 执行处理
result = main_graph.process(state)
```

## ⚙️ 配置说明

### 账号配置 (config.yaml)
```yaml
accounts:
  - description: "wangyili"
    url: "https://dev.account.sprintray.com/"
    username: "wangyili@sprintray.cn"
    password: "password456"
  - description: "user1"
    url: "https://dev.account.sprintray.com/"
    username: "zhufeng@sprintray.cn"
    password: "xunshi@123"
```

### Design Service 系统配置
```yaml
design_service:
  base_url: "https://dev.designservice.sprintray.com"
  urls:
    home: "https://dev.designservice.sprintray.com/home-screen"
    rayware: "https://dev.designservice.sprintray.com/print-setup"
    print_history: "https://dev.designservice.sprintray.com/print-history"
    new_print_job: "https://dev.designservice.sprintray.com/print-setup"
  page_indicators:
    rayware_home: ["print-setup", "designservice.sprintray.com"]
    print_setup: ["print-setup"]
    print_history: ["print-history"]
```

### 配置结构说明

1. **design_service**: 主配置节点，包含整个 Design Service 系统的配置
2. **base_url**: Design Service 系统的基础URL
3. **urls**: 各个功能页面的具体URL
   - `home`: 首页
   - `rayware`: Rayware 打印设置页面
   - `print_history`: 打印历史页面
   - `new_print_job`: 新建打印任务页面（通常与 rayware 相同）
4. **page_indicators**: 用于自动识别当前页面类型的关键词

### 意图路由配置
```yaml
intent_routing:
  new_print_job:
    keywords: ["新建", "打印任务", "新建打印任务", "创建打印"]
    description: "用户想要创建新的打印任务"
  
  recent_print_jobs:
    keywords: ["最近", "历史", "查看", "打印历史", "查看历史"]
    description: "用户想要查看最近的打印任务"
```

### 配置管理优势

1. **集中管理**：所有 URL 配置在一个地方，便于维护
2. **环境切换**：可以轻松切换开发/测试/生产环境
3. **智能识别**：通过 `page_indicators` 自动识别当前页面类型
4. **灵活扩展**：可以轻松添加新的页面和URL

### 配置验证

运行配置验证脚本确保配置正确：
```bash
python scripts/validate_config.py
```

该脚本会验证：
- LLM 配置完整性
- 账号配置正确性
- Rayware URL 格式和可访问性
- 浏览器配置有效性
- 配置方法功能测试

## 🔍 执行流程详解

### 1. 用户输入解析
```
输入: "用wangyili登录并新建打印任务"
↓
解析出: 
- 登录用户: wangyili
- 后续操作: 新建打印任务
```

### 2. 登录执行
```
auto_login(user_desc="wangyili")
↓
查找账号配置 → 打开登录页 → 输入凭据 → 验证登录
```

### 3. 意图检测
```
检查用户输入中的关键词:
['新建', '打印任务', '创建', '新增'] → 触发新建打印任务流程
```

### 4. Rayware 图调用
```
rayware_module_graph.invoke(state)
↓
classify_intent → navigate_to_rayware → create_new_print_job → submit_print_job
```

### 5. 业务操作执行
```
导航到 Rayware → 点击新建按钮 → 填写表单 → 提交任务
```

## 🛠️ 自定义扩展

### 添加新的业务操作
1. 在 `rayware_graph.py` 中添加新的节点函数
2. 更新图结构，添加新的条件边
3. 在意图分类中添加新的关键词

### 添加新的登录后操作
1. 在主图的登录后处理逻辑中添加新的关键词检测
2. 创建对应的业务图或直接执行操作
3. 更新配置文件中的意图路由

## 🐛 故障排除

### 常见问题

1. **登录失败**
   - 检查账号配置是否正确
   - 确认网络连接正常
   - 查看 ChromeDriver 是否正常工作

2. **Rayware 图调用失败**
   - 检查登录是否真正成功
   - 确认页面 URL 是否正确
   - 查看元素定位是否准确

3. **意图识别错误**
   - 检查关键词配置
   - 确认用户输入格式
   - 查看日志中的意图识别结果

### 调试方法

1. **启用详细日志**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **检查状态变化**
```python
print(f"当前状态: {state}")
```

3. **单步执行**
```python
# 分别测试登录和业务操作
result1 = auto_login(user_desc="wangyili")
result2 = rayware_module_graph.invoke(state)
```

## 📝 最佳实践

1. **指令格式规范**
   - 使用清晰的动词：登录、新建、创建、查看
   - 明确指定用户：user1、wangyili
   - 明确指定操作：打印任务、历史

2. **错误处理**
   - 每个步骤都有错误处理机制
   - 失败时会提供明确的错误信息
   - 支持重试机制

3. **性能优化**
   - 复用浏览器实例
   - 智能元素定位
   - 异步操作支持

## 🎉 总结

通过这个框架，你可以用一句话完成复杂的业务操作：

```
"用wangyili登录并新建打印任务"
```

框架会自动：
1. 解析指令意图
2. 执行登录操作
3. 导航到业务系统
4. 执行具体业务操作
5. 返回执行结果

这大大简化了自动化测试的复杂度，提高了测试效率。 