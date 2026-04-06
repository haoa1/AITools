#!/usr/bin/env python3
"""
TaskUpdateTool implementation for AITools (Claude Code compatible version).
Update a task by its ID.
Simplified version focusing on basic task update functionality.
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

__TASK_UPDATE_TASK_ID_PROPERTY__ = property_param(
    name="taskId",
    description="The ID of the task to update.",
    t="string",
    required=True
)

__TASK_UPDATE_SUBJECT_PROPERTY__ = property_param(
    name="subject",
    description="New subject for the task.",
    t="string",
    required=False
)

__TASK_UPDATE_DESCRIPTION_PROPERTY__ = property_param(
    name="description",
    description="New description for the task.",
    t="string",
    required=False
)

__TASK_UPDATE_ACTIVE_FORM_PROPERTY__ = property_param(
    name="activeForm",
    description="Present continuous form shown in spinner when in_progress (e.g., 'Running tests').",
    t="string",
    required=False
)

__TASK_UPDATE_STATUS_PROPERTY__ = property_param(
    name="status",
    description="New status for the task (todo, in_progress, done, or 'deleted' to delete the task).",
    t="string",
    required=False
)

__TASK_UPDATE_METADATA_PROPERTY__ = property_param(
    name="metadata",
    description="Metadata keys to merge into the task as JSON string. Set a key to null to delete it.",
    t="string",
    required=False
)

# ============================================================================
# CONFIGURATION CLASS
# ============================================================================

class TaskUpdateConfig:
    """TaskUpdateTool配置类"""
    
    @staticmethod
    def from_env():
        """从环境变量创建配置"""
        import os
        
        # 读取环境变量，使用空字符串表示使用配置默认值
        task_update_enabled = os.getenv("TASK_UPDATE_ENABLED", "")
        task_update_interactive = os.getenv("TASK_UPDATE_INTERACTIVE", "")
        task_update_storage_path = os.getenv("TASK_UPDATE_STORAGE_PATH", "")
        task_update_allow_delete = os.getenv("TASK_UPDATE_ALLOW_DELETE", "")
        
        config = {
            "TASK_UPDATE_ENABLED": True,  # 默认启用
            "TASK_UPDATE_INTERACTIVE": True,  # 默认交互模式
            "TASK_UPDATE_STORAGE_PATH": os.path.join(os.path.expanduser("~"), ".aitools_tasks.json"),  # 任务存储路径
            "TASK_UPDATE_ANALYTICS_ENABLED": False,  # 默认禁用分析
            "TASK_UPDATE_ALLOW_DELETE": True,  # 默认允许删除任务
        }
        
        # 覆盖环境变量设置（如果非空）
        if task_update_enabled != "":
            config["TASK_UPDATE_ENABLED"] = task_update_enabled.lower() in ["true", "1", "yes", "y"]
        
        if task_update_interactive != "":
            config["TASK_UPDATE_INTERACTIVE"] = task_update_interactive.lower() in ["true", "1", "yes", "y"]
        
        if task_update_storage_path != "":
            config["TASK_UPDATE_STORAGE_PATH"] = task_update_storage_path
        
        if task_update_allow_delete != "":
            config["TASK_UPDATE_ALLOW_DELETE"] = task_update_allow_delete.lower() in ["true", "1", "yes", "y"]
        
        return config

# ============================================================================
# TASK STORAGE MANAGEMENT (shared with other task tools)
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

def _save_tasks(tasks_data: Dict[str, Any], storage_path: str):
    """保存任务到文件"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(storage_path), exist_ok=True)
        
        # 更新时间戳
        tasks_data["updated_at"] = datetime.utcnow().isoformat()
        
        with open(storage_path, 'w') as f:
            json.dump(tasks_data, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save tasks to {storage_path}: {e}")

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

def _validate_parameters(
    task_id: str,
    subject: Optional[str],
    description: Optional[str],
    active_form: Optional[str],
    status: Optional[str],
    metadata: Optional[str]
) -> List[str]:
    """验证TaskUpdateTool参数"""
    errors = []
    
    # 验证任务ID
    if not task_id or not isinstance(task_id, str):
        errors.append("'taskId' must be a non-empty string")
    elif len(task_id) > 100:  # UUID通常为36字符，留有余量
        errors.append("'taskId' must be at most 100 characters")
    
    # 验证主题（如果提供）
    if subject is not None:
        if not isinstance(subject, str):
            errors.append("'subject' must be a string")
        elif len(subject) > 200:
            errors.append("'subject' must be at most 200 characters")
    
    # 验证描述（如果提供）
    if description is not None:
        if not isinstance(description, str):
            errors.append("'description' must be a string")
        elif len(description) > 5000:
            errors.append("'description' must be at most 5000 characters")
    
    # 验证active_form（如果提供）
    if active_form is not None:
        if not isinstance(active_form, str):
            errors.append("'activeForm' must be a string")
        elif len(active_form) > 100:
            errors.append("'activeForm' must be at most 100 characters")
    
    # 验证状态（如果提供）
    if status is not None:
        if not isinstance(status, str):
            errors.append("'status' must be a string")
        elif status not in ["todo", "in_progress", "done", "deleted"]:
            errors.append("'status' must be one of: todo, in_progress, done, deleted")
    
    # 验证metadata（JSON字符串）
    if metadata is not None:
        if not isinstance(metadata, str):
            errors.append("'metadata' must be a JSON string")
        else:
            try:
                parsed = json.loads(metadata)
                if not isinstance(parsed, dict):
                    errors.append("'metadata' must be a JSON object")
            except json.JSONDecodeError as e:
                errors.append(f"Invalid JSON in metadata: {str(e)}")
    
    return errors

def _update_task_in_storage(
    task_id: str,
    subject: Optional[str],
    description: Optional[str],
    active_form: Optional[str],
    status: Optional[str],
    metadata: Optional[Dict],
    config: Dict
) -> tuple[bool, List[str], Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
    """在存储中更新任务"""
    storage_path = config["TASK_UPDATE_STORAGE_PATH"]
    tasks_data = _load_tasks(storage_path)
    
    # 检查任务是否存在
    if task_id not in tasks_data.get("tasks", {}):
        return False, [], None, None
    
    # 获取任务
    task = tasks_data["tasks"][task_id]
    original_task = task.copy()
    
    # 记录更新的字段
    updated_fields = []
    status_change = None
    
    # 记录原始状态（用于状态变更检测）
    original_status = task.get("status", "todo")
    
    # 更新字段
    if subject is not None and subject != task.get("subject"):
        task["subject"] = subject
        updated_fields.append("subject")
    
    if description is not None and description != task.get("description"):
        task["description"] = description
        updated_fields.append("description")
    
    if active_form is not None:
        # 如果active_form是空字符串，则删除该字段
        if active_form == "":
            if "active_form" in task:
                del task["active_form"]
                updated_fields.append("activeForm")  # 使用驼峰格式
        elif active_form != task.get("active_form"):
            task["active_form"] = active_form
            updated_fields.append("activeForm")  # 使用驼峰格式
    
    if status is not None:
        if status == "deleted":
            # 删除任务
            del tasks_data["tasks"][task_id]
            updated_fields.append("deleted")
        elif status != task.get("status"):
            task["status"] = status
            updated_fields.append("status")
            status_change = {
                "from": original_status,
                "to": status
            }
    
    # 更新metadata
    if metadata is not None:
        # 获取当前metadata
        current_metadata = task.get("metadata", {})
        
        # 合并metadata
        for key, value in metadata.items():
            if value is None:
                # 删除键
                if key in current_metadata:
                    del current_metadata[key]
                    updated_fields.append(f"metadata.{key}")
            else:
                # 更新或添加键
                if key not in current_metadata or current_metadata[key] != value:
                    current_metadata[key] = value
                    updated_fields.append(f"metadata.{key}")
        
        # 如果metadata不为空，更新task；否则删除metadata字段
        if current_metadata:
            task["metadata"] = current_metadata
        elif "metadata" in task:
            del task["metadata"]
    
    # 如果没有字段被更新且任务未被删除
    if not updated_fields and task_id in tasks_data["tasks"]:
        return False, ["no changes"], task, None
    
    # 更新任务时间戳
    if task_id in tasks_data["tasks"]:
        task["updated_at"] = datetime.utcnow().isoformat()
    
    # 保存到文件
    _save_tasks(tasks_data, storage_path)
    
    # 如果任务被删除，返回None
    if status == "deleted":
        return True, updated_fields, None, None
    
    return True, updated_fields, task, status_change

def _format_update_for_display(
    success: bool,
    task_id: str,
    updated_fields: List[str],
    task: Optional[Dict[str, Any]],
    status_change: Optional[Dict[str, str]]
) -> str:
    """格式化更新结果用于显示"""
    task_id_short = task_id[:8]  # 使用短ID
    
    if not success:
        return f"\n❌ Update failed for task {task_id_short}"
    
    if "deleted" in updated_fields:
        return f"\n🗑️  Task deleted: {task_id_short}"
    
    if not updated_fields or updated_fields == ["no changes"]:
        return f"\nℹ️  No changes made to task {task_id_short}"
    
    # 构建更新信息
    lines = [f"\n✅ Task updated: {task_id_short}"]
    
    # 添加更新字段
    if updated_fields:
        lines.append(f"   Updated fields: {', '.join(updated_fields)}")
    
    # 添加状态变更
    if status_change:
        from_status = status_change["from"]
        to_status = status_change["to"]
        status_emojis = {
            "todo": "📝",
            "in_progress": "🔄",
            "done": "✅"
        }
        from_emoji = status_emojis.get(from_status, "")
        to_emoji = status_emojis.get(to_status, "")
        lines.append(f"   Status change: {from_emoji} {from_status} → {to_emoji} {to_status}")
    
    # 添加当前任务信息（如果存在）
    if task:
        status_emoji = {
            "todo": "📝",
            "in_progress": "🔄",
            "done": "✅"
        }.get(task.get("status", "todo"), "📝")
        
        lines.append(f"   Current status: {status_emoji} {task.get('status', 'todo')}")
        lines.append(f"   Subject: {task['subject'][:50]}{'...' if len(task['subject']) > 50 else ''}")
    
    return "\n".join(lines)

def _display_update_result(
    success: bool,
    task_id: str,
    updated_fields: List[str],
    task: Optional[Dict[str, Any]],
    status_change: Optional[Dict[str, str]],
    config: Dict
):
    """显示更新结果"""
    if config["TASK_UPDATE_INTERACTIVE"]:
        # 交互模式显示
        formatted = _format_update_for_display(success, task_id, updated_fields, task, status_change)
        print(formatted)
    else:
        # 非交互模式
        task_id_short = task_id[:8]
        if not success:
            print(f"[TASK_UPDATE] Update failed for task: {task_id_short}")
        elif "deleted" in updated_fields:
            print(f"[TASK_UPDATE] Deleted task: {task_id_short}")
        elif not updated_fields or updated_fields == ["no changes"]:
            print(f"[TASK_UPDATE] No changes for task: {task_id_short}")
        else:
            print(f"[TASK_UPDATE] Updated task: {task_id_short} ({', '.join(updated_fields)})")

def _log_task_update_event(
    task_id: str,
    success: bool,
    updated_fields: List[str],
    deleted: bool
):
    """记录任务更新事件（简化版）"""
    try:
        from system.config import log_analytics_event
        log_analytics_event(
            "task_updated",
            {
                "task_id": task_id,
                "success": success,
                "updated_fields": updated_fields,
                "deleted": deleted,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except:
        pass  # 分析是可选的

# ============================================================================
# AI FUNCTION DEFINITION
# ============================================================================

__TASK_UPDATE_FUNCTION__ = function_ai(
    name="task_update",
    description="Update a task by its ID.",
    parameters=parameters_func([
        __TASK_UPDATE_TASK_ID_PROPERTY__,
        __TASK_UPDATE_SUBJECT_PROPERTY__,
        __TASK_UPDATE_DESCRIPTION_PROPERTY__,
        __TASK_UPDATE_ACTIVE_FORM_PROPERTY__,
        __TASK_UPDATE_STATUS_PROPERTY__,
        __TASK_UPDATE_METADATA_PROPERTY__
    ]),
)

tools = [__TASK_UPDATE_FUNCTION__]

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def task_update(
    taskId: str,
    subject: Optional[str] = None,
    description: Optional[str] = None,
    activeForm: Optional[str] = None,
    status: Optional[str] = None,
    metadata: Optional[str] = None
):
    """
    Update a task by its ID.
    
    Args:
        taskId: The ID of the task to update
        subject: New subject for the task
        description: New description for the task
        activeForm: Present continuous form shown in spinner when in_progress
        status: New status for the task (todo, in_progress, done, or 'deleted')
        metadata: Metadata keys to merge into the task as JSON string
        
    Returns:
        Dictionary with update result information
    """
    # 验证参数
    errors = _validate_parameters(taskId, subject, description, activeForm, status, metadata)
    if errors:
        raise ValueError(f"Parameter validation failed: {', '.join(errors)}")
    
    # 获取配置
    config = TaskUpdateConfig.from_env()
    
    # 检查工具是否启用
    if not config["TASK_UPDATE_ENABLED"]:
        raise RuntimeError("Task update tool is not enabled in configuration")
    
    # 检查删除是否允许
    if status == "deleted" and not config["TASK_UPDATE_ALLOW_DELETE"]:
        raise RuntimeError("Task deletion is not allowed in configuration")
    
    # 解析metadata
    parsed_metadata = None
    if metadata is not None:
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in metadata: {str(e)}")
    
    # 检查任务是否存在
    storage_path = config["TASK_UPDATE_STORAGE_PATH"]
    if not _task_exists(taskId, storage_path):
        return {
            "success": False,
            "taskId": taskId,
            "updatedFields": [],
            "error": f"Task not found: {taskId}"
        }
    
    # 更新任务
    try:
        success, updated_fields, updated_task, status_change = _update_task_in_storage(
            task_id=taskId,
            subject=subject,
            description=description,
            active_form=activeForm,
            status=status,
            metadata=parsed_metadata,
            config=config
        )
    except Exception as e:
        return {
            "success": False,
            "taskId": taskId,
            "updatedFields": [],
            "error": f"Update failed: {str(e)}"
        }
    
    # 记录分析事件
    if config["TASK_UPDATE_ANALYTICS_ENABLED"]:
        _log_task_update_event(
            taskId,
            success,
            updated_fields,
            deleted=("deleted" in updated_fields)
        )
    
    # 显示更新结果
    try:
        _display_update_result(success, taskId, updated_fields, updated_task, status_change, config)
    except Exception as e:
        # 回退到简单输出
        print(f"\nTask update completed: {'success' if success else 'failed'}")
    
    # 准备响应数据（与Claude Code兼容）
    response_data = {
        "success": success,
        "taskId": taskId,
        "updatedFields": updated_fields
    }
    
    # 添加错误信息（如果失败）
    if not success:
        response_data["error"] = "Update failed or no changes made"
    
    # 添加状态变更信息
    if status_change:
        response_data["statusChange"] = status_change
    
    # 简化：不支持verificationNudgeNeeded
    response_data["verificationNudgeNeeded"] = False
    
    return response_data

# ============================================================================
# CONFIG GETTER (for testing)
# ============================================================================

def _get_config():
    """获取当前配置（用于测试）"""
    return TaskUpdateConfig.from_env()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ["tools", "task_update", "TaskUpdateConfig", "_get_config"]