# tools/retry_llm_intent_guess.py

from typing import TypedDict, List
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.runnables import RunnableLambda
import json

class UnknownState(TypedDict):
    messages: List[BaseMessage]

# 提示词模版
INTENT_GUESS_PROMPT = """你是一个用户意图分析助手。请阅读以下用户消息，并猜测用户可能想做什么：

{messages}

请从以下选项中选择最有可能的一个意图，并用 JSON 格式输出：
- new_print_job：用户想新建一个打印任务
- recent_print_jobs：用户想查看最近的打印任务
- unknown：仍然无法判断

返回格式如下：
{{"intent": "new_print_job", "reason": "你的解释..."}}
"""

def retry_llm_intent_guess(llm, state: UnknownState) -> UnknownState:
    user_messages = "\n".join([f"- {m.content}" for m in state["messages"] if m.type == "human"])
    prompt = INTENT_GUESS_PROMPT.format(messages=user_messages)

    response = llm.invoke(prompt)
    print("🤖 猜测意图返回:", response.content)

    try:
        result = json.loads(response.content)
        intent = result.get("intent", "unknown")
        reason = result.get("reason", "无法解释")
    except Exception:
        intent = "unknown"
        reason = "返回格式错误"

    reply = f"我猜你可能的意图是 `{intent}`，因为：{reason}\n如果正确，请尝试更清晰地表达你的需求~"
    state["messages"].append(AIMessage(content=reply))
    return state

retry_llm_intent_guess_node = RunnableLambda(retry_llm_intent_guess).with_config({"name": "retry_llm_intent_guess"})