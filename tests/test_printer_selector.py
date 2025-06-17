"""
打印机选择器测试模块
"""

import pytest
import logging
from unittest.mock import Mock, patch
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from web_tools.web_toolkit import PrinterSelector

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_driver():
    """创建模拟的 WebDriver"""
    return Mock(spec=WebDriver)

@pytest.fixture
def printer_selector(mock_driver):
    """创建打印机选择器实例"""
    return PrinterSelector(mock_driver)

def test_click_element_success(printer_selector, mock_driver):
    """测试成功点击元素"""
    # 准备测试数据
    selector = {
        "by": "xpath",
        "value": "//test-element"
    }
    mock_element = Mock()
    mock_driver.find_element.return_value = mock_element
    mock_element.is_displayed.return_value = True

    # 执行测试
    result = printer_selector._click_element(selector)

    # 验证结果
    assert result is True
    mock_element.click.assert_called_once()

def test_click_element_timeout(printer_selector, mock_driver):
    """测试点击元素超时"""
    # 准备测试数据
    selector = {
        "by": "xpath",
        "value": "//test-element"
    }
    mock_driver.find_element.side_effect = TimeoutException()

    # 执行测试
    result = printer_selector._click_element(selector)

    # 验证结果
    assert result is False

def test_click_element_intercepted(printer_selector, mock_driver):
    """测试元素被遮挡"""
    # 准备测试数据
    selector = {
        "by": "xpath",
        "value": "//test-element"
    }
    mock_element = Mock()
    mock_driver.find_element.return_value = mock_element
    mock_element.click.side_effect = ElementClickInterceptedException("Element click intercepted")

    # 执行测试
    result = printer_selector._click_element(selector)

    # 验证结果
    assert result is False

def test_click_printer_dropdown_success(printer_selector):
    """测试成功点击打印机下拉框"""
    # 模拟 _click_element 方法
    with patch.object(printer_selector, '_click_element', return_value=True):
        result = printer_selector._click_printer_dropdown(10)
        assert result["success"] is True
        assert "成功点击打印机选择下拉框" in result["message"]

def test_click_printer_dropdown_failure(printer_selector):
    """测试点击打印机下拉框失败"""
    # 模拟 _click_element 方法
    with patch.object(printer_selector, '_click_element', return_value=False):
        result = printer_selector._click_printer_dropdown(10)
        assert result["success"] is False
        assert "点击打印机选择下拉框失败" in result["message"]

def test_select_connected_printer_success(printer_selector):
    """测试成功选择已连接打印机"""
    # 模拟 _click_element 方法
    with patch.object(printer_selector, '_click_element', return_value=True):
        result = printer_selector._select_connected_printer("Test Printer", 10)
        assert result["success"] is True
        assert "成功选择已连接打印机" in result["message"]

def test_select_connected_printer_not_found(printer_selector):
    """测试未找到已连接打印机"""
    # 模拟 _click_element 方法
    with patch.object(printer_selector, '_click_element', return_value=False):
        result = printer_selector._select_connected_printer("Test Printer", 10)
        assert result["success"] is False
        assert "未找到已连接打印机" in result["message"]

def test_select_virtual_printer_success(printer_selector):
    """测试成功选择虚拟打印机"""
    # 模拟 _click_element 方法
    with patch.object(printer_selector, '_click_element', return_value=True):
        result = printer_selector._select_virtual_printer("Test Printer", 10)
        assert result["success"] is True
        assert "成功选择虚拟打印机" in result["message"]

def test_select_virtual_printer_not_found(printer_selector):
    """测试未找到虚拟打印机"""
    # 模拟 _click_element 方法
    with patch.object(printer_selector, '_click_element', return_value=False):
        result = printer_selector._select_virtual_printer("Test Printer", 10)
        assert result["success"] is False
        assert "未找到虚拟打印机" in result["message"]

def test_select_printer_missing_printer(printer_selector):
    """测试缺少打印机参数"""
    result = printer_selector.select_printer("")
    assert result["success"] is False
    assert "缺少必要的参数：printer" in result["message"]

def test_select_printer_connected_success(printer_selector):
    """测试成功选择已连接打印机"""
    # 模拟相关方法
    with patch.object(printer_selector, '_click_printer_dropdown') as mock_dropdown, \
         patch.object(printer_selector, '_select_connected_printer') as mock_select:
        # 设置返回值
        mock_dropdown.return_value = {"success": True, "message": "成功点击下拉框"}
        mock_select.return_value = {"success": True, "message": "成功选择打印机"}

        # 执行测试
        result = printer_selector.select_printer("Test Printer", "connected")

        # 验证结果
        assert result["success"] is True
        assert "成功选择打印机" in result["message"]
        mock_dropdown.assert_called_once()
        mock_select.assert_called_once_with("Test Printer", 10)

def test_select_printer_virtual_success(printer_selector):
    """测试成功选择虚拟打印机"""
    # 模拟相关方法
    with patch.object(printer_selector, '_click_printer_dropdown') as mock_dropdown, \
         patch.object(printer_selector, '_select_virtual_printer') as mock_select:
        # 设置返回值
        mock_dropdown.return_value = {"success": True, "message": "成功点击下拉框"}
        mock_select.return_value = {"success": True, "message": "成功选择打印机"}

        # 执行测试
        result = printer_selector.select_printer("Test Printer", "virtual")

        # 验证结果
        assert result["success"] is True
        assert "成功选择打印机" in result["message"]
        mock_dropdown.assert_called_once()
        mock_select.assert_called_once_with("Test Printer", 10)

def test_select_printer_dropdown_failure(printer_selector):
    """测试点击下拉框失败"""
    # 模拟下拉框点击失败
    with patch.object(printer_selector, '_click_printer_dropdown') as mock_dropdown:
        mock_dropdown.return_value = {"success": False, "message": "点击失败"}

        # 执行测试
        result = printer_selector.select_printer("Test Printer")

        # 验证结果
        assert result["success"] is False
        assert "点击失败" in result["message"]
        mock_dropdown.assert_called_once() 