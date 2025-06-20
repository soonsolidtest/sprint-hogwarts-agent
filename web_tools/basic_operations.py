from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, JavascriptException,ElementNotVisibleException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from time import sleep
from typing import Dict, Any
from langchain_core.tools import tool
import logging
from .driver_management import get_driver

logger = logging.getLogger(__name__)

@tool
def selenium_get(**kwargs) -> Dict[str, Any]:
    """打开网页"""
    url = kwargs.get("url")
    if not url:
        logger.error("❌ 缺少必要参数: url")
        return {
            "status": "error",
            "message": "缺少必要参数: url"
        }
        
    logger.info(f"🌐 打开网页: {url}")
    try:
        driver = get_driver()
        driver.get(url)
        logger.info("✅ 网页打开成功")
        return {
            "status": "success",
            "message": f"成功打开网页: {url}"
        }
    except Exception as e:
        logger.error(f"❌ 打开网页失败: {str(e)}")
        return {
            "status": "error",
            "message": f"打开网页失败: {str(e)}"
        }

@tool
def selenium_sendkeys(**kwargs) -> Dict[str, Any]:
    """向元素输入文本"""
    selector = kwargs.get("selector", {})
    text = kwargs.get("text")
    
    if not selector or not text:
        logger.error("❌ 缺少必要参数: selector 或 text")
        return {
            "status": "error",
            "message": "缺少必要参数: selector 或 text"
        }
        
    by = selector.get("by", "id")
    value = selector.get("value")
    
    logger.info(f"⌨️ 输入文本: {by}={value}, text={text}")
    try:
        driver = get_driver()
        by_type = {
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "link": By.LINK_TEXT
        }.get(by.lower(), By.ID)
        
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((by_type, value))
        )
        element.clear()
        element.send_keys(text)
        logger.info("✅ 文本输入成功")
        return {
            "status": "success",
            "message": f"成功输入文本: {text}"
        }
    except Exception as e:
        logger.error(f"❌ 输入文本失败: {str(e)}")
        return {
            "status": "error",
            "message": f"输入文本失败: {str(e)}"
        }

@tool
def selenium_click(param: dict) -> dict:
    """使用 Selenium 点击元素"""
    print(f"[selenium_click] 调用参数: {param}")
    selectors = param.get("selectors", [])
    wait_time = param.get("wait", 5)
    driver = get_driver()

    for second in range(wait_time):
        print(f"[selenium_click] 第 {second + 1} 次尝试")
        for selector in selectors:
            by = selector.get("by")
            value = selector.get("value", "").strip()
            print(f"[selenium_click] 尝试选择器: {by}={value}")

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
                    if not element.is_displayed():
                        print(f"[selenium_click] 元素不可见: {by}={value}")
                        try:
                            driver.execute_script("arguments[0].scrollIntoView(true);", element)
                            sleep(0.5)  # 等待滚动完成
                            if not element.is_displayed():
                                print(f"[selenium_click] 滚动后元素仍然不可见: {by}={value}")
                                continue
                        except Exception as e:
                            print(f"[selenium_click] 滚动到元素位置失败: {e}")
                            continue

                    try:
                        # 尝试使用 Actions 链
                        actions = ActionChains(driver)
                        actions.move_to_element(element).click().perform()
                        print(f"[selenium_click] Actions 链点击成功: {by}={value}")
                        return {
                            "success": True,
                            "message": f"[selenium_click] Actions 链点击成功: {by}={value}",
                            "selector": selector
                        }
                    except Exception as e:
                        print(f"[selenium_click] Actions 链点击失败: {e}")
                        try:
                            element.click()
                            print(f"[selenium_click] 点击成功: {by}={value}")
                            return {
                                "success": True,
                                "message": f"[selenium_click] 点击成功: {by}={value}",
                                "selector": selector
                            }
                        except Exception as e:
                            print(f"[selenium_click] 正常点击失败，尝试 JS 点击: {e}")
                            try:
                                driver.execute_script("arguments[0].click();", element)
                                print(f"[selenium_click] JS 点击成功: {by}={value}")
                                return {
                                    "success": True,
                                    "message": f"[selenium_click] JS 点击成功: {by}={value}",
                                    "selector": selector
                                }
                            except Exception as js_e:
                                print(f"[selenium_click] JS 点击失败: {js_e}")
                                continue

            except NoSuchElementException:
                print(f"[selenium_click] 找不到元素: {by}={value}")
                continue
            except Exception as e:
                print(f"[selenium_click] 尝试 {by}={value} 报错: {e}")
                continue
        sleep(1)

    return {
        "success": False,
        "message": "[selenium_click] 未能成功找到并点击任何元素。",
        "tried_selectors": selectors
    }

@tool
def selenium_wait_for_element(param: dict) -> dict:
    """等待元素出现并可交互"""
    logger.info(f"[selenium_wait_for_element] 调用参数: {param}")
    selectors = param.get("selectors", [])
    timeout = param.get("timeout", 10)
    driver = get_driver()

    for selector in selectors:
        by = selector.get("by")
        value = selector.get("value", "").strip()
        logger.info(f"[selenium_wait_for_element] 尝试选择器: {by}={value}")

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
                logger.warning(f"[selenium_wait_for_element] 不支持的选择器类型: {by}")
                continue

            if element and element.is_displayed():
                logger.info(f"[selenium_wait_for_element] 元素找到并可见: {by}={value}")
                return {
                    "success": True,
                    "message": f"[selenium_wait_for_element] 元素找到并可见: {by}={value}",
                    "selector": selector
                }

        except Exception as e:
            logger.warning(f"[selenium_wait_for_element] 等待元素失败: {by}={value}, 错误: {e}")
            continue

    return {
        "success": False,
        "message": "[selenium_wait_for_element] 未能找到任何指定元素。",
        "tried_selectors": selectors
    }

@tool
def selenium_quit() -> Dict[str, Any]:
    """关闭浏览器"""
    try:
        from .driver_management import close_driver
        close_driver()
        return {
            "status": "success",
            "message": "浏览器已关闭"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"关闭浏览器失败: {str(e)}"
        }

def _try_click_element(driver, element) -> dict:
    """尝试多种方式点击元素"""
    try:
        # 方法1: 直接点击
        element.click()
        return {"success": True, "method": "direct_click"}
    except Exception as e1:
        try:
            # 方法2: Actions 链点击
            actions = ActionChains(driver)
            actions.move_to_element(element).click().perform()
            return {"success": True, "method": "actions_click"}
        except Exception as e2:
            try:
                # 方法3: JavaScript 点击
                driver.execute_script("arguments[0].click();", element)
                return {"success": True, "method": "javascript_click"}
            except Exception as e3:
                return {
                    "success": False,
                    "errors": {
                        "direct_click": str(e1),
                        "actions_click": str(e2),
                        "javascript_click": str(e3)
                    }
                }

def _ensure_element_visible(driver, element_or_selector, by=By.XPATH, wait_time=0.5) -> bool:
    """
    确保元素可见，无论传入 WebElement 还是定位字符串。

    参数:
        driver: Selenium WebDriver 实例
        element_or_selector: WebElement 或 定位字符串（XPath, CSS, ID 等）
        by: 定位方式，默认 By.XPATH
        wait_time: 滚动后等待时间，默认 0.5 秒

    返回:
        bool: 元素是否可见
    """
    try:
        # 如果是字符串，则查找元素
        if isinstance(element_or_selector, str):
            element = driver.find_element(by, element_or_selector)
        elif isinstance(element_or_selector, WebElement):
            element = element_or_selector
        else:
            logger.error(f"[_ensure_element_visible] 非法参数类型: {type(element_or_selector)}")
            return False

        # 检查是否已显示
        if element.is_displayed():
            return True

        # 尝试滚动
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        sleep(wait_time)

        return element.is_displayed()

    except NoSuchElementException:
        logger.error(f"[_ensure_element_visible] 元素未找到: {element_or_selector}")
        return False
    except Exception as e:
        logger.error(f"[_ensure_element_visible] 异常: {e}")
        return False

def _get_extended_selectors(selectors: list) -> list:
    """扩展选择器列表，增加备用选择器"""
    extended = []
    for selector in selectors:
        extended.append(selector)
        
        # 为 XPath 选择器添加备用版本
        if selector.get("by") == "xpath":
            value = selector.get("value", "")
            # 添加不区分大小写的版本
            if "contains(" in value.lower():
                extended.append({
                    "by": "xpath",
                    "value": value.replace("contains(", "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), ")
                })
    return extended

def _display_find_element(driver,selector: str, timeout: int = 60, el=None):
    try:
        if el:
            elements = WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, selector))
            )
            return elements
        else:
            try:
                ele = (WebDriverWait(driver, timeout=timeout).until(
                    EC.visibility_of_element_located((By.XPATH, selector))))
            except:
                # screen_shot(f"无法定位元素")
                raise ElementNotVisibleException
        return ele
    except:
        logger.error("元素定位失败: {}".format(selector))
        # self.screen_shot(f"无法定位元素")
        raise