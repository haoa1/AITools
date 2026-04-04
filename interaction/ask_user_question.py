from base import function_ai, parameters_func, property_param
import json
import sys
from typing import List, Dict, Any

__QUESTIONS_PROPERTY__ = property_param(
    name="questions",
    description="Questions to ask the user (1-4 questions). Each question should have 'question' (the question text), 'header' (short label), 'options' (2-4 options with 'label' and 'description'), and 'multiSelect' (boolean for multiple selection).",
    t="string",
    required=True,
)

__ANSWERS_PROPERTY__ = property_param(
    name="answers",
    description="User answers collected by permission component (for internal use).",
    t="string",
)

__ANNOTATIONS_PROPERTY__ = property_param(
    name="annotations",
    description="Optional per-question annotations from the user (e.g., notes on preview selections).",
    t="string",
)

__METADATA_PROPERTY__ = property_param(
    name="metadata",
    description="Optional metadata for tracking and analytics purposes.",
    t="string",
)

__ASK_USER_QUESTION_FUNCTION__ = function_ai(
    name="ask_user_question",
    description="Ask the user multiple-choice questions. Similar to Claude Code's AskUserQuestionTool, this presents questions with options and collects user responses. Supports both single and multiple selection.",
    parameters=parameters_func(
        [__QUESTIONS_PROPERTY__, __ANSWERS_PROPERTY__, __ANNOTATIONS_PROPERTY__, __METADATA_PROPERTY__]
    ),
)

tools = [__ASK_USER_QUESTION_FUNCTION__]

def _display_question(question: Dict[str, Any], question_num: int, total_questions: int) -> str:
    """Display a single question and get user's answer."""
    print(f"\n{'='*60}")
    print(f"Question {question_num}/{total_questions}: {question.get('header', 'Question')}")
    print(f"{'='*60}")
    print(f"{question.get('question', '')}")
    print()
    
    options = question.get('options', [])
    multi_select = question.get('multiSelect', False)
    
    if len(options) < 2 or len(options) > 4:
        return f"Error: Question must have 2-4 options (got {len(options)})"
    
    # Display options
    for i, option in enumerate(options, 1):
        label = option.get('label', f'Option {i}')
        description = option.get('description', '')
        print(f"{i}. {label}")
        if description:
            print(f"   {description}")
        print()
    
    # Get user input
    if multi_select:
        print("Select one or more options (comma-separated, e.g., '1,3'): ", end='')
    else:
        print("Select an option (1-{}): ".format(len(options)), end='')
    
    sys.stdout.flush()
    
    try:
        user_input = sys.stdin.readline().strip()
        
        if multi_select:
            # Parse multiple selections
            selections = [s.strip() for s in user_input.split(',')]
            valid_selections = []
            
            for sel in selections:
                try:
                    idx = int(sel) - 1
                    if 0 <= idx < len(options):
                        valid_selections.append(options[idx]['label'])
                except ValueError:
                    continue
            
            if not valid_selections:
                return f"Error: No valid selections. Please select at least one option."
            
            return ','.join(valid_selections)
        else:
            # Parse single selection
            try:
                idx = int(user_input) - 1
                if 0 <= idx < len(options):
                    return options[idx]['label']
                else:
                    return f"Error: Selection out of range. Please choose 1-{len(options)}."
            except ValueError:
                return f"Error: Invalid input. Please enter a number 1-{len(options)}."
    
    except KeyboardInterrupt:
        return "Error: User interrupted the question."
    except Exception as e:
        return f"Error: {str(e)}"

def ask_user_question(
    questions: str,
    answers: str = "{}",
    annotations: str = "{}",
    metadata: str = "{}"
) -> str:
    """
    Ask the user multiple-choice questions and collect responses.
    
    Args:
        questions: JSON string containing array of question objects
        answers: JSON string of pre-collected answers (for compatibility)
        annotations: JSON string of annotations (for compatibility)
        metadata: JSON string of metadata (for compatibility)
    
    Returns:
        JSON string with questions, answers, and annotations
    """
    # Parse input
    try:
        questions_list = json.loads(questions)
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON format for questions: {str(e)}"
    
    if not isinstance(questions_list, list):
        return "Error: Questions must be a JSON array"
    
    if len(questions_list) < 1 or len(questions_list) > 4:
        return f"Error: Must have 1-4 questions (got {len(questions_list)})"
    
    # Validate questions
    for i, question in enumerate(questions_list, 1):
        if not isinstance(question, dict):
            return f"Error: Question {i} must be a JSON object"
        
        required_fields = ['question', 'header', 'options']
        for field in required_fields:
            if field not in question:
                return f"Error: Question {i} missing required field: '{field}'"
        
        options = question.get('options', [])
        if not isinstance(options, list) or len(options) < 2 or len(options) > 4:
            return f"Error: Question {i} must have 2-4 options (got {len(options)})"
        
        for j, option in enumerate(options, 1):
            if not isinstance(option, dict):
                return f"Error: Question {i}, Option {j} must be a JSON object"
            if 'label' not in option:
                return f"Error: Question {i}, Option {j} missing required field: 'label'"
    
    # Parse other parameters
    try:
        answers_dict = json.loads(answers) if answers else {}
    except json.JSONDecodeError:
        answers_dict = {}
    
    try:
        annotations_dict = json.loads(annotations) if annotations else {}
    except json.JSONDecodeError:
        annotations_dict = {}
    
    try:
        metadata_dict = json.loads(metadata) if metadata else {}
    except json.JSONDecodeError:
        metadata_dict = {}
    
    # Ask questions
    print("\n" + "="*60)
    print("USER QUESTIONNAIRE")
    print("="*60)
    
    collected_answers = {}
    
    for i, question in enumerate(questions_list, 1):
        question_text = question.get('question', '')
        
        # Skip if already answered
        if question_text in answers_dict:
            print(f"\nQuestion {i}: Using pre-provided answer")
            collected_answers[question_text] = answers_dict[question_text]
            continue
        
        # Ask the question
        answer = _display_question(question, i, len(questions_list))
        
        if answer.startswith("Error:"):
            return answer
        
        collected_answers[question_text] = answer
    
    # Build response
    response = {
        "questions": questions_list,
        "answers": collected_answers,
    }
    
    if annotations_dict:
        response["annotations"] = annotations_dict
    
    if metadata_dict:
        response["metadata"] = metadata_dict
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for question_text, answer in collected_answers.items():
        print(f"Q: {question_text}")
        print(f"A: {answer}")
        print()
    
    print("Questions answered successfully. You can now continue with the user's answers in mind.")
    
    return json.dumps(response, indent=2)

TOOL_CALL_MAP = {
    "ask_user_question": ask_user_question,
}