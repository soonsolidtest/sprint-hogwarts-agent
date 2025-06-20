#!/usr/bin/env python3
"""
Web Toolkit 迁移助手
帮助用户快速验证和迁移到新的模块化结构
"""

import sys
import os
import logging
import importlib
from typing import Dict, List, Any

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MigrationHelper:
    """迁移助手类"""
    
    def __init__(self):
        self.old_imports = []
        self.new_imports = []
        self.test_results = {}
        
    def scan_old_imports(self, directory: str = ".") -> List[str]:
        """扫描目录中的旧导入语句"""
        logger.info(f"🔍 扫描目录: {directory}")
        
        old_imports = []
        for root, dirs, files in os.walk(directory):
            # 跳过虚拟环境和缓存目录
            if any(skip in root for skip in ['venv', '__pycache__', '.git', '.pytest_cache']):
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # 查找旧的导入语句
                        if 'from web_tools.web_toolkit import' in content:
                            old_imports.append(file_path)
                            logger.info(f"发现旧导入: {file_path}")
                            
                    except Exception as e:
                        logger.warning(f"无法读取文件 {file_path}: {e}")
        
        self.old_imports = old_imports
        return old_imports
    
    def generate_migration_suggestions(self) -> Dict[str, List[str]]:
        """生成迁移建议"""
        suggestions = {}
        
        for file_path in self.old_imports:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 分析导入的模块
                imports = self._analyze_imports(content)
                suggestions[file_path] = self._generate_suggestions(imports)
                
            except Exception as e:
                logger.error(f"分析文件 {file_path} 失败: {e}")
        
        return suggestions
    
    def _analyze_imports(self, content: str) -> List[str]:
        """分析导入的模块"""
        imports = []
        
        # 查找 from web_tools.web_toolkit import 语句
        import_lines = [line.strip() for line in content.split('\n') 
                       if 'from web_tools.web_toolkit import' in line]
        
        for line in import_lines:
            # 提取导入的模块名
            if 'import' in line:
                parts = line.split('import')
                if len(parts) > 1:
                    module_names = parts[1].strip().split(',')
                    for name in module_names:
                        name = name.strip()
                        if name:
                            imports.append(name)
        
        return imports
    
    def _generate_suggestions(self, imports: List[str]) -> List[str]:
        """生成迁移建议"""
        suggestions = []
        
        # 模块映射
        module_mapping = {
            'selenium_get': 'basic_operations',
            'selenium_sendkeys': 'basic_operations',
            'selenium_click': 'basic_operations',
            'selenium_wait_for_element': 'basic_operations',
            'selenium_quit': 'basic_operations',
            'smart_click': 'smart_operations',
            'smart_select_open': 'smart_operations',
            'smart_select_and_choose': 'smart_operations',
            'login_with_credentials': 'login_tools',
            'auto_login': 'login_tools',
            'create_new_print_job': 'print_job_tools',
            'select_printer': 'print_job_tools',
            'submit_print_job': 'print_job_tools',
            'get_page_structure': 'page_analysis',
            'find_elements_by_text': 'page_analysis',
            'find_elements_by_selector': 'page_analysis',
            'wait_for_element': 'page_analysis',
            'get_driver': 'driver_management',
            'close_driver': 'driver_management',
            'get_current_driver': 'driver_management'
        }
        
        # 按模块分组
        module_groups = {}
        for imp in imports:
            if imp in module_mapping:
                module = module_mapping[imp]
                if module not in module_groups:
                    module_groups[module] = []
                module_groups[module].append(imp)
        
        # 生成建议
        if module_groups:
            suggestions.append("# 方式1: 使用新的整合模块（推荐）")
            suggestions.append("from web_tools.web_toolkit_new import " + ", ".join(imports))
            suggestions.append("")
            
            suggestions.append("# 方式2: 按模块导入")
            for module, module_imports in module_groups.items():
                suggestions.append(f"from web_tools.{module} import {', '.join(module_imports)}")
            suggestions.append("")
            
            suggestions.append("# 方式3: 包级别导入")
            suggestions.append("from web_tools import " + ", ".join(imports))
        
        return suggestions
    
    def test_migration(self) -> Dict[str, bool]:
        """测试迁移是否成功"""
        logger.info("🧪 测试迁移...")
        
        test_results = {}
        
        # 测试各个模块的导入
        modules_to_test = [
            ('web_tools.driver_management', ['get_driver', 'close_driver']),
            ('web_tools.basic_operations', ['selenium_get', 'selenium_quit']),
            ('web_tools.smart_operations', ['smart_click']),
            ('web_tools.login_tools', ['auto_login']),
            ('web_tools.print_job_tools', ['create_new_print_job']),
            ('web_tools.page_analysis', ['get_page_structure']),
            ('web_tools.web_toolkit_new', ['selenium_get', 'smart_click']),
        ]
        
        for module_name, functions in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                success = True
                
                # 测试函数是否存在
                for func_name in functions:
                    if not hasattr(module, func_name):
                        success = False
                        break
                
                test_results[module_name] = success
                logger.info(f"{'✅' if success else '❌'} {module_name}")
                
            except Exception as e:
                test_results[module_name] = False
                logger.error(f"❌ {module_name}: {e}")
        
        self.test_results = test_results
        return test_results
    
    def generate_migration_report(self) -> str:
        """生成迁移报告"""
        report = []
        report.append("# Web Toolkit 迁移报告")
        report.append("")
        
        # 扫描结果
        report.append("## 扫描结果")
        report.append(f"- 发现 {len(self.old_imports)} 个文件包含旧导入")
        if self.old_imports:
            report.append("- 需要迁移的文件:")
            for file_path in self.old_imports:
                report.append(f"  - {file_path}")
        report.append("")
        
        # 测试结果
        report.append("## 测试结果")
        all_passed = all(self.test_results.values())
        report.append(f"- 整体状态: {'✅ 通过' if all_passed else '❌ 失败'}")
        report.append("- 模块测试:")
        for module, success in self.test_results.items():
            status = "✅ 通过" if success else "❌ 失败"
            report.append(f"  - {module}: {status}")
        report.append("")
        
        # 迁移建议
        if self.old_imports:
            report.append("## 迁移建议")
            suggestions = self.generate_migration_suggestions()
            for file_path, file_suggestions in suggestions.items():
                report.append(f"### {file_path}")
                for suggestion in file_suggestions:
                    report.append(suggestion)
                report.append("")
        
        return "\n".join(report)
    
    def run_full_migration_check(self) -> bool:
        """运行完整的迁移检查"""
        logger.info("🚀 开始完整的迁移检查...")
        
        # 1. 扫描旧导入
        self.scan_old_imports()
        
        # 2. 测试新模块
        test_results = self.test_migration()
        
        # 3. 生成报告
        report = self.generate_migration_report()
        
        # 4. 保存报告
        with open('migration_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info("📄 迁移报告已保存到 migration_report.md")
        
        # 5. 打印摘要
        print("\n" + "="*50)
        print("迁移检查摘要")
        print("="*50)
        print(f"发现需要迁移的文件: {len(self.old_imports)}")
        print(f"模块测试通过: {sum(test_results.values())}/{len(test_results)}")
        print(f"整体状态: {'✅ 可以迁移' if all(test_results.values()) else '❌ 需要修复'}")
        print("="*50)
        
        return all(test_results.values())

def main():
    """主函数"""
    helper = MigrationHelper()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "scan":
            # 只扫描
            old_imports = helper.scan_old_imports()
            print(f"发现 {len(old_imports)} 个文件包含旧导入")
            
        elif command == "test":
            # 只测试
            test_results = helper.test_migration()
            print("测试结果:", test_results)
            
        elif command == "suggest":
            # 生成建议
            helper.scan_old_imports()
            suggestions = helper.generate_migration_suggestions()
            for file_path, file_suggestions in suggestions.items():
                print(f"\n{file_path}:")
                for suggestion in file_suggestions:
                    print(suggestion)
                    
        else:
            print("未知命令。可用命令: scan, test, suggest, full")
    else:
        # 运行完整检查
        success = helper.run_full_migration_check()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 