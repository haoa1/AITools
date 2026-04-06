#!/usr/bin/env python3
"""
TaskGetTool implementation for AITools (Claude Code compatible version).
Retrieve a task by its ID.
Simplified version focusing on basic task retrieval functionality.
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__TASK_GET_TASK_ID_PROPERTY__ = property_param(
    name="taskId",
    description="The ID of the task to retrieve.",
    t="string",
    required=True
)

# ============================================================================
# CONFIGURATION CLASS
# ============================================================================

class TaskGetConfig:
    """TaskGetTool配置类"""
    
    @staticmethod
    def from_env():
        """从环境变量创建配置"""
        import os
        
        # 读取环境变量，使用空字符串表示使用配置默认值
        task_get_enabled = os.getenv("TASK_GET_ENABLED", "")
        task_get_interactive = os.getenv("TASK_GET_INTERACTIVE", "")
        task_get_storage_path = os.getenv("TASK_GET_STORAGE_PATH", "")
        
        config = {
            "TASK_GET_ENABLED": True,  # 默认启用
            "TASK_GET_INTERACTIVE": True,  # 默认交互模式
            "TASK_GET_STORAGE_PATH": os.path.join(os.path.expanduser("~"), ".aitools_tasks.json"),  # 任务存储路径
            "TASK_GET_ANALYTICS_ENABLED": False,  # 默认禁用分析
        }
        
        # 覆盖环境变量设置（如果非空）
        if task_get_enabled != "":
            config["TASK_GET_ENABLED"] = task_get_enabled.lower() in ["true", "1", "yes", "y"]
        
        if task_get_interactive != "":
            config["TASK_GET_INTERACTIVE"] = task_get_interactive.lower() in ["true", "1", "yes", "y"]
        
        if task_get_storage_path != "":
            config["TASK_GET_STORAGE_PATH"] = task_get_storage_path
        
        return config

# ============================================================================
# TASK STORAGE MANAGEMENT (shared with TaskCreateTool)
# ============================================================================

def _load_tasks(storage_path: str) -> Dict[str, Any]:
    """从文件加载任务"""
    try:
        if os.path.exists(storage_path):
            with open(storage_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load tasks from {storage_path}: {e}")
    
    # 返回空任务结构
    return {
        "version": "1.0",
        "tasks": {},
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

def _get_task_by_id(task_id: str, storage_path: str) -> Optional[Dict[str, Any]]:
    """通过ID获取任务"""
    tasks_data = _load_tasks(storage_path)
    tasks = tasks_data.get("tasks", {})
    return tasks.get(task_id)

def _task_exists(task_id: str, storage_path: str) -> bool:
    """检查任务是否存在"""
    return _get_task_by_id(task_id, storage_path) is not None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _validate_parameters(task_id: str) -> List[str]:
    """验证TaskGetTool参数"""
    errors = []
    
    # 验证任务ID
    if not task_id or not isinstance(task_id, str):
        errors.append("'taskId' must be a non-empty string")
    elif len(task_id) > 100:  # UUID通常为36字符，留有余量
        errors.append("'taskId' must be at most 100 characters")
    
    return errors

def _format_task_for_display(task: Dict[str, Any]) -> str:
    """格式化任务用于显示"""
    task_id_short = task["id"][:8]  # 使用短ID
    status_emoji = {
        "todo": "📝",
        "in_progress": "🔄",
        "done": "✅"
    }.get(task.get("status", "todo"), "📝")
    
    lines = [
        f"\n{status_emoji} Task Found: {task['subject']}",
        f"   ID: {task_id_short} (full: {task['id']})",
        f"   Description: {task['description']}",
    ]
    
    if "active_form" in task:
        lines.append(f"   Active Form: {task['active_form']}")
    
    lines.append(f"   Status: {task.get('status', 'todo')}")
    lines.append(f"   Created: {task['created_at'][:19]}")  # 只显示日期和时间
    lines.append(f"   Updated: {task['updated_at'][:19]}")
    
    # 添加metadata信息（如果有）
    if "metadata" in task and task["metadata"]:
        metadata_str = json.dumps(task["metadata"], indent=2)
        metadata_lines = metadata_str.split('\n')
        if len(metadata_lines) > 5:  # 如果metadata太长，只显示摘要
            lines.append(f"   Metadata: {len(task['metadata'])} key-value pairs")
        else:
            lines.append("   Metadata:")
            for line in metadata_lines:
                lines.append(f"     {line}")
    
    return "\n".join(lines)

def _display_task_found(task: Dict[str, Any], config: Dict):
    """显示找到的任务信息"""
    if config["TASK_GET_INTERACTIVE"]:
        # 交互模式显示
        formatted = _format_task_for_display(task)
        print(formatted)
    else:
        # 非交互模式
        task_id_short = task["id"][:8]
        print(f"[TASK_GET] Found task: {task['subject']} (ID: {task_id_short}, Status: {task.get('status', 'todo')})")

def _display_task_not_found(task_id: str, config: Dict):
    """显示任务未找到信息"""
    if config["TASK_GET_INTERACTIVE"]:
        print(f"\n❌ Task Not Found: {task_id}")
    else:
        print(f"[TASK_GET] Task not found: {task_id}")

def _log_task_retrieval_event(task_id: str, found: bool):
    """记录任务检索事件（简化版）"""
    try:
        from system.config import log_analytics_event
        log_analytics_event(
            "task_retrieved",
            {
                "task_id": task_id,
                "found": found,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except:
        pass  # 分析是可选的

# ============================================================================
# AI FUNCTION DEFINITION
# ============================================================================

__TASK_GET_FUNCTION__ = function_ai(
    name="task_get",
    description="Retrieve a task by its ID.",
    parameters=parameters_func([
        __TASK_GET_TASK_ID_PROPERTY__
    ]),
)

tools = [__TASK_GET_FUNCTION__]

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def task_get(taskId: str):
    """
    Retrieve a task by its ID.
    
    Args:
        taskId: The ID of the task to retrieve
        
    Returns:
        Dictionary with task information or null task
    """
    # 验证参数
    errors = _validate_parameters(taskId)
    if errors:
        raise ValueError(f"Parameter validation failed: {', '.join(errors)}")
    
    # 获取配置
    config = TaskGetConfig.from_env()
    
    # 检查工具是否启用
    if not config["TASK_GET_ENABLED"]:
        raise RuntimeError("Task get tool is not enabled in configuration")
    
    # 检查任务是否存在
    storage_path = config["TASK_GET_STORAGE_PATH"]
    task = _get_task_by_id(taskId, storage_path)
    
    # 记录分析事件
    if config["TASK_GET_ANALYTICS_ENABLED"]:
        _log_task_retrieval_event(taskId, task is not None)
    
    # 处理结果
    if task:
        # 显示任务信息
        try:
            _display_task_found(task, config)
        except Exception as e:
            # 回退到简单输出
            print(f"\nTask found: {task['subject']} (ID: {task['id'][:8]})")
        
        # 准备响应数据（与Claude Code兼容）
        response_data = {
            "task": {
                "id": task["id"],
                "subject": task["subject"],
                "description": task["description"],
                "status": task.get("status", "todo"),
                "blocks": [],  # 简化：不支持任务块
                "blockedBy": []  # 简化：不支持被阻塞关系
            }
        }
    else:
        # 任务未找到
        _display_task_not_found(taskId, config)
        
        # 准备响应数据（与Claude Code兼容）
        response_data = {
            "task": None
        }
    
    return response_data

# ============================================================================
# CONFIG GETTER (for testing)
# ============================================================================

def _get_config():
    """获取当前配置（用于测试）"""
    return TaskGetConfig.from_env()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ["tools", "task_get", "TaskGetConfig", "_get_config"]