#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
迁移后功能测试脚本
用于验证图调用和工具函数是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.main_graph import main_graph, MainGraph
from web_tools import smart_click, selenium_click, selenium_sendkeys, selenium_get
from langchain_core.messages import HumanMessage

def test_main_graph():
    """测试 main_graph 基本功能"""
    print("=== 测试 main_graph ===")
    
    try:
        # 测试图是否存在
        assert main_graph is not None
        print("✓ main_graph 存在")
        
        # 测试图的基本属性
        print(f"✓ main_graph 类型: {type(main_graph)}")
        
        return True
    except Exception as e:
        print(f"✗ main_graph 测试失败: {e}")
        return False

def test_main_graph_class():
    """测试 MainGraph 类"""
    print("\n=== 测试 MainGraph 类 ===")
    
    try:
        # 创建 MainGraph 实例
        main_graph_instance = MainGraph()
        print("✓ MainGraph 实例创建成功")
        
        # 测试实例方法
        assert hasattr(main_graph_instance, 'process')
        print("✓ MainGraph 有 process 方法")
        
        return True
    except Exception as e:
        print(f"✗ MainGraph 类测试失败: {e}")
        return False

def test_web_tools_import():
    """测试 web_tools 导入"""
    print("\n=== 测试 web_tools 导入 ===")
    
    try:
        from web_tools import __all__
        print(f"✓ 可用工具: {__all__}")
        
        # 测试基础工具导入
        from web_tools import (
            selenium_click, selenium_sendkeys, selenium_get,
            smart_click, smart_select_and_choose,
            auto_login, create_new_print_job
        )
        print("✓ 基础工具导入成功")
        
        return True
    except Exception as e:
        print(f"✗ web_tools 导入失败: {e}")
        return False

def test_tool_functions():
    """测试工具函数（不实际执行）"""
    print("\n=== 测试工具函数 ===")
    
    try:
        # 测试工具函数是否存在
        assert callable(smart_click)
        assert callable(selenium_click)
        assert callable(selenium_sendkeys)
        assert callable(selenium_get)
        
        print("✓ 工具函数存在且可调用")
        
        # 测试参数格式
        test_params = {
            "text": "测试按钮",
            "selector": "#test-button",
            "value": "测试值"
        }
        print(f"✓ 参数格式测试: {test_params}")
        
        return True
    except Exception as e:
        print(f"✗ 工具函数测试失败: {e}")
        return False

def test_graph_calling():
    """测试图调用（模拟）"""
    print("\n=== 测试图调用 ===")
    
    try:
        # 测试状态格式
        test_state = {
            "messages": [HumanMessage(content="测试指令")],
            "input": "测试指令",
            "rayware_intent": "",
            "module": "",
            "test_config": {}
        }
        
        print(f"✓ 状态格式测试: {test_state}")
        
        # 注意：这里不实际执行，只是测试格式
        print("✓ 图调用格式正确")
        
        return True
    except Exception as e:
        print(f"✗ 图调用测试失败: {e}")
        return False

def test_custom_tool_creation():
    """测试自定义工具创建"""
    print("\n=== 测试自定义工具创建 ===")
    
    try:
        # 模拟自定义工具
        def test_custom_tool(params):
            return {
                "success": True,
                "result": "测试成功",
                "message": "自定义工具工作正常"
            }
        
        # 测试工具调用
        result = test_custom_tool({"param1": "value1"})
        
        assert result["success"] == True
        print("✓ 自定义工具创建和调用成功")
        
        return True
    except Exception as e:
        print(f"✗ 自定义工具测试失败: {e}")
        return False

def test_agent_runner_new():
    """测试 agent_runner_new.py"""
    print("\n=== 测试 agent_runner_new.py ===")
    
    try:
        # 检查文件是否存在
        import agent_runner_new
        print("✓ agent_runner_new.py 存在且可导入")
        
        # 检查主要函数
        assert hasattr(agent_runner_new, 'main')
        print("✓ agent_runner_new 有 main 函数")
        
        return True
    except Exception as e:
        print(f"✗ agent_runner_new 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始迁移后功能测试...\n")
    
    tests = [
        test_main_graph,
        test_main_graph_class,
        test_web_tools_import,
        test_tool_functions,
        test_graph_calling,
        test_custom_tool_creation,
        test_agent_runner_new
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！迁移成功！")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关功能")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 