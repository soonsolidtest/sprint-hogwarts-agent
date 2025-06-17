import os
import yaml
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START, MessagesState

# 导入工具模块
from web_tools.web_toolkit import (
    selenium_get,
    selenium_click,
    smart_select_and_choose,
    smart_select_open,
    smart_click,
    selenium_sendkeys,
    selenium_wait_for_element,
    selenium_wait_until_text,
    selenium_quit
)

# 加载 .env
load_dotenv()

# 注册工具
TOOLS = [
    selenium_get,
    # selenium_click,
    smart_select_and_choose,
    smart_click,
    smart_select_open,
    selenium_sendkeys,
    selenium_wait_for_element,
    selenium_wait_until_text,
    selenium_quit,
]
TOOLS_BY_NAME = {tool.name: tool for tool in TOOLS}

# 构建 OpenAI LLM
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    temperature=0.3
).bind_tools(TOOLS)

# 加载 system prompt 模板
def load_prompt_template(path: str, tools_info: str, tool_names: str) -> str:
    config_path = Path(path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    raw_template = config["system_prompt"]
    return raw_template.replace("{tools}", tools_info).replace("{tool_names}", tool_names)

def generate_tools_info(tools: list) -> tuple[str, str]:
    tools_info = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
    tool_names = ", ".join([tool.name for tool in tools])
    return tools_info, tool_names

tools_info, tool_names = generate_tools_info(TOOLS)
system_prompt = load_prompt_template("../prompts/base_agent_config.yaml", tools_info, tool_names)

# 调用 LLM 判断是否使用工具
def llm_call(state: MessagesState):
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    return {"messages": [llm.invoke(messages)]}

# 执行工具调用
def tool_node(state: MessagesState):
    last_msg = state["messages"][-1]
    results = []

    for tool_call in last_msg.tool_calls:
        tool_name = tool_call["name"]
        args = tool_call["args"]

        tool = TOOLS_BY_NAME.get(tool_name)
        print(f"Executing tool: {tool_call['name']} with args {tool_call['args']}")
        if not tool:
            results.append(ToolMessage(content=f"[未知工具]: {tool_name}", tool_call_id=tool_call["id"]))
            continue
        try:
            obs = tool.invoke(args)
            print(f"Tool returned: {obs}")
            results.append(ToolMessage(content=str(obs), tool_call_id=tool_call["id"]))
        except Exception as e:
            results.append(ToolMessage(content=f"[工具执行失败]: {e}", tool_call_id=tool_call["id"]))
    return {"messages": results}

# 判断是否继续循环
def should_continue(state: MessagesState) -> Literal["Action", END]:
    last_message = state["messages"][-1]

    # 如果上一条消息是工具调用 → 继续执行
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        tool_call_names = [tc["name"] for tc in last_message.tool_calls]
        if "selenium_quit" in tool_call_names:
            print("[should_continue] 检测到 selenium_quit，流程终止")
            return END
        print("[should_continue] continue (tool call)")
        return "Action"

    # 如果上一条是工具的返回消息（ToolMessage）
    if isinstance(last_message, ToolMessage):
        print("[should_continue] continue (tool message)")
        return "Action"

    # 如果失败标记
    if hasattr(last_message, "additional_kwargs"):
        if last_message.additional_kwargs.get("failed", False):
            print("[should_continue] 检测到失败标志，流程终止")
            return END

    # 如果文本里包含明显失败提示
    if hasattr(last_message, "content"):
        if "登录失败" in last_message.content or "等待超时" in last_message.content:
            print("[should_continue] 检测到失败内容，流程终止")
            return END

    # 默认终止（防止死循环）
    print("[should_continue] 默认终止")
    return END


# 构建 LangGraph
builder = StateGraph(MessagesState)
builder.add_node("llm_call", llm_call)
builder.add_node("tools", tool_node)
builder.set_entry_point("llm_call")
builder.set_finish_point("llm_call")
builder.add_conditional_edges("llm_call", should_continue, {
    "Action": "tools",
    END: END
})
builder.add_edge("tools", "llm_call")
agent_executor = builder.compile()
agent_executor.get_graph().print_ascii()


# 主入口
if __name__ == "__main__":
    print("输入自然语言指令（例如：打开网址 https://dev.xxx.com）：")
    user_input = input("\n> ")

    result = agent_executor.invoke({
        "messages": [HumanMessage(content=user_input)]
    })

    print("最终消息流：")
    for msg in result["messages"]:
        print("-", msg.pretty_print())