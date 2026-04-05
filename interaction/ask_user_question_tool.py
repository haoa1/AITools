"""
Claude Code兼容的AskUserQuestionTool简化实现。

基于Claude Code的AskUserQuestionTool.tsx（265行TypeScript代码）分析：
- 输入：questions数组（1-4个问题），每个问题包含question、header、options、multiSelect
- 输出：questions、answers、annotations
- 功能：向用户提出多选问题并获取回答

简化策略：
1. 在命令行环境下，通过终端提示模拟用户交互
2. 支持多选和单选模式
3. 提供模拟回答模式，用于非交互式环境
4. 保持与Claude Code接口的兼容性

注意：这是简化版本，不包含复杂的UI渲染、HTML预览验证和权限检查。
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from base import function_ai, parameters_func, property_param

# ===== 数据结构定义 =====

@dataclass
class QuestionOption:
    """问题选项"""
    label: str
    description: str
    preview: Optional[str] = None

@dataclass
class Question:
    """单个问题"""
    question: str
    header: str
    options: List[QuestionOption]
    multiSelect: bool = False

@dataclass
class Annotation:
    """用户注释"""
    preview: Optional[str] = None
    notes: Optional[str] = None

# ===== 输入参数定义 =====

# 由于AITools的参数系统不支持复杂嵌套结构，我们需要将questions作为JSON字符串传递
# 然后在函数内部解析

__QUESTIONS_PROPERTY__ = property_param(
    name="questions",
    description="Questions to ask the user (1-4 questions) as JSON string. Each question should have 'question', 'header', 'options' (2-4 options), and 'multiSelect' fields.",
    t="string",
    required=True,
)

__ANSWERS_PROPERTY__ = property_param(
    name="answers",
    description="User answers collected by the permission component (optional)",
    t="string",
    required=False,
)

__ANNOTATIONS_PROPERTY__ = property_param(
    name="annotations",
    description="Optional per-question annotations from the user (e.g., notes on preview selections) as JSON string (optional)",
    t="string",
    required=False,
)

__METADATA_PROPERTY__ = property_param(
    name="metadata",
    description="Optional metadata for tracking and analytics purposes as JSON string (optional)",
    t="string",
    required=False,
)

# ===== 工具函数定义 =====

__ASK_USER_QUESTION_FUNCTION__ = function_ai(
    name="ask_user_question",
    description="Ask the user multiple-choice questions and get their answers (simplified version of Claude Code's AskUserQuestionTool).",
    parameters=parameters_func([
        __QUESTIONS_PROPERTY__,
        __ANSWERS_PROPERTY__,
        __ANNOTATIONS_PROPERTY__,
        __METADATA_PROPERTY__,
    ]),
)

tools = [__ASK_USER_QUESTION_FUNCTION__]

# ===== 配置管理 =====

class AskUserQuestionConfig:
    """用户提问工具配置"""
    
    def __init__(self):
        # 是否启用交互模式（默认为True）
        self.interactive_mode = True
        
        # 非交互模式下的默认行为
        # "first_option": 总是选择第一个选项
        # "random": 随机选择选项
        # "simulate": 使用模拟回答（基于问题内容）
        self.non_interactive_mode = "simulate"
        
        # 是否允许用户跳过问题（按回车跳过）
        self.allow_skip = True
        
        # 跳过时的默认回答（如果allow_skip为True）
        self.skip_answer = "skipped"
    
    @classmethod
    def from_env(cls):
        """从环境变量加载配置"""
        config = cls()
        
        # 从环境变量读取配置
        interactive = os.environ.get("ASK_USER_QUESTION_INTERACTIVE", "true").lower()
        config.interactive_mode = interactive in ("true", "1", "yes")
        
        config.non_interactive_mode = os.environ.get(
            "ASK_USER_QUESTION_NON_INTERACTIVE_MODE", 
            "simulate"
        )
        
        allow_skip = os.environ.get("ASK_USER_QUESTION_ALLOW_SKIP", "true").lower()
        config.allow_skip = allow_skip in ("true", "1", "yes")
        
        config.skip_answer = os.environ.get(
            "ASK_USER_QUESTION_SKIP_ANSWER", 
            "skipped"
        )
        
        return config

def _get_config() -> AskUserQuestionConfig:
    """获取当前配置（每次调用都重新读取环境变量）"""
    return AskUserQuestionConfig.from_env()

# ===== 核心实现函数 =====

def _parse_questions_input(questions_input: str) -> List[Dict[str, Any]]:
    """解析questions输入（JSON字符串）"""
    try:
        questions = json.loads(questions_input)
        if not isinstance(questions, list):
            raise ValueError("questions must be a list")
        
        if len(questions) < 1 or len(questions) > 4:
            raise ValueError("questions must have 1-4 questions")
        
        # 验证每个问题的结构
        validated_questions = []
        for i, q in enumerate(questions):
            if not isinstance(q, dict):
                raise ValueError(f"Question at index {i} must be an object")
            
            # 必需字段检查
            required_fields = ["question", "header", "options"]
            for field in required_fields:
                if field not in q:
                    raise ValueError(f"Question at index {i} must have '{field}'")
            
            # 验证问题文本
            question_text = q["question"]
            if not question_text or not isinstance(question_text, str):
                raise ValueError(f"Question at index {i} must have non-empty 'question' string")
            
            # 验证header
            header = q["header"]
            if not header or not isinstance(header, str):
                raise ValueError(f"Question at index {i} must have non-empty 'header' string")
            
            # 验证选项
            options = q["options"]
            if not isinstance(options, list):
                raise ValueError(f"Question at index {i} must have 'options' as a list")
            
            if len(options) < 2 or len(options) > 4:
                raise ValueError(f"Question at index {i} must have 2-4 options")
            
            # 验证每个选项
            validated_options = []
            option_labels = set()
            for j, opt in enumerate(options):
                if not isinstance(opt, dict):
                    raise ValueError(f"Option at index {j} in question {i} must be an object")
                
                # 检查label
                if "label" not in opt or not opt["label"]:
                    raise ValueError(f"Option at index {j} in question {i} must have non-empty 'label'")
                
                label = str(opt["label"])
                if label in option_labels:
                    raise ValueError(f"Option labels must be unique within each question (duplicate: '{label}')")
                option_labels.add(label)
                
                # 检查description
                if "description" not in opt or not opt["description"]:
                    raise ValueError(f"Option at index {j} in question {i} must have non-empty 'description'")
                
                # 可选字段：preview
                preview = opt.get("preview")
                if preview is not None and not isinstance(preview, str):
                    raise ValueError(f"Option at index {j} in question {i} must have 'preview' as string or null")
                
                validated_options.append({
                    "label": label,
                    "description": str(opt["description"]),
                    "preview": preview
                })
            
            # 验证multiSelect
            multi_select = q.get("multiSelect", False)
            if not isinstance(multi_select, bool):
                raise ValueError(f"Question at index {i} must have 'multiSelect' as boolean")
            
            validated_questions.append({
                "question": question_text,
                "header": header,
                "options": validated_options,
                "multiSelect": multi_select
            })
        
        # 检查问题文本的唯一性
        question_texts = [q["question"] for q in validated_questions]
        if len(question_texts) != len(set(question_texts)):
            raise ValueError("Question texts must be unique")
        
        return validated_questions
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except Exception as e:
        raise ValueError(f"Error parsing questions: {e}")

def _parse_optional_json(input_str: Optional[str], field_name: str) -> Optional[Any]:
    """解析可选的JSON字段"""
    if input_str is None or input_str.strip() == "":
        return None
    
    try:
        return json.loads(input_str)
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format for {field_name}")

def _display_question(question: Dict[str, Any], question_num: int, total_questions: int) -> None:
    """在终端显示问题"""
    print(f"\n{'='*60}")
    print(f"Question {question_num}/{total_questions}: {question['header']}")
    print(f"{'='*60}")
    print(f"\n{question['question']}\n")
    
    options = question["options"]
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt['label']}")
        print(f"     {opt['description']}")
        if opt.get("preview"):
            print(f"     [Preview available: {opt['preview'][:50]}...]")
        print()
    
    if question["multiSelect"]:
        print("You can select multiple options (e.g., '1,3' or '1 3')")
    
    config = _get_config()
    if config.allow_skip:
        print("Press Enter to skip this question")

def _get_user_answer_interactive(question: Dict[str, Any]) -> str:
    """交互式获取用户回答"""
    options = question["options"]
    multi_select = question["multiSelect"]
    
    while True:
        try:
            user_input = input("Your choice: ").strip()
            
            # 处理跳过
            config = _get_config()
            if config.allow_skip and user_input == "":
                return config.skip_answer
            
            # 处理多选
            if multi_select:
                # 支持逗号分隔、空格分隔或混合
                selections = []
                for part in user_input.replace(",", " ").split():
                    if part.strip():
                        selections.append(int(part.strip()))
                
                # 验证选择
                valid_selections = []
                for sel in selections:
                    if 1 <= sel <= len(options):
                        valid_selections.append(sel)
                    else:
                        print(f"Warning: Option {sel} is out of range (1-{len(options)})")
                
                if not valid_selections:
                    print("Please select at least one valid option")
                    continue
                
                # 返回逗号分隔的选项标签
                answer_labels = [options[sel-1]["label"] for sel in valid_selections]
                return ", ".join(answer_labels)
            
            else:
                # 处理单选
                if not user_input:
                    print("Please enter a choice")
                    continue
                
                selection = int(user_input)
                if 1 <= selection <= len(options):
                    return options[selection-1]["label"]
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
        
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nQuestionnaire cancelled by user")
            return "cancelled"

def _get_simulated_answer(question: Dict[str, Any]) -> str:
    """生成模拟回答（用于非交互式环境）"""
    options = question["options"]
    multi_select = question["multiSelect"]
    
    config = _get_config()
    
    # 根据配置选择回答策略
    if config.non_interactive_mode == "first_option":
        # 总是选择第一个选项
        if multi_select:
            return options[0]["label"]
        else:
            return options[0]["label"]
    
    elif config.non_interactive_mode == "random":
        # 随机选择
        import random
        if multi_select:
            # 随机选择1-所有选项
            num_selections = random.randint(1, len(options))
            selected_indices = random.sample(range(len(options)), num_selections)
            answer_labels = [options[i]["label"] for i in selected_indices]
            return ", ".join(answer_labels)
        else:
            index = random.randint(0, len(options)-1)
            return options[index]["label"]
    
    else:  # "simulate" - 基于问题内容智能选择
        # 简化的智能选择逻辑
        question_text = question["question"].lower()
        options_labels = [opt["label"].lower() for opt in options]
        
        # 检查常见模式
        if any(word in question_text for word in ["yes", "no", "agree", "disagree"]):
            # 是/否类型问题，通常选择第一个积极选项
            positive_words = ["yes", "agree", "accept", "enable", "true", "on"]
            for i, label in enumerate(options_labels):
                if any(word in label for word in positive_words):
                    return options[i]["label"]
            return options[0]["label"]
        
        elif any(word in question_text for word in ["which", "select", "choose", "prefer"]):
            # 选择类型问题，根据选项长度选择较短的（通常更简洁）
            shortest_index = min(range(len(options_labels)), key=lambda i: len(options_labels[i]))
            if multi_select:
                # 对于多选，选择前两个选项
                selected = options[:min(2, len(options))]
                return ", ".join(opt["label"] for opt in selected)
            else:
                return options[shortest_index]["label"]
        
        else:
            # 默认选择第一个选项
            if multi_select:
                selected = options[:min(2, len(options))]
                return ", ".join(opt["label"] for opt in selected)
            else:
                return options[0]["label"]

def _collect_answers(questions: List[Dict[str, Any]]) -> Tuple[Dict[str, str], Dict[str, Dict[str, Any]]]:
    """收集所有问题的回答"""
    answers = {}
    annotations = {}
    
    total_questions = len(questions)
    
    config = _get_config()
    
    print(f"\n{'='*60}")
    print(f"ASK USER QUESTION TOOL")
    print(f"Total questions: {total_questions}")
    print(f"Interactive mode: {config.interactive_mode}")
    print(f"{'='*60}")
    
    for i, question in enumerate(questions, 1):
        question_text = question["question"]
        
        # 显示问题
        if config.interactive_mode:
            _display_question(question, i, total_questions)
        
        # 获取回答
        if config.interactive_mode:
            answer = _get_user_answer_interactive(question)
        else:
            answer = _get_simulated_answer(question)
            print(f"\nQuestion {i}/{total_questions}: {question['header']}")
            print(f"Simulated answer: {answer}")
        
        # 如果用户取消，提前退出
        if answer == "cancelled":
            print("Questionnaire cancelled. Returning collected answers so far.")
            break
        
        # 保存回答
        answers[question_text] = answer
        
        # 生成简单的注释（简化版本）
        if config.interactive_mode and answer != config.skip_answer:
            # 在实际实现中，这里可以收集用户对预览的反馈或笔记
            # 简化版本：只添加基本注释
            annotations[question_text] = {
                "notes": f"Answered via interactive prompt"
            }
        else:
            annotations[question_text] = {
                "notes": f"Answered via {config.non_interactive_mode} simulation"
            }
    
    print(f"\n{'='*60}")
    print("Questionnaire completed")
    print(f"{'='*60}")
    
    return answers, annotations

def ask_user_question(
    questions: str,
    answers: Optional[str] = None,
    annotations: Optional[str] = None,
    metadata: Optional[str] = None,
) -> str:
    """
    向用户提问并获取回答（Claude Code AskUserQuestionTool的简化版本）。
    
    参数:
        questions: JSON字符串格式的问题列表（1-4个问题）
        answers: 可选的已有回答（JSON字符串格式）
        annotations: 可选的注释信息（JSON字符串格式）
        metadata: 可选的元数据（JSON字符串格式）
    
    返回:
        JSON格式的结果，包含questions、answers和annotations
    """
    start_time = time.time()
    
    try:
        # 1. 解析输入
        parsed_questions = _parse_questions_input(questions)
        
        # 2. 解析可选字段
        parsed_answers = _parse_optional_json(answers, "answers")
        parsed_annotations = _parse_optional_json(annotations, "annotations")
        parsed_metadata = _parse_optional_json(metadata, "metadata")
        
        # 3. 如果已经提供了回答，直接返回
        if parsed_answers and isinstance(parsed_answers, dict) and len(parsed_answers) > 0:
            print("Using provided answers (skipping user interaction)")
            result = {
                "questions": parsed_questions,
                "answers": parsed_answers,
                "annotations": parsed_annotations or {},
            }
        else:
            # 4. 收集用户回答
            collected_answers, collected_annotations = _collect_answers(parsed_questions)
            
            # 合并已有的注释（如果有）
            if parsed_annotations and isinstance(parsed_annotations, dict):
                collected_annotations.update(parsed_annotations)
            
            result = {
                "questions": parsed_questions,
                "answers": collected_answers,
                "annotations": collected_annotations,
            }
        
        # 5. 添加元数据（如果提供）
        if parsed_metadata:
            result["metadata"] = parsed_metadata
        
        # 6. 添加执行时间（Claude Code兼容）
        result["durationMs"] = int((time.time() - start_time) * 1000)
        
        return json.dumps(result, ensure_ascii=False)
        
    except ValueError as e:
        # 输入验证错误
        error_result = {
            "error": str(e),
            "questions": [],
            "answers": {},
            "annotations": {},
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(error_result, ensure_ascii=False)
    
    except Exception as e:
        # 其他错误
        error_result = {
            "error": f"Unexpected error: {str(e)}",
            "questions": [],
            "answers": {},
            "annotations": {},
            "durationMs": int((time.time() - start_time) * 1000)
        }
        return json.dumps(error_result, ensure_ascii=False)

# ===== 工具注册 =====
__all__ = ["tools", "ask_user_question", "AskUserQuestionConfig"]