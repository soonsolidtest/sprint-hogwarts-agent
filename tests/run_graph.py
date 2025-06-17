# run.py

from langchain_core.messages import HumanMessage
from tools.llm_call import llm_call
from state.types import MessagesState

def run_router():
    state: MessagesState = {
        "messages": [HumanMessage(content="我想创建一个新的打印任务")]
    }
    result = llm_call(state, mode="router")
    intent = result["messages"][-1].additional_kwargs.get("intent", "unknown")
    print("识别的意图:", intent)

def run_web_agent():
    state: MessagesState = {
        "messages": [HumanMessage(content="点击页面中的登录按钮")]
    }
    result = llm_call(state, mode="agent")
    print("Web Agent 回复:", result["messages"][-1].content)

if __name__ == "__main__":
    run_router()       # 测试意图识别
    # run_web_agent()  # 需要你填好 TOOLS 列表和 Selenium 工具后启用
