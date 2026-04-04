from base import function_ai, parameters_func, property_param
import requests
import json
import time
from urllib.parse import urlparse
from typing import Optional, Dict, Any

__URL_PROPERTY__ = property_param(
    name="url",
    description="The URL to fetch content from. Must be a valid URL.",
    t="string",
    required=True,
)

__PROMPT_PROPERTY__ = property_param(
    name="prompt",
    description="Optional prompt describing what to extract or how to process the fetched content. If not provided, returns raw content or summary.",
    t="string",
)

__TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description="Request timeout in seconds. Default is 30 seconds.",
    t="number",
)

__WEB_FETCH_FUNCTION__ = function_ai(
    name="web_fetch",
    description="Fetch and process content from a URL. Similar to Claude Code's WebFetchTool, this tool retrieves web content and can apply basic processing. Supports redirect handling and content extraction.",
    parameters=parameters_func(
        [__URL_PROPERTY__, __PROMPT_PROPERTY__, __TIMEOUT_PROPERTY__]
    ),
)

tools = [__WEB_FETCH_FUNCTION__]

def _extract_text_from_html(html_content: str) -> str:
    """Extract readable text from HTML content (simplified version)."""
    # Simple text extraction - in a real implementation, you'd use BeautifulSoup
    # For now, just remove some HTML tags and return a simplified version
    import re
    
    # Remove script and style tags
    content = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<style.*?>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags but keep text
    content = re.sub(r'<[^>]+>', ' ', content)
    
    # Normalize whitespace
    content = re.sub(r'\s+', ' ', content)
    
    return content.strip()

def _apply_prompt_to_content(prompt: str, content: str) -> str:
    """
    Apply a prompt to content (simplified version).
    In Claude Code, this uses AI models. Here we provide basic text processing.
    """
    content_lower = content.lower()
    prompt_lower = prompt.lower()
    
    # Basic keyword-based processing
    if any(keyword in prompt_lower for keyword in ['summar', 'brief', 'overview']):
        # Create a simple summary (first 500 chars + ...)
        if len(content) > 500:
            return f"Summary (first 500 characters):\n{content[:500]}..."
        return content
    
    elif any(keyword in prompt_lower for keyword in ['extract', 'find', 'search']):
        # Try to find relevant sections
        lines = content.split('\n')
        relevant_lines = []
        for line in lines:
            if any(word in line.lower() for word in prompt_lower.split()[:5]):
                relevant_lines.append(line)
        
        if relevant_lines:
            return "Extracted relevant content:\n" + "\n".join(relevant_lines[:20])
    
    elif any(keyword in prompt_lower for keyword in ['list', 'bullets', 'points']):
        # Extract list-like content
        lines = content.split('\n')
        bullet_points = [line for line in lines if line.strip().startswith(('-', '*', '•', '✓', '→'))]
        if bullet_points:
            return "Bullet points found:\n" + "\n".join(bullet_points[:20])
    
    # Default: return content with length note
    if len(content) > 1000:
        return f"Content (truncated to 1000 characters):\n{content[:1000]}..."
    return content

def web_fetch(url: str, prompt: Optional[str] = None, timeout: int = 30) -> str:
    """
    Fetch and process content from a URL.
    
    Args:
        url: The URL to fetch content from
        prompt: Optional prompt describing how to process the content
        timeout: Request timeout in seconds
    
    Returns:
        Formatted string with fetch results
    """
    start_time = time.time()
    
    # Validate URL
    try:
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return "Error: Invalid URL. Must include scheme (http:// or https://) and hostname."
    except Exception as e:
        return f"Error: Invalid URL - {str(e)}"
    
    # Set default headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Make the request
        response = requests.get(
            url, 
            headers=headers, 
            timeout=timeout,
            allow_redirects=True
        )
        
        # Check for redirects
        if response.history:
            redirect_info = []
            for resp in response.history:
                redirect_info.append(f"  → {resp.status_code} {resp.reason}: {resp.url}")
            
            if redirect_info:
                redirect_msg = "Redirect chain:\n" + "\n".join(redirect_info)
                redirect_msg += f"\n\nFinal URL: {response.url}"
                # Continue with final response but note redirect
                redirect_note = f"\n\nNote: Request was redirected. {redirect_msg}"
            else:
                redirect_note = ""
        else:
            redirect_note = ""
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Get content
        content_type = response.headers.get('content-type', '').lower()
        content_length = len(response.content)
        
        # Process content based on type
        if 'text/html' in content_type:
            # HTML content
            raw_content = response.text
            extracted_content = _extract_text_from_html(raw_content)
            content_to_process = extracted_content
            content_note = f"HTML content extracted to text ({len(extracted_content)} characters)"
        
        elif 'application/json' in content_type:
            # JSON content
            try:
                json_data = response.json()
                content_to_process = json.dumps(json_data, indent=2)
                content_note = f"JSON content ({len(content_to_process)} characters)"
            except:
                content_to_process = response.text
                content_note = f"JSON-like text content ({len(content_to_process)} characters)"
        
        elif 'text/plain' in content_type or 'text/' in content_type:
            # Plain text or other text content
            content_to_process = response.text
            content_note = f"Text content ({len(content_to_process)} characters)"
        
        else:
            # Binary or unknown content
            content_to_process = f"[Binary content: {content_type}, {content_length} bytes]"
            content_note = f"Binary content: {content_type}"
        
        # Apply prompt if provided
        if prompt:
            processed_content = _apply_prompt_to_content(prompt, content_to_process)
            processing_note = f"Processed with prompt: '{prompt}'"
        else:
            processed_content = content_to_process
            processing_note = "Raw content (no prompt applied)"
        
        # Build response
        result_lines = []
        result_lines.append(f"✅ Successfully fetched: {url}")
        result_lines.append(f"Status: {response.status_code} {response.reason}")
        result_lines.append(f"Content Type: {content_type}")
        result_lines.append(f"Content Size: {content_length} bytes")
        result_lines.append(f"Duration: {duration_ms}ms")
        result_lines.append(f"Processing: {processing_note}")
        
        if redirect_note:
            result_lines.append(redirect_note)
        
        result_lines.append("")
        result_lines.append("=" * 60)
        result_lines.append("CONTENT")
        result_lines.append("=" * 60)
        result_lines.append("")
        result_lines.append(processed_content)
        
        if len(processed_content) > 10000:
            result_lines.append("")
            result_lines.append(f"[Content truncated. Original: {len(content_to_process)} characters]")
        
        return "\n".join(result_lines)
    
    except requests.exceptions.Timeout:
        return f"Error: Request timed out after {timeout} seconds."
    
    except requests.exceptions.TooManyRedirects:
        return "Error: Too many redirects."
    
    except requests.exceptions.RequestException as e:
        return f"Error: Request failed - {str(e)}"
    
    except Exception as e:
        return f"Error: Unexpected error - {str(e)}"

TOOL_CALL_MAP = {
    "web_fetch": web_fetch,
}