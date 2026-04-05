"""
SnipTool - 快照工具
Claude Code工具复刻，简化版本。
用于保存和加载工作区快照/状态。
"""

import json
import time
import os
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime

# ===== 工具实现 =====

def snip_tool(
    action: str = "save",
    name: Optional[str] = None,
    description: Optional[str] = None,
    include_files: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    保存或加载工作区快照。
    
    参数:
        action: 操作类型 - "save"（保存快照）, "load"（加载快照）, "list"（列出快照）
        name: 快照名称（保存时必填）
        description: 快照描述
        include_files: 要包含的文件列表（支持通配符）
        metadata: 额外的元数据
    
    返回:
        JSON字符串格式的快照操作结果
    """
    start_time = time.time()
    
    try:
        # 快照存储目录
        snapshots_dir = os.path.expanduser("~/.aitools/snapshots")
        os.makedirs(snapshots_dir, exist_ok=True)
        
        # 快照索引文件
        index_file = os.path.join(snapshots_dir, "index.json")
        
        # 加载快照索引
        if os.path.exists(index_file):
            with open(index_file, 'r', encoding='utf-8') as f:
                snapshots = json.load(f)
        else:
            snapshots = []
        
        if action == "list":
            # 列出所有快照
            result = {
                "success": True,
                "action": "list",
                "snapshots": snapshots,
                "count": len(snapshots),
                "timestamp": int(time.time() * 1000),
                "durationMs": int((time.time() - start_time) * 1000),
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif action == "save":
            # 保存快照
            if not name:
                return json.dumps({
                    "success": False,
                    "error": "Snapshot name is required for save action",
                    "timestamp": int(time.time() * 1000),
                    "durationMs": int((time.time() - start_time) * 1000),
                }, ensure_ascii=False)
            
            # 检查名称是否已存在
            for snapshot in snapshots:
                if snapshot.get("name") == name:
                    return json.dumps({
                        "success": False,
                        "error": f"Snapshot '{name}' already exists",
                        "timestamp": int(time.time() * 1000),
                        "durationMs": int((time.time() - start_time) * 1000),
                    }, ensure_ascii=False)
            
            # 创建快照
            snapshot_id = f"snap_{int(time.time() * 1000)}"
            snapshot_dir = os.path.join(snapshots_dir, snapshot_id)
            os.makedirs(snapshot_dir, exist_ok=True)
            
            # 保存当前目录的文件（简化版，只保存文件列表）
            current_dir = os.getcwd()
            
            # 收集文件信息
            files_info = []
            if include_files:
                import glob
                for pattern in include_files:
                    for filepath in glob.glob(pattern, recursive=True):
                        if os.path.isfile(filepath):
                            try:
                                file_info = {
                                    "path": filepath,
                                    "size": os.path.getsize(filepath),
                                    "modified": os.path.getmtime(filepath),
                                }
                                files_info.append(file_info)
                            except Exception:
                                pass  # 忽略无法访问的文件
            
            # 创建快照元数据
            snapshot_data = {
                "id": snapshot_id,
                "name": name,
                "description": description or f"Snapshot created at {datetime.now().isoformat()}",
                "created": int(time.time() * 1000),
                "directory": current_dir,
                "files_count": len(files_info),
                "files": files_info,
                "metadata": metadata or {},
            }
            
            # 保存快照数据
            snapshot_file = os.path.join(snapshot_dir, "snapshot.json")
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, ensure_ascii=False, indent=2)
            
            # 更新索引
            snapshots.append({
                "id": snapshot_id,
                "name": name,
                "description": description or "",
                "created": int(time.time() * 1000),
                "files_count": len(files_info),
            })
            
            # 保存索引
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(snapshots, f, ensure_ascii=False, indent=2)
            
            result = {
                "success": True,
                "action": "save",
                "snapshot": {
                    "id": snapshot_id,
                    "name": name,
                    "description": snapshot_data["description"],
                    "created": snapshot_data["created"],
                    "files_count": len(files_info),
                },
                "note": "Simplified snapshot tool - only saves metadata, not file contents",
                "timestamp": int(time.time() * 1000),
                "durationMs": int((time.time() - start_time) * 1000),
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        elif action == "load":
            # 加载快照
            if not name:
                return json.dumps({
                    "success": False,
                    "error": "Snapshot name is required for load action",
                    "timestamp": int(time.time() * 1000),
                    "durationMs": int((time.time() - start_time) * 1000),
                }, ensure_ascii=False)
            
            # 查找快照
            snapshot_info = None
            snapshot_id = None
            for snapshot in snapshots:
                if snapshot.get("name") == name:
                    snapshot_info = snapshot
                    snapshot_id = snapshot["id"]
                    break
            
            if not snapshot_info:
                return json.dumps({
                    "success": False,
                    "error": f"Snapshot '{name}' not found",
                    "timestamp": int(time.time() * 1000),
                    "durationMs": int((time.time() - start_time) * 1000),
                }, ensure_ascii=False)
            
            # 加载快照数据
            snapshot_dir = os.path.join(snapshots_dir, snapshot_id)
            snapshot_file = os.path.join(snapshot_dir, "snapshot.json")
            
            if not os.path.exists(snapshot_file):
                return json.dumps({
                    "success": False,
                    "error": f"Snapshot data for '{name}' not found",
                    "timestamp": int(time.time() * 1000),
                    "durationMs": int((time.time() - start_time) * 1000),
                }, ensure_ascii=False)
            
            with open(snapshot_file, 'r', encoding='utf-8') as f:
                snapshot_data = json.load(f)
            
            result = {
                "success": True,
                "action": "load",
                "snapshot": snapshot_data,
                "note": "Simplified snapshot tool - only loads metadata, not file contents",
                "timestamp": int(time.time() * 1000),
                "durationMs": int((time.time() - start_time) * 1000),
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        else:
            return json.dumps({
                "success": False,
                "error": f"Unknown action: {action}. Supported actions: save, load, list",
                "timestamp": int(time.time() * 1000),
                "durationMs": int((time.time() - start_time) * 1000),
            }, ensure_ascii=False)
            
    except Exception as e:
        # 错误处理
        result = {
            "success": False,
            "error": f"SnipTool operation failed: {str(e)}",
            "timestamp": int(time.time() * 1000),
            "durationMs": int((time.time() - start_time) * 1000),
        }
        return json.dumps(result, ensure_ascii=False)


# ===== 工具注册 =====

# 工具定义
TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "snip",
        "description": "Save, load, or list workspace snapshots.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform: 'save', 'load', or 'list'",
                    "enum": ["save", "load", "list"]
                },
                "name": {
                    "type": "string",
                    "description": "Snapshot name (required for save and load)"
                },
                "description": {
                    "type": "string",
                    "description": "Snapshot description"
                },
                "include_files": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of file patterns to include in snapshot"
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata for snapshot"
                }
            },
            "required": ["action"]
        }
    }
}

# 工具调用映射
TOOL_CALL_MAP = {
    "snip": snip_tool
}

# 工具列表
tools = [TOOL_DEF]

# ===== 模块导出 =====
__all__ = ["tools", "TOOL_CALL_MAP", "snip_tool"]