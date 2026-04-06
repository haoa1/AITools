"""
OverflowTestTool - 溢出测试工具
Claude Code工具复刻，简化版本。
用于测试大输出或边界情况的工具。
"""

import json
import time
import random
import string
from typing import Dict, Any, Optional

# ===== 工具实现 =====

def overflow_test_tool(
    size_kb: Optional[int] = 10,
    test_type: Optional[str] = "text",
    include_metadata: Optional[bool] = True,
) -> str:
    """
    生成测试数据以测试溢出或边界情况。
    
    参数:
        size_kb: 生成数据的大小（KB），默认10KB
        test_type: 测试类型 - "text"（文本）, "json"（JSON）, "mixed"（混合）
        include_metadata: 是否包含元数据
    
    返回:
        JSON字符串格式的测试结果
    """
    start_time = time.time()
    
    try:
        # 限制大小以避免真正溢出
        max_size_kb = 100  # 最大100KB，避免真正溢出
        requested_size = size_kb
        if size_kb > max_size_kb:
            size_kb = max_size_kb
        
        # 生成测试数据
        test_data = ""
        if test_type == "text":
            # 生成随机文本
            chars = string.ascii_letters + string.digits + " \n\t"
            target_size = size_kb * 1024
            while len(test_data) < target_size:
                chunk_size = min(1000, target_size - len(test_data))
                test_data += ''.join(random.choice(chars) for _ in range(chunk_size))
                
        elif test_type == "json":
            # 生成嵌套JSON结构
            target_items = max(10, size_kb * 5)  # 每KB约5个项
            data = {
                "testType": "json",
                "sizeKB": size_kb,
                "items": []
            }
            
            for i in range(target_items):
                item = {
                    "id": i,
                    "name": f"Item_{i}",
                    "value": random.random() * 1000,
                    "nested": {
                        "level1": {
                            "level2": {
                                "level3": f"Nested value {i}"
                            }
                        }
                    }
                }
                data["items"].append(item)
            
            test_data = json.dumps(data, indent=2)
            
        else:  # mixed
            # 混合文本和JSON
            text_part = "Text section:\n" + "\n".join([f"Line {i}: Test data" for i in range(100)])
            json_part = json.dumps({
                "metadata": {
                    "sizeKB": size_kb,
                    "type": test_type,
                    "timestamp": time.time()
                },
                "sampleData": [{"id": i, "value": i*2} for i in range(50)]
            }, indent=2)
            
            test_data = f"{text_part}\n\nJSON section:\n{json_part}"
            
            # 如果数据太小，添加更多内容
            while len(test_data) < size_kb * 1024:
                test_data += "\nAdditional test data line to meet size requirement."
        
        # 计算实际大小
        actual_size_kb = len(test_data) / 1024
        
        # 构建结果
        result = {
            "success": True,
            "testType": test_type,
            "requestedSizeKB": requested_size,
            "actualSizeKB": round(actual_size_kb, 2),
            "dataSizeBytes": len(test_data),
            "testDataPreview": test_data[:500] + "..." if len(test_data) > 500 else test_data,
            "timestamp": int(time.time() * 1000),
            "durationMs": int((time.time() - start_time) * 1000),
        }
        
        if include_metadata:
            result["metadata"] = {
                "generatedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
                "randomSeed": random.randint(1, 10000),
                "note": "Simplified overflow test tool for AITools"
            }
        
        # 如果数据很大，添加警告
        if requested_size > 50:
            result["warning"] = f"Large test data generated ({requested_size}KB requested, limited to {size_kb}KB). Consider smaller size for performance."
            result["sizeLimited"] = requested_size > max_size_kb
            result["sizeLimitKB"] = max_size_kb
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        # 错误处理
        result = {
            "success": False,
            "error": f"Failed to generate test data: {str(e)}",
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(result, ensure_ascii=False)


# ===== 工具注册 =====

# 工具定义
TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "overflow_test",
        "description": "Generate test data for overflow or boundary testing.",
        "parameters": {
            "type": "object",
            "properties": {
                "size_kb": {
                    "type": "integer",
                    "description": "Size of test data to generate in KB (default: 10, max: 100)",
                    "minimum": 1,
                    "maximum": 1000
                },
                "test_type": {
                    "type": "string",
                    "description": "Type of test data: 'text', 'json', or 'mixed'",
                    "enum": ["text", "json", "mixed"]
                },
                "include_metadata": {
                    "type": "boolean",
                    "description": "Include metadata in the response"
                }
            }
        }
    }
}

# 工具调用映射
TOOL_CALL_MAP = {
    "overflow_test": overflow_test_tool
}

# 工具列表
tools = [TOOL_DEF]

# ===== 模块导出 =====
__all__ = ["tools", "TOOL_CALL_MAP", "overflow_test_tool"]