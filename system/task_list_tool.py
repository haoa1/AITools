#!/usr/bin/env python3
"""
TaskListTool implementation for AITools (Claude Code compatible version).
List all tasks in the task list.
Simplified version focusing on basic task listing functionality.
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

# TaskListTool没有输入参数，但我们需要定义一个空参数列表
# 注意：base模块可能需要至少一个参数，所以我们将创建一个虚拟参数

__TASK_LIST_DUMMY_PROPERTY__ = property_param(
    name="_dummy",
    description="Dummy parameter for TaskListTool (no actual parameters needed).",
    t="string",
    required=False
)

# ============================================================================
# CONFIGURATION CLASS
# ============================================================================

class TaskListConfig:
    """TaskListTool配置类"""
    
    @staticmethod
    def from_env():
        """从环境变量创建配置"""
        import os
        
        # 读取环境变量，使用空字符串表示使用配置默认值
        task_list_enabled = os.getenv("TASK_LIST_ENABLED", "")
        task_list_interactive = os.getenv("TASK_LIST_INTERACTIVE", "")
        task_list_storage_path = os.getenv("TASK_LIST_STORAGE_PATH", "")
        task_list_max_tasks = os.getenv("TASK_LIST_MAX_TASKS", "")
        
        config = {
            "TASK_LIST_ENABLED": True,  # 默认启用
            "TASK_LIST_INTERACTIVE": True,  # 默认交互模式
            "TASK_LIST_STORAGE_PATH": os.path.join(os.path.expanduser("~"), ".aitools_tasks.json"),  # 任务存储路径
            "TASK_LIST_MAX_TASKS": 1000,  # 最大显示任务数
            "TASK_LIST_ANALYTICS_ENABLED": False,  # 默认禁用分析
        }
        
        # 覆盖环境变量设置（如果非空）
        if task_list_enabled != "":
            config["TASK_LIST_ENABLED"] = task_list_enabled.lower() in ["true", "1", "yes", "y"]
        
        if task_list_interactive != "":
            config["TASK_LIST_INTERACTIVE"] = task_list_interactive.lower() in ["true", "1", "yes", "y"]
        
        if task_list_storage_path != "":
            config["TASK_LIST_STORAGE_PATH"] = task_list_storage_path
        
        if task_list_max_tasks != "":
            try:
                config["TASK_LIST_MAX_TASKS"] = int(task_list_max_tasks)
            except ValueError:
                pass  # 保持默认值
        
        return config

# ============================================================================
# TASK STORAGE MANAGEMENT (shared with TaskCreateTool and TaskGetTool)
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

def _get_all_tasks(storage_path: str) -> List[Dict[str, Any]]:
    """获取所有任务"""
    tasks_data = _load_tasks(storage_path)
    tasks_dict = tasks_data.get("tasks", {})
    
    # 转换为列表并按创建时间排序（最新的在前）
    tasks_list = list(tasks_dict.values())
    tasks_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return tasks_list

def _get_task_count(storage_path: str) -> int:
    """获取任务数量"""
    tasks_data = _load_tasks(storage_path)
    return len(tasks_data.get("tasks", {}))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _format_task_for_listing(task: Dict[str, Any], index: int) -> str:
    """格式化任务用于列表显示"""
    task_id_short = task["id"][:8]  # 使用短ID
    status_emoji = {
        "todo": "📝",
        "in_progress": "🔄",
        "done": "✅"
    }.get(task.get("status", "todo"), "📝")
    
    # 构建任务行
    line = f"{index+1:3d}. {status_emoji} {task['subject'][:50]}{'...' if len(task['subject']) > 50 else ''}"
    line += f" (ID: {task_id_short})"
    
    return line

def _format_task_list_for_display(tasks: List[Dict[str, Any]], total_count: int, config: Dict) -> str:
    """格式化任务列表用于显示"""
    if not tasks:
        return "\n📭 No tasks found. Use TaskCreateTool to create a task."
    
    lines = [f"\n📋 Task List ({len(tasks)} tasks):"]
    
    # 添加每个任务
    for i, task in enumerate(tasks):
        lines.append(_format_task_for_listing(task, i))
    
    # 添加统计信息
    lines.append(f"\n📊 Statistics:")
    lines.append(f"   • Total tasks in system: {total_count}")
    
    # 状态统计
    status_counts = {}
    for task in tasks:
        status = task.get("status", "todo")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    if status_counts:
        lines.append(f"   • Status breakdown:")
        for status, count in sorted(status_counts.items()):
            status_display = {
                "todo": "To Do",
                "in_progress": "In Progress",
                "done": "Done"
            }.get(status, status)
            lines.append(f"     - {status_display}: {count}")
    
    # 如果任务数超过显示限制，添加提示
    max_display = config["TASK_LIST_MAX_TASKS"]
    if total_count > max_display:
        lines.append(f"\nℹ️  Showing first {max_display} tasks (oldest hidden).")
    
    return "\n".join(lines)

def _display_task_list(tasks: List[Dict[str, Any]], total_count: int, config: Dict):
    """显示任务列表"""
    if config["TASK_LIST_INTERACTIVE"]:
        # 交互模式显示
        formatted = _format_task_list_for_display(tasks, total_count, config)
        print(formatted)
    else:
        # 非交互模式
        if not tasks:
            print("[TASK_LIST] No tasks found")
        else:
            print(f"[TASK_LIST] Found {len(tasks)} tasks")

def _log_task_list_event(task_count: int):
    """记录任务列表事件（简化版）"""
    try:
        from system.config import log_analytics_event
        log_analytics_event(
            "task_listed",
            {
                "task_count": task_count,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except:
        pass  # 分析是可选的

def _limit_tasks_for_display(tasks: List[Dict[str, Any]], config: Dict) -> List[Dict[str, Any]]:
    """限制显示的任务数量"""
    max_tasks = config["TASK_LIST_MAX_TASKS"]
    if len(tasks) > max_tasks:
        return tasks[:max_tasks]
    return tasks

# ============================================================================
# AI FUNCTION DEFINITION
# ============================================================================

__TASK_LIST_FUNCTION__ = function_ai(
    name="task_list",
    description="List all tasks in the task list.",
    parameters=parameters_func([
        __TASK_LIST_DUMMY_PROPERTY__
    ]),
)

tools = [__TASK_LIST_FUNCTION__]

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def task_list(_dummy: Optional[str] = None):
    """
    List all tasks in the task list.
    
    Args:
        _dummy: Dummy parameter (not used, required by base module)
        
    Returns:
        Dictionary with list of tasks
    """
    # 获取配置
    config = TaskListConfig.from_env()
    
    # 检查工具是否启用
    if not config["TASK_LIST_ENABLED"]:
        raise RuntimeError("Task list tool is not enabled in configuration")
    
    # 获取所有任务
    storage_path = config["TASK_LIST_STORAGE_PATH"]
    all_tasks = _get_all_tasks(storage_path)
    total_count = _get_task_count(storage_path)
    
    # 限制显示的任务数量
    display_tasks = _limit_tasks_for_display(all_tasks, config)
    
    # 记录分析事件
    if config["TASK_LIST_ANALYTICS_ENABLED"]:
        _log_task_list_event(total_count)
    
    # 显示任务列表
    try:
        _display_task_list(display_tasks, total_count, config)
    except Exception as e:
        # 回退到简单输出
        print(f"\nFound {total_count} tasks")
    
    # 准备响应数据（与Claude Code兼容）
    # 注意：我们只返回显示的任务，而不是所有任务（为了性能）
    response_tasks = []
    for task in display_tasks:
        response_tasks.append({
            "id": task["id"],
            "subject": task["subject"],
            "status": task.get("status", "todo"),
            "owner": None,  # 简化：不支持所有者
            "blockedBy": []  # 简化：不支持被阻塞关系
        })
    
    response_data = {
        "tasks": response_tasks
    }
    
    return response_data

# ============================================================================
# CONFIG GETTER (for testing)
# ============================================================================

def _get_config():
    """获取当前配置（用于测试）"""
    return TaskListConfig.from_env()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ["tools", "task_list", "TaskListConfig", "_get_config"]