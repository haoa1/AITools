"""
Summary module for handling large model contexts and reducing redundancy.
Provides a single function to enhance conversation history using model-generated summaries.
"""

from base import function_ai, parameters_func, property_param
import json
import re
from typing import List, Dict, Any, Set, Tuple
import datetime

def ensure_message_dict(msg: Any) -> Dict:
    """
    Ensure message is a dictionary.
    Handles both dict and ChatCompletionMessage/Pydantic objects.
    """
    if isinstance(msg, dict):
        return msg
    # Check if it's a Pydantic model or has model_dump method
    elif hasattr(msg, 'model_dump'):
        return msg.model_dump()
    # Check if it's an object with attributes
    elif hasattr(msg, '__dict__'):
        return vars(msg)
    else:
        # Try to convert to dict
        try:
            return dict(msg)
        except:
            # Fallback: create minimal dict with available attributes
            result = {}
            if hasattr(msg, 'role'):
                result['role'] = msg.role
            if hasattr(msg, 'content'):
                result['content'] = msg.content
            if hasattr(msg, 'tool_calls'):
                result['tool_calls'] = msg.tool_calls
            if hasattr(msg, 'tool_call_id'):
                result['tool_call_id'] = msg.tool_call_id
            if hasattr(msg, 'reasoning_content'):
                result['reasoning_content'] = msg.reasoning_content
            return result

def ensure_messages_dict(messages: List[Any]) -> List[Dict]:
    """Convert list of messages to list of dictionaries."""
    return [ensure_message_dict(msg) for msg in messages]

# ============================================================================
# Summary工具参数定义
# ============================================================================

__SUMMARY_PROPERTY_MESSAGES__ = property_param(
    name="messages",
    description="The conversation messages to optimize. System will handle this automatically, you do not need to provide it.",
    t="array"
)

__SUMMARY_PROPERTY_MESSAGES_OPTIMIZED__ = property_param(
    name="messages_optimized",
    description="The optimized conversation messages after applying the summary.",
    t="array"
)

__SUMMARY_PROPERTY_CONTENT__ = property_param(
    name="content",
    description="The model-generated summary content to use for optimization.",
    t="string"
)

# ============================================================================
# Summary工具函数定义
# ============================================================================

__ENHANCE_SUMMARY_FUNCTION__ = function_ai(
    name="enhance_summary",
    description="Use model-generated summary to optimize conversation history, reducing token usage while preserving context.",
    parameters=parameters_func([__SUMMARY_PROPERTY_MESSAGES__, __SUMMARY_PROPERTY_CONTENT__])
)

__ENHANCE_UPDATE_FUNCTION__ = function_ai(
    name="update",
    description="Update the original messages list with the optimized messages.",
    parameters=parameters_func([__SUMMARY_PROPERTY_MESSAGES_OPTIMIZED__])
)


__ENHANCE_COMPACT__ = function_ai(
    name="compact",
    description="Use this:\n1. context is too mush, 2. user requirement.",
    parameters=parameters_func([])
)
tools = [__ENHANCE_COMPACT__]

# ============================================================================
# Summary核心实现 - 智能保留策略
# ============================================================================

def is_error_message(message: Dict) -> bool:
    """Check if message contains error information."""
    content = message.get('content', '')
    if not content or not isinstance(content, str):
        return False
    
    error_keywords = ['error', 'Error', 'ERROR', 'fail', 'Fail', 'FAIL', 'exception', 'Exception', 
                      'traceback', 'Traceback', 'failed', 'Failed', 'failure', 'Failure',
                      '错误', '失败', '异常']
    
    content_lower = content.lower()
    return any(keyword.lower() in content_lower for keyword in error_keywords)

def is_important_tool_result(message: Dict) -> bool:
    """Check if tool result contains important data."""
    if message.get('role') != 'tool':
        return False
    
    content = message.get('content', '')
    if not content or not isinstance(content, str):
        return False
    
    # Important tool results often contain data like file contents, code, etc.
    important_patterns = [
        r'file.*content', r'code.*:', r'data.*:', r'result.*:', r'output.*:',
        r'成功', r'完成', r'created', r'deleted', r'modified', r'updated',
        r'内容', r'结果', r'输出'
    ]
    
    content_lower = content.lower()
    return any(re.search(pattern, content_lower) for pattern in important_patterns)

def contains_key_info(message: Dict) -> bool:
    """Check if message contains key information like file paths, URLs, etc."""
    content = message.get('content', '')
    if not content or not isinstance(content, str):
        return False
    
    key_patterns = [
        r'/[\w/.-]+',  # File paths
        r'http[s]?://\S+',  # URLs
        r'\w+\.(py|js|java|cpp|txt|md|json|yaml|yml)',  # File extensions
        r'^\s*def\s+\w+',  # Function definitions
        r'^\s*class\s+\w+',  # Class definitions
        r'^\s*import\s+\w+',  # Import statements
    ]
    
    for pattern in key_patterns:
        if re.search(pattern, content, re.MULTILINE):
            return True
    
    return False

def calculate_message_importance(message: Dict, index: int, total_messages: int) -> int:
    """
    Calculate importance score for a message (higher = more important).
    
    Scoring criteria:
    - System messages: 100
    - First user message: 90
    - Error messages: 85
    - Messages with key info: 80
    - Recent messages (last 3): 70 - 50 based on recency
    - Important tool results: 65
    - Tool messages: 40
    - User/Assistant messages: 30
    - Old messages: 10 - 0 based on age
    """
    role = message.get('role', '')
    
    # System messages are most important
    if role == 'system':
        return 100
    
    # First user message (initial request)
    if index == 1 and role == 'user':  # index 0 is usually system
        return 90
    
    # Error messages
    if is_error_message(message):
        return 85
    
    # Messages containing key information
    if contains_key_info(message):
        return 80
    
    # Recent messages (last 3 non-system messages get bonus)
    recency_bonus = max(0, 50 - (total_messages - index) * 10)
    if recency_bonus > 0:
        base_score = 30 if role in ['user', 'assistant'] else 40
        return base_score + recency_bonus
    
    # Important tool results
    if is_important_tool_result(message):
        return 65
    
    # Tool messages
    if role == 'tool':
        return 40
    
    # User/Assistant messages
    if role in ['user', 'assistant']:
        return 30
    
    # Default
    return 10

def find_tool_call_pairs(messages: List[Dict]) -> Tuple[Set[int], Dict[str, int]]:
    """
    Find indices of tool calls and their corresponding tool responses.
    Returns tuple of (set of indices to keep, mapping from tool_call_id to assistant message index).
    """
    keep_indices = set()
    
    # Map tool_call_id to assistant message index
    tool_call_to_assistant = {}
    
    # First pass: find assistant messages with tool calls
    for i, msg in enumerate(messages):
        if msg.get('role') == 'assistant' and msg.get('tool_calls'):
            keep_indices.add(i)
            # Track tool call IDs
            tool_calls = msg.get('tool_calls', [])
            # Ensure tool_calls is a list
            if not isinstance(tool_calls, list):
                tool_calls = []
            for tool_call in tool_calls:
                if isinstance(tool_call, dict) and 'id' in tool_call:
                    tool_call_to_assistant[tool_call['id']] = i
                elif hasattr(tool_call, 'id'):
                    tool_call_to_assistant[tool_call.id] = i
    
    # Second pass: find corresponding tool responses
    for i, msg in enumerate(messages):
        if msg.get('role') == 'tool':
            tool_call_id = msg.get('tool_call_id')
            if tool_call_id in tool_call_to_assistant:
                keep_indices.add(i)
    
    return keep_indices, tool_call_to_assistant


from openai import OpenAI
import os
from summary.template import template 
def compact(messages: List[Any]) -> str:
    if len(messages) < 20:
        return ""

    # origin messages
    optimized_messages = []
    optimized_messages.append(messages[0])

    need_skip = True
    recent_compact_messages = []
    for i, msg in enumerate(messages[-15:-1]):
        if msg.get('role') == 'assistant':
            need_skip = False
        if not need_skip:
            recent_compact_messages.append(msg)

    systemPrompt = '''
你是上下文压缩大师
'''
    need_compact_messages = [
        {"role": "system",
        "content": systemPrompt},
        {"role": "user",
         "content": template(messages[-10:-1])}
    ]

    client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/")
    response = client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL", 'deepseek-chat'),
        messages=need_compact_messages,
        extra_body={ "thinking": { "type": "enabled" } }
    )

    optimized_messages.append({
        "role": "user",
        "content": response.choices[0].message.content
    })
    print(response.choices[0].message.content)
    print("\n\n\n")
    optimized_messages.extend(recent_compact_messages)
    
    messages.clear()
    messages.extend(optimized_messages)
    return "compacted"

def enhance_summary(messages: List[Any], content: str) -> str:
    '''
    Use model-generated summary to optimize conversation history.
    
    :param messages: Conversation messages list (can be dicts or objects)
    :type messages: list
    :param content: Model-generated summary content
    :type content: str
    :return: JSON string containing optimized messages and statistics
    :rtype: str
    '''
    try:
        # Convert all messages to dict format for processing
        messages_dict = ensure_messages_dict(messages)
        
        if not content or not content.strip():
            return json.dumps({
                'error': 'Content cannot be empty',
                'original_message_count': len(messages_dict),
                'optimized_message_count': len(messages_dict),
                'optimization_percentage': 0.0,
                'summary_used': False
            }, ensure_ascii=False)
        

        # print("messages_dict:\n\n", json.dumps(messages_dict, ensure_ascii=False, indent=2))
        original_count = len(messages_dict)
       
        optimized_messages = []
        
        tool_find = False
        save_count = 15

        if original_count > 20:
            for i, msg in enumerate(messages_dict):
                if tool_find:
                    optimized_messages.append(msg)
                    tool_find = False
                    continue
                if i == original_count -save_count:
                    summary_message = {
                        'role': 'user',
                        'content': f'## Context Summary (Generated at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})\n\n{content}\n\n---\nNote: Previous conversation has been summarized above. Key messages are preserved below.'
                    }
                    optimized_messages.append(summary_message)
                if i > original_count - save_count:
                    if msg.get('role') == 'user' and not msg.get("content").startswith("## Context Optimization Needed") and not msg.get("content").startswith("## Context Summary") and not msg.get("content".startswith("Warning:  context monitoring")):
                        optimized_messages.append(msg)
                    if msg.get('role') == 'assistant':
                        tool_calls = msg.get('tool_calls', [])
                        # Ensure tool_calls is a list
                        if not isinstance(tool_calls, list):
                            tool_calls = []
                        if len(tool_calls) > 0:
                            optimized_messages.append(msg)
                            tool_find = True


                if msg.get('role') == 'system':
                    optimized_messages.append(msg)

                if msg.get('role') == 'user' and not msg.get("content").startswith("## Context Optimization Needed") and not msg.get("content").startswith("## Context Summary"):
                    optimized_messages.append(msg)
                
                if msg.get('role') == 'assistant':
                    tool_calls = msg.get('tool_calls', [])
                    # Ensure tool_calls is a list
                    if not isinstance(tool_calls, list):
                        tool_calls = []
                    if tool_calls and len(tool_calls) > 0:
                        for tool_call in tool_calls:
                            function = tool_call.get('function', {})

                            filter = {"get_project_summary"}
                            if function.get('name') in filter:
                                if hasattr(msg, "reasoning_content"):
                                    msg["reasoning_content"] = None
                                optimized_messages.append(msg)
                                tool_find = True
                
        # print("optimized_messages before tool pairing:\n\n", json.dumps(optimized_messages, ensure_ascii=False, indent=2))
        # must pair
        tool_calls_copy = []
        optimized_messages_copy = optimized_messages.copy()
        for i, msg in enumerate(optimized_messages_copy):
            if len(tool_calls_copy) >0:
                if msg.get('role') != 'tool':
                    print("Removing unpaired assistant tool_calls:", tool_calls)
                    optimized_messages.remove(msg)
                    tool_calls_copy=[]
                    continue

                tool_call_id = msg.get('tool_call_id')
                tmp = tool_calls_copy.copy()
                for i, tool_call in enumerate(tmp):
                    if tool_call.get("id") == tool_call_id:
                        tool_calls_copy.remove(tool_call)
                        continue
            
            if msg.get('role') == 'assistant':
                tool_calls = msg.get('tool_calls', [])
                # Ensure tool_calls is a list before copying
                if not isinstance(tool_calls, list):
                    tool_calls = []
                tool_calls_copy = tool_calls.copy()

        for i, msg in enumerate(optimized_messages):
            if msg.get('role') == 'assistant':
                tool_calls = msg.get('tool_calls', [])
                for j, tool_call in enumerate(tool_calls):
                    function = tool_call.get('function', {})
                    name = function.get('name', '')
                    arguments = function.get('arguments', "{}")
                    if name in ["write_file"]:
                        if len(arguments) > 50:
                            optimized_messages[i]['tool_calls'][j]["function"]["arguments"] = arguments[:50] + "... optimized for summary"


        # Step 5: Calculate statistics
        optimized_count = len(optimized_messages)
        optimization_percentage = ((original_count - optimized_count) / original_count * 100) if original_count > 0 else 0
        
        # Calculate character reduction
        original_chars = sum(len(str(msg.get('content', ''))) for msg in messages_dict)
        optimized_chars = sum(len(str(msg.get('content', ''))) for msg in optimized_messages)
        char_reduction = ((original_chars - optimized_chars) / original_chars * 100) if original_chars > 0 else 0
        
        # Step 6: Update the original messages list in place
        # Clear and extend with optimized messages (all dicts)
        messages.clear()
        messages.extend(optimized_messages)
        
        print("messages after enhance_summary:\n\n", json.dumps(messages, ensure_ascii=False, indent=2))
        
        result = {
            'success': True,
            'original_message_count': original_count,
            'optimized_message_count': optimized_count,
            'optimization_percentage': round(optimization_percentage, 1),
            'char_reduction_percentage': round(char_reduction, 1),
            'summary_used': True,
            'summary_content': content[:200] + '...' if len(content) > 200 else content,
            'timestamp': datetime.datetime.now().isoformat(),
        }
        
        print(f"✅ Context optimized: {original_count} → {optimized_count} messages "
              f"({optimization_percentage:.1f}% reduction)")
        print(f"   Character reduction: {char_reduction:.1f}%")
        print(f"   Strategy: aggressive_retention_v2")
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_msg = f'Error enhancing summary: {str(e)}'
        print(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        
        return json.dumps({
            'error': error_msg,
            'original_message_count': len(messages) if isinstance(messages, list) else 0,
            'optimized_message_count': 0,
            'optimization_percentage': 0.0,
            'summary_used': False
        }, ensure_ascii=False)

def update(messages_old: List[Any], messages_optimized: List[Any]) -> str:
    messages_old.clear()
    messages_old.extend(messages_optimized)
    return json.dumps({"len_optimized": len(messages_optimized)})

# ============================================================================
# 工具调用映射
# ============================================================================

# TOOL_CALL_MAP = {
#     "enhance_summary": enhance_summary
# }
TOOL_CALL_MAP = {
    "compact": compact
}

# ============================================================================
# 测试代码
# ============================================================================


if __name__ == "__main__":
    pass
    # print("AITools Summary模块测试 (智能保留策略版)")
    # print("=" * 60)
    
    # # 测试数据 - 模拟一个复杂对话
    # test_messages = [
    #     {"role": "system", "content": "你是一个软件专家，拥有操作系统、文件、网络、Git等工具。请谨慎使用工具，必要时向用户确认。"},
    #     {"role": "user", "content": "请帮我创建一个Python项目，用于处理数据分析和可视化。"},
    #     {"role": "assistant", "content": "好的，我将帮您创建Python项目。请告诉我项目名称和需要的功能。"},
    #     {"role": "user", "content": "项目名为DataAnalyzer，需要pandas, matplotlib, seaborn库。"},
    #     {"role": "assistant", "content": "正在创建项目DataAnalyzer..."},
    #     {"role": "tool", "tool_call_id": "call_123", "content": "项目目录创建成功"},
    #     {"role": "assistant", "content": "正在安装依赖库..."},
    #     {"role": "tool", "tool_call_id": "call_456", "content": "Error: 网络连接失败，无法安装pandas"},
    #     {"role": "assistant", "content": "安装遇到错误，正在尝试其他方法..."},
    #     {"role": "tool", "tool_call_id": "call_789", "content": "已使用本地缓存安装pandas, matplotlib, seaborn"},
    #     {"role": "assistant", "content": "依赖安装成功。正在创建示例代码..."},
    #     {"role": "tool", "tool_call_id": "call_999", "content": "示例代码已创建: data_analyzer.py"},
    #     {"role": "assistant", "content": "项目创建完成！包含数据分析和可视化示例代码。"},
    #     {"role": "user", "content": "谢谢！现在请帮我运行测试，确保一切正常。"},
    #     {"role": "assistant", "content": "正在运行测试..."},
    #     {"role": "tool", "tool_call_id": "call_101", "content": "测试通过：所有功能正常"},
    # ]
    
    # # 测试总结增强
    # print("测试enhance_summary函数:")
    # test_summary = "用户请求创建Python数据分析项目DataAnalyzer。助手创建了项目目录，安装依赖时遇到网络错误但通过本地缓存解决，创建了示例代码，最后运行测试通过。"
    # print(f"原始消息数: {len(test_messages)}")
    # print(f"总结内容: {test_summary[:100]}...")
    # print()
    
    # # 创建副本用于测试
    # test_messages_copy = test_messages.copy()
    
    # result = enhance_summary(test_messages_copy, test_summary)
    # print("\n优化结果:")
    # print(result[:500] + "..." if len(result) > 500 else result)
    # print()
    
    # # 解析结果
    # try:
    #     result_dict = json.loads(result)
    #     print(f"原始消息数: {result_dict.get('original_message_count')}")
    #     print(f"优化后消息数: {result_dict.get('optimized_message_count')}")
    #     print(f"优化比例: {result_dict.get('optimization_percentage', 0):.1f}%")
    #     print(f"字符减少比例: {result_dict.get('char_reduction_percentage', 0):.1f}%")
    #     print(f"保留的消息类型: {result_dict.get('kept_message_types')}")
    #     print(f"必须保留的消息数: {result_dict.get('must_keep_count')}")
    #     print(f"按重要性选择的消息数: {result_dict.get('selected_by_importance')}")
    #     print(f"优化策略: {result_dict.get('optimization_strategy')}")
    #     print()
        
    #     # 显示优化后的消息
    #     print("优化后的消息列表:")
    #     for i, msg in enumerate(test_messages_copy):
    #         role = msg.get('role', 'unknown')
    #         content_preview = str(msg.get('content', ''))[:80].replace('\n', ' ')
    #         print(f"  {i}. [{role}] {content_preview}{'...' if len(str(msg.get('content', ''))) > 80 else ''}")
            
    # except Exception as e:
    #     print(f"解析结果时出错: {e}")
    #     import traceback
    #     traceback.print_exc()
    
    # print("\nSummary模块测试完成!")
