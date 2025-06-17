from tools.tool_node import tool_node
from state.types import MessagesState
from langchain_core.messages import AIMessage
import time

def test_selenium_get():
    # 测试打开浏览器
    state = MessagesState(
        messages=[
            AIMessage(content='```json\n{"action": "selenium_get", "action_input": {"url": "https://dev.designservice.sprintray.com/home-screen"}}\n```')
        ],
        input=''
    )
    result = tool_node(state)
    print("Test selenium_get result:", result)
    # 等待页面加载
    time.sleep(5)

def test_selenium_wait_for_element():
    # 测试等待元素
    state = MessagesState(
        messages=[
            AIMessage(content='```json\n{"action": "selenium_wait_for_element", "action_input": {"locator": "新建打印任务", "by": "xpath", "value": "//button[contains(text(), \'新建打印任务\')]"}}\n```')
        ],
        input=''
    )
    result = tool_node(state)
    print("Test selenium_wait_for_element result:", result)
    # 等待元素出现
    time.sleep(2)

def test_smart_click():
    # 测试点击元素
    state = MessagesState(
        messages=[
            AIMessage(content='```json\n{"action": "smart_click", "action_input": {"locator": "新建打印任务", "by": "xpath", "value": "//button[contains(text(), \'新建打印任务\')]"}}\n```')
        ],
        input=''
    )
    result = tool_node(state)
    print("Test smart_click result:", result)

if __name__ == "__main__":
    print("Testing tool_node...")
    test_selenium_get()
    test_selenium_wait_for_element()
    test_smart_click() 