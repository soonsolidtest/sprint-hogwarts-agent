from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from state.types import MessagesState
from tools.llm_call import llm_call
from tools.should_continue import should_continue
from graphs.unknown import unknown_graph
from utils.intent_router import classify_rayware_intent
from web_tools.web_toolkit import selenium_get, selenium_click, selenium_sendkeys, smart_click, create_new_print_job, submit_print_job
from config import config
import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

logger = logging.getLogger(__name__)

# 定义 Rayware 子模块状态结构
class RaywareState(TypedDict):
    messages: List[BaseMessage]
    rayware_intent: str
    collected_fields: set
    error_count: int
    last_error: str
    test_config: Dict[str, Any]
    current_page: str
    print_job_data: Dict[str, Any]

def init_rayware_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """初始化 Rayware 状态"""
    logger.info("📍 初始化 Rayware 状态")
    
    if not isinstance(state, dict):
        state = {}
    
    state.setdefault("messages", [])
    state.setdefault("rayware_intent", "")
    state.setdefault("collected_fields", set())
    state.setdefault("error_count", 0)
    state.setdefault("last_error", "")
    state.setdefault("test_config", {})
    state.setdefault("current_page", "")
    state.setdefault("print_job_data", {})
    
    return state

def classify_intent_with_log(state: Dict[str, Any]) -> Dict[str, Any]:
    """分类意图并记录日志"""
    logger.info("📍 分类 Rayware 意图")
    
    state = init_rayware_state(state)
    try:
        # 获取最后一条用户消息
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, HumanMessage):
                user_input = last_message.content
                
                # 简单的意图识别
                if any(keyword in user_input for keyword in ['新建', '打印任务', '创建', '新增']):
                    intent = "new_print_job"
                elif any(keyword in user_input for keyword in ['历史', '查看', '最近']):
                    intent = "view_history"
                else:
                    intent = "unknown"
                
                logger.info(f"✅ 识别到意图: {intent}")
                state["rayware_intent"] = intent
                
                # 添加确认消息
                if intent == "new_print_job":
                    state["messages"].append(AIMessage(content="✅ 准备创建新的打印任务"))
                elif intent == "view_history":
                    state["messages"].append(AIMessage(content="✅ 准备查看打印历史"))
                else:
                    state["messages"].append(AIMessage(content="❓ 请明确您要执行的操作"))
            else:
                state["rayware_intent"] = "unknown"
        else:
            state["rayware_intent"] = "unknown"
            
    except Exception as e:
        logger.error(f"❌ 意图识别失败: {e}")
        state["rayware_intent"] = "error"
        state["last_error"] = str(e)
    
    return state

def navigate_to_rayware(state: Dict[str, Any]) -> Dict[str, Any]:
    """导航到 Rayware 主页"""
    logger.info("📍 导航到 Rayware 主页")
    
    try:
        # 检查是否已经在正确页面
        from web_tools.web_toolkit import get_driver, selenium_get, smart_click
        driver = get_driver()
        
        if driver is None:
            logger.error("❌ WebDriver 未初始化")
            state["last_error"] = "WebDriver 未初始化"
            state["rayware_intent"] = "error"
            return state
            
        current_url = driver.current_url
        logger.info(f"🔍 当前URL: {current_url}")
        
        # 检查是否已经在 rayware 页面
        if "print-setup" in current_url:
            logger.info("✅ 已在 Rayware 页面")
            state["current_page"] = "rayware"
            state["messages"].append(AIMessage(content="✅ 已在 Rayware 页面"))
            return state
        
        # 检查是否在 Design Service 系统内
        if "designservice.sprintray.com" in current_url:
            logger.info("🔍 已在 Design Service 系统内，尝试点击 Rayware 菜单")
            
            # 等待页面加载完成
            import time
            time.sleep(6)  # 增加等待时间
            
            # 尝试点击 Rayware 菜单按钮
            max_retries = 3
            for attempt in range(max_retries):
                logger.info(f"🔄 尝试点击 Rayware 菜单 (第 {attempt + 1} 次)")
                
                click_result = smart_click.invoke({
                    "param": {
                        "selectors": [
                            # 精确匹配 Angular 组件中的 Rayware 链接
                            {"by": "css", "value": "a[routerlink='/print-setup']"},
                            {"by": "css", "value": "a.nav-link[routerlink='/print-setup']"},
                            {"by": "css", "value": "a.nav-link-has-badge[routerlink='/print-setup']"},
                            {"by": "xpath", "value": "//a[@routerlink='/print-setup']"},
                            {"by": "xpath", "value": "//a[contains(@class, 'nav-link') and @routerlink='/print-setup']"},
                            # 通过文本内容匹配
                            {"by": "xpath", "value": "//span[contains(@class, 'nav-item-overflow') and contains(text(), 'RayWare')]"},
                            {"by": "xpath", "value": "//a[.//span[contains(text(), 'RayWare')]]"},
                            # 备用选择器
                            {"by": "css", "value": "a[href='/print-setup']"},
                            {"by": "xpath", "value": "//a[@href='/print-setup']"},
                            {"by": "text", "value": "RayWare"}
                        ],
                        "wait": 10,
                        "driver": driver  # 显式传递 driver 对象
                    }
                })
                
                if click_result.get("status") == "success":
                    logger.info("✅ 成功点击 Rayware 菜单")
                    state["current_page"] = "rayware"
                    state["messages"].append(AIMessage(content="✅ 已进入 Rayware 页面"))
                    
                    # 等待页面加载
                    time.sleep(3)
                    
                    # 验证是否成功进入 rayware 页面
                    new_url = driver.current_url
                    if "print-setup" in new_url:
                        logger.info(f"✅ 确认已进入 Rayware 页面: {new_url}")
                        return state
                    else:
                        logger.warning(f"⚠️ 点击后URL未变化: {new_url}")
                        if attempt < max_retries - 1:
                            time.sleep(2)  # 等待后重试
                            continue
                else:
                    logger.warning(f"⚠️ 点击失败 (第 {attempt + 1} 次): {click_result.get('message')}")
                    if attempt < max_retries - 1:
                        time.sleep(2)  # 等待后重试
                        continue
            
            # 如果所有点击尝试都失败，尝试直接导航
            logger.warning("⚠️ 所有点击尝试都失败，尝试直接导航")
            target_url = "https://dev.designservice.sprintray.com/print-setup"
            logger.info(f"🔄 直接导航到: {target_url}")
            
            # 修复参数格式
            result = selenium_get.invoke({
                "url": target_url,
                "driver": driver  # 显式传递 driver 对象
            })
            
            if result.get("status") == "success":
                logger.info("✅ 成功直接导航到 Rayware")
                state["current_page"] = "rayware"
                state["messages"].append(AIMessage(content="✅ 已进入 Rayware 页面"))
            else:
                logger.error(f"❌ 直接导航失败: {result.get('message')}")
                state["last_error"] = f"导航到 Rayware 失败: {result.get('message')}"
                state["rayware_intent"] = "error"
        else:
            logger.error("❌ 不在 Design Service 系统内，无法导航到 Rayware")
            state["last_error"] = "不在 Design Service 系统内，请先登录"
            state["rayware_intent"] = "error"
        
    except Exception as e:
        logger.error(f"❌ 导航过程中发生错误: {e}")
        state["last_error"] = str(e)
        state["rayware_intent"] = "error"
    
    return state

def create_print_job_node(state: dict) -> dict:
    """创建打印任务节点"""
    logger.info("开始创建打印任务...")
    
    try:
        # 创建新的打印任务
        result = create_new_print_job.invoke({
            "param": {
                "indication": "Crown",
                "orientation": "Automatic",
                "support_raft": False,
                "printer": "Pro55S",
                "build_platform": "Standard",
                "material": "Model Resin",
                "show_advanced": False,
                "layer_thickness": 100,
                "fit_offset": 0.0,
                "mesh_repair": True,
                "supports": True,
                "orientation_advanced": True,
                "layout": True,
                "file_source": "cloud"
            }
        })
        
        if result.get("status") != "success":
            raise Exception(f"创建打印任务失败: {result.get('message')}")
            
        logger.info("✅ 成功创建打印任务")
        
        # 更新状态
        state["print_job_created"] = True
        state["print_job_details"] = result.get("details", {})
        
        return state
        
    except Exception as e:
        logger.error(f"❌ 创建打印任务失败: {str(e)}")
        state["error"] = str(e)
        return state

def submit_job_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """提交任务节点 - 调用工具"""
    logger.info("📍 进入提交任务节点")
    
    try:
        # 调用提交打印任务工具
        result = submit_print_job.invoke({})
        
        if result.get("status") == "success":
            logger.info("✅ 打印任务提交成功")
            state["rayware_intent"] = "completed"
            state["messages"].append(AIMessage(content=f"🎉 {result.get('message')}"))
        else:
            logger.error(f"❌ 打印任务提交失败: {result.get('message')}")
            state["rayware_intent"] = "error"
            state["last_error"] = result.get("message")
            state["messages"].append(AIMessage(content=f"❌ {result.get('message')}"))
            
    except Exception as e:
        logger.error(f"❌ 提交任务节点执行失败: {e}")
        state["rayware_intent"] = "error"
        state["last_error"] = str(e)
        state["messages"].append(AIMessage(content=f"❌ 提交任务失败: {str(e)}"))
    
    return state

def handle_rayware_error(state: Dict[str, Any]) -> Dict[str, Any]:
    """处理 Rayware 错误"""
    logger.info("📍 处理 Rayware 错误")
    
    state = init_rayware_state(state)
    state["error_count"] += 1
    
    error_msg = state.get("last_error", "未知错误")
    state["messages"].append(AIMessage(content=f"❌ 操作失败: {error_msg}"))
    
    return state

# 构建 Rayware 图结构
logger.info("🔧 构建 Rayware 图结构")

builder = StateGraph(MessagesState)

# 添加节点
builder.add_node("classify_intent", classify_intent_with_log)
builder.add_node("navigate_to_rayware", navigate_to_rayware)
builder.add_node("create_print_job_node", create_print_job_node)
builder.add_node("submit_job_node", submit_job_node)
builder.add_node("handle_error", handle_rayware_error)
builder.add_node("unknown", unknown_graph)

# 设置入口点
builder.set_entry_point("classify_intent")

# 添加条件边
builder.add_conditional_edges(
    "classify_intent",
    lambda x: x.get("rayware_intent", "unknown"),
    {
        "new_print_job": "navigate_to_rayware",
        "view_history": "navigate_to_rayware", 
        "unknown": "unknown",
        "error": "handle_error"
    }
)

builder.add_conditional_edges(
    "navigate_to_rayware",
    lambda x: x.get("rayware_intent", "error"),
    {
        "new_print_job": "create_print_job_node",
        "view_history": "unknown",  # 暂时用 unknown 处理
        "error": "handle_error"
    }
)

builder.add_conditional_edges(
    "create_print_job_node",
    lambda x: x.get("rayware_intent", "error"),
    {
        "submit_print_job": "submit_job_node",
        "error": "handle_error"
    }
)

# 设置结束点
builder.add_edge("submit_job_node", END)
builder.add_edge("handle_error", END)
builder.add_edge("unknown", END)

logger.info("✅ Rayware 图结构构建完成")
rayware_module_graph = builder.compile()