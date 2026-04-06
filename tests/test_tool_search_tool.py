#!/usr/bin/env python3
"""
ToolSearchTool单元测试

测试Claude Code兼容的ToolSearchTool实现。
测试工具搜索和发现功能。
"""

import os
import sys
import json
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from system.tool_search_tool import (
    tool_search, 
    _validate_parameters,
    _parse_tool_name,
    _get_tool_description,
    _get_search_hint,
    _get_all_tools,
    _search_tools_with_keywords,
    _handle_select_query,
    _get_config,
    ToolSearchConfig
)

class TestToolSearchTool:
    """ToolSearchTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_tool_search_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 设置环境变量以使用非交互模式
        os.environ["TOOL_SEARCH_INTERACTIVE"] = "false"
        os.environ["TOOL_SEARCH_ENABLED"] = "true"
        
        # 清理可能影响测试的其他环境变量
        for key in ["TOOL_SEARCH_ANALYTICS_ENABLED", "TOOL_SEARCH_MIN_SCORE", "TOOL_SEARCH_MAX_TOOLS"]:
            if key in os.environ:
                del os.environ[key]
    
    def teardown_method(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        
        # 清理环境变量
        for key in [
            "TOOL_SEARCH_INTERACTIVE",
            "TOOL_SEARCH_ENABLED",
            "TOOL_SEARCH_ANALYTICS_ENABLED",
            "TOOL_SEARCH_MIN_SCORE",
            "TOOL_SEARCH_MAX_TOOLS"
        ]:
            if key in os.environ:
                del os.environ[key]
    
    # ============================================================================
    # 参数验证测试
    # ============================================================================
    
    def test_validate_parameters_valid(self):
        """测试参数验证（有效）"""
        errors = _validate_parameters(
            query="file read",
            max_results=5
        )
        assert len(errors) == 0
        
        errors = _validate_parameters(
            query="file",
            max_results=None
        )
        assert len(errors) == 0
    
    def test_validate_parameters_invalid_query(self):
        """测试参数验证（无效查询）"""
        # 空查询
        errors = _validate_parameters(
            query="",
            max_results=5
        )
        assert "'query' must be a non-empty string" in errors[0]
        
        # 非字符串查询
        errors = _validate_parameters(
            query=None,
            max_results=5
        )
        assert "'query' must be a non-empty string" in errors[0]
    
    def test_validate_parameters_invalid_max_results(self):
        """测试参数验证（无效最大结果数）"""
        # 非整数
        errors = _validate_parameters(
            query="test",
            max_results="not_a_number"
        )
        assert "'max_results' must be an integer" in errors[0]
        
        # 小于1
        errors = _validate_parameters(
            query="test",
            max_results=0
        )
        assert "'max_results' must be at least 1" in errors[0]
        
        # 大于100
        errors = _validate_parameters(
            query="test",
            max_results=101
        )
        assert "'max_results' must be at most 100" in errors[0]
    
    # ============================================================================
    # 配置测试
    # ============================================================================
    
    def test_config_from_env(self):
        """测试从环境变量创建配置"""
        # 保存原始环境变量
        original_enabled = os.environ.get("TOOL_SEARCH_ENABLED")
        original_interactive = os.environ.get("TOOL_SEARCH_INTERACTIVE")
        original_min_score = os.environ.get("TOOL_SEARCH_MIN_SCORE")
        
        try:
            # 清理环境变量以测试默认值
            for key in ["TOOL_SEARCH_ENABLED", "TOOL_SEARCH_INTERACTIVE", "TOOL_SEARCH_MIN_SCORE"]:
                if key in os.environ:
                    del os.environ[key]
            
            # 测试默认值
            config = ToolSearchConfig.from_env()
            assert config["TOOL_SEARCH_ENABLED"] == True
            assert config["TOOL_SEARCH_INTERACTIVE"] == True
            assert config["TOOL_SEARCH_MIN_SCORE"] == 1
            
            # 测试环境变量覆盖
            os.environ["TOOL_SEARCH_ENABLED"] = "false"
            os.environ["TOOL_SEARCH_INTERACTIVE"] = "false"
            os.environ["TOOL_SEARCH_MIN_SCORE"] = "3"
            
            config = ToolSearchConfig.from_env()
            assert config["TOOL_SEARCH_ENABLED"] == False
            assert config["TOOL_SEARCH_INTERACTIVE"] == False
            assert config["TOOL_SEARCH_MIN_SCORE"] == 3
            
            # 测试空字符串使用默认值
            os.environ["TOOL_SEARCH_ENABLED"] = ""
            config = ToolSearchConfig.from_env()
            assert config["TOOL_SEARCH_ENABLED"] == True  # 应该使用默认值
        finally:
            # 恢复原始环境变量
            if original_enabled is not None:
                os.environ["TOOL_SEARCH_ENABLED"] = original_enabled
            else:
                if "TOOL_SEARCH_ENABLED" in os.environ:
                    del os.environ["TOOL_SEARCH_ENABLED"]
                    
            if original_interactive is not None:
                os.environ["TOOL_SEARCH_INTERACTIVE"] = original_interactive
            else:
                if "TOOL_SEARCH_INTERACTIVE" in os.environ:
                    del os.environ["TOOL_SEARCH_INTERACTIVE"]
                    
            if original_min_score is not None:
                os.environ["TOOL_SEARCH_MIN_SCORE"] = original_min_score
            else:
                if "TOOL_SEARCH_MIN_SCORE" in os.environ:
                    del os.environ["TOOL_SEARCH_MIN_SCORE"]
    
    def test_get_config(self):
        """测试获取配置函数"""
        config = _get_config()
        assert isinstance(config, dict)
        assert "TOOL_SEARCH_ENABLED" in config
        assert "TOOL_SEARCH_INTERACTIVE" in config
    
    # ============================================================================
    # 辅助函数测试
    # ============================================================================
    
    def test_parse_tool_name(self):
        """测试工具名称解析"""
        # 常规工具
        result = _parse_tool_name("FileReadTool")
        assert result["parts"] == ["file", "read", "tool"]
        assert result["full"] == "file read tool"
        assert result["is_mcp"] == False
        assert result["original"] == "FileReadTool"
        
        # 下划线分隔工具
        result = _parse_tool_name("file_read_tool")
        assert result["parts"] == ["file", "read", "tool"]
        assert result["full"] == "file read tool"
        assert result["is_mcp"] == False
        
        # MCP工具（简化版本）
        result = _parse_tool_name("mcp__server__action")
        assert result["is_mcp"] == True
        # 注意：我们的简化版本会将mcp__前缀移除并分割
    
    def test_get_tool_description(self):
        """测试获取工具描述"""
        # 已知工具
        description = _get_tool_description("FileReadTool")
        assert description == "Read content from a file"
        
        description = _get_tool_description("BashTool")
        assert description == "Execute bash commands"
        
        # 未知工具
        description = _get_tool_description("UnknownTool")
        assert description == "Tool: UnknownTool"
    
    def test_get_search_hint(self):
        """测试获取搜索提示"""
        # 已知工具
        hint = _get_search_hint("FileReadTool")
        assert hint == "read files content"
        
        hint = _get_search_hint("BashTool")
        assert hint == "execute shell commands terminal"
        
        # 未知工具
        hint = _get_search_hint("UnknownTool")
        assert hint is None
    
    def test_get_all_tools(self):
        """测试获取所有工具列表"""
        tools = _get_all_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert "FileReadTool" in tools
        assert "BashTool" in tools
        assert "ToolSearchTool" in tools  # 工具本身应该在列表中
    
    def test_search_tools_with_keywords(self):
        """测试关键词搜索"""
        # 精确名称搜索
        results = _search_tools_with_keywords("FileReadTool", 5)
        assert "FileReadTool" in results
        
        # 部分名称搜索
        results = _search_tools_with_keywords("file", 10)
        assert "FileReadTool" in results
        assert "FileWriteTool" in results
        assert "FileEditTool" in results
        
        # 功能搜索
        results = _search_tools_with_keywords("read", 5)
        assert "FileReadTool" in results
        
        # 描述搜索
        results = _search_tools_with_keywords("content", 5)
        assert "FileReadTool" in results
        
        # 限制结果数
        results = _search_tools_with_keywords("file", 2)
        assert len(results) <= 2
    
    def test_search_tools_with_keywords_no_matches(self):
        """测试关键词搜索 - 无匹配"""
        results = _search_tools_with_keywords("nonexistenttoolxyz", 5)
        assert len(results) == 0
    
    def test_search_tools_with_keywords_mcp_prefix(self):
        """测试MCP前缀搜索"""
        # 注意：我们的简化版本没有真正的MCP工具，但会检查前缀
        results = _search_tools_with_keywords("mcp__test", 5)
        # 由于没有真正的MCP工具，可能返回空列表或进行常规搜索
        # 这个测试主要是确保函数不会崩溃
    
    def test_handle_select_query(self):
        """测试处理select查询"""
        # 单个工具
        results = _handle_select_query("select:FileReadTool")
        assert results == ["FileReadTool"]
        
        # 多个工具
        results = _handle_select_query("select:FileReadTool,FileWriteTool")
        assert "FileReadTool" in results
        assert "FileWriteTool" in results
        
        # 不区分大小写
        results = _handle_select_query("select:filereadtool")
        assert "FileReadTool" in results  # 应该返回正确的大小写
        
        # 无效查询格式
        results = _handle_select_query("not a select query")
        assert results == []
        
        # 包含空格
        results = _handle_select_query("select: FileReadTool , FileWriteTool ")
        assert "FileReadTool" in results
        assert "FileWriteTool" in results
        
        # 未知工具
        results = _handle_select_query("select:UnknownTool")
        assert len(results) == 0
    
    # ============================================================================
    # 主函数测试
    # ============================================================================
    
    def test_tool_search_keyword(self):
        """测试关键词搜索"""
        with patch('system.tool_search_tool._format_search_results'):
            result = tool_search("file read")
            
            # 验证结果结构
            assert "matches" in result
            assert "query" in result
            assert "total_deferred_tools" in result
            assert result["query"] == "file read"
            assert isinstance(result["matches"], list)
            assert isinstance(result["total_deferred_tools"], int)
            assert result["total_deferred_tools"] > 0
            
            # 验证应该找到FileReadTool
            assert "FileReadTool" in result["matches"]
    
    def test_tool_search_select(self):
        """测试select查询"""
        with patch('system.tool_search_tool._format_search_results'):
            result = tool_search("select:FileReadTool")
            
            # 验证结果
            assert "matches" in result
            assert result["query"] == "select:FileReadTool"
            assert "FileReadTool" in result["matches"]
    
    def test_tool_search_select_multiple(self):
        """测试select多个工具"""
        with patch('system.tool_search_tool._format_search_results'):
            result = tool_search("select:FileReadTool,FileWriteTool")
            
            assert "FileReadTool" in result["matches"]
            assert "FileWriteTool" in result["matches"]
    
    def test_tool_search_with_max_results(self):
        """测试带最大结果数的搜索"""
        with patch('system.tool_search_tool._format_search_results'):
            result = tool_search("file", max_results=2)
            
            assert len(result["matches"]) <= 2
    
    def test_tool_search_disabled(self):
        """测试工具搜索禁用"""
        os.environ["TOOL_SEARCH_ENABLED"] = "false"
        
        with pytest.raises(RuntimeError, match="Tool search tool is not enabled"):
            tool_search("file")
    
    def test_tool_search_validation_error(self):
        """测试参数验证失败"""
        with pytest.raises(ValueError, match="Parameter validation failed"):
            tool_search("", max_results=5)  # 空查询
    
    def test_tool_search_no_matches(self):
        """测试无匹配结果"""
        with patch('system.tool_search_tool._format_search_results'):
            result = tool_search("nonexistenttoolxyz123")
            
            assert len(result["matches"]) == 0
            assert result["query"] == "nonexistenttoolxyz123"
            assert result["total_deferred_tools"] > 0
    
    # ============================================================================
    # 集成测试
    # ============================================================================
    
    def test_full_workflow_tool_search(self):
        """完整工作流测试 - 工具搜索"""
        os.environ["TOOL_SEARCH_INTERACTIVE"] = "false"
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            result = tool_search("file")
        
        output = f.getvalue()
        assert "file" in output.lower() or "TOOL_SEARCH" in output
        
        # 验证结果结构
        assert "matches" in result
        assert "query" in result
        assert "total_deferred_tools" in result
        assert isinstance(result["matches"], list)
    
    def test_full_workflow_select_query(self):
        """完整工作流测试 - select查询"""
        os.environ["TOOL_SEARCH_INTERACTIVE"] = "false"
        
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            result = tool_search("select:FileReadTool")
        
        output = f.getvalue()
        
        # 验证结果
        assert "FileReadTool" in result["matches"]
        assert result["query"] == "select:FileReadTool"
    
    # ============================================================================
    # Claude Code兼容性测试
    # ============================================================================
    
    def test_claude_code_compatibility(self):
        """测试Claude Code兼容性"""
        # 测试函数装饰器属性
        from system.tool_search_tool import __TOOL_SEARCH_FUNCTION__
        assert 'function' in __TOOL_SEARCH_FUNCTION__
        function_def = __TOOL_SEARCH_FUNCTION__['function']
        assert function_def.get('name') == 'tool_search'
        
        # 测试参数定义
        params = function_def.get('parameters', {})
        properties = params.get('properties', {})
        assert 'query' in properties
        assert 'max_results' in properties
        
        # 测试必需参数
        required = params.get('required', [])
        assert 'query' in required
    
    def test_response_structure(self):
        """测试响应结构"""
        with patch('system.tool_search_tool._format_search_results'):
            result = tool_search("file")
            
            # 基本字段
            assert isinstance(result, dict)
            assert "matches" in result
            assert "query" in result
            assert "total_deferred_tools" in result
            
            # 字段类型
            assert isinstance(result["matches"], list)
            assert isinstance(result["query"], str)
            assert isinstance(result["total_deferred_tools"], int)
            
            # 所有匹配项应该是字符串
            for match in result["matches"]:
                assert isinstance(match, str)