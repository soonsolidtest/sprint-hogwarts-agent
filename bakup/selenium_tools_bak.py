import logging
from typing import Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

# 全局 WebDriver 实例
_driver: Optional[webdriver.Chrome] = None

def _get_driver() -> webdriver.Chrome:
    """获取 WebDriver 实例"""
    global _driver
    if _driver is None:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # 无头模式
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        _driver = webdriver.Chrome(options=options)
    return _driver

def selenium_get(url: str) -> Dict[str, Any]:
    """打开 URL"""
    try:
        driver = _get_driver()
        driver.get(url)
        return {
            "status": "success",
            "url": url,
            "title": driver.title
        }
    except Exception as e:
        logger.error(f"Failed to get URL {url}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_click(selector: str, by: str = By.CSS_SELECTOR) -> Dict[str, Any]:
    """点击元素"""
    try:
        driver = _get_driver()
        element = driver.find_element(by, selector)
        element.click()
        return {
            "status": "success",
            "selector": selector,
            "by": by
        }
    except Exception as e:
        logger.error(f"Failed to click element {selector}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_sendkeys(selector: str, text: str, by: str = By.CSS_SELECTOR) -> Dict[str, Any]:
    """输入文本"""
    try:
        driver = _get_driver()
        element = driver.find_element(by, selector)
        element.clear()
        element.send_keys(text)
        return {
            "status": "success",
            "selector": selector,
            "text": text,
            "by": by
        }
    except Exception as e:
        logger.error(f"Failed to send keys to element {selector}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_get_text(selector: str, by: str = By.CSS_SELECTOR) -> Dict[str, Any]:
    """获取元素文本"""
    try:
        driver = _get_driver()
        element = driver.find_element(by, selector)
        text = element.text
        return {
            "status": "success",
            "selector": selector,
            "text": text,
            "by": by
        }
    except Exception as e:
        logger.error(f"Failed to get text from element {selector}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_get_attribute(selector: str, attribute: str, by: str = By.CSS_SELECTOR) -> Dict[str, Any]:
    """获取元素属性"""
    try:
        driver = _get_driver()
        element = driver.find_element(by, selector)
        value = element.get_attribute(attribute)
        return {
            "status": "success",
            "selector": selector,
            "attribute": attribute,
            "value": value,
            "by": by
        }
    except Exception as e:
        logger.error(f"Failed to get attribute {attribute} from element {selector}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_wait_for_element(selector: str, timeout: int = 10, by: str = By.CSS_SELECTOR) -> Dict[str, Any]:
    """等待元素出现"""
    try:
        driver = _get_driver()
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return {
            "status": "success",
            "selector": selector,
            "by": by,
            "timeout": timeout
        }
    except TimeoutException:
        logger.error(f"Timeout waiting for element {selector}")
        return {
            "status": "error",
            "message": f"Timeout waiting for element {selector}"
        }
    except Exception as e:
        logger.error(f"Failed to wait for element {selector}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_wait_for_text(selector: str, text: str, timeout: int = 10, by: str = By.CSS_SELECTOR) -> Dict[str, Any]:
    """等待元素文本"""
    try:
        driver = _get_driver()
        element = WebDriverWait(driver, timeout).until(
            EC.text_to_be_present_in_element((by, selector), text)
        )
        return {
            "status": "success",
            "selector": selector,
            "text": text,
            "by": by,
            "timeout": timeout
        }
    except TimeoutException:
        logger.error(f"Timeout waiting for text {text} in element {selector}")
        return {
            "status": "error",
            "message": f"Timeout waiting for text {text} in element {selector}"
        }
    except Exception as e:
        logger.error(f"Failed to wait for text {text} in element {selector}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_wait_for_attribute(selector: str, attribute: str, value: str, timeout: int = 10, by: str = By.CSS_SELECTOR) -> Dict[str, Any]:
    """等待元素属性"""
    try:
        driver = _get_driver()
        element = WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(by, selector).get_attribute(attribute) == value
        )
        return {
            "status": "success",
            "selector": selector,
            "attribute": attribute,
            "value": value,
            "by": by,
            "timeout": timeout
        }
    except TimeoutException:
        logger.error(f"Timeout waiting for attribute {attribute}={value} in element {selector}")
        return {
            "status": "error",
            "message": f"Timeout waiting for attribute {attribute}={value} in element {selector}"
        }
    except Exception as e:
        logger.error(f"Failed to wait for attribute {attribute}={value} in element {selector}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_wait_for_url(url: str, timeout: int = 10) -> Dict[str, Any]:
    """等待 URL"""
    try:
        driver = _get_driver()
        WebDriverWait(driver, timeout).until(EC.url_to_be(url))
        return {
            "status": "success",
            "url": url,
            "timeout": timeout
        }
    except TimeoutException:
        logger.error(f"Timeout waiting for URL {url}")
        return {
            "status": "error",
            "message": f"Timeout waiting for URL {url}"
        }
    except Exception as e:
        logger.error(f"Failed to wait for URL {url}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_wait_for_title(title: str, timeout: int = 10) -> Dict[str, Any]:
    """等待标题"""
    try:
        driver = _get_driver()
        WebDriverWait(driver, timeout).until(EC.title_is(title))
        return {
            "status": "success",
            "title": title,
            "timeout": timeout
        }
    except TimeoutException:
        logger.error(f"Timeout waiting for title {title}")
        return {
            "status": "error",
            "message": f"Timeout waiting for title {title}"
        }
    except Exception as e:
        logger.error(f"Failed to wait for title {title}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_wait_for_alert(timeout: int = 10) -> Dict[str, Any]:
    """等待警告框"""
    try:
        driver = _get_driver()
        alert = WebDriverWait(driver, timeout).until(EC.alert_is_present())
        return {
            "status": "success",
            "text": alert.text,
            "timeout": timeout
        }
    except TimeoutException:
        logger.error("Timeout waiting for alert")
        return {
            "status": "error",
            "message": "Timeout waiting for alert"
        }
    except Exception as e:
        logger.error(f"Failed to wait for alert: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_accept_alert() -> Dict[str, Any]:
    """接受警告框"""
    try:
        driver = _get_driver()
        alert = driver.switch_to.alert
        alert.accept()
        return {
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to accept alert: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_dismiss_alert() -> Dict[str, Any]:
    """关闭警告框"""
    try:
        driver = _get_driver()
        alert = driver.switch_to.alert
        alert.dismiss()
        return {
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to dismiss alert: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_get_alert_text() -> Dict[str, Any]:
    """获取警告框文本"""
    try:
        driver = _get_driver()
        alert = driver.switch_to.alert
        text = alert.text
        return {
            "status": "success",
            "text": text
        }
    except Exception as e:
        logger.error(f"Failed to get alert text: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_sendkeys_to_alert(text: str) -> Dict[str, Any]:
    """向警告框输入文本"""
    try:
        driver = _get_driver()
        alert = driver.switch_to.alert
        alert.send_keys(text)
        return {
            "status": "success",
            "text": text
        }
    except Exception as e:
        logger.error(f"Failed to send keys to alert: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_get_cookies() -> Dict[str, Any]:
    """获取所有 cookies"""
    try:
        driver = _get_driver()
        cookies = driver.get_cookies()
        return {
            "status": "success",
            "cookies": cookies
        }
    except Exception as e:
        logger.error(f"Failed to get cookies: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_add_cookie(name: str, value: str, **kwargs) -> Dict[str, Any]:
    """添加 cookie"""
    try:
        driver = _get_driver()
        cookie = {"name": name, "value": value, **kwargs}
        driver.add_cookie(cookie)
        return {
            "status": "success",
            "cookie": cookie
        }
    except Exception as e:
        logger.error(f"Failed to add cookie {name}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_delete_cookie(name: str) -> Dict[str, Any]:
    """删除 cookie"""
    try:
        driver = _get_driver()
        driver.delete_cookie(name)
        return {
            "status": "success",
            "name": name
        }
    except Exception as e:
        logger.error(f"Failed to delete cookie {name}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_delete_all_cookies() -> Dict[str, Any]:
    """删除所有 cookies"""
    try:
        driver = _get_driver()
        driver.delete_all_cookies()
        return {
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to delete all cookies: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_get_screenshot(path: Optional[str] = None) -> Dict[str, Any]:
    """获取截图"""
    try:
        driver = _get_driver()
        if path:
            driver.save_screenshot(path)
            return {
                "status": "success",
                "path": path
            }
        else:
            screenshot = driver.get_screenshot_as_base64()
            return {
                "status": "success",
                "screenshot": screenshot
            }
    except Exception as e:
        logger.error(f"Failed to get screenshot: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_get_page_source() -> Dict[str, Any]:
    """获取页面源码"""
    try:
        driver = _get_driver()
        source = driver.page_source
        return {
            "status": "success",
            "source": source
        }
    except Exception as e:
        logger.error(f"Failed to get page source: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_execute_script(script: str, *args) -> Dict[str, Any]:
    """执行 JavaScript"""
    try:
        driver = _get_driver()
        result = driver.execute_script(script, *args)
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        logger.error(f"Failed to execute script: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_get_window_handles() -> Dict[str, Any]:
    """获取所有窗口句柄"""
    try:
        driver = _get_driver()
        handles = driver.window_handles
        return {
            "status": "success",
            "handles": handles
        }
    except Exception as e:
        logger.error(f"Failed to get window handles: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_get_window_handle() -> Dict[str, Any]:
    """获取当前窗口句柄"""
    try:
        driver = _get_driver()
        handle = driver.current_window_handle
        return {
            "status": "success",
            "handle": handle
        }
    except Exception as e:
        logger.error(f"Failed to get window handle: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_switch_to_window(handle: str) -> Dict[str, Any]:
    """切换到指定窗口"""
    try:
        driver = _get_driver()
        driver.switch_to.window(handle)
        return {
            "status": "success",
            "handle": handle
        }
    except Exception as e:
        logger.error(f"Failed to switch to window {handle}: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_close_window() -> Dict[str, Any]:
    """关闭当前窗口"""
    try:
        driver = _get_driver()
        driver.close()
        return {
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to close window: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

def selenium_quit() -> Dict[str, Any]:
    """退出浏览器"""
    try:
        global _driver
        if _driver:
            _driver.quit()
            _driver = None
        return {
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Failed to quit browser: {e}")
        return {
            "status": "error",
            "message": str(e)
        } 