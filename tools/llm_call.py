from langchain_core.messages import SystemMessage, AIMessage
from state.types import MessagesState
from config import system_prompt
import json
import re
import yaml
import os
from langchain_openai import ChatOpenAI

# 初始化LLM实例
def get_llm():
    """获取LLM实例"""
    # 从 config.yaml 读取 LLM 配置
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    llm_config = config.get("llm", {})
    api_key = llm_config.get("api_key")
    api_base = llm_config.get("api_base", "https://api.deepseek.com/v1")
    model = llm_config.get("model", "deepseek-chat")
    
    if not api_key:
        raise ValueError("llm.api_key not set in config.yaml")
    
    return ChatOpenAI(
        model=model,
        temperature=0,
        api_key=api_key,
        base_url=api_base
    )

def llm_call(state: MessagesState) -> dict:
    """调用LLM处理用户输入"""
    print("\n📍 [LLM Call] 开始处理用户输入")
    print(f"📥 输入状态: {state}")
    
    msgs = state["messages"]
    # 强调只返回一个Action，不要模拟Observation
    system_content = """你是一个网页自动化测试 Agent，专门用于测试SprintRay的Rayware系统。

重要：你只需要返回下一步要执行的单个操作，不要模拟执行结果！

严格按照以下格式回复：
```
{
  "action": "工具名称",
  "action_input": {
    "参数": "值"
  }
}
```

可用的工具：
- selenium_get: 打开指定网址，参数：{"url": "网址"}
- selenium_click: 点击指定元素，参数：{"locator": "选择器", "locator_type": "类型"}
- selenium_sendkeys: 输入指定内容，参数：{"selector": {"by": "类型", "value": "选择器"}, "text": "内容"}
- selenium_wait_for_element: 等待元素加载，参数：{"selector": {"by": "类型", "value": "选择器"}}
- selenium_quit: 退出浏览器

严格规则：
1. 只返回一个JSON格式的工具调用
2. 不要添加"No Thought"、"Observation"等文本
3. 不要模拟执行结果
4. 专注于下一步需要执行的操作"""
    
    system = SystemMessage(content=system_content)
    
    # 如果有test_config，添加到系统消息中
    if "test_config" in state and state["test_config"]:
        config_msg = f"\n当前测试配置: {state['test_config']}"
        system = SystemMessage(content=system_content + config_msg)
        print(f"🔧 添加测试配置到系统消息: {config_msg}")
    
    # 获取LLM实例并调用
    llm = get_llm()
    resp = llm.invoke([system, *msgs])
    print(f"🤖 LLM响应: {resp.content}")
    
    # 解析第一个 action
    content = resp.content
    action = None
    start = content.find('{')
    if start != -1:
        # 找到第一个完整的JSON
        brace_count = 0
        end = start
        for i, char in enumerate(content[start:], start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
        
        if end > start:
            action_str = content[start:end]
            try:
                action = json.loads(action_str)
                print(f"✅ 成功解析action: {action}")
            except json.JSONDecodeError as e:
                print(f"❌ Action解析失败: {e}")
                # 尝试从```块中解析
                start = content.find('```')
                if start != -1:
                    end = content.find('```', start + 3)
                    if end != -1:
                        action_str = content[start + 3:end].strip()
                        if action_str.startswith('json'):
                            action_str = action_str[4:].strip()
                        try:
                            action = json.loads(action_str)
                            print(f"✅ 从代码块成功解析action: {action}")
                        except json.JSONDecodeError:
                            print("❌ 代码块Action解析失败")
    
    # 如果找到 action，设置 tool_calls
    if action and 'action' in action and 'action_input' in action:
        tool_call = {
            "id": f"call_{hash(str(action))}", 
            "name": action["action"],
            "args": action["action_input"]
        }
        print(f"🔧 创建tool_call: {tool_call}")
        # 创建新的 AIMessage，只包含 action
        resp = AIMessage(
            content=json.dumps(action, ensure_ascii=False, indent=2),
            tool_calls=[tool_call]
        )
    else:
        print("❌ 未找到有效的action，使用原始响应")
    
    new_state = {
        **state,  # 保留所有现有状态
        "messages": state["messages"] + [resp]  # 将新响应添加到消息历史中
    }
    print(f"📤 输出状态: {new_state}")
    return new_state
