import sys
import os
import logging
import traceback
from typing import Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graphs.rayware_graph import create_print_job_node
from web_tools.web_toolkit import get_driver, auto_login

def test_create_print_job():
    """测试创建打印任务功能"""
    try:
        # 初始化 WebDriver
        logger.info("正在初始化 WebDriver...")
        driver = get_driver()
        if not driver:
            raise Exception("WebDriver 初始化失败")
            
        # 自动登录
        logger.info("正在执行自动登录...")
        login_result = auto_login.invoke({"user_desc": "wangyili"})
        if not login_result.get("status") == "success":
            raise Exception(f"登录失败: {login_result.get('message')}")
        
        # 准备测试状态
        state = {
            "user_input": "患者：测试患者",
            "messages": [],
            "rayware_intent": None,
            "last_error": None,
            "logged_in": True
        }
        
        # 调用创建打印任务节点
        logger.info("开始创建打印任务...")
        result = create_print_job_node(state)
        
        # 检查结果
        if result["rayware_intent"] == "submit_print_job":
            logger.info("✅ 测试成功：打印任务创建成功")
            logger.info(f"消息: {result['messages'][-1].content if result['messages'] else '无消息'}")
        else:
            logger.error("❌ 测试失败：打印任务创建失败")
            logger.error(f"错误信息: {result.get('last_error', '未知错误')}")
            logger.error(f"消息: {result['messages'][-1].content if result['messages'] else '无消息'}")
            
    except Exception as e:
        logger.error(f"❌ 测试过程中发生错误: {str(e)}")
        traceback.print_exc()
    finally:
        # 关闭浏览器
        if driver:
            driver.quit()
            logger.info("WebDriver 已关闭")

if __name__ == "__main__":
    test_create_print_job() 