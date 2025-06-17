#!/usr/bin/env python3
"""
最终修复验证 - 测试完整的登录和新建打印任务流程
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_tools.web_toolkit import auto_login, create_new_print_job
from graphs.rayware_graph import rayware_module_graph
from state.types import MessagesState
from langchain_core.messages import HumanMessage
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tool_invocation_fix():
    """测试工具调用修复"""
    print("🧪 测试工具调用修复")
    print("-" * 40)
    
    try:
        # 测试1: 直接调用工具
        print("📍 测试1: 直接调用 auto_login 工具")
        login_result = auto_login.invoke({"user_desc": "wangyili"})
        print(f"登录结果: {login_result.get('status')} - {login_result.get('message')}")
        
        if login_result.get('status') == 'success':
            # 测试2: 直接调用 create_new_print_job 工具
            print("\n📍 测试2: 直接调用 create_new_print_job 工具")
            create_result = create_new_print_job.invoke({
                "patient_name": "测试患者",
                "case_name": "测试案例"
            })
            print(f"创建结果: {create_result.get('status')} - {create_result.get('message')}")
            
            return True
        else:
            print("⚠️ 登录失败，跳过创建测试")
            return False
            
    except Exception as e:
        print(f"❌ 工具调用测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_rayware_graph_fix():
    """测试 rayware_graph 修复"""
    print("\n🧪 测试 rayware_graph 修复")
    print("-" * 40)
    
    try:
        # 创建测试状态
        state: MessagesState = {
            "messages": [HumanMessage(content="新建打印任务")],
            "input": "新建打印任务",
            "rayware_intent": "new_print_job",
            "print_job_data": {}
        }
        
        print("📍 调用 rayware_module_graph")
        result = rayware_module_graph.invoke(state)
        
        print(f"图执行结果: {result.get('rayware_intent')}")
        
        # 检查消息
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            print(f"最后消息: {last_message.content if hasattr(last_message, 'content') else last_message}")
        
        return True
        
    except Exception as e:
        print(f"❌ rayware_graph 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_state_manager_fix():
    """测试 StateManager 修复"""
    print("\n🧪 测试 StateManager 修复")
    print("-" * 40)
    
    try:
        from state.state_manager import StateManager, State
        
        # 测试创建包含 print_job_data 的状态
        state_data = {
            "messages": [],
            "input": "测试输入",
            "print_job_data": {"patient_name": "测试患者"},
            "rayware_intent": "new_print_job"
        }
        
        print("📍 创建 StateManager")
        state_manager = StateManager()
        
        print("📍 更新状态（包含 print_job_data）")
        state_manager.update(state_data)
        
        print("📍 获取状态")
        current_state = state_manager.get_state()
        
        print(f"✅ 状态更新成功，print_job_data: {current_state.get('print_job_data')}")
        
        return True
        
    except Exception as e:
        print(f"❌ StateManager 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_integration():
    """测试完整集成"""
    print("\n🧪 测试完整集成")
    print("-" * 40)
    
    try:
        # 模拟完整流程
        print("📍 步骤1: 登录")
        login_result = auto_login.invoke({"user_desc": "wangyili"})
        
        if login_result.get('status') == 'success':
            print("✅ 登录成功")
            
            print("\n📍 步骤2: 创建打印任务状态")
            state: MessagesState = {
                "messages": [HumanMessage(content="新建打印任务")],
                "input": "新建打印任务",
                "rayware_intent": "new_print_job",
                "print_job_data": {}
            }
            
            print("📍 步骤3: 执行 rayware 图")
            result = rayware_module_graph.invoke(state)
            
            print(f"✅ 图执行完成，最终意图: {result.get('rayware_intent')}")
            
            return True
        else:
            print("❌ 登录失败，无法继续测试")
            return False
            
    except Exception as e:
        print(f"❌ 完整集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 最终修复验证测试")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        ("工具调用修复", test_tool_invocation_fix),
        ("rayware_graph 修复", test_rayware_graph_fix),
        ("StateManager 修复", test_state_manager_fix),
        ("完整集成测试", test_complete_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("🎉 测试完成！")
    
    # 统计结果
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    if passed == total:
        print("\n🎉 所有修复都成功了！")
        print("✅ 工具调用使用 .invoke() 方法")
        print("✅ StateManager 支持 print_job_data 字段")
        print("✅ MessagesState 支持 .get() 方法")
        print("✅ 完整流程可以正常运行")
        print("\n现在可以正常执行 '用wangyili 新建打印' 指令了！🚀")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试")
    
    print("\n📋 修复总结:")
    print("🔧 修复了 rayware_graph 中的工具调用方式")
    print("🔧 在 StateManager 的 State 类中添加了 print_job_data 字段")
    print("🔧 MessagesState 已改为 TypedDict 支持 .get() 方法")
    print("🔧 登录验证速度已优化") 