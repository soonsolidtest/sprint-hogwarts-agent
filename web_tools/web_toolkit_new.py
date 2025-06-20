"""
Web Toolkit - 整合版本
提供完整的 Web 自动化工具集，通过模块化设计提高可维护性
"""

# 导入所有模块的工具函数
from .driver_management import get_driver, close_driver, get_current_driver
from .basic_operations import (
    selenium_get,
    selenium_sendkeys,
    selenium_click,
    selenium_wait_for_element,
    selenium_quit,
    _try_click_element,
    _ensure_element_visible,
    _get_extended_selectors
)
from .smart_operations import (
    smart_click,
    smart_select_open,
    smart_select_and_choose
)
from .login_tools import (
    login_with_credentials,
    auto_login
)
from .print_job_tools import (
    create_new_print_job,
    select_printer,
    submit_print_job,
    select_material
)
from .page_analysis import (
    get_page_structure,
    find_elements_by_text,
    find_elements_by_selector,
    wait_for_element
)

# 为了向后兼容，保留全局 WebDriver 实例的引用
_driver = None

def get_driver_compat():
    """向后兼容的 get_driver 函数"""
    global _driver
    if _driver is None:
        _driver = get_driver()
    return _driver

# 导出所有工具函数，保持与原始 web_toolkit.py 相同的接口
__all__ = [
    # 驱动管理
    "get_driver",
    "close_driver", 
    "get_current_driver",
    "get_driver_compat",
    
    # 基础操作
    "selenium_get",
    "selenium_sendkeys",
    "selenium_click",
    "selenium_wait_for_element",
    "selenium_quit",
    "_try_click_element",
    "_ensure_element_visible",
    "_get_extended_selectors",
    
    # 智能操作
    "smart_click",
    "smart_select_open",
    "smart_select_and_choose",
    
    # 登录工具
    "login_with_credentials",
    "auto_login",
    
    # 打印任务工具
    "create_new_print_job",
    "select_printer",
    "submit_print_job",
    "select_material",
    
    # 页面分析
    "get_page_structure",
    "find_elements_by_text",
    "find_elements_by_selector",
    "wait_for_element"
] 