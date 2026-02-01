from base import function_ai, parameters_func, property_param
import os
import json
import re
import urllib.parse
from typing import Dict, List, Any, Optional, Tuple
import traceback
import time

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__SEARCH_URL_PROP__ = property_param(
    name="url",
    description="URL of the webpage to fetch or search.",
    t="string",
    required=True
)

__SEARCH_QUERY_PROP__ = property_param(
    name="query",
    description="Search query or keywords.",
    t="string",
    required=True
)

__SEARCH_KEYWORDS_PROP__ = property_param(
    name="keywords",
    description="Keywords to search for (comma-separated or JSON array).",
    t="string",
    required=True
)

__SEARCH_API_KEY_PROP__ = property_param(
    name="api_key",
    description="API key for search services (Google Custom Search, etc.).",
    t="string"
)

__SEARCH_MAX_RESULTS_PROP__ = property_param(
    name="max_results",
    description="Maximum number of results to return.",
    t="integer"
)

__SEARCH_TIMEOUT_PROP__ = property_param(
    name="timeout",
    description="Request timeout in seconds.",
    t="integer"
)

__SEARCH_USER_AGENT_PROP__ = property_param(
    name="user_agent",
    description="Custom User-Agent header for web requests.",
    t="string"
)

__SEARCH_EXTRACT_TEXT_PROP__ = property_param(
    name="extract_text",
    description="Whether to extract and return text content (remove HTML).",
    t="boolean"
)

__SEARCH_FOLLOW_LINKS_PROP__ = property_param(
    name="follow_links",
    description="Whether to follow and search links from the page.",
    t="boolean"
)

__SEARCH_DEPTH_PROP__ = property_param(
    name="depth",
    description="Maximum depth for link following (1 = only current page).",
    t="integer"
)

__SEARCH_ENGINE_PROP__ = property_param(
    name="search_engine",
    description="Search engine to use: 'google', 'bing', 'duckduckgo'.",
    t="string"
)

__SEARCH_LANGUAGE_PROP__ = property_param(
    name="language",
    description="Language for search results (e.g., 'en', 'zh-CN').",
    t="string"
)

__SEARCH_REGION_PROP__ = property_param(
    name="region",
    description="Region for search results (e.g., 'us', 'cn', 'uk').",
    t="string"
)

__SEARCH_SAFE_SEARCH_PROP__ = property_param(
    name="safe_search",
    description="Enable safe search filtering.",
    t="boolean"
)

__SEARCH_START_DATE_PROP__ = property_param(
    name="start_date",
    description="Start date for search results (YYYY-MM-DD).",
    t="string"
)

__SEARCH_END_DATE_PROP__ = property_param(
    name="end_date",
    description="End date for search results (YYYY-MM-DD).",
    t="string"
)

# ============================================================================
# FUNCTION DEFINITIONS
# ============================================================================

# Basic webpage operations
__FETCH_WEBPAGE_FUNCTION__ = function_ai(
    name="fetch_webpage",
    description="Fetch webpage content and extract text. Returns webpage text or error.",
    parameters=parameters_func([
        __SEARCH_URL_PROP__,
        __SEARCH_TIMEOUT_PROP__,
        __SEARCH_USER_AGENT_PROP__,
        __SEARCH_EXTRACT_TEXT_PROP__
    ])
)

__SEARCH_WEBPAGE_FUNCTION__ = function_ai(
    name="search_webpage",
    description="Search for keywords within a webpage. Returns matching content.",
    parameters=parameters_func([
        __SEARCH_URL_PROP__,
        __SEARCH_KEYWORDS_PROP__,
        __SEARCH_TIMEOUT_PROP__,
        __SEARCH_USER_AGENT_PROP__,
        __SEARCH_EXTRACT_TEXT_PROP__
    ])
)

__EXTRACT_LINKS_FUNCTION__ = function_ai(
    name="extract_links",
    description="Extract all links from a webpage. Returns list of URLs.",
    parameters=parameters_func([
        __SEARCH_URL_PROP__,
        __SEARCH_TIMEOUT_PROP__,
        __SEARCH_USER_AGENT_PROP__,
        __SEARCH_FOLLOW_LINKS_PROP__,
        __SEARCH_DEPTH_PROP__
    ])
)

# Search engine operations
__GOOGLE_SEARCH_FUNCTION__ = function_ai(
    name="google_search",
    description="Perform Google search using Custom Search API (requires API key). Returns search results.",
    parameters=parameters_func([
        __SEARCH_QUERY_PROP__,
        __SEARCH_API_KEY_PROP__,
        __SEARCH_MAX_RESULTS_PROP__,
        __SEARCH_LANGUAGE_PROP__,
        __SEARCH_REGION_PROP__,
        __SEARCH_SAFE_SEARCH_PROP__,
        __SEARCH_START_DATE_PROP__,
        __SEARCH_END_DATE_PROP__
    ])
)

__WEB_SEARCH_FUNCTION__ = function_ai(
    name="web_search",
    description="General web search (tries to use available methods). Returns search results.",
    parameters=parameters_func([
        __SEARCH_QUERY_PROP__,
        __SEARCH_ENGINE_PROP__,
        __SEARCH_MAX_RESULTS_PROP__,
        __SEARCH_LANGUAGE_PROP__,
        __SEARCH_TIMEOUT_PROP__
    ])
)

# Content extraction
__EXTRACT_ARTICLE_FUNCTION__ = function_ai(
    name="extract_article_content",
    description="Extract main article/content from a webpage (removes navigation, ads, etc.).",
    parameters=parameters_func([
        __SEARCH_URL_PROP__,
        __SEARCH_TIMEOUT_PROP__,
        __SEARCH_USER_AGENT_PROP__
    ])
)

__SUMMARIZE_WEBPAGE_FUNCTION__ = function_ai(
    name="summarize_webpage",
    description="Generate summary of webpage content (extracts key points).",
    parameters=parameters_func([
        __SEARCH_URL_PROP__,
        __SEARCH_TIMEOUT_PROP__,
        __SEARCH_USER_AGENT_PROP__,
        __SEARCH_MAX_RESULTS_PROP__  # Reused as max sentences for summary
    ])
)

# Advanced search
__DEEP_SEARCH_FUNCTION__ = function_ai(
    name="deep_search",
    description="Search for information across multiple pages/depth. Returns comprehensive results.",
    parameters=parameters_func([
        __SEARCH_QUERY_PROP__,
        __SEARCH_URL_PROP__,  # Starting URL
        __SEARCH_DEPTH_PROP__,
        __SEARCH_MAX_RESULTS_PROP__,
        __SEARCH_TIMEOUT_PROP__,
        __SEARCH_USER_AGENT_PROP__
    ])
)

__FIND_CONTACTS_FUNCTION__ = function_ai(
    name="find_contacts",
    description="Find contact information (emails, phone numbers) on a webpage.",
    parameters=parameters_func([
        __SEARCH_URL_PROP__,
        __SEARCH_TIMEOUT_PROP__,
        __SEARCH_USER_AGENT_PROP__
    ])
)

__EXTRACT_METADATA_FUNCTION__ = function_ai(
    name="extract_metadata",
    description="Extract metadata (title, description, keywords, author) from webpage.",
    parameters=parameters_func([
        __SEARCH_URL_PROP__,
        __SEARCH_TIMEOUT_PROP__,
        __SEARCH_USER_AGENT_PROP__
    ])
)

# List of all tools
tools = [
    __FETCH_WEBPAGE_FUNCTION__,
    __SEARCH_WEBPAGE_FUNCTION__,
    __EXTRACT_LINKS_FUNCTION__,
    __GOOGLE_SEARCH_FUNCTION__,
    __WEB_SEARCH_FUNCTION__,
    __EXTRACT_ARTICLE_FUNCTION__,
    __SUMMARIZE_WEBPAGE_FUNCTION__,
    __DEEP_SEARCH_FUNCTION__,
    __FIND_CONTACTS_FUNCTION__,
    __EXTRACT_METADATA_FUNCTION__
]

# ============================================================================
# DEPENDENCY MANAGEMENT
# ============================================================================

# Try to import required libraries with graceful fallback
_HAS_REQUESTS = False
_HAS_BEAUTIFULSOUP = False
_HAS_GOOGLE_API = False

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    requests = None

try:
    from bs4 import BeautifulSoup
    _HAS_BEAUTIFULSOUP = True
except ImportError:
    BeautifulSoup = None

try:
    from googleapiclient.discovery import build
    _HAS_GOOGLE_API = True
except ImportError:
    build = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _get_default_user_agent() -> str:
    """Get default user agent."""
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

def _parse_keywords(keywords_str: str) -> List[str]:
    """Parse keywords from string (could be comma-separated or JSON)."""
    if not keywords_str:
        return []
    
    try:
        # Try to parse as JSON array
        keywords = json.loads(keywords_str)
        if isinstance(keywords, list):
            return [str(k).strip() for k in keywords]
    except json.JSONDecodeError:
        pass
    
    # Parse as comma-separated string
    keywords = [k.strip() for k in keywords_str.split(',') if k.strip()]
    return keywords

def _fetch_url_content(url: str, timeout: int = 30, user_agent: str = None) -> Tuple[bool, Any]:
    """
    Fetch URL content.
    
    Returns: (success, content_or_error)
    """
    if not _HAS_REQUESTS:
        return False, "Error: requests library not installed. Please install with: pip install requests"
    
    try:
        headers = {}
        if user_agent:
            headers['User-Agent'] = user_agent
        else:
            headers['User-Agent'] = _get_default_user_agent()
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # Check content type
        content_type = response.headers.get('Content-Type', '').lower()
        if 'text/html' in content_type or 'text/plain' in content_type:
            return True, response.text
        else:
            return True, f"Non-text content (Content-Type: {content_type}). Size: {len(response.content)} bytes"
            
    except requests.exceptions.Timeout:
        return False, f"Error: Request to {url} timed out after {timeout} seconds"
    except requests.exceptions.HTTPError as e:
        return False, f"Error: HTTP error {e.response.status_code} for {url}"
    except requests.exceptions.ConnectionError:
        return False, f"Error: Failed to connect to {url}"
    except requests.exceptions.RequestException as e:
        return False, f"Error: Request failed: {str(e)}"
    except Exception as e:
        return False, f"Error: Unexpected error: {str(e)}"

def _extract_text_from_html(html_content: str) -> str:
    """Extract clean text from HTML content."""
    if not _HAS_BEAUTIFULSOUP:
        # Simple regex-based extraction as fallback
        # Remove script and style tags
        cleaned = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        cleaned = re.sub(r'<style[^>]*>.*?</style>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        # Remove HTML tags
        cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        return f"Error extracting text: {str(e)}"

def _extract_article_from_html(html_content: str) -> str:
    """Extract article/main content from HTML."""
    if not _HAS_BEAUTIFULSOUP:
        # Fallback to simple text extraction
        return _extract_text_from_html(html_content)
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Try to find article tag
        article = soup.find('article')
        if article:
            return _extract_text_from_html(str(article))
        
        # Try main content area
        main = soup.find('main')
        if main:
            return _extract_text_from_html(str(main))
        
        # Try common content containers
        content_selectors = [
            '#content', '.content', '.post-content', '.article-content',
            '.entry-content', '.story-content', '.text'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                return _extract_text_from_html(str(element))
        
        # Fallback to body, but remove navigation etc.
        body = soup.find('body')
        if body:
            # Remove navigation, headers, footers
            for elem in body.select('nav, header, footer, aside, .navbar, .menu, .sidebar'):
                elem.decompose()
            return _extract_text_from_html(str(body))
        
        # Last resort: extract all text
        return _extract_text_from_html(html_content)
        
    except Exception as e:
        return f"Error extracting article: {str(e)}"

def _extract_links_from_html(html_content: str, base_url: str) -> List[str]:
    """Extract all links from HTML content."""
    links = []
    
    if not _HAS_BEAUTIFULSOUP:
        # Simple regex extraction
        pattern = r'href=["\']([^"\']+)["\']'
        found_links = re.findall(pattern, html_content, re.IGNORECASE)
        
        for link in found_links:
            try:
                # Resolve relative URLs
                absolute_url = urllib.parse.urljoin(base_url, link)
                links.append(absolute_url)
            except:
                pass
        return links
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Skip empty, javascript, mailto, etc.
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            try:
                # Resolve relative URLs
                absolute_url = urllib.parse.urljoin(base_url, href)
                links.append(absolute_url)
            except:
                pass
        
        return list(set(links))  # Remove duplicates
    except Exception as e:
        # Fallback to regex
        pattern = r'href=["\']([^"\']+)["\']'
        found_links = re.findall(pattern, html_content, re.IGNORECASE)
        
        for link in found_links:
            try:
                if link and not link.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    absolute_url = urllib.parse.urljoin(base_url, link)
                    links.append(absolute_url)
            except:
                pass
        
        return list(set(links))

def _extract_metadata_from_html(html_content: str) -> Dict[str, str]:
    """Extract metadata from HTML."""
    metadata = {}
    
    if not _HAS_BEAUTIFULSOUP:
        # Simple regex extraction
        # Title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        if title_match:
            metadata['title'] = re.sub(r'\s+', ' ', title_match.group(1)).strip()
        
        # Meta tags
        meta_pattern = r'<meta[^>]+(?:name|property)=["\']([^"\']+)["\'][^>]+content=["\']([^"\']+)["\']'
        for match in re.finditer(meta_pattern, html_content, re.IGNORECASE):
            name = match.group(1).lower()
            content = match.group(2)
            
            if name in ['description', 'keywords', 'author', 'viewport']:
                metadata[name] = content
            elif 'og:' in name or 'twitter:' in name:
                metadata[name] = content
        
        return metadata
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Title
        title = soup.find('title')
        if title:
            metadata['title'] = title.get_text().strip()
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                name = name.lower()
                if name in ['description', 'keywords', 'author', 'viewport']:
                    metadata[name] = content
                elif 'og:' in name or 'twitter:' in name:
                    metadata[name] = content
        
        # Try to extract description from first paragraph if not found
        if 'description' not in metadata:
            first_p = soup.find('p')
            if first_p:
                description = first_p.get_text()[:200].strip()
                if description:
                    metadata['description'] = description + ('...' if len(first_p.get_text()) > 200 else '')
        
        return metadata
    except Exception as e:
        return metadata

def _find_contact_info(text: str) -> Dict[str, List[str]]:
    """Find contact information in text."""
    contacts = {
        'emails': [],
        'phone_numbers': [],
        'urls': []
    }
    
    # Email pattern
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    contacts['emails'] = list(set(emails))
    
    # Phone number patterns (international and local)
    phone_patterns = [
        r'\+\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{1,4}[\s-]?\d{1,9}',  # International
        r'\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}',  # US-style
        r'\d{4}[\s-]?\d{3}[\s-]?\d{3}',  # Other formats
    ]
    
    all_phones = []
    for pattern in phone_patterns:
        phones = re.findall(pattern, text)
        all_phones.extend(phones)
    
    contacts['phone_numbers'] = list(set(all_phones))
    
    # URL pattern (simple)
    url_pattern = r'https?://[^\s<>"\']+'
    urls = re.findall(url_pattern, text)
    contacts['urls'] = list(set(urls))
    
    return contacts

# ============================================================================
# MAIN FUNCTION IMPLEMENTATIONS
# ============================================================================

def fetch_webpage(url: str, timeout: int = 30, user_agent: str = None, 
                  extract_text: bool = True) -> str:
    """
    Fetch webpage content and extract text.
    
    Args:
        url: URL of the webpage
        timeout: Request timeout in seconds
        user_agent: Custom User-Agent header
        extract_text: Whether to extract and return text content
        
    Returns:
        Webpage content or error message
    """
    success, result = _fetch_url_content(url, timeout, user_agent)
    
    if not success:
        return result
    
    if not extract_text or not isinstance(result, str):
        return f"Successfully fetched content from {url}\nContent length: {len(result)} characters"
    
    # Extract text from HTML
    text_content = _extract_text_from_html(result)
    
    # Get metadata
    metadata = _extract_metadata_from_html(result)
    
    # Format output
    output = []
    output.append(f"Successfully fetched and extracted content from {url}")
    output.append(f"Content length: {len(text_content)} characters")
    
    if metadata.get('title'):
        output.append(f"Title: {metadata['title']}")
    
    if metadata.get('description'):
        output.append(f"Description: {metadata['description']}")
    
    output.append("\n" + "="*60)
    output.append("CONTENT:")
    output.append("="*60)
    
    # Truncate if too long
    if len(text_content) > 5000:
        output.append(text_content[:5000] + f"\n\n... (truncated, total {len(text_content)} characters)")
    else:
        output.append(text_content)
    
    return "\n".join(output)

def search_webpage(url: str, keywords: str, timeout: int = 30, 
                   user_agent: str = None, extract_text: bool = True) -> str:
    """
    Search for keywords within a webpage.
    
    Args:
        url: URL of the webpage
        keywords: Keywords to search for (comma-separated or JSON array)
        timeout: Request timeout in seconds
        user_agent: Custom User-Agent header
        extract_text: Whether to extract text before searching
        
    Returns:
        Search results or error message
    """
    # Parse keywords
    keyword_list = _parse_keywords(keywords)
    if not keyword_list:
        return "Error: No keywords provided"
    
    # Fetch webpage
    success, result = _fetch_url_content(url, timeout, user_agent)
    if not success:
        return result
    
    # Extract text if requested
    if extract_text:
        content = _extract_text_from_html(result)
    else:
        content = result
    
    # Search for keywords
    matches = {}
    for keyword in keyword_list:
        # Case-insensitive search
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        found_matches = list(pattern.finditer(content))
        
        if found_matches:
            matches[keyword] = []
            for match in found_matches[:10]:  # Limit matches per keyword
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end]
                matches[keyword].append(context)
    
    # Format output
    output = []
    output.append(f"Search results for {len(keyword_list)} keywords in {url}")
    output.append(f"Content length: {len(content)} characters")
    output.append("="*60)
    
    if not matches:
        output.append(f"No matches found for keywords: {', '.join(keyword_list)}")
        return "\n".join(output)
    
    for keyword, contexts in matches.items():
        output.append(f"\nKeyword: '{keyword}' - {len(contexts)} match(es)")
        output.append("-" * 40)
        
        for i, context in enumerate(contexts, 1):
            output.append(f"Match {i}:")
            output.append(f"  ...{context}...")
            output.append("")
    
    return "\n".join(output)

def extract_links(url: str, timeout: int = 30, user_agent: str = None,
                  follow_links: bool = False, depth: int = 1) -> str:
    """
    Extract all links from a webpage.
    
    Args:
        url: URL of the webpage
        timeout: Request timeout in seconds
        user_agent: Custom User-Agent header
        follow_links: Whether to follow and extract links from linked pages
        depth: Maximum depth for link following
        
    Returns:
        List of extracted links or error message
    """
    if depth < 1:
        depth = 1
    if depth > 3:
        return "Error: Depth limited to 3 for safety"
    
    all_links = set()
    urls_to_process = [(url, 1)]  # (url, current_depth)
    processed_urls = set()
    
    while urls_to_process:
        current_url, current_depth = urls_to_process.pop(0)
        
        if current_url in processed_urls:
            continue
        
        processed_urls.add(current_url)
        
        # Fetch webpage
        success, result = _fetch_url_content(current_url, timeout, user_agent)
        if not success:
            all_links.add(f"ERROR: {result}")
            continue
        
        # Extract links
        links = _extract_links_from_html(result, current_url)
        all_links.update(links)
        
        # Add to processing queue if following links and not at max depth
        if follow_links and current_depth < depth:
            for link in links[:10]:  # Limit to first 10 links per page for safety
                if link not in processed_urls:
                    urls_to_process.append((link, current_depth + 1))
    
    # Format output
    output = []
    output.append(f"Extracted {len(all_links)} unique links from {url}")
    if follow_links:
        output.append(f"Search depth: {depth} levels")
    output.append("="*60)
    
    # Sort links
    sorted_links = sorted(list(all_links))
    for i, link in enumerate(sorted_links, 1):
        output.append(f"{i:3}. {link}")
    
    return "\n".join(output)

def google_search(query: str, api_key: str = None, max_results: int = 10,
                  language: str = "en", region: str = "us", safe_search: bool = True,
                  start_date: str = None, end_date: str = None) -> str:
    """
    Perform Google search using Custom Search API.
    
    Args:
        query: Search query
        api_key: Google Custom Search API key (required)
        max_results: Maximum number of results to return
        language: Language code for results
        region: Region code for results
        safe_search: Enable safe search filtering
        start_date: Start date for results (YYYY-MM-DD)
        end_date: End date for results (YYYY-MM-DD)
        
    Returns:
        Search results or error message
    """
    if not api_key:
        return "Error: Google Custom Search API key is required. Get one from: https://developers.google.com/custom-search/v1/overview"
    
    if not _HAS_GOOGLE_API:
        return "Error: google-api-python-client library not installed. Install with: pip install google-api-python-client"
    
    try:
        # Initialize API client
        service = build("customsearch", "v1", developerKey=api_key)
        
        # Build search parameters
        params = {
            "q": query,
            "num": min(max_results, 10),  # API max is 10 per request
            "lr": f"lang_{language}",
            "cr": region,
            "safe": "high" if safe_search else "off"
        }
        
        # Add date range if provided
        if start_date or end_date:
            date_restrict = ""
            if start_date and end_date:
                date_restrict = f"daterange:{start_date}:{end_date}"
            elif start_date:
                date_restrict = f"after:{start_date}"
            elif end_date:
                date_restrict = f"before:{end_date}"
            
            if date_restrict:
                params["dateRestrict"] = date_restrict
        
        # Execute search
        result = service.cse().list(**params).execute()
        
        # Parse results
        output = []
        output.append(f"Google Search Results for: '{query}'")
        output.append(f"Found approximately {result.get('searchInformation', {}).get('totalResults', 0)} results")
        output.append(f"Search time: {result.get('searchInformation', {}).get('formattedSearchTime', 0)} seconds")
        output.append("="*60)
        
        items = result.get("items", [])
        if not items:
            output.append("No results found.")
            return "\n".join(output)
        
        for i, item in enumerate(items, 1):
            output.append(f"\n{i}. {item.get('title', 'No title')}")
            output.append(f"   URL: {item.get('link', 'No URL')}")
            
            snippet = item.get('snippet', '')
            if snippet:
                output.append(f"   Description: {snippet}")
            
            # Display info if available
            display_link = item.get('displayLink', '')
            if display_link:
                output.append(f"   Site: {display_link}")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"Error performing Google search: {str(e)}"

def web_search(query: str, search_engine: str = "google", max_results: int = 10,
               language: str = "en", timeout: int = 30) -> str:
    """
    General web search (tries to use available methods).
    
    Args:
        query: Search query
        search_engine: Search engine to use
        max_results: Maximum number of results
        language: Language for results
        timeout: Request timeout
        
    Returns:
        Search results or error message
    """
    # For now, this is a wrapper that provides guidance
    # In a real implementation, this could use different search APIs
    
    output = []
    output.append(f"Web Search Request: '{query}'")
    output.append(f"Search Engine: {search_engine}")
    output.append(f"Language: {language}")
    output.append(f"Max Results: {max_results}")
    output.append("="*60)
    
    if search_engine.lower() == "google":
        output.append("\nTo perform Google search, you need:")
        output.append("1. A Google Custom Search API key")
        output.append("2. google-api-python-client library installed")
        output.append("")
        output.append("Use the google_search function with your API key.")
        output.append("Get API key from: https://developers.google.com/custom-search/v1/overview")
        output.append("Install library: pip install google-api-python-client")
    
    elif search_engine.lower() == "bing":
        output.append("\nBing Search API requires:")
        output.append("1. Bing Search API key from Azure Portal")
        output.append("2. requests library for API calls")
        output.append("")
        output.append("Documentation: https://docs.microsoft.com/en-us/bing/search-apis/")
    
    elif search_engine.lower() == "duckduckgo":
        output.append("\nDuckDuckGo offers an HTML interface that can be scraped,")
        output.append("but official API is limited.")
        output.append("")
        output.append("Alternative: Use DuckDuckGo Instant Answer API")
        output.append("Example URL: https://api.duckduckgo.com/?q=query&format=json")
    
    else:
        output.append(f"\nSearch engine '{search_engine}' not directly supported.")
        output.append("Available options: google, bing, duckduckgo")
    
    output.append("\n" + "="*60)
    output.append("ALTERNATIVE APPROACH:")
    output.append("You can use the fetch_webpage and search_webpage functions")
    output.append("to manually search specific websites.")
    
    return "\n".join(output)

def extract_article_content(url: str, timeout: int = 30, user_agent: str = None) -> str:
    """
    Extract main article/content from a webpage.
    
    Args:
        url: URL of the webpage
        timeout: Request timeout in seconds
        user_agent: Custom User-Agent header
        
    Returns:
        Extracted article content or error message
    """
    success, result = _fetch_url_content(url, timeout, user_agent)
    if not success:
        return result
    
    # Extract article content
    article_content = _extract_article_from_html(result)
    
    # Get metadata
    metadata = _extract_metadata_from_html(result)
    
    # Format output
    output = []
    output.append(f"Article extracted from: {url}")
    
    if metadata.get('title'):
        output.append(f"Title: {metadata['title']}")
    
    if metadata.get('author'):
        output.append(f"Author: {metadata['author']}")
    
    output.append(f"Content length: {len(article_content)} characters")
    output.append("="*60)
    output.append("\nARTICLE CONTENT:")
    output.append("="*60)
    
    # Truncate if too long
    if len(article_content) > 10000:
        output.append(article_content[:10000] + f"\n\n... (truncated, total {len(article_content)} characters)")
    else:
        output.append(article_content)
    
    return "\n".join(output)

def summarize_webpage(url: str, timeout: int = 30, user_agent: str = None,
                      max_results: int = 5) -> str:
    """
    Generate summary of webpage content.
    
    Args:
        url: URL of the webpage
        timeout: Request timeout in seconds
        user_agent: Custom User-Agent header
        max_results: Maximum number of sentences for summary
        
    Returns:
        Summary or error message
    """
    success, result = _fetch_url_content(url, timeout, user_agent)
    if not success:
        return result
    
    # Extract text
    text_content = _extract_text_from_html(result)
    
    # Get metadata
    metadata = _extract_metadata_from_html(result)
    
    # Simple summarization: extract key sentences
    sentences = re.split(r'[.!?]+', text_content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    # Sort sentences by length (longer sentences often have more information)
    sentences.sort(key=len, reverse=True)
    
    # Take top sentences
    summary_sentences = sentences[:max_results]
    
    # Format output
    output = []
    output.append(f"Summary of: {url}")
    
    if metadata.get('title'):
        output.append(f"Title: {metadata['title']}")
    
    output.append(f"Original content: {len(text_content)} characters")
    output.append(f"Summary: {len(' '.join(summary_sentences))} characters")
    output.append("="*60)
    
    if not summary_sentences:
        output.append("Could not generate summary (no suitable sentences found).")
        output.append("\nFull content preview:")
        output.append(text_content[:500] + "..." if len(text_content) > 500 else text_content)
    else:
        output.append("\nKEY POINTS:")
        for i, sentence in enumerate(summary_sentences, 1):
            output.append(f"\n{i}. {sentence}")
    
    return "\n".join(output)

def deep_search(query: str, url: str = None, depth: int = 2, max_results: int = 20,
                timeout: int = 30, user_agent: str = None) -> str:
    """
    Search for information across multiple pages/depth.
    
    Args:
        query: Search query or keywords
        url: Starting URL (optional)
        depth: Search depth
        max_results: Maximum results to return
        timeout: Request timeout per page
        user_agent: Custom User-Agent header
        
    Returns:
        Comprehensive search results
    """
    if depth < 1:
        depth = 1
    if depth > 3:
        return "Error: Depth limited to 3 for safety"
    
    # Parse query as keywords
    keyword_list = _parse_keywords(query)
    if not keyword_list:
        return "Error: No search query provided"
    
    output = []
    output.append(f"Deep Search for: {', '.join(keyword_list)}")
    if url:
        output.append(f"Starting from: {url}")
    output.append(f"Search depth: {depth}")
    output.append("="*60)
    
    # If no starting URL, provide guidance
    if not url:
        output.append("\nNo starting URL provided.")
        output.append("You can:")
        output.append("1. Use google_search with API key for initial results")
        output.append("2. Or provide a starting URL to search from")
        return "\n".join(output)
    
    # Perform search
    all_results = {}
    urls_to_search = [(url, 1)]  # (url, current_depth)
    searched_urls = set()
    
    while urls_to_search and len(searched_urls) < max_results:
        current_url, current_depth = urls_to_search.pop(0)
        
        if current_url in searched_urls:
            continue
        
        searched_urls.add(current_url)
        
        # Fetch webpage
        success, content = _fetch_url_content(current_url, timeout, user_agent)
        if not success:
            continue
        
        # Extract text
        text_content = _extract_text_from_html(content)
        
        # Search for keywords
        for keyword in keyword_list:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            if pattern.search(text_content):
                if current_url not in all_results:
                    all_results[current_url] = {
                        'depth': current_depth,
                        'matches': []
                    }
                all_results[current_url]['matches'].append(keyword)
        
        # Extract links for next level if not at max depth
        if current_depth < depth:
            links = _extract_links_from_html(content, current_url)
            for link in links[:5]:  # Limit to 5 links per page
                if link not in searched_urls and len(searched_urls) < max_results:
                    urls_to_search.append((link, current_depth + 1))
    
    # Format results
    if not all_results:
        output.append(f"\nNo matches found for keywords in {len(searched_urls)} pages searched.")
        return "\n".join(output)
    
    output.append(f"\nFound matches in {len(all_results)} of {len(searched_urls)} pages:")
    output.append("-" * 60)
    
    for url_info, data in all_results.items():
        output.append(f"\nURL: {url_info}")
        output.append(f"Depth: {data['depth']}")
        output.append(f"Matches: {', '.join(data['matches'])}")
    
    return "\n".join(output)

def find_contacts(url: str, timeout: int = 30, user_agent: str = None) -> str:
    """
    Find contact information on a webpage.
    
    Args:
        url: URL of the webpage
        timeout: Request timeout in seconds
        user_agent: Custom User-Agent header
        
    Returns:
        Contact information or error message
    """
    success, result = _fetch_url_content(url, timeout, user_agent)
    if not success:
        return result
    
    # Extract text
    text_content = _extract_text_from_html(result)
    
    # Find contact info
    contacts = _find_contact_info(text_content)
    
    # Format output
    output = []
    output.append(f"Contact information found on: {url}")
    output.append("="*60)
    
    if contacts['emails']:
        output.append("\nEMAIL ADDRESSES:")
        for email in contacts['emails']:
            output.append(f"  • {email}")
    
    if contacts['phone_numbers']:
        output.append("\nPHONE NUMBERS:")
        for phone in contacts['phone_numbers']:
            output.append(f"  • {phone}")
    
    if contacts['urls']:
        output.append("\nURLS FOUND:")
        for url_found in contacts['urls'][:10]:  # Limit URLs
            output.append(f"  • {url_found}")
    
    if not any(contacts.values()):
        output.append("\nNo contact information found on this page.")
        output.append("Try checking linked pages or using deeper search.")
    
    return "\n".join(output)

def extract_metadata(url: str, timeout: int = 30, user_agent: str = None) -> str:
    """
    Extract metadata from webpage.
    
    Args:
        url: URL of the webpage
        timeout: Request timeout in seconds
        user_agent: Custom User-Agent header
        
    Returns:
        Metadata or error message
    """
    success, result = _fetch_url_content(url, timeout, user_agent)
    if not success:
        return result
    
    # Extract metadata
    metadata = _extract_metadata_from_html(result)
    
    # Format output
    output = []
    output.append(f"Metadata from: {url}")
    output.append("="*60)
    
    if not metadata:
        output.append("No metadata found.")
        return "\n".join(output)
    
    # Display common metadata
    common_fields = ['title', 'description', 'keywords', 'author', 'viewport']
    for field in common_fields:
        if field in metadata:
            output.append(f"\n{field.upper()}:")
            output.append(f"  {metadata[field]}")
    
    # Display Open Graph and Twitter metadata
    og_metadata = {k: v for k, v in metadata.items() if 'og:' in k}
    twitter_metadata = {k: v for k, v in metadata.items() if 'twitter:' in k}
    
    if og_metadata:
        output.append("\nOPEN GRAPH METADATA:")
        for key, value in og_metadata.items():
            output.append(f"  {key}: {value}")
    
    if twitter_metadata:
        output.append("\nTWITTER METADATA:")
        for key, value in twitter_metadata.items():
            output.append(f"  {key}: {value}")
    
    return "\n".join(output)

# ============================================================================
# TOOL CALL MAP
# ============================================================================

TOOL_CALL_MAP = {
    "fetch_webpage": fetch_webpage,
    "search_webpage": search_webpage,
    "extract_links": extract_links,
    "google_search": google_search,
    "web_search": web_search,
    "extract_article_content": extract_article_content,
    "summarize_webpage": summarize_webpage,
    "deep_search": deep_search,
    "find_contacts": find_contacts,
    "extract_metadata": extract_metadata,
}