#!/usr/bin/env python3
"""
登录后新建打印任务示例
演示如何使用框架进行登录并自动创建打印任务
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import HumanMessage
from graphs.main_graph import main_graph
from state.types import MessagesState
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def demo_login_and_create_print_job():
    """演示登录后创建打印任务的完整流程"""
    
    print("🚀 登录后新建打印任务演示")
    print("=" * 50)
    
    # 示例1: 用 wangyili 登录并新建打印任务
    test_cases = [
        "用wangyili登录并新建打印任务",
        "请用user1登录然后创建一个新的打印任务", 
        "用wangyili登录，我要新建打印任务"
    ]
    
    for i, instruction in enumerate(test_cases, 1):
        print(f"\n📝 测试案例 {i}: {instruction}")
        print("-" * 30)
        
        # 创建初始状态
        initial_message = HumanMessage(content=instruction)
        state = {
            "messages": [initial_message],
            "input": instruction,
            "rayware_intent": "",
            "module": "",
            "test_config": {},
            "error_count": 0,
            "last_error": "",
            "collected_fields": set(),
            "should_stop": False,
            "waiting_for_confirmation": False
        }
        
        try:
            # 执行主图处理
            logger.info(f"🔄 开始处理指令: {instruction}")
            result = main_graph.process(state)
            
            # 输出结果
            if result and result.get("messages"):
                last_message = result["messages"][-1]
                print(f"✅ 执行结果: {last_message.content}")
            else:
                print("❌ 未获得有效结果")
                
        except Exception as e:
            logger.error(f"❌ 执行失败: {e}")
            print(f"❌ 执行失败: {str(e)}")
        
        print("\n" + "="*50)

def interactive_demo():
    """交互式演示"""
    print("\n🎮 交互式演示模式")
    print("输入指令来测试登录后新建打印任务功能")
    print("示例指令:")
    print("  - 用wangyili登录并新建打印任务")
    print("  - 请用user1登录然后创建打印任务")
    print("  - 输入 'quit' 退出")
    print("-" * 50)
    
    while True:
        try:
            instruction = input("\n> 请输入指令: ").strip()
            
            if instruction.lower() in ['quit', 'exit', '退出']:
                print("👋 再见！")
                break
            
            if not instruction:
                continue
            
            # 创建状态
            initial_message = HumanMessage(content=instruction)
            state = {
                "messages": [initial_message],
                "input": instruction,
                "rayware_intent": "",
                "module": "",
                "test_config": {},
                "error_count": 0,
                "last_error": "",
                "collected_fields": set(),
                "should_stop": False,
                "waiting_for_confirmation": False
            }
            
            # 执行处理
            logger.info(f"🔄 处理指令: {instruction}")
            result = main_graph.process(state)
            
            # 显示结果
            if result and result.get("messages"):
                print("\n📋 执行过程:")
                for msg in result["messages"][-3:]:  # 显示最后3条消息
                    if hasattr(msg, 'content'):
                        print(f"  {type(msg).__name__}: {msg.content}")
            
        except KeyboardInterrupt:
            print("\n👋 用户中断，退出程序")
            break
        except Exception as e:
            logger.error(f"❌ 处理失败: {e}")
            print(f"❌ 处理失败: {str(e)}")

if __name__ == "__main__":
    print("选择运行模式:")
    print("1. 自动演示 (运行预设测试案例)")
    print("2. 交互式演示 (手动输入指令)")
    
    try:
        choice = input("请选择 (1/2): ").strip()
        
        if choice == "1":
            demo_login_and_create_print_job()
        elif choice == "2":
            interactive_demo()
        else:
            print("❌ 无效选择，退出程序")
            
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"❌ 程序执行失败: {str(e)}") 