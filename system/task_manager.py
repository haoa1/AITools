#!/usr/bin/env python3
"""
Simple task manager for AITools.
Provides basic task management functionality for TaskStopTool and related tools.
"""

import uuid
import time
from typing import Dict, List, Any, Optional, Union
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    """Represents a managed task."""
    
    def __init__(self, task_type: str, description: str = "", command: str = ""):
        self.task_id = str(uuid.uuid4())[:8]  # Short ID for simplicity
        self.task_type = task_type
        self.description = description
        self.command = command
        self.status = TaskStatus.PENDING
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.stopped_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.metadata: Dict[str, Any] = {}
    
    def start(self) -> None:
        """Mark task as running."""
        self.status = TaskStatus.RUNNING
        self.started_at = time.time()
    
    def stop(self) -> None:
        """Mark task as stopped."""
        self.status = TaskStatus.STOPPED
        self.stopped_at = time.time()
    
    def complete(self) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = time.time()
    
    def fail(self) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.stopped_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "command": self.command,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }
    
    def __str__(self) -> str:
        return f"Task({self.task_id}, {self.task_type}, {self.status.value})"


class TaskManager:
    """Simple in-memory task manager."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskManager, cls).__new__(cls)
            cls._instance._tasks: Dict[str, Task] = {}
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._tasks: Dict[str, Task] = {}
            self._initialized = True
    
    def register_task(self, task_type: str, description: str = "", command: str = "") -> str:
        """
        Register a new task.
        
        Args:
            task_type: Type of task (e.g., "bash", "process", "background")
            description: Human-readable description
            command: Command or operation being performed
            
        Returns:
            Task ID
        """
        task = Task(task_type, description, command)
        self._tasks[task.task_id] = task
        return task.task_id
    
    def start_task(self, task_id: str) -> bool:
        """
        Start a task (mark as running).
        
        Args:
            task_id: ID of the task to start
            
        Returns:
            True if task was started, False if task not found or already running
        """
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        if task.status == TaskStatus.PENDING:
            task.start()
            return True
        return False
    
    def stop_task(self, task_id: str) -> bool:
        """
        Stop a running task.
        
        Args:
            task_id: ID of the task to stop
            
        Returns:
            True if task was stopped, False if task not found or not running
        """
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        if task.status == TaskStatus.RUNNING:
            task.stop()
            return True
        return False
    
    def complete_task(self, task_id: str) -> bool:
        """Mark a task as completed."""
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        if task.status in [TaskStatus.RUNNING, TaskStatus.PENDING]:
            task.complete()
            return True
        return False
    
    def fail_task(self, task_id: str) -> bool:
        """Mark a task as failed."""
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        if task.status in [TaskStatus.RUNNING, TaskStatus.PENDING]:
            task.fail()
            return True
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self._tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks as dictionaries."""
        return [task.to_dict() for task in self._tasks.values()]
    
    def get_running_tasks(self) -> List[Dict[str, Any]]:
        """Get all running tasks."""
        return [task.to_dict() for task in self._tasks.values() 
                if task.status == TaskStatus.RUNNING]
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        """Get task status by ID."""
        task = self._tasks.get(task_id)
        return task.status.value if task else None
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False
    
    def clear_completed_tasks(self) -> int:
        """Clear all completed and failed tasks, return count cleared."""
        to_delete = []
        for task_id, task in self._tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.STOPPED]:
                to_delete.append(task_id)
        
        for task_id in to_delete:
            del self._tasks[task_id]
        
        return len(to_delete)
    
    def cleanup_old_tasks(self, max_age_seconds: int = 3600) -> int:
        """
        Clean up old tasks.
        
        Args:
            max_age_seconds: Maximum age in seconds
            
        Returns:
            Number of tasks cleaned up
        """
        current_time = time.time()
        to_delete = []
        
        for task_id, task in self._tasks.items():
            # Determine the relevant timestamp
            if task.completed_at:
                timestamp = task.completed_at
            elif task.stopped_at:
                timestamp = task.stopped_at
            elif task.started_at:
                timestamp = task.started_at
            else:
                timestamp = task.created_at
            
            if current_time - timestamp > max_age_seconds:
                to_delete.append(task_id)
        
        for task_id in to_delete:
            del self._tasks[task_id]
        
        return len(to_delete)
    
    def reset(self) -> None:
        """Reset task manager (clear all tasks)."""
        self._tasks.clear()


# Global instance for easy access
task_manager = TaskManager()


def create_test_task(task_type: str = "test", description: str = "Test task", 
                     command: str = "echo 'test'", start: bool = True) -> str:
    """
    Helper function to create a test task.
    
    Args:
        task_type: Task type
        description: Task description
        command: Task command
        start: Whether to start the task immediately
        
    Returns:
        Task ID
    """
    task_id = task_manager.register_task(task_type, description, command)
    if start:
        task_manager.start_task(task_id)
    return task_id


if __name__ == "__main__":
    # Test the task manager
    print("Testing TaskManager...")
    
    # Create some tasks
    task1_id = create_test_task("bash", "Test shell command", "ls -la", start=True)
    task2_id = create_test_task("process", "Background process", "sleep 60", start=True)
    task3_id = create_test_task("monitor", "System monitor", "monitor.py", start=False)
    
    print(f"Created tasks: {task1_id}, {task2_id}, {task3_id}")
    
    # List all tasks
    print("\nAll tasks:")
    for task in task_manager.get_all_tasks():
        print(f"  {task['task_id']}: {task['task_type']} - {task['status']}")
    
    # Stop a task
    print(f"\nStopping task {task1_id}: {task_manager.stop_task(task1_id)}")
    
    # Get running tasks
    print("\nRunning tasks:")
    for task in task_manager.get_running_tasks():
        print(f"  {task['task_id']}: {task['task_type']}")
    
    # Cleanup
    print(f"\nCleared {task_manager.clear_completed_tasks()} completed tasks")
    
    print("\nTaskManager test completed!")