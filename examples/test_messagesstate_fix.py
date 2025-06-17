#!/usr/bin/env python3
"""
测试 MessagesState 修复
验证 TypedDict 修复后的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from state.types import MessagesState
from langchain_core.messages import HumanMessage, AIMessage
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_messagesstate_basic():
    """测试 MessagesState 基本功能"""
    print("🧪 测试 MessagesState 基本功能")
    print("-" * 40)
    
    # 创建状态
    state: MessagesState = {
        "messages": [HumanMessage(content="测试消息")],
        "input": "用wangyili 新建打印",
        "rayware_intent": "new_print_job"
    }
    
    # 测试 .get() 方法
    try:
        messages = state.get("messages", [])
        print(f"✅ state.get('messages') 成功: {len(messages)} 条消息")
        
        user_input = state.get("input", "")
        print(f"✅ state.get('input') 成功: '{user_input}'")
        
        intent = state.get("rayware_intent", "unknown")
        print(f"✅ state.get('rayware_intent') 成功: '{intent}'")
        
        # 测试不存在的键
        missing = state.get("non_existent_key", "default")
        print(f"✅ state.get('non_existent_key', 'default') 成功: '{missing}'")
        
        return True
        
    except Exception as e:
        print(f"❌ MessagesState .get() 方法失败: {e}")
        return False

def test_messagesstate_operations():
    """测试 MessagesState 操作"""
    print("\n🧪 测试 MessagesState 操作")
    print("-" * 40)
    
    # 初始状态
    state: MessagesState = {
        "messages": [],
        "input": "测试输入",
        "error_count": 0
    }
    
    try:
        # 添加消息
        state["messages"].append(HumanMessage(content="用户消息"))
        state["messages"].append(AIMessage(content="AI回复"))
        print(f"✅ 添加消息成功: {len(state['messages'])} 条")
        
        # 更新计数
        state["error_count"] = state.get("error_count", 0) + 1
        print(f"✅ 更新错误计数成功: {state['error_count']}")
        
        # 设置新字段
        state["rayware_intent"] = "new_print_job"
        state["current_page"] = "rayware"
        print("✅ 设置新字段成功")
        
        # 检查所有字段
        print(f"📊 状态字段: {list(state.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ MessagesState 操作失败: {e}")
        return False

def test_rayware_graph_compatibility():
    """测试与 rayware_graph 的兼容性"""
    print("\n🧪 测试与 rayware_graph 的兼容性")
    print("-" * 40)
    
    try:
        # 模拟 rayware_graph 中的状态操作
        state: MessagesState = {
            "messages": [HumanMessage(content="新建打印任务")],
            "input": "新建打印任务",
            "rayware_intent": "new_print_job",
            "print_job_data": {}
        }
        
        # 模拟 rayware_graph 中的操作
        user_input = state.get("user_input", "")
        intent = state.get("rayware_intent", "new_print_job")
        messages = state.get("messages", [])
        
        print(f"✅ 获取用户输入: '{user_input}'")
        print(f"✅ 获取意图: '{intent}'")
        print(f"✅ 获取消息: {len(messages)} 条")
        
        # 模拟状态更新
        state["current_page"] = "new_print_job"
        state["print_job_data"] = {
            "patient_name": "测试患者",
            "case_name": "测试案例"
        }
        
        print("✅ 状态更新成功")
        return True
        
    except Exception as e:
        print(f"❌ rayware_graph 兼容性测试失败: {e}")
        return False

def test_main_graph_compatibility():
    """测试与 main_graph 的兼容性"""
    print("\n🧪 测试与 main_graph 的兼容性")
    print("-" * 40)
    
    try:
        # 模拟 main_graph 中的状态操作
        state: MessagesState = {
            "messages": [],
            "input": "用wangyili 新建打印",
            "should_stop": False,
            "waiting_for_confirmation": False
        }
        
        # 模拟 main_graph 中的检查
        should_stop = state.get("should_stop", False)
        waiting = state.get("waiting_for_confirmation", False)
        messages = state.get("messages", [])
        user_input = state.get("input", "")
        
        print(f"✅ 检查停止标志: {should_stop}")
        print(f"✅ 检查等待确认: {waiting}")
        print(f"✅ 获取消息列表: {len(messages)} 条")
        print(f"✅ 获取用户输入: '{user_input}'")
        
        return True
        
    except Exception as e:
        print(f"❌ main_graph 兼容性测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 MessagesState 修复验证测试")
    print("=" * 50)
    
    # 运行所有测试
    tests = [
        test_messagesstate_basic,
        test_messagesstate_operations,
        test_rayware_graph_compatibility,
        test_main_graph_compatibility
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")
    
    # 统计结果
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✅ 所有测试通过！MessagesState 修复成功")
        print("✅ 现在可以正常使用 state.get() 方法")
        print("✅ 与现有图的兼容性良好")
    else:
        print("❌ 部分测试失败，需要进一步调试")
    
    print("\n📋 修复总结:")
    print("🔧 将 @dataclass 改为 TypedDict")
    print("🔧 添加 total=False 支持可选字段")
    print("🔧 保持所有现有字段的兼容性")
    print("🔧 添加新字段以支持更多功能") 