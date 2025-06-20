#!/usr/bin/env python3
"""
快速迁移脚本
一键将旧导入语句迁移到新的模块结构
"""

import os
import re
import shutil
from typing import List, Dict, Tuple
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuickMigrator:
    """快速迁移器"""
    
    def __init__(self):
        self.backup_dir = "migration_backup"
        self.migration_stats = {
            "files_processed": 0,
            "files_migrated": 0,
            "imports_updated": 0,
            "errors": 0
        }
        
    def create_backup(self, file_path: str) -> str:
        """创建文件备份"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def find_files_to_migrate(self, directory: str = ".") -> List[str]:
        """查找需要迁移的文件"""
        files_to_migrate = []
        
        for root, dirs, files in os.walk(directory):
            # 跳过不需要的目录
            if any(skip in root for skip in ['venv', '__pycache__', '.git', '.pytest_cache', 'migration_backup']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        if 'from web_tools.web_toolkit import' in content:
                            files_to_migrate.append(file_path)
                            
                    except Exception as e:
                        logger.warning(f"无法读取文件 {file_path}: {e}")
        
        return files_to_migrate
    
    def migrate_file(self, file_path: str) -> bool:
        """迁移单个文件"""
        try:
            # 创建备份
            backup_path = self.create_backup(file_path)
            logger.info(f"已备份: {backup_path}")
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 执行迁移
            new_content, changes = self.migrate_content(content)
            
            if changes > 0:
                # 写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info(f"✅ 迁移成功: {file_path} ({changes} 处更改)")
                self.migration_stats["files_migrated"] += 1
                self.migration_stats["imports_updated"] += changes
                return True
            else:
                logger.info(f"ℹ️ 无需迁移: {file_path}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 迁移失败: {file_path} - {e}")
            self.migration_stats["errors"] += 1
            return False
    
    def migrate_content(self, content: str) -> Tuple[str, int]:
        """迁移文件内容"""
        changes = 0
        
        # 模式1: 简单导入迁移
        pattern1 = r'from web_tools\.web_toolkit import (.+)'
        replacement1 = r'from web_tools.web_toolkit_new import \1'
        
        new_content, count1 = re.subn(pattern1, replacement1, content)
        changes += count1
        
        # 模式2: 多行导入迁移
        pattern2 = r'from web_tools\.web_toolkit import\s*\n\s*(.+)'
        replacement2 = r'from web_tools.web_toolkit_new import \1'
        
        new_content, count2 = re.subn(pattern2, replacement2, new_content)
        changes += count2
        
        return new_content, changes
    
    def run_migration(self, directory: str = ".") -> Dict:
        """运行完整迁移"""
        logger.info("🚀 开始快速迁移...")
        
        # 查找需要迁移的文件
        files_to_migrate = self.find_files_to_migrate(directory)
        logger.info(f"发现 {len(files_to_migrate)} 个文件需要迁移")
        
        if not files_to_migrate:
            logger.info("没有找到需要迁移的文件")
            return self.migration_stats
        
        # 显示迁移计划
        print("\n迁移计划:")
        for i, file_path in enumerate(files_to_migrate, 1):
            print(f"{i}. {file_path}")
        
        # 确认迁移
        response = input("\n是否继续迁移？(y/N): ").strip().lower()
        if response != 'y':
            logger.info("迁移已取消")
            return self.migration_stats
        
        # 执行迁移
        for file_path in files_to_migrate:
            self.migration_stats["files_processed"] += 1
            self.migrate_file(file_path)
        
        # 生成迁移报告
        self.generate_migration_report()
        
        return self.migration_stats
    
    def generate_migration_report(self):
        """生成迁移报告"""
        report = []
        report.append("# 快速迁移报告")
        report.append("")
        report.append(f"- 处理文件数: {self.migration_stats['files_processed']}")
        report.append(f"- 成功迁移: {self.migration_stats['files_migrated']}")
        report.append(f"- 更新导入: {self.migration_stats['imports_updated']}")
        report.append(f"- 错误数量: {self.migration_stats['errors']}")
        report.append("")
        
        if self.migration_stats['errors'] > 0:
            report.append("## 注意事项")
            report.append("- 部分文件迁移失败，请检查备份文件")
            report.append("- 建议手动检查失败的文件")
            report.append("")
        
        report.append("## 验证步骤")
        report.append("1. 运行测试: `python test_refactored_modules.py`")
        report.append("2. 运行业务测试: `python test_create_print_job.py`")
        report.append("3. 检查功能是否正常")
        report.append("")
        
        report.append("## 回滚方法")
        report.append("如需回滚，请使用备份文件:")
        report.append(f"```bash")
        report.append(f"# 恢复单个文件")
        report.append(f"cp migration_backup/[文件名] [原文件路径]")
        report.append(f"```")
        
        # 保存报告
        with open('quick_migration_report.md', 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        logger.info("📄 迁移报告已保存到 quick_migration_report.md")
    
    def rollback_file(self, file_path: str) -> bool:
        """回滚单个文件"""
        try:
            backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
                logger.info(f"✅ 回滚成功: {file_path}")
                return True
            else:
                logger.error(f"❌ 备份文件不存在: {backup_path}")
                return False
        except Exception as e:
            logger.error(f"❌ 回滚失败: {file_path} - {e}")
            return False
    
    def rollback_all(self) -> bool:
        """回滚所有文件"""
        logger.info("🔄 开始回滚所有文件...")
        
        if not os.path.exists(self.backup_dir):
            logger.error("❌ 备份目录不存在")
            return False
        
        success_count = 0
        total_count = 0
        
        for backup_file in os.listdir(self.backup_dir):
            if backup_file.endswith('.py'):
                total_count += 1
                # 尝试找到原文件路径
                original_paths = self.find_original_file(backup_file)
                for original_path in original_paths:
                    if self.rollback_file(original_path):
                        success_count += 1
                        break
        
        logger.info(f"回滚完成: {success_count}/{total_count} 个文件")
        return success_count == total_count
    
    def find_original_file(self, backup_filename: str) -> List[str]:
        """查找原文件路径"""
        original_paths = []
        
        for root, dirs, files in os.walk("."):
            if any(skip in root for skip in ['venv', '__pycache__', '.git', '.pytest_cache', 'migration_backup']):
                continue
                
            if backup_filename in files:
                original_paths.append(os.path.join(root, backup_filename))
        
        return original_paths

def main():
    """主函数"""
    migrator = QuickMigrator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "rollback":
            # 回滚所有文件
            response = input("确定要回滚所有文件吗？这将覆盖当前更改 (y/N): ").strip().lower()
            if response == 'y':
                migrator.rollback_all()
            else:
                print("回滚已取消")
                
        elif command == "rollback-file" and len(sys.argv) > 2:
            # 回滚单个文件
            file_path = sys.argv[2]
            migrator.rollback_file(file_path)
            
        elif command == "list":
            # 列出需要迁移的文件
            files = migrator.find_files_to_migrate()
            print(f"发现 {len(files)} 个文件需要迁移:")
            for i, file_path in enumerate(files, 1):
                print(f"{i}. {file_path}")
                
        else:
            print("未知命令。可用命令: rollback, rollback-file [文件路径], list")
    else:
        # 运行迁移
        stats = migrator.run_migration()
        
        print("\n" + "="*50)
        print("迁移完成!")
        print("="*50)
        print(f"处理文件: {stats['files_processed']}")
        print(f"成功迁移: {stats['files_migrated']}")
        print(f"更新导入: {stats['imports_updated']}")
        print(f"错误数量: {stats['errors']}")
        print("="*50)
        
        if stats['errors'] == 0:
            print("🎉 迁移成功！请运行测试验证功能。")
        else:
            print("⚠️ 部分文件迁移失败，请检查日志和备份文件。")

if __name__ == "__main__":
    import sys
    main() 