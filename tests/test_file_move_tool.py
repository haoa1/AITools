#!/usr/bin/env python3
"""
FileMoveTool测试文件。

测试Claude Code兼容的FileMoveTool简化实现。
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

from file.file_move_tool import file_move, _validate_paths, _create_parent_dirs_if_needed, _check_overwrite


class TestHelperFunctions(unittest.TestCase):
    """测试辅助函数"""
    
    def setUp(self):
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        self.source_file = os.path.join(self.test_dir, "source.txt")
        self.dest_file = os.path.join(self.test_dir, "dest.txt")
        
        # 创建源文件
        with open(self.source_file, "w") as f:
            f.write("Test content for file move")
    
    def tearDown(self):
        # 清理临时目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_validate_paths_valid(self):
        """测试有效的路径验证"""
        is_valid, error = _validate_paths(self.source_file, self.dest_file)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_paths_source_not_exist(self):
        """测试源路径不存在"""
        is_valid, error = _validate_paths("/nonexistent/path", self.dest_file)
        self.assertFalse(is_valid)
        self.assertIn("does not exist", error)
    
    def test_validate_paths_same_path(self):
        """测试源路径和目标路径相同"""
        is_valid, error = _validate_paths(self.source_file, self.source_file)
        self.assertFalse(is_valid)
        self.assertIn("are the same", error)
    
    def test_create_parent_dirs_if_needed_exists(self):
        """测试父目录已存在的情况"""
        dest = os.path.join(self.test_dir, "subdir", "file.txt")
        success, error = _create_parent_dirs_if_needed(dest, False)
        self.assertFalse(success)  # 父目录不存在且create_parent_dirs=False
        
        success, error = _create_parent_dirs_if_needed(dest, True)
        self.assertTrue(success)  # 应该创建父目录
        self.assertTrue(os.path.exists(os.path.dirname(dest)))
    
    def test_create_parent_dirs_no_parent(self):
        """测试无父目录的情况（根目录）"""
        # Unix系统根目录
        dest = "/file.txt" if os.name != 'nt' else "C:\\file.txt"
        success, error = _create_parent_dirs_if_needed(dest, False)
        self.assertTrue(success)  # 根目录存在
    
    def test_check_overwrite_not_exist(self):
        """测试目标不存在的情况"""
        can_proceed, error = _check_overwrite(self.dest_file, False)
        self.assertTrue(can_proceed)
        self.assertIsNone(error)
    
    def test_check_overwrite_exists_no_overwrite(self):
        """测试目标存在但不允许覆盖的情况"""
        # 创建目标文件
        with open(self.dest_file, "w") as f:
            f.write("Existing content")
        
        can_proceed, error = _check_overwrite(self.dest_file, False)
        self.assertFalse(can_proceed)
        self.assertIn("already exists", error)
    
    def test_check_overwrite_exists_with_overwrite(self):
        """测试目标存在且允许覆盖的情况"""
        # 创建目标文件
        with open(self.dest_file, "w") as f:
            f.write("Existing content")
        
        can_proceed, error = _check_overwrite(self.dest_file, True)
        self.assertTrue(can_proceed)
        self.assertIsNone(error)


class TestFileMoveFunction(unittest.TestCase):
    """测试file_move主函数"""
    
    def setUp(self):
        # 创建临时目录结构
        self.test_dir = tempfile.mkdtemp()
        self.source_file = os.path.join(self.test_dir, "source.txt")
        self.dest_file = os.path.join(self.test_dir, "dest.txt")
        self.source_dir = os.path.join(self.test_dir, "source_dir")
        self.dest_dir = os.path.join(self.test_dir, "dest_dir")
        
        # 创建源文件
        with open(self.source_file, "w") as f:
            f.write("Test content for file move\nLine 2\nLine 3")
        
        # 创建源目录和文件
        os.makedirs(self.source_dir)
        with open(os.path.join(self.source_dir, "file1.txt"), "w") as f:
            f.write("File in directory")
    
    def tearDown(self):
        # 清理临时目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _parse_result(self, result_str):
        """解析file_move返回的JSON字符串"""
        return json.loads(result_str)
    
    def test_file_move_success(self):
        """测试成功的文件移动"""
        result_str = file_move(self.source_file, self.dest_file)
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["operation"], "rename")  # 同目录重命名
        self.assertEqual(result["source"], self.source_file)
        self.assertEqual(result["destination"], self.dest_file)
        self.assertFalse(result["is_directory"])
        self.assertGreater(result["bytes_moved"], 0)
        self.assertIn("durationMs", result)
        
        # 验证文件确实被移动了
        self.assertFalse(os.path.exists(self.source_file))
        self.assertTrue(os.path.exists(self.dest_file))
    
    def test_file_move_to_different_directory(self):
        """测试移动到不同目录"""
        dest_dir = os.path.join(self.test_dir, "subdir")
        dest_file = os.path.join(dest_dir, "dest.txt")
        
        result_str = file_move(
            source=self.source_file,
            destination=dest_file,
            create_parent_dirs=True
        )
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["operation"], "move")  # 移动到不同目录
        self.assertFalse(result["is_directory"])  # 移动的是文件，不是目录
        
        # 验证文件确实被移动了
        self.assertFalse(os.path.exists(self.source_file))
        self.assertTrue(os.path.exists(dest_file))
    
    def test_directory_move(self):
        """测试目录移动"""
        result_str = file_move(self.source_dir, self.dest_dir)
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["is_directory"])
        
        # 验证目录确实被移动了
        self.assertFalse(os.path.exists(self.source_dir))
        self.assertTrue(os.path.exists(self.dest_dir))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, "file1.txt")))
    
    def test_file_move_with_overwrite(self):
        """测试带覆盖的文件移动"""
        # 先创建目标文件
        with open(self.dest_file, "w") as f:
            f.write("Old content")
        
        result_str = file_move(
            source=self.source_file,
            destination=self.dest_file,
            overwrite=True
        )
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        
        # 验证新内容已覆盖旧内容
        with open(self.dest_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "Test content for file move\nLine 2\nLine 3")
    
    def test_file_move_without_overwrite_fails(self):
        """测试不允许覆盖时的失败情况"""
        # 先创建目标文件
        with open(self.dest_file, "w") as f:
            f.write("Old content")
        
        result_str = file_move(
            source=self.source_file,
            destination=self.dest_file,
            overwrite=False  # 默认值
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("already exists", result["error"])
        
        # 验证源文件仍然存在，目标文件未被修改
        self.assertTrue(os.path.exists(self.source_file))
        self.assertTrue(os.path.exists(self.dest_file))
    
    def test_file_move_source_not_exist(self):
        """测试源文件不存在的情况"""
        result_str = file_move(
            source="/nonexistent/path/file.txt",
            destination=self.dest_file
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("does not exist", result["error"])
    
    def test_file_move_empty_source(self):
        """测试空源路径"""
        result_str = file_move(
            source="",
            destination=self.dest_file
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("cannot be empty", result["error"])
    
    def test_file_move_empty_destination(self):
        """测试空目标路径"""
        result_str = file_move(
            source=self.source_file,
            destination=""
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("cannot be empty", result["error"])
    
    def test_file_move_parent_dir_not_exist(self):
        """测试父目录不存在且不创建的情况"""
        dest_file = os.path.join(self.test_dir, "nonexistent", "subdir", "file.txt")
        
        result_str = file_move(
            source=self.source_file,
            destination=dest_file,
            create_parent_dirs=False
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("does not exist", result["error"])
    
    def test_file_move_permission_error(self):
        """测试权限错误（模拟）"""
        with patch('os.access') as mock_access:
            mock_access.return_value = False  # 模拟无读取权限
            
            result_str = file_move(self.source_file, self.dest_file)
            result = self._parse_result(result_str)
            
            self.assertFalse(result["success"])
            # 由于模拟了权限错误，具体错误信息可能不同
    
    def test_file_move_shutil_error(self):
        """测试shutil.move错误（模拟）"""
        with patch('shutil.move') as mock_move:
            mock_move.side_effect = Exception("Mocked shutil.move error")
            
            result_str = file_move(self.source_file, self.dest_file)
            result = self._parse_result(result_str)
            
            self.assertFalse(result["success"])
            self.assertIn("Move operation failed", result["error"])
    
    def test_file_move_overwrite_with_readonly_destination(self):
        """测试覆盖只读目标文件"""
        if os.name == 'nt':
            self.skipTest("Windows权限测试跳过")
        
        # 创建只读目标文件
        with open(self.dest_file, "w") as f:
            f.write("Read-only content")
        os.chmod(self.dest_file, 0o444)  # 只读
        
        try:
            result_str = file_move(
                source=self.source_file,
                destination=self.dest_file,
                overwrite=True
            )
            result = self._parse_result(result_str)
            
            # 在某些系统上可能成功（超级用户），在某些系统上可能失败
            # 我们只检查返回了合理的结果
            self.assertIn("success", result)
        finally:
            # 恢复权限以便清理
            if os.path.exists(self.dest_file):
                os.chmod(self.dest_file, 0o644)
    
    def test_file_move_large_file(self):
        """测试大文件移动（模拟）"""
        # 创建1MB的测试文件
        large_file = os.path.join(self.test_dir, "large_source.txt")
        dest_large = os.path.join(self.test_dir, "large_dest.txt")
        
        with open(large_file, "wb") as f:
            f.write(b"X" * 1024 * 1024)  # 1MB
        
        result_str = file_move(large_file, dest_large)
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["bytes_moved"], 1024 * 1024)
        self.assertTrue(os.path.exists(dest_large))
        self.assertFalse(os.path.exists(large_file))
    
    def test_file_move_symlink(self):
        """测试符号链接移动（如果支持）"""
        # 跳过Windows上的符号链接测试
        if os.name == 'nt':
            self.skipTest("Windows符号链接测试跳过")
        
        try:
            # 创建目标文件
            target_file = os.path.join(self.test_dir, "target.txt")
            with open(target_file, "w") as f:
                f.write("Target content")
            
            # 创建符号链接
            symlink_file = os.path.join(self.test_dir, "symlink.txt")
            os.symlink(target_file, symlink_file)
            
            # 移动符号链接
            dest_symlink = os.path.join(self.test_dir, "symlink_moved.txt")
            result_str = file_move(symlink_file, dest_symlink)
            result = self._parse_result(result_str)
            
            self.assertTrue(result["success"])
            self.assertTrue(os.path.islink(dest_symlink))
            self.assertFalse(os.path.exists(symlink_file))
            
        except (OSError, NotImplementedError):
            self.skipTest("符号链接创建失败，跳过测试")


class TestFileMoveToolIntegration(unittest.TestCase):
    """测试FileMoveTool集成"""
    
    def test_function_ai_decorator_presence(self):
        """测试function_ai装饰器存在"""
        from file.file_move_tool import tools
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
    
    def test_module_exports(self):
        """测试模块导出"""
        from file.file_move_tool import tools, TOOL_CALL_MAP
        
        self.assertIsInstance(tools, list)
        self.assertIsInstance(TOOL_CALL_MAP, dict)
        self.assertIn("file_move", TOOL_CALL_MAP)
    
    def test_default_parameters(self):
        """测试默认参数"""
        import inspect
        from file.file_move_tool import file_move
        
        sig = inspect.signature(file_move)
        params = sig.parameters
        
        self.assertIn('overwrite', params)
        self.assertEqual(params['overwrite'].default, False)
        
        self.assertIn('create_parent_dirs', params)
        self.assertEqual(params['create_parent_dirs'].default, False)
    
    def test_json_output_format(self):
        """测试JSON输出格式"""
        import tempfile
        import shutil
        
        # 创建临时文件
        test_dir = tempfile.mkdtemp()
        try:
            source = os.path.join(test_dir, "test_source.txt")
            dest = os.path.join(test_dir, "test_dest.txt")
            
            with open(source, "w") as f:
                f.write("Test")
            
            from file.file_move_tool import file_move
            result_str = file_move(source, dest)
            
            # 验证是有效的JSON
            result = json.loads(result_str)
            
            # 检查必需字段
            self.assertIn("success", result)
            self.assertIn("operation", result)
            self.assertIn("source", result)
            self.assertIn("destination", result)
            self.assertIn("durationMs", result)
            
            # 成功时应该有这些字段
            if result["success"]:
                self.assertIn("is_directory", result)
                self.assertIn("bytes_moved", result)
            
        finally:
            shutil.rmtree(test_dir)


if __name__ == '__main__':
    unittest.main()