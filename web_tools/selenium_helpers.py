from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException
)
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import logging

logger = logging.getLogger(__name__)

def wait_for_element(driver, by: str, value: str, timeout: int = 10) -> dict:
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

def click_element(driver, element, by: str, value: str) -> dict:
    """点击元素"""
    try:
        if not element.is_displayed():
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                sleep(0.5)
                if not element.is_displayed():
                    return {
                        "success": False,
                        "message": f"滚动后元素仍然不可见: {by}={value}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"滚动到元素位置失败: {e}"
                }

        try:
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()
            return {
                "success": True,
                "message": f"Actions 链点击成功: {by}={value}"
            }
        except Exception:
            try:
                element.click()
                return {
                    "success": True,
                    "message": f"直接点击成功: {by}={value}"
                }
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", element)
                    return {
                        "success": True,
                        "message": f"JS 点击成功: {by}={value}"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "message": f"所有点击方式都失败: {e}"
                    }
    except Exception as e:
        return {
            "success": False,
            "message": f"点击元素时发生错误: {e}"
        }

def find_element(driver, by: str, value: str) -> dict:
    """查找元素"""
    try:
        element = None
        if by == "id":
            element = driver.find_element(By.ID, value)
        elif by == "name":
            element = driver.find_element(By.NAME, value)
        elif by == "xpath":
            element = driver.find_element(By.XPATH, value)
        elif by == "css":
            element = driver.find_element(By.CSS_SELECTOR, value)
        else:
            return {
                "success": False,
                "message": f"不支持的选择器类型: {by}"
            }

        if element:
            return {
                "success": True,
                "message": f"找到元素: {by}={value}",
                "element": element
            }
        else:
            return {
                "success": False,
                "message": f"未找到元素: {by}={value}"
            }
    except NoSuchElementException:
        return {
            "success": False,
            "message": f"找不到元素: {by}={value}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"查找元素时发生错误: {e}"
        } 