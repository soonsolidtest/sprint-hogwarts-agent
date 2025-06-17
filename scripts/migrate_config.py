#!/usr/bin/env python3
"""
配置迁移脚本
将旧的 rayware 配置迁移到新的 design_service 配置
"""

import sys
import os
import yaml
import shutil
from datetime import datetime

def backup_config(config_file: str) -> str:
    """备份原配置文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{config_file}.backup_{timestamp}"
    
    try:
        shutil.copy2(config_file, backup_file)
        print(f"✅ 配置文件已备份到: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None

def load_config(config_file: str) -> dict:
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"❌ 加载配置文件失败: {e}")
        return None

def save_config(config: dict, config_file: str) -> bool:
    """保存配置文件"""
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
        print(f"✅ 配置文件已保存: {config_file}")
        return True
    except Exception as e:
        print(f"❌ 保存配置文件失败: {e}")
        return False

def migrate_rayware_to_design_service(config: dict) -> dict:
    """将 rayware 配置迁移到 design_service"""
    
    if 'rayware' in config and 'design_service' not in config:
        print("🔄 检测到旧的 rayware 配置，开始迁移...")
        
        # 复制 rayware 配置到 design_service
        rayware_config = config['rayware']
        design_service_config = rayware_config.copy()
        
        # 更新 URLs 映射
        if 'urls' in design_service_config:
            urls = design_service_config['urls']
            
            # 如果有 print_setup，重命名为 rayware
            if 'print_setup' in urls:
                urls['rayware'] = urls['print_setup']
                del urls['print_setup']
                print("  - 将 print_setup URL 重命名为 rayware")
            
            # 确保必要的 URL 存在
            required_urls = ['home', 'rayware', 'print_history', 'new_print_job']
            base_url = design_service_config.get('base_url', 'https://dev.designservice.sprintray.com')
            
            for url_key in required_urls:
                if url_key not in urls:
                    if url_key == 'home':
                        urls[url_key] = f"{base_url}/home-screen"
                    elif url_key == 'rayware':
                        urls[url_key] = f"{base_url}/print-setup"
                    elif url_key == 'print_history':
                        urls[url_key] = f"{base_url}/print-history"
                    elif url_key == 'new_print_job':
                        urls[url_key] = f"{base_url}/print-setup"
                    print(f"  - 添加缺失的 URL: {url_key}")
        
        # 添加新的配置
        config['design_service'] = design_service_config
        
        # 保留旧配置以便向后兼容（可选）
        # del config['rayware']  # 如果要完全删除旧配置，取消注释这行
        
        print("✅ rayware 配置已迁移到 design_service")
        return config
    
    elif 'design_service' in config:
        print("✅ 已使用新的 design_service 配置，无需迁移")
        return config
    
    else:
        print("⚠️ 未找到 rayware 或 design_service 配置")
        return config

def validate_migrated_config(config: dict) -> bool:
    """验证迁移后的配置"""
    print("\n🔍 验证迁移后的配置...")
    
    if 'design_service' not in config:
        print("❌ 缺少 design_service 配置")
        return False
    
    design_service = config['design_service']
    
    # 检查必要字段
    required_fields = ['base_url', 'urls']
    for field in required_fields:
        if field not in design_service:
            print(f"❌ design_service 缺少字段: {field}")
            return False
    
    # 检查必要的 URLs
    required_urls = ['home', 'rayware', 'print_history', 'new_print_job']
    urls = design_service.get('urls', {})
    
    for url_key in required_urls:
        if url_key not in urls:
            print(f"❌ 缺少 URL: {url_key}")
            return False
    
    print("✅ 配置验证通过")
    return True

def show_config_diff(old_config: dict, new_config: dict):
    """显示配置变更"""
    print("\n📋 配置变更摘要:")
    print("=" * 50)
    
    if 'rayware' in old_config and 'design_service' in new_config:
        print("🔄 主要变更:")
        print("  - 配置节点从 'rayware' 更改为 'design_service'")
        
        old_urls = old_config.get('rayware', {}).get('urls', {})
        new_urls = new_config.get('design_service', {}).get('urls', {})
        
        if 'print_setup' in old_urls and 'rayware' in new_urls:
            print("  - URL 键名从 'print_setup' 更改为 'rayware'")
        
        # 显示新增的 URLs
        for key, url in new_urls.items():
            if key not in old_urls:
                print(f"  + 新增 URL: {key} = {url}")
    
    print("\n📝 新的 design_service 配置:")
    if 'design_service' in new_config:
        design_service = new_config['design_service']
        print(f"  base_url: {design_service.get('base_url')}")
        print("  urls:")
        for key, url in design_service.get('urls', {}).items():
            print(f"    {key}: {url}")

def main():
    """主函数"""
    print("🚀 配置迁移脚本")
    print("将 rayware 配置迁移到 design_service 配置")
    print("=" * 50)
    
    config_file = "config.yaml"
    
    # 检查配置文件是否存在
    if not os.path.exists(config_file):
        print(f"❌ 配置文件不存在: {config_file}")
        return False
    
    # 加载原配置
    print(f"📖 加载配置文件: {config_file}")
    original_config = load_config(config_file)
    if not original_config:
        return False
    
    # 备份原配置
    backup_file = backup_config(config_file)
    if not backup_file:
        print("❌ 无法备份配置文件，迁移中止")
        return False
    
    # 执行迁移
    migrated_config = migrate_rayware_to_design_service(original_config.copy())
    
    # 验证迁移结果
    if not validate_migrated_config(migrated_config):
        print("❌ 迁移后的配置验证失败")
        return False
    
    # 显示变更
    show_config_diff(original_config, migrated_config)
    
    # 确认保存
    print("\n" + "=" * 50)
    choice = input("是否保存迁移后的配置？(y/n): ").strip().lower()
    
    if choice == 'y':
        if save_config(migrated_config, config_file):
            print("\n🎉 配置迁移完成！")
            print(f"📁 原配置已备份到: {backup_file}")
            print("💡 建议运行 'python scripts/validate_config.py' 验证新配置")
            return True
        else:
            print("❌ 保存配置失败")
            return False
    else:
        print("❌ 用户取消保存，配置未更改")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出迁移")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 迁移脚本执行失败: {str(e)}")
        sys.exit(1) 