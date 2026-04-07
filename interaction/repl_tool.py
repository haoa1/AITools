"""
Claude Code兼容的REPLTool简化实现。

基于Claude Code的REPLTool分析：
- REPL模式：启用时隐藏基础工具（FileRead, FileWrite, FileEdit, Bash, Grep, Glob, NotebookEdit, Agent）
- 交互式执行：提供类似Python REPL的代码执行环境
- 条件性启用：仅对ant用户启用（在AITools中简化为配置选项）

简化策略：
1. 提供基本的代码执行环境，支持Python语法
2. 实现工具隐藏机制，模拟REPL模式
3. 支持执行上下文保持和变量存储
4. 安全沙箱：限制危险操作，保护系统安全

注意：这是简化版本，不包含Claude Code中的复杂UI渲染和完整工具隐藏逻辑。
"""

import os
import sys
import json
import time
import ast
import traceback
import re
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from io import StringIO
import builtins
import importlib

# ===== 数据结构定义 =====

@dataclass
class REPLExecutionResult:
    """REPL执行结果"""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0
    variables_added: List[str] = None
    variables_modified: List[str] = None
    
    def __post_init__(self):
        if self.variables_added is None:
            self.variables_added = []
        if self.variables_modified is None:
            self.variables_modified = []

@dataclass  
class REPLContext:
    """REPL执行上下文"""
    variables: Dict[str, Any]
    execution_count: int
    last_execution_time: float
    enabled: bool = False
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}

# ===== 安全沙箱配置 =====

# 禁止的危险操作
DISALLOWED_KEYWORDS = [
    '__import__', 'eval', 'exec', 'compile', 'open', 'file',
    'os.system', 'subprocess', 'shutil', 'sys.exit', 'quit',
    'globals', 'locals', 'dir', 'type', 'isinstance',
    'getattr', 'setattr', 'delattr', 'hasattr',
    'memoryview', 'buffer', 'compile', '__builtins__'
]

# 允许的安全模块
SAFE_MODULES = [
    'math', 'random', 'datetime', 'time', 'json', 're',
    'collections', 'itertools', 'functools', 'operator',
    'string', 'decimal', 'fractions', 'statistics'
]

# ===== REPL执行器核心类 =====

class REPLExecutor:
    """REPL代码执行器"""
    
    def __init__(self):
        self.context = REPLContext(
            variables={},
            execution_count=0,
            last_execution_time=0.0,
            enabled=False
        )
        self.safe_builtins = self._create_safe_builtins()
        self.output_capture = StringIO()
        
    def _create_safe_builtins(self) -> dict:
        """创建安全的builtins字典"""
        safe_builtins = {}
        for name in dir(builtins):
            if name.startswith('_') and name != '__name__':
                continue
            if name in DISALLOWED_KEYWORDS:
                continue
            try:
                safe_builtins[name] = getattr(builtins, name)
            except:
                pass
        return safe_builtins
    
    def _create_safe_globals(self) -> dict:
        """创建安全的全局命名空间"""
        safe_globals = {
            '__builtins__': self.safe_builtins,
            '__name__': '__repl__',
            '__context__': self.context,
            'print': self._safe_print
        }
        
        # 添加安全模块
        for module_name in SAFE_MODULES:
            try:
                module = importlib.import_module(module_name)
                safe_globals[module_name] = module
            except ImportError:
                pass
        
        # 添加上下文中的变量
        safe_globals.update(self.context.variables)
        
        return safe_globals
    
    def _safe_print(self, *args, **kwargs):
        """安全的print函数，重定向到输出捕获"""
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        file = kwargs.get('file', self.output_capture)
        
        output = sep.join(str(arg) for arg in args) + end
        file.write(output)
        
        # 同时也输出到控制台（用于调试）
        sys.__stdout__.write(output)
    
    def _analyze_code(self, code: str) -> Tuple[List[str], List[str]]:
        """分析代码，识别新增和修改的变量"""
        try:
            tree = ast.parse(code)
            
            added = []
            modified = []
            loaded = []
            
            class VariableVisitor(ast.NodeVisitor):
                def visit_Assign(self, node):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            modified.append(target.id)
                        elif isinstance(target, ast.Tuple):
                            for elt in target.elts:
                                if isinstance(elt, ast.Name):
                                    modified.append(elt.id)
                    self.generic_visit(node)
                
                def visit_AugAssign(self, node):
                    if isinstance(node.target, ast.Name):
                        modified.append(node.target.id)
                    self.generic_visit(node)
                
                def visit_Name(self, node):
                    if isinstance(node.ctx, ast.Store):
                        if node.id not in modified:
                            added.append(node.id)
                    elif isinstance(node.ctx, ast.Load):
                        loaded.append(node.id)
                    self.generic_visit(node)
                
                def visit_FunctionDef(self, node):
                    added.append(node.name)
                    self.generic_visit(node)
                
                def visit_ClassDef(self, node):
                    added.append(node.name)
                    self.generic_visit(node)
                
                def visit_Import(self, node):
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name.split('.')[0]
                        added.append(name)
                    self.generic_visit(node)
                
                def visit_ImportFrom(self, node):
                    for alias in node.names:
                        name = alias.asname if alias.asname else alias.name
                        added.append(name)
                    self.generic_visit(node)
            
            visitor = VariableVisitor()
            visitor.visit(tree)
            
            # 识别哪些是真正新增的（不在现有上下文中）
            truly_added = [var for var in added if var not in self.context.variables]
            
            # 识别哪些是修改的（在上下文中且被赋值）
            truly_modified = [var for var in modified if var in self.context.variables]
            
            return truly_added, truly_modified
            
        except SyntaxError:
            return [], []
    
    def _validate_code_safety(self, code: str) -> Tuple[bool, Optional[str]]:
        """验证代码安全性"""
        # 检查危险关键字
        for keyword in DISALLOWED_KEYWORDS:
            pattern = rf'\b{re.escape(keyword)}\b'
            if re.search(pattern, code):
                return False, f"禁止使用危险关键字: {keyword}"
        
        # 检查危险的导入
        dangerous_imports = ['os', 'sys', 'subprocess', 'shutil', 'ctypes', 'socket']
        for imp in dangerous_imports:
            patterns = [
                rf'import\s+{imp}',
                rf'from\s+{imp}\s+import',
                rf'__import__\s*\(\s*[\'\"]{imp}[\'\"]'
            ]
            for pattern in patterns:
                if re.search(pattern, code):
                    return False, f"禁止导入危险模块: {imp}"
        
        # 检查文件操作
        file_patterns = [
            r'open\s*\([^)]*[\'\"][rwax+bm]*[\'\"]',
            r'__import__\s*\(\s*[\'\"](os|sys)[\'\"][^)]*\)'
        ]
        for pattern in file_patterns:
            if re.search(pattern, code):
                return False, "禁止执行文件操作"
        
        return True, None
    
    def execute(self, code: str) -> REPLExecutionResult:
        """执行代码片段"""
        start_time = time.time()
        self.output_capture = StringIO()
        
        try:
            # 1. 安全性验证
            is_safe, error_msg = self._validate_code_safety(code)
            if not is_safe:
                return REPLExecutionResult(
                    success=False,
                    output="",
                    error=f"安全性检查失败: {error_msg}",
                    execution_time=time.time() - start_time
                )
            
            # 2. 分析代码变量
            added_vars, modified_vars = self._analyze_code(code)
            
            # 3. 创建安全的执行环境
            safe_globals = self._create_safe_globals()
            safe_locals = {}
            
            # 保存标准输出以便恢复
            old_stdout = sys.stdout
            sys.stdout = self.output_capture
            
            # 4. 执行代码
            try:
                exec(compile(code, '<repl>', 'exec'), safe_globals, safe_locals)
                error = None
            except Exception as e:
                error = f"{type(e).__name__}: {str(e)}"
                # 捕获异常信息
                exc_info = traceback.format_exception_only(type(e), e)
                error_details = ''.join(exc_info).strip()
                if error_details:
                    error = error_details
            
            # 恢复标准输出
            sys.stdout = old_stdout
            
            # 5. 更新上下文变量
            if error is None:
                # 合并局部变量到全局上下文
                for key, value in safe_locals.items():
                    if key not in safe_globals or safe_globals[key] != value:
                        self.context.variables[key] = value
                
                # 更新全局变量
                for key in added_vars + modified_vars:
                    if key in safe_globals and key not in ['__builtins__', '__name__', '__context__', 'print']:
                        self.context.variables[key] = safe_globals[key]
            
            # 6. 更新执行统计
            self.context.execution_count += 1
            self.context.last_execution_time = time.time() - start_time
            
            # 7. 准备结果
            output = self.output_capture.getvalue()
            
            return REPLExecutionResult(
                success=error is None,
                output=output,
                error=error,
                execution_time=self.context.last_execution_time,
                variables_added=added_vars,
                variables_modified=modified_vars
            )
            
        except Exception as e:
            # 恢复标准输出
            sys.stdout = old_stdout
            
            return REPLExecutionResult(
                success=False,
                output="",
                error=f"执行器内部错误: {type(e).__name__}: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def get_context(self) -> REPLContext:
        """获取当前执行上下文"""
        return self.context
    
    def clear_context(self):
        """清空执行上下文（保留安全内置函数）"""
        self.context.variables = {}
        self.context.execution_count = 0
        self.context.last_execution_time = 0.0
        self.output_capture = StringIO()
    
    def set_enabled(self, enabled: bool):
        """启用或禁用REPL模式"""
        self.context.enabled = enabled

# ===== 工具函数实现 =====

# 全局REPL执行器实例
_repl_executor = REPLExecutor()

def repl_tool(
    command: str,
    code: Optional[str] = None,
    enable: Optional[bool] = None,
    clear_context: Optional[bool] = None,
    get_context: Optional[bool] = None
) -> str:
    """
    REPL交互工具（Claude Code REPLTool的简化版本）
    
    参数:
        command: REPL命令，可选值: 
                'execute' - 执行代码
                'enable' - 启用/禁用REPL模式
                'clear' - 清空上下文
                'context' - 获取上下文信息
                'status' - 获取状态信息
        code: 要执行的Python代码（当command='execute'时必需）
        enable: 启用或禁用REPL模式（当command='enable'时必需）
        clear_context: 是否清空上下文（当command='clear'时有效）
        get_context: 是否获取详细上下文（当command='context'时有效）
    
    返回:
        JSON格式的执行结果
    """
    start_time = time.time()
    
    try:
        # 解析字符串参数为适当类型
        if enable is not None and isinstance(enable, str):
            enable = enable.lower() == 'true'
        if clear_context is not None and isinstance(clear_context, str):
            clear_context = clear_context.lower() == 'true'
        if get_context is not None and isinstance(get_context, str):
            get_context = get_context.lower() == 'true'
        
        # 根据命令执行相应操作
        if command == 'execute':
            if not code:
                return json.dumps({
                    "success": False,
                    "error": "执行命令需要提供代码",
                    "execution_time": time.time() - start_time
                }, ensure_ascii=False)
            
            result = _repl_executor.execute(code)
            
            return json.dumps({
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "execution_time": result.execution_time,
                "variables_added": result.variables_added,
                "variables_modified": result.variables_modified,
                "execution_count": _repl_executor.context.execution_count
            }, ensure_ascii=False)
        
        elif command == 'enable':
            if enable is None:
                return json.dumps({
                    "success": False,
                    "error": "启用命令需要指定enable参数",
                    "execution_time": time.time() - start_time
                }, ensure_ascii=False)
            
            _repl_executor.set_enabled(enable)
            
            # 获取REPL_ONLY工具列表
            repl_only_tools = [
                "read", "write", "edit", "bash", 
                "grep", "glob", "notebook_edit", "agent"
            ]
            
            return json.dumps({
                "success": True,
                "enabled": enable,
                "repl_only_tools": repl_only_tools if enable else [],
                "message": f"REPL模式已{'启用' if enable else '禁用'}，{'基础工具已隐藏' if enable else '所有工具可用'}",
                "execution_time": time.time() - start_time
            }, ensure_ascii=False)
        
        elif command == 'clear':
            force_clear = clear_context if clear_context is not None else False
            
            if force_clear:
                _repl_executor.clear_context()
                message = "REPL上下文已清空"
            else:
                # 只是返回上下文信息，不实际清空
                message = "使用 clear_context=true 来实际清空上下文"
            
            return json.dumps({
                "success": True,
                "cleared": force_clear,
                "message": message,
                "variables_count": len(_repl_executor.context.variables),
                "execution_time": time.time() - start_time
            }, ensure_ascii=False)
        
        elif command == 'context':
            detailed = get_context if get_context is not None else False
            
            context = _repl_executor.get_context()
            
            result = {
                "success": True,
                "enabled": context.enabled,
                "execution_count": context.execution_count,
                "last_execution_time": context.last_execution_time,
                "variables_count": len(context.variables),
                "execution_time": time.time() - start_time
            }
            
            if detailed:
                # 只包含可序列化的变量
                serializable_vars = {}
                for key, value in context.variables.items():
                    try:
                        json.dumps(value)
                        serializable_vars[key] = value
                    except:
                        serializable_vars[key] = f"<non-serializable: {type(value).__name__}>"
                
                result["variables"] = serializable_vars
            
            return json.dumps(result, ensure_ascii=False)
        
        elif command == 'status':
            context = _repl_executor.get_context()
            
            return json.dumps({
                "success": True,
                "status": "active" if context.enabled else "inactive",
                "enabled": context.enabled,
                "execution_count": context.execution_count,
                "variables_count": len(context.variables),
                "last_execution_time": context.last_execution_time,
                "repl_only_tools": [
                    "read", "write", "edit", "bash", 
                    "grep", "glob", "notebook_edit", "agent"
                ] if context.enabled else [],
                "execution_time": time.time() - start_time
            }, ensure_ascii=False)
        
        else:
            return json.dumps({
                "success": False,
                "error": f"未知命令: {command}",
                "available_commands": ["execute", "enable", "clear", "context", "status"],
                "execution_time": time.time() - start_time
            }, ensure_ascii=False)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"REPL工具错误: {type(e).__name__}: {str(e)}",
            "traceback": traceback.format_exc(),
            "execution_time": time.time() - start_time
        }, ensure_ascii=False)

# ===== 工具注册 =====

# 工具列表
tools = [repl_tool]

# 工具调用映射
TOOL_CALL_MAP = {
    "repl": repl_tool
}

# ===== 辅助函数 =====

def get_repl_only_tools() -> List[str]:
    """获取REPL模式下隐藏的工具列表"""
    return [
        "read",      # FileReadTool
        "write",     # FileWriteTool  
        "edit",      # FileEditTool
        "bash",      # BashTool
        "grep",      # GrepTool
        "glob",      # GlobTool
        "notebook_edit",  # NotebookEditTool
        "agent"      # AgentTool
    ]

def is_repl_mode_enabled() -> bool:
    """检查REPL模式是否启用"""
    return _repl_executor.context.enabled

def filter_tools_for_repl(all_tools: List[str]) -> List[str]:
    """根据REPL模式过滤工具列表"""
    if not is_repl_mode_enabled():
        return all_tools
    
    repl_only = get_repl_only_tools()
    return [tool for tool in all_tools if tool not in repl_only]

if __name__ == "__main__":
    # 测试代码
    test_code = """
x = 10
y = 20
result = x + y
print(f"{x} + {y} = {result}")
"""
    
    result = repl_tool("execute", code=test_code)
    print("执行结果:", result)
    
    result = repl_tool("enable", enable="true")
    print("启用结果:", result)
    
    result = repl_tool("status")
    print("状态:", result)