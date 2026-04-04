#!/usr/bin/env python3
"""
WebSearchTool implementation for AITools.
Provides web search functionality, similar to Claude Code's WebSearchTool.
Note: This is a simulated implementation since we don't have actual search API access.
"""

import os
import sys
import json
import time
import random
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import re

# AITools decorators
from base import function_ai, parameters_func, property_param

__WEB_SEARCH_PROPERTY_ONE__ = property_param(
    name="query",
    description="The search query to use. Minimum 2 characters.",
    t="string",
    required=True,
)

__WEB_SEARCH_PROPERTY_TWO__ = property_param(
    name="allowed_domains",
    description="Optional list of domains to restrict search results to.",
    t="string",
)

__WEB_SEARCH_PROPERTY_THREE__ = property_param(
    name="blocked_domains",
    description="Optional list of domains to exclude from search results.",
    t="string",
)

@function_ai(
    name="web_search",
    description="Search the web for information. This is a simulated implementation that returns example results.",
    category="network"
)
def web_search(
    query: str,
    allowed_domains: str = "",
    blocked_domains: str = ""
) -> str:
    """
    Perform a web search (simulated).
    
    This tool mimics Claude Code's WebSearchTool functionality with a simulated
    implementation since we don't have actual search API access.
    
    Args:
        query: Search query string (minimum 2 characters)
        allowed_domains: Comma-separated list of allowed domains (optional)
        blocked_domains: Comma-separated list of blocked domains (optional)
        
    Returns:
        JSON-formatted search results with query, results, and duration
    """
    start_time = time.time()
    
    try:
        # Validate inputs
        if not query or len(query.strip()) < 2:
            return json.dumps({
                "error": "Query must be at least 2 characters long",
                "query": query,
                "results": [],
                "durationSeconds": 0
            }, indent=2)
        
        # Parse domain lists
        allowed_list = []
        blocked_list = []
        
        if allowed_domains:
            allowed_list = [domain.strip().lower() for domain in allowed_domains.split(",") if domain.strip()]
        
        if blocked_domains:
            blocked_list = [domain.strip().lower() for domain in blocked_domains.split(",") if domain.strip()]
        
        # Check for conflicting domain restrictions
        if allowed_list and blocked_list:
            return json.dumps({
                "error": "Cannot specify both allowed_domains and blocked_domains in the same request",
                "query": query,
                "results": [],
                "durationSeconds": 0
            }, indent=2)
        
        # Generate simulated search results
        search_results = generate_simulated_results(query, allowed_list, blocked_list)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Format the response similar to Claude Code's output
        response = {
            "query": query,
            "results": search_results,
            "durationSeconds": round(duration, 2)
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        duration = time.time() - start_time
        return json.dumps({
            "error": f"Search error: {str(e)}",
            "query": query,
            "results": [],
            "durationSeconds": round(duration, 2)
        }, indent=2)


def generate_simulated_results(query: str, allowed_domains: List[str], blocked_domains: List[str]) -> List[Dict[str, Any]]:
    """
    Generate simulated search results based on the query.
    """
    # Base set of example domains for different query types
    tech_domains = ["github.com", "stackoverflow.com", "wikipedia.org", "docs.python.org", "medium.com"]
    news_domains = ["news.ycombinator.com", "bbc.com", "reuters.com", "techcrunch.com", "arxiv.org"]
    general_domains = ["example.com", "w3.org", "mozilla.org", "python.org", "opensource.org"]
    
    # Determine which domains to use based on query
    query_lower = query.lower()
    
    if any(keyword in query_lower for keyword in ["python", "code", "programming", "github", "stack", "api"]):
        domain_pool = tech_domains
        result_type = "technical"
    elif any(keyword in query_lower for keyword in ["news", "update", "latest", "today", "202", "current"]):
        domain_pool = news_domains
        result_type = "news"
    else:
        domain_pool = general_domains
        result_type = "general"
    
    # Apply domain filtering
    filtered_domains = []
    for domain in domain_pool:
        domain_lower = domain.lower()
        
        # Check if domain is blocked
        if blocked_domains and any(blocked in domain_lower for blocked in blocked_domains):
            continue
        
        # Check if domain is allowed (if allowed_domains is specified)
        if allowed_domains:
            if any(allowed in domain_lower for allowed in allowed_domains):
                filtered_domains.append(domain)
        else:
            filtered_domains.append(domain)
    
    # If no domains match the filter, use a default
    if not filtered_domains:
        filtered_domains = ["example.com", "wikipedia.org"]
    
    # Generate 3-8 results
    num_results = random.randint(3, 8)
    results = []
    
    for i in range(num_results):
        domain = random.choice(filtered_domains)
        title = generate_title(query, domain, i, result_type)
        url = generate_url(domain, query, i)
        
        # Create a result entry
        tool_use_id = f"search_{int(time.time())}_{i}"
        
        # Sometimes include text commentary (like Claude Code does)
        if random.random() < 0.3:  # 30% chance of text commentary
            results.append(f"Found result from {domain}: {title[:50]}...")
        
        # Add the actual search result
        results.append({
            "tool_use_id": tool_use_id,
            "content": [
                {
                    "title": title,
                    "url": url
                }
            ]
        })
    
    return results


def generate_title(query: str, domain: str, index: int, result_type: str) -> str:
    """Generate a simulated title for a search result."""
    query_words = query.split()
    main_topic = query_words[0] if query_words else query
    
    templates = {
        "technical": [
            f"How to {query} - Complete Guide",
            f"{query} Tutorial: Best Practices and Examples",
            f"Understanding {main_topic}: A Comprehensive Overview",
            f"{main_topic.capitalize()} Documentation and API Reference",
            f"GitHub Repository: {query} Implementation",
            f"Stack Overflow Discussion: {query} Solutions",
            f"Python {main_topic.capitalize()} Library Documentation"
        ],
        "news": [
            f"Latest News: {query}",
            f"Breaking: {query} Developments",
            f"{query} - Current Updates and Analysis",
            f"Industry Impact of {main_topic.capitalize()}",
            f"Expert Analysis: {query} Trends"
        ],
        "general": [
            f"What is {query}?",
            f"Introduction to {main_topic.capitalize()}",
            f"{query}: Definition and Examples",
            f"Learn About {main_topic.capitalize()}",
            f"Comprehensive Guide to {query}"
        ]
    }
    
    template_list = templates.get(result_type, templates["general"])
    title = random.choice(template_list)
    
    # Add domain indicator
    if random.random() < 0.5:
        title = f"{title} | {domain}"
    
    return title


def generate_url(domain: str, query: str, index: int) -> str:
    """Generate a simulated URL for a search result."""
    # Clean the query for URL
    query_slug = re.sub(r'[^a-zA-Z0-9]+', '-', query.lower()).strip('-')
    
    # Different URL patterns based on domain
    if "github.com" in domain:
        path = f"/user/{query_slug}/repo"
    elif "stackoverflow.com" in domain:
        path = f"/questions/{random.randint(100000, 999999)}/{query_slug}"
    elif "wikipedia.org" in domain:
        path = f"/wiki/{query_slug.capitalize()}"
    elif "docs.python.org" in domain:
        path = f"/3/library/{query_slug}.html"
    elif "arxiv.org" in domain:
        path = f"/abs/{random.randint(2000, 2300)}.{random.randint(10000, 99999)}"
    elif "news.ycombinator.com" in domain:
        path = f"/item?id={random.randint(30000000, 39999999)}"
    else:
        path = f"/{query_slug}/article/{index}"
    
    return f"https://{domain}{path}"


def validate_domain_filters(domains: List[str]) -> bool:
    """Validate domain filter strings."""
    domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    
    for domain in domains:
        if not re.match(domain_pattern, domain):
            return False
    
    return True


# Export tools
tools = [web_search]
TOOL_CALL_MAP = {
    "web_search": web_search
}

if __name__ == "__main__":
    # Test the web_search function
    print("Testing WebSearchTool...")
    print("-" * 60)
    
    # Test 1: Basic search
    print("1. Basic search for 'Python programming':")
    result = web_search("Python programming")
    print(json.dumps(json.loads(result), indent=2)[:500] + "..." if len(result) > 500 else result)
    
    # Test 2: Search with allowed domains
    print("\n2. Search with allowed domains (wikipedia.org, github.com):")
    result = web_search("machine learning", "wikipedia.org,github.com")
    print(json.dumps(json.loads(result), indent=2)[:400] + "..." if len(result) > 400 else result)
    
    # Test 3: Invalid query (too short)
    print("\n3. Invalid query (too short):")
    result = web_search("a")
    print(result)
    
    # Test 4: Conflicting domain filters
    print("\n4. Conflicting domain filters (should error):")
    result = web_search("test query", "example.com", "wikipedia.org")
    print(result)
    
    print("-" * 60)
    print("Test completed!")