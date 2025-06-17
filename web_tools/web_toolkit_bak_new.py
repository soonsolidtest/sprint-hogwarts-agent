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
            self.driver.execute_script(js_code)
            return {"status": "success", "message": "DOM Snapshot 脚本执行成功"}
        except JavascriptException as e:
            return {"status": "failed", "message": str(e)}

# 单例对象
toolkit = WebToolkit()


# 工具导出
@tool
def selenium_get(url: str):
    """打开指定网址"""
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

@tool
def selenium_quit():
    """退出工具"""
    return toolkit.quit()

# 智能点击工具
@tool
def smart_click(param: dict) -> dict:
    """
    智能点击页面元素，尝试多种方式定位。。常用 selector 类型包括：

    - id
    - name
    - xpath
    - css
    - text
    - contains_text
    - exact_text
    - image_src：适用于点击图标、按钮上的图片，如 <img src="edit.png"> 或类似图片链接。
    示例：
    如果你要点击一个铅笔图标按钮，可以传入：
    {
        "selectors": [{"by": "image_src", "value": "edit.png"}]
    }
    参数格式:
    {
        "selectors": [
            {"by": "id", "value": "submit"},
            {"by": "xpath", "value": "//button[text()='登录']"},
            {"by": "text", "value": "登录"},
            {"by": "contains_text", "value": "元素"},
            {"by": "image_src", "value": "xxx.png"}
        ],
        "wait": 5
    }
    """
    print(f"[smart_click] 调用参数: {param}")
    selectors = param.get("selectors", [])
    wait_time = param.get("wait", 5)
    driver = toolkit.driver

    for second in range(wait_time):
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
                elif by == "image_src":
                    # 查找 img[src*='xxx']
                    img_xpath = f"//img[contains(@src, '{value}')]"
                    images = driver.find_elements("xpath", img_xpath)
                    for img in images:
                        if not img.is_displayed():
                            continue
                        try:
                            img.click()
                            return {
                                "status": "success",
                                "message": f"[smart_click] 点击成功: {by}={value}（点击 <img> 元素）",
                                "selector": selector
                            }
                        except Exception as e:
                            print(f"[smart_click] 图片点击失败: {e}")
                            # 尝试点击父级
                            try:
                                parent = img.find_element("xpath", "..")
                                parent.click()
                                return {
                                    "status": "success",
                                    "message": f"[smart_click] 点击成功: {by}={value}（点击父级）",
                                    "selector": selector
                                }
                            except Exception as e2:
                                print(f"[smart_click] 父级点击也失败: {e2}")
                elif by in ["text", "contains_text"]:
                    xpath = f"//*[contains(normalize-space(text()), '{value}')]"
                    elements = driver.find_elements("xpath", xpath)

                    for el in elements:
                        if not el.is_displayed():
                            continue

                        # Step 1: 尝试直接点击元素本身
                        try:
                            el.click()
                            return {
                                "status": "success",
                                "message": f"[smart_click] 点击成功: {by}={value}（直接点击）",
                                "selector": selector
                            }
                        except Exception as e:
                            print(f"[smart_click] 直接点击失败: {e}")

                        # Step 2: 向上追溯最多 3 层父级，尝试点击
                        clickable_el = el
                        try:
                            for _ in range(3):
                                parent = clickable_el.find_element("xpath", "..")
                                tag = parent.tag_name.lower()
                                if tag in ["button", "a", "div"]:
                                    clickable_el = parent
                                else:
                                    break

                                try:
                                    clickable_el.click()
                                    return {
                                        "status": "success",
                                        "message": f"[smart_click] 点击成功: {by}={value}（上溯点击）",
                                        "selector": selector
                                    }
                                except Exception as e2:
                                    print(f"[smart_click] 上溯点击失败: {e2}")
                        except Exception as e3:
                            print(f"[smart_click] 查找父级失败: {e3}")
                elif by == "exact_text":
                    candidates = driver.find_elements("xpath", "//*[self::button or self::a or self::div or self::span]")
                    for el in candidates:
                        if el.text.strip() == value:
                            element = el
                            break
                else:
                    print(f"[smart_click] 不支持的 selector 类型: {by}")
                    continue

                if element and element.is_displayed():
                    try:
                        element.click()
                    except Exception as e:
                        print(f"[smart_click] 正常点击失败，尝试 JS 点击: {e}")
                        try:
                            driver.execute_script("arguments[0].click();", element)
                        except Exception as js_e:
                            print(f"[smart_click] JS 点击失败: {js_e}")
                            continue

                    return {
                        "status": "success",
                        "message": f"[smart_click] 点击成功: {by}={value}",
                        "selector": selector
                    }

            except NoSuchElementException:
                print(f"[smart_click] 找不到元素: {by}={value}")
                continue
            except Exception as e:
                print(f"[smart_click] 尝试 {by}={value} 报错: {e}")
        sleep(1)

    return {
        "status": "failed",
        "message": "[smart_click] 未能成功找到并点击任何元素。",
        "tried_selectors": selectors
    }

@tool
def smart_select_open(param: dict) -> dict:
    """
    智能定位并点击“选择框”元素，常用于打开下拉菜单。
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
    智能选择选择框并选择指定选项。
    参数示例：
    {
        "text": "Printer",
        "option": "Midas",
        "wait": 5
    }
    """
    print(f"[smart_select_and_choose] 调用参数: {param}")
    text = param.get("text")
    option = param.get("option")
    wait = param.get("wait", 5)

    if not text or not option:
        return {
            "status": "failed",
            "message": "[smart_select_and_choose] 缺少必要参数 text 或 option"
        }

    try:
        # 调用 smart_select_open 工具
        open_result = smart_select_open_tool.invoke({
            "param": {
                "selectors": [{"by": "text", "value": text}],
                "wait": wait
            }
        })

        if open_result.get("status") != "success":
            return {
                "status": "failed",
                "message": f"[smart_select_and_choose] 无法点击选择框: {text}",
                "step": "open"
            }

        sleep(1)

        # 调用 smart_click 工具
        click_result = smart_click_tool.invoke({
            "param": {
                "selectors": [
                    {"by": "text", "value": option},
                    {"by": "contains_text", "value": option}
                ],
                "wait": wait
            }
        })

        if click_result.get("status") != "success":
            return {
                "status": "failed",
                "message": f"[smart_select_and_choose] 无法选择选项: {option}",
                "step": "choose"
            }

        return {
            "status": "success",
            "message": f"[smart_select_and_choose] 成功选择 '{option}'",
            "step": "done"
        }

    except Exception as e:
        return {
            "status": "failed",
            "message": f"[smart_select_and_choose] 异常: {e}",
            "step": "exception"
        }

smart_select_and_choose_tool = RunnableLambda(smart_select_and_choose)