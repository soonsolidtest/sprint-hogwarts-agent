import os
import json
import re
import yaml
from dotenv import load_dotenv
import json
from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers.openai_tools import (
    JsonOutputToolsParser,
    PydanticToolsParser,
)

# 导入 selenium 工具
from web_tools.web_toolkit import (
    selenium_get,
    selenium_click,
    selenium_sendkeys,
    selenium_wait_for_element,
    selenium_quit
)

TERMINATION_KEYWORDS = ["登录失败", "等待超时"]
TERMINATION_TOOL_CALLS = ["selenium_quit"]

# 加载 .env
load_dotenv()


# 构造 LLM
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "deepseek-chat"),
    openai_api_key=os.getenv("OPENAI_API_KEY", "not-needed"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com/v1"),
    temperature=0.3
)

# 工具列表
tools = [
    selenium_get,
    selenium_click,
    selenium_sendkeys,
    selenium_wait_for_element,
    selenium_quit
]


# 读取 YAML 提示词模板
def load_prompt_template(path: str, tools_info: str, tool_names: str) -> str:
    config_path = Path(path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    raw_template = config["system_prompt"]
    filled_prompt = raw_template \
        .replace("{tools}", tools_info) \
        .replace("{tool_names}", tool_names)
    return filled_prompt


# 工具信息生成
def generate_tools_info(tools: list) -> tuple[str, str]:
    tools_info = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
    tool_names = ", ".join([tool.name for tool in tools])
    return tools_info, tool_names


tools_info, tool_names = generate_tools_info(tools)
system_prompt = load_prompt_template("../prompts/base_agent_config.yaml", tools_info, tool_names)
print(system_prompt)
tool_dict = {tool.name: tool for tool in tools}



# print(chain)

# 运行函数
def run_agent(state: dict) -> dict:
    user_input = state.get("input", "")
    print(f"[Agent] 用户指令: {user_input}")

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"{user_input}")
    ])
    chain = prompt | llm

    try:
        result = chain.invoke({"input": user_input})
        print(f"[Agent] LLM 原始响应:\n{result.content}")

        content = result.content.strip()

        # 提取 JSON 内容
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if not match:
            raise ValueError("响应中未找到有效 JSON 结构")
        json_str = match.group(1).strip()
        print(f"[Agent] 提取到的 JSON:\n{json_str}")

        action_data = json.loads(json_str)

        if not isinstance(action_data, dict):
            return {"input": user_input, "result": "[格式错误] 提取内容不是有效的 JSON 对象"}

        tool_name = action_data.get("action")
        tool_input = action_data.get("action_input", {})

        if not tool_name:
            return {"input": user_input, "result": "[格式错误] 缺少 action 字段"}

        if tool_name == "Final Answer":
            return {"input": user_input, "result": tool_input}

        tool = tool_dict.get(tool_name)
        if not tool:
            return {"input": user_input, "result": f"[未注册工具] {tool_name}"}

        # 调用对应工具
        tool_result = tool.invoke(tool_input)
        print(f"[Agent] 工具返回结果:\n{tool_result}")
        return {"input": user_input, "result": tool_result}

    except json.JSONDecodeError as je:
        return {"input": user_input, "result": f"[JSON 解析失败] {je}"}
    except Exception as e:
        return {"input": user_input, "result": f"[执行出错] {e}"}


# 构建 LangGraph 状态图
workflow = StateGraph(dict)
workflow.add_node("agent_step", RunnableLambda(run_agent))
workflow.set_entry_point("agent_step")
workflow.set_finish_point("agent_step")
agent_executor = workflow.compile()
agent_executor.get_graph().print_ascii()



# 主程序运行
if __name__ == "__main__":
    user_instruction = input("请输入测试指令：\n> ")
    result = agent_executor.invoke({"input": user_instruction})
    print("最终执行结果:\n", result["result"])
