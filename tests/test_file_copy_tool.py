#!/usr/bin/env python3
"""
FileCopyTool测试文件。

测试Claude Code兼容的FileCopyTool简化实现。
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

from file.file_copy_tool import file_copy, _validate_copy_paths, _create_parent_dirs_if_needed, _check_overwrite, _count_files_and_bytes, _copy_with_stats


class TestHelperFunctions(unittest.TestCase):
    """测试辅助函数"""
    
    def setUp(self):
        # 创建临时目录用于测试
        self.test_dir = tempfile.mkdtemp()
        self.source_file = os.path.join(self.test_dir, "source.txt")
        self.dest_file = os.path.join(self.test_dir, "dest.txt")
        
        # 创建源文件
        with open(self.source_file, "w") as f:
            f.write("Test content for file copy")
    
    def tearDown(self):
        # 清理临时目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_validate_copy_paths_valid(self):
        """测试有效的路径验证"""
        is_valid, error = _validate_copy_paths(self.source_file, self.dest_file)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_copy_paths_source_not_exist(self):
        """测试源路径不存在"""
        is_valid, error = _validate_copy_paths("/nonexistent/path", self.dest_file)
        self.assertFalse(is_valid)
        self.assertIn("does not exist", error)
    
    def test_validate_copy_paths_same_path(self):
        """测试源路径和目标路径相同"""
        is_valid, error = _validate_copy_paths(self.source_file, self.source_file)
        self.assertFalse(is_valid)
        self.assertIn("are the same", error)
    
    def test_validate_copy_paths_directory_inside_itself(self):
        """测试目录复制到自身内部"""
        # 创建源目录
        source_dir = os.path.join(self.test_dir, "source_dir")
        os.makedirs(source_dir)
        
        # 目标在源目录内部
        dest_inside = os.path.join(source_dir, "subdir", "copy")
        is_valid, error = _validate_copy_paths(source_dir, dest_inside)
        self.assertFalse(is_valid)
        self.assertIn("inside source", error)
    
    def test_create_parent_dirs_if_needed_exists(self):
        """测试父目录已存在的情况"""
        dest = os.path.join(self.test_dir, "subdir", "file.txt")
        success, error = _create_parent_dirs_if_needed(dest, False)
        self.assertFalse(success)  # 父目录不存在且create_parent_dirs=False
        
        success, error = _create_parent_dirs_if_needed(dest, True)
        self.assertTrue(success)  # 应该创建父目录
        self.assertTrue(os.path.exists(os.path.dirname(dest)))
    
    def test_check_overwrite_not_exist(self):
        """测试目标不存在的情况"""
        can_proceed, error = _check_overwrite(self.dest_file, False, False)
        self.assertTrue(can_proceed)
        self.assertIsNone(error)
    
    def test_check_overwrite_exists_no_overwrite(self):
        """测试目标存在但不允许覆盖的情况"""
        # 创建目标文件
        with open(self.dest_file, "w") as f:
            f.write("Existing content")
        
        can_proceed, error = _check_overwrite(self.dest_file, False, False)
        self.assertFalse(can_proceed)
        self.assertIn("already exists", error)
    
    def test_check_overwrite_exists_with_overwrite(self):
        """测试目标存在且允许覆盖的情况"""
        # 创建目标文件
        with open(self.dest_file, "w") as f:
            f.write("Existing content")
        
        can_proceed, error = _check_overwrite(self.dest_file, True, False)
        self.assertTrue(can_proceed)
        self.assertIsNone(error)
    
    def test_check_overwrite_type_mismatch(self):
        """测试类型不匹配（文件vs目录）"""
        # 创建目标目录
        dest_dir = os.path.join(self.test_dir, "dest_dir")
        os.makedirs(dest_dir)
        
        # 尝试用文件覆盖目录
        can_proceed, error = _check_overwrite(dest_dir, True, False)
        self.assertFalse(can_proceed)
        self.assertIn("Cannot overwrite directory with file", error)
        
        # 尝试用目录覆盖文件（需要先创建目标文件）
        with open(self.dest_file, "w") as f:
            f.write("Test file")
        
        can_proceed, error = _check_overwrite(self.dest_file, True, True)
        self.assertFalse(can_proceed)
        self.assertIn("Cannot overwrite file with directory", error)
    
    def test_count_files_and_bytes_file(self):
        """测试单个文件的计数"""
        self.assertIn("Cannot overwrite file with directory", error)
    
    def test_count_files_and_bytes_file(self):
        """测试单个文件的计数"""
        # 创建测试文件
        test_file = os.path.join(self.test_dir, "test.txt")
        content = "Hello, World!" * 100
        with open(test_file, "w") as f:
            f.write(content)
        
        file_count, total_bytes = _count_files_and_bytes(test_file)
        self.assertEqual(file_count, 1)
        self.assertGreater(total_bytes, 0)
    
    def test_count_files_and_bytes_directory(self):
        """测试目录的计数"""
        # 创建测试目录结构
        test_dir = os.path.join(self.test_dir, "test_dir")
        os.makedirs(test_dir)
        
        # 创建几个文件
        for i in range(3):
            file_path = os.path.join(test_dir, f"file{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Content {i}" * 10)
        
        # 创建子目录
        sub_dir = os.path.join(test_dir, "subdir")
        os.makedirs(sub_dir)
        with open(os.path.join(sub_dir, "subfile.txt"), "w") as f:
            f.write("Subfile content")
        
        file_count, total_bytes = _count_files_and_bytes(test_dir)
        self.assertEqual(file_count, 4)  # 3个文件 + 1个子文件
        self.assertGreater(total_bytes, 0)
    
    def test_copy_with_stats_file(self):
        """测试文件复制统计"""
        dest = os.path.join(self.test_dir, "copy.txt")
        success, error, files_copied, bytes_copied = _copy_with_stats(
            self.source_file, dest, True, True
        )
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(files_copied, 1)
        self.assertGreater(bytes_copied, 0)
        self.assertTrue(os.path.exists(dest))
    
    def test_copy_with_stats_directory(self):
        """测试目录复制统计"""
        # 创建源目录
        source_dir = os.path.join(self.test_dir, "source_dir")
        os.makedirs(source_dir)
        
        # 创建几个文件
        for i in range(2):
            file_path = os.path.join(source_dir, f"file{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"Content {i}" * 20)
        
        dest_dir = os.path.join(self.test_dir, "dest_dir")
        success, error, files_copied, bytes_copied = _copy_with_stats(
            source_dir, dest_dir, True, True
        )
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(files_copied, 2)
        self.assertGreater(bytes_copied, 0)
        self.assertTrue(os.path.exists(dest_dir))
    
    def test_copy_with_stats_directory_non_recursive(self):
        """测试非递归目录复制"""
        # 创建源目录
        source_dir = os.path.join(self.test_dir, "source_dir")
        os.makedirs(source_dir)
        
        # 创建文件（不会被复制）
        file_path = os.path.join(source_dir, "file.txt")
        with open(file_path, "w") as f:
            f.write("Content")
        
        dest_dir = os.path.join(self.test_dir, "dest_dir")
        success, error, files_copied, bytes_copied = _copy_with_stats(
            source_dir, dest_dir, False, True
        )
        
        self.assertTrue(success)
        self.assertIsNone(error)
        self.assertEqual(files_copied, 0)  # 非递归，只创建目录，不复制文件
        self.assertTrue(os.path.exists(dest_dir))
        self.assertFalse(os.path.exists(os.path.join(dest_dir, "file.txt")))


class TestFileCopyFunction(unittest.TestCase):
    """测试file_copy主函数"""
    
    def setUp(self):
        # 创建临时目录结构
        self.test_dir = tempfile.mkdtemp()
        self.source_file = os.path.join(self.test_dir, "source.txt")
        self.dest_file = os.path.join(self.test_dir, "dest.txt")
        self.source_dir = os.path.join(self.test_dir, "source_dir")
        self.dest_dir = os.path.join(self.test_dir, "dest_dir")
        
        # 创建源文件
        with open(self.source_file, "w") as f:
            f.write("Test content for file copy\nLine 2\nLine 3")
        
        # 创建源目录和文件
        os.makedirs(self.source_dir)
        for i in range(2):
            file_path = os.path.join(self.source_dir, f"file{i}.txt")
            with open(file_path, "w") as f:
                f.write(f"File {i} content")
    
    def tearDown(self):
        # 清理临时目录
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _parse_result(self, result_str):
        """解析file_copy返回的JSON字符串"""
        return json.loads(result_str)
    
    def test_file_copy_success(self):
        """测试成功的文件复制"""
        result_str = file_copy(self.source_file, self.dest_file)
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["operation"], "copy")
        self.assertEqual(result["source"], self.source_file)
        self.assertEqual(result["destination"], self.dest_file)
        self.assertFalse(result["is_directory"])
        self.assertEqual(result["files_copied"], 1)
        self.assertGreater(result["bytes_copied"], 0)
        self.assertIsNone(result.get("recursive"))  # 文件复制没有recursive参数
        self.assertTrue(result["preserve_metadata"])
        self.assertIn("durationMs", result)
        
        # 验证文件确实被复制了（源文件应仍然存在）
        self.assertTrue(os.path.exists(self.source_file))
        self.assertTrue(os.path.exists(self.dest_file))
        
        # 验证内容相同
        with open(self.source_file, "r") as f1, open(self.dest_file, "r") as f2:
            self.assertEqual(f1.read(), f2.read())
    
    def test_directory_copy_recursive(self):
        """测试递归目录复制"""
        result_str = file_copy(self.source_dir, self.dest_dir, recursive=True)
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["is_directory"])
        self.assertEqual(result["files_copied"], 2)
        self.assertGreater(result["bytes_copied"], 0)
        self.assertTrue(result["recursive"])
        
        # 验证目录和文件被复制
        self.assertTrue(os.path.exists(self.source_dir))
        self.assertTrue(os.path.exists(self.dest_dir))
        for i in range(2):
            self.assertTrue(os.path.exists(os.path.join(self.dest_dir, f"file{i}.txt")))
    
    def test_directory_copy_non_recursive(self):
        """测试非递归目录复制"""
        result_str = file_copy(self.source_dir, self.dest_dir, recursive=False)
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        self.assertTrue(result["is_directory"])
        self.assertEqual(result["files_copied"], 0)  # 非递归，只创建空目录
        self.assertEqual(result["bytes_copied"], 0)
        self.assertFalse(result["recursive"])
        
        # 验证目录被创建，但文件没有被复制
        self.assertTrue(os.path.exists(self.dest_dir))
        self.assertFalse(os.path.exists(os.path.join(self.dest_dir, "file0.txt")))
    
    def test_file_copy_with_overwrite(self):
        """测试带覆盖的文件复制"""
        # 先创建目标文件
        with open(self.dest_file, "w") as f:
            f.write("Old content")
        
        result_str = file_copy(
            source=self.source_file,
            destination=self.dest_file,
            overwrite=True
        )
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        
        # 验证新内容已覆盖旧内容
        with open(self.dest_file, "r") as f:
            content = f.read()
        self.assertEqual(content, "Test content for file copy\nLine 2\nLine 3")
    
    def test_file_copy_without_overwrite_fails(self):
        """测试不允许覆盖时的失败情况"""
        # 先创建目标文件
        with open(self.dest_file, "w") as f:
            f.write("Old content")
        
        result_str = file_copy(
            source=self.source_file,
            destination=self.dest_file,
            overwrite=False  # 默认值
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("already exists", result["error"])
        
        # 验证源文件仍然存在，目标文件未被修改
        self.assertTrue(os.path.exists(self.source_file))
        with open(self.dest_file, "r") as f:
            self.assertEqual(f.read(), "Old content")
    
    def test_file_copy_without_metadata_preservation(self):
        """测试不保留元数据的文件复制"""
        result_str = file_copy(
            source=self.source_file,
            destination=self.dest_file,
            preserve_metadata=False
        )
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        self.assertFalse(result["preserve_metadata"])
        
        # 文件应该被复制
        self.assertTrue(os.path.exists(self.dest_file))
    
    def test_file_copy_source_not_exist(self):
        """测试源文件不存在的情况"""
        result_str = file_copy(
            source="/nonexistent/path/file.txt",
            destination=self.dest_file
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("does not exist", result["error"])
    
    def test_file_copy_empty_source(self):
        """测试空源路径"""
        result_str = file_copy(
            source="",
            destination=self.dest_file
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("cannot be empty", result["error"])
    
    def test_file_copy_empty_destination(self):
        """测试空目标路径"""
        result_str = file_copy(
            source=self.source_file,
            destination=""
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("cannot be empty", result["error"])
    
    def test_file_copy_parent_dir_not_exist(self):
        """测试父目录不存在且不创建的情况"""
        dest_file = os.path.join(self.test_dir, "nonexistent", "subdir", "file.txt")
        
        result_str = file_copy(
            source=self.source_file,
            destination=dest_file,
            create_parent_dirs=False
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("does not exist", result["error"])
    
    def test_file_copy_parent_dir_create(self):
        """测试自动创建父目录"""
        dest_file = os.path.join(self.test_dir, "new", "subdir", "file.txt")
        
        result_str = file_copy(
            source=self.source_file,
            destination=dest_file,
            create_parent_dirs=True
        )
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        self.assertTrue(os.path.exists(os.path.dirname(dest_file)))
    
    def test_file_copy_shutil_error(self):
        """测试shutil复制错误（模拟）"""
        with patch('shutil.copy2') as mock_copy:
            mock_copy.side_effect = Exception("Mocked shutil.copy2 error")
            
            result_str = file_copy(self.source_file, self.dest_file)
            result = self._parse_result(result_str)
            
            self.assertFalse(result["success"])
            self.assertIn("Copy operation failed", result["error"])
    
    def test_file_copy_overwrite_directory_with_file(self):
        """测试用文件覆盖目录的失败情况"""
        # 创建目标目录
        os.makedirs(self.dest_dir)
        
        result_str = file_copy(
            source=self.source_file,
            destination=self.dest_dir,
            overwrite=True
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("Cannot overwrite directory with file", result["error"])
    
    def test_file_copy_overwrite_file_with_directory(self):
        """测试用目录覆盖文件的失败情况"""
        # 创建目标文件
        with open(self.dest_file, "w") as f:
            f.write("Some content")
        
        result_str = file_copy(
            source=self.source_dir,
            destination=self.dest_file,
            overwrite=True
        )
        result = self._parse_result(result_str)
        
        self.assertFalse(result["success"])
        self.assertIn("Cannot overwrite file with directory", result["error"])
    
    def test_file_copy_large_file(self):
        """测试大文件复制"""
        # 创建1MB的测试文件
        large_file = os.path.join(self.test_dir, "large_source.txt")
        dest_large = os.path.join(self.test_dir, "large_dest.txt")
        
        with open(large_file, "wb") as f:
            f.write(b"X" * 1024 * 1024)  # 1MB
        
        result_str = file_copy(large_file, dest_large)
        result = self._parse_result(result_str)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["bytes_copied"], 1024 * 1024)
        self.assertTrue(os.path.exists(dest_large))
        self.assertTrue(os.path.exists(large_file))  # 源文件应仍然存在
    
    def test_file_copy_symlink(self):
        """测试符号链接复制（如果支持）"""
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
            
            # 复制符号链接
            dest_symlink = os.path.join(self.test_dir, "symlink_copy.txt")
            result_str = file_copy(symlink_file, dest_symlink)
            result = self._parse_result(result_str)
            
            self.assertTrue(result["success"])
            # 符号链接可能被解引用或保持为链接，取决于shutil.copy2的实现
            # 我们只检查复制成功
            self.assertTrue(os.path.exists(dest_symlink))
            
        except (OSError, NotImplementedError):
            self.skipTest("符号链接创建失败，跳过测试")


class TestFileCopyToolIntegration(unittest.TestCase):
    """测试FileCopyTool集成"""
    
    def test_function_ai_decorator_presence(self):
        """测试function_ai装饰器存在"""
        from file.file_copy_tool import tools
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
    
    def test_module_exports(self):
        """测试模块导出"""
        from file.file_copy_tool import tools, TOOL_CALL_MAP
        
        self.assertIsInstance(tools, list)
        self.assertIsInstance(TOOL_CALL_MAP, dict)
        self.assertIn("file_copy", TOOL_CALL_MAP)
    
    def test_default_parameters(self):
        """测试默认参数"""
        import inspect
        from file.file_copy_tool import file_copy
        
        sig = inspect.signature(file_copy)
        params = sig.parameters
        
        self.assertIn('overwrite', params)
        self.assertEqual(params['overwrite'].default, False)
        
        self.assertIn('create_parent_dirs', params)
        self.assertEqual(params['create_parent_dirs'].default, False)
        
        self.assertIn('recursive', params)
        self.assertEqual(params['recursive'].default, True)
        
        self.assertIn('preserve_metadata', params)
        self.assertEqual(params['preserve_metadata'].default, True)
    
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
            
            from file.file_copy_tool import file_copy
            result_str = file_copy(source, dest)
            
            # 验证是有效的JSON
            result = json.loads(result_str)
            
            # 检查必需字段
            self.assertIn("success", result)
            self.assertIn("operation", result)
            self.assertIn("source", result)
            self.assertIn("destination", result)
            self.assertIn("durationMs", result)
            self.assertIn("is_directory", result)
            self.assertIn("files_copied", result)
            self.assertIn("bytes_copied", result)
            self.assertIn("preserve_metadata", result)
            
            # 成功时应该有这些字段
            if result["success"] and result["is_directory"]:
                self.assertIn("recursive", result)
            
        finally:
            shutil.rmtree(test_dir)


if __name__ == '__main__':
    unittest.main()