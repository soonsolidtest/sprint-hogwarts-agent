#!/usr/bin/env python3
"""
测试 login_with_credentials 工具的调用方式
"""

from web_tools.login_tools import login_with_credentials

def test_login_with_credentials():
    """测试 login_with_credentials 工具的调用"""
    
    # 测试参数
    test_params = {
        "username": "wangyili@sprintray.cn",
        "password": "12345678Dev",
        "login_url": "https://dev.account.sprintray.com/"
    }
    
    print("🔍 测试 login_with_credentials 工具调用")
    print(f"📤 测试参数: {test_params}")
    
    try:
        # 方法1: 使用 .invoke() 方法，直接传递参数
        print("\n📋 方法1: 使用 .invoke() 方法，直接传递参数")
        result1 = login_with_credentials.invoke(test_params)
        print(f"✅ 结果1: {result1}")
        
    except Exception as e:
        print(f"❌ 方法1失败: {e}")
    
    try:
        # 方法2: 使用 param 包装
        print("\n📋 方法2: 使用 param 包装")
        result2 = login_with_credentials.invoke({"param": test_params})
        print(f"✅ 结果2: {result2}")
        
    except Exception as e:
        print(f"❌ 方法2失败: {e}")
    
    try:
        # 方法3: 使用 param 包装，但参数在 param 内部
        print("\n📋 方法3: 使用 param 包装，参数在 param 内部")
        result3 = login_with_credentials.invoke({
            "param": {
                "username": "wangyili@sprintray.cn",
                "password": "12345678Dev",
                "login_url": "https://dev.account.sprintray.com/"
            }
        })
        print(f"✅ 结果3: {result3}")
        
    except Exception as e:
        print(f"❌ 方法3失败: {e}")
    
    try:
        # 方法4: 直接调用函数（不使用工具装饰器）
        print("\n📋 方法4: 直接调用函数（不使用工具装饰器）")
        # 获取原始函数
        original_func = login_with_credentials.func if hasattr(login_with_credentials, 'func') else login_with_credentials
        result4 = original_func(**test_params)
        print(f"✅ 结果4: {result4}")
        
    except Exception as e:
        print(f"❌ 方法4失败: {e}")

if __name__ == "__main__":
    test_login_with_credentials() 