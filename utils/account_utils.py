import json
import re
from typing import Dict, List, Any, Optional
from config import config

def load_accounts() -> List[Dict[str, str]]:
    """从配置文件加载账号信息"""
    return config.accounts

def find_account_by_user(user_desc: str, accounts: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
    """根据用户描述查找账号"""
    for acc in accounts:
        if isinstance(acc, dict) and acc.get("description") == user_desc:
            return acc
    return None

def parse_user_instruction(instruction: str) -> Dict[str, Any]:
    """解析用户指令，提取用户名和操作意图"""
    instruction_lower = instruction.lower()
    
    # 提取用户名的多种模式
    user_patterns = [
        r"用\s*(\w+)\s*登录",           # "用user1登录"
        r"使用\s*(\w+)\s*登录",         # "使用user1登录" 
        r"(\w+)\s*登录",              # "user1登录"
        r"用\s*(\w+)\s*打开",          # "用user1打开"
        r"请\s*用\s*(\w+)",           # "请用user1"
        r"(\w+)\s*账号",              # "user1账号"
    ]
    
    user_desc = None
    for pattern in user_patterns:
        match = re.search(pattern, instruction)
        if match:
            user_desc = match.group(1)
            break
    
    # 判断操作意图
    login_keywords = ["登录", "登入", "打开网址", "进入", "访问"]
    is_login_request = any(keyword in instruction for keyword in login_keywords)
    
    # 判断是否需要新建打印任务
    print_job_keywords = ["新建", "创建", "打印任务", "新建打印任务"]
    needs_print_job = any(keyword in instruction for keyword in print_job_keywords)
    
    return {
        "user_desc": user_desc,
        "is_login_request": is_login_request,
        "needs_print_job": needs_print_job,
        "original_instruction": instruction
    }

def parse_instruction(instruction: str, accounts: List[Dict[str, str]]) -> Dict[str, Any]:
    """解析用户指令，提取用户信息和操作意图"""
    
    # 用户登录模式匹配
    user_patterns = [
        r'用\s*(\w+)\s*登录',
        r'使用\s*(\w+)\s*登录',
        r'(\w+)\s*登录',
        r'登录\s*(\w+)',
    ]
    
    for pattern in user_patterns:
        match = re.search(pattern, instruction, re.IGNORECASE)
        if match:
            user_desc = match.group(1)
            # 查找对应的账号配置
            for account in accounts:
                if account.get('description') == user_desc:
                    return {
                        'action': 'login',
                        'user': user_desc,
                        'url': account.get('url'),
                        'username': account.get('username'),
                        'password': account.get('password')
                    }
    
    # 其他操作模式
    if any(keyword in instruction for keyword in ['新建', '打印任务', '创建']):
        return {
            'action': 'create_print_job',
            'user': None
        }
    
    if any(keyword in instruction for keyword in ['历史', '查看', '最近']):
        return {
            'action': 'view_history',
            'user': None
        }
    
    return {
        'action': 'unknown',
        'user': None
    } 