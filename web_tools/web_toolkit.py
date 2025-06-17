from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, JavascriptException
from time import sleep
from pathlib import Path
from langchain_core.tools import tool
from langchain_core.runnables import RunnableLambda
from selenium.common.exceptions import (
    ElementNotInteractableException,
    TimeoutException,
    NoSuchElementException,
)
from typing import Dict, Any, List, Optional, Type, Union
from langchain.tools import BaseTool
import logging
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config import config
from pydantic import BaseModel, Field
from enum import Enum
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# 配置日志 - 使用统一配置
logger = logging.getLogger(__name__)

# 全局 WebDriver 实例
_driver = None

def get_driver() -> webdriver.Chrome:
    """获取或创建 WebDriver 实例"""
    global _driver
    if _driver is None:
        browser_config = config.browser
        options = Options()
        
        if not browser_config.get('headless', False):
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        else:
            options.add_argument("--headless")
        
        window_size = browser_config.get('window_size', [1920, 1080])
        options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
        
        # 按优先级尝试初始化 ChromeDriver
        driver_initialized = False
        
        # 方法1: 优先使用本框架内的 ChromeDriver
        try:
            logger.info("🔄 尝试使用框架内的 ChromeDriver...")
            
            # 检查框架内的 ChromeDriver 路径
            framework_paths = [
                "./drivers/chromedriver",
                "./drivers/chromedriver.exe",
                "drivers/chromedriver",
                "drivers/chromedriver.exe"
            ]
            
            driver_path = None
            for path in framework_paths:
                if Path(path).exists():
                    driver_path = path
                    break
            
            if driver_path:
                # 确保有执行权限 (Unix系统)
                import os
                import stat
                if not driver_path.endswith('.exe'):
                    current_permissions = os.stat(driver_path).st_mode
                    os.chmod(driver_path, current_permissions | stat.S_IEXEC)
                
                service = Service(driver_path)
                _driver = webdriver.Chrome(service=service, options=options)
                logger.info(f"✅ 框架内 ChromeDriver 初始化成功: {driver_path}")
                driver_initialized = True
            else:
                logger.info("ℹ️ 框架内未找到 ChromeDriver")
                
        except Exception as e1:
            logger.warning(f"⚠️ 框架内 ChromeDriver 失败: {e1}")
        
        # 方法2: 使用系统路径中的 chromedriver
        if not driver_initialized:
            try:
                logger.info("🔄 尝试使用系统路径中的 ChromeDriver...")
                _driver = webdriver.Chrome(options=options)
                logger.info("✅ 系统 ChromeDriver 初始化成功")
                driver_initialized = True
                
            except Exception as e2:
                logger.warning(f"⚠️ 系统 ChromeDriver 失败: {e2}")
        
        # 方法3: 最后尝试通过网络下载 (WebDriverManager)
        if not driver_initialized:
            try:
                logger.info("🔄 尝试通过网络下载 ChromeDriver...")
                logger.info("⚠️ 这需要网络连接，可能需要一些时间...")
                
                service = Service(ChromeDriverManager().install())
                _driver = webdriver.Chrome(service=service, options=options)
                logger.info("✅ 网络下载 ChromeDriver 初始化成功")
                driver_initialized = True
                
            except Exception as e3:
                logger.error("❌ 网络下载 ChromeDriver 失败")
        
        # 如果所有方法都失败
        if not driver_initialized:
            logger.error("❌ 所有 ChromeDriver 初始化方法都失败")
            logger.info("💡 解决建议:")
            logger.info("1. 手动下载 ChromeDriver 到 ./drivers/ 目录")
            logger.info("2. 访问 https://googlechromelabs.github.io/chrome-for-testing/")
            logger.info("3. 下载与你的 Chrome 版本匹配的 ChromeDriver")
            logger.info("4. 将下载的文件重命名为 chromedriver 并放到 drivers 目录")
            logger.info("5. 在 macOS/Linux 上运行: chmod +x drivers/chromedriver")
            
            raise Exception("ChromeDriver 初始化失败，请手动下载 ChromeDriver 到 drivers 目录")
        
        # 设置浏览器参数
        _driver.implicitly_wait(browser_config.get('implicit_wait', 10))
        _driver.set_page_load_timeout(browser_config.get('page_load_timeout', 30))
        
        logger.info("🌐 浏览器启动成功")
    return _driver

def close_driver():
    """关闭 WebDriver"""
    global _driver
    if _driver:
        _driver.quit()
        _driver = None
        logger.info("🚪 浏览器已关闭")

# 工具类封装
class WebToolkit:
    def __init__(self):
        self.driver: WebDriver = None

    def start(self, browser='chrome'):
        if browser == 'chrome':
            self.driver = webdriver.Chrome()
            self.driver.implicitly_wait(10)
        else:
            raise Exception(f'Browser not supported: {browser}')

    def open(self, url: str):
        print(f'Opening {url}')
        if self.driver is None:
            self.start()
        try:
            self.driver.get(url)
            sleep(2)
            return {"status": "success", "message": f"已打开 {url}"}
        except Exception as e:
            return {"status": "failed", "message": f"打开页面失败: {e}"}

    def click(self, by: str, value: str):
        try:
            element = self.driver.find_element(self._map_by(by), value)
            element.click()
            sleep(1)
            return {"status": "success", "message": f"已点击元素 {by}={value}"}
        except NoSuchElementException:
            return {"status": "failed", "message": f"未找到元素: {by}={value}"}
        except Exception as e:
            return {"status": "failed", "message": f"点击元素时发生错误: {e}"}

    def send_keys(self, by: str, value: str, text: str):
        try:
            element = self.driver.find_element(self._map_by(by), value)
            element.clear()
            element.send_keys(text)
            sleep(1)
            return {"status": "success", "message": f"已输入内容到元素 {by}={value}"}
        except NoSuchElementException:
            return {"status": "failed", "message": f"未找到元素: {by}={value}"}
        except Exception as e:
            return {"status": "failed", "message": f"输入内容时发生错误: {e}"}

    def wait_for_element(self, by: str, value: str, timeout: int = 10):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((self._map_by(by), value))
            )
            return {"status": "success", "message": f"元素已出现: {by}={value}"}
        except Exception as e:
            return {"status": "failed", "message": f"等待元素失败: {by}={value}，错误: {e}"}

    def wait_until_text(self, by: str, value: str, target_text: str, timeout: int = 10):
        def check_text(driver):
            try:
                el = driver.find_element(self._map_by(by), value)
                return target_text in el.text
            except:
                return False

        try:
            WebDriverWait(self.driver, timeout).until(check_text)
            return {"status": "success", "message": f"目标文本已出现: {target_text}"}
        except Exception as e:
            return {"status": "failed", "message": f"等待文本失败: {target_text}，错误: {e}"}

    def quit(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            return {"status": "success", "message": "浏览器已关闭"}
        return {"status": "failed", "message": "浏览器尚未启动"}

    def _map_by(self, by: str):
        mapping = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "tag": By.TAG_NAME,
            "class": By.CLASS_NAME,
            "link": By.LINK_TEXT
        }
        return mapping.get(by.lower(), By.CSS_SELECTOR)

    def get_dom_snapshot(self, mode: str = "browser_use") -> dict:
        mode_map = {
            "full": "enhance_dom.js",
            "light": "openai_gen.js",
            "large_only": "source.js",
            "highlight": "interactive_elements_v1.js",
            "browser_use": "origin_browser_use.js"
        }
        js_dir = Path(__file__).parent / "js"
        js_file = mode_map.get(mode)
        if not js_file:
            return {"status": "failed", "message": f"不支持的模式: {mode}"}

        js_path = js_dir / js_file
        if not js_path.exists():
            return {"status": "failed", "message": f"找不到 JS 文件: {js_path}"}

        print(f"正在加载 JS 文件：{js_path}")
        js_code = js_path.read_text(encoding="utf-8")

        try:
            result = self.driver.execute_script(js_code)
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "failed", "message": f"执行 DOM 快照失败: {str(e)}"}

# 单例对象
toolkit = WebToolkit()


# 工具导出
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
    """
    使用 Selenium 点击元素。
    """
    print(f"[selenium_click] 调用参数: {param}")
    selectors = param.get("selectors", [])
    wait_time = param.get("wait", 5)
    driver = _driver

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
    """等待元素出现并可交互。"""
    logger.info(f"[selenium_wait_for_element] 调用参数: {param}")
    selectors = param.get("selectors", [])
    timeout = param.get("timeout", 10)
    driver = _driver

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
                logger.info(f"[selenium_wait_for_element] 元素可见: {by}={value}")
                return {
                    "success": True,
                    "message": f"[selenium_wait_for_element] 元素可见: {by}={value}",
                    "selector": selector
                }
            else:
                logger.warning(f"[selenium_wait_for_element] 元素不可见: {by}={value}")
                continue

        except TimeoutException:
            logger.warning(f"[selenium_wait_for_element] 等待元素超时: {by}={value}")
            continue
        except Exception as e:
            logger.error(f"[selenium_wait_for_element] 等待元素出错: {e}")
            continue

    return {
        "success": False,
        "message": "[selenium_wait_for_element] 未能找到任何可见元素。",
        "tried_selectors": selectors
    }

@tool
def selenium_quit() -> Dict[str, Any]:
    """关闭浏览器"""
    logger.info("🚪 退出浏览器")
    global _driver
    try:
        if _driver is not None:
            _driver.quit()
            _driver = None
            logger.info("✅ 浏览器退出成功")
        return {
            "status": "success",
            "message": "浏览器已关闭"
        }
    except Exception as e:
        logger.error(f"❌ 浏览器退出失败: {str(e)}")
        return {
            "status": "error",
            "message": f"浏览器退出失败: {str(e)}"
        }

def _try_click_element(driver, element, selector) -> dict:
    """尝试使用不同方式点击元素"""
    try:
        # 尝试使用 Actions 链
        actions = ActionChains(driver)
        actions.move_to_element(element).click().perform()
        print(f"[smart_click] Actions 链点击成功: {selector['by']}={selector['value']}")
        return {
            "status": "success",
            "message": f"[smart_click] Actions 链点击成功: {selector['by']}={selector['value']}",
            "selector": selector
        }
    except Exception as e:
        print(f"[smart_click] Actions 链点击失败: {e}")
        try:
            # 尝试直接点击
            element.click()
            print(f"[smart_click] 直接点击成功: {selector['by']}={selector['value']}")
            return {
                "status": "success",
                "message": f"[smart_click] 直接点击成功: {selector['by']}={selector['value']}",
                "selector": selector
            }
        except Exception as e:
            print(f"[smart_click] 直接点击失败，尝试 JS 点击: {e}")
            try:
                # 尝试 JavaScript 点击
                driver.execute_script("arguments[0].click();", element)
                print(f"[smart_click] JS 点击成功: {selector['by']}={selector['value']}")
                return {
                    "status": "success",
                    "message": f"[smart_click] JS 点击成功: {selector['by']}={selector['value']}",
                    "selector": selector
                }
            except Exception as js_e:
                print(f"[smart_click] JS 点击失败: {js_e}")
                return None

def _ensure_element_visible(driver, element, selector) -> bool:
    """确保元素可见"""
    if not element.is_displayed():
        print(f"[smart_click] 元素不可见: {selector['by']}={selector['value']}")
        try:
            # 滚动到元素位置
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            sleep(0.5)  # 等待滚动完成
            
            # 再次检查可见性
            if not element.is_displayed():
                print(f"[smart_click] 滚动后元素仍然不可见: {selector['by']}={selector['value']}")
                return False
            return True
        except Exception as e:
            print(f"[smart_click] 滚动到元素位置失败: {e}")
            return False
    return True

def _get_extended_selectors(selectors: list) -> list:
    """获取扩展的选择器列表"""
    extended_selectors = []
    for selector in selectors:
        by = selector.get("by")
        value = selector.get("value", "").strip()
        
        # 原始选择器
        extended_selectors.append(selector)
        
        # 如果是 xpath，添加更多变体
        if by == "xpath":
            # 添加包含文本的变体
            if "text()" not in value:
                text_variant = f"{value}[contains(text(), '{value}')]"
                extended_selectors.append({"by": "xpath", "value": text_variant})
            
            # 添加按钮变体
            if "button" not in value.lower():
                button_variant = f"//button{value}"
                extended_selectors.append({"by": "xpath", "value": button_variant})
            
            # 添加 div 变体
            if "div" not in value.lower():
                div_variant = f"//div{value}"
                extended_selectors.append({"by": "xpath", "value": div_variant})
    
    return extended_selectors

@tool
def smart_click(param: dict) -> dict:
    """
    智能点击元素，支持多个选择器，按优先级尝试。
    """
    print(f"[smart_click] 调用参数: {param}")
    driver = _driver
    
    try:
        selectors = param.get("selectors", [])
        wait_time = param.get("wait", 10)
        
        if not selectors:
            raise Exception("未提供选择器")
            
        # 尝试每个选择器，直到成功点击一个
        for selector in selectors:
            try:
                by = selector.get("by")
                value = selector.get("value")
                
                if not by or not value:
                    continue

                print(f"[smart_click] 尝试选择器: {by}={value}")
                
                # 等待元素可见和可点击
                element = WebDriverWait(driver, wait_time).until(
                    EC.element_to_be_clickable((by, value))
                )
                
                # 点击元素
                element.click()
                print(f"[smart_click] ✅ 成功点击元素: {by}={value}")
                
                # 成功点击后立即返回
                return {
                    "status": "success",
                    "message": f"成功点击元素: {by}={value}"
                }

            except Exception as e:
                print(f"[smart_click] 选择器 {by}={value} 失败: {str(e)}")
                continue

        # 如果所有选择器都失败
        raise Exception("所有选择器都未能成功点击元素")
        
    except Exception as e:
        print(f"[smart_click] ❌ 点击失败: {str(e)}")
        return {
            "status": "failed",
            "message": f"点击失败: {str(e)}"
        }

@tool
def smart_select_open(param: dict) -> dict:
    """
    智能定位并点击"选择框"元素，常用于打开下拉菜单。
    参数格式:
    {
        "selectors": [
            {"by": "text", "value": "请选择医生"},
            {"by": "xpath", "value": "//label[text()='医生']/following-sibling::div"},
            ...
        ],
        "wait": 5
    }
    """
    print(f"[smart_select_open] 调用参数: {param}")
    selectors = param.get("selectors", [])
    wait_time = param.get("wait", 5)
    driver = toolkit.driver

    for _ in range(wait_time):
        for selector in selectors:
            by = selector.get("by")
            value = selector.get("value", "").strip()

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
                elif by == "text":
                    xpath = f"//*[contains(normalize-space(text()), '{value}')]"
                    candidates = driver.find_elements("xpath", xpath)
                    for el in candidates:
                        # 找到下层 div 或 label 容器并尝试点击
                        try:
                            clickable_el = el.find_element("xpath", "..")
                            clickable_el.click()
                            print(f"[smart_select_open] success 成功点击选择框: {by}={value}")
                            return {
                                "status": "success",
                                "message": f"[smart_select_open] 成功点击选择框: {by}={value}",
                                "selector": selector
                            }
                        except Exception as e:
                            print(f"[smart_select_open] 点击失败: {e}")
                elif by == "exact_text":
                    candidates = driver.find_elements("xpath", "//*[self::div or self::label or self::span]")
                    for el in candidates:
                        if el.text.strip() == value:
                            element = el
                            break

                if element:
                    try:
                        element.click()
                    except Exception as e:
                        print(f"[smart_select_open] 正常点击失败，尝试 JS 点击: {e}")
                        driver.execute_script("arguments[0].click();", element)
                    print(f"[smart_select_open] success 成功点击选择框: {by}={value}")
                    return {
                        "status": "success",
                        "message": f"[smart_select_open] 成功点击选择框: {by}={value}",
                        "selector": selector
                    }

            except NoSuchElementException:
                continue
            except Exception as e:
                print(f"[smart_select_open] 尝试 {by}={value} 报错: {e}")
        sleep(1)
    print("[smart_select_open] failed")
    return {
        "status": "failed",
        "message": "[smart_select_open] 未能成功点击选择框。",
        "tried_selectors": selectors
    }

smart_select_open_tool = RunnableLambda(smart_select_open)
smart_click_tool = RunnableLambda(smart_click)
@tool
def smart_select_and_choose(param: dict) -> dict:
    """
    智能选择并点击下拉选项。
    参数:
        param: 包含以下字段的字典:
            - selectors: 选择器列表，用于定位下拉框
            - options: 选项选择器列表，用于定位要选择的选项
            - wait: 等待时间（秒）
    """
    logger.info(f"[smart_select_and_choose] 调用参数: {param}")
    driver = _driver

    # 1. 获取参数
    selectors = param.get("selectors", [])
    options = param.get("options", [])
    wait_time = param.get("wait", 10)

    if not selectors or not options:
        return {
            "success": False,
            "message": "缺少必要的参数：selectors 或 options"
        }

    # 2. 智能滚动查找下拉框
    max_scroll_attempts = 5
    scroll_height = 300  # 每次滚动的高度
    dropdown_clicked = False

    for attempt in range(max_scroll_attempts):
        for selector in selectors:
            try:
                logger.info(f"[smart_select_and_choose] 尝试选择器: {selector}")
                element = driver.find_element(selector["by"], selector["value"])
                if element.is_displayed():
                    element.click()
                    dropdown_clicked = True
                    logger.info(f"[smart_select_and_choose] 成功点击下拉框: {selector}")
                    break
            except Exception as e:
                logger.error(f"[smart_select_and_choose] 点击下拉框失败: {str(e)}")
                continue

        if dropdown_clicked:
            break

        # 如果没找到，向下滚动
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(1)  # 等待页面加载
        logger.info(f"[smart_select_and_choose] 向下滚动 {scroll_height}px，尝试次数: {attempt + 1}")

    if not dropdown_clicked:
        return {
            "success": False,
            "message": "无法点击下拉框"
        }

    # 3. 等待选项出现并点击
    time.sleep(3)  # 等待下拉框展开
    option_clicked = False

    for option in options:
        try:
            logger.info(f"[smart_select_and_choose] 尝试选项: {option}")
            element = driver.find_element(option["by"], option["value"])
            if element.is_displayed():
                element.click()
                option_clicked = True
                logger.info(f"[smart_select_and_choose] 成功选择选项: {option}")
                break
        except Exception as e:
            logger.error(f"[smart_select_and_choose] 选择选项失败: {str(e)}")
            continue

    if not option_clicked:
        return {
            "success": False,
            "message": "无法选择选项"
        }

    return {
        "success": True,
        "message": "成功选择选项"
    }

class PrintJobTool(BaseTool):
    """打印任务相关工具"""
    name: str = "print_job"
    description: str = "处理打印任务相关操作，包括新建打印任务、设置参数等"
    
    def _run(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        action = tool_input.get("action")
        if action == "create":
            return self._create_print_job(tool_input)
        elif action == "set_parameter":
            return self._set_parameter(tool_input)
        else:
            return {"status": "error", "message": f"未知的打印任务操作: {action}"}
    
    def _create_print_job(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """创建新的打印任务"""
        try:
            # 点击新建打印任务按钮
            driver = webdriver.Chrome()  # 使用已打开的driver
            wait = WebDriverWait(driver, 10)
            
            # 等待并点击新建打印任务按钮
            new_job_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '新建打印任务')]"))
            )
            new_job_btn.click()
            
            # 设置基本参数
            if "indications" in params:
                indications_input = wait.until(
                    EC.presence_of_element_located((By.NAME, "indications"))
                )
                indications_input.send_keys(params["indications"])
            
            return {
                "status": "success",
                "message": "成功创建打印任务",
                "job_id": "mock_job_id"  # 实际应该返回真实的job_id
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"创建打印任务失败: {str(e)}"
            }
    
    def _set_parameter(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """设置打印任务参数"""
        try:
            driver = webdriver.Chrome()
            wait = WebDriverWait(driver, 10)
            
            param_name = params.get("name")
            param_value = params.get("value")
            
            if not param_name or not param_value:
                return {
                    "status": "error",
                    "message": "参数名称和值不能为空"
                }
            
            # 查找并设置参数
            param_input = wait.until(
                EC.presence_of_element_located((By.NAME, param_name))
            )
            param_input.clear()
            param_input.send_keys(param_value)
            
            return {
                "status": "success",
                "message": f"成功设置参数 {param_name} = {param_value}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"设置参数失败: {str(e)}"
            }

@tool
def login_with_credentials(**kwargs) -> Dict[str, Any]:
    """专门的登录工具：使用用户名和密码登录指定网站"""
    url = kwargs.get("url")
    username = kwargs.get("username")
    password = kwargs.get("password")
    
    if not all([url, username, password]):
        logger.error("❌ 缺少必要参数: url, username, password")
        return {
            "status": "error",
            "message": "缺少必要参数: url, username, password"
        }
    
    logger.info(f"🔐 开始登录: {username} -> {url}")
    
    try:
        driver = get_driver()
        
        # 1. 打开登录页面
        logger.info(f"🌐 打开登录页面: {url}")
        driver.get(url)
        time.sleep(3)
        
        # 2. 输入用户名 - 查找 id="username"
        username_result = _input_username_by_id(driver, username)
        if username_result["status"] != "success":
            return username_result
        
        # 3. 点击第一个 Continue 按钮
        continue_result = _click_continue_button(driver, "第一个")
        if continue_result["status"] != "success":
            return continue_result
        
        # 4. 输入密码 - 查找包含 "xunshi@123" 的输入框或密码框
        password_result = _input_password_by_placeholder(driver, password)
        if password_result["status"] != "success":
            return password_result
        
        # 5. 点击第二个 Continue 按钮
        continue_result = _click_continue_button(driver, "第二个")
        if continue_result["status"] != "success":
            return continue_result
        
        # 6. 验证登录结果
        return _verify_login_success(driver, url, username)
        
    except Exception as e:
        logger.error(f"❌ 登录失败: {str(e)}")
        return {
            "status": "error",
            "message": f"登录失败: {str(e)}"
        }

def _input_username_by_id(driver: webdriver.Chrome, username: str) -> Dict[str, Any]:
    """根据 id="username" 输入用户名"""
    logger.info(f"👤 输入用户名到 id='username': {username}")
    
    try:
        # 等待用户名输入框出现
        username_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "username"))
        )
        logger.info("✅ 找到用户名输入框: id='username'")
        
        username_element.click()
        time.sleep(0.5)
        username_element.clear()
        username_element.send_keys(username)
        
        return {"status": "success", "message": "用户名输入成功"}
        
    except Exception as e:
        logger.error(f"❌ 输入用户名失败: {str(e)}")
        return {"status": "error", "message": f"输入用户名失败: {str(e)}"}

def _input_password_by_placeholder(driver: webdriver.Chrome, password: str) -> Dict[str, Any]:
    """输入密码到包含 xunshi@123 提示的输入框"""
    logger.info("🔑 输入密码到密码输入框")
    
    # 等待页面加载
    time.sleep(2)
    
    password_selectors = [
        "input[type='password']",
        "input[id='password']",
        "input[name='password']",
        "input[placeholder*='xunshi']",
        "input[placeholder*='password']"
    ]
    
    for selector in password_selectors:
        try:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            logger.info(f"✅ 找到密码输入框: {selector}")
            
            element.click()
            time.sleep(0.5)
            element.clear()
            element.send_keys(password)
            
            return {"status": "success", "message": "密码输入成功"}
            
        except Exception:
            continue
    
    logger.error("❌ 未找到密码输入框")
    return {"status": "error", "message": "未找到密码输入框"}

def _click_continue_button(driver: webdriver.Chrome, button_desc: str) -> Dict[str, Any]:
    """点击 Continue 按钮"""
    logger.info(f"🚀 点击{button_desc} Continue 按钮")
    
    try:
        # 使用 XPath 查找包含 "Continue" 文本的按钮
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]"))
        )
        logger.info("✅ 找到 Continue 按钮")
        
        continue_button.click()
        time.sleep(2)  # 等待页面响应
        
        return {"status": "success", "message": f"{button_desc} Continue 按钮点击成功"}
        
    except Exception as e:
        logger.error(f"❌ 点击 Continue 按钮失败: {str(e)}")
        
        # 如果 XPath 失败，尝试使用 smart_click
        logger.info("🔄 尝试使用智能点击")
        click_result = smart_click({
            "selectors": [
                {"by": "text", "value": "Continue"},
                {"by": "contains_text", "value": "Continue"},
                {"by": "css", "value": "button[type='submit']"},
                {"by": "css", "value": ".continue-btn"},
                {"by": "css", "value": ".btn-primary"}
            ],
            "wait": 10
        })
        
        if click_result.get("status") == "success":
            logger.info(f"✅ 智能点击{button_desc} Continue 按钮成功")
            time.sleep(2)
            return {"status": "success", "message": f"智能点击{button_desc} Continue 按钮成功"}
        else:
            return {
                "status": "error", 
                "message": f"点击{button_desc} Continue 按钮失败: {str(e)}"
            }

def _input_username(driver: webdriver.Chrome, username: str) -> Dict[str, Any]:
    """输入用户名（保留原有的通用方法）"""
    logger.info(f"👤 输入用户名: {username}")
    
    username_selectors = [
        "input[name='email']",
        "input[type='email']",
        "input[name='username']",
        "input[id='email']",
        "input[id='username']",
        "input[placeholder*='email']",
        "input[placeholder*='用户名']",
        "input[placeholder*='邮箱']",
        "input[placeholder*='Email']",
        "input[placeholder*='Username']"
    ]
    
    for selector in username_selectors:
        try:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            logger.info(f"✅ 找到用户名输入框: {selector}")
            
            element.click()
            time.sleep(0.5)
            element.clear()
            element.send_keys(username)
            
            return {"status": "success", "message": "用户名输入成功"}
            
        except Exception:
            continue
    
    logger.error("❌ 未找到用户名输入框")
    return {"status": "error", "message": "未找到用户名输入框"}

def _input_password(driver: webdriver.Chrome, password: str) -> Dict[str, Any]:
    """输入密码（保留原有的通用方法）"""
    logger.info("🔑 输入密码")
    
    password_selectors = [
        "input[name='password']",
        "input[type='password']",
        "input[id='password']",
        "input[placeholder*='密码']",
        "input[placeholder*='password']",
        "input[placeholder*='Password']"
    ]
    
    for selector in password_selectors:
        try:
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            logger.info(f"✅ 找到密码输入框: {selector}")
            
            element.click()
            time.sleep(0.5)
            element.clear()
            element.send_keys(password)
            
            return {"status": "success", "message": "密码输入成功"}
            
        except Exception:
            continue
    
    logger.error("❌ 未找到密码输入框")
    return {"status": "error", "message": "未找到密码输入框"}

def _click_login_button(driver: webdriver.Chrome) -> Dict[str, Any]:
    """使用智能点击登录按钮（保留原有的通用方法）"""
    logger.info("🚀 使用智能点击登录按钮")
    
    login_button_selectors = [
        {"by": "text", "value": "登录"},
        {"by": "text", "value": "Login"},
        {"by": "text", "value": "Sign In"},
        {"by": "text", "value": "登入"},
        {"by": "text", "value": "立即登录"},
        {"by": "contains_text", "value": "登录"},
        {"by": "contains_text", "value": "Login"},
        {"by": "contains_text", "value": "Sign"},
        {"by": "css", "value": "button[type='submit']"},
        {"by": "css", "value": "input[type='submit']"},
        {"by": "css", "value": ".login-button"},
        {"by": "css", "value": "#login-button"},
        {"by": "css", "value": "button[class*='login']"},
        {"by": "css", "value": "button[id*='login']"},
        {"by": "css", "value": ".btn-primary"},
        {"by": "css", "value": ".submit-btn"}
    ]
    
    # 调用智能点击函数
    click_result = smart_click.invoke({"param": {
        "selectors": login_button_selectors,
        "wait": 10
    }})
    
    if click_result.get("status") == "success":
        logger.info("✅ 成功点击登录按钮")
        time.sleep(3)  # 等待登录处理
        return {"status": "success", "message": "登录按钮点击成功"}
    else:
        logger.error(f"❌ 智能点击登录按钮失败: {click_result.get('message')}")
        return {
            "status": "error",
            "message": f"点击登录按钮失败: {click_result.get('message')}"
        }

def _verify_login_success(driver: webdriver.Chrome, original_url: str, username: str) -> Dict[str, Any]:
    """验证登录是否成功"""
    logger.info("⏳ 验证登录结果...")
    time.sleep(3)  # 等待页面加载
    
    current_url = driver.current_url
    page_title = driver.title
    
    logger.info(f"📍 当前URL: {current_url}")
    logger.info(f"📍 页面标题: {page_title}")
    
    # 检查是否还在登录页面
    login_indicators = ["login", "signin", "sign-in", "登录", "auth"]
    is_still_login_page = any(indicator in current_url.lower() for indicator in login_indicators)
    
    # 快速检查是否有错误信息 - 使用 find_elements 避免等待超时
    error_selectors = [
        "div[class*='error']",
        "span[class*='error']", 
        "div[class*='alert']",
        ".error-message",
        ".alert-danger",
        ".login-error",
        ".error-text",
        "[role='alert']"
    ]
    
    error_message = ""
    try:
        # 使用 JavaScript 快速检查错误元素
        script = """
        const selectors = arguments[0];
        for (let selector of selectors) {
            const elements = document.querySelectorAll(selector);
            for (let element of elements) {
                if (element.offsetParent !== null && element.textContent.trim()) {
                    return element.textContent.trim();
                }
            }
        }
        return null;
        """
        error_message = driver.execute_script(script, error_selectors) or ""
        
        if error_message:
            logger.info(f"🔍 发现错误信息: {error_message}")
        else:
            logger.info("🔍 未发现错误信息")
            
    except Exception as e:
        logger.warning(f"⚠️ 检查错误信息时出现异常: {e}")
    
    # 检查是否有成功登录的标识
    success_indicators = []
    try:
        # 检查是否有用户信息、菜单等登录成功的标识
        script = """
        const indicators = [
            'nav', '.navbar', '.user-menu', '.profile', '.dashboard',
            '[class*="user"]', '[class*="profile"]', '[class*="menu"]'
        ];
        let found = [];
        for (let selector of indicators) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                found.push(selector);
            }
        }
        return found;
        """
        success_indicators = driver.execute_script(script) or []
        logger.info(f"🔍 发现成功标识: {success_indicators}")
        
    except Exception as e:
        logger.warning(f"⚠️ 检查成功标识时出现异常: {e}")
    
    # 判断登录结果
    if error_message:
        logger.error(f"❌ 登录失败，发现错误信息: {error_message}")
        return {
            "status": "error",
            "message": f"登录失败: {error_message}",
            "current_url": current_url,
            "page_title": page_title
        }
    elif is_still_login_page and not success_indicators:
        logger.warning("⚠️ 登录可能失败，当前仍在登录页面且无成功标识")
        return {
            "status": "warning", 
            "message": "登录可能失败，请检查账号密码",
            "current_url": current_url,
            "page_title": page_title
        }
    else:
        # URL变化或有成功标识，认为登录成功
        success_reason = []
        if not is_still_login_page:
            success_reason.append("URL已跳转")
        if success_indicators:
            success_reason.append(f"发现成功标识: {success_indicators[:3]}")
        
        reason_text = ", ".join(success_reason) if success_reason else "页面状态正常"
        logger.info(f"✅ 登录成功 ({reason_text})")
        return {
            "status": "success",
            "message": f"用户 '{username}' 登录成功 ({reason_text})",
            "current_url": current_url,
            "page_title": page_title
        }

@tool
def auto_login(user_desc: str = None, **kwargs) -> dict:
    """
    自动登录系统。用 description 匹配 config.yaml accounts，获取 url/username/password，按 continue-continue 流程登录。
    """
    logger.info(f"[auto_login] 调用参数: user_desc={user_desc}, kwargs={kwargs}")
    try:
        if not user_desc:
            raise Exception("未提供用户描述")
            
        logger.info(f"[auto_login] 使用用户描述: {user_desc}")
        
        # 获取用户信息
        user_info = _get_user_info(user_desc)
        if not user_info:
            raise Exception(f"未找到用户信息: {user_desc}")
            
        url = user_info.get("url")
        username = user_info.get("username")
        password = user_info.get("password")
        
        if not url or not username or not password:
            raise Exception(f"用户信息不完整: {user_desc}")
            
        # 获取或初始化 driver
        driver = get_driver()
        if not driver:
            raise Exception("无法初始化浏览器")
            
        logger.info(f"[auto_login] 打开登录页面: {url}")
        driver.get(url)
        time.sleep(2)
        
        # 1. 输入用户名
        username_result = _input_username_by_id(driver, username)
        if username_result["status"] != "success":
            return username_result
            
        # 2. 点击 continue
        continue_result1 = _click_continue_button(driver, "第一个")
        if continue_result1["status"] != "success":
            return continue_result1
            
        # 3. 输入密码
        password_result = _input_password_by_placeholder(driver, password)
        if password_result["status"] != "success":
            return password_result
            
        # 4. 点击 continue
        continue_result2 = _click_continue_button(driver, "第二个")
        if continue_result2["status"] != "success":
            return continue_result2
            
        # 5. 检查登录是否成功
        time.sleep(2)
        current_url = driver.current_url
        if "login" in current_url.lower():
            return {"status": "error", "message": "登录后仍在登录页，登录失败", "current_url": current_url}
            
        return {
            "status": "success",
            "message": "登录成功",
            "current_url": current_url,
            "page_title": driver.title
        }
    except Exception as e:
        logger.error(f"[auto_login] 登录失败: {str(e)}")
        return {
            "status": "error",
            "message": f"登录失败: {str(e)}",
            "current_url": driver.current_url if driver else None,
            "page_title": driver.title if driver else None
        }

def _get_user_info(user_desc: str) -> dict:
    """
    根据用户描述获取用户信息。
    """
    try:
        # 加载账号配置
        from utils.account_utils import load_accounts, find_account_by_user
        accounts = load_accounts()
        account = find_account_by_user(user_desc, accounts)
        
        if not account:
            return None
            
        return {
            "url": account.get("url"),
            "username": account.get("username"),
            "password": account.get("password")
        }
    except Exception as e:
        print(f"[_get_user_info] ❌ 获取用户信息失败: {str(e)}")
        return None

@tool
def get_page_structure(**kwargs) -> Dict[str, Any]:
    """获取当前页面的DOM结构"""
    mode = kwargs.get("mode", "simple")
    include_text = kwargs.get("include_text", True)
    max_depth = kwargs.get("max_depth", 5)
    
    logger.info(f"📄 获取页面结构: mode={mode}")
    
    try:
        driver = get_driver()
        
        if mode == "simple":
            # 简化版本：只获取主要交互元素
            script = """
            function getSimpleStructure() {
                const interactiveElements = document.querySelectorAll(
                    'button, input, select, textarea, a[href], [onclick], [role="button"], [role="link"]'
                );
                
                const structure = [];
                interactiveElements.forEach((el, index) => {
                    if (el.offsetParent !== null || el.tagName === 'INPUT') { // 只获取可见元素
                        structure.push({
                            tag: el.tagName.toLowerCase(),
                            id: el.id || null,
                            class: el.className || null,
                            text: el.textContent?.trim()?.substring(0, 50) || null,
                            type: el.type || null,
                            placeholder: el.placeholder || null,
                            href: el.href || null,
                            index: index
                        });
                    }
                });
                return structure;
            }
            return getSimpleStructure();
            """
            
            elements = driver.execute_script(script)
            
            # 格式化为HTML结构
            html_parts = ["<html><body>"]
            for elem in elements[:20]:  # 限制数量
                tag = elem['tag']
                attrs = []
                if elem['id']:
                    attrs.append(f'id="{elem["id"]}"')
                if elem['class']:
                    attrs.append(f'class="{elem["class"][:30]}..."')
                if elem['type']:
                    attrs.append(f'type="{elem["type"]}"')
                
                attr_str = ' ' + ' '.join(attrs) if attrs else ''
                text = elem['text'][:30] + '...' if elem['text'] and len(elem['text']) > 30 else elem['text'] or ''
                
                if tag in ['input', 'br', 'hr']:
                    html_parts.append(f'  <{tag}{attr_str}/>')
                else:
                    html_parts.append(f'  <{tag}{attr_str}>{text}</{tag}>')
            
            html_parts.append("</body></html>")
            html_structure = '\n'.join(html_parts)
            
            return {
                "status": "success",
                "message": "页面结构获取成功",
                "html_structure": html_structure,
                "element_count": len(elements)
            }
            
        elif mode == "full":
            # 完整版本：获取整个页面结构（简化版）
            script = """
            function getFullStructure(element, depth, maxDepth) {
                if (depth > maxDepth) return null;
                
                const result = {
                    tag: element.tagName.toLowerCase(),
                    id: element.id || null,
                    class: element.className || null,
                    children: []
                };
                
                // 只获取重要文本
                if (element.children.length === 0 && element.textContent) {
                    const text = element.textContent.trim();
                    if (text && text.length < 100) {
                        result.text = text;
                    }
                }
                
                // 递归获取子元素（限制数量）
                for (let i = 0; i < Math.min(element.children.length, 10); i++) {
                    const child = getFullStructure(element.children[i], depth + 1, maxDepth);
                    if (child) {
                        result.children.push(child);
                    }
                }
                
                return result;
            }
            
            return getFullStructure(document.body, 0, arguments[0]);
            """
            
            structure = driver.execute_script(script, max_depth)
            
            # 转换为简化HTML
            def structure_to_html(struct, indent=0):
                if not struct:
                    return ""
                
                tag = struct['tag']
                attrs = []
                if struct.get('id'):
                    attrs.append(f'id="{struct["id"]}"')
                if struct.get('class'):
                    attrs.append(f'class="{struct["class"][:20]}..."')
                
                attr_str = ' ' + ' '.join(attrs) if attrs else ''
                indent_str = '  ' * indent
                
                if not struct.get('children'):
                    text = struct.get('text', '')[:50] if struct.get('text') else ''
                    if tag in ['input', 'br', 'hr']:
                        return f'{indent_str}<{tag}{attr_str}/>'
                    else:
                        return f'{indent_str}<{tag}{attr_str}>{text}</{tag}>'
                else:
                    lines = [f'{indent_str}<{tag}{attr_str}>']
                    for child in struct['children'][:5]:  # 限制子元素数量
                        lines.append(structure_to_html(child, indent + 1))
                    lines.append(f'{indent_str}</{tag}>')
                    return '\n'.join(lines)
            
            html_structure = f"<html><body>\n{structure_to_html(structure, 1)}\n</body></html>"
            
            return {
                "status": "success", 
                "message": "完整页面结构获取成功",
                "html_structure": html_structure
            }
            
        else:
            return {
                "status": "error",
                "message": f"不支持的模式: {mode}，支持的模式: simple, full"
            }
            
    except Exception as e:
        logger.error(f"❌ 获取页面结构失败: {str(e)}")
        return {
            "status": "error",
            "message": f"获取页面结构失败: {str(e)}"
        }

@tool
def create_new_print_job(param: dict) -> dict:
    """
    创建新的打印任务。
    """
    print(f"[create_new_print_job] 调用参数: {param}")
    driver = _driver
    
    try:
        # 1. 点击 New Print Job 按钮
        new_job_result = smart_click.invoke({
            "param": {
                "selectors": [
                    {
                        "by": "xpath",
                        "value": "//button[contains(@class, 'btn-primary')]//div[contains(@class, 'btn-text') and contains(text(), 'New Print Job')]"
                    },
                    {
                        "by": "xpath",
                        "value": "//button[contains(., 'New Print Job')]"
                    }
                ],
                "wait": 10
            }
        })
        
        if new_job_result.get("status") != "success":
            raise Exception(f"点击 New Print Job 按钮失败: {new_job_result.get('message')}")
            
        print("[create_new_print_job] ✅ 成功点击 New Print Job 按钮")
        
        # 2. 等待并填写表单
        sleep(2)  # 等待表单加载
        
        # 3. 选择 Indication
        indication = param.get("indication", "")
        if indication:
            indication_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": f"//div[contains(@class, 'type-name') and text()='{indication}']"
                        },
                        {
                            "by": "xpath",
                            "value": f"//div[contains(@class, 'indication-select')]//div[text()='{indication}']"
                        }
                    ],
                    "wait": 5
                }
            })
            if indication_result.get("status") != "success":
                raise Exception(f"选择 Indication 失败: {indication_result.get('message')}")
            
            # 验证是否选择成功
            try:
                selected_indication = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, f"//span[contains(@class, 'appliance-name') and text()='{indication}']"))
                )
                if not selected_indication.is_displayed():
                    raise Exception("Indication 选择后未显示")
                print(f"[create_new_print_job] ✅ 成功选择 Indication: {indication}")
            except Exception as e:
                raise Exception(f"Indication 选择验证失败: {str(e)}")
        
        # 4. 选择 Orientation
        orientation = param.get("orientation", "")
        if orientation:
            orientation_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": f"//span[contains(.,'{orientation}')]"
                        },
                        {
                            "by": "xpath",
                            "value": f"//div[contains(@class, 'orientation-select')]//div[text()='{orientation}']"
                        }
                    ],
                    "wait": 5
                }
            })
            if orientation_result.get("status") != "success":
                raise Exception(f"选择 Orientation 失败: {orientation_result.get('message')}")
            
            # 验证是否选择成功
            try:
                selected_orientation = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'type-name') and text()='{orientation}']"))
                )
                if not selected_orientation.is_displayed():
                    raise Exception("Orientation 选择后未显示")
                print(f"[create_new_print_job] ✅ 成功选择 Orientation: {orientation}")
            except Exception as e:
                raise Exception(f"Orientation 选择验证失败: {str(e)}")
        
        # 5. 设置 Support Raft
        support_raft = param.get("support_raft", False)
        if support_raft:
            raft_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": "//div[contains(@class, 'support-raft-toggle')]//input[@type='checkbox']"
                        }
                    ],
                    "wait": 5
                }
            })
            if raft_result.get("status") != "success":
                raise Exception(f"设置 Support Raft 失败: {raft_result.get('message')}")
            
            # 验证是否设置成功
            try:
                raft_checkbox = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'support-raft-toggle')]//input[@type='checkbox']"))
                )
                if not raft_checkbox.is_selected():
                    raise Exception("Support Raft 设置后未选中")
                print("[create_new_print_job] ✅ 成功设置 Support Raft")
            except Exception as e:
                raise Exception(f"Support Raft 设置验证失败: {str(e)}")
        
        # 6. 选择 Printer
        printer = param.get("printer", "")
        if printer:
            printer_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": f"//div[contains(@class, 'type-name') and text()='{printer}']"
                        },
                        {
                            "by": "xpath",
                            "value": f"//div[contains(@class, 'printer-select')]//div[text()='{printer}']"
                        }
                    ],
                    "wait": 5
                }
            })
            if printer_result.get("status") != "success":
                raise Exception(f"选择 Printer 失败: {printer_result.get('message')}")
            
            # 验证是否选择成功
            try:
                selected_printer = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'type-name') and text()='{printer}']"))
                )
                if not selected_printer.is_displayed():
                    raise Exception("Printer 选择后未显示")
                print(f"[create_new_print_job] ✅ 成功选择 Printer: {printer}")
            except Exception as e:
                raise Exception(f"Printer 选择验证失败: {str(e)}")
        
        # 7. 选择 Build Platform
        build_platform = param.get("build_platform", "")
        if build_platform:
            platform_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": f"//div[contains(@class, 'type-name') and text()='{build_platform}']"
                        },
                        {
                            "by": "xpath",
                            "value": f"//div[contains(@class, 'build-platform-select')]//div[text()='{build_platform}']"
                        }
                    ],
                    "wait": 5
                }
            })
            if platform_result.get("status") != "success":
                raise Exception(f"选择 Build Platform 失败: {platform_result.get('message')}")
            
            # 验证是否选择成功
            try:
                selected_platform = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'type-name') and text()='{build_platform}']"))
                )
                if not selected_platform.is_displayed():
                    raise Exception("Build Platform 选择后未显示")
                print(f"[create_new_print_job] ✅ 成功选择 Build Platform: {build_platform}")
            except Exception as e:
                raise Exception(f"Build Platform 选择验证失败: {str(e)}")
        
        # 8. 选择 Material
        material = param.get("material", "")
        if material:
            material_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": f"//div[contains(@class, 'type-name') and text()='{material}']"
                        },
                        {
                            "by": "xpath",
                            "value": f"//div[contains(@class, 'material-select')]//div[text()='{material}']"
                        }
                    ],
                    "wait": 5
                }
            })
            if material_result.get("status") != "success":
                raise Exception(f"选择 Material 失败: {material_result.get('message')}")
            
            # 验证是否选择成功
            try:
                selected_material = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'type-name') and text()='{material}']"))
                )
                if not selected_material.is_displayed():
                    raise Exception("Material 选择后未显示")
                print(f"[create_new_print_job] ✅ 成功选择 Material: {material}")
            except Exception as e:
                raise Exception(f"Material 选择验证失败: {str(e)}")
        
        # 9. 点击 Show Advanced 按钮（如果需要）
        show_advanced = param.get("show_advanced", False)
        if show_advanced:
            advanced_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": "//button[contains(@class, 'show-advanced-btn')]"
                        }
                    ],
                    "wait": 5
                }
            })
            if advanced_result.get("status") != "success":
                raise Exception(f"点击 Show Advanced 按钮失败: {advanced_result.get('message')}")
            
            # 验证是否展开成功
            try:
                advanced_section = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'advanced-settings')]"))
                )
                if not advanced_section.is_displayed():
                    raise Exception("Advanced 设置未展开")
                print("[create_new_print_job] ✅ 成功点击 Show Advanced 按钮")
            except Exception as e:
                raise Exception(f"Advanced 设置展开验证失败: {str(e)}")
            
            # 设置高级选项
            layer_thickness = param.get("layer_thickness")
            if layer_thickness:
                # 输入 Layer Thickness
                layer_input = driver.find_element(By.XPATH, "//input[contains(@class, 'layer-thickness-input')]")
                layer_input.clear()
                layer_input.send_keys(str(layer_thickness))
                print(f"[create_new_print_job] ✅ 成功设置 Layer Thickness: {layer_thickness}")
            
            fit_offset = param.get("fit_offset")
            if fit_offset is not None:
                # 输入 Fit Offset
                offset_input = driver.find_element(By.XPATH, "//input[contains(@class, 'fit-offset-input')]")
                offset_input.clear()
                offset_input.send_keys(str(fit_offset))
                print(f"[create_new_print_job] ✅ 成功设置 Fit Offset: {fit_offset}")
            
            mesh_repair = param.get("mesh_repair")
            if mesh_repair is not None:
                # 设置 Mesh Repair
                mesh_checkbox = driver.find_element(By.XPATH, "//input[contains(@class, 'mesh-repair-checkbox')]")
                if mesh_checkbox.is_selected() != mesh_repair:
                    mesh_checkbox.click()
                print(f"[create_new_print_job] ✅ 成功设置 Mesh Repair: {mesh_repair}")
            
            supports = param.get("supports")
            if supports is not None:
                # 设置 Supports
                supports_checkbox = driver.find_element(By.XPATH, "//input[contains(@class, 'supports-checkbox')]")
                if supports_checkbox.is_selected() != supports:
                    supports_checkbox.click()
                print(f"[create_new_print_job] ✅ 成功设置 Supports: {supports}")
            
            orientation_advanced = param.get("orientation_advanced")
            if orientation_advanced is not None:
                # 设置 Orientation Advanced
                orientation_checkbox = driver.find_element(By.XPATH, "//input[contains(@class, 'orientation-advanced-checkbox')]")
                if orientation_checkbox.is_selected() != orientation_advanced:
                    orientation_checkbox.click()
                print(f"[create_new_print_job] ✅ 成功设置 Orientation Advanced: {orientation_advanced}")
            
            layout = param.get("layout")
            if layout is not None:
                # 设置 Layout
                layout_checkbox = driver.find_element(By.XPATH, "//input[contains(@class, 'layout-checkbox')]")
                if layout_checkbox.is_selected() != layout:
                    layout_checkbox.click()
                print(f"[create_new_print_job] ✅ 成功设置 Layout: {layout}")
        
        # 10. 选择 File Source
        file_source = param.get("file_source", "")
        if file_source:
            source_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": f"//div[contains(@class, 'type-name') and text()='{file_source}']"
                        },
                        {
                            "by": "xpath",
                            "value": f"//div[contains(@class, 'file-source-select')]//div[text()='{file_source}']"
                        }
                    ],
                    "wait": 5
                }
            })
            if source_result.get("status") != "success":
                raise Exception(f"选择 File Source 失败: {source_result.get('message')}")
            
            # 验证是否选择成功
            try:
                selected_source = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'type-name') and text()='{file_source}']"))
                )
                if not selected_source.is_displayed():
                    raise Exception("File Source 选择后未显示")
                print(f"[create_new_print_job] ✅ 成功选择 File Source: {file_source}")
            except Exception as e:
                raise Exception(f"File Source 选择验证失败: {str(e)}")
        
        # 11. 点击 Create 按钮
        create_result = smart_click.invoke({
            "param": {
                "selectors": [
                    {
                        "by": "xpath",
                        "value": "//button[contains(@class, 'create-btn')]"
                    }
                ],
                "wait": 5
            }
        })
        if create_result.get("status") != "success":
            raise Exception(f"点击 Create 按钮失败: {create_result.get('message')}")
        
        # 验证是否创建成功
        try:
            success_message = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'success-message')]"))
            )
            if not success_message.is_displayed():
                raise Exception("创建任务后未显示成功消息")
            print("[create_new_print_job] ✅ 成功点击 Create 按钮")
        except Exception as e:
            raise Exception(f"创建任务验证失败: {str(e)}")
        
        return {
            "status": "success",
            "message": "成功创建新的打印任务",
            "details": {
                "indication": indication,
                "orientation": orientation,
                "support_raft": support_raft,
                "printer": printer,
                "build_platform": build_platform,
                "material": material,
                "show_advanced": show_advanced,
                "layer_thickness": layer_thickness if show_advanced else None,
                "fit_offset": fit_offset if show_advanced else None,
                "mesh_repair": mesh_repair if show_advanced else None,
                "supports": supports if show_advanced else None,
                "orientation_advanced": orientation_advanced if show_advanced else None,
                "layout": layout if show_advanced else None,
                "file_source": file_source
            }
        }
        
    except Exception as e:
        print(f"[create_new_print_job] ❌ 创建打印任务失败: {str(e)}")
        return {
            "status": "failed",
            "message": f"创建打印任务失败: {str(e)}"
        }

@tool
def submit_print_job(**kwargs) -> Dict[str, Any]:
    """提交打印任务工具"""
    logger.info("📍 提交打印任务")
    
    try:
        # 查找并点击提交按钮
        submit_result = smart_click.invoke({"param": {
            "selectors": [
                {"by": "text", "value": "Submit"},
                {"by": "text", "value": "提交"},
                {"by": "text", "value": "Create"},
                {"by": "xpath", "value": "//button[contains(text(), 'Submit') or contains(text(), '提交')]"},
                {"by": "css", "value": "[type='submit'], .submit-btn, .create-btn"}
            ],
            "wait": 10
        }})
        
        if submit_result.get("status") == "success":
            logger.info("✅ 成功提交打印任务")
            return {
                "status": "success",
                "message": "打印任务创建成功！"
            }
        else:
            logger.error(f"❌ 提交失败: {submit_result.get('message')}")
            return {
                "status": "error",
                "message": f"提交打印任务失败: {submit_result.get('message')}"
            }
        
    except Exception as e:
        logger.error(f"❌ 提交过程中发生错误: {e}")
        return {
            "status": "error",
            "message": f"提交失败: {str(e)}"
            }

# 添加到工具列表
TOOLS = [
    selenium_get,
    smart_select_and_choose,
    selenium_click,
    smart_select_open,
    selenium_sendkeys,
    selenium_wait_for_element,
    selenium_quit,
    PrintJobTool(),  # 添加新的打印任务工具
    auto_login,  # 添加自动登录工具
    get_page_structure,  # 添加获取页面DOM结构的工具
    create_new_print_job,  # 添加创建新的打印任务工具
    submit_print_job  # 添加提交打印任务工具
]

class IndicationType(str, Enum):
    CROWN = "Crown"
    BRIDGE = "Bridge"
    PARTIAL = "Partial"
    FULL_DENTURE = "Full Denture"
    MODEL = "Model"
    SPLINT = "Splint"
    NIGHT_GUARD = "Night Guard"
    ALIGNER = "Aligner"
    TEMPORARY = "Temporary"
    CUSTOM = "Custom"

class OrientationType(str, Enum):
    AUTOMATIC = "Automatic"
    MANUAL = "Manual"

class BuildPlatformType(str, Enum):
    STANDARD = "Standard"
    CUSTOM = "Custom"

class PrintJobConfig(BaseModel):
    """打印任务配置"""
    # 基本设置
    indication: IndicationType = Field(default=IndicationType.CROWN, description="打印类型")
    orientation: OrientationType = Field(default=OrientationType.AUTOMATIC, description="打印方向")
    support_raft: bool = Field(default=False, description="是否启用支撑筏")
    printer: str = Field(default="", description="打印机名称")
    build_platform: BuildPlatformType = Field(default=BuildPlatformType.STANDARD, description="构建平台类型")
    material: str = Field(default="", description="材料名称")
    
    # 高级设置
    show_advanced: bool = Field(default=False, description="是否显示高级设置")
    layer_thickness: int = Field(default=100, description="层厚度(微米)")
    fit_offset: float = Field(default=0.0, description="拟合偏移")
    mesh_repair: bool = Field(default=True, description="是否启用网格修复")
    supports: bool = Field(default=True, description="是否启用支撑")
    orientation_advanced: bool = Field(default=True, description="是否启用高级方向设置")
    layout: bool = Field(default=True, description="是否启用布局")
    
    # 文件上传
    file_source: str = Field(default="cloud", description="文件来源: cloud 或 computer")
    file_path: Optional[str] = Field(default=None, description="文件路径(本地文件时使用)")

class PrintJobField(BaseModel):
    """打印任务字段配置"""
    name: str
    type: str  # "select", "toggle", "number", "dropdown"
    default_value: Any
    required: bool = False
    options: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    step: Optional[float] = None
    description: str = ""

# 定义所有可配置的字段
PRINT_JOB_FIELDS = {
    "indication": PrintJobField(
        name="Indication",
        type="select",
        default_value="Crown",
        required=True,
        options=[e.value for e in IndicationType],
        description="打印类型"
    ),
    "orientation": PrintJobField(
        name="Orientation",
        type="select",
        default_value="Automatic",
        required=True,
        options=[e.value for e in OrientationType],
        description="打印方向"
    ),
    "support_raft": PrintJobField(
        name="Support Raft",
        type="toggle",
        default_value=False,
        description="是否启用支撑筏"
    ),
    "printer": PrintJobField(
        name="Printer",
        type="dropdown",
        default_value="",
        required=True,
        description="选择打印机"
    ),
    "build_platform": PrintJobField(
        name="Build Platform",
        type="select",
        default_value="Standard",
        required=True,
        options=[e.value for e in BuildPlatformType],
        description="构建平台类型"
    ),
    "material": PrintJobField(
        name="Material",
        type="dropdown",
        default_value="",
        required=True,
        description="选择材料"
    ),
    "layer_thickness": PrintJobField(
        name="Layer Thickness",
        type="number",
        default_value=100,
        required=True,
        min_value=50,
        max_value=200,
        step=10,
        description="层厚度(微米)"
    ),
    "fit_offset": PrintJobField(
        name="Fit Offset",
        type="number",
        default_value=0.0,
        min_value=-1.0,
        max_value=1.0,
        step=0.1,
        description="拟合偏移"
    ),
    "mesh_repair": PrintJobField(
        name="Mesh Repair",
        type="toggle",
        default_value=True,
        description="是否启用网格修复"
    ),
    "supports": PrintJobField(
        name="Supports",
        type="toggle",
        default_value=True,
        description="是否启用支撑"
    ),
    "orientation_advanced": PrintJobField(
        name="Orientation",
        type="toggle",
        default_value=True,
        description="是否启用高级方向设置"
    ),
    "layout": PrintJobField(
        name="Layout",
        type="toggle",
        default_value=True,
        description="是否启用布局"
    )
}

def set_print_job_field(field_name: str, value: Any) -> Dict[str, Any]:
    """设置打印任务字段值
    
    Args:
        field_name: 字段名称
        value: 字段值
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        field_config = PRINT_JOB_FIELDS.get(field_name)
        if not field_config:
            return {
                "status": "error",
                "message": f"未知字段: {field_name}"
            }
            
        # 根据字段类型执行不同的操作
        if field_config.type == "select":
            return select_option(field_config.name, str(value))
        elif field_config.type == "toggle":
            return toggle_option(field_config.name, bool(value))
        elif field_config.type == "number":
            return set_number_value(field_config.name, float(value))
        elif field_config.type == "dropdown":
            return select_dropdown_option(field_config.name, str(value))
        else:
            return {
                "status": "error",
                "message": f"不支持的字段类型: {field_config.type}"
            }
            
    except Exception as e:
        logger.error(f"设置字段 {field_name} 时发生错误: {e}")
        return {
            "status": "error",
            "message": f"设置字段失败: {str(e)}"
        }

def select_option(field_name: str, value: str) -> Dict[str, Any]:
    """选择选项
    
    Args:
        field_name: 字段名称
        value: 选项值
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        driver = get_driver()
        if not driver:
            return {"status": "error", "message": "WebDriver未初始化"}
            
        # 构建选择器
        selectors = [
            f"//div[contains(@class, 'form-group')]//label[contains(text(), '{field_name}')]/following-sibling::div//button[contains(text(), '{value}')]",
            f"//div[contains(@class, 'form-group')]//label[contains(text(), '{field_name}')]/following-sibling::div//div[contains(text(), '{value}')]",
            f"//div[contains(@class, 'form-group')]//label[contains(text(), '{field_name}')]/following-sibling::div//span[contains(text(), '{value}')]"
        ]
        
        # 尝试点击选项
        for selector in selectors:
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                element.click()
                logger.info(f"✅ 成功选择 {field_name}: {value}")
                return {"status": "success", "message": f"已选择 {value}"}
            except:
                continue
                
        return {"status": "error", "message": f"未找到选项: {value}"}
        
    except Exception as e:
        logger.error(f"选择选项时发生错误: {e}")
        return {"status": "error", "message": f"选择选项失败: {str(e)}"}

def toggle_option(field_name: str, value: bool) -> Dict[str, Any]:
    """切换开关选项
    
    Args:
        field_name: 字段名称
        value: 是否启用
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        driver = get_driver()
        if not driver:
            return {"status": "error", "message": "WebDriver未初始化"}
            
        # 构建选择器
        selectors = [
            f"//div[contains(@class, 'form-group')]//label[contains(text(), '{field_name}')]/following-sibling::div//input[@type='checkbox']",
            f"//div[contains(@class, 'form-group')]//label[contains(text(), '{field_name}')]/following-sibling::div//div[contains(@class, 'toggle')]"
        ]
        
        # 尝试切换开关
        for selector in selectors:
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                current_state = element.is_selected() if element.tag_name == "input" else "active" in element.get_attribute("class")
                
                if current_state != value:
                    element.click()
                    
                logger.info(f"✅ 成功切换 {field_name}: {value}")
                return {"status": "success", "message": f"已{'启用' if value else '禁用'} {field_name}"}
            except:
                continue
                
        return {"status": "error", "message": f"未找到开关: {field_name}"}
        
    except Exception as e:
        logger.error(f"切换开关时发生错误: {e}")
        return {"status": "error", "message": f"切换开关失败: {str(e)}"}

def set_number_value(field_name: str, value: float) -> Dict[str, Any]:
    """设置数值
    
    Args:
        field_name: 字段名称
        value: 数值
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        driver = get_driver()
        if not driver:
            return {"status": "error", "message": "WebDriver未初始化"}
            
        # 构建选择器
        selectors = [
            f"//div[contains(@class, 'form-group')]//label[contains(text(), '{field_name}')]/following-sibling::div//input[@type='number']",
            f"//div[contains(@class, 'form-group')]//label[contains(text(), '{field_name}')]/following-sibling::div//input[contains(@class, 'form-control')]"
        ]
        
        # 尝试设置数值
        for selector in selectors:
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                
                # 清除现有值
                element.clear()
                # 输入新值
                element.send_keys(str(value))
                # 触发change事件
                element.send_keys(Keys.TAB)
                
                logger.info(f"✅ 成功设置 {field_name}: {value}")
                return {"status": "success", "message": f"已设置 {field_name} 为 {value}"}
            except:
                continue
                
        return {"status": "error", "message": f"未找到输入框: {field_name}"}
        
    except Exception as e:
        logger.error(f"设置数值时发生错误: {e}")
        return {"status": "error", "message": f"设置数值失败: {str(e)}"}

def select_dropdown_option(field_name: str, value: str) -> Dict[str, Any]:
    """选择下拉选项
    
    Args:
        field_name: 字段名称
        value: 选项值
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        driver = get_driver()
        if not driver:
            return {"status": "error", "message": "WebDriver未初始化"}
            
        # 构建选择器
        dropdown_selectors = [
            f"//div[contains(@class, 'form-group')]//label[contains(text(), '{field_name}')]/following-sibling::div//select",
            f"//div[contains(@class, 'form-group')]//label[contains(text(), '{field_name}')]/following-sibling::div//div[contains(@class, 'dropdown')]"
        ]
        
        # 尝试打开下拉框
        for selector in dropdown_selectors:
            try:
                dropdown = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                # 点击下拉框
                dropdown.click()
                time.sleep(1)  # 等待选项加载
                
                # 构建选项选择器
                option_selectors = [
                    f"//div[contains(@class, 'dropdown-menu')]//a[contains(text(), '{value}')]",
                    f"//div[contains(@class, 'dropdown-menu')]//div[contains(text(), '{value}')]",
                    f"//select/option[contains(text(), '{value}')]"
                ]
                
                # 尝试选择选项
                for option_selector in option_selectors:
                    try:
                        option = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, option_selector))
                        )
                        option.click()
                        
                        logger.info(f"✅ 成功选择 {field_name}: {value}")
                        return {"status": "success", "message": f"已选择 {value}"}
                    except:
                        continue
                        
                return {"status": "error", "message": f"未找到选项: {value}"}
            except:
                continue
                
        return {"status": "error", "message": f"未找到下拉框: {field_name}"}
        
    except Exception as e:
        logger.error(f"选择下拉选项时发生错误: {e}")
        return {"status": "error", "message": f"选择下拉选项失败: {str(e)}"}

def toggle_advanced_settings(show: bool) -> Dict[str, Any]:
    """切换高级设置显示状态
    
    Args:
        show: 是否显示高级设置
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        driver = get_driver()
        if not driver:
            return {"status": "error", "message": "WebDriver未初始化"}
            
        # 构建选择器
        selectors = [
            "//button[contains(text(), 'Show Advanced Settings')]",
            "//button[contains(text(), '高级设置')]",
            "//div[contains(@class, 'advanced-settings-toggle')]"
        ]
        
        # 尝试点击高级设置按钮
        for selector in selectors:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                
                # 检查当前状态
                current_state = "collapsed" not in button.get_attribute("class")
                if current_state != show:
                    button.click()
                    time.sleep(1)  # 等待动画完成
                    
                logger.info(f"✅ 成功{'显示' if show else '隐藏'}高级设置")
                return {"status": "success", "message": f"已{'显示' if show else '隐藏'}高级设置"}
            except:
                continue
                
        return {"status": "error", "message": "未找到高级设置按钮"}
        
    except Exception as e:
        logger.error(f"切换高级设置时发生错误: {e}")
        return {"status": "error", "message": f"切换高级设置失败: {str(e)}"}

def upload_cloud_file() -> Dict[str, Any]:
    """上传云端文件
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        driver = get_driver()
        if not driver:
            return {"status": "error", "message": "WebDriver未初始化"}
            
        # 构建选择器
        selectors = [
            "//button[contains(text(), 'Cloud Drive')]",
            "//button[contains(text(), '云端文件')]",
            "//div[contains(@class, 'cloud-upload')]"
        ]
        
        # 尝试点击云端文件按钮
        for selector in selectors:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                button.click()
                
                # 等待文件选择对话框
                time.sleep(2)
                
                # TODO: 实现文件选择逻辑
                
                logger.info("✅ 成功打开云端文件选择器")
                return {"status": "success", "message": "已打开云端文件选择器"}
            except:
                continue
                
        return {"status": "error", "message": "未找到云端文件按钮"}
        
    except Exception as e:
        logger.error(f"上传云端文件时发生错误: {e}")
        return {"status": "error", "message": f"上传云端文件失败: {str(e)}"}

def upload_local_file(file_path: str) -> Dict[str, Any]:
    """上传本地文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        driver = get_driver()
        if not driver:
            return {"status": "error", "message": "WebDriver未初始化"}
            
        # 构建选择器
        selectors = [
            "//button[contains(text(), 'Computer')]",
            "//button[contains(text(), '本地文件')]",
            "//div[contains(@class, 'local-upload')]"
        ]
        
        # 尝试点击本地文件按钮
        for selector in selectors:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                button.click()
                
                # 等待文件选择对话框
                time.sleep(2)
                
                # 查找文件输入框
                file_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                )
                
                # 设置文件路径
                file_input.send_keys(file_path)
                
                logger.info(f"✅ 成功上传本地文件: {file_path}")
                return {"status": "success", "message": f"已上传文件: {file_path}"}
            except:
                continue
                
        return {"status": "error", "message": "未找到本地文件按钮"}
        
    except Exception as e:
        logger.error(f"上传本地文件时发生错误: {e}")
        return {"status": "error", "message": f"上传本地文件失败: {str(e)}"}

def _scroll_and_click_element(driver, selector, scroll_container=None, scroll_amount=100):
    """
    滚动并点击元素的辅助函数
    """
    try:
        elements = driver.find_elements(selector["by"], selector["value"])
        for element in elements:
            if element.is_displayed():
                # 如果提供了滚动容器，则在容器内滚动
                if scroll_container:
                    driver.execute_script("arguments[0].scrollIntoView(true);", element)
                # 尝试点击元素
                element.click()
                return True
        # 如果提供了滚动容器，尝试滚动
        if scroll_container:
            driver.execute_script(f"arguments[0].scrollTop += {scroll_amount}", scroll_container)
            time.sleep(0.5)
        return False
    except Exception as e:
        logger.error(f"滚动点击元素失败: {str(e)}")
        return False

def _find_and_click_element(driver, selector, max_attempts=5, scroll_step=100):
    """
    查找并点击元素的辅助函数
    """
    for attempt in range(max_attempts):
        try:
            element = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((selector["by"], selector["value"]))
            )
            if element.is_displayed():
                element.click()
                return True
            driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            time.sleep(0.5)
        except Exception as e:
            logger.error(f"点击元素失败: {str(e)}")
            continue
    return False

def _handle_error(error: Exception, context: str) -> dict:
    """统一处理错误"""
    error_msg = f"[{context}] 错误: {str(error)}"
    logger.error(error_msg)
    return {
        "success": False,
        "message": error_msg
    }

def _select_connected_printer(printer: str, wait_time: int) -> dict:
    """选择已连接的打印机"""
    try:
        result = smart_click.invoke({
            "param": {
                "selectors": [
                    {
                        "by": "xpath",
                        "value": f"//mat-option//div[contains(@class, 'printer-name') and text()='{printer}']"
                    },
                    {
                        "by": "xpath",
                        "value": f"//mat-option//div[contains(@class, 'printer-model-name') and text()='{printer}']"
                    }
                ],
                "wait": wait_time
            }
        })
        return result
    except Exception as e:
        return _handle_error(e, "select_connected_printer")

def _select_virtual_printer(printer: str, wait_time: int) -> dict:
    """选择虚拟打印机"""
    try:
        result = smart_click.invoke({
            "param": {
                "selectors": [
                    {
                        "by": "xpath",
                        "value": f"//mat-option//img[@title='printer-text' and contains(@src,'{printer}_text')]"
                    }
                ],
                "wait": wait_time
            }
        })
        return result
    except Exception as e:
        return _handle_error(e, "select_virtual_printer")

def _click_printer_dropdown(wait_time: int) -> dict:
    """点击打印机选择下拉框"""
    try:
        result = smart_click.invoke({
            "param": {
                "selectors": [
                    {
                        "by": "xpath",
                        "value": "//printer-platform-list-v2//div[@class='position-relative']"
                    }
                ],
                "wait": wait_time
            }
        })
        return result
    except Exception as e:
        return _handle_error(e, "click_printer_dropdown")

@tool
def select_printer(param: dict) -> dict:
    """
    智能选择打印机。
    参数:
        param: 包含以下字段的字典:
            - printer: 打印机名称或序列号
            - printer_type: 打印机类型 ('connected' 或 'virtual')
            - wait: 等待时间（秒）
    返回:
        dict: 包含操作结果的字典
    """
    try:
        # 1. 获取参数
        printer = param.get("printer", "")
        printer_type = param.get("printer_type", "connected")
        wait_time = param.get("wait", 10)

        logger.info(f"[select_printer] 调用参数: printer={printer}, type={printer_type}, wait={wait_time}")

        if not printer:
            return {
                "success": False,
                "message": "缺少必要的参数：printer"
            }

        # 2. 点击打印机选择下拉框
        dropdown_result = _click_printer_dropdown(wait_time)
        if not dropdown_result.get("success", False):
            return dropdown_result

        # 3. 等待下拉框展开
        time.sleep(3)

        # 4. 根据打印机类型选择打印机
        if printer_type == "connected":
            printer_result = _select_connected_printer(printer, wait_time)
        else:
            printer_result = _select_virtual_printer(printer, wait_time)

        if not printer_result.get("success", False):
            return printer_result

        logger.info(f"[select_printer] 成功选择打印机: {printer}")
        return {
            "success": True,
            "message": f"成功选择打印机: {printer}"
        }

    except Exception as e:
        return _handle_error(e, "select_printer")