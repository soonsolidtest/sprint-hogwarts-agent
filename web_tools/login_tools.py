from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from time import sleep
from typing import Dict, Any
from langchain_core.tools import tool
import logging
from .driver_management import get_driver
from .basic_operations import selenium_sendkeys
from .smart_operations import smart_click
from config import config
import time

logger = logging.getLogger(__name__)

@tool
def login_with_credentials(**kwargs) -> Dict[str, Any]:
    """专门的登录工具：使用用户名和密码登录指定网站（分步式）"""
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
        sleep(3)
        
        # 2. 输入用户名 - 查找 id=\"username\"
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

def _input_username_by_id(driver, username: str) -> Dict[str, Any]:
    """通过ID输入用户名"""
    try:
        # 等待用户名输入框出现
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        
        # 清空并输入用户名
        username_field.clear()
        username_field.send_keys(username)
        
        logger.info("✅ 用户名输入成功")
        return {"status": "success", "message": "用户名输入成功"}
        
    except TimeoutException:
        logger.error("❌ 用户名输入框未找到")
        return {"status": "error", "message": "用户名输入框未找到"}
    except Exception as e:
        logger.error(f"❌ 输入用户名失败: {str(e)}")
        return {"status": "error", "message": f"输入用户名失败: {str(e)}"}

def _input_password_by_placeholder(driver, password: str) -> Dict[str, Any]:
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

def _click_continue_button(driver, button_desc: str) -> Dict[str, Any]:
    """点击继续按钮"""
    try:
        # 尝试多种选择器找到继续按钮
        continue_selectors = [
            (By.XPATH, f"//button[contains(text(), '{button_desc}')]"),
            (By.XPATH, f"//button[contains(text(), 'Continue')]"),
            (By.XPATH, f"//button[contains(text(), '继续')]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']")
        ]
        
        for by, value in continue_selectors:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, value))
                )
                button.click()
                logger.info(f"✅ 点击继续按钮成功: {value}")
                return {"status": "success", "message": f"点击继续按钮成功: {value}"}
            except TimeoutException:
                continue
        
        logger.error("❌ 未找到可点击的继续按钮")
        return {"status": "error", "message": "未找到可点击的继续按钮"}
        
    except Exception as e:
        logger.error(f"❌ 点击继续按钮失败: {str(e)}")
        return {"status": "error", "message": f"点击继续按钮失败: {str(e)}"}

def _click_login_button(driver) -> Dict[str, Any]:
    """点击登录按钮"""
    try:
        # 尝试多种选择器找到登录按钮
        login_selectors = [
            (By.XPATH, "//button[contains(text(), 'Login')]"),
            (By.XPATH, "//button[contains(text(), '登录')]"),
            (By.XPATH, "//button[@type='submit']"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, ".login-button"),
            (By.CSS_SELECTOR, ".btn-primary")
        ]
        
        for by, value in login_selectors:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, value))
                )
                button.click()
                logger.info(f"✅ 点击登录按钮成功: {value}")
                return {"status": "success", "message": f"点击登录按钮成功: {value}"}
            except TimeoutException:
                continue
        
        logger.error("❌ 未找到可点击的登录按钮")
        return {"status": "error", "message": "未找到可点击的登录按钮"}
        
    except Exception as e:
        logger.error(f"❌ 点击登录按钮失败: {str(e)}")
        return {"status": "error", "message": f"点击登录按钮失败: {str(e)}"}

def _verify_login_success(driver, original_url: str, username: str) -> Dict[str, Any]:
    """验证登录是否成功（恢复为原始web_toolkit.py逻辑）"""
    logger.info("⏳ 验证登录结果...")
    time.sleep(3)  # 等待页面加载
    
    current_url = driver.current_url
    page_title = driver.title
    
    logger.info(f"📍 当前URL: {current_url}")
    logger.info(f"📍 页面标题: {page_title}")
    
    # 轮询等待 URL 变化为目标域名（最多等待10秒）
    target_domain = "designservice.sprintray.com"
    max_wait_time = 10
    poll_interval = 2
    waited_time = 0
    
    logger.info(f"🔄 等待跳转到目标域名: {target_domain}")
    while target_domain not in current_url and waited_time < max_wait_time:
        time.sleep(poll_interval)
        waited_time += poll_interval
        current_url = driver.current_url
        logger.info(f"⏳ 等待中... ({waited_time}s) 当前URL: {current_url}")
        
        # 如果页面还在 authenticating 状态，继续等待
        if "authenticating" in current_url:
            continue
        # 如果已经跳转到其他页面，检查是否为目标域名
        elif target_domain in current_url:
            break
        # 如果跳转到其他非目标页面，可能登录失败
        elif "login" in current_url or "auth" in current_url:
            logger.warning("⚠️ 检测到重新跳转到登录页面")
            break
    
    # 更新最终的 URL 和页面标题
    current_url = driver.current_url
    page_title = driver.title
    logger.info(f"📍 最终URL: {current_url}")
    logger.info(f"📍 最终页面标题: {page_title}")
    
    # 检查是否还在登录页面
    login_indicators = ["login", "signin", "sign-in", "登录", "auth"]
    is_still_login_page = any(indicator in current_url.lower() for indicator in login_indicators)
    
    # 快速检查是否有错误信息 - 使用 JS 一次性查找
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
    elif target_domain in current_url:
        logger.info(f"✅ 登录成功，已跳转到目标域名: {target_domain}")
        return {
            "status": "success",
            "message": f"用户 '{username}' 登录成功，已跳转到 {target_domain}",
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
def auto_login(user_desc: str) -> dict:
    """自动登录，根据用户描述获取登录信息"""
    logger.info(f"🔐 自动登录: {user_desc}")
    
    try:
        # 获取用户信息
        user_info = _get_user_info(user_desc)
        if not user_info:
            return {
                "status": "error",
                "message": f"未找到用户信息: {user_desc}"
            }
        
        print(f"[auto_login] 📝 获取到的用户信息: {user_info}")
        
        # 准备登录参数 - 注意参数名从 login_url 改为 url
        login_params = {
            "url": user_info.get("login_url", "https://dev.account.sprintray.com/"),
            "username": user_info["username"],
            "password": user_info["password"]
        }
        
        print(f"[auto_login] 📤 准备传递给 login_with_credentials 的参数: {login_params}")
        
        # 直接调用原始函数，不使用 .invoke() 方法
        original_func = login_with_credentials.func if hasattr(login_with_credentials, 'func') else login_with_credentials
        login_result = original_func(**login_params)
        
        print(f"[auto_login] 📥 登录结果: {login_result}")
        
        return login_result
        
    except Exception as e:
        logger.error(f"❌ 自动登录失败: {str(e)}")
        return {
            "status": "error",
            "message": f"自动登录失败: {str(e)}"
        }

def _get_user_info(user_desc: str) -> dict:
    """根据用户描述获取用户信息"""
    print(f"[_get_user_info] 🔍 开始查找用户: {user_desc}")
    
    # 从配置文件获取用户信息
    accounts = config.accounts
    print(f"[_get_user_info] 📋 从配置加载的账号数量: {len(accounts)}")
    print(f"[_get_user_info] 📋 账号列表: {accounts}")
    
    # 尝试精确匹配 description
    for account in accounts:
        if account.get('description') == user_desc:
            print(f"[_get_user_info] ✅ 精确匹配找到账号: {account.get('description')}")
            return {
                "username": account.get('username'),
                "password": account.get('password'),
                "login_url": account.get('url', "https://dev.account.sprintray.com/")
            }
    
    # 尝试模糊匹配 description
    for account in accounts:
        description = account.get('description', '')
        if user_desc.lower() in description.lower() or description.lower() in user_desc.lower():
            print(f"[_get_user_info] ✅ 模糊匹配找到账号: {account.get('description')}")
            return {
                "username": account.get('username'),
                "password": account.get('password'),
                "login_url": account.get('url', "https://dev.account.sprintray.com/")
            }
    
    # 尝试匹配 username
    for account in accounts:
        username = account.get('username', '')
        if user_desc.lower() in username.lower() or username.lower() in user_desc.lower():
            print(f"[_get_user_info] ✅ 用户名匹配找到账号: {account.get('description')}")
            return {
                "username": account.get('username'),
                "password": account.get('password'),
                "login_url": account.get('url', "https://dev.account.sprintray.com/")
            }
    
    print(f"[_get_user_info] ❌ 未找到匹配的账号")
    return None 