#!/usr/bin/env python3
"""
TaskCreateTool implementation for AITools (Claude Code compatible version).
Create tasks in the task list.
Simplified version focusing on basic task creation functionality.
"""

import os
import sys
import json
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__TASK_CREATE_SUBJECT_PROPERTY__ = property_param(
    name="subject",
    description="A brief title for the task.",
    t="string",
    required=True
)

__TASK_CREATE_DESCRIPTION_PROPERTY__ = property_param(
    name="description",
    description="What needs to be done.",
    t="string",
    required=True
)

__TASK_CREATE_ACTIVE_FORM_PROPERTY__ = property_param(
    name="activeForm",
    description="Present continuous form shown in spinner when in_progress (e.g., 'Running tests').",
    t="string",
    required=False
)

__TASK_CREATE_METADATA_PROPERTY__ = property_param(
    name="metadata",
    description="Arbitrary metadata to attach to the task.",
    t="string",
    required=False
)

# ============================================================================
# CONFIGURATION CLASS
# ============================================================================

class TaskCreateConfig:
    """TaskCreateTool配置类"""
    
    @staticmethod
    def from_env():
        """从环境变量创建配置"""
        import os
        
        # 读取环境变量，使用空字符串表示使用配置默认值
        task_create_enabled = os.getenv("TASK_CREATE_ENABLED", "")
        task_create_interactive = os.getenv("TASK_CREATE_INTERACTIVE", "")
        task_create_default_status = os.getenv("TASK_CREATE_DEFAULT_STATUS", "")
        task_create_max_tasks = os.getenv("TASK_CREATE_MAX_TASKS", "")
        task_create_analytics_enabled = os.getenv("TASK_CREATE_ANALYTICS_ENABLED", "")
        task_create_storage_path = os.getenv("TASK_CREATE_STORAGE_PATH", "")
        
        config = {
            "TASK_CREATE_ENABLED": True,  # 默认启用
            "TASK_CREATE_INTERACTIVE": True,  # 默认交互模式
            "TASK_CREATE_DEFAULT_STATUS": "todo",  # 默认状态：todo, in_progress, done
            "TASK_CREATE_MAX_TASKS": 1000,  # 最大任务数
            "TASK_CREATE_ANALYTICS_ENABLED": False,  # 默认禁用分析
            "TASK_CREATE_STORAGE_PATH": os.path.join(os.path.expanduser("~"), ".aitools_tasks.json"),  # 任务存储路径
        }
        
        # 覆盖环境变量设置（如果非空）
        if task_create_enabled != "":
            config["TASK_CREATE_ENABLED"] = task_create_enabled.lower() in ["true", "1", "yes", "y"]
        
        if task_create_interactive != "":
            config["TASK_CREATE_INTERACTIVE"] = task_create_interactive.lower() in ["true", "1", "yes", "y"]
        
        if task_create_default_status != "":
            if task_create_default_status in ["todo", "in_progress", "done"]:
                config["TASK_CREATE_DEFAULT_STATUS"] = task_create_default_status
        
        if task_create_max_tasks != "":
            try:
                config["TASK_CREATE_MAX_TASKS"] = int(task_create_max_tasks)
            except ValueError:
                pass  # 保持默认值
        
        if task_create_analytics_enabled != "":
            config["TASK_CREATE_ANALYTICS_ENABLED"] = task_create_analytics_enabled.lower() in ["true", "1", "yes", "y"]
        
        if task_create_storage_path != "":
            config["TASK_CREATE_STORAGE_PATH"] = task_create_storage_path
        
        return config

# ============================================================================
# TASK STORAGE MANAGEMENT
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

def _generate_task_id() -> str:
    """生成任务ID"""
    return str(uuid.uuid4())

def _create_task_in_storage(
    subject: str,
    description: str,
    active_form: Optional[str],
    metadata: Optional[Dict],
    config: Dict
) -> Dict[str, Any]:
    """在存储中创建任务"""
    storage_path = config["TASK_CREATE_STORAGE_PATH"]
    tasks_data = _load_tasks(storage_path)
    
    # 生成任务ID
    task_id = _generate_task_id()
    
    # 创建任务对象
    task = {
        "id": task_id,
        "subject": subject,
        "description": description,
        "status": config["TASK_CREATE_DEFAULT_STATUS"],
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    # 添加可选字段
    if active_form:
        task["active_form"] = active_form
    
    if metadata:
        task["metadata"] = metadata
    
    # 添加到任务列表
    tasks_data["tasks"][task_id] = task
    
    # 保存到文件
    _save_tasks(tasks_data, storage_path)
    
    return task

def _get_task_count(storage_path: str) -> int:
    """获取任务数量"""
    tasks_data = _load_tasks(storage_path)
    return len(tasks_data.get("tasks", {}))

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _validate_parameters(
    subject: str,
    description: str,
    active_form: Optional[str],
    metadata: Optional[str]
) -> List[str]:
    """验证TaskCreateTool参数"""
    errors = []
    
    # 验证主题
    if not subject or not isinstance(subject, str):
        errors.append("'subject' must be a non-empty string")
    elif len(subject) > 200:
        errors.append("'subject' must be at most 200 characters")
    
    # 验证描述
    if not description or not isinstance(description, str):
        errors.append("'description' must be a non-empty string")
    elif len(description) > 5000:
        errors.append("'description' must be at most 5000 characters")
    
    # 验证active_form
    if active_form is not None:
        if not isinstance(active_form, str):
            errors.append("'active_form' must be a string")
        elif len(active_form) > 100:
            errors.append("'active_form' must be at most 100 characters")
    
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

def _format_task_for_display(task: Dict[str, Any]) -> str:
    """格式化任务用于显示"""
    task_id_short = task["id"][:8]  # 使用短ID
    status_emoji = {
        "todo": "📝",
        "in_progress": "🔄",
        "done": "✅"
    }.get(task.get("status", "todo"), "📝")
    
    lines = [
        f"\n{status_emoji} Task Created: {task['subject']}",
        f"   ID: {task_id_short}",
        f"   Description: {task['description'][:100]}{'...' if len(task['description']) > 100 else ''}",
    ]
    
    if "active_form" in task:
        lines.append(f"   Active Form: {task['active_form']}")
    
    lines.append(f"   Status: {task.get('status', 'todo')}")
    lines.append(f"   Created: {task['created_at'][:19]}")  # 只显示日期和时间
    
    return "\n".join(lines)

def _display_task_creation(
    subject: str,
    description: str,
    active_form: Optional[str],
    task: Dict[str, Any],
    config: Dict
):
    """显示任务创建信息"""
    if config["TASK_CREATE_INTERACTIVE"]:
        # 交互模式显示
        formatted = _format_task_for_display(task)
        print(formatted)
        
        # 显示任务总数
        task_count = _get_task_count(config["TASK_CREATE_STORAGE_PATH"])
        print(f"\n📊 Total tasks in system: {task_count}")
    else:
        # 非交互模式
        task_id_short = task["id"][:8]
        print(f"[TASK_CREATE] Created task: {task['subject']} (ID: {task_id_short})")

def _log_task_creation_event(task: Dict[str, Any]):
    """记录任务创建事件（简化版）"""
    try:
        from system.config import log_analytics_event
        log_analytics_event(
            "task_created",
            {
                "task_id": task["id"],
                "subject_length": len(task["subject"]),
                "description_length": len(task["description"]),
                "has_active_form": "active_form" in task,
                "has_metadata": "metadata" in task
            }
        )
    except:
        pass  # 分析是可选的

def _execute_task_created_hooks(task: Dict[str, Any]):
    """执行任务创建钩子（简化版）"""
    # 在实际实现中，这里应该执行注册的钩子
    # 这里我们只是记录一下
    try:
        # 尝试导入钩子系统
        from system.hooks import execute_task_created_hooks as execute_hooks
        execute_hooks(task)
    except ImportError:
        # 钩子系统不存在，跳过
        pass

# ============================================================================
# AI FUNCTION DEFINITION
# ============================================================================

__TASK_CREATE_FUNCTION__ = function_ai(
    name="task_create",
    description="Create a task in the task list.",
    parameters=parameters_func([
        __TASK_CREATE_SUBJECT_PROPERTY__,
        __TASK_CREATE_DESCRIPTION_PROPERTY__,
        __TASK_CREATE_ACTIVE_FORM_PROPERTY__,
        __TASK_CREATE_METADATA_PROPERTY__
    ]),
)

tools = [__TASK_CREATE_FUNCTION__]

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def task_create(
    subject: str,
    description: str,
    activeForm: Optional[str] = None,
    metadata: Optional[str] = None
):
    """
    Create a task in the task list.
    
    Args:
        subject: A brief title for the task
        description: What needs to be done
        activeForm: Present continuous form shown in spinner when in_progress
        metadata: Arbitrary metadata as JSON string
        
    Returns:
        Dictionary with created task information
    """
    # 验证参数
    errors = _validate_parameters(subject, description, activeForm, metadata)
    if errors:
        raise ValueError(f"Parameter validation failed: {', '.join(errors)}")
    
    # 获取配置
    config = TaskCreateConfig.from_env()
    
    # 检查任务创建是否启用
    if not config["TASK_CREATE_ENABLED"]:
        raise RuntimeError("Task create tool is not enabled in configuration")
    
    # 解析metadata
    parsed_metadata = None
    if metadata is not None:
        try:
            parsed_metadata = json.loads(metadata)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in metadata: {str(e)}")
    
    # 检查任务数量限制
    task_count = _get_task_count(config["TASK_CREATE_STORAGE_PATH"])
    if task_count >= config["TASK_CREATE_MAX_TASKS"]:
        raise RuntimeError(f"Maximum task limit reached ({config['TASK_CREATE_MAX_TASKS']} tasks)")
    
    # 创建任务
    try:
        task = _create_task_in_storage(
            subject=subject,
            description=description,
            active_form=activeForm,
            metadata=parsed_metadata,
            config=config
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create task: {str(e)}")
    
    # 显示任务创建信息
    try:
        _display_task_creation(subject, description, activeForm, task, config)
    except Exception as e:
        # 回退到简单输出
        print(f"\nTask created: {subject} (ID: {task['id'][:8]})")
    
    # 记录分析事件
    if config["TASK_CREATE_ANALYTICS_ENABLED"]:
        _log_task_creation_event(task)
    
    # 执行任务创建钩子
    _execute_task_created_hooks(task)
    
    # 准备响应数据
    response_data = {
        "task": {
            "id": task["id"],
            "subject": task["subject"]
        }
    }
    
    return response_data

# ============================================================================
# CONFIG GETTER (for testing)
# ============================================================================

def _get_config():
    """获取当前配置（用于测试）"""
    return TaskCreateConfig.from_env()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ["tools", "task_create", "TaskCreateConfig", "_get_config"]