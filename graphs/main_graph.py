from langgraph.graph import StateGraph, END
from state.types import MessagesState
from tools.llm_call import llm_call
from tools.tool_node import tool_node, handle_confirmation, invoke_tool
from tools.should_continue import should_continue
from graphs.rayware_graph import rayware_module_graph
from graphs.cloud_driver_graph import cloud_driver_module_graph
from graphs.cloud_design_graph import cloud_design_module_graph
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from utils.account_utils import load_accounts, parse_instruction
from typing import Dict, Any, List
from state.state_manager import StateManager
from tools.message_handler import MessageHandler
from tools.tool_executor import ToolExecutor
from langchain_openai import ChatOpenAI
from config import system_prompt
import logging
import json
import time
import os
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import yaml
from tools.manual_append_message import manual_append_message

logger = logging.getLogger(__name__)

def manual_append_message(message_cls):
    def _append(state: Dict[str, Any]) -> Dict[str, Any]:
        print("\n🔄 节点流转: append_user -> preprocess")
        messages = state.get("messages", [])
        messages.append(message_cls(content=state["input"]))
        return {**state, "messages": messages}
    return RunnableLambda(_append)


def preprocess_input(state: Dict[str, Any]) -> Dict[str, Any]:
    """预处理输入，识别意图"""
    print("\n🔄 节点流转: preprocess -> llm_call")
    return state


def main():
    """主函数"""
    print("\n🚀 [Main Graph] 开始执行主函数")
    
    accounts = load_accounts()
    try:
        instruction = input("请输入测试指令：\n")
    except Exception:
        instruction = "测试默认指令"
    
    test_config = parse_instruction(instruction, accounts)
    
    # 创建初始消息
    initial_message = HumanMessage(content=instruction)
    
    # 使用字典创建状态
    state = {
        "messages": [initial_message],
        "input": instruction,
        "rayware_intent": "",
        "module": "",
        "test_config": test_config,
        "error_count": 0,
        "last_error": "",
        "collected_fields": set()
    }
    
    print("\n📍 开始测试对话系统")
    print(f"📝 测试配置: {test_config}")
    print("\n🔄 图的流转信息:")
    
    try:
        result = main_graph.invoke(state)
        print("\n✅ 测试完成!")
        print(f"📤 最终状态: {result}")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()

def main_graph(state: Dict[str, Any]) -> Dict[str, Any]:
    """主图，控制流程执行"""
    # 如果用户要求停止，直接返回
    if state.get("should_stop", False):
        return state
    
    # 如果正在等待用户确认，处理确认
    if state.get("waiting_for_confirmation", False):
        return handle_confirmation(state)
    
    # 否则继续正常流程
    messages = state.get("messages", [])
    if not messages:
        return state
    
    last_message = messages[-1]
    
    # 如果是用户消息，调用 LLM
    if isinstance(last_message, HumanMessage):
        return llm_call(state)
    
    # 如果是 AI 消息且包含工具调用，执行工具
    elif isinstance(last_message, AIMessage) and last_message.tool_calls:
        return tool_node(state)
    
    # 其他情况，继续执行
    return should_continue(state)

class MainGraph:
    """主图"""
    
    def __init__(self):
        """初始化"""
        self.state_manager = StateManager()
        self.message_handler = MessageHandler(self.state_manager)
        self.tool_executor = ToolExecutor(self.state_manager, self.message_handler)
        
        # 从 config.yaml 读取 LLM 配置
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        llm_config = config.get("llm", {})
        api_key = llm_config.get("api_key")
        api_base = llm_config.get("api_base", "https://api.deepseek.com/v1")
        model = llm_config.get("model", "deepseek-chat")
        
        if not api_key:
            raise ValueError("llm.api_key not set in config.yaml")
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=0,
            api_key=api_key,
            base_url=api_base
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """处理状态"""
        try:
            # 1. 更新状态管理器
            self.state_manager.update(state)
            
            # 2. 检查是否应该停止
            if state.get("should_stop", False):
                logger.info("Process stopped by user")
                return self.state_manager.get_state()
            
            # 3. 检查用户交互超时
            if self.state_manager.check_user_interaction_timeout():
                logger.warning("User interaction timeout")
                state["should_stop"] = True
                state["messages"].append(AIMessage(content="用户交互超时，任务已停止"))
                self.state_manager.update(state)
                return state
            
            # 4. 处理消息
            last_message = state["messages"][-1] if state["messages"] else None
            if isinstance(last_message, HumanMessage):
                # 处理用户消息
                if state.get("waiting_for_confirmation"):
                    if last_message.content.lower() == "n":
                        state["should_stop"] = True
                        state["waiting_for_confirmation"] = False
                        self.state_manager.update(state)
                        return state
                    elif last_message.content.lower() == "y":
                        state["waiting_for_confirmation"] = False
                        self.state_manager.update(state)
                        return state
                
                # 调用 LLM 处理用户输入
                try:
                    # 修改系统提示，强调只返回一个工具调用
                    custom_system_prompt = """你是一个网页自动化测试 Agent，专门用于测试SprintRay的Rayware系统。

重要：你只需要返回下一步要执行的单个操作，不要模拟执行结果！

严格按照以下格式回复：
```
{
  "action": "工具名称",
  "action_input": {
    "参数": "值"
  }
}
```

可用的工具：
- selenium_get: 打开指定网址，参数：{"url": "网址"}
- selenium_click: 点击指定元素，参数：{"locator": "选择器", "locator_type": "类型"}
- selenium_sendkeys: 输入指定内容，参数：{"selector": {"by": "类型", "value": "选择器"}, "text": "内容"}
- selenium_wait_for_element: 等待元素加载，参数：{"selector": {"by": "类型", "value": "选择器"}}
- selenium_quit: 退出浏览器
- auto_login: 根据用户描述自动登录，参数：{"user_desc": "用户描述"}
- login_with_credentials: 使用具体凭据登录，参数：{"url": "网址", "username": "用户名", "password": "密码"}

严格规则：
1. 只返回一个JSON格式的工具调用
2. 不要添加"No Thought"、"Observation"等文本
3. 不要模拟执行结果
4. 专注于下一步需要执行的操作

登录工具使用说明：
- 当用户说"用[用户名]登录"时，使用 auto_login 工具，参数为 {"user_desc": "用户名"}
- 当需要直接使用用户名密码登录时，使用 login_with_credentials 工具
- 登录工具会自动使用智能点击功能来处理登录按钮

示例：
- "用user1登录" -> {"action": "auto_login", "action_input": {"user_desc": "user1"}}
- 直接登录 -> {"action": "login_with_credentials", "action_input": {"url": "网址", "username": "用户名", "password": "密码"}}"""
                    
                    # 添加系统提示
                    messages = [SystemMessage(content=custom_system_prompt)] + state["messages"]
                    response = self.llm.invoke(messages)
                    print(f"🤖 LLM响应: {response.content}")
                    
                    if isinstance(response, AIMessage):
                        # 解析响应中的工具调用
                        content = response.content
                        action = None
                        
                        # 查找JSON格式的action
                        start = content.find('{')
                        if start != -1:
                            brace_count = 0
                            end = start
                            for i, char in enumerate(content[start:], start):
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        end = i + 1
                                        break
                            
                            if end > start:
                                action_str = content[start:end]
                                try:
                                    action = json.loads(action_str)
                                    print(f"✅ 成功解析action: {action}")
                                except json.JSONDecodeError as e:
                                    print(f"❌ Action解析失败: {e}")
                                    # 尝试从```块中解析
                                    start = content.find('```')
                                    if start != -1:
                                        end = content.find('```', start + 3)
                                        if end != -1:
                                            action_str = content[start + 3:end].strip()
                                            if action_str.startswith('json'):
                                                action_str = action_str[4:].strip()
                                            try:
                                                action = json.loads(action_str)
                                                print(f"✅ 从代码块成功解析action: {action}")
                                            except json.JSONDecodeError:
                                                print("❌ 代码块Action解析失败")
                        
                        # 如果解析到了action，创建工具调用
                        if action and 'action' in action and 'action_input' in action:
                            # 创建包含工具调用的新响应
                            tool_call = {
                                "id": f"call_{hash(str(action))}", 
                                "name": action["action"],
                                "args": action["action_input"]
                            }
                            print(f"🔧 创建tool_call: {tool_call}")
                            
                            response = AIMessage(
                                content=json.dumps(action, ensure_ascii=False, indent=2),
                                tool_calls=[tool_call]
                            )
                        
                        state["messages"].append(response)
                        self.state_manager.update(state)
                        
                        # 处理工具调用
                        if hasattr(response, "tool_calls") and response.tool_calls:
                            tool_call = response.tool_calls[0]
                            try:
                                print(f"⚙️ 执行工具: {tool_call['name']}")
                                print(f"📝 工具参数: {tool_call['args']}")
                                
                                # 执行工具
                                result = invoke_tool(tool_call["name"], tool_call["args"])
                                tool_message = ToolMessage(
                                    content=str(result),
                                    tool_call_id=tool_call["id"]
                                )
                                state["messages"].append(tool_message)
                                
                                # 检查是否是登录成功，如果是则检查后续操作
                                if tool_call["name"] in ["auto_login", "login_with_credentials"]:
                                    if isinstance(result, dict) and result.get("status") == "success":
                                        logger.info("✅ 登录成功，检查是否需要执行后续操作")
                                        
                                        # 检查用户输入是否包含后续操作意图
                                        user_input = state.get("input", "")
                                        if any(keyword in user_input for keyword in ['新建', '打印任务', '创建', '新增']):
                                            logger.info("🎯 检测到新建打印任务意图，准备调用 rayware 图")
                                            
                                            # 添加一个新的用户消息来触发 rayware 图
                                            rayware_message = HumanMessage(content="新建打印任务")
                                            state["messages"].append(rayware_message)
                                            
                                            # 调用 rayware 图
                                            try:
                                                logger.info("🔄 调用 rayware 图处理新建打印任务")
                                                
                                                rayware_result = rayware_module_graph.invoke(state)
                                                
                                                # 更新状态
                                                if rayware_result:
                                                    state.update(rayware_result)
                                                    logger.info("✅ rayware 图执行完成")
                                                
                                            except Exception as rayware_error:
                                                logger.error(f"❌ rayware 图执行失败: {rayware_error}")
                                                state["messages"].append(AIMessage(
                                                    content=f"❌ 执行打印任务操作失败: {str(rayware_error)}"
                                                ))
                                        
                                        elif any(keyword in user_input for keyword in ['历史', '查看', '最近']):
                                            logger.info("🎯 检测到查看历史意图")
                                    state["messages"].append(AIMessage(
                                                content="✅ 登录成功，准备查看打印历史"
                                    ))
                                
                                self.state_manager.update(state)
                                
                            except Exception as e:
                                print(f"❌ 工具执行失败: {e}")
                                logger.error(f"Tool execution error: {e}")
                                self.state_manager.record_error(e, {"state": state})
                                tool_message = ToolMessage(
                                    content=f"工具执行失败: {str(e)}",
                                    tool_call_id=tool_call.get("id", "unknown")
                                )
                                state["messages"].append(tool_message)
                                self.state_manager.update(state)
                        else:
                            print("❌ 未找到有效的工具调用")
                            # 如果没有工具调用，添加一个默认响应
                            state["messages"].append(AIMessage(content="我理解您的请求，但需要更具体的操作指令。"))
                            self.state_manager.update(state)
                    else:
                        # 如果 LLM 返回的不是 AI 消息，添加一个默认响应
                        state["messages"].append(AIMessage(content="我理解您的请求，让我来处理。"))
                        self.state_manager.update(state)
                except Exception as e:
                    logger.error(f"LLM invocation error: {e}")
                    self.state_manager.record_error(e, {"state": state})
                    state["messages"].append(AIMessage(content="抱歉，我遇到了一些问题，请重试。"))
                    self.state_manager.update(state)
            
            elif isinstance(last_message, ToolMessage):
                # 处理工具消息
                if state.get("current_tool"):
                    try:
                        content = json.loads(last_message.content) if isinstance(last_message.content, str) else last_message.content
                        if content.get("status") == "success":
                            state["current_tool"].complete(content)
                            # 检查是否需要用户确认
                            if state["current_tool"].tool_name in ["selenium_click", "selenium_sendkeys"]:
                                state["waiting_for_confirmation"] = True
                                state["messages"].append(AIMessage(
                                    content=f"工具 {state['current_tool'].tool_name} 执行成功，是否继续？(y/n)"
                                ))
                        else:
                            state["current_tool"].fail(Exception(content.get("message", "Unknown error")))
                            state["waiting_for_confirmation"] = True
                            state["messages"].append(AIMessage(
                                content=f"工具执行失败: {content.get('message', 'Unknown error')}，是否重试？(y/n)"
                            ))
                        self.state_manager.update(state)
                    except Exception as e:
                        logger.error(f"Error processing tool message: {e}")
                        self.state_manager.record_error(e, {"state": state})
                        state["waiting_for_confirmation"] = True
                        state["messages"].append(AIMessage(
                            content=f"处理工具消息失败: {str(e)}，是否重试？(y/n)"
                        ))
                        self.state_manager.update(state)
            
            return self.state_manager.get_state()
            
        except Exception as e:
            logger.error(f"Process error: {e}")
            self.state_manager.record_error(e, {"state": state})
            return self.state_manager.get_state()

# 创建主图实例
main_graph = MainGraph()

def process_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """处理状态的入口函数"""
    return main_graph.process(state)
