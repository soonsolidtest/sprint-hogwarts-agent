"""
打印机选择器集成测试模块
"""

import pytest
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from web_tools.web_toolkit import PrinterSelector, select_printer

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def driver():
    """创建 WebDriver 实例"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()

@pytest.fixture(scope="module")
def printer_selector(driver):
    """创建打印机选择器实例"""
    return PrinterSelector(driver)

def test_select_connected_printer_integration(printer_selector):
    """测试选择已连接打印机的完整流程"""
    try:
        # 1. 导航到测试页面
        printer_selector.driver.get("https://dev.account.sprintray.com/")
        time.sleep(2)  # 等待页面加载

        # 2. 选择打印机
        result = printer_selector.select_printer("Pro55S", "connected")

        # 3. 验证结果
        assert result["success"] is True
        assert "成功选择打印机" in result["message"]

    except Exception as e:
        logger.error(f"集成测试失败: {str(e)}")
        pytest.fail(f"集成测试失败: {str(e)}")

def test_select_virtual_printer_integration(printer_selector):
    """测试选择虚拟打印机的完整流程"""
    try:
        # 1. 导航到测试页面
        printer_selector.driver.get("https://dev.account.sprintray.com/")
        time.sleep(2)  # 等待页面加载

        # 2. 选择打印机
        result = printer_selector.select_printer("Midas", "virtual")

        # 3. 验证结果
        assert result["success"] is True
        assert "成功选择打印机" in result["message"]

    except Exception as e:
        logger.error(f"集成测试失败: {str(e)}")
        pytest.fail(f"集成测试失败: {str(e)}")

def test_tool_function_integration(driver):
    """测试工具函数的完整流程"""
    try:
        # 1. 导航到测试页面
        driver.get("https://dev.account.sprintray.com/")
        time.sleep(2)  # 等待页面加载

        # 2. 使用工具函数选择打印机
        result = select_printer({
            "printer": "Pro55S",
            "printer_type": "connected",
            "wait": 10
        })

        # 3. 验证结果
        assert result["success"] is True
        assert "成功选择打印机" in result["message"]

        # 4. 测试选择虚拟打印机
        result = select_printer({
            "printer": "Midas",
            "printer_type": "virtual",
            "wait": 10
        })

        # 5. 验证结果
        assert result["success"] is True
        assert "成功选择打印机" in result["message"]

    except Exception as e:
        logger.error(f"工具函数集成测试失败: {str(e)}")
        pytest.fail(f"工具函数集成测试失败: {str(e)}")

def test_error_handling_integration(printer_selector):
    """测试错误处理的完整流程"""
    try:
        # 1. 测试缺少打印机参数
        result = printer_selector.select_printer("")
        assert result["success"] is False
        assert "缺少必要的参数" in result["message"]

        # 2. 测试无效的打印机类型
        result = printer_selector.select_printer("Test", "invalid_type")
        assert result["success"] is False

        # 3. 测试不存在的打印机
        result = printer_selector.select_printer("NonExistentPrinter")
        assert result["success"] is False
        assert "未找到" in result["message"]

    except Exception as e:
        logger.error(f"错误处理集成测试失败: {str(e)}")
        pytest.fail(f"错误处理集成测试失败: {str(e)}")

def test_performance_integration(printer_selector):
    """测试性能相关的完整流程"""
    try:
        # 1. 测试快速连续选择
        start_time = time.time()
        
        result1 = printer_selector.select_printer("Pro55S", "connected", wait_time=5)
        result2 = printer_selector.select_printer("Midas", "virtual", wait_time=5)
        
        end_time = time.time()
        execution_time = end_time - start_time

        # 验证结果
        assert result1["success"] is True
        assert result2["success"] is True
        assert execution_time < 20  # 总执行时间应小于20秒

        # 2. 测试超时处理
        result = printer_selector.select_printer("Pro55S", wait_time=1)  # 设置较短的超时时间
        assert "超时" in result.get("message", "") or not result["success"]

    except Exception as e:
        logger.error(f"性能集成测试失败: {str(e)}")
        pytest.fail(f"性能集成测试失败: {str(e)}")

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 