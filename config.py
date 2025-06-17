# config.py
import os, yaml
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import logging
from typing import Dict, Any, List

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    """统一配置管理器"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self._config = self._load_config()
        self._setup_logging()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print(f"✅ 配置文件加载成功: {self.config_file}")
            return config
        except FileNotFoundError:
            print(f"❌ 配置文件未找到: {self.config_file}")
            return {}
        except yaml.YAMLError as e:
            print(f"❌ 配置文件格式错误: {e}")
            return {}
    
    def _setup_logging(self):
        """设置日志配置"""
        log_config = self._config.get('logging', {})
        level = getattr(logging, log_config.get('level', 'INFO'))
        
        # 创建日志目录
        log_file = log_config.get('file', 'logs/agent.log')
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # 配置日志格式
        logging.basicConfig(
            level=level,
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    
    @property
    def llm(self) -> Dict[str, Any]:
        """LLM配置"""
        return self._config.get('llm', {})
    
    @property
    def system(self) -> Dict[str, Any]:
        """系统配置"""
        return self._config.get('system', {})
    
    @property
    def accounts(self) -> List[Dict[str, str]]:
        """账号配置"""
        return self._config.get('accounts', [])
    
    @property
    def browser(self) -> Dict[str, Any]:
        """浏览器配置"""
        return self._config.get('browser', {})
    
    @property
    def intent_routing(self) -> Dict[str, Any]:
        """意图路由配置"""
        return self._config.get('intent_routing', {})
    
    @property
    def system_prompt(self) -> str:
        """系统提示词"""
        return self._config.get('system_prompt', '')
    
    @property
    def tools(self) -> Dict[str, Any]:
        """工具配置"""
        return self._config.get('tools', {})
    
    @property
    def design_service(self) -> Dict[str, Any]:
        """Design Service 系统配置"""
        return self._config.get('design_service', {})
    
    @property
    def rayware(self) -> Dict[str, Any]:
        """Rayware 系统配置 (向后兼容)"""
        # 为了向后兼容，保留 rayware 属性，但指向 design_service
        return self._config.get('design_service', {})
    
    def get_design_service_url(self, page: str) -> str:
        """获取 Design Service 页面URL"""
        design_service_config = self.design_service
        urls = design_service_config.get('urls', {})
        return urls.get(page, design_service_config.get('base_url', ''))
    
    def get_rayware_url(self, page: str) -> str:
        """获取 Rayware 页面URL (向后兼容)"""
        # 为了向后兼容，保留此方法
        return self.get_design_service_url(page)
    
    def check_design_service_page(self, current_url: str) -> str:
        """检查当前页面是否为 Design Service 页面"""
        design_service_config = self.design_service
        page_indicators = design_service_config.get('page_indicators', {})
        
        for page_name, indicators in page_indicators.items():
            if any(indicator in current_url for indicator in indicators):
                return page_name
        
        return "unknown"
    
    def check_rayware_page(self, current_url: str) -> str:
        """检查当前页面是否为 Rayware 页面 (向后兼容)"""
        # 为了向后兼容，保留此方法
        return self.check_design_service_page(current_url)
    
    def get(self, key: str, default=None):
        """获取配置项"""
        return self._config.get(key, default)
    
    def get_account_by_description(self, description: str) -> Dict[str, str]:
        """根据描述获取账号配置"""
        for account in self.accounts:
            if account.get('description') == description:
                return account
        return {}

# 创建全局配置实例
config = Config()

# 向后兼容的导出
system_prompt = config.system_prompt

logger.info("🔄 开始加载系统配置")
router_prompt = config.get('router_prompt', 'prompts/router_config.yaml')
logger.info("✅ 系统配置加载完成")