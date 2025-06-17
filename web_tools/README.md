# Web 工具包

本模块提供了一组用于 Web 自动化的工具函数和类。

## 打印机选择器

`PrinterSelector` 类提供了选择打印机的功能，支持已连接打印机和虚拟打印机。

### 安装依赖

```bash
pip install selenium pytest
```

### 使用示例

```python
from web_tools.web_toolkit import select_printer

# 选择已连接打印机
result = select_printer({
    "printer": "Pro55S",
    "printer_type": "connected",
    "wait": 10
})

# 选择虚拟打印机
result = select_printer({
    "printer": "Midas",
    "printer_type": "virtual",
    "wait": 10
})
```

### API 文档

#### select_printer

```python
def select_printer(param: Dict[str, Any]) -> Dict[str, Any]:
    """
    智能选择打印机。
    
    参数:
        param: 包含以下字段的字典:
            - printer: 打印机名称或序列号
            - printer_type: 打印机类型 ('connected' 或 'virtual')
            - wait: 等待时间（秒）
    
    返回:
        Dict[str, Any]: 操作结果，包含以下字段:
            - success: 是否成功
            - message: 操作结果消息
    """
```

### 错误处理

该模块提供了完善的错误处理机制：

1. 参数验证
   - 检查必要参数是否存在
   - 验证参数类型和值的合法性

2. 超时处理
   - 设置合理的等待时间
   - 处理元素加载超时的情况

3. 元素交互错误
   - 处理元素不可见的情况
   - 处理元素被遮挡的情况
   - 处理元素点击失败的情况

4. 日志记录
   - 记录详细的操作日志
   - 记录错误信息和堆栈跟踪

### 测试

本模块提供了完整的测试套件：

1. 单元测试
   ```bash
   pytest tests/test_printer_selector.py
   ```

2. 集成测试
   ```bash
   pytest tests/test_printer_integration.py
   ```

### 最佳实践

1. 选择打印机时，建议：
   - 使用准确的打印机名称或序列号
   - 设置合理的等待时间（建议 10 秒）
   - 正确指定打印机类型

2. 错误处理：
   - 始终检查返回结果的 success 字段
   - 记录并处理错误消息
   - 实现重试机制（如果需要）

3. 性能优化：
   - 避免过长的等待时间
   - 使用精确的选择器
   - 及时清理资源

### 常见问题

1. 打印机选择失败
   - 检查打印机名称是否正确
   - 确认打印机类型是否正确
   - 检查网络连接状态
   - 查看详细的错误日志

2. 元素交互问题
   - 确保页面已完全加载
   - 检查元素是否可见
   - 检查元素是否被遮挡
   - 调整等待时间

3. 性能问题
   - 优化选择器
   - 减少不必要的等待
   - 使用无头模式运行

### 贡献指南

1. 代码规范
   - 遵循 PEP 8 规范
   - 添加详细的文档字符串
   - 编写完整的测试用例

2. 提交流程
   - 创建功能分支
   - 编写测试用例
   - 提交代码审查
   - 合并到主分支

### 更新日志

#### v1.0.0
- 初始版本
- 支持已连接打印机和虚拟打印机的选择
- 提供完整的测试套件
- 添加详细的文档

#### v1.1.0
- 改进错误处理机制
- 优化选择器性能
- 添加更多测试用例
- 更新文档 