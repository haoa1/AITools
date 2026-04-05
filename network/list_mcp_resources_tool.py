"""
ListMcpResourcesTool - MCP资源列表工具
Claude Code工具复刻，简化版本。
用于列出连接的MCP服务器提供的资源。
"""

import json
import time
import random
from typing import Dict, Any, List, Optional

# ===== 工具实现 =====

def list_mcp_resources_tool(
    server: Optional[str] = None,
) -> str:
    """
    列出MCP服务器提供的资源。
    
    参数:
        server: 可选的服务器名称，用于按服务器过滤资源
    
    返回:
        JSON字符串格式的MCP资源列表结果
    """
    start_time = time.time()
    
    try:
        # 模拟的MCP服务器和资源
        # 在实际Claude Code中，这会从连接的MCP服务器获取实时数据
        mock_servers = {
            "filesystem": [
                {
                    "uri": "file:///home/user/documents",
                    "name": "Documents Directory",
                    "mimeType": "inode/directory",
                    "description": "User documents directory",
                    "server": "filesystem"
                },
                {
                    "uri": "file:///home/user/projects",
                    "name": "Projects Directory",
                    "mimeType": "inode/directory",
                    "description": "User projects workspace",
                    "server": "filesystem"
                },
                {
                    "uri": "file:///tmp/logs",
                    "name": "Log Files",
                    "mimeType": "text/plain",
                    "description": "System and application log files",
                    "server": "filesystem"
                }
            ],
            "github": [
                {
                    "uri": "github://repos/user/project1",
                    "name": "Project 1 Repository",
                    "mimeType": "application/vnd.github.v3+json",
                    "description": "GitHub repository for project 1",
                    "server": "github"
                },
                {
                    "uri": "github://repos/user/project2",
                    "name": "Project 2 Repository",
                    "mimeType": "application/vnd.github.v3+json",
                    "description": "GitHub repository for project 2",
                    "server": "github"
                },
                {
                    "uri": "github://issues/user/project1",
                    "name": "Project 1 Issues",
                    "mimeType": "application/vnd.github.v3+json",
                    "description": "GitHub issues for project 1",
                    "server": "github"
                }
            ],
            "calendar": [
                {
                    "uri": "calendar://events/today",
                    "name": "Today's Events",
                    "mimeType": "application/calendar+json",
                    "description": "Calendar events for today",
                    "server": "calendar"
                },
                {
                    "uri": "calendar://events/upcoming",
                    "name": "Upcoming Events",
                    "mimeType": "application/calendar+json",
                    "description": "Upcoming calendar events",
                    "server": "calendar"
                }
            ],
            "weather": [
                {
                    "uri": "weather://current/local",
                    "name": "Current Local Weather",
                    "mimeType": "application/json",
                    "description": "Current weather conditions for local area",
                    "server": "weather"
                },
                {
                    "uri": "weather://forecast/local",
                    "name": "Local Weather Forecast",
                    "mimeType": "application/json",
                    "description": "Weather forecast for local area",
                    "server": "weather"
                }
            ]
        }
        
        # 过滤资源（如果指定了服务器）
        if server:
            if server in mock_servers:
                resources = mock_servers[server]
                server_list = [server]
            else:
                # 服务器不存在
                available_servers = list(mock_servers.keys())
                result = {
                    "success": False,
                    "error": f"Server '{server}' not found. Available servers: {', '.join(available_servers)}",
                    "durationMs": int((time.time() - start_time) * 1000),
                    "note": "Simplified implementation - using mock MCP data"
                }
                return json.dumps(result, ensure_ascii=False)
        else:
            # 返回所有服务器的资源
            resources = []
            for server_name, server_resources in mock_servers.items():
                resources.extend(server_resources)
            server_list = list(mock_servers.keys())
        
        # 构建结果
        result = {
            "success": True,
            "resources": resources,
            "serverFilter": server,
            "serversAvailable": server_list,
            "totalResources": len(resources),
            "timestamp": int(time.time() * 1000),
            "durationMs": int((time.time() - start_time) * 1000),
            "note": "Simplified implementation - using mock MCP data instead of real MCP connections"
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        # 错误处理
        result = {
            "success": False,
            "error": f"Failed to list MCP resources: {str(e)}",
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(result, ensure_ascii=False)


# ===== 工具注册 =====

# 工具定义
TOOL_DEF = {
    "type": "function",
    "function": {
        "name": "list_mcp_resources",
        "description": "List resources from connected MCP (Model Context Protocol) servers.",
        "parameters": {
            "type": "object",
            "properties": {
                "server": {
                    "type": "string",
                    "description": "Optional server name to filter resources by"
                }
            }
        }
    }
}

# 工具调用映射
TOOL_CALL_MAP = {
    "list_mcp_resources": list_mcp_resources_tool
}

# 工具列表
tools = [TOOL_DEF]

# ===== 模块导出 =====
__all__ = ["tools", "TOOL_CALL_MAP", "list_mcp_resources_tool"]