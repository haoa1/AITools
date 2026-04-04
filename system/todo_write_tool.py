"""
Claude Code兼容的TodoWriteTool简化实现。

基于Claude Code的TodoWriteTool.ts（115行TypeScript代码）分析：
- 输入：todos数组（包含content、status、activeForm字段）
- 输出：oldTodos（更新前的待办事项）、newTodos（更新后的待办事项）、verificationNudgeNeeded（可选）
- 功能：管理会话任务清单，帮助跟踪进度和组织复杂任务

简化策略：
1. 使用简单的JSON文件存储待办事项状态，替代Claude Code的应用状态管理
2. 简化verificationNudgeNeeded逻辑，只实现基本功能
3. 保持与Claude Code接口的兼容性
4. 使用内存缓存提高性能，减少文件IO

注意：这是简化版本，不包含复杂的代理ID管理和会话状态管理。
"""

import os
import json
import time
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from base import function_ai, parameters_func, property_param

# ===== 数据结构定义 =====

@dataclass
class TodoItem:
    """单个待办事项"""
    content: str
    status: str  # 'pending', 'in_progress', 'completed'
    activeForm: str

@dataclass
class TodoList:
    """待办事项列表"""
    items: List[TodoItem]

# ===== 输入参数定义 =====

# todos: 必需，待办事项数组
# 在Claude Code中，TodoListSchema是一个包含TodoItemSchema的数组
# TodoItemSchema包含：content（字符串，非空）、status（枚举）、activeForm（字符串，非空）

# 由于AITools的参数系统不支持复杂嵌套结构，我们需要将todos作为JSON字符串传递
# 然后在函数内部解析

__TODOS_PROPERTY__ = property_param(
    name="todos",
    description="The updated todo list as JSON string. Each todo item should have 'content', 'status' ('pending', 'in_progress', or 'completed'), and 'activeForm' fields.",
    t="string",
    required=True,
)

# ===== 工具函数定义 =====

__TODO_WRITE_FUNCTION__ = function_ai(
    name="todo_write",
    description="Manage session task checklist - create and update todo lists for tracking progress on complex tasks (simplified version of Claude Code's TodoWriteTool).",
    parameters=parameters_func([
        __TODOS_PROPERTY__,
    ]),
)

tools = [__TODO_WRITE_FUNCTION__]

# ===== 存储管理 =====

class TodoStorage:
    """待办事项存储管理（简化版本）"""
    
    def __init__(self, storage_file: str = ".todo_storage.json"):
        self.storage_file = storage_file
        self._cache = {}
        self._load_storage()
    
    def _load_storage(self) -> None:
        """从文件加载存储数据"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._cache = {}
        else:
            self._cache = {}
    
    def _save_storage(self) -> None:
        """保存存储数据到文件"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except IOError:
            # 如果无法保存到文件，只使用内存缓存
            pass
    
    def get_todos(self, key: str = "default") -> List[Dict[str, Any]]:
        """获取指定键的待办事项"""
        # 每次获取都重新加载，确保测试隔离性
        self._load_storage()
        return self._cache.get(key, [])
    
    def set_todos(self, key: str, todos: List[Dict[str, Any]]) -> None:
        """设置指定键的待办事项"""
        self._cache[key] = todos
        self._save_storage()

# 全局存储实例
_todo_storage = TodoStorage()

# ===== 核心实现函数 =====

def _parse_todos_input(todos_input: str) -> List[Dict[str, Any]]:
    """解析todos输入（JSON字符串）"""
    try:
        todos = json.loads(todos_input)
        if not isinstance(todos, list):
            raise ValueError("todos must be a list")
        
        # 验证每个待办事项的结构
        validated_todos = []
        for i, item in enumerate(todos):
            if not isinstance(item, dict):
                raise ValueError(f"Todo item at index {i} must be an object")
            
            # 必需字段检查
            if "content" not in item or not item["content"]:
                raise ValueError(f"Todo item at index {i} must have non-empty 'content'")
            
            if "status" not in item:
                raise ValueError(f"Todo item at index {i} must have 'status'")
            
            # 验证状态值
            status = item["status"]
            if status not in ["pending", "in_progress", "completed"]:
                raise ValueError(f"Todo item at index {i} has invalid status '{status}'. Must be 'pending', 'in_progress', or 'completed'")
            
            if "activeForm" not in item or not item["activeForm"]:
                raise ValueError(f"Todo item at index {i} must have non-empty 'activeForm'")
            
            validated_todos.append({
                "content": str(item["content"]),
                "status": str(item["status"]),
                "activeForm": str(item["activeForm"])
            })
        
        return validated_todos
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        raise ValueError(f"Error parsing todos: {e}")

def _check_verification_nudge_needed(todos: List[Dict[str, Any]]) -> bool:
    """
    检查是否需要验证提醒（简化版本）
    
    在Claude Code中，当满足以下条件时设置verificationNudgeNeeded：
    1. 特性标记启用
    2. 主线程代理（无agentId）
    3. 所有待办事项已完成
    4. 待办事项数量>=3
    5. 没有包含"verif"的待办事项
    
    简化：只检查基本条件3-5
    """
    # 检查是否所有待办事项已完成
    all_done = all(item["status"] == "completed" for item in todos)
    
    # 检查待办事项数量>=3
    has_enough_items = len(todos) >= 3
    
    # 检查是否没有包含"verif"的待办事项（不区分大小写）
    has_verification_item = any("verif" in item["content"].lower() for item in todos)
    
    # 简化条件：所有完成、数量>=3、没有验证项
    return all_done and has_enough_items and not has_verification_item

def todo_write(todos: str) -> str:
    """
    更新待办事项列表（Claude Code TodoWriteTool的简化版本）。
    
    参数:
        todos: JSON字符串格式的待办事项列表，每个项目包含content、status、activeForm字段
    
    返回:
        JSON格式的结果，包含oldTodos、newTodos和可选的verificationNudgeNeeded
    """
    start_time = time.time()
    
    try:
        # 1. 解析输入
        parsed_todos = _parse_todos_input(todos)
        
        # 2. 获取旧的待办事项（使用默认键）
        old_todos = _todo_storage.get_todos("default")
        
        # 3. 检查是否所有待办事项已完成
        all_done = all(item["status"] == "completed" for item in parsed_todos)
        
        # 4. 更新存储（如果全部完成则清空，否则保存）
        if all_done:
            new_stored_todos = []
        else:
            new_stored_todos = parsed_todos
        
        _todo_storage.set_todos("default", new_stored_todos)
        
        # 5. 检查是否需要验证提醒
        verification_nudge_needed = _check_verification_nudge_needed(parsed_todos)
        
        # 6. 构建结果
        result = {
            "oldTodos": old_todos,
            "newTodos": parsed_todos,
        }
        
        if verification_nudge_needed:
            result["verificationNudgeNeeded"] = True
        
        # 7. 添加执行时间（Claude Code兼容）
        result["durationMs"] = int((time.time() - start_time) * 1000)
        
        return json.dumps(result, ensure_ascii=False)
        
    except ValueError as e:
        # 输入验证错误
        error_result = {
            "error": str(e),
            "oldTodos": [],
            "newTodos": [],
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(error_result, ensure_ascii=False)
    
    except Exception as e:
        # 其他错误
        error_result = {
            "error": f"Unexpected error: {str(e)}",
            "oldTodos": [],
            "newTodos": [],
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(error_result, ensure_ascii=False)

# ===== 工具注册 =====
__all__ = ["tools", "todo_write"]