from typing import Dict, Any, Callable, List, Union, Optional
from dataclasses import dataclass
from enum import Enum

# 定义状态类型
MessagesState = Dict[str, Any]

# 特殊状态标记
END = "END"

class StateGraph:
    """状态图实现"""
    
    def __init__(self, state_type: type):
        """初始化状态图"""
        print("\n📍 [State Graph] 初始化状态图")
        self.state_type = state_type
        self.nodes: Dict[str, Callable] = {}
        self.edges: Dict[str, Union[str, Callable]] = {}
        self.entry: Optional[str] = None
        self.finish_points: List[str] = []
        
    def add_node(self, name: str, func: Callable) -> None:
        """添加节点"""
        print(f"➕ 添加节点: {name}")
        self.nodes[name] = func
        
    def add_edge(self, from_node: str, to_node: str) -> None:
        """添加边"""
        print(f"🔀 添加边: {from_node} -> {to_node}")
        if from_node not in self.nodes:
            raise ValueError(f"起始节点不存在: {from_node}")
        if to_node not in self.nodes and to_node != END:
            raise ValueError(f"目标节点不存在: {to_node}")
        self.edges[from_node] = to_node
        
    def add_conditional_edges(self, from_node: str, condition: Callable, routes: Dict[str, str]) -> None:
        """添加条件边"""
        print(f"🔀 添加条件边: {from_node}")
        if from_node not in self.nodes:
            raise ValueError(f"起始节点不存在: {from_node}")
        for to_node in routes.values():
            if to_node not in self.nodes and to_node != END:
                raise ValueError(f"目标节点不存在: {to_node}")
        self.edges[from_node] = lambda x: routes[condition(x)]
        
    def set_entry_point(self, node: str) -> None:
        """设置入口点"""
        print(f"🎯 设置入口点: {node}")
        if node not in self.nodes:
            raise ValueError(f"入口节点不存在: {node}")
        self.entry = node
        
    def set_finish_point(self, node: str) -> None:
        """设置结束点"""
        print(f"🏁 设置结束点: {node}")
        if node not in self.nodes:
            raise ValueError(f"结束节点不存在: {node}")
        self.finish_points.append(node)
        
    def compile(self) -> 'CompiledGraph':
        """编译图"""
        print("✅ 编译状态图")
        if not self.entry:
            raise ValueError("未设置入口点")
        return CompiledGraph(self)
        
    def get_next_node(self, current: str, state: MessagesState) -> Optional[str]:
        """获取下一个节点"""
        if current not in self.edges:
            return None
        edge = self.edges[current]
        if callable(edge):
            return edge(state)
        return edge

class CompiledGraph:
    """已编译的状态图"""
    
    def __init__(self, graph: StateGraph):
        """初始化已编译图"""
        self.graph = graph
        
    def invoke(self, initial_state: MessagesState) -> MessagesState:
        """执行图"""
        print("\n🚀 [State Graph] 开始执行")
        
        if not isinstance(initial_state, dict):
            raise ValueError("初始状态必须是字典类型")
            
        current = self.graph.entry
        state = initial_state
        
        while current != END and current is not None:
            print(f"\n📍 当前节点: {current}")
            print(f"📥 输入状态: {state}")
            
            # 执行当前节点
            try:
                state = self.graph.nodes[current](state)
                print(f"📤 输出状态: {state}")
            except Exception as e:
                print(f"❌ 节点执行错误: {e}")
                raise
                
            # 获取下一个节点
            next_node = self.graph.get_next_node(current, state)
            print(f"🔄 下一个节点: {next_node}")
            
            if next_node is None and current not in self.graph.finish_points:
                raise ValueError(f"节点 {current} 没有后继节点且不是结束点")
                
            current = next_node
            
        print("\n✅ 图执行完成")
        return state 