#!/usr/bin/env python3
"""
GrepTool单元测试

测试Claude Code兼容的GrepTool简化实现。
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file.grep_tool import grep

class TestGrepTool:
    """GrepTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_grep_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 创建测试文件
        self._create_test_files()
    
    def teardown_method(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def _create_test_files(self):
        """创建测试文件"""
        # 文件1: 包含多个"test"单词
        with open("file1.txt", "w") as f:
            f.write("""This is a test file.
Line 2 with test word.
Line 3 without.
Another test here.
Last line with test.""")

        # 文件2: 包含"test"和"Test"（大小写）
        with open("file2.txt", "w") as f:
            f.write("""Test with capital T.
Another test with lowercase.
No match here.
Test again.""")

        # 文件3: 不包含"test"
        with open("file3.txt", "w") as f:
            f.write("""No matches in this file.
Just some random text.
Nothing to see here.""")

        # 嵌套目录中的文件
        os.makedirs("subdir", exist_ok=True)
        with open("subdir/file4.txt", "w") as f:
            f.write("""Test in subdirectory.
Another test in nested dir.""")

        # Python文件用于测试glob模式
        with open("script.py", "w") as f:
            f.write("""def test_function():
    \"\"\"Test function docstring.\"\"\"
    test_variable = "test"
    return test_variable

# Another test comment""")

    def test_grep_basic_pattern(self):
        """测试基本模式搜索"""
        result = grep(pattern="test")
        data = json.loads(result)
        
        assert data["mode"] == "files_with_matches"
        assert data["numFiles"] >= 3  # file1.txt, file2.txt, subdir/file4.txt
        
        # 检查文件名（处理相对路径，如./file1.txt）
        filenames = [os.path.basename(f) for f in data["filenames"]]
        assert "file1.txt" in filenames
        assert "file2.txt" in filenames
        # 对于子目录文件，检查完整路径是否包含
        subdir_files = [f for f in data["filenames"] if "subdir" in f]
        assert len(subdir_files) > 0
        
        file3_files = [f for f in data["filenames"] if "file3.txt" in f]
        assert len(file3_files) == 0
        assert "durationMs" in data
    
    def test_grep_with_path(self):
        """测试指定路径搜索"""
        result = grep(pattern="test", path=".")
        data = json.loads(result)
        
        assert data["mode"] == "files_with_matches"
        assert data["numFiles"] >= 3
    
    def test_grep_output_mode_content(self):
        """测试content输出模式"""
        result = grep(pattern="test", output_mode="content", n=True)
        data = json.loads(result)
        
        assert data["mode"] == "content"
        assert "content" in data
        assert data["numLines"] > 0
        assert "file1.txt" in data["content"] or "1:test" in data["content"]
    
    def test_grep_output_mode_count(self):
        """测试count输出模式"""
        result = grep(pattern="test", output_mode="count")
        data = json.loads(result)
        
        assert data["mode"] == "count"
        assert "content" in data
        assert "numMatches" in data
        assert data["numMatches"] > 0
        assert data["numFiles"] > 0
        
        # 验证计数内容格式
        lines = data["content"].split('\n')
        for line in lines:
            if line and ':' in line:
                filename, count = line.rsplit(':', 1)
                assert filename.endswith('.txt') or filename.endswith('.py')
                int(count)  # 应该能转换为整数
    
    def test_grep_case_insensitive(self):
        """测试大小写不敏感搜索"""
        # 大小写敏感搜索（默认）
        result_sensitive = grep(pattern="Test")
        data_sensitive = json.loads(result_sensitive)
        
        # 大小写不敏感搜索
        result_insensitive = grep(pattern="Test", i=True)
        data_insensitive = json.loads(result_insensitive)
        
        # 大小写不敏感应该找到更多匹配
        assert data_insensitive["numFiles"] >= data_sensitive["numFiles"]
    
    def test_grep_with_glob(self):
        """测试glob模式筛选"""
        # 只搜索Python文件
        result = grep(pattern="test", glob="*.py")
        data = json.loads(result)
        
        assert data["mode"] == "files_with_matches"
        # 应该只找到script.py
        filenames = [os.path.basename(f) for f in data["filenames"]]
        assert "script.py" in filenames
        assert "file1.txt" not in filenames
        assert "file2.txt" not in filenames
    
    def test_grep_with_context(self):
        """测试上下文行"""
        result = grep(
            pattern="test",
            output_mode="content",
            context=1,  # 前后各1行上下文
            n=True
        )
        data = json.loads(result)
        
        assert data["mode"] == "content"
        content = data["content"]
        
        # 检查是否包含上下文行（匹配行前后应该有其他行）
        lines = content.split('\n')
        # 简单验证：至少有一些行包含文件名
        assert any(':' in line for line in lines)
    
    def test_grep_head_limit(self):
        """测试输出限制"""
        # 先获取无限制的结果
        result_unlimited = grep(pattern="test", head_limit=0)
        data_unlimited = json.loads(result_unlimited)
        total_files = data_unlimited["numFiles"]
        
        # 应用限制
        limit = 2
        result_limited = grep(pattern="test", head_limit=limit)
        data_limited = json.loads(result_limited)
        
        assert data_limited["numFiles"] == min(limit, total_files)
        if total_files > limit:
            assert "appliedLimit" in data_limited
            assert data_limited["appliedLimit"] == limit
        else:
            assert "appliedLimit" not in data_limited
    
    def test_grep_with_offset(self):
        """测试偏移量"""
        result = grep(pattern="test", head_limit=2, offset=1)
        data = json.loads(result)
        
        assert "appliedOffset" in data
        assert data["appliedOffset"] == 1
        assert data["numFiles"] <= 2  # 应用了head_limit
    
    def test_grep_nonexistent_path(self):
        """测试不存在的路径"""
        result = grep(pattern="test", path="/nonexistent/path/12345")
        data = json.loads(result)
        
        assert "error" in data
        assert data["error"].startswith("Path does not exist")
        assert data["numFiles"] == 0
    
    def test_grep_invalid_pattern(self):
        """测试无效正则表达式（应该返回空结果而不是崩溃）"""
        result = grep(pattern="[invalid(regex")
        data = json.loads(result)
        
        # 应该返回有效结果（空或错误处理）
        assert "mode" in data
        assert "numFiles" in data
        # 无效模式应该返回0个文件
        assert data["numFiles"] == 0
    
    def test_grep_file_instead_of_directory(self):
        """测试直接搜索文件而不是目录"""
        result = grep(pattern="test", path="file1.txt")
        data = json.loads(result)
        
        assert data["mode"] == "files_with_matches"
        assert data["numFiles"] == 1
        assert "file1.txt" in data["filenames"][0] or "./file1.txt" == data["filenames"][0]
    
    def test_grep_claude_code_compatibility(self):
        """测试Claude Code兼容性"""
        # 测试所有输出模式
        for mode in ["files_with_matches", "content", "count"]:
            result = grep(
                pattern="test",
                output_mode=mode,
                n=True if mode == "content" else None,
                head_limit=10
            )
            data = json.loads(result)
            
            # 检查必需字段
            assert data["mode"] == mode
            assert "durationMs" in data
            assert "numFiles" in data
            
            if mode == "content":
                assert "content" in data
                assert "numLines" in data
            elif mode == "count":
                assert "content" in data
                assert "numMatches" in data
            else:  # files_with_matches
                assert "filenames" in data
    
    def test_grep_without_line_numbers(self):
        """测试不显示行号"""
        result = grep(pattern="test", output_mode="content", n=False)
        data = json.loads(result)
        
        assert data["mode"] == "content"
        content = data["content"]
        
        # 检查内容中不包含行号格式（简化的检查）
        lines = content.split('\n')
        for line in lines[:5]:  # 只检查前几行
            if line and ':' in line:
                # 应该只有文件名和内容，没有行号
                parts = line.split(':')
                # 至少应该有文件名和内容两部分
                assert len(parts) >= 2
    
    def test_grep_multiple_context_options(self):
        """测试多个上下文选项的优先级"""
        # 测试-B和-A选项
        result = grep(
            pattern="test",
            output_mode="content",
            B=1,
            A=1,
            n=True
        )
        data = json.loads(result)
        
        assert data["mode"] == "content"
        assert "content" in data
        # 内容应该包含匹配行
        
        # 测试context选项（应该覆盖-B和-A）
        result_context = grep(
            pattern="test",
            output_mode="content",
            context=2,
            n=True
        )
        data_context = json.loads(result_context)
        
        assert data_context["mode"] == "content"
        # 两个结果都应该有效

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])