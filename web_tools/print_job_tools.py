from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from time import sleep
from typing import Dict, Any
from langchain_core.tools import tool
import logging
from .driver_management import get_driver
from .smart_operations import smart_click, smart_select_and_choose
from pydantic import BaseModel, Field
from enum import Enum
from .basic_operations import _ensure_element_visible,_display_find_element

logger = logging.getLogger(__name__)

class Orientation(str, Enum):
    """打印方向枚举"""
    LANDSCAPE = "Landscape"
    PORTRAIT = "Portrait"

class SupportRaft(str, Enum):
    """支撑筏设置枚举"""
    ENABLED = "enabled"
    DISABLED = "disabled"

class PrintJobConfig(BaseModel):
    """打印任务配置"""
    indication: str = Field(default="", description="打印指示/类型")
    orientation: Orientation = Field(default=Orientation.LANDSCAPE, description="打印方向")
    support_raft: SupportRaft = Field(default=SupportRaft.DISABLED, description="支撑筏设置")
    printer: str = Field(default="", description="打印机名称")
    build_platform: str = Field(default="", description="构建平台")
    material: str = Field(default="", description="材料类型")
    layer_height: float = Field(default=0.1, description="层高")
    infill_density: int = Field(default=20, description="填充密度")
    print_speed: int = Field(default=60, description="打印速度")
    temperature: int = Field(default=200, description="打印温度")
    file_path: str = Field(default="", description="文件路径")

@tool
def create_new_print_job(param: dict) -> dict:
    """创建新的打印任务"""
    logger.info("[PrintJob] 创建新打印任务节点开始")
    logger.info(f"[create_new_print_job] 调用参数: {param}")
    driver = get_driver()
    
    try:
        # 1. 点击 New Print Job 按钮
        new_job_result = smart_click.invoke({
            "param": {
                "selectors": [
                    {
                        "by": "xpath",
                        "value": "//button[contains(@class, 'btn-primary')]//div[contains(@class, 'btn-text') and contains(text(), 'New Print Job')]"
                    }
                ],
                "wait": 10
            }
        })
        
        if new_job_result.get("status") != "success":
            raise Exception(f"点击 New Print Job 按钮失败: {new_job_result.get('message')}")
        logger.info("[create_new_print_job] ✅ 成功点击 New Print Job 按钮")


        # 2. 选择 Indication
        sleep(3)
        indication = param.get("indication", "")
        if indication:
            indication_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": f"//print-job-type//div[text()='{indication}']/ancestor::div[1]"
                        }
                    ],
                    "wait": 5
                }
            })
            if indication_result.get("status") != "success":
                raise Exception(f"选择 Indication 失败: {indication_result.get('message')}")
            sleep(2)
            # 验证是否选择成功
            try:
                selected_indication = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, f"//span[contains(@class, 'appliance-name') and text()='{indication}']"))
                )
                if not selected_indication.is_displayed():
                    raise Exception("Indication 选择后未显示")
                logger.info(f"[create_new_print_job] ✅ 成功选择 Indication: {indication}")
            except Exception as e:
                # 重新点一遍
                smart_click.invoke({
                    "param": {
                        "selectors": [
                            {
                                "by": "xpath",
                                "value": f"//div[contains(@class, 'appliance-name') and text()='Select Indication']"
                            }
                        ],
                        "wait": 5
                    }
                })
                logger.info(f"[create_new_print_job] Indication: 选择验证失败，重新点击了一遍")
                raise Exception(f"Indication 选择验证失败: {str(e)}")


        # 3. 选择 Orientation
        sleep(3)
        orientation = param.get("orientation", "")
        if orientation:
            orientation_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": f"//span[contains(.,'{orientation}')]"
                        }
                    ],
                    "wait": 5
                }
            })
            sleep(2)
            if orientation_result.get("status") != "success":
                raise Exception(f"选择 Orientation 失败: {orientation_result.get('message')}")

            # 验证是否选择成功
            try:
                selected_orientation = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, 'info-container')]//span[contains(text(), '{orientation}')]"))
                )
                if not selected_orientation.is_displayed():
                    raise Exception("Orientation 选择后未显示")
                logger.info(f"[create_new_print_job] ✅ 成功选择 Orientation: {orientation}")
            except Exception as e:
                logger.info("Orientation 选择验证失败")
                raise Exception(f"Orientation 选择验证失败: {str(e)}")

        # 4. 选择 Printer
        printer = param.get("printer", "")
        if printer:
            try:
                if _ensure_element_visible(driver, "//printer-platform-list-v2//div[@class='position-relative']"):
                    logger.info("滑动到printer成功")
            except Exception as e:
                logger.warning(f"无法找到打印机下拉框: {e}")

            printer_result = select_printer.invoke({
                "param": {
                    "printer": "PRO2",
                    "printer_type": "virtual",
                    "match_by":"name"
                }
            })
            logger.info(f"printer_result,{printer_result}")
            if printer_result.get("status") != "success":
                raise Exception(f"选择 Printer 失败: {printer_result.get('message')}")

        sleep(3)
        # 5. 选择 Build Platform
        if printer != "MIDAS":
            build_platform = param.get("build_platform", "")
            if build_platform:
                platform_result = smart_click.invoke({
                    "param": {
                        "selectors": [
                            {
                                "by": "xpath",
                                "value": f"//span[contains(.,'{build_platform}')]"
                            },
                        ],
                        "wait": 5
                    }
                })
                if platform_result.get("status") != "success":
                    raise Exception(f"选择 Build Platform 失败: {platform_result.get('message')}")

                # 验证是否选择成功
                try:
                    selected_platform = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located(
                            (By.XPATH, f"//span[contains(.,'{build_platform}')]"))
                    )
                    if not selected_platform.is_displayed():
                        raise Exception("Build Platform 选择后未显示")
                    print(f"[create_new_print_job] ✅ 成功选择 Build Platform: {build_platform}")
                except Exception as e:
                    raise Exception(f"Build Platform 选择验证失败: {str(e)}")

        # 6. 选择 Material
        material = param.get("material", "")
        if material:
            material_result = select_material(material)
            if material_result.get("status") != "success":
                raise Exception(f"选择 Material 失败: {material_result.get('message')}")

            # 验证是否选择成功
            try:
                selected_material = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located(
                        (By.XPATH, f"//div[contains(@class, 'type-name') and text()='{material}']"))
                )
                if not selected_material.is_displayed():
                    raise Exception("Material 选择后未显示")
                print(f"[create_new_print_job] ✅ 成功选择 Material: {material}")
            except Exception as e:
                raise Exception(f"Material 选择验证失败: {str(e)}")

        # 7 是否点击show_advanced
        indication = param.get("indication", "")


        # 6. 设置 Support Raft
        support_raft = param.get("support_raft", False)
        if support_raft:
            raft_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": "//div[contains(@class, 'support-raft-toggle')]//input[@type='checkbox']"
                        }
                    ],
                    "wait": 5
                }
            })
            if raft_result.get("status") != "success":
                raise Exception(f"设置 Support Raft 失败: {raft_result.get('message')}")
            
            # 验证是否设置成功
            try:
                raft_checkbox = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'support-raft-toggle')]//input[@type='checkbox']"))
                )
                if not raft_checkbox.is_selected():
                    raise Exception("Support Raft 设置后未选中")
                print("[create_new_print_job] ✅ 成功设置 Support Raft")
            except Exception as e:
                raise Exception(f"Support Raft 设置验证失败: {str(e)}")



        # 8. 高级设置
        advanced_settings = param.get("advanced_settings", {})
        if advanced_settings:
            # 点击高级设置按钮
            advanced_result = smart_click.invoke({
                "param": {
                    "selectors": [
                        {
                            "by": "xpath",
                            "value": "//button[contains(text(), 'Advanced')]"
                        },
                        {
                            "by": "xpath",
                            "value": "//button[contains(text(), '高级')]"
                        }
                    ],
                    "wait": 5
                }
            })
            
            if advanced_result.get("status") == "success":
                # 设置层高
                layer_height = advanced_settings.get("layer_height")
                if layer_height:
                    _set_layer_height(driver, layer_height)
                
                # 设置填充密度
                infill_density = advanced_settings.get("infill_density")
                if infill_density:
                    _set_infill_density(driver, infill_density)
                
                # 设置打印速度
                print_speed = advanced_settings.get("print_speed")
                if print_speed:
                    _set_print_speed(driver, print_speed)
                
                # 设置温度
                temperature = advanced_settings.get("temperature")
                if temperature:
                    _set_temperature(driver, temperature)

        # 10. 上传文件
        file_path = param.get("file_path", "")
        if file_path:
            upload_result = upload_local_file(file_path)
            if upload_result.get("status") != "success":
                raise Exception(f"文件上传失败: {upload_result.get('message')}")
            print(f"[create_new_print_job] ✅ 成功上传文件: {file_path}")

        print("[create_new_print_job] ✅ 打印任务创建完成")
        logger.info("[PrintJob] 创建新打印任务节点结束")
        return {
            "status": "success",
            "message": "打印任务创建完成",
            "config": param
        }
        
    except Exception as e:
        logger.error(f"❌ 创建打印任务失败: {str(e)}")
        return {
            "status": "error",
            "message": f"创建打印任务失败: {str(e)}"
        }

@tool
def select_printer(param: Dict[str, Any]) -> Dict[str, Any]:
    """选择打印机"""
    printer = param.get("printer", "").strip()
    printer_type = param.get("printer_type", "connected")
    match_by = param.get("match_by", "name")
    index = param.get("index", 0)
    wait_time = param.get("wait", 10)
    driver = get_driver()

    if not printer:
        return {"status": "error","message": "缺少 printer 参数"}

    logger.info(f"[select_printer] 参数: {param}")

    def select_compatible_virtual_printer(driver, printer_keyword: str, match_by: str = "name") -> dict:
        try:
            sleep(10)
            # 1. 找到 Compatible Virtual Printers 的 <span>
            compatible_span = driver.find_element(
                "xpath", "//span[contains(@class, 'virtual-printer-text') and contains(text(), 'Compatible Virtual Printers')]"
            )
            # 2. 找到该 <span> 后面的所有 mat-option
            mat_options = compatible_span.find_elements(
                "xpath", "following-sibling::mat-option"
            )
            logger.info(f"mat_options,{mat_options}")
            if not mat_options:
                # 兼容：有时 mat-option 不是直接 sibling，而是同级下的所有 mat-option
                parent = compatible_span.find_element("xpath", "..")
                mat_options = parent.find_elements("xpath", ".//mat-option")
            # 3. 遍历 option，优先用文本匹配
            for option in mat_options:
                # 先用option.text匹配
                if printer_keyword.lower() in option.text.lower():
                    option.click()
                    logger.info(f"已选择虚拟打印机: {printer_keyword}")
                    return {"status": "success", "message": f"已选择虚拟打印机: {printer_keyword}"}
                # 再用图片src匹配
                try:
                    container = option.find_element("class name", "virtual-printer-container")
                    imgs = container.find_elements("tag name", "img")
                    for img in imgs:
                        src = img.get_attribute("src") or ""
                        if printer_keyword in src:
                            option.click()
                            return {"status": "success", "message": f"已选择虚拟打印机: {printer_keyword}"}
                except Exception as e:
                    logger.warning(f"[select_compatible_virtual_printer] 匹配图片src异常: {e}")
            return {"status": "error", "message": f"未找到匹配的虚拟打印机: {printer_keyword}"}
        except Exception as e:
            return {"status": "error", "message": f"异常: {e}"}

    try:
        # 1. 打开下拉框
        dropdown = driver.find_element("xpath", "//printer-platform-list-v2//div[@class='position-relative']")
        dropdown.click()
        sleep(1)

        if printer_type == "virtual":
            # 只在 Compatible Virtual Printers 下查找
            return select_compatible_virtual_printer(driver, printer, match_by)
        else:
            # 保留原有物理打印机查找逻辑
            base_xpath = "//mat-option//div[contains(@class, 'printer-container')]"
            def find_matched_elements():
                all_elements = driver.find_elements("xpath", base_xpath)
                matched_elements = []
                for el in all_elements:
                    try:
                        if match_by == "name":
                            name_div = el.find_element("class name", "printer-name")
                            logger.info(name_div)
                            if printer in name_div.text.strip():
                                matched_elements.append(el)
                        elif match_by == "serial":
                            serial_div = el.find_element("class name", "printer-id")
                            if printer in serial_div.text.strip():
                                matched_elements.append(el)
                    except Exception as e:
                        logger.warning(f"[select_printer] 单个元素匹配失败: {e}")
                return matched_elements

            matched_elements = find_matched_elements()
            if not matched_elements:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dropdown)
                sleep(1)
                matched_elements = find_matched_elements()
                if not matched_elements:
                    return {"status": "error", "message": f"未找到匹配打印机: {printer}"}

            if index >= len(matched_elements):
                return {"status": "error", "message": f"匹配到 {len(matched_elements)} 项，但 index={index} 越界"}

            target_el = matched_elements[index]
            driver.execute_script("arguments[0].scrollIntoView(true);", target_el)
            sleep(0.5)
            target_el.click()

            return {"status": "success", "message": f"成功选择打印机: {printer}"}

    except Exception as e:
        logger.error(f"[select_printer] 异常: {e}")
        return {"status": "error", "message": str(e)}


@tool
def select_material(text: str):
    """
    选择材料
    """
    ele = None
    driver = get_driver()
    # 打开下拉框
    dropdown = driver.find_element("xpath", "//f-autocomplete-complex[@name='resin']")
    driver.execute_script("""
                        arguments[0].scrollIntoView({block: 'center', inline: 'center'});
                    """, dropdown)
    dropdown.click()
    sleep(1)
    try:
        ele = driver.find_element(By.XPATH,
                                  f"//mat-option//span[@class='mat-option-text']//span[normalize-space()='{text}']")
        _ensure_element_visible(driver, ele)
        ele.click()
        return {"status": "success", "message": f"[select_material] 成功选择材料: {text}"}
    except:
        ele = _display_find_element(driver, "(//mat-option)[1]")
        _text = ele.text
        _ensure_element_visible(driver, ele)
        ele.click()
        return {"status": "success", "message": f"[select_material] 找不到材料默认选择第一个材料：{_text}"}


def _set_layer_height(driver, layer_height: float):
    """设置层高"""
    try:
        # 查找层高输入框
        layer_height_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Layer Height') or contains(@placeholder, '层高')]"))
        )
        layer_height_input.clear()
        layer_height_input.send_keys(str(layer_height))
        logger.info(f"✅ 设置层高: {layer_height}")
    except Exception as e:
        logger.warning(f"⚠️ 设置层高失败: {str(e)}")

def _set_infill_density(driver, infill_density: int):
    """设置填充密度"""
    try:
        # 查找填充密度输入框
        infill_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Infill') or contains(@placeholder, '填充')]"))
        )
        infill_input.clear()
        infill_input.send_keys(str(infill_density))
        logger.info(f"✅ 设置填充密度: {infill_density}%")
    except Exception as e:
        logger.warning(f"⚠️ 设置填充密度失败: {str(e)}")

def _set_print_speed(driver, print_speed: int):
    """设置打印速度"""
    try:
        # 查找打印速度输入框
        speed_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Speed') or contains(@placeholder, '速度')]"))
        )
        speed_input.clear()
        speed_input.send_keys(str(print_speed))
        logger.info(f"✅ 设置打印速度: {print_speed}")
    except Exception as e:
        logger.warning(f"⚠️ 设置打印速度失败: {str(e)}")

def _set_temperature(driver, temperature: int):
    """设置温度"""
    try:
        # 查找温度输入框
        temp_input = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Temperature') or contains(@placeholder, '温度')]"))
        )
        temp_input.clear()
        temp_input.send_keys(str(temperature))
        logger.info(f"✅ 设置温度: {temperature}°C")
    except Exception as e:
        logger.warning(f"⚠️ 设置温度失败: {str(e)}")

def upload_local_file(file_path: str) -> Dict[str, Any]:
    """上传本地文件"""
    try:
        driver = get_driver()
        
        # 查找文件上传输入框
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        )
        
        # 上传文件
        file_input.send_keys(file_path)
        
        # 等待上传完成
        sleep(3)
        
        logger.info(f"✅ 文件上传成功: {file_path}")
        return {
            "status": "success",
            "message": f"文件上传成功: {file_path}"
        }
        
    except Exception as e:
        logger.error(f"❌ 文件上传失败: {str(e)}")
        return {
            "status": "error",
            "message": f"文件上传失败: {str(e)}"
        }

@tool
def submit_print_job(**kwargs) -> Dict[str, Any]:
    """提交打印任务"""
    logger.info("🚀 提交打印任务")
    driver = get_driver()
    
    try:
        # 查找提交按钮
        submit_selectors = [
            (By.XPATH, "//button[contains(text(), 'Submit')]"),
            (By.XPATH, "//button[contains(text(), '提交')]"),
            (By.XPATH, "//button[contains(text(), 'Start Print')]"),
            (By.XPATH, "//button[contains(text(), '开始打印')]"),
            (By.CSS_SELECTOR, ".submit-button"),
            (By.CSS_SELECTOR, ".btn-primary")
        ]
        
        for by, value in submit_selectors:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((by, value))
                )
                button.click()
                logger.info("✅ 打印任务提交成功")
                return {
                    "status": "success",
                    "message": "打印任务提交成功"
                }
            except TimeoutException:
                continue
        
        return {
            "status": "error",
            "message": "未找到提交按钮"
        }
        
    except Exception as e:
        logger.error(f"❌ 提交打印任务失败: {str(e)}")
        return {
            "status": "error",
            "message": f"提交打印任务失败: {str(e)}"
        } 