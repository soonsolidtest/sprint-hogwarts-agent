# run_rayware.py
from graphs.rayware_graph import rayware_module_graph
from langchain_core.messages import HumanMessage
import asyncio

async def run_graph_with_input(user_input: str):
    # 初始状态
    config = {}  # 你可以加入 tracing、callbacks、model config 等
    state = {
        "messages": [HumanMessage(content=user_input)]
    }

    # 执行 LangGraph 图
    async for step in rayware_module_graph.astream(state, config=config):
        print("📍 当前状态:")
        print(step)

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("❗请输入自然语言指令，例如：")
        print("   python run_rayware.py '新建一个牙科打印任务，打印材料是Denture Base。'")
    else:
        user_command = sys.argv[1]
        asyncio.run(run_graph_with_input(user_command))
