"""
CtxInspectTool - 上下文检查工具
Claude Code工具复刻，简化版本。
用于检查当前上下文信息，如工作区、内存、配置等。
"""

import json
import time
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# 尝试导入psutil，但如果没有则提供回退
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# ===== 工具实现 =====

def ctx_inspect_tool(
    detail_level: Optional[str] = "basic",
    include_memory: Optional[bool] = True,
    include_config: Optional[bool] = True,
    include_workspace: Optional[bool] = True,
) -> str:
    """
    检查当前上下文信息。
    
    参数:
        detail_level: 详细级别 - "basic" (基础), "detailed" (详细), "full" (完整)
        include_memory: 是否包含内存使用信息
        include_config: 是否包含配置信息
        include_workspace: 是否包含工作区信息
    
    返回:
        JSON字符串格式的上下文检查结果
    """
    start_time = time.time()
    
    try:
        # 收集上下文信息
        context_info = {
            "timestamp": datetime.now().isoformat(),
            "detailLevel": detail_level,
            "inspectedAt": int(time.time() * 1000),
        }
        
        # 基础系统信息
        system_info = {
            "platform": sys.platform,
            "pythonVersion": sys.version,
            "cwd": os.getcwd(),
            "username": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
        }
        
        # 根据详细级别调整信息收集
        if detail_level in ["detailed", "full"]:
            system_info.update({
                "executable": sys.executable,
                "argv": sys.argv,
                "path": sys.path[:10],  # 限制长度
            })
        
        context_info["system"] = system_info
        
        # 内存信息
        if include_memory:
            try:
                if PSUTIL_AVAILABLE:
                    process = psutil.Process()
                    memory_info = {
                        "processMemoryMB": round(process.memory_info().rss / 1024 / 1024, 2),
                        "processMemoryPercent": round(process.memory_percent(), 2),
                    }
                    
                    if detail_level in ["detailed", "full"]:
                        system_memory = psutil.virtual_memory()
                        memory_info.update({
                            "systemTotalMB": round(system_memory.total / 1024 / 1024, 2),
                            "systemAvailableMB": round(system_memory.available / 1024 / 1024, 2),
                            "systemUsedPercent": round(system_memory.percent, 2),
                        })
                    
                    context_info["memory"] = memory_info
                else:
                    # psutil不可用时的回退信息
                    context_info["memory"] = {
                        "note": "psutil not available, memory information limited",
                        "psutilAvailable": False
                    }
            except Exception as e:
                context_info["memory"] = {"error": f"Failed to collect memory info: {str(e)}", "psutilAvailable": PSUTIL_AVAILABLE}
        
        # 环境变量信息（简化配置）
        if include_config:
            config_info = {}
            
            # 收集一些重要的环境变量
            important_env_vars = [
                "HOME", "PATH", "USER", "LANG", "PWD",
                "PYTHONPATH", "VIRTUAL_ENV"
            ]
            
            for var in important_env_vars:
                if var in os.environ:
                    config_info[var] = os.environ[var]
            
            # 添加一些统计
            config_info["totalEnvVars"] = len(os.environ)
            
            if detail_level == "full":
                # 在完整模式下包含所有环境变量（但限制敏感信息）
                all_env = {}
                for key, value in os.environ.items():
                    # 过滤掉可能敏感的信息
                    if any(sensitive in key.lower() for sensitive in ["pass", "secret", "token", "key"]):
                        all_env[key] = "[REDACTED]"
                    else:
                        all_env[key] = value
                config_info["allEnvironment"] = all_env
            
            context_info["configuration"] = config_info
        
        # 工作区信息
        if include_workspace:
            workspace_info = {}
            cwd = os.getcwd()
            
            try:
                # 列出当前目录
                files = os.listdir(cwd)
                workspace_info["currentDirectory"] = cwd
                workspace_info["fileCount"] = len(files)
                
                if detail_level in ["detailed", "full"]:
                    # 分类文件
                    file_types = {
                        "pythonFiles": [],
                        "textFiles": [],
                        "directories": [],
                        "otherFiles": []
                    }
                    
                    for file in files[:50]:  # 限制数量
                        full_path = os.path.join(cwd, file)
                        if os.path.isdir(full_path):
                            file_types["directories"].append(file)
                        elif file.endswith((".py", ".pyc", ".pyo")):
                            file_types["pythonFiles"].append(file)
                        elif file.endswith((".txt", ".md", ".json", ".yml", ".yaml", ".ini")):
                            file_types["textFiles"].append(file)
                        else:
                            file_types["otherFiles"].append(file)
                    
                    workspace_info["fileTypes"] = file_types
                    
                    # 磁盘使用情况（仅当psutil可用时）
                    if PSUTIL_AVAILABLE:
                        try:
                            disk_usage = psutil.disk_usage(cwd)
                            workspace_info["diskUsage"] = {
                                "totalGB": round(disk_usage.total / 1024 / 1024 / 1024, 2),
                                "usedGB": round(disk_usage.used / 1024 / 1024 / 1024, 2),
                                "freeGB": round(disk_usage.free / 1024 / 1024 / 1024, 2),
                                "percentUsed": disk_usage.percent
                            }
                        except Exception as e:
                            workspace_info["diskUsage"] = {"error": f"Failed to get disk usage: {str(e)}"}
                    else:
                        workspace_info["diskUsage"] = {"note": "psutil not available, disk usage information not collected"}
                
                context_info["workspace"] = workspace_info
            except Exception as e:
                context_info["workspace"] = {"error": f"Failed to collect workspace info: {str(e)}"}
        
        # 处理时间信息
        context_info["collectionTimeMs"] = int((time.time() - start_time) * 1000)
        
        # 构建结果
        result = {
            "success": True,
            "context": context_info,
            "detailLevel": detail_level,
            "timestamp": int(time.time() * 1000),
            "durationMs": int((time.time() - start_time) * 1000),
            "note": "Simplified CtxInspectTool implementation for AITools"
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        # 错误处理
        result = {
            "success": False,
            "error": f"Failed to inspect context: {str(e)}",
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(result, ensure_ascii=False)


# ===== 工具注册 =====

# 工具定义
TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "ctx_inspect",
        "description": "Inspect current context including system, memory, configuration and workspace information.",
        "parameters": {
            "type": "object",
            "properties": {
                "detail_level": {
                    "type": "string",
                    "description": "Level of detail: 'basic', 'detailed', or 'full'",
                    "enum": ["basic", "detailed", "full"]
                },
                "include_memory": {
                    "type": "boolean",
                    "description": "Include memory usage information"
                },
                "include_config": {
                    "type": "boolean",
                    "description": "Include configuration and environment information"
                },
                "include_workspace": {
                    "type": "boolean",
                    "description": "Include workspace and file system information"
                }
            }
        }
    }
}

# 工具调用映射
TOOL_CALL_MAP = {
    "ctx_inspect": ctx_inspect_tool
}

# 工具列表
tools = [TOOL_DEF]

# ===== 模块导出 =====
__all__ = ["tools", "TOOL_CALL_MAP", "ctx_inspect_tool"]