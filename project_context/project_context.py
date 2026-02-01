"""
Project Context Management Module for AITools.
Provides tools for detecting, saving, and loading project context across sessions.
Enables AI to continue work where it left off in any project.
"""

from base import function_ai, parameters_func, property_param
import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import datetime
import subprocess
import re
import ast

# ============================================================================
# Project Context Tool Parameter Definitions
# ============================================================================

__PROJECT_PROPERTY_PATH__ = property_param(
    name="project_path",
    description="Path to the project directory (default: current directory).",
    t="string"
)

__PROJECT_PROPERTY_NAME__ = property_param(
    name="project_name",
    description="Name of the project.",
    t="string"
)

__PROJECT_PROPERTY_DESCRIPTION__ = property_param(
    name="description",
    description="Description of the project or plan.",
    t="string"
)

__PROJECT_PROPERTY_CONTEXT_DATA__ = property_param(
    name="context_data",
    description="Context data to save (JSON string).",
    t="string"
)

__PROJECT_PROPERTY_PHASES__ = property_param(
    name="phases",
    description="Development phases (list of dicts).",
    t="array"
)

__PROJECT_PROPERTY_TASKS__ = property_param(
    name="tasks",
    description="Development tasks (list of dicts).",
    t="array"
)

__PROJECT_PROPERTY_TASK_ID__ = property_param(
    name="task_id",
    description="ID of the task to update.",
    t="integer"
)

__PROJECT_PROPERTY_STATUS__ = property_param(
    name="status",
    description="New status for the task.",
    t="string"
)

__PROJECT_PROPERTY_HOURS__ = property_param(
    name="actual_hours",
    description="Actual hours spent on task.",
    t="number",
    required=False
)

__PROJECT_PROPERTY_LOG_TEXT__ = property_param(
    name="log_text",
    description="Text for progress log.",
    t="string"
)

__PROJECT_PROPERTY_MAX_DEPTH__ = property_param(
    name="max_depth",
    description="Maximum depth to search for projects.",
    t="integer",
    required=False
)

__PROJECT_PROPERTY_RECURSIVE__ = property_param(
    name="recursive",
    description="Search recursively for projects.",
    t="boolean",
    required=False
)

__PROJECT_PROPERTY_MESSAGES__ = property_param(
    name="messages",
    description="The conversation messages to optimize. System will handle this automatically, you do not need to provide it.",
    t="array"
)

__PROJECT_PROPERTY_COMPLETED_FEATURE__ = property_param(
    name="completed_feature",
    description="Description of the completed atomic feature.",
    t="string"
)

__PROJECT_PROPERTY_NEXT_FEATURE__ = property_param(
    name="next_feature",
    description="Description of the next atomic feature to work on.",
    t="string",
    required=False
)

# ============================================================================
# Project Context Tool Function Definitions
# ============================================================================

__DETECT_PROJECT_FUNCTION__ = function_ai(
    name="detect_project",
    description="Detect project information from current or specified directory.",
    parameters=parameters_func([__PROJECT_PROPERTY_PATH__])
)

__SAVE_PROJECT_CONTEXT_FUNCTION__ = function_ai(
    name="save_project_context",
    description="Save project context to .aitools_context.json file.",
    parameters=parameters_func([
        __PROJECT_PROPERTY_PATH__,
        __PROJECT_PROPERTY_CONTEXT_DATA__
    ])
)

__LOAD_PROJECT_CONTEXT_FUNCTION__ = function_ai(
    name="load_project_context",
    description="Load project context from .aitools_context.json file.",
    parameters=parameters_func([__PROJECT_PROPERTY_PATH__])
)

__LIST_PROJECTS_FUNCTION__ = function_ai(
    name="list_projects",
    description="List all projects with saved context in the directory tree.",
    parameters=parameters_func([
        __PROJECT_PROPERTY_PATH__,
        __PROJECT_PROPERTY_RECURSIVE__,
        __PROJECT_PROPERTY_MAX_DEPTH__
    ])
)

__CREATE_DEVELOPMENT_PLAN_FUNCTION__ = function_ai(
    name="create_development_plan",
    description="Create a development plan for a project.",
    parameters=parameters_func([
        __PROJECT_PROPERTY_PATH__,
        __PROJECT_PROPERTY_NAME__,
        __PROJECT_PROPERTY_DESCRIPTION__,
        __PROJECT_PROPERTY_PHASES__,
        __PROJECT_PROPERTY_TASKS__
    ])
)

__UPDATE_TASK_STATUS_FUNCTION__ = function_ai(
    name="update_task_status",
    description="Update the status of a development task.",
    parameters=parameters_func([
        __PROJECT_PROPERTY_PATH__,
        __PROJECT_PROPERTY_TASK_ID__,
        __PROJECT_PROPERTY_STATUS__,
        __PROJECT_PROPERTY_HOURS__
    ])
)

__GET_PROJECT_SUMMARY_FUNCTION__ = function_ai(
    name="get_project_summary",
    description="Get a summary of project context and development plan.",
    parameters=parameters_func([__PROJECT_PROPERTY_PATH__])
)

__ADD_PROGRESS_LOG_FUNCTION__ = function_ai(
    name="add_progress_log",
    description="Add a progress log entry to a task.",
    parameters=parameters_func([
        __PROJECT_PROPERTY_PATH__,
        __PROJECT_PROPERTY_TASK_ID__,
        __PROJECT_PROPERTY_LOG_TEXT__
    ])
)

__FEATURE_CONTEXT_OPTIMIZE_FUNCTION__ = function_ai(
    name="optimize_feature_context",
    description="After completing an atomic feature, optimize conversation context by clearing intermediate data and loading TODO.md for next feature.",
    parameters=parameters_func([
        __PROJECT_PROPERTY_MESSAGES__,
        __PROJECT_PROPERTY_COMPLETED_FEATURE__,
        __PROJECT_PROPERTY_NEXT_FEATURE__
    ])
)

tools = [
    __DETECT_PROJECT_FUNCTION__,
    __SAVE_PROJECT_CONTEXT_FUNCTION__,
    __LOAD_PROJECT_CONTEXT_FUNCTION__,
    __LIST_PROJECTS_FUNCTION__,
    __CREATE_DEVELOPMENT_PLAN_FUNCTION__,
    __UPDATE_TASK_STATUS_FUNCTION__,
    __GET_PROJECT_SUMMARY_FUNCTION__,
    __ADD_PROGRESS_LOG_FUNCTION__,
    __FEATURE_CONTEXT_OPTIMIZE_FUNCTION__,
]

# ============================================================================
# Project Context 核心实现
# ============================================================================

class ProjectDetector:
    """Detect project information from directory."""
    
    def __init__(self):
        self.project_types = {
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
            'nodejs': ['package.json', 'package-lock.json', 'yarn.lock'],
            'java': ['pom.xml', 'build.gradle', 'build.gradle.kts'],
            'go': ['go.mod', 'go.sum'],
            'rust': ['Cargo.toml', 'Cargo.lock'],
            'docker': ['Dockerfile', 'docker-compose.yml'],
            'git': ['.git'],  # Git repository
        }
    
    def detect_from_path(self, path: str = ".") -> Dict[str, Any]:
        """Detect project information from path."""
        path = Path(path).resolve()
        
        if not path.exists():
            return {"error": f"Path does not exist: {path}"}
        
        result = {
            "path": str(path),
            "exists": True,
            "is_directory": path.is_dir(),
            "project_type": "unknown",
            "project_name": path.name,
            "git_info": None,
            "project_files": {},
            "detected_at": datetime.datetime.now().isoformat()
        }
        
        # Check if it's a directory
        if not path.is_dir():
            # Check parent directories
            parent = path.parent
            if parent.exists() and parent.is_dir():
                return self.detect_from_path(str(parent))
            return result
        
        # Check for git repository
        git_info = self._detect_git_repo(path)
        if git_info:
            result["git_info"] = git_info
            result["project_type"] = "git"
        
        # Check for project type files
        detected_types = []
        for ptype, files in self.project_types.items():
            for file in files:
                file_path = path / file
                if file_path.exists():
                    detected_types.append(ptype)
                    result["project_files"][file] = str(file_path)
                    break
        
        # If multiple types detected, choose the most specific
        if detected_types:
            if 'git' in detected_types and len(detected_types) > 1:
                # Remove git if other types found
                detected_types.remove('git')
            if detected_types:
                result["project_type"] = detected_types[0]
        
        # Get additional information based on project type
        if result["project_type"] == "python":
            result.update(self._detect_python_project(path))
        elif result["project_type"] == "nodejs":
            result.update(self._detect_nodejs_project(path))
        
        return result
    
    def _detect_git_repo(self, path: Path) -> Optional[Dict[str, Any]]:
        """Detect git repository information."""
        git_dir = path / ".git"
        if git_dir.exists() and git_dir.is_dir():
            try:
                # Get git remote URL
                result = subprocess.run(
                    ['git', 'config', '--get', 'remote.origin.url'],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                remote_url = result.stdout.strip() if result.returncode == 0 else None
                
                # Get current branch
                result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                current_branch = result.stdout.strip() if result.returncode == 0 else None
                
                return {
                    "is_git_repo": True,
                    "remote_url": remote_url,
                    "current_branch": current_branch,
                    "git_dir": str(git_dir),
                }
            except (subprocess.SubprocessError, FileNotFoundError):
                return {"is_git_repo": True, "git_dir": str(git_dir)}
        
        # Check parent directories
        if path.parent != path:
            return self._detect_git_repo(path.parent)
        
        return None
    
    def _detect_python_project(self, path: Path) -> Dict[str, Any]:
        """Detect Python project specific information."""
        info = {}
        
        # Check for Python version files
        python_version_file = path / ".python-version"
        if python_version_file.exists():
            try:
                with open(python_version_file, 'r') as f:
                    info["python_version"] = f.read().strip()
            except:
                pass
        
        # Check for virtual environment
        venv_candidates = ['venv', 'env', '.venv', '.env']
        for venv in venv_candidates:
            venv_path = path / venv
            if venv_path.exists() and venv_path.is_dir():
                info["virtualenv"] = str(venv_path)
                break
        
        # Try to read requirements.txt
        req_file = path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    info["requirements_count"] = len(requirements)
            except:
                pass
        
        return info
    
    def _detect_nodejs_project(self, path: Path) -> Dict[str, Any]:
        """Detect Node.js project specific information."""
        info = {}
        
        # Try to read package.json
        pkg_file = path / "package.json"
        if pkg_file.exists():
            try:
                with open(pkg_file, 'r') as f:
                    package_data = json.load(f)
                    info["package_name"] = package_data.get("name", "unknown")
                    info["package_version"] = package_data.get("version", "unknown")
                    info["dependencies_count"] = len(package_data.get("dependencies", {}))
                    info["dev_dependencies_count"] = len(package_data.get("devDependencies", {}))
            except:
                pass
        
        return info

class ProjectContextManager:
    """Manage project context files."""
    
    def __init__(self, context_filename: str = ".aitools_context.json"):
        self.context_filename = context_filename
        self.detector = ProjectDetector()
    
    def save_context(self, project_path: str, context_data: Dict) -> Dict[str, Any]:
        """Save project context to file."""
        project_path = Path(project_path).resolve()
        context_file = project_path / self.context_filename
        
        # Ensure project path exists
        if not project_path.exists():
            return {"error": f"Project path does not exist: {project_path}"}
        
        # Add metadata
        context_data["_metadata"] = {
            "saved_at": datetime.datetime.now().isoformat(),
            "context_version": "1.0",
            "project_path": str(project_path),
            "context_file": str(context_file),
        }
        
        try:
            # Create backup if file exists
            if context_file.exists():
                backup_file = project_path / f"{self.context_filename}.backup"
                context_file.rename(backup_file)
            
            # Write context file
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, ensure_ascii=False, indent=2)
            
            return {
                "success": True,
                "message": f"Context saved to {context_file}",
                "context_file": str(context_file),
                "data_keys": list(context_data.keys()),
            }
        except Exception as e:
            return {"error": f"Failed to save context: {str(e)}"}
    
    def load_context(self, project_path: str) -> Dict[str, Any]:
        """Load project context from file."""
        project_path = Path(project_path).resolve()
        context_file = project_path / self.context_filename
        
        if not context_file.exists():
            # Try to find context file in parent directories
            for parent in project_path.parents:
                parent_context = parent / self.context_filename
                if parent_context.exists():
                    context_file = parent_context
                    break
            
            if not context_file.exists():
                return {"error": f"No context file found: {self.context_filename}"}
        
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
            
            return {
                "success": True,
                "message": f"Context loaded from {context_file}",
                "context_file": str(context_file),
                "data": context_data,
            }
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON in context file: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to load context: {str(e)}"}
    
    def list_projects(self, root_path: str = ".", recursive: bool = True, max_depth: int = 3) -> Dict[str, Any]:
        """List all projects with context files in directory tree."""
        root_path = Path(root_path).resolve()
        
        if not root_path.exists() or not root_path.is_dir():
            return {"error": f"Root path does not exist or is not a directory: {root_path}"}
        
        projects = []
        
        def scan_directory(current_path: Path, current_depth: int):
            if current_depth > max_depth:
                return
            
            # Check for context file
            context_file = current_path / self.context_filename
            if context_file.exists():
                try:
                    with open(context_file, 'r', encoding='utf-8') as f:
                        context_data = json.load(f)
                    
                    # Get project info
                    project_info = self.detector.detect_from_path(str(current_path))
                    
                    projects.append({
                        "path": str(current_path),
                        "name": current_path.name,
                        "context_file": str(context_file),
                        "project_type": project_info.get("project_type", "unknown"),
                        "has_git": bool(project_info.get("git_info")),
                        "context_data_keys": list(context_data.keys()) if isinstance(context_data, dict) else [],
                        "detected_at": project_info.get("detected_at"),
                    })
                except:
                    # Skip invalid context files
                    pass
            
            # Recursively scan subdirectories
            if recursive and current_depth < max_depth:
                try:
                    for item in current_path.iterdir():
                        if item.is_dir() and not item.name.startswith('.') and item.name != '__pycache__':
                            scan_directory(item, current_depth + 1)
                except PermissionError:
                    # Skip directories without permission
                    pass
        
        scan_directory(root_path, 0)
        
        return {
            "success": True,
            "root_path": str(root_path),
            "recursive": recursive,
            "max_depth": max_depth,
            "projects_found": len(projects),
            "projects": projects,
        }

class DevelopmentPlanManager:
    """Manage development plans within project context."""
    
    def __init__(self, context_manager: ProjectContextManager):
        self.context_manager = context_manager
    
    def create_plan(self, project_path: str, project_name: str, description: str, 
                   phases: List[Dict], tasks: List[Dict]) -> Dict[str, Any]:
        """Create a development plan for a project."""
        # Load existing context or create new
        context_result = self.context_manager.load_context(project_path)
        if "error" in context_result and "No context file found" in context_result["error"]:
            context_data = {}
        elif "data" in context_result:
            context_data = context_result["data"]
        else:
            return {"error": f"Failed to load context: {context_result.get('error', 'Unknown error')}"}
        
        # Create or update development plan
        development_plan = {
            "project_name": project_name,
            "description": description,
            "created_at": datetime.datetime.now().isoformat(),
            "last_updated": datetime.datetime.now().isoformat(),
            "phases": phases,
            "tasks": tasks,
            "next_task_id": 1,
            "task_status": {
                "pending": len(tasks),
                "in_progress": 0,
                "completed": 0,
            }
        }
        
        # Initialize task tracking
        for i, task in enumerate(tasks, 1):
            task["id"] = i
            task["status"] = "pending"
            task["created_at"] = datetime.datetime.now().isoformat()
            task["progress_logs"] = []
        
        context_data["development_plan"] = development_plan
        
        # Save updated context
        save_result = self.context_manager.save_context(project_path, context_data)
        if "error" in save_result:
            return save_result
        
        return {
            "success": True,
            "message": f"Development plan created for {project_name}",
            "plan_summary": {
                "phases_count": len(phases),
                "tasks_count": len(tasks),
                "project_name": project_name,
                "description": description,
            }
        }
    
    def update_task_status(self, project_path: str, task_id: int, status: str, 
                          actual_hours: Optional[float] = None) -> Dict[str, Any]:
        """Update task status in development plan."""
        context_result = self.context_manager.load_context(project_path)
        if "error" in context_result:
            return context_result
        
        context_data = context_result["data"]
        
        if "development_plan" not in context_data:
            return {"error": "No development plan found in context"}
        
        plan = context_data["development_plan"]
        
        # Find and update task
        task_found = False
        for task in plan["tasks"]:
            if task.get("id") == task_id:
                old_status = task.get("status", "pending")
                task["status"] = status
                task["last_updated"] = datetime.datetime.now().isoformat()
                
                if actual_hours is not None:
                    task["actual_hours"] = actual_hours
                
                # Update progress log
                log_entry = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "action": "status_change",
                    "old_status": old_status,
                    "new_status": status,
                    "message": f"Task status changed from {old_status} to {status}"
                }
                # Initialize progress_logs if it doesn't exist
                if "progress_logs" not in task:
                    task["progress_logs"] = []
                task["progress_logs"].append(log_entry)
                
                task_found = True
                break
        
        if not task_found:
            return {"error": f"Task with ID {task_id} not found"}
        
        # Update task status counts
        status_counts = {"pending": 0, "in_progress": 0, "completed": 0}
        for task in plan["tasks"]:
            current_status = task.get("status", "pending")
            if current_status in status_counts:
                status_counts[current_status] += 1
        
        plan["task_status"] = status_counts
        plan["last_updated"] = datetime.datetime.now().isoformat()
        
        # Save updated context
        save_result = self.context_manager.save_context(project_path, context_data)
        if "error" in save_result:
            return save_result
        
        return {
            "success": True,
            "message": f"Task {task_id} status updated to {status}",
            "task_id": task_id,
            "new_status": status,
            "status_counts": status_counts,
        }
    
    def add_progress_log(self, project_path: str, task_id: int, log_text: str) -> Dict[str, Any]:
        """Add progress log to a task."""
        context_result = self.context_manager.load_context(project_path)
        if "error" in context_result:
            return context_result
        
        context_data = context_result["data"]
        
        if "development_plan" not in context_data:
            return {"error": "No development plan found in context"}
        
        plan = context_data["development_plan"]
        
        # Find task
        task_found = False
        for task in plan["tasks"]:
            if task.get("id") == task_id:
                log_entry = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "action": "progress_log",
                    "message": log_text,
                }
                # Initialize progress_logs if it doesn't exist
                if "progress_logs" not in task:
                    task["progress_logs"] = []
                task["progress_logs"].append(log_entry)
                task["last_updated"] = datetime.datetime.now().isoformat()
                task_found = True
                break
        
        if not task_found:
            return {"error": f"Task with ID {task_id} not found"}
        
        plan["last_updated"] = datetime.datetime.now().isoformat()
        
        # Save updated context
        save_result = self.context_manager.save_context(project_path, context_data)
        if "error" in save_result:
            return save_result
        
        return {
            "success": True,
            "message": f"Progress log added to task {task_id}",
            "task_id": task_id,
            "log_text": log_text,
        }
    
    def get_summary(self, project_path: str) -> Dict[str, Any]:
        """Get summary of project context and development plan."""
        context_result = self.context_manager.load_context(project_path)
        if "error" in context_result:
            return context_result
        
        context_data = context_result["data"]
        
        # Get project info
        project_info = self.context_manager.detector.detect_from_path(project_path)
        
        summary = {
            "project_info": {
                "path": project_info.get("path"),
                "name": project_info.get("project_name"),
                "type": project_info.get("project_type"),
                "has_git": bool(project_info.get("git_info")),
            },
            "context_info": {
                "has_context": True,
                "context_file": context_result.get("context_file"),
                "data_keys": list(context_data.keys()),
            }
        }
        
        # Add development plan summary if available
        if "development_plan" in context_data:
            plan = context_data["development_plan"]
            tasks = plan.get("tasks", [])
            
            # Calculate statistics
            status_counts = plan.get("task_status", {"pending": 0, "in_progress": 0, "completed": 0})
            total_tasks = sum(status_counts.values())
            completed_percentage = (status_counts["completed"] / total_tasks * 100) if total_tasks > 0 else 0
            
            # Get next pending task
            next_task = None
            for task in tasks:
                if task.get("status") == "pending":
                    next_task = task
                    break
            
            summary["development_plan"] = {
                "project_name": plan.get("project_name"),
                "description": plan.get("description"),
                "created_at": plan.get("created_at"),
                "last_updated": plan.get("last_updated"),
                "phases_count": len(plan.get("phases", [])),
                "tasks_count": total_tasks,
                "status_counts": status_counts,
                "completion_percentage": round(completed_percentage, 1),
                "next_task": next_task,
            }
        
        return summary

# ============================================================================
# 全局实例
# ============================================================================

_context_manager = ProjectContextManager()
_plan_manager = DevelopmentPlanManager(_context_manager)
_detector = ProjectDetector()

# ============================================================================
# Project Context Tool Function Implementations
# ============================================================================

def detect_project(project_path: str = ".") -> str:
    '''
    Detect project information from current or specified directory.

    :param project_path: Path to the project directory
    :type project_path: str
    :return: Project detection result
    :rtype: str
    '''
    try:
        result = _detector.detect_from_path(project_path)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Failed to detect project: {e}"

def save_project_context(project_path: str = ".", context_data: str = "{}") -> str:
    '''
    Save project context to .aitools_context.json file

    :param project_path: Path to the project directory
    :type project_path: str
    :param context_data: Context data (JSON string)
    :type context_data: str
    :return: Save operation result
    :rtype: str
    '''
    try:
        # Parse context data
        data = json.loads(context_data)
        
        # Save context
        result = _context_manager.save_context(project_path, data)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except json.JSONDecodeError as e:
        return f"Invalid JSON data: {e}"
    except Exception as e:
        return f"Failed to save project context: {e}"

def load_project_context(project_path: str = ".") -> str:
    '''
    Load project context from .aitools_context.json file

    :param project_path: Path to the project directory
    :type project_path: str
    :return: Load operation result
    :rtype: str
    '''
    try:
        result = _context_manager.load_context(project_path)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Failed to load project context: {e}"

def list_projects(project_path: str = ".", recursive: bool = True, max_depth: int = 3) -> str:
    '''
    List all projects with saved context in the directory tree

    :param project_path: Root directory path
    :type project_path: str
    :param recursive: Whether to search recursively
    :type recursive: bool
    :param max_depth: Maximum search depth
    :type max_depth: int
    :return: List of projects
    :return: 项目列表
    :rtype: str
    '''
    try:
        result = _context_manager.list_projects(project_path, recursive, max_depth)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Failed to list projects: {e}"

def create_development_plan(project_path: str = ".", project_name: str = None, 
                           description: str = "", phases: list = [], tasks: list = []) -> str:
    '''
    为项目创建开发规划
    
    :param project_path: 项目目录路径
    :type project_path: str
    :param project_name: 项目名称
    :type project_name: str
    :param description: 项目描述
    :type description: str
    :param phases: 开发阶段列表
    :type phases: list
    :param tasks: 开发任务列表
    :type tasks: list
    :return: 创建操作结果
    :rtype: str
    '''
    try:
        # If project_name not provided, use directory name
        if not project_name:
            project_name = Path(project_path).name
        
        result = _plan_manager.create_plan(project_path, project_name, description, phases, tasks)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Failed to create development plan: {e}"

def update_task_status(project_path: str = ".", task_id: int = 1, status: str = "pending", 
                      actual_hours: float = None) -> str:
    '''Update the status of a development task

    :param project_path: Path to the project directory
    :type project_path: str
    :param task_id: Task ID
    :type task_id: int
    :param status: New status
    :type status: str
    :param actual_hours: Actual hours spent (hours)
    :type actual_hours: float
    :return: Update operation result
    :rtype: str
    '''
    try:
        result = _plan_manager.update_task_status(project_path, task_id, status, actual_hours)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Failed to update task status: {e}"
        result = _plan_manager.update_task_status(project_path, task_id, status, actual_hours)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Failed to update task status: {e}"

def get_project_summary(project_path: str = ".") -> str:
    '''
    Get a summary of project context and development plan

    :param project_path: Path to the project directory
    :type project_path: str
    :return: Project summary
    :rtype: str
    '''
    try:
        result = _plan_manager.get_summary(project_path)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Failed to get project summary: {e}"

def add_progress_log(project_path: str = ".", task_id: int = 1, log_text: str = "") -> str:
    '''
    Add a progress log entry to a task

    :param project_path: Path to the project directory
    :type project_path: str
    :param task_id: Task ID
    :type task_id: int
    :param log_text: Log text
    :type log_text: str
    :return: Add operation result
    :type log_text: str
    :return: 添加操作结果
    :rtype: str
    '''
    try:
        result = _plan_manager.add_progress_log(project_path, task_id, log_text)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return f"Failed to add progress log: {e}"

def optimize_feature_context(messages: List[Any] = None, completed_feature: str = "", next_feature: str = "") -> str:
    '''
    Optimize context after completing an atomic feature: clear intermediate data, load TODO.md, prompt for next feature development
    
    :param messages: Conversation messages list (system will handle automatically, no need to provide)
    :type messages: list
    :param completed_feature: Description of completed atomic feature
    :type completed_feature: str
    :param next_feature: Description of next atomic feature to work on (optional)
    :type next_feature: str
    :return: Context optimization result and next steps
    :rtype: str
    '''
    try:
        # Helper function: ensure message is in dict format
        def ensure_message_dict(msg: Any) -> Dict:
            if isinstance(msg, dict):
                return msg
            elif hasattr(msg, 'model_dump'):
                return msg.model_dump()
            elif hasattr(msg, '__dict__'):
                return vars(msg)
            else:
                try:
                    return dict(msg)
                except:
                    result = {}
                    if hasattr(msg, 'role'):
                        result['role'] = msg.role
                    if hasattr(msg, 'content'):
                        result['content'] = msg.content
                    return result
        
        def ensure_messages_dict(messages: List[Any]) -> List[Dict]:
            return [ensure_message_dict(msg) for msg in messages] if messages else []
        
        # Analyze messages to extract core information
        original_user_request = ""
        system_prompt = ""
        
        if messages:
            messages_dict = ensure_messages_dict(messages)
            
            # Find system prompt
            for msg in messages_dict:
                if msg.get('role') == 'system':
                    system_prompt = msg.get("content", "You're a helpful assistant")
                    break
            
            # Find original user request (first user message)
            for msg in messages_dict:
                if msg.get('role') == 'user':
                    content = msg.get('content', '')
                    # Skip context optimization related messages
                    if not content.startswith('## Context Optimization Needed') and not content.startswith('## Context Summary'):
                        original_user_request = original_user_request + content + "\n"
        
        # Get current project summary
        project_summary = ""
        try:
            project_summary = get_project_summary(".")
            project_summary_json = json.loads(project_summary)
            if "project_info" in project_summary_json:
                summary_text = f"Project: {project_summary_json['project_info'].get('name', 'Unknown')}\n"
                summary_text += f"Type: {project_summary_json['project_info'].get('type', 'Unknown')}\n"
                if "development_plan" in project_summary_json:
                    dev_plan = project_summary_json['development_plan']
                    summary_text += f"Development progress: {dev_plan.get('completion_percentage', 0)}%\n"
                    summary_text += f"Task status: {dev_plan.get('status_counts', {}).get('completed', 0)} completed, {dev_plan.get('status_counts', {}).get('in_progress', 0)} in progress\n"
                project_summary = summary_text
        except Exception as e:
            project_summary = f"Failed to get project summary: {e}"
        
        # Try to load TODO.md file
        todo_content = ""
        try:
            todo_path = Path("TODO.md")
            if todo_path.exists():
                todo_content = todo_path.read_text(encoding='utf-8')
            else:
                todo_path = Path("todo.md")
                if todo_path.exists():
                    todo_content = todo_path.read_text(encoding='utf-8')
        except Exception as e:
            todo_content = f"Failed to load TODO.md: {e}"
        
        # Clean up message list (if messages provided)
        if messages is not None and len(messages) > 0:
            # Save last message (usually current assistant response)
            last_message = messages[-1] if messages else None
            
            # Clear message list
            messages.clear()
            
            # Re-add core messages: system prompt and original user request
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if original_user_request:
                messages.append({"role": "user", "content": original_user_request})
            
            # If last message exists, re-add it
            if last_message:
                messages.append(ensure_message_dict(last_message))
        
        # Build response
        response = {
            "optimization_completed": True,
            "completed_feature": completed_feature,
            "project_summary": project_summary,
            "next_steps": [
                "1. Review TODO.md items" if todo_content else "1. Create TODO.md file to record tasks",
                "2. Use get_project_summary to check project status",
                f"3. Suggested next feature: {next_feature}" if next_feature else "3. Select next atomic feature for development",
                "4. Use optimize_feature_context again after development for context cleanup"
            ],
            "note": "Unlike enhance_summary, this tool focuses on context cleanup after feature completion, with significant token optimization."
        }   # If next feature specified, add to response
        if next_feature:
            response["suggested_next_feature"] = next_feature
        
        return json.dumps(response, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "optimization_completed": False,
            "error": str(e),
            "recommendation": "Optimization failed, please manually clean up context and continue to next task"
        }, ensure_ascii=False, indent=2)
# Tool Call Mapping
# ============================================================================

TOOL_CALL_MAP = {
    "detect_project": detect_project,
    "save_project_context": save_project_context,
    "load_project_context": load_project_context,
    "list_projects": list_projects,
    "create_development_plan": create_development_plan,
    "update_task_status": update_task_status,
    "get_project_summary": get_project_summary,
    "add_progress_log": add_progress_log,
    "optimize_feature_context": optimize_feature_context,
}

# ============================================================================
# 上下文管理辅助函数
# ============================================================================

def get_active_project_context() -> Dict[str, Any]:
    """
    Get the context of the current active project

    Returns:
        Dict[str, Any]: Project context data
    """
    try:
        # Try to load context from current directory
        result = _context_manager.load_context(".")
        if "error" not in result and "data" in result:
            return result["data"]
        
        # Try to detect project
        project_info = _detector.detect_from_path(".")
        
        # Create basic context if none exists
        basic_context = {
            "project_info": project_info,
            "created_at": datetime.datetime.now().isoformat(),
            "context_version": "1.0",
        }
        
        return basic_context
    except Exception:
        return {}

def analyze_project_structure(project_path: str = ".") -> Dict[str, Any]:
    """
    分析项目结构，获取详细架构信息
    
    Args:
        project_path: 项目路径
    
    Returns:
        Dict[str, Any]: 项目架构信息
    """
    try:
        project_path = Path(project_path).resolve()
        if not project_path.exists():
            return {"error": f"项目路径不存在: {project_path}"}
        
        analysis = {
            "project_path": str(project_path),
            "analyzed_at": datetime.datetime.now().isoformat(),
            "directory_structure": {},
            "python_files": [],
            "key_files": [],
            "dependencies": {},
            "entry_points": [],
            "modules": [],
            "test_files": [],
            "documentation_files": [],
        }
        
        # 扫描目录结构
        def scan_dir(current_path: Path, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth > max_depth:
                return {}
            
            result = {}
            try:
                for item in current_path.iterdir():
                    if item.name.startswith('.') or item.name == '__pycache__':
                        continue
                    
                    if item.is_dir():
                        result[item.name] = scan_dir(item, max_depth, current_depth + 1)
                    else:
                        result[item.name] = "file"
                        
                        # 分类文件
                        if item.suffix == '.py':
                            analysis["python_files"].append(str(item.relative_to(project_path)))
                            
                            # 尝试提取模块信息
                            try:
                                with open(item, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                # 简单提取类定义
                                class_matches = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
                                # 简单提取函数定义
                                func_matches = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)
                                
                                if class_matches or func_matches:
                                    rel_path = str(item.relative_to(project_path))
                                    module_name = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
                                    analysis["modules"].append({
                                        "module": module_name,
                                        "classes": class_matches,
                                        "functions": func_matches[:5],  # 只取前5个函数
                                        "file": rel_path,
                                    })
                            except:
                                pass
                        
                        # 关键文件
                        key_files = {
                            'requirements.txt': '依赖文件',
                            'setup.py': '安装配置',
                            'pyproject.toml': '项目配置',
                            'README.md': '项目说明',
                            'README.rst': '项目说明',
                            'README.txt': '项目说明',
                            'Dockerfile': '容器配置',
                            'docker-compose.yml': '容器编排',
                            '.env': '环境变量',
                            '.env.example': '环境变量示例',
                            'config.yaml': '配置文件',
                            'config.yml': '配置文件',
                            'config.json': '配置文件',
                            'Makefile': '构建脚本',
                            'LICENSE': '许可证',
                            'CHANGELOG.md': '更新日志',
                        }
                        
                        if item.name in key_files:
                            analysis["key_files"].append({
                                "file": str(item.relative_to(project_path)),
                                "type": key_files[item.name],
                            })
                        
                        # 测试文件
                        if 'test' in item.name.lower() or item.parent.name == 'tests':
                            analysis["test_files"].append(str(item.relative_to(project_path)))
                        
                        # 文档文件
                        if item.suffix in ['.md', '.rst', '.txt', '.pdf']:
                            analysis["documentation_files"].append(str(item.relative_to(project_path)))
            
            except PermissionError:
                pass
            
            return result
        
        analysis["directory_structure"] = scan_dir(project_path)
        
        # 分析依赖关系
        # 尝试读取 setup.py
        setup_file = project_path / "setup.py"
        if setup_file.exists():
            try:
                with open(setup_file, 'r', encoding='utf-8') as f:
                    setup_content = f.read()
                
                # 简单提取 install_requires
                install_match = re.search(r'install_requires\s*=\s*\[(.*?)\]', setup_content, re.DOTALL)
                if install_match:
                    requires_text = install_match.group(1)
                    # Extract dependencies within quotes
                    deps = re.findall(r'["\']([^"\']+)["\']', requires_text)
                    analysis["dependencies"]["install_requires"] = deps
                
                # 提取 extras_require
                extras_match = re.search(r'extras_require\s*=\s*\{(.*?)\}', setup_content, re.DOTALL)
                if extras_match:
                    extras_text = extras_match.group(1)
                    # 简单解析额外依赖
                    extras = {}
                    current_key = None
                    current_value = []
                    
                    for line in extras_text.split('\n'):
                        line = line.strip()
                        if line.endswith(':['):
                            if current_key:
                                extras[current_key] = current_value
                            current_key = line[:-2].strip().replace('"', '').replace("'", "")
                            current_value = []
                        elif line.startswith("'") or line.startswith('"'):
                            dep = line.replace('"', '').replace("'", "").replace(',', '')
                            if dep:
                                current_value.append(dep)
                    
                    if current_key and current_value:
                        extras[current_key] = current_value
                    
                    analysis["dependencies"]["extras_require"] = extras
                    
            except Exception as e:
                analysis["dependencies"]["setup.py_error"] = str(e)
        
        # 尝试读取 requirements.txt
        req_file = project_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                analysis["dependencies"]["requirements.txt"] = requirements
            except:
                pass
        
        # 提取入口点
        # Check for common entry files
        entry_files = ['main.py', 'app.py', 'cli.py', '__main__.py', 'run.py']
        for entry_file in entry_files:
            if (project_path / entry_file).exists():
                analysis["entry_points"].append(entry_file)
        
        # 检查 src 目录
        src_dir = project_path / "src"
        if src_dir.exists():
            for entry_file in entry_files:
                if (src_dir / entry_file).exists():
                    analysis["entry_points"].append(f"src/{entry_file}")
        
        return analysis
    
    except Exception as e:
        return {"error": f"Failed to analyze project structure: {str(e)}"}
def generate_context_summary_for_ai(project_path: str = ".") -> str:
    """
    为AI生成项目上下文摘要
    
    Args:
        project_path: 项目路径
    
    Returns:
        str: 格式化后的上下文摘要
    """
    try:
        summary_result = _plan_manager.get_summary(project_path)
        
        if "error" in summary_result:
            # Try to get basic project info
            project_info = _detector.detect_from_path(project_path)
            
            # 分析项目结构
            structure = analyze_project_structure(project_path)
            
            output_parts = ["## 项目上下文摘要\n"]
            
            output_parts.append("📋 **项目信息**")
            output_parts.append(f"- 项目路径: {project_info.get('path', '未知')}")
            output_parts.append(f"- 项目类型: {project_info.get('project_type', '未知')}")
            output_parts.append(f"- 项目名称: {project_info.get('project_name', '未知')}")
            output_parts.append(f"- Git仓库: {'是' if project_info.get('git_info') else '否'}")
            output_parts.append("")
            
            output_parts.append("📁 **状态**")
            output_parts.append("- 上下文文件: 未找到 (.aitools_context.json)")
            output_parts.append("- 建议: 使用 create_development_plan 创建开发规划")
            output_parts.append("")
            
            # 添加项目结构信息
            if "error" not in structure:
                output_parts.append("🏗️ **项目结构概览**")
                
                # Python文件统计
                python_files = structure.get("python_files", [])
                if python_files:
                    output_parts.append(f"- Python文件: {len(python_files)}个")
                    # 显示主要模块
                    modules = structure.get("modules", [])
                    if modules:
                        module_names = [m.get("module", "") for m in modules[:5]]  # 只显示前5个
                        output_parts.append(f"- 主要模块: {', '.join(module_names)}" + ("..." if len(modules) > 5 else ""))
                
                # 关键文件
                key_files = structure.get("key_files", [])
                if key_files:
                    output_parts.append(f"- 关键文件: {len(key_files)}个 (包括: {', '.join([f['file'] for f in key_files[:3]])}" + 
                                       ("..." if len(key_files) > 3 else "") + ")")
                
                # 依赖关系
                deps = structure.get("dependencies", {})
                if deps:
                    install_deps = deps.get("install_requires", [])
                    if install_deps:
                        output_parts.append(f"- 主要依赖: {len(install_deps)}个")
                        output_parts.append(f"  核心依赖: {', '.join(install_deps[:5])}" + 
                                           ("..." if len(install_deps) > 5 else ""))
                
                # 入口点
                entry_points = structure.get("entry_points", [])
                if entry_points:
                    output_parts.append(f"- 入口点: {', '.join(entry_points)}")
                
                output_parts.append("")
            
            output_parts.append("💡 **下一步**")
            output_parts.append("1. 使用 detect_project 查看详细项目信息")
            output_parts.append("2. 使用 create_development_plan 创建开发规划")
            output_parts.append("3. 使用 save_project_context 保存自定义上下文")
            
            return "\n".join(output_parts)
        
        # Format detailed summary
        summary = summary_result
        
        project_info = summary.get("project_info", {})
        context_info = summary.get("context_info", {})
        dev_plan = summary.get("development_plan", {})
        
        # 分析项目结构
        structure = analyze_project_structure(project_path)
        
        output_parts = ["## 项目上下文摘要\n"]
        
        # Project info
        output_parts.append("📋 **项目信息**")
        output_parts.append(f"- 项目路径: {project_info.get('path', '未知')}")
        output_parts.append(f"- 项目名称: {project_info.get('name', '未知')}")
        output_parts.append(f"- 项目类型: {project_info.get('type', '未知')}")
        output_parts.append(f"- Git仓库: {'是' if project_info.get('has_git') else '否'}")
        output_parts.append("")
        
        # Context info
        output_parts.append("📁 **上下文状态**")
        output_parts.append(f"- 上下文文件: {context_info.get('context_file', '无')}")
        output_parts.append(f"- 数据模块: {', '.join(context_info.get('data_keys', []))}")
        output_parts.append("")
        
        # Development plan if exists
        if dev_plan:
            output_parts.append("🗺️ **开发规划**")
            output_parts.append(f"- 项目: {dev_plan.get('project_name', '未知')}")
            output_parts.append(f"- 描述: {dev_plan.get('description', '无描述')}")
            output_parts.append(f"- 阶段数量: {dev_plan.get('phases_count', 0)}")
            output_parts.append(f"- 任务总数: {dev_plan.get('tasks_count', 0)}")
            
            status_counts = dev_plan.get('status_counts', {})
            output_parts.append(f"- 任务状态: 待处理({status_counts.get('pending', 0)}), 进行中({status_counts.get('in_progress', 0)}), 已完成({status_counts.get('completed', 0)})")
            output_parts.append(f"- 完成进度: {dev_plan.get('completion_percentage', 0)}%")
            
            next_task = dev_plan.get('next_task')
            if next_task:
                output_parts.append(f"- 下一个任务: #{next_task.get('id')} {next_task.get('name', '未知')}")
            output_parts.append("")
        
        # 添加项目架构信息
        if "error" not in structure:
            output_parts.append("🏗️ **项目架构概览**")
            
            # Python文件统计
            python_files = structure.get("python_files", [])
            if python_files:
                output_parts.append(f"- Python文件: {len(python_files)}个")
            
            # 模块信息
            modules = structure.get("modules", [])
            if modules:
                # 按目录分组
                module_groups = {}
                for module in modules:
                    mod_name = module.get("module", "")
                    # 提取顶层包名
                    parts = mod_name.split('.')
                    if len(parts) > 1:
                        top_level = parts[0]
                    else:
                        top_level = "main"
                    
                    if top_level not in module_groups:
                        module_groups[top_level] = []
                    module_groups[top_level].append(module)
                
                if module_groups:
                    output_parts.append(f"- 主要包: {', '.join(sorted(module_groups.keys()))}")
            
            # 关键文件
            key_files = structure.get("key_files", [])
            if key_files:
                # 按类型分组
                file_types = {}
                for kf in key_files:
                    ftype = kf.get("type", "其他")
                    if ftype not in file_types:
                        file_types[ftype] = []
                    file_types[ftype].append(kf.get("file", ""))
                
                for ftype, files in file_types.items():
                    if files:
                        output_parts.append(f"- {ftype}: {', '.join(files[:2])}" + 
                                           ("..." if len(files) > 2 else ""))
            
            # 依赖关系
            deps = structure.get("dependencies", {})
            if deps:
                install_deps = deps.get("install_requires", [])
                if install_deps:
                    output_parts.append(f"- 核心依赖: {len(install_deps)}个")
                
                extras = deps.get("extras_require", {})
                if extras:
                    output_parts.append(f"- 额外依赖组: {', '.join(extras.keys())}")
            
            # 测试文件
            test_files = structure.get("test_files", [])
            if test_files:
                output_parts.append(f"- 测试文件: {len(test_files)}个")
            
            output_parts.append("")
        
        # Recommendations
        output_parts.append("💡 **建议操作**")
        if not dev_plan:
            output_parts.append("1. 使用 create_development_plan 创建开发规划")
        elif dev_plan.get('completion_percentage', 0) < 100:
            output_parts.append("1. 使用 update_task_status 更新任务状态")
            output_parts.append("2. 使用 add_progress_log 添加进度日志")
        
        # 根据项目状态添加特定建议
        if "error" not in structure:
            # 检查是否有web目录或web相关文件（仅用于信息性建议）
            has_web = any('web' in f.lower() for f in structure.get("python_files", []))
            if has_web:
                output_parts.append("3. 检查CLI界面优化进度（项目聚焦命令行工具）")
            
            # 检查是否有测试文件
            if structure.get("test_files"):
                output_parts.append("4. 运行测试确保功能正常")
        
        output_parts.append("5. 使用 get_project_summary 查看最新状态")
        
        return "\n".join(output_parts)
    
    except Exception as e:
        return f"生成上下文摘要失败: {e}"

# ============================================================================
# 测试代码
# ============================================================================

if __name__ == "__main__":
    print("AITools Project Context 模块测试")
    print("=" * 60)
    
    # 测试项目检测
    print("1. 测试项目检测:")
    result = detect_project(".")
    print(result[:300] + "..." if len(result) > 300 else result)
    print()
    
    # 测试获取项目摘要
    print("2. 测试获取项目摘要:")
    result = get_project_summary(".")
    print(result[:300] + "..." if len(result) > 300 else result)
    print()
    
    # 测试列出项目
    print("3. 测试列出项目:")
    result = list_projects(".", recursive=False)
    print(result[:300] + "..." if len(result) > 300 else result)
    print()
    
    print("Project Context 模块测试完成!")
