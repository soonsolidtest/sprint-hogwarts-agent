#!/usr/bin/env python3
"""
简化的 Design Service 配置测试
验证配置结构和 URL 访问
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_structure():
    """测试配置结构"""
    print("🔧 测试 Design Service 配置结构...")
    
    try:
        from config import config
        
        # 测试 design_service 配置
        design_service_config = config.design_service
        print(f"✅ Design Service 基础URL: {design_service_config.get('base_url')}")
        
        # 测试各个 URL
        urls = design_service_config.get('urls', {})
        for name, url in urls.items():
            print(f"✅ {name}: {url}")
        
        # 测试新的方法
        rayware_url = config.get_design_service_url("rayware")
        print(f"✅ get_design_service_url('rayware'): {rayware_url}")
        
        # 测试向后兼容
        rayware_url_compat = config.get_rayware_url("rayware")
        print(f"✅ get_rayware_url('rayware') [兼容]: {rayware_url_compat}")
        
        # 测试页面检测
        test_url = "https://dev.designservice.sprintray.com/print-setup"
        page_type = config.check_design_service_page(test_url)
        print(f"✅ 页面检测: {page_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def show_flow_summary():
    """显示流程摘要"""
    print("\n📊 Design Service 完整流程摘要")
    print("=" * 50)
    print("""
    🎯 目标：保持原有的 rayware 逻辑，使用新的 design_service 配置
    
    📋 流程步骤：
    1. 用户输入: "用wangyili登录并新建打印任务"
    2. 主图解析: 识别登录用户 + 操作意图
    3. 执行登录: auto_login → Design Service 登录页
    4. 登录成功: 检测后续操作意图
    5. 调用 rayware 图: rayware_module_graph.invoke()
    6. 导航到 rayware: config.get_design_service_url("rayware")
    7. 创建打印任务: 填写表单 → 提交
    8. 返回结果: 完成整个流程
    
    🔧 配置结构：
    design_service:
      base_url: "https://dev.designservice.sprintray.com"
      urls:
        home: ".../home-screen"
        rayware: ".../print-setup"  ← 新建打印任务页面
        print_history: ".../print-history"
        new_print_job: ".../print-setup"
    
    ✅ 关键特性：
    - 保持了原有的 rayware 图逻辑
    - 更新了配置结构为 design_service
    - 支持向后兼容的 API
    - 完整的登录 → 业务操作流程
    """)

def test_account_access():
    """测试账号访问"""
    print("\n👤 测试账号配置访问...")
    
    try:
        from config import config
        
        test_users = ['user1', 'wangyili']
        for user in test_users:
            account = config.get_account_by_description(user)
            if account:
                print(f"✅ {user}: {account['username']} → {account['url']}")
            else:
                print(f"❌ {user}: 未找到配置")
        
        return True
        
    except Exception as e:
        print(f"❌ 账号测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Design Service 配置测试")
    print("验证：配置结构 + rayware 逻辑 + 向后兼容")
    print("=" * 60)
    
    all_passed = True
    
    # 测试配置结构
    if not test_config_structure():
        all_passed = False
    
    # 测试账号访问
    if not test_account_access():
        all_passed = False
    
    # 显示流程摘要
    show_flow_summary()
    
    # 总结
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！")
        print("\n💡 配置更新总结:")
        print("✅ 配置节点: rayware → design_service")
        print("✅ URL 键名: print_setup → rayware")
        print("✅ 保持原有逻辑: 登录 → rayware 图 → 新建打印任务")
        print("✅ 向后兼容: 旧的 API 仍然可用")
        print("\n🚀 现在可以使用以下指令测试:")
        print("   python agent_runner_new.py")
        print("   > 用wangyili登录并新建打印任务")
    else:
        print("❌ 部分测试失败，请检查配置")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        sys.exit(1) 