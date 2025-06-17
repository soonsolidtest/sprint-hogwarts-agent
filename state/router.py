from typing import Dict, Any
from langchain.schema import HumanMessage, AIMessage

def route_to_module(state: Dict[str, Any]) -> Dict[str, Any]:
    """根据意图路由到对应模块"""
    print("\n📍 [Router] 开始路由到模块")
    print(f"📥 输入状态: {state}")
    
    try:
        intent = state.get("rayware_intent", "unknown")
        print(f"🔍 当前意图: {intent}")
        
        # 设置模块
        if intent == "rayware":
            state["module"] = "rayware"
        elif intent == "unknown":
            state["module"] = "unknown"
        else:
            state["module"] = "error"
            
        print(f"✅ 路由到模块: {state['module']}")
        
        # 添加路由确认消息
        messages = state.get("messages", [])
        messages.append(AIMessage(content=f"✅ 路由到模块：{state['module']}"))
        state["messages"] = messages
        
        print(f"📤 输出状态: {state}")
        return state
        
    except Exception as e:
        print(f"❌ 路由错误: {e}")
        state["module"] = "error"
        state["error_count"] = state.get("error_count", 0) + 1
        state["last_error"] = str(e)
        return state 