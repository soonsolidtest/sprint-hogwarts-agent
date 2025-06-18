from typing import Dict, Any, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from web_tools.web_toolkit import get_driver
import logging

logger = logging.getLogger(__name__)

def select_printer(driver,printer_name: str) -> Dict[str, Any]:
    """选择指定的打印机
    
    Args:
        driver: WebDriver 实例
        printer_name: 打印机名称
        
    Returns:
        Dict[str, Any]: 包含操作结果的字典
    """
    try:
        if not driver:
            raise Exception("无法获取浏览器实例")
        
        # 等待打印机列表加载
        wait = WebDriverWait(driver, 10)
        printer_list = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.printer-list"))
        )
        
        # 查找指定打印机
        printer_elements = printer_list.find_elements(By.CSS_SELECTOR, "div.printer-item")
        target_printer = None
        
        for printer in printer_elements:
            name_element = printer.find_element(By.CSS_SELECTOR, "div.printer-name")
            if name_element.text.strip() == printer_name:
                target_printer = printer
                break
        
        if not target_printer:
            raise NoSuchElementException(f"未找到打印机: {printer_name}")
        
        # 点击选择打印机
        target_printer.click()
        
        # 等待打印机状态更新
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f"div.printer-item.selected[data-name='{printer_name}']"))
        )
        
        logger.info(f"✅ 成功选择打印机: {printer_name}")
        return {
            "status": "success",
            "message": f"已选择打印机: {printer_name}",
            "printer_name": printer_name
        }
        
    except TimeoutException:
        error_msg = "等待打印机列表超时"
        logger.error(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg
        }
    except NoSuchElementException as e:
        error_msg = str(e)
        logger.error(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg
        }
    except Exception as e:
        error_msg = f"选择打印机时发生错误: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {
            "status": "error",
            "message": error_msg
        } 