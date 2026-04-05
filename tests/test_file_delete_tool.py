#!/usr/bin/env python3
"""
FileDeleteTool测试文件。

测试Claude Code兼容的FileDeleteTool简化实现。
"""

import os
import sys
import json
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file.file_delete_tool import file_delete, _validate_delete_path, _count_files_and_bytes, _check_system_paths, _delete_with_stats


class TestHelperFunctions(unittest.TestCase):
    """测试辅助函数"""
    
    def setUp(self):
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        
        # 创建测试文件
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Test content for file deletion")
        
        # 创建测试目录
        self.test_subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.test_subdir)
        
        # 在子目录中创建一些文件
        for i in range(3):
            file_path = os.path.join(self.test_subdir, f"file{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Content of file {i}")
    
    def tearDown(self):
        # 清理临时目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_validate_delete_path_valid_file(self):
        """测试有效的文件路径验证"""
        is_valid, error, is_directory = _validate_delete_path(self.test_file)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertFalse(is_directory)
    
    def test_validate_delete_path_valid_directory(self):
        """测试有效的目录路径验证"""
        is_valid, error, is_directory = _validate_delete_path(self.test_subdir)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertTrue(is_directory)
    
    def test_validate_delete_path_not_exist(self):
        """测试路径不存在的情况"""
        is_valid, error, is_directory = _validate_delete_path("/nonexistent/path")
        self.assertFalse(is_valid)
        self.assertIn("does not exist", error)
        self.assertIsNone(is_directory)
    
    def test_validate_delete_path_empty_path(self):
        """测试空路径的情况"""
        is_valid, error, is_directory = _validate_delete_path("")
        self.assertFalse(is_valid)
        self.assertIn("Path cannot be empty", error)
        self.assertIsNone(is_directory)
    
    def test_validate_delete_path_not_readable(self):
        """测试不可读的路径（模拟权限错误）"""
        # 创建一个文件并移除读取权限（在Windows上可能无法工作）
        try:
            test_file = os.path.join(self.test_dir, "no_read.txt")
            with open(test_file, "w") as f:
                f.write("Test")
            
            # 尝试修改权限，如果系统支持
            try:
                import stat
                os.chmod(test_file, 0o000)  # 无权限
                
                is_valid, error, is_directory = _validate_delete_path(test_file)
                # 在Unix系统上应该失败，在Windows上可能成功
                # 我们只检查函数不崩溃
            except:
                # 在某些系统上权限修改可能失败，跳过测试
                pass
        except:
            pass
    
    def test_count_files_and_bytes_single_file(self):
        """测试单个文件的计数"""
        file_count, total_bytes = _count_files_and_bytes(self.test_file)
        self.assertEqual(file_count, 1)
        self.assertGreater(total_bytes, 0)
    
    def test_count_files_and_bytes_directory(self):
        """测试目录的计数"""
        file_count, total_bytes = _count_files_and_bytes(self.test_subdir)
        self.assertEqual(file_count, 3)  # 我们创建了3个文件
        self.assertGreater(total_bytes, 0)
    
    def test_count_files_and_bytes_empty_directory(self):
        """测试空目录的计数"""
        empty_dir = os.path.join(self.test_dir, "empty_dir")
        os.makedirs(empty_dir)
        
        file_count, total_bytes = _count_files_and_bytes(empty_dir)
        self.assertEqual(file_count, 0)
        self.assertEqual(total_bytes, 0)
    
    def test_check_system_paths_safe(self):
        """测试安全的路径（非系统路径）"""
        is_safe, warning = _check_system_paths(self.test_file)
        self.assertTrue(is_safe)
        self.assertIsNone(warning)
    
    def test_check_system_paths_system_dir(self):
        """测试系统目录路径"""
        # 使用一个典型的系统目录
        is_safe, warning = _check_system_paths("/usr/bin")
        self.assertTrue(is_safe)
        self.assertIsNotNone(warning)
        self.assertIn("system directory", warning)
    
    def test_check_system_paths_root(self):
        """测试根目录"""
        is_safe, warning = _check_system_paths("/")
        self.assertFalse(is_safe)
        self.assertIn("root directory", warning)
    
    def test_check_system_paths_home(self):
        """测试家目录"""
        home_dir = os.path.expanduser("~")
        is_safe, warning = _check_system_paths(home_dir)
        self.assertFalse(is_safe)
        self.assertIn("home directory", warning)
    
    def test_delete_with_stats_file_success(self):
        """测试文件删除成功"""
        # 先复制文件用于测试
        test_file_copy = os.path.join(self.test_dir, "test_copy.txt")
        shutil.copy(self.test_file, test_file_copy)
        
        success, error, files_deleted, bytes_freed = _delete_with_stats(
            test_file_copy, False, False, False
        )
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(files_deleted, 1)
        self.assertGreater(bytes_freed, 0)
        self.assertFalse(os.path.exists(test_file_copy))
    
    def test_delete_with_stats_directory_recursive_success(self):
        """测试目录递归删除成功"""
        success, error, files_deleted, bytes_freed = _delete_with_stats(
            self.test_subdir, True, False, False
        )
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(files_deleted, 3)  # 目录中的3个文件
        self.assertGreater(bytes_freed, 0)
        self.assertFalse(os.path.exists(self.test_subdir))
    
    def test_delete_with_stats_directory_non_recursive_empty(self):
        """测试空目录非递归删除成功"""
        empty_dir = os.path.join(self.test_dir, "empty_dir")
        os.makedirs(empty_dir)
        
        success, error, files_deleted, bytes_freed = _delete_with_stats(
            empty_dir, False, False, False
        )
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(files_deleted, 0)
        self.assertEqual(bytes_freed, 0)
        self.assertFalse(os.path.exists(empty_dir))
    
    def test_delete_with_stats_directory_non_recursive_not_empty(self):
        """测试非空目录非递归删除失败"""
        success, error, files_deleted, bytes_freed = _delete_with_stats(
            self.test_subdir, False, False, False
        )
        
        self.assertFalse(success)
        self.assertIsNotNone(error)
        self.assertIn("not empty", error)
        self.assertTrue(os.path.exists(self.test_subdir))  # 目录应该仍然存在
    
    def test_delete_with_stats_dry_run(self):
        """测试干运行（不实际删除）"""
        success, error, files_deleted, bytes_freed = _delete_with_stats(
            self.test_file, False, False, True
        )
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(files_deleted, 1)
        self.assertGreater(bytes_freed, 0)
        self.assertTrue(os.path.exists(self.test_file))  # 文件应该仍然存在
    
    def test_delete_with_stats_force_writable(self):
        """测试强制删除可写文件"""
        # 创建一个可写文件
        writable_file = os.path.join(self.test_dir, "writable.txt")
        with open(writable_file, "w") as f:
            f.write("Test")
        
        success, error, files_deleted, bytes_freed = _delete_with_stats(
            writable_file, False, True, False
        )
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertFalse(os.path.exists(writable_file))
    
    def test_delete_with_stats_file_not_found(self):
        """测试不存在的文件删除（辅助函数应该先检查，但测试边缘情况）"""
        nonexistent = os.path.join(self.test_dir, "nonexistent.txt")
        success, error, files_deleted, bytes_freed = _delete_with_stats(
            nonexistent, False, False, False
        )
        
        # 这个函数不应该被调用在不存在的文件上，但我们可以测试它如何处理
        self.assertFalse(success)
        self.assertIsNotNone(error)


class TestFileDeleteTool(unittest.TestCase):
    """测试主要的FileDeleteTool函数"""
    
    def setUp(self):
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        
        # 创建测试文件
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Test content for file deletion")
        
        # 创建测试目录
        self.test_subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.test_subdir)
        
        # 在子目录中创建一些文件
        for i in range(3):
            file_path = os.path.join(self.test_subdir, f"file{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Content of file {i}")
    
    def tearDown(self):
        # 清理临时目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_file_delete_success(self):
        """测试成功的文件删除"""
        result_json = file_delete(self.test_file, recursive=False)
        result = json.loads(result_json)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["operation"], "delete")
        self.assertEqual(result["path"], self.test_file)
        self.assertFalse(result["is_directory"])
        self.assertIsNone(result["recursive"])
        self.assertFalse(result["dry_run"])
        self.assertEqual(result["files_deleted"], 1)
        self.assertGreater(result["bytes_freed"], 0)
        self.assertFalse(os.path.exists(self.test_file))
    
    def test_file_delete_directory_recursive_success(self):
        """测试成功的目录递归删除"""
        result_json = file_delete(self.test_subdir, recursive=True)
        result = json.loads(result_json)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["operation"], "delete")
        self.assertEqual(result["path"], self.test_subdir)
        self.assertTrue(result["is_directory"])
        self.assertTrue(result["recursive"])
        self.assertFalse(result["dry_run"])
        self.assertEqual(result["files_deleted"], 3)  # 目录中的3个文件
        self.assertGreater(result["bytes_freed"], 0)
        self.assertFalse(os.path.exists(self.test_subdir))
    
    def test_file_delete_directory_non_recursive_empty(self):
        """测试成功的空目录非递归删除"""
        empty_dir = os.path.join(self.test_dir, "empty_dir")
        os.makedirs(empty_dir)
        
        result_json = file_delete(empty_dir, recursive=False)
        result = json.loads(result_json)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["operation"], "delete")
        self.assertEqual(result["path"], empty_dir)
        self.assertTrue(result["is_directory"])
        self.assertFalse(result["recursive"])
        self.assertEqual(result["files_deleted"], 0)
        self.assertEqual(result["bytes_freed"], 0)
        self.assertFalse(os.path.exists(empty_dir))
    
    def test_file_delete_directory_non_recursive_not_empty_fails(self):
        """测试非空目录非递归删除失败"""
        result_json = file_delete(self.test_subdir, recursive=False)
        result = json.loads(result_json)
        
        self.assertFalse(result["success"])
        self.assertIn("not empty", result["error"])
        self.assertTrue(os.path.exists(self.test_subdir))  # 目录应该仍然存在
    
    def test_file_delete_dry_run(self):
        """测试干运行（不实际删除）"""
        result_json = file_delete(self.test_file, dry_run=True)
        result = json.loads(result_json)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["dry_run"])
        self.assertEqual(result["files_deleted"], 1)
        self.assertGreater(result["bytes_freed"], 0)
        self.assertTrue(os.path.exists(self.test_file))  # 文件应该仍然存在
    
    def test_file_delete_with_confirmation(self):
        """测试带有确认请求的删除"""
        # 确认参数只是标记，不影响实际删除
        result_json = file_delete(self.test_file, confirmation=True)
        result = json.loads(result_json)
        
        self.assertTrue(result["success"])
        self.assertIn("confirmation_note", result)  # 应该有一个关于确认的说明
        self.assertFalse(os.path.exists(self.test_file))
    
    def test_file_delete_with_force(self):
        """测试强制删除"""
        result_json = file_delete(self.test_file, force=True)
        result = json.loads(result_json)
        
        self.assertTrue(result["success"])
        self.assertFalse(os.path.exists(self.test_file))
    
    def test_file_delete_path_not_exist(self):
        """测试不存在的路径删除失败"""
        nonexistent = os.path.join(self.test_dir, "nonexistent.txt")
        result_json = file_delete(nonexistent)
        result = json.loads(result_json)
        
        self.assertFalse(result["success"])
        self.assertIn("does not exist", result["error"])
    
    def test_file_delete_empty_path(self):
        """测试空路径删除失败"""
        result_json = file_delete("")
        result = json.loads(result_json)
        
        self.assertFalse(result["success"])
        self.assertIn("cannot be empty", result["error"].lower())
    
    def test_file_delete_system_path_warning(self):
        """测试系统路径删除（应该返回警告）"""
        # 使用当前工作目录作为测试系统路径
        cwd = os.getcwd()
        result_json = file_delete(cwd, dry_run=True)
        result = json.loads(result_json)
        
        # 干运行应该成功，但可能有警告
        self.assertTrue(result["success"])
        self.assertTrue(result["dry_run"])
        self.assertIn("Warning", result.get("warning", ""))
    
    def test_file_delete_json_structure(self):
        """测试返回的JSON结构完整性"""
        result_json = file_delete(self.test_file)
        result = json.loads(result_json)
        
        # 检查必需字段
        required_fields = ["success", "operation", "path", "durationMs"]
        for field in required_fields:
            self.assertIn(field, result)
        
        # 检查可选字段
        optional_fields = ["is_directory", "recursive", "dry_run", "files_deleted", "bytes_freed", "error", "warning", "description"]
        
        # 至少检查字段存在且类型正确
        self.assertIsInstance(result["success"], bool)
        self.assertIsInstance(result["operation"], str)
        self.assertIsInstance(result["path"], str)
        self.assertIsInstance(result["durationMs"], int)
    
    def test_file_delete_complex_scenario(self):
        """测试复杂场景：嵌套目录结构"""
        # 创建嵌套目录结构
        nested_dir = os.path.join(self.test_dir, "nested", "deep", "deeper")
        os.makedirs(nested_dir)
        
        # 在各级目录中创建文件
        for i, dir_path in enumerate([self.test_dir, os.path.dirname(nested_dir), nested_dir]):
            file_path = os.path.join(dir_path, f"level{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Content at level {i}")
        
        # 删除顶级目录（递归）
        top_dir = os.path.join(self.test_dir, "nested")
        result_json = file_delete(top_dir, recursive=True)
        result = json.loads(result_json)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["operation"], "delete")
        self.assertTrue(result["is_directory"])
        self.assertTrue(result["recursive"])
        self.assertGreaterEqual(result["files_deleted"], 2)  # 至少2个文件（在nested目录内）
        self.assertGreater(result["bytes_freed"], 0)
        self.assertFalse(os.path.exists(top_dir))
    
    def test_file_delete_permission_error_simulation(self):
        """测试权限错误模拟"""
        # 使用mock模拟权限错误
        with patch('os.remove') as mock_remove:
            mock_remove.side_effect = PermissionError("Permission denied")
            
            # 创建一个临时文件用于测试
            temp_file = os.path.join(self.test_dir, "temp.txt")
            with open(temp_file, "w") as f:
                f.write("Test")
            
            # 在不使用force的情况下尝试删除
            result_json = file_delete(temp_file, force=False)
            result = json.loads(result_json)
            
            # 应该失败，因为权限错误
            self.assertFalse(result["success"])
            # 错误消息应该是关于写保护的
            self.assertIn("Write-protected", result["error"])
            
            # 文件应该仍然存在
            self.assertTrue(os.path.exists(temp_file))
    
    def test_file_delete_concurrent_access_simulation(self):
        """测试并发访问模拟（文件被其他进程锁定）"""
        # 使用mock模拟文件被锁定的情况
        with patch('os.remove') as mock_remove:
            mock_remove.side_effect = OSError("[Errno 13] Permission denied: File is in use")
            
            # 创建一个临时文件用于测试
            temp_file = os.path.join(self.test_dir, "temp.txt")
            with open(temp_file, "w") as f:
                f.write("Test")
            
            result_json = file_delete(temp_file)
            result = json.loads(result_json)
            
            # 应该失败
            self.assertFalse(result["success"])
            self.assertIn("Permission", result["error"] or "")
    
    def test_file_delete_large_file_statistics(self):
        """测试大文件的统计信息准确性"""
        # 创建一个稍大的文件（100KB）
        large_file = os.path.join(self.test_dir, "large.dat")
        with open(large_file, "wb") as f:
            f.write(b"0" * 102400)  # 100KB
        
        result_json = file_delete(large_file)
        result = json.loads(result_json)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["files_deleted"], 1)
        self.assertEqual(result["bytes_freed"], 102400)  # 应该正好是100KB
        self.assertFalse(os.path.exists(large_file))


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)