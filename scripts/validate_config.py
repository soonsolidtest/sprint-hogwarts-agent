#!/usr/bin/env python3
"""
配置验证脚本
检查 config.yaml 中的配置是否正确
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config
import requests
from urllib.parse import urlparse

def validate_llm_config():
    """验证 LLM 配置"""
    print("🔍 验证 LLM 配置...")
    
    llm_config = config.llm
    required_fields = ['api_key', 'api_base', 'model']
    
    for field in required_fields:
        if not llm_config.get(field):
            print(f"❌ LLM 配置缺少必要字段: {field}")
            return False
    
    print(f"✅ LLM 配置验证通过")
    print(f"   - API Base: {llm_config['api_base']}")
    print(f"   - Model: {llm_config['model']}")
    return True

def validate_accounts_config():
    """验证账号配置"""
    print("\n🔍 验证账号配置...")
    
    accounts = config.accounts
    if not accounts:
        print("❌ 未配置任何账号")
        return False
    
    for i, account in enumerate(accounts):
        required_fields = ['description', 'url', 'username', 'password']
        missing_fields = [field for field in required_fields if not account.get(field)]
        
        if missing_fields:
            print(f"❌ 账号 {i+1} 缺少字段: {missing_fields}")
            return False
        
        print(f"✅ 账号 {account['description']} 配置正确")
    
    return True



def validate_browser_config():
    """验证浏览器配置"""
    print("\n🔍 验证浏览器配置...")
    
    browser_config = config.browser
    if not browser_config:
        print("❌ 未配置浏览器")
        return False
    
    # 检查窗口大小格式
    window_size = browser_config.get('window_size')
    if window_size and (not isinstance(window_size, list) or len(window_size) != 2):
        print(f"❌ 窗口大小格式错误: {window_size}")
        return False
    
    print("✅ 浏览器配置验证通过")
    print(f"   - 类型: {browser_config.get('type', 'chrome')}")
    print(f"   - 无头模式: {browser_config.get('headless', False)}")
    print(f"   - 窗口大小: {window_size}")
    
    return True

def validate_design_service_config():
    """验证 Design Service 配置"""
    print("\n🔍 验证 Design Service 配置...")
    
    design_service_config = config.design_service
    if not design_service_config:
        print("❌ 未配置 Design Service 系统")
        return False
    
    # 检查必要字段
    required_fields = ['base_url', 'urls', 'page_indicators']
    for field in required_fields:
        if not design_service_config.get(field):
            print(f"❌ Design Service 配置缺少字段: {field}")
            return False
    
    # 检查 URLs
    urls = design_service_config['urls']
    required_urls = ['home', 'rayware', 'print_history', 'new_print_job']
    
    for url_key in required_urls:
        if not urls.get(url_key):
            print(f"❌ Design Service URLs 缺少: {url_key}")
            return False
        
        # 验证 URL 格式
        url = urls[url_key]
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            print(f"❌ 无效的 URL 格式: {url_key} = {url}")
            return False
    
    print("✅ Design Service 配置验证通过")
    for key, url in urls.items():
        print(f"   - {key}: {url}")
    
    return True



def test_design_service_urls():
    """测试 Design Service URLs 的可访问性"""
    print("\n🌐 测试 Design Service URLs 可访问性...")
    
    design_service_config = config.design_service
    urls = design_service_config.get('urls', {})
    
    for name, url in urls.items():
        try:
            print(f"🔄 测试 {name}: {url}")
            response = requests.head(url, timeout=10, allow_redirects=True)
            
            if response.status_code < 400:
                print(f"✅ {name} 可访问 (状态码: {response.status_code})")
            else:
                print(f"⚠️ {name} 返回状态码: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} 无法访问: {str(e)}")
    
    return True

def test_config_methods():
    """测试配置方法"""
    print("\n🧪 测试配置方法...")
    
    # 测试 get_design_service_url
    test_pages = ['home', 'rayware', 'print_history', 'new_print_job']
    for page in test_pages:
        url = config.get_design_service_url(page)
        if url:
            print(f"✅ get_design_service_url('{page}') = {url}")
        else:
            print(f"❌ get_design_service_url('{page}') 返回空值")
    
    # 测试向后兼容的 get_rayware_url
    print("\n🔄 测试向后兼容方法...")
    for page in test_pages:
        url = config.get_rayware_url(page)
        if url:
            print(f"✅ get_rayware_url('{page}') = {url}")
        else:
            print(f"❌ get_rayware_url('{page}') 返回空值")
    
    # 测试 check_design_service_page
    test_urls = [
        "https://dev.designservice.sprintray.com/print-setup",
        "https://dev.designservice.sprintray.com/print-history",
        "https://dev.designservice.sprintray.com/home-screen",
        "https://other-site.com/page"
    ]
    
    for test_url in test_urls:
        page_type = config.check_design_service_page(test_url)
        print(f"✅ check_design_service_page('{test_url}') = {page_type}")
    
    # 测试 get_account_by_description
    test_users = ['user1', 'wangyili', 'nonexistent']
    for user in test_users:
        account = config.get_account_by_description(user)
        if account:
            print(f"✅ get_account_by_description('{user}') = {account['username']}")
        else:
            print(f"❌ get_account_by_description('{user}') 未找到")
    
    return True

def main():
    """主函数"""
    print("🚀 配置验证脚本")
    print("=" * 50)
    
    all_passed = True
    
    # 验证各个配置部分
    validators = [
        validate_llm_config,
        validate_accounts_config,
        validate_design_service_config,
        validate_browser_config,
        test_config_methods
    ]
    
    for validator in validators:
        try:
            if not validator():
                all_passed = False
        except Exception as e:
            print(f"❌ 验证过程中发生错误: {str(e)}")
            all_passed = False
    
    # 可选：测试网络连接
    print("\n" + "=" * 50)
    choice = input("是否测试 Rayware URLs 的网络连接？(y/n): ").strip().lower()
    if choice == 'y':
        try:
            test_rayware_urls()
        except Exception as e:
            print(f"❌ 网络测试失败: {str(e)}")
    
    # 可选：测试 Design Service URLs 的网络连接
    print("\n" + "=" * 50)
    choice = input("是否测试 Design Service URLs 的网络连接？(y/n): ").strip().lower()
    if choice == 'y':
        try:
            test_design_service_urls()
        except Exception as e:
            print(f"❌ 网络测试失败: {str(e)}")
    
    # 总结
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有配置验证通过！")
        print("框架已准备就绪，可以开始使用。")
    else:
        print("❌ 配置验证失败，请检查并修复上述问题。")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出验证")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 验证脚本执行失败: {str(e)}")
        sys.exit(1) 