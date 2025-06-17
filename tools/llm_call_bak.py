import os
import json
import re
from pathlib import Path
import yaml
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from state.types import MessagesState
from langchain_openai import ChatOpenAI

# 加载 .env
load_dotenv()

# 构建工具信息（如 smart_click 等），为空则跳过
TOOLS = []  # 这里你可以替换成你的 tools 列表

def generate_tools_info(tools: list) -> tuple[str, str]:
    tools_info = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools])
    tool_names = ", ".join([tool.name for tool in tools])
    return tools_info, tool_names

tools_info, tool_names = generate_tools_info(TOOLS)

# 根据模式加载 prompt
def load_prompt_template(path: str, tools_info: str, tool_names: str) -> str:
    config_path = Path(path)
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    raw_template = config["system_prompt"]
    return raw_template.replace("{tools}", tools_info).replace("{tool_names}", tool_names)

def get_prompt_by_mode(mode: str) -> str:
    if mode == "router":
        return load_prompt_template("prompts/router_config.yaml", tools_info, tool_names)
    else:
        return load_prompt_template("prompts/base_agent_config.yaml", tools_info, tool_names)

# 初始化 LLM
llm = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    temperature=0.3
)

# 统一的 LLM 调用方法
def llm_call(state: MessagesState, mode: str = "router"):
    prompt = get_prompt_by_mode(mode)
    messages = [SystemMessage(content=prompt)] + state["messages"]
    ai_msg = llm.invoke(messages)

    # 如果是 router 模式，提取 JSON 中的 intent
    if mode == "router":
        match = re.search(r"{.*}", ai_msg.content, re.DOTALL)
        if match:
            try:
                parsed_json = json.loads(match.group(0))
                ai_msg.additional_kwargs["intent"] = parsed_json.get("intent", "unknown")
                ai_msg.additional_kwargs["action"] = parsed_json.get("action", "unknown")
            except json.JSONDecodeError:
                ai_msg.additional_kwargs["intent"] = "unknown"
                ai_msg.additional_kwargs["action"] = "invalid_json"

    return {"messages": state["messages"] + [ai_msg]}