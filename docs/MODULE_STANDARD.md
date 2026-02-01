# AITools 模块接口标准规范

## 概述

本文档定义了AITools框架中模块的标准接口规范。所有模块都应遵循此规范以确保兼容性和一致性。

## 模块结构

一个标准的AITools模块应包含以下文件和目录结构：

```
module_name/
├── __init__.py          # 模块入口点（必需）
├── module_name.py       # 主实现文件（可选，但推荐）
├── README.md            # 模块文档（可选）
└── tests/               # 测试文件（可选）
```

## 模块元数据

模块必须提供元数据信息，可以通过以下方式之一：

### 方式1：`__module_metadata__` 字典（推荐）

在模块的`__init__.py`或主实现文件中定义：

```python
__module_metadata__ = {
    "name": "module_name",          # 模块名称（必需）
    "version": "1.0.0",             # 版本号（必需）
    "description": "模块描述",       # 模块描述（必需）
    "author": "作者名称",            # 作者信息（可选）
    "dependencies": [],             # 依赖包列表（可选）
    "tags": ["tag1", "tag2"],       # 标签列表（可选）
    "config_schema": {              # 配置模式（可选）
        "setting_name": {
            "type": "string",
            "default": "default_value",
            "description": "设置描述"
        }
    }
}
```

### 方式2：模块属性

也可以在`__init__.py`中直接定义属性：

```python
__version__ = "1.0.0"
__author__ = "作者名称"
__description__ = "模块描述"
__dependencies__ = []  # 可选
```

## 工具定义

模块必须通过`tools`列表和`TOOL_CALL_MAP`字典导出其功能。

### 1. 工具函数定义

使用`base`模块提供的装饰器定义工具：

```python
from base import function_ai, parameters_func, property_param

# 定义参数属性
__PARAM_PROPERTY__ = property_param(
    name="param_name",
    description="参数描述",
    t="string",  # 类型：string, number, integer, boolean, array, object
    required=True
)

# 定义工具函数
__TOOL_FUNCTION__ = function_ai(
    name="tool_name",
    description="工具描述",
    parameters=parameters_func([__PARAM_PROPERTY__])
)
```

### 2. 工具实现

为每个工具提供实现函数：

```python
def tool_name(param_name: str) -> str:
    """工具实现函数。
    
    Args:
        param_name: 参数描述
        
    Returns:
        执行结果
    """
    # 实现逻辑
    return f"Result: {param_name}"
```

### 3. 工具列表和映射

在模块中定义：

```python
# 工具列表（OpenAI格式）
tools = [__TOOL_FUNCTION__]

# 工具调用映射
TOOL_CALL_MAP = {
    "tool_name": tool_name,
}
```

## 模块入口点（__init__.py）

模块的`__init__.py`文件应至少包含：

```python
"""
模块文档字符串
"""

# 导入工具定义
from .module_file import tools, TOOL_CALL_MAP

# 可选：导出其他函数
__all__ = ['tools', 'TOOL_CALL_MAP']
```

## 命名规范

### 模块名称
- 使用小写字母和下划线
- 简短、描述性强
- 示例：`file_operations`, `pdf_tools`, `git_utils`

### 工具名称
- 使用小写字母和下划线
- 动词开头，描述操作
- 格式：`action_object` 或 `module_action`
- 示例：`read_file`, `extract_text_from_pdf`, `git_status`

### 参数名称
- 使用小写字母和下划线
- 描述参数用途
- 示例：`file_path`, `page_range`, `repo_path`

## 错误处理

工具函数应包含适当的错误处理：

```python
def tool_function(param):
    try:
        # 实现逻辑
        return result
    except Exception as e:
        return f"错误: {str(e)}"
```

## 文档要求

每个模块应包含：

1. **模块级文档**：在`__init__.py`中描述模块功能和用途
2. **工具级文档**：每个工具函数应有完整的docstring，包含参数说明和返回说明
3. **示例**：提供使用示例

## 配置支持

模块可以通过`config_schema`定义配置选项，并通过`get_config()`函数访问配置：

```python
def get_config():
    """获取模块配置"""
    from base.config_manager import get_module_config
    return get_module_config("module_name")
```

## 测试要求

每个模块应包含测试文件，至少覆盖：
- 工具函数的基本功能
- 错误处理
- 边界情况

## 兼容性

### 向后兼容性
- 避免破坏性更改
- 新增功能应保持向后兼容
- 弃用功能应提供迁移路径

### 导入兼容性
- 处理导入错误
- 提供优雅的回退机制

## 验证工具

使用以下代码验证模块是否符合标准：

```python
from base.module_loader import ModuleLoader

loader = ModuleLoader()
module = loader.load_module("module_name")
if module:
    print(f"✓ 模块 '{module.name}' 加载成功")
    print(f"  工具数量: {len(module.tools)}")
else:
    print(f"✗ 模块加载失败")
```

## 示例模块

参考 `module_template/` 目录中的模板模块。

## 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-01-28 | 初始版本 |

## 联系方式

如有问题或建议，请联系项目维护者。