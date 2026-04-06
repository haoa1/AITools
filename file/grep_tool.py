"""
Claude Code兼容的GrepTool简化实现。

基于Claude Code的GrepTool.ts（577行TypeScript代码）分析：
- 输入：pattern (必需), path (可选), glob (可选), output_mode (可选)
- 输出：根据不同output_mode返回不同结构
- 使用ripgrep执行搜索，提供高效的文本搜索功能

简化策略：
1. 使用Python的re模块和os.walk实现基本搜索，而不是ripgrep
2. 只实现核心功能：pattern搜索、path目录、output_mode选择
3. 简化高级选项：支持基本的上下文行数和行号
4. 不实现复杂的权限检查、VCS目录排除等
5. 保持与Claude Code接口的兼容性

注意：这是简化版本，性能不如ripgrep，适用于中小规模文件搜索。
"""

import os
import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from base import function_ai, parameters_func, property_param

# ===== 输入参数定义 =====

# pattern: 必需，正则表达式模式
__PATTERN_PROPERTY__ = property_param(
    name="pattern",
    description="The regular expression pattern to search for in file contents",
    t="string",
    required=True,
)

# path: 可选，搜索路径
__PATH_PROPERTY__ = property_param(
    name="path",
    description="File or directory to search in. Defaults to current working directory.",
    t="string",
    required=False,
)

# glob: 可选，glob模式筛选
__GLOB_PROPERTY__ = property_param(
    name="glob",
    description="Glob pattern to filter files (e.g. '*.js', '*.{ts,tsx}')",
    t="string",
    required=False,
)

# output_mode: 可选，输出模式
__OUTPUT_MODE_PROPERTY__ = property_param(
    name="output_mode",
    description='Output mode: "content" shows matching lines, "files_with_matches" shows file paths, "count" shows match counts. Defaults to "files_with_matches".',
    t="string",
    required=False,
)

# -B: 上下文前几行
__B_CONTEXT_PROPERTY__ = property_param(
    name="-B",
    description="Number of lines to show before each match. Requires output_mode: 'content'.",
    t="number",
    required=False,
)

# -A: 上下文后几行
__A_CONTEXT_PROPERTY__ = property_param(
    name="-A",
    description="Number of lines to show after each match. Requires output_mode: 'content'.",
    t="number",
    required=False,
)

# context: 上下文行数
__CONTEXT_PROPERTY__ = property_param(
    name="context",
    description="Number of lines to show before and after each match. Requires output_mode: 'content'.",
    t="number",
    required=False,
)

# -n: 显示行号
__N_LINE_NUM_PROPERTY__ = property_param(
    name="-n",
    description="Show line numbers in output. Requires output_mode: 'content'. Defaults to true.",
    t="boolean",
    required=False,
)

# -i: 大小写不敏感
__I_CASE_INSENSITIVE_PROPERTY__ = property_param(
    name="-i",
    description="Case insensitive search",
    t="boolean",
    required=False,
)

# head_limit: 输出限制
__HEAD_LIMIT_PROPERTY__ = property_param(
    name="head_limit",
    description="Limit output to first N lines/entries. Works across all output modes. Defaults to 250.",
    t="number",
    required=False,
)

# offset: 偏移量
__OFFSET_PROPERTY__ = property_param(
    name="offset",
    description="Skip first N lines/entries before applying head_limit. Defaults to 0.",
    t="number",
    required=False,
)

# ===== 工具函数定义 =====

__GREP_FUNCTION__ = function_ai(
    name="grep",
    description="Search for patterns in files using regular expressions (simplified version of Claude Code's GrepTool).",
    parameters=parameters_func([
        __PATTERN_PROPERTY__,
        __PATH_PROPERTY__,
        __GLOB_PROPERTY__,
        __OUTPUT_MODE_PROPERTY__,
        __B_CONTEXT_PROPERTY__,
        __A_CONTEXT_PROPERTY__,
        __CONTEXT_PROPERTY__,
        __N_LINE_NUM_PROPERTY__,
        __I_CASE_INSENSITIVE_PROPERTY__,
        __HEAD_LIMIT_PROPERTY__,
        __OFFSET_PROPERTY__,
    ]),
)

tools = [__GREP_FUNCTION__]

# ===== 数据结构 =====

@dataclass
class GrepOptions:
    """Grep搜索选项"""
    pattern: str
    path: str = "."
    glob: Optional[str] = None
    output_mode: str = "files_with_matches"
    context_before: int = 0
    context_after: int = 0
    show_line_numbers: bool = True
    case_insensitive: bool = False
    head_limit: Optional[int] = 250
    offset: int = 0

@dataclass
class GrepMatch:
    """单个匹配结果"""
    filepath: str
    line_num: int
    line_content: str
    match_start: int
    match_end: int

@dataclass
class FileMatches:
    """文件的匹配结果"""
    filepath: str
    matches: List[GrepMatch]
    match_count: int

# ===== 核心实现函数 =====

def _apply_head_limit(items: List[Any], limit: Optional[int], offset: int = 0) -> Tuple[List[Any], Optional[int]]:
    """应用head_limit和offset分页"""
    # 明确0表示无限制
    if limit == 0:
        return items[offset:], None
    
    effective_limit = limit if limit is not None else 250
    sliced = items[offset:offset + effective_limit]
    
    # 仅在实际发生截断时报告appliedLimit
    was_truncated = len(items) - offset > effective_limit
    applied_limit = effective_limit if was_truncated else None
    
    return sliced, applied_limit

def _should_include_file(filepath: str, glob_pattern: Optional[str] = None) -> bool:
    """根据glob模式判断是否包含文件"""
    if not glob_pattern:
        return True
    
    # 简单的glob模式匹配（简化的实现）
    try:
        from fnmatch import fnmatch
        return fnmatch(filepath, glob_pattern)
    except ImportError:
        # 如果fnmatch不可用，使用简单匹配
        if "*" in glob_pattern:
            # 简单通配符匹配
            import re
            pattern = glob_pattern.replace("*", ".*").replace("?", ".")
            return bool(re.match(pattern, filepath))
        return glob_pattern in filepath

def _search_in_file(filepath: str, options: GrepOptions) -> FileMatches:
    """在单个文件中搜索"""
    matches = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except (IOError, UnicodeDecodeError):
        # 如果无法读取文件，返回空结果
        return FileMatches(filepath=filepath, matches=[], match_count=0)
    
    # 编译正则表达式
    re_flags = re.IGNORECASE if options.case_insensitive else 0
    try:
        pattern_re = re.compile(options.pattern, re_flags)
    except re.error:
        # 无效的正则表达式
        return FileMatches(filepath=filepath, matches=[], match_count=0)
    
    # 搜索每一行
    for line_num, line in enumerate(lines, 1):
        for match in pattern_re.finditer(line):
            matches.append(GrepMatch(
                filepath=filepath,
                line_num=line_num,
                line_content=line.rstrip('\n'),
                match_start=match.start(),
                match_end=match.end()
            ))
    
    return FileMatches(filepath=filepath, matches=matches, match_count=len(matches))

def _get_context_lines(lines: List[str], line_num: int, context_before: int, context_after: int) -> List[Tuple[int, str]]:
    """获取上下文行"""
    start_line = max(1, line_num - context_before)
    end_line = min(len(lines), line_num + context_after)
    
    context = []
    for ctx_line_num in range(start_line, end_line + 1):
        context.append((ctx_line_num, lines[ctx_line_num - 1].rstrip('\n')))
    
    return context

def _format_match_display(match: GrepMatch, context_before: int = 0, context_after: int = 0, show_line_numbers: bool = True) -> str:
    """格式化匹配行显示"""
    try:
        with open(match.filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
    except (IOError, UnicodeDecodeError):
        # 如果无法重新读取文件，只显示匹配行
        if show_line_numbers:
            return f"{match.filepath}:{match.line_num}:{match.line_content}"
        else:
            return f"{match.filepath}:{match.line_content}"
    
    # 获取上下文行
    context = _get_context_lines(lines, match.line_num, context_before, context_after)
    
    # 格式化输出
    result_lines = []
    for ctx_line_num, ctx_line_content in context:
        if ctx_line_num == match.line_num:
            # 匹配行：高亮显示匹配部分（在终端中会高亮）
            if show_line_numbers:
                line_prefix = f"{match.filepath}:{ctx_line_num}:"
            else:
                line_prefix = f"{match.filepath}:"
            
            # 在匹配部分添加标记（在文本输出中显示为**标记**）
            highlighted = (
                ctx_line_content[:match.match_start] +
                f"**{ctx_line_content[match.match_start:match.match_end]}**" +
                ctx_line_content[match.match_end:]
            )
            result_lines.append(f"{line_prefix}{highlighted}")
        else:
            # 上下文行
            if show_line_numbers:
                line_prefix = f"{match.filepath}:{ctx_line_num}:"
            else:
                line_prefix = f"{match.filepath}:"
            result_lines.append(f"{line_prefix}{ctx_line_content}")
    
    return '\n'.join(result_lines)

def grep(
    pattern: str,
    path: Optional[str] = None,
    glob: Optional[str] = None,
    output_mode: Optional[str] = None,
    B: Optional[int] = None,
    A: Optional[int] = None,
    context: Optional[int] = None,
    n: Optional[bool] = None,
    i: Optional[bool] = None,
    head_limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> str:
    """
    在文件中搜索正则表达式模式（Claude Code GrepTool的简化版本）。
    
    参数:
        pattern: 正则表达式模式（必需）
        path: 搜索路径（默认当前目录）
        glob: glob模式筛选文件
        output_mode: 输出模式（content, files_with_matches, count）
        B: 匹配前的上下文行数
        A: 匹配后的上下文行数
        context: 上下文行数（前后相同）
        n: 是否显示行号（默认True）
        i: 是否大小写不敏感（默认False）
        head_limit: 输出限制（默认250）
        offset: 偏移量（默认0）
    
    返回:
        JSON格式的结果，与Claude Code GrepTool兼容
    """
    start_time = time.time()
    
    # 参数处理
    search_path = path or "."
    output_mode = output_mode or "files_with_matches"
    show_line_numbers = n if n is not None else True
    case_insensitive = i or False
    head_limit_val = head_limit
    offset_val = offset or 0
    
    # 上下文处理
    context_before = 0
    context_after = 0
    if context is not None:
        context_before = context
        context_after = context
    if B is not None:
        context_before = B
    if A is not None:
        context_after = A
    
    # 验证路径
    if not os.path.exists(search_path):
        error_result = {
            "error": f"Path does not exist: {search_path}",
            "mode": output_mode,
            "numFiles": 0,
            "filenames": [],
            "content": "",
        }
        return json.dumps(error_result, ensure_ascii=False)
    
    # 收集要搜索的文件
    files_to_search = []
    if os.path.isfile(search_path):
        files_to_search = [search_path]
    else:
        # 目录：递归搜索所有文件
        for root, dirs, filenames in os.walk(search_path):
            # 排除一些常见目录（简化版本）
            if '.git' in dirs:
                dirs.remove('.git')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            
            for filename in filenames:
                filepath = os.path.join(root, filename)
                # 应用glob筛选
                if _should_include_file(filepath, glob):
                    files_to_search.append(filepath)
    
    # 在所有文件中搜索
    all_matches: List[FileMatches] = []
    for filepath in files_to_search:
        options = GrepOptions(
            pattern=pattern,
            path=search_path,
            glob=glob,
            output_mode=output_mode,
            context_before=context_before,
            context_after=context_after,
            show_line_numbers=show_line_numbers,
            case_insensitive=case_insensitive,
            head_limit=head_limit_val,
            offset=offset_val
        )
        file_matches = _search_in_file(filepath, options)
        if file_matches.match_count > 0:
            all_matches.append(file_matches)
    
    # 根据输出模式处理结果
    if output_mode == "content":
        # 收集所有匹配行
        all_content_lines = []
        for file_matches in all_matches:
            for match in file_matches.matches:
                formatted = _format_match_display(
                    match, 
                    context_before, 
                    context_after, 
                    show_line_numbers
                )
                all_content_lines.append(formatted)
        
        # 应用分页
        limited_content, applied_limit = _apply_head_limit(all_content_lines, head_limit_val, offset_val)
        
        # 构建结果
        result = {
            "mode": "content",
            "numFiles": len(all_matches),
            "filenames": [],
            "content": "\n".join(limited_content),
            "numLines": len(limited_content),
        }
        if applied_limit is not None:
            result["appliedLimit"] = applied_limit
        if offset_val > 0:
            result["appliedOffset"] = offset_val
        
    elif output_mode == "count":
        # 统计模式
        total_matches = sum(fm.match_count for fm in all_matches)
        count_lines = [f"{fm.filepath}:{fm.match_count}" for fm in all_matches]
        
        # 应用分页
        limited_counts, applied_limit = _apply_head_limit(count_lines, head_limit_val, offset_val)
        
        # 构建结果
        result = {
            "mode": "count",
            "numFiles": len(all_matches),
            "filenames": [],
            "content": "\n".join(limited_counts),
            "numMatches": total_matches,
        }
        if applied_limit is not None:
            result["appliedLimit"] = applied_limit
        if offset_val > 0:
            result["appliedOffset"] = offset_val
            
    else:  # files_with_matches (默认)
        # 文件列表模式
        filenames = [fm.filepath for fm in all_matches]
        
        # 应用分页
        limited_filenames, applied_limit = _apply_head_limit(filenames, head_limit_val, offset_val)
        
        # 构建结果
        result = {
            "mode": "files_with_matches",
            "numFiles": len(limited_filenames),
            "filenames": limited_filenames,
        }
        if applied_limit is not None:
            result["appliedLimit"] = applied_limit
        if offset_val > 0:
            result["appliedOffset"] = offset_val
    
    # 添加执行时间（Claude Code兼容）
    result["durationMs"] = int((time.time() - start_time) * 1000)
    
    return json.dumps(result, ensure_ascii=False)

# ===== 工具注册 =====
__all__ = ["tools", "grep"]