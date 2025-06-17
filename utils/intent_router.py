# 模块意图分流器
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, AIMessage
import yaml
import os

def load_router_config() -> Dict:
    """加载路由配置"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "router_config.yaml")
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading router config: {e}")
        return {}

def classify_rayware_intent(state: Dict[str, Any]) -> Dict[str, Any]:
    """分类用户意图"""
    print("\n📍 [Intent Router] 开始分类用户意图")
    print(f"📥 输入状态: {state}")
    
    try:
        # 获取消息历史
        messages = state.get("messages", [])
        if not messages:
            print("❌ 没有消息历史")
            state["rayware_intent"] = "error"
            return state

        # 获取最后一条用户消息
        human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
        if not human_messages:
            print("❌ 没有用户消息")
            state["rayware_intent"] = "error"
            return state

        last_human_message = human_messages[-1]
        user_input = last_human_message.content
        print(f"👤 分析用户消息: {user_input}")

        # 加载路由配置
        router_config = load_router_config()
        if not router_config:
            print("❌ 路由配置加载失败")
            state["rayware_intent"] = "error"
            return state

        # 遍历配置中的意图
        print("🔍 开始匹配意图...")
        for intent, config in router_config.items():
            keywords = config.get("keywords", [])
            description = config.get("description", "")
            print(f"检查意图 '{intent}' ({description})")
            
            # 检查关键词匹配
            if any(keyword in user_input for keyword in keywords):
                print(f"✅ 匹配到意图: {intent}")
                state["rayware_intent"] = intent
                # 添加意图确认消息
                messages.append(AIMessage(content=f"✅ 识别意图为：{intent}"))
                state["messages"] = messages
                print(f"📤 输出状态: {state}")
                return state

        # 如果没有匹配的意图
        print("❓ 未匹配到任何已知意图")
        state["rayware_intent"] = "unknown"
        messages.append(AIMessage(content="❓ 未能识别具体意图，请提供更多信息"))
        state["messages"] = messages
        print(f"📤 输出状态: {state}")
        return state

    except Exception as e:
        print(f"❌ 意图分类错误: {e}")
        state["rayware_intent"] = "error"
        print(f"📤 输出状态: {state}")
        return state


# def classify_rayware_intent(state):
#     last_message = state["messages"][-1].content
#     # 调用 LLM 进行意图分类（略）
#     intent = "new_print_job"  # 示例结果
#     reason = "用户明确提到了新建打印任务"
#
#     print("🤖 猜测意图返回:", {
#         "next": intent,
#         "reason": reason
#     })
#
#     return {"next": intent}  # ✅ 关键点

# classify_intent_node = RunnableLambda(classify_rayware_intent)