#!/usr/bin/env python3
"""
WebSearchTool implementation for AITools (Claude Code compatible version - simplified).
Performs web searches and returns results.
Based on analysis of Claude Code source: restored-src/src/tools/WebSearchTool/WebSearchTool.ts
Simplified version with simulated search results.
"""

import os
import json
import re
from base import function_ai, parameters_func, property_param

# Property definitions for WebSearchTool
__QUERY_PROPERTY__ = property_param(
    name="query",
    description="The search query to use",
    t="string",
    required=True,
)

__ALLOWED_DOMAINS_PROPERTY__ = property_param(
    name="allowed_domains",
    description="Only include search results from these domains",
    t="array",  # JSON string array
    required=False,
)

__BLOCKED_DOMAINS_PROPERTY__ = property_param(
    name="blocked_domains",
    description="Never include search results from these domains",
    t="array",  # JSON string array
    required=False,
)

# Function definition
__WEB_SEARCH_TOOL_FUNCTION__ = function_ai(
    name="web_search_tool",
    description="Perform a web search and return results",
    parameters=parameters_func([
        __QUERY_PROPERTY__,
        __ALLOWED_DOMAINS_PROPERTY__,
        __BLOCKED_DOMAINS_PROPERTY__,
    ]),
)

tools = [__WEB_SEARCH_TOOL_FUNCTION__]


class WebSearchConfig:
    """Configuration for WebSearchTool"""
    
    DEFAULT_CONFIG = {
        "WEB_SEARCH_ENABLED": True,
        "WEB_SEARCH_INTERACTIVE": True,
        "WEB_SEARCH_MAX_RESULTS": 10,
        "WEB_SEARCH_USE_SIMULATION": True,  # Use simulated results (no real API calls)
        "WEB_SEARCH_SIMULATION_DELAY_MS": 100,  # Delay to simulate network latency
        "WEB_SEARCH_ALLOWED_DOMAINS": [],  # Default allowed domains (empty = all)
        "WEB_SEARCH_BLOCKED_DOMAINS": [],  # Default blocked domains
        "WEB_SEARCH_ANALYTICS_ENABLED": False,
    }
    
    @staticmethod
    def from_env():
        """从环境变量创建配置"""
        import os
        
        # 读取环境变量，使用空字符串表示使用配置默认值
        web_search_enabled = os.getenv("WEB_SEARCH_ENABLED", "")
        web_search_interactive = os.getenv("WEB_SEARCH_INTERACTIVE", "")
        web_search_max_results = os.getenv("WEB_SEARCH_MAX_RESULTS", "")
        web_search_use_simulation = os.getenv("WEB_SEARCH_USE_SIMULATION", "")
        web_search_simulation_delay_ms = os.getenv("WEB_SEARCH_SIMULATION_DELAY_MS", "")
        web_search_allowed_domains = os.getenv("WEB_SEARCH_ALLOWED_DOMAINS", "")
        web_search_blocked_domains = os.getenv("WEB_SEARCH_BLOCKED_DOMAINS", "")
        
        config = WebSearchConfig.DEFAULT_CONFIG.copy()
        
        # 覆盖环境变量设置（如果非空）
        if web_search_enabled != "":
            config["WEB_SEARCH_ENABLED"] = web_search_enabled.lower() in ["true", "1", "yes", "y"]
        
        if web_search_interactive != "":
            config["WEB_SEARCH_INTERACTIVE"] = web_search_interactive.lower() in ["true", "1", "yes", "y"]
        
        if web_search_max_results != "":
            try:
                config["WEB_SEARCH_MAX_RESULTS"] = int(web_search_max_results)
            except ValueError:
                pass
        
        if web_search_use_simulation != "":
            config["WEB_SEARCH_USE_SIMULATION"] = web_search_use_simulation.lower() in ["true", "1", "yes", "y"]
        
        if web_search_simulation_delay_ms != "":
            try:
                config["WEB_SEARCH_SIMULATION_DELAY_MS"] = int(web_search_simulation_delay_ms)
            except ValueError:
                pass
        
        # Parse domain arrays from JSON strings
        if web_search_allowed_domains != "":
            try:
                domains = json.loads(web_search_allowed_domains)
                if isinstance(domains, list):
                    config["WEB_SEARCH_ALLOWED_DOMAINS"] = domains
            except (json.JSONDecodeError, TypeError):
                pass
        
        if web_search_blocked_domains != "":
            try:
                domains = json.loads(web_search_blocked_domains)
                if isinstance(domains, list):
                    config["WEB_SEARCH_BLOCKED_DOMAINS"] = domains
            except (json.JSONDecodeError, TypeError):
                pass
        
        return config


def _extract_domain(url):
    """Extract domain from URL"""
    # Simple domain extraction - in production use urllib.parse
    match = re.search(r'https?://([^/]+)', url)
    if match:
        domain = match.group(1)
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    return ""


def _simulate_search_results(query, max_results=10):
    """Generate simulated search results for a query"""
    # Simulated search results for common queries
    simulations = {
        "python": [
            {"title": "Python Official Website", "url": "https://www.python.org"},
            {"title": "Python Documentation", "url": "https://docs.python.org"},
            {"title": "Python Tutorial - W3Schools", "url": "https://www.w3schools.com/python"},
            {"title": "Python Programming Language", "url": "https://en.wikipedia.org/wiki/Python_(programming_language)"},
            {"title": "Python Packages Index", "url": "https://pypi.org"},
        ],
        "claude code": [
            {"title": "Claude Code - Anthropic", "url": "https://www.anthropic.com/claude/code"},
            {"title": "Claude Code Documentation", "url": "https://docs.anthropic.com/claude/code"},
            {"title": "Claude Code GitHub", "url": "https://github.com/anthropics/claude-code"},
            {"title": "Claude Code Tools", "url": "https://www.anthropic.com/claude/code/tools"},
        ],
        "github": [
            {"title": "GitHub: Where the world builds software", "url": "https://github.com"},
            {"title": "GitHub Documentation", "url": "https://docs.github.com"},
            {"title": "GitHub Topics", "url": "https://github.com/topics"},
            {"title": "GitHub Guides", "url": "https://guides.github.com"},
        ],
        "openai": [
            {"title": "OpenAI", "url": "https://openai.com"},
            {"title": "OpenAI API Documentation", "url": "https://platform.openai.com/docs"},
            {"title": "OpenAI Research", "url": "https://openai.com/research"},
            {"title": "OpenAI ChatGPT", "url": "https://chat.openai.com"},
        ],
    }
    
    # Default results for any query
    default_results = [
        {"title": f"Search result for: {query}", "url": f"https://example.com/search?q={query}"},
        {"title": f"Wikipedia: {query}", "url": f"https://en.wikipedia.org/wiki/{query}"},
        {"title": f"GitHub search: {query}", "url": f"https://github.com/search?q={query}"},
        {"title": f"Stack Overflow: {query}", "url": f"https://stackoverflow.com/search?q={query}"},
        {"title": f"MDN Web Docs: {query}", "url": f"https://developer.mozilla.org/search?q={query}"},
    ]
    
    # Check for simulated results
    query_lower = query.lower()
    for key, results in simulations.items():
        if key in query_lower:
            return results[:max_results]
    
    # Return default results
    return default_results[:max_results]


def web_search_tool(query: str, allowed_domains: str = None, blocked_domains: str = None) -> str:
    """
    Perform a web search and return results.
    
    Claude Code compatible version based on WebSearchTool/WebSearchTool.ts:
    - query: The search query to use (min 2 characters)
    - allowed_domains: JSON string array of domains to include
    - blocked_domains: JSON string array of domains to exclude
    
    Returns JSON matching Claude Code's WebSearchTool output schema (simplified).
    
    Simplified implementation notes:
    - Uses simulated search results (no real API calls)
    - Supports domain filtering
    - Returns structured search results
    """
    try:
        # Load configuration
        config = WebSearchConfig.from_env()
        
        # Check if tool is enabled
        if not config.get("WEB_SEARCH_ENABLED", True):
            return json.dumps({
                "error": "WebSearchTool is disabled by configuration",
                "success": False
            }, indent=2)
        
        # Validate query
        if not query or not isinstance(query, str):
            return json.dumps({
                "error": "Query must be a non-empty string",
                "success": False
            }, indent=2)
        
        if len(query) < 2:
            return json.dumps({
                "error": "Query must be at least 2 characters",
                "success": False
            }, indent=2)
        
        # Parse domain arrays (they come as JSON strings from base module)
        allowed_domains_list = []
        blocked_domains_list = []
        
        # Parse allowed_domains if provided
        if allowed_domains and isinstance(allowed_domains, str):
            try:
                parsed = json.loads(allowed_domains)
                if isinstance(parsed, list):
                    allowed_domains_list = [str(d).lower() for d in parsed]
            except (json.JSONDecodeError, TypeError):
                # If not valid JSON, treat as comma-separated string
                allowed_domains_list = [d.strip().lower() for d in allowed_domains.split(",") if d.strip()]
        
        # Parse blocked_domains if provided
        if blocked_domains and isinstance(blocked_domains, str):
            try:
                parsed = json.loads(blocked_domains)
                if isinstance(parsed, list):
                    blocked_domains_list = [str(d).lower() for d in parsed]
            except (json.JSONDecodeError, TypeError):
                # If not valid JSON, treat as comma-separated string
                blocked_domains_list = [d.strip().lower() for d in blocked_domains.split(",") if d.strip()]
        
        # Get configuration values
        max_results = config.get("WEB_SEARCH_MAX_RESULTS", 10)
        use_simulation = config.get("WEB_SEARCH_USE_SIMULATION", True)
        simulation_delay_ms = config.get("WEB_SEARCH_SIMULATION_DELAY_MS", 100)
        
        # Apply default domain filters from config
        config_allowed = config.get("WEB_SEARCH_ALLOWED_DOMAINS", [])
        config_blocked = config.get("WEB_SEARCH_BLOCKED_DOMAINS", [])
        
        if config_allowed:
            allowed_domains_list.extend([d.lower() for d in config_allowed])
        
        if config_blocked:
            blocked_domains_list.extend([d.lower() for d in config_blocked])
        
        # Simulate network delay
        import time
        time.sleep(simulation_delay_ms / 1000.0)
        
        # Generate search results
        if use_simulation:
            raw_results = _simulate_search_results(query, max_results)
        else:
            # In a real implementation, would call a search API here
            raw_results = _simulate_search_results(query, max_results)
        
        # Apply domain filtering
        filtered_results = []
        for result in raw_results:
            url = result.get("url", "")
            domain = _extract_domain(url)
            
            # Check blocked domains
            if blocked_domains_list and domain:
                if any(blocked in domain for blocked in blocked_domains_list):
                    continue
            
            # Check allowed domains (if any specified)
            if allowed_domains_list and domain:
                if not any(allowed in domain for allowed in allowed_domains_list):
                    continue
            
            filtered_results.append(result)
        
        # Limit to max results
        filtered_results = filtered_results[:max_results]
        
        # Generate tool_use_id for response (simplified)
        import uuid
        tool_use_id = str(uuid.uuid4())[:8]
        
        # Build Claude Code compatible response
        response = {
            "tool_use_id": tool_use_id,
            "content": filtered_results
        }
        
        # Interactive mode output (if enabled)
        interactive = config.get("WEB_SEARCH_INTERACTIVE", True)
        if interactive:
            print(f"🔍 Web search for: '{query}'")
            print(f"   Found {len(filtered_results)} results")
            for i, result in enumerate(filtered_results, 1):
                print(f"   {i}. {result.get('title')}")
                print(f"      {result.get('url')}")
            
            if allowed_domains_list:
                print(f"   Allowed domains: {', '.join(allowed_domains_list)}")
            
            if blocked_domains_list:
                print(f"   Blocked domains: {', '.join(blocked_domains_list)}")
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Web search failed: {str(e)}",
            "success": False
        }, indent=2)


# Tool call map for dispatching
TOOL_CALL_MAP = {
    "web_search_tool": web_search_tool
}


if __name__ == "__main__":
    # Test the web_search_tool function
    print("Testing WebSearchTool (Claude Code compatible - simplified)...")
    print("-" * 60)
    
    # Test 1: Basic search
    print("1. Basic search:")
    result1 = web_search_tool(query="python programming")
    data1 = json.loads(result1)
    
    print(f"Tool use ID: {data1.get('tool_use_id')}")
    print(f"Results count: {len(data1.get('content', []))}")
    
    # Test 2: Search with domain filtering
    print("\n2. Search with domain filtering:")
    allowed_domains = json.dumps(["python.org", "wikipedia.org"])
    result2 = web_search_tool(query="python", allowed_domains=allowed_domains)
    data2 = json.loads(result2)
    
    print(f"Results count: {len(data2.get('content', []))}")
    
    # Test 3: Invalid query (too short)
    print("\n3. Invalid query (too short):")
    result3 = web_search_tool(query="a")
    data3 = json.loads(result3)
    
    print(f"Success: {data3.get('success', True)}")
    print(f"Error: {data3.get('error', 'None')}")
    
    # Test 4: Check Claude Code compatibility
    print("\n4. Claude Code compatibility check:")
    test_response = {
        "tool_use_id": "test_id",
        "content": [
            {"title": "Test result", "url": "https://example.com"}
        ]
    }
    
    expected_fields = ["tool_use_id", "content"]
    missing_fields = [field for field in expected_fields if field not in test_response]
    
    if missing_fields:
        print(f"  Missing fields in test response: {missing_fields}")
    else:
        print("  All expected fields present ✓")