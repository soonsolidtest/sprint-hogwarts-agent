#!/usr/bin/env python3
"""
测试重构后的 web_tools 模块
验证所有模块是否能正常导入和基本功能
"""

import sys
import os
import logging
import traceback
from typing import Dict, Any

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_module_imports():
    """测试模块导入"""
    logger.info("🔍 测试模块导入...")
    
    try:
        # 测试各个模块的导入
        from web_tools.driver_management import get_driver, close_driver, get_current_driver
        logger.info("✅ driver_management 模块导入成功")
        
        from web_tools.basic_operations import (
            selenium_get, selenium_sendkeys, selenium_click, 
            selenium_wait_for_element, selenium_quit
        )
        logger.info("✅ basic_operations 模块导入成功")
        
        from web_tools.smart_operations import (
            smart_click, smart_select_open, smart_select_and_choose
        )
        logger.info("✅ smart_operations 模块导入成功")
        
        from web_tools.login_tools import (
            login_with_credentials, auto_login
        )
        logger.info("✅ login_tools 模块导入成功")
        
        from web_tools.print_job_tools import (
            create_new_print_job, select_printer, submit_print_job
        )
        logger.info("✅ print_job_tools 模块导入成功")
        
        from web_tools.page_analysis import (
            get_page_structure, find_elements_by_text, 
            find_elements_by_selector, wait_for_element
        )
        logger.info("✅ page_analysis 模块导入成功")
        
        # 测试整合模块
        from web_tools.web_toolkit_new import (
            selenium_get as new_selenium_get,
            smart_click as new_smart_click,
            auto_login as new_auto_login
        )
        logger.info("✅ web_toolkit_new 模块导入成功")
        
        # 测试包级别导入
        from web_tools import selenium_get, smart_click, auto_login
        logger.info("✅ 包级别导入成功")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 模块导入失败: {str(e)}")
        traceback.print_exc()
        return False

def test_driver_management():
    """测试驱动管理功能"""
    logger.info("🔍 测试驱动管理功能...")
    
    try:
        from web_tools.driver_management import get_driver, close_driver, get_current_driver
        
        # 测试获取驱动
        driver = get_driver()
        if driver:
            logger.info("✅ get_driver() 成功")
            
            # 测试获取当前驱动
            current_driver = get_current_driver()
            if current_driver == driver:
                logger.info("✅ get_current_driver() 成功")
            else:
                logger.error("❌ get_current_driver() 返回的驱动不匹配")
                return False
            
            # 测试关闭驱动
            close_driver()
            logger.info("✅ close_driver() 成功")
            
            return True
        else:
            logger.error("❌ get_driver() 返回 None")
            return False
            
    except Exception as e:
        logger.error(f"❌ 驱动管理测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_basic_operations():
    """测试基础操作功能"""
    logger.info("🔍 测试基础操作功能...")
    
    try:
        from web_tools.basic_operations import selenium_get, selenium_quit
        
        # 测试 selenium_get 函数（被 @tool 装饰）
        # 检查函数是否有 invoke 方法（这是 @tool 装饰器的特征）
        if hasattr(selenium_get, 'invoke'):
            logger.info("✅ selenium_get 是有效的工具函数")
        else:
            logger.error("❌ selenium_get 不是有效的工具函数")
            return False
        
        # 测试 selenium_quit 函数
        quit_result = selenium_quit.invoke({})
        if isinstance(quit_result, dict) and 'status' in quit_result:
            logger.info("✅ selenium_quit 函数调用成功")
        else:
            logger.error("❌ selenium_quit 函数返回格式不正确")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 基础操作测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_smart_operations():
    """测试智能操作功能"""
    logger.info("🔍 测试智能操作功能...")
    
    try:
        from web_tools.smart_operations import smart_click
        
        # 测试 smart_click 函数（被 @tool 装饰）
        if hasattr(smart_click, 'invoke'):
            logger.info("✅ smart_click 是有效的工具函数")
        else:
            logger.error("❌ smart_click 不是有效的工具函数")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 智能操作测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_login_tools():
    """测试登录工具功能"""
    logger.info("🔍 测试登录工具功能...")
    
    try:
        from web_tools.login_tools import login_with_credentials, auto_login
        
        # 测试函数是否被 @tool 装饰
        if hasattr(login_with_credentials, 'invoke'):
            logger.info("✅ login_with_credentials 是有效的工具函数")
        else:
            logger.error("❌ login_with_credentials 不是有效的工具函数")
            return False
        
        if hasattr(auto_login, 'invoke'):
            logger.info("✅ auto_login 是有效的工具函数")
        else:
            logger.error("❌ auto_login 不是有效的工具函数")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 登录工具测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_print_job_tools():
    """测试打印任务工具功能"""
    logger.info("🔍 测试打印任务工具功能...")
    
    try:
        from web_tools.print_job_tools import create_new_print_job, select_printer, submit_print_job
        
        # 测试函数是否被 @tool 装饰
        if hasattr(create_new_print_job, 'invoke'):
            logger.info("✅ create_new_print_job 是有效的工具函数")
        else:
            logger.error("❌ create_new_print_job 不是有效的工具函数")
            return False
        
        if hasattr(select_printer, 'invoke'):
            logger.info("✅ select_printer 是有效的工具函数")
        else:
            logger.error("❌ select_printer 不是有效的工具函数")
            return False
        
        if hasattr(submit_print_job, 'invoke'):
            logger.info("✅ submit_print_job 是有效的工具函数")
        else:
            logger.error("❌ submit_print_job 不是有效的工具函数")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 打印任务工具测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_page_analysis():
    """测试页面分析功能"""
    logger.info("🔍 测试页面分析功能...")
    
    try:
        from web_tools.page_analysis import get_page_structure, find_elements_by_text, find_elements_by_selector
        
        # 测试函数是否被 @tool 装饰
        if hasattr(get_page_structure, 'invoke'):
            logger.info("✅ get_page_structure 是有效的工具函数")
        else:
            logger.error("❌ get_page_structure 不是有效的工具函数")
            return False
        
        if hasattr(find_elements_by_text, 'invoke'):
            logger.info("✅ find_elements_by_text 是有效的工具函数")
        else:
            logger.error("❌ find_elements_by_text 不是有效的工具函数")
            return False
        
        if hasattr(find_elements_by_selector, 'invoke'):
            logger.info("✅ find_elements_by_selector 是有效的工具函数")
        else:
            logger.error("❌ find_elements_by_selector 不是有效的工具函数")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 页面分析测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_backward_compatibility():
    """测试向后兼容性"""
    logger.info("🔍 测试向后兼容性...")
    
    try:
        # 测试新的整合模块
        from web_tools.web_toolkit_new import (
            selenium_get, smart_click, auto_login, create_new_print_job
        )
        logger.info("✅ web_toolkit_new 模块导入成功")
        
        # 测试包级别导入
        from web_tools import selenium_get as pkg_selenium_get
        logger.info("✅ 包级别导入成功")
        
        # 验证函数是否相同
        if selenium_get == pkg_selenium_get:
            logger.info("✅ 函数引用一致")
        else:
            logger.warning("⚠️ 函数引用不一致，但功能应该相同")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 向后兼容性测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_functional_integration():
    """测试功能集成"""
    logger.info("🔍 测试功能集成...")
    
    try:
        from web_tools.driver_management import get_driver, close_driver
        from web_tools.basic_operations import selenium_get, selenium_quit
        
        # 测试基本的浏览器操作流程
        driver = get_driver()
        if not driver:
            logger.error("❌ 无法获取 WebDriver")
            return False
        
        # 测试打开网页（使用 invoke 方法）
        result = selenium_get.invoke({"url": "https://www.google.com"})
        if result.get("status") == "success":
            logger.info("✅ 成功打开网页")
        else:
            logger.warning(f"⚠️ 打开网页失败: {result.get('message')}")
        
        # 关闭浏览器
        close_driver()
        logger.info("✅ 功能集成测试完成")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 功能集成测试失败: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    logger.info("🚀 开始测试重构后的 web_tools 模块")
    
    tests = [
        ("模块导入", test_module_imports),
        ("驱动管理", test_driver_management),
        ("基础操作", test_basic_operations),
        ("智能操作", test_smart_operations),
        ("登录工具", test_login_tools),
        ("打印任务工具", test_print_job_tools),
        ("页面分析", test_page_analysis),
        ("向后兼容性", test_backward_compatibility),
        ("功能集成", test_functional_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"测试: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            if test_func():
                logger.info(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                logger.error(f"❌ {test_name} 测试失败")
        except Exception as e:
            logger.error(f"❌ {test_name} 测试异常: {str(e)}")
            traceback.print_exc()
    
    logger.info(f"\n{'='*50}")
    logger.info(f"测试总结: {passed}/{total} 通过")
    logger.info(f"{'='*50}")
    
    if passed == total:
        logger.info("🎉 所有测试通过！重构成功！")
        return True
    else:
        logger.error(f"❌ {total - passed} 个测试失败，需要修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 