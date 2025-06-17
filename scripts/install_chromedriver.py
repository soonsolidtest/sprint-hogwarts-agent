#!/usr/bin/env python3
"""
ChromeDriver 安装脚本
自动检测 Chrome 版本并下载对应的 ChromeDriver
"""

import os
import sys
import platform
import subprocess
import requests
import zipfile
import json
from pathlib import Path

def get_chrome_version():
    """获取 Chrome 浏览器版本"""
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            result = subprocess.run([
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", 
                "--version"
            ], capture_output=True, text=True)
            version = result.stdout.strip().split()[-1]
            
        elif system == "Linux":
            result = subprocess.run([
                "google-chrome", "--version"
            ], capture_output=True, text=True)
            version = result.stdout.strip().split()[-1]
            
        elif system == "Windows":
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            winreg.CloseKey(key)
            
        else:
            raise Exception(f"不支持的操作系统: {system}")
            
        print(f"✅ 检测到 Chrome 版本: {version}")
        return version
        
    except Exception as e:
        print(f"❌ 无法检测 Chrome 版本: {e}")
        return None

def get_chromedriver_download_url(chrome_version):
    """获取 ChromeDriver 下载链接"""
    try:
        # 获取主版本号
        major_version = chrome_version.split('.')[0]
        
        # 获取可用版本列表
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/latest-patch-versions-per-build.json"
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        builds = data.get("builds", {})
        
        # 查找匹配的版本
        matching_version = None
        for version in builds.keys():
            if version.startswith(major_version + "."):
                matching_version = version
                break
        
        if not matching_version:
            raise Exception(f"未找到 Chrome {major_version} 对应的 ChromeDriver")
        
        # 获取下载链接
        system = platform.system()
        if system == "Darwin":
            platform_key = "mac-x64"
        elif system == "Linux":
            platform_key = "linux64"
        elif system == "Windows":
            platform_key = "win64"
        else:
            raise Exception(f"不支持的平台: {system}")
        
        downloads = builds[matching_version]["downloads"]["chromedriver"]
        for download in downloads:
            if download["platform"] == platform_key:
                print(f"✅ 找到匹配版本: {matching_version}")
                return download["url"], matching_version
        
        raise Exception(f"未找到 {platform_key} 平台的下载链接")
        
    except Exception as e:
        print(f"❌ 获取下载链接失败: {e}")
        return None, None

def download_chromedriver(url, version):
    """下载 ChromeDriver"""
    try:
        print(f"🔄 开始下载 ChromeDriver {version}...")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # 保存到临时文件
        temp_file = f"chromedriver_{version}.zip"
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ 下载完成: {temp_file}")
        return temp_file
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None

def extract_chromedriver(zip_file):
    """解压 ChromeDriver"""
    try:
        print("🔄 解压文件...")
        
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # 查找 chromedriver 可执行文件
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith('chromedriver') or file_info.filename.endswith('chromedriver.exe'):
                    # 解压到 drivers 目录
                    drivers_dir = Path("drivers")
                    drivers_dir.mkdir(exist_ok=True)
                    
                    # 提取文件名
                    filename = Path(file_info.filename).name
                    target_path = drivers_dir / filename
                    
                    # 解压文件
                    with zip_ref.open(file_info) as source, open(target_path, 'wb') as target:
                        target.write(source.read())
                    
                    # 设置执行权限 (Unix系统)
                    if not filename.endswith('.exe'):
                        os.chmod(target_path, 0o755)
                    
                    print(f"✅ ChromeDriver 安装完成: {target_path}")
                    return str(target_path)
        
        raise Exception("在压缩包中未找到 chromedriver 文件")
        
    except Exception as e:
        print(f"❌ 解压失败: {e}")
        return None
    finally:
        # 清理临时文件
        if os.path.exists(zip_file):
            os.remove(zip_file)

def main():
    """主函数"""
    print("🚀 ChromeDriver 自动安装脚本")
    print("=" * 40)
    
    # 检查 Chrome 版本
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("💡 请确保已安装 Google Chrome 浏览器")
        return False
    
    # 获取下载链接
    download_url, driver_version = get_chromedriver_download_url(chrome_version)
    if not download_url:
        print("💡 请手动下载 ChromeDriver:")
        print("   1. 访问 https://googlechromelabs.github.io/chrome-for-testing/")
        print("   2. 下载对应版本的 ChromeDriver")
        print("   3. 解压后放到 drivers 目录")
        return False
    
    # 下载 ChromeDriver
    zip_file = download_chromedriver(download_url, driver_version)
    if not zip_file:
        return False
    
    # 解压安装
    chromedriver_path = extract_chromedriver(zip_file)
    if not chromedriver_path:
        return False
    
    print("\n🎉 安装成功!")
    print(f"ChromeDriver 路径: {chromedriver_path}")
    print("现在可以运行你的自动化脚本了。")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 