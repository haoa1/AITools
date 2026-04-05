"""
TerminalCaptureTool - 终端捕获工具
Claude Code工具复刻，简化版本。
用于捕获终端输出或执行终端命令。
"""

import json
import time
import subprocess
import shlex
from typing import Dict, Any, Optional, List

# ===== 工具实现 =====

def terminal_capture_tool(
    command: Optional[str] = None,
    capture_output: Optional[bool] = True,
    timeout_seconds: Optional[int] = 30,
    working_directory: Optional[str] = None,
) -> str:
    """
    执行终端命令并捕获输出。
    
    参数:
        command: 要执行的终端命令（如果为空，则返回当前终端状态）
        capture_output: 是否捕获输出
        timeout_seconds: 命令执行超时时间（秒）
        working_directory: 工作目录
    
    返回:
        JSON字符串格式的终端捕获结果
    """
    start_time = time.time()
    
    try:
        # 如果没有提供命令，返回终端状态信息
        if not command:
            result = {
                "success": True,
                "command": None,
                "output": "",
                "status": "idle",
                "terminalInfo": {
                    "timestamp": int(time.time() * 1000),
                    "note": "No command provided, returning terminal status"
                },
                "timestamp": int(time.time() * 1000),
                "durationMs": int((time.time() - start_time) * 1000),
                "note": "Simplified terminal capture tool for AITools"
            }
            return json.dumps(result, ensure_ascii=False)
        
        # 执行命令
        if capture_output:
            try:
                # 设置工作目录
                cwd = working_directory if working_directory else None
                
                # 执行命令并捕获输出
                process = subprocess.run(
                    shlex.split(command) if isinstance(command, str) else command,
                    capture_output=True,
                    text=True,
                    timeout=timeout_seconds,
                    cwd=cwd
                )
                
                # 构建结果
                result = {
                    "success": True,
                    "command": command,
                    "returnCode": process.returncode,
                    "stdout": process.stdout,
                    "stderr": process.stderr,
                    "captured": True,
                    "timeoutSeconds": timeout_seconds,
                    "workingDirectory": cwd or "current",
                    "timestamp": int(time.time() * 1000),
                    "durationMs": int((time.time() - start_time) * 1000),
                }
                
                # 添加命令执行状态
                if process.returncode == 0:
                    result["status"] = "success"
                else:
                    result["status"] = "error"
                    result["error"] = f"Command exited with code {process.returncode}"
                
            except subprocess.TimeoutExpired:
                # 超时处理
                result = {
                    "success": False,
                    "command": command,
                    "error": f"Command timed out after {timeout_seconds} seconds",
                    "status": "timeout",
                    "timeoutSeconds": timeout_seconds,
                    "timestamp": int(time.time() * 1000),
                    "durationMs": int((time.time() - start_time) * 1000),
                }
            except FileNotFoundError:
                # 命令未找到
                result = {
                    "success": False,
                    "command": command,
                    "error": "Command not found",
                    "status": "command_not_found",
                    "timestamp": int(time.time() * 1000),
                    "durationMs": int((time.time() - start_time) * 1000),
                }
            except Exception as e:
                # 其他错误
                result = {
                    "success": False,
                    "command": command,
                    "error": f"Command execution failed: {str(e)}",
                    "status": "execution_error",
                    "timestamp": int(time.time() * 1000),
                    "durationMs": int((time.time() - start_time) * 1000),
                }
        else:
            # 不捕获输出，仅执行命令
            result = {
                "success": True,
                "command": command,
                "output": "",
                "captured": False,
                "status": "executed_without_capture",
                "note": "Command executed without output capture",
                "timestamp": int(time.time() * 1000),
                "durationMs": int((time.time() - start_time) * 1000),
            }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        # 顶层错误处理
        result = {
            "success": False,
            "error": f"Terminal capture failed: {str(e)}",
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(result, ensure_ascii=False)


# ===== 工具注册 =====

# 工具定义
TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "terminal_capture",
        "description": "Execute terminal commands and capture output, or get terminal status.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Terminal command to execute (if empty, returns terminal status)"
                },
                "capture_output": {
                    "type": "boolean",
                    "description": "Whether to capture command output"
                },
                "timeout_seconds": {
                    "type": "integer",
                    "description": "Timeout for command execution in seconds",
                    "minimum": 1,
                    "maximum": 300
                },
                "working_directory": {
                    "type": "string",
                    "description": "Working directory for command execution"
                }
            }
        }
    }
}

# 工具调用映射
TOOL_CALL_MAP = {
    "terminal_capture": terminal_capture_tool
}

# 工具列表
tools = [TOOL_DEF]

# ===== 模块导出 =====
__all__ = ["tools", "TOOL_CALL_MAP", "terminal_capture_tool"]