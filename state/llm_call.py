from typing import Dict, Any, List
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from utils.intent_router import classify_rayware_intent
import json

def llm_call(state: Dict[str, Any]) -> Dict[str, Any]:
    """调用LLM处理用户输入"""
    print("\n📍 [LLM Call] 开始处理用户输入")
    print(f"📥 输入状态: {state}")
    
    try:
        messages = state.get("messages", [])
        if not messages:
            print("❌ 没有消息历史")
            return state
            
        # 获取最后一条用户消息
        human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
        if not human_messages:
            print("❌ 没有用户消息")
            return state
            
        last_human_message = human_messages[-1]
        user_input = last_human_message.content
        print(f"👤 处理用户消息: {user_input}")
        
        # 首先进行意图分类
        state = classify_rayware_intent(state)
        intent = state.get("rayware_intent", "unknown")
        print(f"🎯 识别到意图: {intent}")
        
        # 如果是未知意图，创建系统消息要求用户提供更多信息
        if intent == "unknown":
            system_prompt = """你是一个智能助手。用户的输入不够清晰，请引导用户提供更多关于Rayware系统测试的信息。
可以询问用户是否需要：
1. 新建打印任务
2. 查看打印历史
3. 其他Rayware相关操作"""
        else:
            system_prompt = """你是一个智能助手。请根据用户的意图提供相应的帮助。"""
        
        system = SystemMessage(content=system_prompt)
        
        # 如果有测试配置，添加到系统消息
        if state.get("test_config"):
            config_msg = f"\n当前测试配置: {state['test_config']}"
            system = SystemMessage(content=system_prompt + config_msg)
            print(f"🔧 添加测试配置到系统消息: {config_msg}")
        
        # 根据意图生成响应
        if intent == "unknown":
            response = "我理解您想使用Rayware系统，但需要更具体的信息。您是想要：\n1. 新建打印任务\n2. 查看打印历史\n3. 还是有其他需求？"
        elif intent == "error":
            response = "抱歉，处理您的请求时遇到了问题。请重试或提供更清晰的指令。"
        else:
            response = f"好的，我来帮您处理{intent}相关的操作。"
            
        print(f"🤖 生成响应: {response}")
        
        # 创建AI消息
        ai_message = AIMessage(content=response)
        messages.append(ai_message)
        state["messages"] = messages
        
        print(f"📤 输出状态: {state}")
        return state
        
    except Exception as e:
        print(f"❌ LLM调用错误: {e}")
        messages = state.get("messages", [])
        messages.append(AIMessage(content=f"处理出错: {str(e)}"))
        state["messages"] = messages
        state["error_count"] = state.get("error_count", 0) + 1
        state["last_error"] = str(e)
        return state 