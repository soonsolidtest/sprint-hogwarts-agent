from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, JavascriptException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from typing import Dict, Any
from langchain_core.tools import tool
import logging
from .driver_management import get_driver
from .basic_operations import _try_click_element, _ensure_element_visible, _get_extended_selectors

logger = logging.getLogger(__name__)

@tool
def smart_click(param: dict) -> dict:
    """
    智能点击页面元素，支持多种选择器方式和点击策略。
    支持的定位方式: id, name, xpath, css, text, contains_text。
    参数格式:
    {
        "selectors": [
            {"by": "id", "value": "submit-btn"},
            {"by": "text", "value": "立即提交"}
        ],
        "wait": 5
    }
    """
    logger.info(f"[smart_click] 调用参数: {param}")
    selectors = param.get("selectors", [])
    wait_time = param.get("wait", 5)
    driver = get_driver()

    extended_selectors = _get_extended_selectors(selectors)

    for selector in extended_selectors:
        by = selector.get("by")
        value = selector.get("value", "").strip()
        logger.info(f"[smart_click] 尝试选择器: {by}={value}")

        try:
            # 构造 By 策略和定位表达式
            if by == "id":
                locator = (By.ID, value)
            elif by == "name":
                locator = (By.NAME, value)
            elif by == "xpath":
                locator = (By.XPATH, value)
            elif by == "css":
                locator = (By.CSS_SELECTOR, value)
            elif by == "text":
                locator = (By.XPATH, f"//*[text()='{value}']")
            elif by == "contains_text":
                locator = (By.XPATH, f"//*[contains(text(), '{value}')]")
            else:
                logger.warning(f"[smart_click] 不支持的选择器类型: {by}")
                continue

            # 等待元素可点击
            element = WebDriverWait(driver, wait_time).until(
                EC.element_to_be_clickable(locator)
            )

            # 可见性检查（如果有额外逻辑）
            if not _ensure_element_visible(driver, element):
                logger.info(f"[smart_click] 元素不可见: {by}={value}")
                continue

            # 尝试点击
            click_result = _try_click_element(driver, element)
            if click_result.get("success"):
                logger.info(f"[smart_click] 点击成功: {by}={value}, 方法: {click_result.get('method')}")
                return {
                    "status": "success",
                    "message": f"[smart_click] 点击成功: {by}={value}, 方法: {click_result.get('method')}",
                    "element_text": element.text,
                    "element_html": element.get_attribute("outerHTML")
                }
            else:
                logger.warning(f"[smart_click] 点击失败: {by}={value}, 错误: {click_result.get('errors')}")

        except TimeoutException:
            logger.info(f"[smart_click] 等待超时: {by}={value}")
        except NoSuchElementException:
            logger.info(f"[smart_click] 找不到元素: {by}={value}")
        except Exception as e:
            logger.exception(f"[smart_click] 尝试 {by}={value} 报错: {e}")

    return {
        "status": "error",
        "message": "[smart_click] 未能成功找到并点击任何元素。",
        "tried_selectors": extended_selectors
    }

@tool
def smart_select_open(param: dict) -> dict:
    """智能打开下拉选择框"""
    print(f"[smart_select_open] 调用参数: {param}")
    selectors = param.get("selectors", [])
    wait_time = param.get("wait", 5)
    driver = get_driver()

    for second in range(wait_time):
        print(f"[smart_select_open] 第 {second + 1} 次尝试")
        for selector in selectors:
            by = selector.get("by")
            value = selector.get("value", "").strip()
            print(f"[smart_select_open] 尝试选择器: {by}={value}")

            try:
                element = None
                if by == "id":
                    element = driver.find_element("id", value)
                elif by == "name":
                    element = driver.find_element("name", value)
                elif by == "xpath":
                    element = driver.find_element("xpath", value)
                elif by == "css":
                    element = driver.find_element("css selector", value)
                else:
                    continue

                if element:
                    if not _ensure_element_visible(driver, element):
                        print(f"[smart_select_open] 元素不可见: {by}={value}")
                        continue

                    # 尝试点击打开下拉框
                    click_result = _try_click_element(driver, element)
                    if click_result["success"]:
                        print(f"[smart_select_open] 下拉框打开成功: {by}={value}")
                        return {
                            "status": "success",
                            "message": f"[smart_select_open] 下拉框打开成功: {by}={value}",
                            "selector": selector
                        }

            except NoSuchElementException:
                print(f"[smart_select_open] 找不到元素: {by}={value}")
                continue
            except Exception as e:
                print(f"[smart_select_open] 尝试 {by}={value} 报错: {e}")
                continue
        sleep(1)

    return {
        "status": "error",
        "message": "[smart_select_open] 未能成功打开下拉选择框。",
        "tried_selectors": selectors
    }

@tool
def smart_select_and_choose(param: dict) -> dict:
    """智能选择下拉选项"""
    print(f"[smart_select_and_choose] 调用参数: {param}")
    dropdown_selectors = param.get("dropdown_selectors", [])
    option_selectors = param.get("option_selectors", [])
    wait_time = param.get("wait", 5)
    driver = get_driver()

    # 第一步：打开下拉框
    open_result = smart_select_open.invoke({
        "param": {
            "selectors": dropdown_selectors,
            "wait": wait_time
        }
    })
    
    if open_result.get("status") != "success":
        return {
            "status": "error",
            "message": f"[smart_select_and_choose] 打开下拉框失败: {open_result.get('message')}"
        }

    # 等待下拉选项出现
    sleep(1)

    # 第二步：选择选项
    for second in range(wait_time):
        print(f"[smart_select_and_choose] 第 {second + 1} 次尝试选择选项")
        for selector in option_selectors:
            by = selector.get("by")
            value = selector.get("value", "").strip()
            print(f"[smart_select_and_choose] 尝试选择器: {by}={value}")

            try:
                element = None
                if by == "id":
                    element = driver.find_element("id", value)
                elif by == "name":
                    element = driver.find_element("name", value)
                elif by == "xpath":
                    element = driver.find_element("xpath", value)
                elif by == "css":
                    element = driver.find_element("css selector", value)
                else:
                    continue

                if element:
                    if not _ensure_element_visible(driver, element):
                        print(f"[smart_select_and_choose] 选项不可见: {by}={value}")
                        continue

                    # 尝试点击选择选项
                    click_result = _try_click_element(driver, element)
                    if click_result["success"]:
                        print(f"[smart_select_and_choose] 选项选择成功: {by}={value}")
                        return {
                            "status": "success",
                            "message": f"[smart_select_and_choose] 选项选择成功: {by}={value}",
                            "selector": selector
                        }

            except NoSuchElementException:
                print(f"[smart_select_and_choose] 找不到选项: {by}={value}")
                continue
            except Exception as e:
                print(f"[smart_select_and_choose] 尝试 {by}={value} 报错: {e}")
                continue
        sleep(1)

    return {
        "status": "error",
        "message": "[smart_select_and_choose] 未能成功选择任何选项。",
        "tried_selectors": option_selectors
    } 