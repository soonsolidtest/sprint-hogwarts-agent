import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main_graph import main_graph
from langchain_core.messages import HumanMessage

if __name__ == "__main__":
    print("🎯 测试未知意图处理路径")
    inputs = {"messages": [HumanMessage(content="我想处理一个新的任务")]}
    for step in main_graph.stream(inputs):
        print("📍 当前状态:", step)