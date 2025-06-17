import unittest
from state.state_manager import StateManager
from tools.message_handler import MessageHandler
from tools.tool_executor import ToolExecutor, ToolContext
from graphs.main_graph import MainGraph
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import time
import os
import json

class TestFramework(unittest.TestCase):
    def setUp(self):
        """测试前准备"""
        # 设置环境变量
        os.environ["OPENAI_API_KEY"] = "test_key"
        
        self.main_graph = MainGraph()
        self.state = {
            "messages": [],
            "should_stop": False,
            "waiting_for_confirmation": False,
            "browser_opened": False,
            "logged_in": False,
            "current_page": "",
            "collected_fields": set(),
            "last_user_interaction": time.time(),
            "interaction_timeout": 300  # 5分钟超时
        }
    
    def test_basic_flow(self):
        """测试基本流程"""
        # 1. 用户输入
        self.state["messages"].append(HumanMessage(content="开始打印任务"))
        
        # 模拟 LLM 响应
        def mock_invoke(messages):
            return AIMessage(
                content="",
                additional_kwargs={
                    "tool_calls": [{
                        "id": "test_1",
                        "type": "function",
                        "function": {
                            "name": "selenium_get",
                            "arguments": '{"url": "https://example.com"}'
                        }
                    }]
                }
            )
        
        self.main_graph.llm.invoke = mock_invoke
        
        state = self.main_graph.process(self.state)
        self.assertFalse(state["should_stop"])
        
        # 2. AI响应
        self.assertTrue(len(state["messages"]) > 0)
        last_message = state["messages"][-1]
        self.assertIsInstance(last_message, (AIMessage, ToolMessage))
        
        # 3. 工具调用
        if isinstance(last_message, AIMessage) and hasattr(last_message, "tool_calls"):
            tool_call = last_message.tool_calls[0]
            self.assertEqual(tool_call["name"], "selenium_get")
    
    def test_error_handling(self):
        """测试错误处理"""
        # 1. 模拟工具执行错误
        self.state["messages"].append(AIMessage(
            content="",
            additional_kwargs={
                "tool_calls": [{
                    "id": "test_1",
                    "type": "function",
                    "function": {
                        "name": "selenium_get",
                        "arguments": '{"url": "invalid_url"}'
                    }
                }]
            }
        ))
        
        # 设置当前工具
        self.state["current_tool"] = ToolContext(
            tool_name="selenium_get",
            args={"url": "invalid_url"},
            start_time=time.time()
        )
        
        # 模拟工具执行失败
        def mock_execute_tool(*args, **kwargs):
            raise Exception("Tool execution failed")
        
        self.main_graph.tool_executor.execute_tool = mock_execute_tool
        
        state = self.main_graph.process(self.state)
        self.assertFalse(state["should_stop"])
        self.assertTrue(state["waiting_for_confirmation"])
        
        # 2. 用户确认重试
        self.state["messages"].append(HumanMessage(content="y"))
        state = self.main_graph.process(self.state)
        self.assertFalse(state["should_stop"])
    
    def test_user_confirmation(self):
        """测试用户确认"""
        # 1. 模拟需要确认的工具执行
        self.state["current_tool"] = ToolContext(
            tool_name="selenium_click",
            args={},
            start_time=time.time()
        )
        self.state["messages"].append(ToolMessage(
            content=json.dumps({"status": "success", "message": "点击成功"}),
            tool_call_id="selenium_click_1"
        ))
        
        state = self.main_graph.process(self.state)
        self.assertTrue(state["waiting_for_confirmation"])
        
        # 2. 用户确认继续
        self.state["messages"].append(HumanMessage(content="y"))
        state = self.main_graph.process(self.state)
        self.assertFalse(state["waiting_for_confirmation"])
        
        # 3. 用户选择停止
        self.state["current_tool"] = ToolContext(
            tool_name="selenium_click",
            args={},
            start_time=time.time()
        )
        self.state["messages"].append(ToolMessage(
            content=json.dumps({"status": "success", "message": "点击成功"}),
            tool_call_id="selenium_click_2"
        ))
        state = self.main_graph.process(self.state)
        self.state["messages"].append(HumanMessage(content="n"))
        state = self.main_graph.process(self.state)
        self.assertTrue(state["should_stop"])
    
    def test_timeout_handling(self):
        """测试超时处理"""
        # 1. 设置超时状态
        self.state["last_user_interaction"] = time.time() - 301  # 超过5分钟
        
        state = self.main_graph.process(self.state)
        self.assertTrue(state["should_stop"])
        self.assertTrue(any("超时" in msg.content for msg in state["messages"]))
    
    def test_state_management(self):
        """测试状态管理"""
        # 1. 更新状态
        self.state["browser_opened"] = True
        self.state["current_page"] = "https://example.com"
        
        state = self.main_graph.process(self.state)
        self.assertTrue(state["browser_opened"])
        self.assertEqual(state["current_page"], "https://example.com")
        
        # 2. 状态回滚
        self.main_graph.state_manager.rollback()
        state = self.main_graph.state_manager.get_state()
        self.assertFalse(state["browser_opened"])
        self.assertEqual(state["current_page"], "")
    
    def test_tool_execution(self):
        """测试工具执行"""
        # 1. 检查工具注册
        tools = self.main_graph.tool_executor.tools
        self.assertIn("selenium_get", tools)
        self.assertIn("selenium_click", tools)
        
        # 2. 检查工具状态
        status = self.main_graph.tool_executor.get_all_tools_status()
        self.assertIn("selenium_get", status)
        self.assertEqual(status["selenium_get"]["total_executions"], 0)
    
    def test_message_handling(self):
        """测试消息处理"""
        # 1. 处理用户消息
        message = HumanMessage(content="测试消息")
        self.state["messages"] = [message]
        
        # 模拟 LLM 响应
        def mock_invoke(messages):
            return AIMessage(content="AI响应")
        
        self.main_graph.llm.invoke = mock_invoke
        
        state = self.main_graph.process(self.state)
        self.assertEqual(len(state["messages"]), 2)
        self.assertEqual(state["messages"][0], message)
        self.assertEqual(state["messages"][1].content, "AI响应")
        
        # 2. 处理工具消息
        message = ToolMessage(
            content=json.dumps({"status": "success"}),
            tool_call_id="test_1"
        )
        self.state["messages"] = [message]
        self.state["current_tool"] = ToolContext(
            tool_name="selenium_click",
            args={},
            start_time=time.time()
        )
        
        state = self.main_graph.process(self.state)
        self.assertEqual(len(state["messages"]), 2)
        self.assertEqual(state["messages"][0], message)
        self.assertTrue("是否继续" in state["messages"][1].content)

if __name__ == "__main__":
    unittest.main() 