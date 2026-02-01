"""
Enhanced interaction module refactored into two main functions:
1. discuss_with_user - for all user interactions (questions, feedback, confirmations, etc.)
2. notify_user - for notifications and alerts
"""

from base import function_ai, parameters_func, property_param
import os
import sys
import json
import time
import readline
from typing import List, Dict, Optional, Any, Union
import tempfile
import subprocess
from datetime import datetime

# Import base interaction functions for extension
from .interaction import (
    display_message as base_display_message,
    get_user_input as base_get_user_input,
    select_from_choices as base_select_from_choices,
    confirm_action as base_confirm_action,
    _format_message
)

# ============================================================================
# Enhanced Property Definitions (保持向后兼容性)
# ============================================================================

__ENHANCED_PROPERTY_1__ = property_param(
    name="question",
    description="The question to ask the user.",
    t="string",
    required=True
)

__ENHANCED_PROPERTY_2__ = property_param(
    name="options",
    description="Options for the user to choose from as JSON string list.",
    t="string",
    required=True
)

__ENHANCED_PROPERTY_3__ = property_param(
    name="allow_multiple",
    description="Allow user to select multiple options.",
    t="boolean"
)

__ENHANCED_PROPERTY_4__ = property_param(
    name="require_confirmation",
    description="Require explicit confirmation before proceeding.",
    t="boolean"
)

__ENHANCED_PROPERTY_5__ = property_param(
    name="confirmation_text",
    description="Text to display for confirmation prompt.",
    t="string"
)

__ENHANCED_PROPERTY_6__ = property_param(
    name="timeout_action",
    description="Action to take on timeout (abort, default, ask_again).",
    t="string"
)

__ENHANCED_PROPERTY_7__ = property_param(
    name="user_feedback_prompt",
    description="Prompt asking for user feedback or opinion.",
    t="string",
    required=True
)

__ENHANCED_PROPERTY_8__ = property_param(
    name="feedback_type",
    description="Type of feedback (rating, text, choice, mixed).",
    t="string"
)

__ENHANCED_PROPERTY_9__ = property_param(
    name="rating_scale",
    description="Rating scale (e.g., '1-5', '1-10', 'poor-excellent').",
    t="string"
)

__ENHANCED_PROPERTY_10__ = property_param(
    name="blocking",
    description="Whether this interaction blocks until user responds.",
    t="boolean"
)

__ENHANCED_PROPERTY_11__ = property_param(
    name="continue_condition",
    description="Condition to continue (user_input, timeout, specific_answer).",
    t="string"
)

__ENHANCED_PROPERTY_12__ = property_param(
    name="expected_answer",
    description="Expected answer format or value for validation.",
    t="string"
)

__ENHANCED_PROPERTY_13__ = property_param(
    name="validation_regex",
    description="Regex pattern to validate user input.",
    t="string"
)

__ENHANCED_PROPERTY_14__ = property_param(
    name="retry_count",
    description="Number of retries allowed for invalid input.",
    t="integer"
)

__ENHANCED_PROPERTY_15__ = property_param(
    name="interactive_mode",
    description="Enable interactive mode with step-by-step guidance.",
    t="boolean"
)

__ENHANCED_PROPERTY_16__ = property_param(
    name="save_to_file",
    description="Save interaction results to specified file.",
    t="string"
)

# 新增属性：讨论类型
__ENHANCED_PROPERTY_17__ = property_param(
    name="interaction_type",
    description="Type of interaction: 'ask', 'feedback', 'confirm', 'validate', 'wizard'",
    t="string",
    required=True
)

# 新增属性：通知消息
__ENHANCED_PROPERTY_18__ = property_param(
    name="message",
    description="The message to display to the user.",
    t="string",
    required=True
)

# 新增属性：消息级别
__ENHANCED_PROPERTY_19__ = property_param(
    name="level",
    description="Message level: 'info', 'warning', 'error', 'success'",
    t="string"
)

# ============================================================================
# Enhanced Tool Definitions (保持向后兼容性)
# ============================================================================

__ENHANCED_ASK_WITH_OPTIONS_FUNCTION__ = function_ai(
    name="ask_user_with_options",
    description="Ask user a question with multiple choice options and get their selection.",
    parameters=parameters_func([__ENHANCED_PROPERTY_1__, __ENHANCED_PROPERTY_2__, 
                               __ENHANCED_PROPERTY_3__, __ENHANCED_PROPERTY_4__,
                               __ENHANCED_PROPERTY_5__, __ENHANCED_PROPERTY_6__])
)

__ENHANCED_GET_FEEDBACK_FUNCTION__ = function_ai(
    name="get_user_feedback",
    description="Get detailed feedback from user with customizable feedback type.",
    parameters=parameters_func([__ENHANCED_PROPERTY_7__, __ENHANCED_PROPERTY_8__,
                               __ENHANCED_PROPERTY_9__, __ENHANCED_PROPERTY_10__,
                               __ENHANCED_PROPERTY_16__])
)

__ENHANCED_BLOCKING_CONFIRM_FUNCTION__ = function_ai(
    name="blocking_confirmation",
    description="Get explicit confirmation from user before proceeding (blocks execution).",
    parameters=parameters_func([__ENHANCED_PROPERTY_1__, __ENHANCED_PROPERTY_4__,
                               __ENHANCED_PROPERTY_10__, __ENHANCED_PROPERTY_11__])
)

__ENHANCED_VALIDATED_INPUT_FUNCTION__ = function_ai(
    name="get_validated_input",
    description="Get user input with validation and retry logic.",
    parameters=parameters_func([__ENHANCED_PROPERTY_1__, __ENHANCED_PROPERTY_12__,
                               __ENHANCED_PROPERTY_13__, __ENHANCED_PROPERTY_14__])
)

__ENHANCED_INTERACTIVE_WIZARD_FUNCTION__ = function_ai(
    name="interactive_wizard",
    description="Run an interactive wizard for multi-step user input.",
    parameters=parameters_func([__ENHANCED_PROPERTY_15__, __ENHANCED_PROPERTY_16__])
)

__ENHANCED_PAUSE_UNTIL_INPUT_FUNCTION__ = function_ai(
    name="pause_until_user_input",
    description="Pause execution until user provides input or confirmation.",
    parameters=parameters_func([__ENHANCED_PROPERTY_1__, __ENHANCED_PROPERTY_10__,
                               __ENHANCED_PROPERTY_11__])
)

# 新增工具定义：讨论函数
__ENHANCED_DISCUSS_FUNCTION__ = function_ai(
    name="discuss_with_user",
    description="Unified function for all user interactions (questions, feedback, confirmations, etc.).",
    parameters=parameters_func([__ENHANCED_PROPERTY_17__, __ENHANCED_PROPERTY_1__,
                               __ENHANCED_PROPERTY_2__, __ENHANCED_PROPERTY_3__,
                               __ENHANCED_PROPERTY_4__, __ENHANCED_PROPERTY_5__,
                               __ENHANCED_PROPERTY_6__, __ENHANCED_PROPERTY_7__,
                               __ENHANCED_PROPERTY_8__, __ENHANCED_PROPERTY_9__,
                               __ENHANCED_PROPERTY_10__, __ENHANCED_PROPERTY_11__,
                               __ENHANCED_PROPERTY_12__, __ENHANCED_PROPERTY_13__,
                               __ENHANCED_PROPERTY_14__, __ENHANCED_PROPERTY_15__,
                               __ENHANCED_PROPERTY_16__])
)

# 新增工具定义：通知函数
__ENHANCED_NOTIFY_FUNCTION__ = function_ai(
    name="notify_user",
    description="Notify user with messages and optional confirmation.",
    parameters=parameters_func([__ENHANCED_PROPERTY_18__, __ENHANCED_PROPERTY_19__,
                               __ENHANCED_PROPERTY_10__, __ENHANCED_PROPERTY_11__])
)

tools = [
    __ENHANCED_ASK_WITH_OPTIONS_FUNCTION__,
    __ENHANCED_GET_FEEDBACK_FUNCTION__,
    __ENHANCED_BLOCKING_CONFIRM_FUNCTION__,
    __ENHANCED_VALIDATED_INPUT_FUNCTION__,
    __ENHANCED_INTERACTIVE_WIZARD_FUNCTION__,
    __ENHANCED_PAUSE_UNTIL_INPUT_FUNCTION__,
    __ENHANCED_DISCUSS_FUNCTION__,
    __ENHANCED_NOTIFY_FUNCTION__,
]

# ============================================================================
# 核心实现：两个主要函数
# ============================================================================

def _parse_options(options_str: str) -> List[str]:
    """Parse options from JSON string or comma-separated string."""
    if not options_str:
        return []
    
    try:
        options = json.loads(options_str)
        if isinstance(options, list):
            return [str(opt) for opt in options]
        else:
            return [str(options)]
    except json.JSONDecodeError:
        # Try comma-separated
        return [opt.strip() for opt in options_str.split(',') if opt.strip()]

def discuss_with_user(
    interaction_type: str,
    question: str = None,
    options: str = None,
    allow_multiple: bool = False,
    require_confirmation: bool = True,
    confirmation_text: str = "Please confirm your selection",
    timeout_action: str = "abort",
    user_feedback_prompt: str = None,
    feedback_type: str = "mixed",
    rating_scale: str = "1-5",
    blocking: bool = True,
    continue_condition: str = "user_input",
    expected_answer: str = None,
    validation_regex: str = None,
    retry_count: int = 3,
    interactive_mode: bool = True,
    save_to_file: str = None
) -> str:
    """
    Unified function for all user interactions.
    
    :param interaction_type: Type of interaction: 'ask', 'feedback', 'confirm', 'validate', 'wizard'
    :param question: The question to ask (for ask, confirm, validate types)
    :param options: Options for selection (for ask type)
    :param allow_multiple: Allow multiple selections (for ask type)
    :param require_confirmation: Require confirmation (for ask, confirm types)
    :param confirmation_text: Text for confirmation prompt
    :param timeout_action: Action on timeout
    :param user_feedback_prompt: Prompt for feedback (for feedback type)
    :param feedback_type: Type of feedback (rating, text, choice, mixed)
    :param rating_scale: Rating scale
    :param blocking: Whether to block execution
    :param continue_condition: Condition to continue
    :param expected_answer: Expected answer (for validate type)
    :param validation_regex: Validation regex (for validate type)
    :param retry_count: Retry count (for validate type)
    :param interactive_mode: Interactive mode (for wizard type)
    :param save_to_file: Save results to file
    :return: Interaction result
    """
    try:
        interaction_type = interaction_type.lower()
        
        if interaction_type == "ask":
            return _handle_ask_interaction(
                question, options, allow_multiple, require_confirmation,
                confirmation_text, timeout_action
            )
        elif interaction_type == "feedback":
            return _handle_feedback_interaction(
                user_feedback_prompt, feedback_type, rating_scale,
                blocking, save_to_file
            )
        elif interaction_type == "confirm":
            return _handle_confirmation_interaction(
                question, require_confirmation, blocking, continue_condition
            )
        elif interaction_type == "validate":
            return _handle_validation_interaction(
                question, expected_answer, validation_regex, retry_count
            )
        elif interaction_type == "wizard":
            return _handle_wizard_interaction(interactive_mode, save_to_file)
        else:
            return f"Error: Unknown interaction type '{interaction_type}'. Must be: ask, feedback, confirm, validate, wizard"
            
    except KeyboardInterrupt:
        return "Interaction interrupted by user"
    except Exception as e:
        return f"Error in discuss_with_user: {str(e)}"

def notify_user(
    message: str,
    level: str = "info",
    blocking: bool = False,
    continue_condition: str = "user_input"
) -> str:
    """
    Notify user with messages and optional confirmation.
    
    :param message: The message to display
    :param level: Message level: 'info', 'warning', 'error', 'success'
    :param blocking: Whether to block until user acknowledges
    :param continue_condition: Condition to continue
    :return: Notification result
    """
    try:
        # Map level to display style
        level_map = {
            "info": "info",
            "warning": "warning",
            "error": "error",
            "success": "success"
        }
        
        display_level = level_map.get(level, "info")
        
        # Display message
        print(_format_message(message, f"Notification ({level})", display_level))
        
        # Handle blocking notification
        if blocking:
            print("\nThis notification requires acknowledgement.")
            
            if continue_condition == "user_input":
                response = input("Press Enter to acknowledge, or type 'skip' to bypass: ").strip()
                if response.lower() == 'skip':
                    return "Notification skipped by user"
                else:
                    return "Notification acknowledged by user"
            elif continue_condition == "timeout":
                timeout = 5
                print(f"Waiting {timeout} seconds for acknowledgement...")
                time.sleep(timeout)
                return f"Notification timeout after {timeout} seconds"
            else:
                return f"Unknown continue condition: {continue_condition}"
        else:
            return f"Notification displayed (level: {level})"
            
    except KeyboardInterrupt:
        return "Notification interrupted by user"
    except Exception as e:
        return f"Error in notify_user: {str(e)}"

# ============================================================================
# 内部处理函数
# ============================================================================

def _handle_ask_interaction(question, options, allow_multiple, require_confirmation,
                          confirmation_text, timeout_action):
    """Handle ask interaction type."""
    if not question:
        return "Error: Question is required for 'ask' interaction type"
    
    if not options:
        return "Error: Options are required for 'ask' interaction type"
    
    options_list = _parse_options(options)
    
    if not options_list:
        return "Error: No valid options provided"
    
    # Display question
    print(_format_message(question, "Question", "info"))
    print("\nOptions:")
    
    for i, option in enumerate(options_list, 1):
        print(f"  {i}. {option}")
    
    # Get selection
    if allow_multiple:
        prompt = f"\nEnter choice numbers separated by commas (e.g., 1,3) or 'all': "
    else:
        prompt = f"\nEnter choice number (1-{len(options_list)}): "
    
    selection_input = input(prompt).strip()
    
    # Parse selection
    selected_indices = []
    if allow_multiple and selection_input.lower() == 'all':
        selected_indices = list(range(1, len(options_list) + 1))
    else:
        try:
            if allow_multiple:
                parts = [part.strip() for part in selection_input.split(',')]
                for part in parts:
                    if part:
                        idx = int(part)
                        if 1 <= idx <= len(options_list):
                            selected_indices.append(idx)
            else:
                idx = int(selection_input)
                if 1 <= idx <= len(options_list):
                    selected_indices.append(idx)
        except ValueError:
            return f"Error: Invalid input '{selection_input}'. Please enter numbers."
    
    if not selected_indices:
        return "Error: No valid selection made"
    
    # Get selected options
    selected_options = [options_list[i-1] for i in selected_indices]
    
    # Display selection
    if allow_multiple:
        selection_text = f"Selected: {', '.join(selected_options)}"
    else:
        selection_text = f"Selected: {selected_options[0]}"
    
    print(f"\n{selection_text}")
    
    # Request confirmation if needed
    if require_confirmation:
        if allow_multiple:
            confirm_prompt = f"{confirmation_text} (selected {len(selected_options)} items)? [yes/no]: "
        else:
            confirm_prompt = f"{confirmation_text}? [yes/no]: "
        
        confirm = input(confirm_prompt).strip().lower()
        
        if confirm in ['yes', 'y']:
            result = f"Confirmed selection: {selection_text}"
        else:
            result = "Selection cancelled by user"
    else:
        result = f"Selection recorded: {selection_text}"
    
    return result

def _handle_feedback_interaction(user_feedback_prompt, feedback_type, rating_scale,
                               blocking, save_to_file):
    """Handle feedback interaction type."""
    if not user_feedback_prompt:
        return "Error: user_feedback_prompt is required for 'feedback' interaction type"
    
    feedback_data = {
        "timestamp": datetime.now().isoformat(),
        "prompt": user_feedback_prompt,
        "feedback_type": feedback_type,
        "responses": {}
    }
    
    print(_format_message("User Feedback Request", "Feedback", "info"))
    print(f"\n{user_feedback_prompt}\n")
    
    # Collect feedback based on type
    if feedback_type == "rating" or feedback_type == "mixed":
        print(f"Please provide a rating ({rating_scale}):")
        
        # Parse rating scale
        if '-' in rating_scale:
            try:
                min_rating, max_rating = map(int, rating_scale.split('-'))
                rating_prompt = f"Enter rating ({min_rating}-{max_rating}): "
                while True:
                    rating_input = input(rating_prompt).strip()
                    try:
                        rating = int(rating_input)
                        if min_rating <= rating <= max_rating:
                            feedback_data["responses"]["rating"] = rating
                            break
                        else:
                            print(f"Please enter a number between {min_rating} and {max_rating}")
                    except ValueError:
                        print("Please enter a valid number")
            except:
                rating_input = input(f"Enter rating ({rating_scale}): ").strip()
                feedback_data["responses"]["rating"] = rating_input
        else:
            rating_input = input(f"Enter rating ({rating_scale}): ").strip()
            feedback_data["responses"]["rating"] = rating_input
    
    if feedback_type == "text" or feedback_type == "mixed":
        print("\nPlease provide detailed feedback (press Enter twice to finish):")
        lines = []
        while True:
            try:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    lines.pop()  # Remove last empty line
                    break
                lines.append(line)
            except EOFError:
                break
            except KeyboardInterrupt:
                return "Feedback collection interrupted"
        
        text_feedback = "\n".join(lines)
        if text_feedback.strip():
            feedback_data["responses"]["text"] = text_feedback
    
    if feedback_type == "choice" or feedback_type == "mixed":
        print("\nPlease choose from the following options:")
        print("1. Excellent")
        print("2. Good")
        print("3. Average")
        print("4. Poor")
        print("5. Very poor")
        
        choice = input("Enter choice (1-5): ").strip()
        choice_map = {
            "1": "Excellent",
            "2": "Good",
            "3": "Average",
            "4": "Poor",
            "5": "Very poor"
        }
        
        if choice in choice_map:
            feedback_data["responses"]["choice"] = choice_map[choice]
        else:
            feedback_data["responses"]["choice"] = f"Invalid choice: {choice}"
    
    # Save to file if requested
    if save_to_file:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_to_file) if os.path.dirname(save_to_file) else '.', exist_ok=True)
            
            # Load existing feedback if file exists
            existing_data = []
            if os.path.exists(save_to_file):
                try:
                    with open(save_to_file, 'r') as f:
                        existing_data = json.load(f)
                        if not isinstance(existing_data, list):
                            existing_data = [existing_data]
                except:
                    existing_data = []
            
            # Add new feedback
            existing_data.append(feedback_data)
            
            # Save back
            with open(save_to_file, 'w') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
            
            feedback_data["saved_to"] = save_to_file
        except Exception as e:
            print(f"Warning: Could not save feedback to file: {str(e)}")
    
    # Format response
    response_summary = []
    for key, value in feedback_data["responses"].items():
        if isinstance(value, str) and len(value) > 100:
            response_summary.append(f"{key}: {value[:100]}...")
        else:
            response_summary.append(f"{key}: {value}")
    
    result = f"Feedback received:\n" + "\n".join(response_summary)
    
    if save_to_file and "saved_to" in feedback_data:
        result += f"\n\nFeedback saved to: {save_to_file}"
    
    return result

def _handle_confirmation_interaction(question, require_confirmation, blocking, continue_condition):
    """Handle confirmation interaction type."""
    if not question:
        return "Error: Question is required for 'confirm' interaction type"
    
    if not blocking:
        print(_format_message(question, "Confirmation Request", "warning"))
        return "Non-blocking confirmation displayed (assuming user will respond later)"
    
    # Blocking mode - wait for user response
    print(_format_message("ACTION REQUIRED", "Blocking Confirmation", "warning"))
    print(f"\n❓ {question}\n")
    
    if continue_condition == "user_input":
        print("This operation requires your confirmation to proceed.")
        response = input("Type 'yes' to confirm, 'no' to cancel, or press Enter to abort: ").strip().lower()
        
        if response in ['yes', 'y']:
            return "User confirmed - proceeding with operation"
        elif response in ['no', 'n']:
            return "User cancelled - operation aborted"
        else:
            return "No confirmation received - operation aborted"
    
    elif continue_condition == "specific_answer":
        answer = input("Please type 'I CONFIRM' to proceed: ").strip()
        if answer == "I CONFIRM":
            return "Explicit confirmation received - proceeding"
        else:
            return "Incorrect confirmation phrase - operation aborted"
    
    else:
        return f"Unknown continue condition: {continue_condition}"

def _handle_validation_interaction(question, expected_answer, validation_regex, retry_count):
    """Handle validation interaction type."""
    if not question:
        return "Error: Question is required for 'validate' interaction type"
    
    import re
    
    print(_format_message(question, "Validated Input", "info"))
    
    if expected_answer:
        print(f"Expected format: {expected_answer}")
    
    for attempt in range(1, retry_count + 1):
        user_input = input(f"\nAttempt {attempt}/{retry_count}: ").strip()
        
        # Validate using regex if provided
        if validation_regex:
            try:
                pattern = re.compile(validation_regex)
                if pattern.match(user_input):
                    return f"Valid input received: {user_input}"
                else:
                    print(f"Input does not match pattern: {validation_regex}")
                    continue
            except re.error as e:
                return f"Error in validation regex: {str(e)}"
        
        # Validate using expected answer if provided
        elif expected_answer:
            if user_input == expected_answer:
                return f"Correct input received: {user_input}"
            else:
                print(f"Input does not match expected: {expected_answer}")
                continue
        
        # No validation - accept any non-empty input
        elif user_input:
            return f"Input received: {user_input}"
        else:
            print("Input cannot be empty")
            continue
    
    return f"Error: Maximum retries ({retry_count}) exceeded"

def _handle_wizard_interaction(interactive_mode, save_to_file):
    """Handle wizard interaction type."""
    if not interactive_mode:
        return "Interactive wizard requires interactive_mode=True"
    
    print(_format_message("Interactive Wizard", "Step-by-Step Setup", "info"))
    print("\nThis wizard will guide you through a series of questions.")
    print("Press Enter to accept defaults, or type your answers.\n")
    
    wizard_data = {
        "timestamp": datetime.now().isoformat(),
        "steps": []
    }
    
    # Define wizard steps
    steps = [
        {
            "question": "What is your name?",
            "key": "name",
            "default": "User"
        },
        {
            "question": "What is your email address?",
            "key": "email",
            "validation_regex": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        },
        {
            "question": "Select your preferred language (Python/JavaScript/Java/Other):",
            "key": "language",
            "default": "Python"
        },
        {
            "question": "Rate your experience level (1-10):",
            "key": "experience_level",
            "validation_regex": r'^[1-9]|10$'
        },
        {
            "question": "Any additional comments?",
            "key": "comments",
            "multiline": True
        }
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"\n{'='*60}")
        print(f"Step {i}/{len(steps)}")
        print(f"{'='*60}")
        
        question = step["question"]
        key = step["key"]
        default = step.get("default")
        validation_regex = step.get("validation_regex")
        multiline = step.get("multiline", False)
        
        # Display question with default
        prompt = question
        if default:
            prompt += f" [{default}]"
        prompt += ": "
        
        print(f"\n{question}")
        
        # Get input
        if multiline:
            print("(Enter multiple lines, press Enter twice to finish)")
            lines = []
            while True:
                try:
                    line = input()
                    if line == "" and lines and lines[-1] == "":
                        lines.pop()  # Remove last empty line
                        break
                    lines.append(line)
                except EOFError:
                    break
            
            value = "\n".join(lines) if lines else default or ""
        else:
            value = input(prompt).strip()
            if not value and default:
                value = default
                print(f"Using default: {default}")
        
        # Validate if regex provided
        if validation_regex and value:
            import re
            if not re.match(validation_regex, value):
                print(f"⚠️  Warning: Input does not match expected format")
                # Ask for confirmation to continue
                confirm = input("Continue anyway? [yes/no]: ").strip().lower()
                if confirm not in ['yes', 'y']:
                    return "Wizard cancelled by user"
        
        # Store result
        wizard_data["steps"].append({
            "step": i,
            "question": question,
            "key": key,
            "value": value
        })
        
        wizard_data[key] = value
    
    # Save to file if requested
    if save_to_file:
        try:
            os.makedirs(os.path.dirname(save_to_file) if os.path.dirname(save_to_file) else '.', exist_ok=True)
            with open(save_to_file, 'w') as f:
                json.dump(wizard_data, f, indent=2, ensure_ascii=False)
            wizard_data["saved_to"] = save_to_file
        except Exception as e:
            print(f"Warning: Could not save wizard data: {str(e)}")
    
    # Format results
    results = ["Wizard completed successfully!", ""]
    for step in wizard_data["steps"]:
        value = step["value"]
        if isinstance(value, str) and len(value) > 50:
            display_value = value[:50] + "..."
        else:
            display_value = value
        results.append(f"{step['key']}: {display_value}")
    
    if save_to_file and "saved_to" in wizard_data:
        results.append(f"\nResults saved to: {save_to_file}")
    
    return "\n".join(results)

# ============================================================================
# 向后兼容性：包装现有函数
# ============================================================================

def ask_user_with_options(question: str, options: str, 
                         allow_multiple: bool = False,
                         require_confirmation: bool = True,
                         confirmation_text: str = "Please confirm your selection",
                         timeout_action: str = "abort") -> str:
    '''
    向后兼容：包装 ask 功能
    '''
    return discuss_with_user(
        interaction_type="ask",
        question=question,
        options=options,
        allow_multiple=allow_multiple,
        require_confirmation=require_confirmation,
        confirmation_text=confirmation_text,
        timeout_action=timeout_action
    )

def get_user_feedback(user_feedback_prompt: str, feedback_type: str = "mixed",
                     rating_scale: str = "1-5", blocking: bool = True,
                     save_to_file: str = None) -> str:
    '''
    向后兼容：包装 feedback 功能
    '''
    return discuss_with_user(
        interaction_type="feedback",
        user_feedback_prompt=user_feedback_prompt,
        feedback_type=feedback_type,
        rating_scale=rating_scale,
        blocking=blocking,
        save_to_file=save_to_file
    )

def blocking_confirmation(question: str, require_confirmation: bool = True,
                         blocking: bool = True, continue_condition: str = "user_input") -> str:
    '''
    向后兼容：包装 confirm 功能
    '''
    return discuss_with_user(
        interaction_type="confirm",
        question=question,
        require_confirmation=require_confirmation,
        blocking=blocking,
        continue_condition=continue_condition
    )

def get_validated_input(question: str, expected_answer: str = None,
                       validation_regex: str = None, retry_count: int = 3) -> str:
    '''
    向后兼容：包装 validate 功能
    '''
    return discuss_with_user(
        interaction_type="validate",
        question=question,
        expected_answer=expected_answer,
        validation_regex=validation_regex,
        retry_count=retry_count
    )

def interactive_wizard(interactive_mode: bool = True, save_to_file: str = None) -> str:
    '''
    向后兼容：包装 wizard 功能
    '''
    return discuss_with_user(
        interaction_type="wizard",
        interactive_mode=interactive_mode,
        save_to_file=save_to_file
    )

def pause_until_user_input(question: str = "Press Enter to continue...",
                          blocking: bool = True, continue_condition: str = "user_input") -> str:
    '''
    向后兼容：包装 pause 功能（使用 notify_user）
    '''
    return notify_user(
        message=question,
        level="info",
        blocking=blocking,
        continue_condition=continue_condition
    )

# ============================================================================
# Tool Call Map (保持向后兼容性)
# ============================================================================

TOOL_CALL_MAP = {
    "ask_user_with_options": ask_user_with_options,
    "get_user_feedback": get_user_feedback,
    "blocking_confirmation": blocking_confirmation,
    "get_validated_input": get_validated_input,
    "interactive_wizard": interactive_wizard,
    "pause_until_user_input": pause_until_user_input,
    "discuss_with_user": discuss_with_user,
    "notify_user": notify_user,
}