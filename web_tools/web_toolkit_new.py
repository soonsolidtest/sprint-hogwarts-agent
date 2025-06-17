from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    JavascriptException,
    ElementNotInteractableException,
    TimeoutException
)
from time import sleep
from pathlib import Path
from langchain_core.tools import tool
from langchain_core.runnables import RunnableLambda
from typing import Dict, Any, List, Optional, Type, Union
from langchain.tools import BaseTool
import logging
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# 配置日志
logger = logging.getLogger(__name__)

# 全局 WebDriver 实例
_driver = None

def _wait_for_element(driver, by: str, value: str, timeout: int) -> dict:
    """等待元素出现"""
    try:
        element = None
        if by == "id":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, value))
            )
        elif by == "name":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.NAME, value))
            )
        elif by == "xpath":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, value))
            )
        elif by == "css":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, value))
            )
        else:
            return {
                "success": False,
                "message": f"不支持的选择器类型: {by}"
            }

        if element and element.is_displayed():
            return {
                "success": True,
                "message": f"元素可见: {by}={value}",
                "element": element
            }
        else:
            return {
                "success": False,
                "message": f"元素不可见: {by}={value}"
            }
    except TimeoutException:
        return {
            "success": False,
            "message": f"等待元素超时: {by}={value}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"等待元素出错: {e}"
        }

@tool
def selenium_wait_for_element(param: dict) -> dict:
    """等待元素出现并可交互。"""
    logger.info(f"[selenium_wait_for_element] 调用参数: {param}")
    selectors = param.get("selectors", [])
    timeout = param.get("timeout", 10)
    driver = _driver

    for selector in selectors:
        by = selector.get("by")
        value = selector.get("value", "").strip()
        logger.info(f"[selenium_wait_for_element] 尝试选择器: {by}={value}")

        result = _wait_for_element(driver, by, value, timeout)
        if result["success"]:
            logger.info(f"[selenium_wait_for_element] {result['message']}")
            return {
                "success": True,
                "message": f"[selenium_wait_for_element] {result['message']}",
                "selector": selector
            }
        else:
            logger.warning(f"[selenium_wait_for_element] {result['message']}")
            continue

    return {
        "success": False,
        "message": "[selenium_wait_for_element] 未能找到任何可见元素。",
        "tried_selectors": selectors
    } 