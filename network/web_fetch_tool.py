"""
Claude Code兼容的WebFetchTool简化实现。

基于Claude Code的WebFetchTool.ts（318行TypeScript代码）分析：
- 输入：url（要获取的URL），prompt（应用于内容的提示词）
- 输出：bytes（字节数）、code（HTTP状态码）、codeText（状态码文本）、
        result（处理结果）、durationMs（耗时）、url（原始URL）
- 功能：获取URL内容，将HTML转换为markdown，应用提示词处理内容

简化策略：
1. 使用requests库进行HTTP请求
2. 简单的HTML到文本转换（去除标签，基本格式化）
3. 简化的提示词处理：关键词搜索和提取
4. 保持与Claude Code接口的兼容性

注意：这是简化版本，不包含：
- 复杂的权限检查
- 重定向处理（除基础重定向外）
- 二进制内容保存
- AI模型驱动的提示词处理
- 预批准域名检查
- 缓存机制
"""

import os
import sys
import json
import time
import re
import html
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from base import function_ai, parameters_func, property_param

# ===== 输入参数定义 =====

__WEB_FETCH_URL_PROPERTY__ = property_param(
    name="url",
    description="The URL to fetch content from",
    t="string",
    required=True
)

__WEB_FETCH_PROMPT_PROPERTY__ = property_param(
    name="prompt",
    description="The prompt to run on the fetched content",
    t="string",
    required=True
)

__WEB_FETCH_TIMEOUT_PROPERTY__ = property_param(
    name="timeout",
    description="Request timeout in seconds",
    t="integer",
    required=False
)

__WEB_FETCH_HEADERS_PROPERTY__ = property_param(
    name="headers",
    description="HTTP headers as a JSON string",
    t="string",
    required=False
)

__WEB_FETCH_VERIFY_SSL_PROPERTY__ = property_param(
    name="verify_ssl",
    description="Verify SSL certificate",
    t="boolean",
    required=False
)

# ===== 工具函数定义 =====

__WEB_FETCH_FUNCTION__ = function_ai(
    name="fetch",
    description="Fetch content from a URL and apply a prompt to extract relevant information",
    parameters=parameters_func([
        __WEB_FETCH_URL_PROPERTY__,
        __WEB_FETCH_PROMPT_PROPERTY__,
        __WEB_FETCH_TIMEOUT_PROPERTY__,
        __WEB_FETCH_HEADERS_PROPERTY__,
        __WEB_FETCH_VERIFY_SSL_PROPERTY__,
    ]),
)

def _html_to_text(html_content: str, url: str = "") -> str:
    """
    将HTML内容转换为纯文本，保留基本结构。
    
    简化版本：使用BeautifulSoup提取文本并添加基本格式化。
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除脚本和样式标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 获取文本
        text = soup.get_text()
        
        # 基本的格式化：移除多余空白，保留段落
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # 添加URL作为标题
        if url:
            text = f"# Content from {url}\n\n{text}"
            
        return text
    except Exception as e:
        # 如果解析失败，返回原始HTML（已转义）或简单处理后的文本
        print(f"警告：HTML解析失败，使用简化文本提取: {e}", file=sys.stderr)
        # 简单去除HTML标签
        text = re.sub(r'<[^>]+>', ' ', html_content)
        text = html.unescape(text)
        # 规范化空白
        text = ' '.join(text.split())
        if url:
            text = f"# Content from {url}\n\n{text}"
        return text

def _apply_prompt_to_content(content: str, prompt: str) -> str:
    """
    将提示词应用于内容，提取相关信息。
    
    简化版本：基于关键词搜索和简单模式匹配。
    """
    # 如果提示词为空或只是通用指令，返回完整内容
    if not prompt or len(prompt.strip()) < 3:
        return content
    
    prompt_lower = prompt.lower()
    
    # 常见提示词模式匹配
    patterns = {
        'summary|summarize|summarise': '提取摘要',
        'key points|main points': '提取关键点',
        'table': '查找表格',
        'list': '查找列表',
        'contact': '查找联系方式',
        'email': '查找邮箱地址',
        'phone': '查找电话号码',
        'address': '查找地址',
        'date': '查找日期',
        'price|\\$|dollar': '查找价格',
        'title': '查找标题',
    }
    
    # 检查是否有特定模式
    for pattern, description in patterns.items():
        if re.search(pattern, prompt_lower):
            # 简单实现：返回包含关键词的行
            lines = content.split('\n')
            result_lines = []
            for line in lines:
                line_lower = line.lower()
                # 检查行是否包含模式中的任何关键词
                pattern_keywords = pattern.split('|')
                for keyword in pattern_keywords:
                    if keyword and keyword in line_lower:
                        result_lines.append(line)
                        break
            
            if result_lines:
                result = f"根据提示词'{prompt}'找到的相关内容：\n\n" + '\n'.join(result_lines)
                # 限制长度
                if len(result) > 5000:
                    result = result[:5000] + "\n\n...（内容截断）"
                return result
    
    # 通用提示词：搜索包含提示词关键词的行
    words = re.findall(r'\w+', prompt_lower)
    if len(words) > 0:
        lines = content.split('\n')
        result_lines = []
        for line in lines:
            line_lower = line.lower()
            if any(word in line_lower for word in words if len(word) >= 3):
                result_lines.append(line)
        
        if result_lines:
            result = f"根据提示词'{prompt}'找到的相关内容：\n\n" + '\n'.join(result_lines)
            if len(result) > 5000:
                result = result[:5000] + "\n\n...（内容截断）"
            return result
    
    # 如果没有找到匹配内容，返回内容的前部分作为摘要
    if len(content) > 2000:
        return f"根据提示词'{prompt}'处理内容。未找到精确匹配，返回内容摘要：\n\n{content[:2000]}...\n\n（内容截断，完整内容{len(content)}字符）"
    else:
        return f"根据提示词'{prompt}'处理内容：\n\n{content}"

def fetch(
    url: str,
    prompt: str,
    timeout: int = 30,
    headers: Optional[str] = None,
    verify_ssl: bool = True
) -> str:
    """
    从URL获取内容并应用提示词处理。
    
    参数：
        url: 要获取的URL
        prompt: 应用于内容的提示词
        timeout: 请求超时时间（秒）
        headers: HTTP头部（JSON字符串）
        verify_ssl: 是否验证SSL证书
    
    返回：
        JSON字符串，包含以下字段：
        - bytes: 内容字节数
        - code: HTTP状态码
        - codeText: HTTP状态码文本
        - result: 处理结果
        - durationMs: 耗时（毫秒）
        - url: 原始URL
    """
    start_time = time.time()
    
    # 验证URL
    try:
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError(f"无效的URL格式: {url}")
    except Exception as e:
        error_result = {
            "bytes": 0,
            "code": 400,
            "codeText": "Bad Request",
            "result": f"URL解析失败: {e}",
            "durationMs": int((time.time() - start_time) * 1000),
            "url": url
        }
        return json.dumps(error_result, ensure_ascii=False)
    
    # 准备请求头
    request_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    if headers:
        try:
            headers_dict = json.loads(headers)
            if isinstance(headers_dict, dict):
                request_headers.update(headers_dict)
        except json.JSONDecodeError:
            print(f"警告：无法解析headers参数，忽略: {headers}", file=sys.stderr)
    
    try:
        # 发送HTTP请求
        response = requests.get(
            url,
            headers=request_headers,
            timeout=timeout,
            verify=verify_ssl,
            allow_redirects=True  # 允许重定向
        )
        
        # 计算耗时
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 获取内容
        content_bytes = len(response.content)
        
        # 根据内容类型处理
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'text/html' in content_type or 'text/plain' in content_type:
            # 文本内容
            if 'text/html' in content_type:
                # HTML转文本
                text_content = _html_to_text(response.text, url)
            else:
                # 纯文本
                text_content = response.text
            
            # 应用提示词
            result = _apply_prompt_to_content(text_content, prompt)
        else:
            # 非文本内容（图片、PDF等）
            result = f"非文本内容类型: {content_type}\n大小: {content_bytes} 字节\nURL: {url}\n\n提示词处理不适用于二进制内容。"
        
        # 返回结果
        output = {
            "bytes": content_bytes,
            "code": response.status_code,
            "codeText": response.reason,
            "result": result,
            "durationMs": duration_ms,
            "url": url
        }
        
        return json.dumps(output, ensure_ascii=False)
        
    except requests.exceptions.Timeout:
        duration_ms = int((time.time() - start_time) * 1000)
        error_result = {
            "bytes": 0,
            "code": 408,
            "codeText": "Request Timeout",
            "result": f"请求超时: {timeout}秒内未收到响应",
            "durationMs": duration_ms,
            "url": url
        }
        return json.dumps(error_result, ensure_ascii=False)
    except requests.exceptions.SSLError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_result = {
            "bytes": 0,
            "code": 495,
            "codeText": "SSL Certificate Error",
            "result": f"SSL证书错误: {e}",
            "durationMs": duration_ms,
            "url": url
        }
        return json.dumps(error_result, ensure_ascii=False)
    except requests.exceptions.ConnectionError as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_result = {
            "bytes": 0,
            "code": 503,
            "codeText": "Connection Error",
            "result": f"连接错误: {e}",
            "durationMs": duration_ms,
            "url": url
        }
        return json.dumps(error_result, ensure_ascii=False)
    except requests.exceptions.RequestException as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_result = {
            "bytes": 0,
            "code": 500,
            "codeText": "Request Error",
            "result": f"请求错误: {e}",
            "durationMs": duration_ms,
            "url": url
        }
        return json.dumps(error_result, ensure_ascii=False)
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        error_result = {
            "bytes": 0,
            "code": 500,
            "codeText": "Internal Error",
            "result": f"内部错误: {e}",
            "durationMs": duration_ms,
            "url": url
        }
        return json.dumps(error_result, ensure_ascii=False)

# ===== 工具注册 =====

# 工具列表
tools = [__WEB_FETCH_FUNCTION__]

# 工具调用映射（注意：web_fetch函数返回JSON字符串，但__WEB_FETCH_FUNCTION__是包装器）
TOOL_CALL_MAP = {
    "fetch": fetch
}

__all__ = ['tools', 'TOOL_CALL_MAP', 'fetch', '__WEB_FETCH_FUNCTION__']