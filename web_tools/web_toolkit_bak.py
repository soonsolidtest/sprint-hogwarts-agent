from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, JavascriptException
from time import sleep
from pathlib import Path
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage


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
        self.driver.get(url)
        sleep(2)
        # return self.get_dom_snapshot(mode="full")

    def click(self, by: str, value: str):
        try:
            element = self.driver.find_element(self._map_by(by), value)
            element.click()
            sleep(1)
            return self.get_dom_snapshot()
        except NoSuchElementException:
            return {"error": f"未找到元素: {by}={value}"}

    def send_keys(self, by: str, value: str, text: str):
        try:
            element = self.driver.find_element(self._map_by(by), value)
            element.clear()
            element.send_keys(text)
            sleep(1)
            return self.get_dom_snapshot()
        except NoSuchElementException:
            return {"error": f"未找到元素: {by}={value}"}

    def wait_for_element(self, by: str, value: str, timeout: int = 10):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((self._map_by(by), value)))
            return {"status": "元素已出现", "by": by, "value": value}
        except:
            return ToolMessage(
                tool_name="selenium_wait_for_element",
                content=f"等待超时，未找到元素: {by}={value}",
                additional_kwargs={"failed": True}
            )

    def wait_until_text(self, by: str, value: str, target_text: str, timeout: int = 10):
        def check_text(driver):
            try:
                el = driver.find_element(self._map_by(by), value)
                return target_text in el.text
            except:
                return False

        try:
            WebDriverWait(self.driver, timeout).until(check_text)
            return self.get_dom_snapshot()
        except:
            return ToolMessage(
                tool_name="wait_until_text",
                content=f"等待超时，未找到元素: {by}={value}",
                additional_kwargs={"failed": True}
            )
    def quit(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
            return {"status": "浏览器已关闭"}
        return {"warning": "浏览器尚未启动"}

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

    def get_dom_snapshot(self, mode: str = "browser_use") -> dict | str:
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
            raise ValueError(f"不支持的模式: {mode}")

        js_path = js_dir / js_file
        if not js_path.exists():
            raise FileNotFoundError(f"找不到 JS 文件: {js_path}")

        print(f"正在加载 JS 文件：{js_path}")

        js_code = js_path.read_text(encoding="utf-8")
        # print("🔍 执行 JS 内容预览（前 500 字符）:")
        # print(js_code[:500])

        try:
            # js_wrapped = f"return ({js_code})();"
            js_wrapped = js_code
            self.driver.execute_script(js_wrapped)
        except JavascriptException as e:
            return {"error": str(e)}

# 单例对象
toolkit = WebToolkit()

# 工具导出（供 LangChain/LangGraph 使用）
@tool
def selenium_get(url: str):
    """打开指定网址"""
    print(f"[selenium_get] 准备打开：{url}")
    return toolkit.open(url)

@tool
def selenium_click(by: str, value: str):
    """点击指定元素"""
    return toolkit.click(by, value)

@tool
def selenium_sendkeys(by: str, value: str, text: str):
    """输入指定内容"""
    return toolkit.send_keys(by, value, text)

@tool
def selenium_wait_for_element(by: str, value: str, timeout: int = 10):
    """等待元素加载"""
    return toolkit.wait_for_element(by, value, timeout)

@tool
def selenium_wait_until_text(by: str, value: str, target_text: str, timeout: int = 10):
    """等待文本加载"""
    return toolkit.wait_until_text(by, value, target_text, timeout)


from selenium.common.exceptions import NoSuchElementException
import time


@tool
def smart_click(param: dict) -> dict:
    """
    智能点击页面元素，尝试多种方式定位。支持 by: id, name, xpath, css, text, contains_text。
    参数格式:
    {
        "selectors": [
            {"by": "id", "value": "submit"},
            {"by": "xpath", "value": "//button[text()='登录']"},
            {"by": "text", "value": "登录"},
            {"by": "contains_text", "value": "元素"}
        ],
        "wait": 5
    }
    """
    print(f"[smart_click] 调用参数: {param}")
    selectors = param.get("selectors", [])
    wait_time = param.get("wait", 5)
    driver = toolkit.driver  # 假设你通过 toolkit.driver 拿到 WebDriver 实例

    for _ in range(wait_time):
        for selector in selectors:
            by = selector.get("by")
            value = selector.get("value").strip()  # 自动清除空格和换行

            try:
                element = None
                if by == "id":
                    element = driver.find_element("id", value)
                elif by == "text":
                    xpath = f"//*[contains(normalize-space(text()), '{value}')]"
                    elements = driver.find_elements("xpath", xpath)
                    if elements:
                        element = elements[0]
                elif by == "name":
                    element = driver.find_element("name", value)
                elif by == "xpath":
                    element = driver.find_element("xpath", value)
                elif by == "css":
                    element = driver.find_element("css selector", value)
                elif by == "exact_text":
                    # 遍历按钮/链接等元素，精确匹配文本
                    candidates = driver.find_elements("xpath", "//*[self::button or self::a or self::div or self::span]")
                    for el in candidates:
                        if el.text.strip() == value:
                            element = el
                            break

                if element:
                    try:
                        element.click()
                    except Exception as e:
                        # 尝试被遮挡时，用 JS 点击兜底
                        print(f"[smart_click] 正常点击失败，尝试 JS 点击: {e}")
                        driver.execute_script("arguments[0].click();", element)

                    return {
                        "status": "success",
                        "message": f"[smart_click] 点击成功: {by}={value}",
                        "selector": selector
                    }

            except NoSuchElementException:
                continue
            except Exception as e:
                print(f"[smart_click] 尝试 {by}={value} 时报错：{e}")
        time.sleep(1)

    return {
        "status": "failed",
        "message": "[smart_click] 未能成功找到并点击任何元素。",
    }

@tool
def selenium_quit():
    """退出工具"""
    return toolkit.quit()
