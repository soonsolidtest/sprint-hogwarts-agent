from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from pathlib import Path
import logging
import os
import stat
from config import config

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

def get_current_driver():
    """获取当前 WebDriver 实例"""
    return _driver 