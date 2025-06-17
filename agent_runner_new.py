from langchain_core.messages import HumanMessage
from graphs.main_graph import main_graph
from state.types import MessagesState
from graphs.state_graph import StateGraph
from state.intent_classifier import classify_intent_with_log
from state.router import route_to_module
from state.llm_call import llm_call
from graphs.rayware_graph import rayware_module_graph

def main():
    print("✅ Agent 启动，输入'exit'退出")
    state = {
        "messages": [],
        "rayware_intent": "",
        "input": "",
        "module": "",  # 添加模块标识
        "test_config": {}  # 添加测试配置
    }
    while True:
        text = input("> ")
        if text.lower() in ("exit", "quit"):
            break

        # 创建 HumanMessage 对象并添加到消息列表
        human_message = HumanMessage(content=text)
        state["messages"].append(human_message)
        state["input"] = text  # 更新输入内容
        print("提交前 state input：", state["input"])
        out = main_graph.process(state)

        state = out  # LangGraph 会返回新的完整 state
        if (state["messages"]):
             print("✅ 输出：", state["messages"][-1].content)
        else:
             print("✅ 输出： (无消息)")

        for msg in out["messages"]:
            msg.pretty_print()
        state["messages"] = out["messages"]

if __name__ == "__main__":
    main()

# 主图流程
builder = StateGraph(MessagesState)

# 添加节点
builder.add_node("classify_intent", classify_intent_with_log)
builder.add_node("route_module", route_to_module)
builder.add_node("llm_call", llm_call)
builder.add_node("rayware", rayware_module_graph)

# 设置流程
builder.set_entry_point("classify_intent")
builder.add_conditional_edges(
    "classify_intent",
    lambda x: x["rayware_intent"],
    {
        "rayware": "rayware",
        "unknown": "llm_call",
        "error": "llm_call"
    }
)
