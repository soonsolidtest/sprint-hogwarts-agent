# Web Tools Package
# 提供完整的 Web 自动化工具集

from .driver_management import get_driver, close_driver, get_current_driver
from .basic_operations import (
    selenium_get,
    selenium_sendkeys,
    selenium_click,
    selenium_wait_for_element,
    selenium_quit,
    _try_click_element,
    _ensure_element_visible,
    _get_extended_selectors,
    _display_find_element
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

# 导出所有工具函数
__all__ = [
    # 驱动管理
    "get_driver",
    "close_driver", 
    "get_current_driver",
    
    # 基础操作
    "selenium_get",
    "selenium_sendkeys",
    "selenium_click",
    "selenium_wait_for_element",
    "selenium_quit",
    "_try_click_element",
    "_ensure_element_visible",
    "_get_extended_selectors",
    "_display_find_element",
    
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
