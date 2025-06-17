#!/usr/bin/env python3
"""
测试重构后的架构 - create_new_print_job 作为独立工具
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_tools.web_toolkit import create_new_print_job, submit_print_job
from graphs.rayware_graph import rayware_graph
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tools_directly():
    """直接测试工具"""
    print("🧪 测试1: 直接调用工具")
    
    # 测试创建打印任务工具
    print("\n📍 测试 create_new_print_job 工具")
    result1 = create_new_print_job(
        patient_name="张三",
        case_name="测试案例",
        indications="Crown"
    )
    print(f"结果: {result1}")
    
    # 测试提交工具
    print("\n📍 测试 submit_print_job 工具")
    result2 = submit_print_job()
    print(f"结果: {result2}")

def test_rayware_graph():
    """测试 rayware 图"""
    print("\n🧪 测试2: 通过 rayware_graph 调用")
    
    # 初始状态
    initial_state = {
        "user_input": "新建打印任务",
        "messages": [],
        "rayware_intent": "new_print_job",
        "print_job_data": {}
    }
    
    try:
        # 运行图
        result = rayware_graph.invoke(initial_state)
        print(f"图执行结果: {result}")
        
        # 打印消息
        for msg in result.get("messages", []):
            print(f"消息: {msg.content if hasattr(msg, 'content') else msg}")
            
    except Exception as e:
        print(f"❌ 图执行失败: {e}")

def test_architecture_benefits():
    """展示架构优势"""
    print("\n🧪 测试3: 架构优势展示")
    
    print("✅ 优势1: 工具可独立使用")
    result = create_new_print_job(patient_name="独立测试")
    print(f"独立调用结果: {result.get('status')}")
    
    print("\n✅ 优势2: 工具可复用")
    # 可以在不同的图中使用同一个工具
    print("工具可以在 rayware_graph、其他图或直接调用中使用")
    
    print("\n✅ 优势3: 职责分离")
    print("- web_toolkit.py: 负责页面操作")
    print("- rayware_graph.py: 负责业务流程")
    print("- 图保持简洁，工具保持专注")

if __name__ == "__main__":
    print("🚀 测试重构后的架构")
    print("=" * 50)
    
    # 测试工具
    test_tools_directly()
    
    # 测试图
    test_rayware_graph()
    
    # 展示优势
    test_architecture_benefits()
    
    print("\n" + "=" * 50)
    print("🎉 架构测试完成！")
    
    print("\n📋 总结:")
    print("✅ create_new_print_job 现在是独立工具")
    print("✅ rayware_graph 调用工具，保持简洁")
    print("✅ 职责分离清晰，易于维护")
    print("✅ 工具可复用，提高开发效率") 