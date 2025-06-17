from typing import Dict, Any, List
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from utils.intent_router import classify_rayware_intent

def classify_intent_with_log(messages: List[Dict[str, Any]]) -> str:
    """分类意图并记录日志"""
    print("\n📍 [Intent Classifier] 开始分类意图")
    print(f"📥 输入消息: {messages}")
    
    try:
        # 获取最后一条用户消息
        human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
        if not human_messages:
            print("❌ 没有用户消息")
            return "unknown"
            
        last_human_message = human_messages[-1]
        user_input = last_human_message.content
        print(f"👤 分析用户消息: {user_input}")
        
        # 调用意图分类
        intent = classify_rayware_intent({"messages": messages})
        print(f"✅ 识别到意图: {intent}")
        
        return intent
        
    except Exception as e:
        print(f"❌ 意图分类错误: {e}")
        return "unknown" 