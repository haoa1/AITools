#!/usr/bin/env python3
"""
ToolSearchTool implementation for AITools (Claude Code compatible version).
Search for tools by name or keywords.
Simplified version focusing on basic tool discovery functionality.
"""

import os
import sys
import json
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from base import function_ai, parameters_func, property_param

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__TOOL_SEARCH_QUERY_PROPERTY__ = property_param(
    name="query",
    description="Query to find tools. Use keywords to search or 'select:<tool_name>' for direct selection.",
    t="string",
    required=True
)

__TOOL_SEARCH_MAX_RESULTS_PROPERTY__ = property_param(
    name="max_results",
    description="Maximum number of results to return (default: 5).",
    t="number",
    required=False
)

# ============================================================================
# CONFIGURATION CLASS
# ============================================================================

class ToolSearchConfig:
    """ToolSearchTool配置类"""
    
    @staticmethod
    def from_env():
        """从环境变量创建配置"""
        import os
        
        # 读取环境变量，使用空字符串表示使用配置默认值
        tool_search_enabled = os.getenv("TOOL_SEARCH_ENABLED", "")
        tool_search_interactive = os.getenv("TOOL_SEARCH_INTERACTIVE", "")
        tool_search_min_score = os.getenv("TOOL_SEARCH_MIN_SCORE", "")
        
        config = {
            "TOOL_SEARCH_ENABLED": True,  # 默认启用
            "TOOL_SEARCH_INTERACTIVE": True,  # 默认交互模式
            "TOOL_SEARCH_MIN_SCORE": 1,  # 最小匹配分数
            "TOOL_SEARCH_MAX_TOOLS": 100,  # 最大工具数
            "TOOL_SEARCH_ANALYTICS_ENABLED": False,  # 默认禁用分析
            "TOOL_SEARCH_CACHE_ENABLED": True,  # 缓存启用
        }
        
        # 覆盖环境变量设置（如果非空）
        if tool_search_enabled != "":
            config["TOOL_SEARCH_ENABLED"] = tool_search_enabled.lower() in ["true", "1", "yes", "y"]
        
        if tool_search_interactive != "":
            config["TOOL_SEARCH_INTERACTIVE"] = tool_search_interactive.lower() in ["true", "1", "yes", "y"]
        
        if tool_search_min_score != "":
            try:
                config["TOOL_SEARCH_MIN_SCORE"] = int(tool_search_min_score)
            except ValueError:
                pass
        
        return config

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _validate_parameters(query: str, max_results: Optional[int]) -> List[str]:
    """验证ToolSearchTool参数"""
    errors = []
    
    # 验证查询
    if not query or not isinstance(query, str):
        errors.append("'query' must be a non-empty string")
    
    # 验证最大结果数
    if max_results is not None:
        if not isinstance(max_results, int):
            errors.append("'max_results' must be an integer")
        elif max_results < 1:
            errors.append("'max_results' must be at least 1")
        elif max_results > 100:
            errors.append("'max_results' must be at most 100")
    
    return errors

def _parse_tool_name(name: str) -> Dict[str, Any]:
    """解析工具名称为可搜索的部分"""
    name_lower = name.lower()
    
    # 检查是否是MCP工具（简化版）
    is_mcp = name_lower.startswith("mcp__")
    
    # 分割工具名称为部分
    if is_mcp:
        # MCP工具：mcp__server__action
        without_prefix = name_lower.replace("mcp__", "")
        parts = without_prefix.replace("__", " ").replace("_", " ").split()
    else:
        # 常规工具：CamelCase或下划线分隔
        # CamelCase转空格：FileReadTool -> "file read tool"
        name_spaced = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        parts = name_spaced.lower().replace("_", " ").split()
    
    return {
        "parts": parts,
        "full": " ".join(parts),
        "is_mcp": is_mcp,
        "original": name
    }

def _get_tool_description(tool_name: str) -> str:
    """获取工具描述（简化版）"""
    # 在实际实现中，这里应该从工具注册表获取工具描述
    # 这里我们使用硬编码的映射作为简化版本
    tool_descriptions = {
        "FileReadTool": "Read content from a file",
        "FileWriteTool": "Write content to a file",
        "FileEditTool": "Edit content in a file",
        "FileMoveTool": "Move or rename a file",
        "FileCopyTool": "Copy a file or directory",
        "FileDeleteTool": "Delete a file or directory",
        "GlobTool": "Find files using glob patterns",
        "GrepTool": "Search for text in files",
        "BashTool": "Execute bash commands",
        "AgentTool": "Execute agent tasks",
        "ConfigTool": "Manage configuration",
        "SleepTool": "Sleep/wait for specified time",
        "ExitPlanModeV2Tool": "Exit plan mode",
        "SystemInfoTool": "Collect system information",
        "EnterPlanModeTool": "Enter plan mode",
        "TaskOutputTool": "Retrieve task output",
        "WebFetchTool": "Fetch web content",
        "HttpTool": "Make HTTP requests",
        "DownloadTool": "Download files",
        "PingTool": "Ping network hosts",
        "NetworkDiagnosticTool": "Diagnose network issues",
        "SkillTool": "Execute skills",
        "SkillSearchTool": "Search for skills",
        "AskUserQuestionTool": "Ask user questions",
        "TodoWriteTool": "Write todo items",
        "NotificationTool": "Send user notifications",
        "ConfirmDialogTool": "Show confirmation dialogs",
        "BriefTool": "Send messages to user",
        "ToolSearchTool": "Search for tools",
    }
    
    return tool_descriptions.get(tool_name, f"Tool: {tool_name}")

def _get_search_hint(tool_name: str) -> Optional[str]:
    """获取工具搜索提示（简化版）"""
    # 在实际实现中，这里应该从工具注册表获取搜索提示
    # 这里我们使用硬编码的映射作为简化版本
    search_hints = {
        "FileReadTool": "read files content",
        "FileWriteTool": "write create files",
        "FileEditTool": "edit modify files",
        "FileMoveTool": "move rename files",
        "FileCopyTool": "copy duplicate files",
        "FileDeleteTool": "delete remove files",
        "GlobTool": "find search files patterns",
        "GrepTool": "search text content files",
        "BashTool": "execute shell commands terminal",
        "AgentTool": "run tasks agents",
        "ConfigTool": "manage settings configuration",
        "SleepTool": "wait delay pause",
        "ExitPlanModeV2Tool": "exit leave plan mode",
        "SystemInfoTool": "system information cpu memory disk network",
        "EnterPlanModeTool": "enter start plan mode",
        "TaskOutputTool": "get retrieve task output results",
        "WebFetchTool": "fetch get web pages content",
        "HttpTool": "http requests api get post",
        "DownloadTool": "download files urls",
        "PingTool": "ping network connectivity hosts",
        "NetworkDiagnosticTool": "diagnose network issues ports dns ssl",
        "SkillTool": "execute run skills",
        "SkillSearchTool": "search find skills",
        "AskUserQuestionTool": "ask user questions choices",
        "TodoWriteTool": "write create todo items tasks",
        "NotificationTool": "send notify user messages alerts",
        "ConfirmDialogTool": "confirm dialogs user input",
        "BriefTool": "send messages user communication",
        "ToolSearchTool": "search find tools discover",
    }
    
    return search_hints.get(tool_name)

def _get_all_tools() -> List[str]:
    """获取所有可用工具列表（简化版）"""
    # 在实际实现中，这里应该从工具注册系统获取
    # 这里我们返回已知的工具列表
    return [
        "FileReadTool",
        "FileWriteTool", 
        "FileEditTool",
        "FileMoveTool",
        "FileCopyTool",
        "FileDeleteTool",
        "GlobTool",
        "GrepTool",
        "BashTool",
        "AgentTool",
        "ConfigTool",
        "SleepTool",
        "ExitPlanModeV2Tool",
        "SystemInfoTool",
        "EnterPlanModeTool",
        "TaskOutputTool",
        "WebFetchTool",
        "HttpTool",
        "DownloadTool",
        "PingTool",
        "NetworkDiagnosticTool",
        "SkillTool",
        "SkillSearchTool",
        "AskUserQuestionTool",
        "TodoWriteTool",
        "NotificationTool",
        "ConfirmDialogTool",
        "BriefTool",
        "ToolSearchTool",
    ]

def _compile_term_patterns(terms: List[str]) -> Dict[str, re.Pattern]:
    """为所有搜索项预编译正则表达式模式"""
    patterns = {}
    for term in terms:
        if term not in patterns:
            # 单词边界匹配
            pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
            patterns[term] = pattern
    return patterns

def _search_tools_with_keywords(query: str, max_results: int) -> List[str]:
    """基于关键词搜索工具"""
    query_lower = query.lower().strip()
    
    # 获取所有工具
    all_tools = _get_all_tools()
    
    # 快速路径：完全匹配工具名
    for tool_name in all_tools:
        if tool_name.lower() == query_lower:
            return [tool_name]
    
    # 检查MCP工具前缀
    if query_lower.startswith("mcp__") and len(query_lower) > 5:
        matches = []
        for tool_name in all_tools:
            if tool_name.lower().startswith(query_lower):
                matches.append(tool_name)
                if len(matches) >= max_results:
                    break
        if matches:
            return matches
    
    # 分割查询项
    query_terms = query_lower.split()
    if not query_terms:
        return []
    
    # 分离必需项（+前缀）和可选项
    required_terms = []
    optional_terms = []
    for term in query_terms:
        if term.startswith("+") and len(term) > 1:
            required_terms.append(term[1:])
        else:
            optional_terms.append(term)
    
    # 所有评分项
    all_scoring_terms = required_terms + optional_terms if required_terms else query_terms
    term_patterns = _compile_term_patterns(all_scoring_terms)
    
    # 候选工具（匹配所有必需项）
    candidate_tools = all_tools
    if required_terms:
        filtered_tools = []
        for tool_name in all_tools:
            tool_info = _parse_tool_name(tool_name)
            description = _get_tool_description(tool_name).lower()
            search_hint = _get_search_hint(tool_name)
            hint_lower = search_hint.lower() if search_hint else ""
            
            matches_all = True
            for term in required_terms:
                pattern = term_patterns.get(term)
                if not pattern:
                    continue
                
                # 检查工具名部分
                part_match = any(term == part for part in tool_info["parts"]) or \
                           any(term in part for part in tool_info["parts"])
                
                # 检查描述
                desc_match = bool(pattern.search(description))
                
                # 检查搜索提示
                hint_match = bool(pattern.search(hint_lower)) if hint_lower else False
                
                if not (part_match or desc_match or hint_match):
                    matches_all = False
                    break
            
            if matches_all:
                filtered_tools.append(tool_name)
        
        candidate_tools = filtered_tools
    
    # 评分和排序
    scored_tools = []
    for tool_name in candidate_tools:
        tool_info = _parse_tool_name(tool_name)
        description = _get_tool_description(tool_name).lower()
        search_hint = _get_search_hint(tool_name)
        hint_lower = search_hint.lower() if search_hint else ""
        
        score = 0
        for term in all_scoring_terms:
            pattern = term_patterns.get(term)
            if not pattern:
                continue
            
            # 精确部分匹配
            if term in tool_info["parts"]:
                score += 12 if tool_info["is_mcp"] else 10
            elif any(term in part for part in tool_info["parts"]):
                score += 6 if tool_info["is_mcp"] else 5
            
            # 完整名称回退
            if term in tool_info["full"] and score == 0:
                score += 3
            
            # 搜索提示匹配
            if hint_lower and pattern.search(hint_lower):
                score += 4
            
            # 描述匹配
            if pattern.search(description):
                score += 2
        
        if score > 0:
            scored_tools.append({"name": tool_name, "score": score})
    
    # 按分数排序并限制结果数
    scored_tools.sort(key=lambda x: x["score"], reverse=True)
    results = [item["name"] for item in scored_tools[:max_results] if item["score"] > 0]
    
    return results

def _handle_select_query(query: str) -> List[str]:
    """处理select:前缀的直接选择"""
    # 匹配 select:tool_name 或 select:tool1,tool2,tool3
    select_match = re.match(r'^select:(.+)$', query, re.IGNORECASE)
    if not select_match:
        return []
    
    requested_tools = [tool.strip() for tool in select_match.group(1).split(",") if tool.strip()]
    all_tools = _get_all_tools()
    
    found_tools = []
    missing_tools = []
    
    for tool_name in requested_tools:
        # 检查工具是否存在（不区分大小写）
        tool_exists = any(name.lower() == tool_name.lower() for name in all_tools)
        if tool_exists:
            # 获取正确的工具名（保持原始大小写）
            actual_name = next((name for name in all_tools if name.lower() == tool_name.lower()), tool_name)
            if actual_name not in found_tools:
                found_tools.append(actual_name)
        else:
            missing_tools.append(tool_name)
    
    return found_tools

def _log_search_outcome(query: str, matches: List[str], query_type: str):
    """记录搜索结果（简化版）"""
    try:
        from system.config import log_analytics_event
        log_analytics_event(
            "tool_search_outcome",
            {
                "query": query,
                "query_type": query_type,
                "match_count": len(matches),
                "has_matches": len(matches) > 0
            }
        )
    except:
        pass  # 分析是可选的

def _format_search_results(query: str, matches: List[str], config: Dict):
    """格式化搜索结果用于显示"""
    total_tools = len(_get_all_tools())
    
    if config["TOOL_SEARCH_INTERACTIVE"]:
        print(f"\n🔍 Tool Search Results for: '{query}'")
        print(f"   Total tools available: {total_tools}")
        print(f"   Matches found: {len(matches)}")
        
        if matches:
            print("\n   Matching tools:")
            for i, tool_name in enumerate(matches, 1):
                description = _get_tool_description(tool_name)
                print(f"   {i}. {tool_name} - {description}")
        else:
            print("\n   No matching tools found.")
            print("   Try different keywords or check tool names.")
    else:
        # 非交互模式
        if matches:
            print(f"[TOOL_SEARCH] Found {len(matches)} tools for '{query}': {', '.join(matches)}")
        else:
            print(f"[TOOL_SEARCH] No matches found for '{query}'")

# ============================================================================
# AI FUNCTION DEFINITION
# ============================================================================

__TOOL_SEARCH_FUNCTION__ = function_ai(
    name="tool_search",
    description="Search for tools by name or keywords. Use to discover available tools in the system.",
    parameters=parameters_func([
        __TOOL_SEARCH_QUERY_PROPERTY__,
        __TOOL_SEARCH_MAX_RESULTS_PROPERTY__
    ]),
)

tools = [__TOOL_SEARCH_FUNCTION__]

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def tool_search(query: str, max_results: Optional[int] = None):
    """
    Search for tools by name or keywords.
    
    Args:
        query: Query to find tools. Use keywords or 'select:<tool_name>'
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        Dictionary with matches, query, and total tools count
    """
    # 设置默认值
    if max_results is None:
        max_results = 5
    
    # 验证参数
    errors = _validate_parameters(query, max_results)
    if errors:
        raise ValueError(f"Parameter validation failed: {', '.join(errors)}")
    
    # 获取配置
    config = ToolSearchConfig.from_env()
    
    # 检查工具搜索是否启用
    if not config["TOOL_SEARCH_ENABLED"]:
        raise RuntimeError("Tool search tool is not enabled in configuration")
    
    # 限制最大结果数
    max_results = min(max_results, config["TOOL_SEARCH_MAX_TOOLS"])
    
    # 处理查询
    all_tools = _get_all_tools()
    total_tools = len(all_tools)
    
    # 检查select:前缀
    found_tools = _handle_select_query(query)
    query_type = "select" if found_tools else "keyword"
    
    # 如果不是select查询，进行关键词搜索
    if not found_tools:
        found_tools = _search_tools_with_keywords(query, max_results)
    
    # 应用最小分数过滤
    if not found_tools and config["TOOL_SEARCH_MIN_SCORE"] > 1:
        # 重新搜索但使用更高的最小分数阈值
        # 这里简化处理：如果第一次没找到，返回空结果
        pass
    
    # 记录搜索结果
    if config["TOOL_SEARCH_ANALYTICS_ENABLED"]:
        _log_search_outcome(query, found_tools, query_type)
    
    # 显示结果（如果交互模式）
    try:
        _format_search_results(query, found_tools, config)
    except Exception as e:
        # 回退到简单输出
        if found_tools:
            print(f"\nTool search found {len(found_tools)} tools: {', '.join(found_tools)}")
        else:
            print(f"\nNo tools found for query: {query}")
    
    # 准备响应数据
    response_data = {
        "matches": found_tools,
        "query": query,
        "total_deferred_tools": total_tools,  # 使用总工具数作为简化版本
    }
    
    # 注意：简化版本中不包含pending_mcp_servers字段
    
    return response_data

# ============================================================================
# CONFIG GETTER (for testing)
# ============================================================================

def _get_config():
    """获取当前配置（用于测试）"""
    return ToolSearchConfig.from_env()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = ["tools", "tool_search", "ToolSearchConfig", "_get_config"]