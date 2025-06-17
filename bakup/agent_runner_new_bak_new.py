from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda
from state.types import MessagesState  # 你的消息状态定义
from tools.llm_call import llm_call  # 原 LLM 调用
from tools.tool_node import tool_node  # 原工具节点
from tools.should_continue import should_continue  # 判断流程是否继续
from graphs.rayware_graph import rayware_module_graph  # 模块子图（包含 new_print_job）

from langgraph.graph import StateGraph, END

# 主图：构建顶层控制流
builder = StateGraph(MessagesState)

# 添加 LLM 节点
builder.add_node("llm_call", llm_call)

# 模块调度节点（根据 LLM 输出选择模块子图）
def route_module(state: MessagesState):
    last_message = state["messages"][-1]
    content = last_message.content if hasattr(last_message, "content") else ""
    if "print job" in content.lower():
        print("[Router] 调用 rayware 模块")
        return {"messages": state["messages"]}
    raise ValueError("目前仅支持 rayware 子图")

router_node = RunnableLambda(route_module)

# 添加子图（如 rayware_graph）为节点
builder.add_node("route_module", router_node)
builder.add_node("rayware", rayware_module_graph)

# 配置执行流程
builder.set_entry_point("llm_call")
builder.set_finish_point("llm_call")
# builder.set_finish_point(END)

builder.add_conditional_edges("llm_call", should_continue, {
    "Action": "route_module",
    END: END
})

builder.add_edge("route_module", "rayware")
builder.add_edge("rayware", "llm_call")

# 编译 Agent
agent_executor = builder.compile()

if __name__ == "__main__":
    # input_state = {
    #     "messages": [
    #         HumanMessage(content="请创建一个新的 print job，使用默认设置"),
    #     ]
    # }
    # for output in agent_executor.stream(input_state):
    #     print("⏩", output)
    state = {"messages": [HumanMessage(content="新建一个牙科打印任务，材料用Denture Base，厚度100μm。")]}
    print("🚀 启动主图流程 ...")
    for step in agent_executor.stream(state):
        print(f"\n📍 当前节点: {step['node']}")
        for msg in step['state'].get("messages", []):
            print(f"💬 {type(msg).__name__}: {msg.content}")
