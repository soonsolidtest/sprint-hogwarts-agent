from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from typing import Dict, Any, List
from langchain_core.tools import tool
import logging
from .driver_management import get_driver

logger = logging.getLogger(__name__)

@tool
def get_page_structure(**kwargs) -> Dict[str, Any]:
    """获取页面结构信息"""
    max_depth = kwargs.get("max_depth", 3)
    include_text = kwargs.get("include_text", True)
    include_attributes = kwargs.get("include_attributes", True)
    
    logger.info(f"🔍 获取页面结构: max_depth={max_depth}")
    driver = get_driver()
    
    try:
        # 获取页面标题
        page_title = driver.title
        current_url = driver.current_url
        
        # 获取页面结构
        structure = _analyze_page_structure(driver, max_depth, include_text, include_attributes)
        
        # 转换为HTML格式
        html_structure = _structure_to_html(structure, 0)
        
        logger.info("✅ 页面结构获取成功")
        return {
            "status": "success",
            "message": "页面结构获取成功",
            "data": {
                "title": page_title,
                "url": current_url,
                "structure": structure,
                "html": html_structure
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 获取页面结构失败: {str(e)}")
        return {
            "status": "error",
            "message": f"获取页面结构失败: {str(e)}"
        }

def _analyze_page_structure(driver, max_depth: int, include_text: bool, include_attributes: bool, current_depth: int = 0) -> dict:
    """分析页面结构"""
    if current_depth >= max_depth:
        return {"type": "truncated", "message": f"达到最大深度 {max_depth}"}
    
    try:
        # 获取body元素
        body = driver.find_element(By.TAG_NAME, "body")
        
        structure = {
            "type": "body",
            "tag": "body",
            "children": []
        }
        
        if include_attributes:
            structure["attributes"] = _get_element_attributes(body)
        
        # 递归分析子元素
        children = body.find_elements(By.XPATH, "./*")
        for child in children[:10]:  # 限制子元素数量
            child_structure = _analyze_element_structure(
                child, max_depth, include_text, include_attributes, current_depth + 1
            )
            structure["children"].append(child_structure)
        
        return structure
        
    except Exception as e:
        return {
            "type": "error",
            "message": f"分析页面结构失败: {str(e)}"
        }

def _analyze_element_structure(element, max_depth: int, include_text: bool, include_attributes: bool, current_depth: int) -> dict:
    """分析元素结构"""
    if current_depth >= max_depth:
        return {"type": "truncated", "message": f"达到最大深度 {max_depth}"}
    
    try:
        tag_name = element.tag_name
        structure = {
            "type": "element",
            "tag": tag_name
        }
        
        if include_attributes:
            structure["attributes"] = _get_element_attributes(element)
        
        if include_text:
            text = element.text.strip()
            if text:
                structure["text"] = text[:100] + "..." if len(text) > 100 else text
        
        # 获取ID和类名
        element_id = element.get_attribute("id")
        class_name = element.get_attribute("class")
        
        if element_id:
            structure["id"] = element_id
        if class_name:
            structure["class"] = class_name
        
        # 递归分析子元素（限制数量）
        try:
            children = element.find_elements(By.XPATH, "./*")
            if children and current_depth < max_depth - 1:
                structure["children"] = []
                for child in children[:5]:  # 限制子元素数量
                    child_structure = _analyze_element_structure(
                        child, max_depth, include_text, include_attributes, current_depth + 1
                    )
                    structure["children"].append(child_structure)
        except Exception:
            pass  # 忽略子元素分析错误
        
        return structure
        
    except Exception as e:
        return {
            "type": "error",
            "message": f"分析元素结构失败: {str(e)}"
        }

def _get_element_attributes(element) -> dict:
    """获取元素属性"""
    try:
        attributes = {}
        common_attrs = ["id", "class", "name", "type", "value", "placeholder", "title", "alt", "src", "href"]
        
        for attr in common_attrs:
            value = element.get_attribute(attr)
            if value:
                attributes[attr] = value
        
        return attributes
    except Exception:
        return {}

def _structure_to_html(structure: dict, indent: int = 0) -> str:
    """将结构转换为HTML格式"""
    if not structure:
        return ""
    
    indent_str = "  " * indent
    
    if structure.get("type") == "error":
        return f"{indent_str}<!-- Error: {structure.get('message', 'Unknown error')} -->\n"
    
    if structure.get("type") == "truncated":
        return f"{indent_str}<!-- {structure.get('message', 'Truncated')} -->\n"
    
    # 构建标签
    tag = structure.get("tag", "div")
    attributes = structure.get("attributes", {})
    
    # 构建属性字符串
    attr_str = ""
    for key, value in attributes.items():
        if value:
            attr_str += f' {key}="{value}"'
    
    # 构建开始标签
    html = f"{indent_str}<{tag}{attr_str}"
    
    # 处理文本内容
    text = structure.get("text", "")
    children = structure.get("children", [])
    
    if text and not children:
        # 自闭合标签或有文本的标签
        html += f">{text}</{tag}>\n"
    elif children:
        # 有子元素的标签
        html += ">\n"
        for child in children:
            html += _structure_to_html(child, indent + 1)
        html += f"{indent_str}</{tag}>\n"
    else:
        # 自闭合标签
        html += " />\n"
    
    return html

@tool
def find_elements_by_text(text: str, **kwargs) -> Dict[str, Any]:
    """根据文本内容查找元素"""
    partial_match = kwargs.get("partial_match", True)
    case_sensitive = kwargs.get("case_sensitive", False)
    
    logger.info(f"🔍 查找包含文本的元素: {text}")
    driver = get_driver()
    
    try:
        elements = []
        
        if partial_match:
            if case_sensitive:
                xpath = f"//*[contains(text(), '{text}')]"
            else:
                xpath = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
        else:
            if case_sensitive:
                xpath = f"//*[text()='{text}']"
            else:
                xpath = f"//*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{text.lower()}']"
        
        found_elements = driver.find_elements(By.XPATH, xpath)
        
        for element in found_elements[:10]:  # 限制结果数量
            element_info = _get_element_info(element)
            elements.append(element_info)
        
        logger.info(f"✅ 找到 {len(elements)} 个元素")
        return {
            "status": "success",
            "message": f"找到 {len(elements)} 个元素",
            "data": {
                "text": text,
                "elements": elements
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 查找元素失败: {str(e)}")
        return {
            "status": "error",
            "message": f"查找元素失败: {str(e)}"
        }

@tool
def find_elements_by_selector(selector: dict, **kwargs) -> Dict[str, Any]:
    """根据选择器查找元素"""
    wait_time = kwargs.get("wait", 5)
    max_elements = kwargs.get("max_elements", 10)
    
    logger.info(f"🔍 根据选择器查找元素: {selector}")
    driver = get_driver()
    
    try:
        by = selector.get("by", "id")
        value = selector.get("value", "")
        
        if not value:
            return {
                "status": "error",
                "message": "选择器值不能为空"
            }
        
        # 转换选择器类型
        by_type = {
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "link": By.LINK_TEXT,
            "partial_link": By.PARTIAL_LINK_TEXT
        }.get(by.lower(), By.ID)
        
        # 查找元素
        elements = driver.find_elements(by_type, value)
        
        # 限制结果数量
        elements = elements[:max_elements]
        
        # 获取元素信息
        elements_info = []
        for element in elements:
            element_info = _get_element_info(element)
            elements_info.append(element_info)
        
        logger.info(f"✅ 找到 {len(elements_info)} 个元素")
        return {
            "status": "success",
            "message": f"找到 {len(elements_info)} 个元素",
            "data": {
                "selector": selector,
                "elements": elements_info
            }
        }
        
    except Exception as e:
        logger.error(f"❌ 查找元素失败: {str(e)}")
        return {
            "status": "error",
            "message": f"查找元素失败: {str(e)}"
        }

def _get_element_info(element) -> dict:
    """获取元素信息"""
    try:
        info = {
            "tag": element.tag_name,
            "text": element.text.strip()[:100] if element.text else "",
            "visible": element.is_displayed(),
            "enabled": element.is_enabled()
        }
        
        # 获取常用属性
        common_attrs = ["id", "class", "name", "type", "value", "placeholder", "title", "alt", "src", "href"]
        for attr in common_attrs:
            value = element.get_attribute(attr)
            if value:
                info[attr] = value
        
        return info
    except Exception as e:
        return {
            "error": str(e)
        }

@tool
def wait_for_element(selector: dict, **kwargs) -> Dict[str, Any]:
    """等待元素出现"""
    timeout = kwargs.get("timeout", 10)
    condition = kwargs.get("condition", "presence")  # presence, clickable, visible
    
    logger.info(f"⏳ 等待元素: {selector}, 条件: {condition}")
    driver = get_driver()
    
    try:
        by = selector.get("by", "id")
        value = selector.get("value", "")
        
        if not value:
            return {
                "status": "error",
                "message": "选择器值不能为空"
            }
        
        # 转换选择器类型
        by_type = {
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "link": By.LINK_TEXT,
            "partial_link": By.PARTIAL_LINK_TEXT
        }.get(by.lower(), By.ID)
        
        # 根据条件等待
        if condition == "clickable":
            element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by_type, value))
            )
        elif condition == "visible":
            element = WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located((by_type, value))
            )
        else:  # presence
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by_type, value))
            )
        
        # 获取元素信息
        element_info = _get_element_info(element)
        
        logger.info("✅ 元素等待成功")
        return {
            "status": "success",
            "message": "元素等待成功",
            "data": {
                "selector": selector,
                "condition": condition,
                "element": element_info
            }
        }
        
    except TimeoutException:
        logger.error(f"❌ 等待元素超时: {selector}")
        return {
            "status": "error",
            "message": f"等待元素超时: {selector}"
        }
    except Exception as e:
        logger.error(f"❌ 等待元素失败: {str(e)}")
        return {
            "status": "error",
            "message": f"等待元素失败: {str(e)}"
        } 