#!/usr/bin/env python3
"""
AskUserQuestionTool单元测试

测试Claude Code兼容的AskUserQuestionTool简化实现。
注意：这是一个交互式工具，测试时使用非交互模式。
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加父目录到路径以便导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from interaction.ask_user_question_tool import ask_user_question, _parse_questions_input, _parse_optional_json
from interaction.ask_user_question_tool import AskUserQuestionConfig

class TestAskUserQuestionTool:
    """AskUserQuestionTool测试类"""
    
    def setup_method(self):
        """测试前设置"""
        self.test_dir = tempfile.mkdtemp(prefix="test_ask_user_question_")
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # 设置环境变量以使用非交互模式
        os.environ["ASK_USER_QUESTION_INTERACTIVE"] = "false"
        os.environ["ASK_USER_QUESTION_NON_INTERACTIVE_MODE"] = "first_option"
        os.environ["ASK_USER_QUESTION_ALLOW_SKIP"] = "false"
    
    def teardown_method(self):
        """测试后清理"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
        
        # 清理环境变量
        for key in [
            "ASK_USER_QUESTION_INTERACTIVE",
            "ASK_USER_QUESTION_NON_INTERACTIVE_MODE",
            "ASK_USER_QUESTION_ALLOW_SKIP",
            "ASK_USER_QUESTION_SKIP_ANSWER"
        ]:
            if key in os.environ:
                del os.environ[key]
    
    def _create_sample_questions_json(self) -> str:
        """创建示例问题JSON"""
        sample_questions = [
            {
                "question": "Which library should we use for date formatting?",
                "header": "Library Choice",
                "options": [
                    {
                        "label": "Moment.js",
                        "description": "Popular library with extensive features, but large bundle size",
                        "preview": "<div>Moment.js: 329KB minified</div>"
                    },
                    {
                        "label": "date-fns",
                        "description": "Modular library with tree-shaking support, smaller footprint",
                        "preview": "<div>date-fns: ~80KB for common functions</div>"
                    },
                    {
                        "label": "Day.js",
                        "description": "Lightweight alternative to Moment.js with similar API",
                        "preview": "<div>Day.js: 2KB minified</div>"
                    }
                ],
                "multiSelect": False
            },
            {
                "question": "Which features do you want to enable?",
                "header": "Features",
                "options": [
                    {
                        "label": "Dark mode",
                        "description": "Enable dark theme support",
                        "preview": "<div>Dark mode toggle component</div>"
                    },
                    {
                        "label": "Analytics",
                        "description": "Add user analytics tracking",
                        "preview": "<div>Analytics dashboard integration</div>"
                    },
                    {
                        "label": "Notifications",
                        "description": "Enable browser notifications",
                        "preview": "<div>Notification permission request</div>"
                    },
                    {
                        "label": "Offline support",
                        "description": "Add service worker for offline usage",
                        "preview": "<div>Service worker configuration</div>"
                    }
                ],
                "multiSelect": True
            }
        ]
        return json.dumps(sample_questions)
    
    def test_ask_user_question_basic_functionality(self):
        """测试基本功能（非交互模式）"""
        questions_json = self._create_sample_questions_json()
        result = ask_user_question(questions_json)
        data = json.loads(result)
        
        assert "questions" in data
        assert "answers" in data
        assert "annotations" in data
        assert "durationMs" in data
        assert data["durationMs"] >= 0
        
        # 验证问题正确返回
        questions = data["questions"]
        assert len(questions) == 2
        assert questions[0]["question"] == "Which library should we use for date formatting?"
        assert questions[0]["header"] == "Library Choice"
        assert len(questions[0]["options"]) == 3
        assert questions[0]["multiSelect"] is False
        
        # 验证回答（在first_option模式下，应该选择第一个选项）
        answers = data["answers"]
        assert len(answers) == 2
        assert "Which library should we use for date formatting?" in answers
        assert "Which features do you want to enable?" in answers
        
        # 第一个问题是单选，应该返回第一个选项的label
        assert answers["Which library should we use for date formatting?"] == "Moment.js"
        
        # 第二个问题是多选，在first_option模式下应该返回第一个选项
        # 注意：多选在first_option模式下也返回单个选项
        assert answers["Which features do you want to enable?"] == "Dark mode"
        
        # 验证注释
        annotations = data["annotations"]
        assert len(annotations) == 2
        for question_text in answers.keys():
            assert question_text in annotations
            assert "notes" in annotations[question_text]
            assert "simulation" in annotations[question_text]["notes"].lower()
    
    def test_ask_user_question_with_provided_answers(self):
        """测试提供已有回答的情况"""
        questions_json = self._create_sample_questions_json()
        
        # 提供已有的回答
        provided_answers = {
            "Which library should we use for date formatting?": "date-fns",
            "Which features do you want to enable?": "Dark mode, Analytics"
        }
        
        result = ask_user_question(
            questions_json,
            answers=json.dumps(provided_answers)
        )
        data = json.loads(result)
        
        # 应该使用提供的回答，而不是收集新的
        answers = data["answers"]
        assert answers["Which library should we use for date formatting?"] == "date-fns"
        assert answers["Which features do you want to enable?"] == "Dark mode, Analytics"
    
    def test_ask_user_question_with_annotations_and_metadata(self):
        """测试提供注释和元数据的情况"""
        questions_json = self._create_sample_questions_json()
        
        # 提供注释和元数据
        provided_annotations = {
            "Which library should we use for date formatting?": {
                "preview": "<div>User reviewed all previews</div>",
                "notes": "User prefers modern, lightweight libraries"
            }
        }
        
        provided_metadata = {
            "source": "test_suite",
            "timestamp": "2024-04-04T18:45:00Z"
        }
        
        result = ask_user_question(
            questions_json,
            annotations=json.dumps(provided_annotations),
            metadata=json.dumps(provided_metadata)
        )
        data = json.loads(result)
        
        # 验证元数据
        assert "metadata" in data
        assert data["metadata"]["source"] == "test_suite"
        assert data["metadata"]["timestamp"] == "2024-04-04T18:45:00Z"
        
        # 验证注释合并
        annotations = data["annotations"]
        assert len(annotations) == 2
        
        # 第一个问题应该有提供的注释
        q1_key = "Which library should we use for date formatting?"
        assert q1_key in annotations
        assert annotations[q1_key]["preview"] == "<div>User reviewed all previews</div>"
        assert annotations[q1_key]["notes"] == "User prefers modern, lightweight libraries"
        
        # 第二个问题应该有生成的注释
        q2_key = "Which features do you want to enable?"
        assert q2_key in annotations
        assert "notes" in annotations[q2_key]
    
    def test_ask_user_question_random_mode(self):
        """测试随机回答模式"""
        # 设置随机模式
        os.environ["ASK_USER_QUESTION_NON_INTERACTIVE_MODE"] = "random"
        
        questions_json = self._create_sample_questions_json()
        result = ask_user_question(questions_json)
        data = json.loads(result)
        
        answers = data["answers"]
        # 在随机模式下，回答应该是有效的选项标签
        valid_labels_q1 = ["Moment.js", "date-fns", "Day.js"]
        valid_labels_q2 = ["Dark mode", "Analytics", "Notifications", "Offline support"]
        
        assert answers["Which library should we use for date formatting?"] in valid_labels_q1
        
        # 多选回答可能是单个或多个选项（逗号分隔）
        q2_answer = answers["Which features do you want to enable?"]
        # 如果是逗号分隔的多个选项，拆分检查
        if "," in q2_answer:
            selected = [label.strip() for label in q2_answer.split(",")]
            for label in selected:
                assert label in valid_labels_q2
        else:
            assert q2_answer in valid_labels_q2
    
    def test_ask_user_question_simulate_mode(self):
        """测试智能模拟回答模式"""
        # 设置模拟模式
        os.environ["ASK_USER_QUESTION_NON_INTERACTIVE_MODE"] = "simulate"
        
        questions_json = self._create_sample_questions_json()
        result = ask_user_question(questions_json)
        data = json.loads(result)
        
        # 在模拟模式下，应该返回有效的回答
        answers = data["answers"]
        assert len(answers) == 2
        # 回答应该是有效的字符串
        for answer in answers.values():
            assert isinstance(answer, str)
            assert len(answer) > 0
    
    def test_ask_user_question_invalid_json_input(self):
        """测试无效JSON输入"""
        result = ask_user_question("invalid json")
        data = json.loads(result)
        
        assert "error" in data
        assert "questions" in data
        assert "answers" in data
        assert "annotations" in data
        assert len(data["questions"]) == 0
        assert len(data["answers"]) == 0
        assert len(data["annotations"]) == 0
        assert "durationMs" in data
    
    def test_ask_user_question_empty_questions_list(self):
        """测试空问题列表"""
        result = ask_user_question("[]")
        data = json.loads(result)
        
        assert "error" in data
        assert "must have 1-4 questions" in data["error"].lower()
    
    def test_ask_user_question_too_many_questions(self):
        """测试问题数量过多"""
        # 创建5个问题（超出限制）
        too_many_questions = [
            {
                "question": f"Question {i}",
                "header": f"Header {i}",
                "options": [
                    {"label": "Option A", "description": "Description A"},
                    {"label": "Option B", "description": "Description B"}
                ],
                "multiSelect": False
            }
            for i in range(5)  # 5个问题，超出1-4的限制
        ]
        
        result = ask_user_question(json.dumps(too_many_questions))
        data = json.loads(result)
        
        assert "error" in data
        assert "must have 1-4 questions" in data["error"].lower()
    
    def test_ask_user_question_missing_required_fields(self):
        """测试缺少必需字段"""
        invalid_questions = [
            {
                "question": "Test question",
                # 缺少header字段
                "options": [
                    {"label": "Option A", "description": "Description A"}
                ]
            }
        ]
        
        result = ask_user_question(json.dumps(invalid_questions))
        data = json.loads(result)
        
        assert "error" in data
        assert "must have 'header'" in data["error"]
    
    def test_ask_user_question_duplicate_question_texts(self):
        """测试重复的问题文本"""
        duplicate_questions = [
            {
                "question": "Same question",
                "header": "Header 1",
                "options": [
                    {"label": "Option A", "description": "Description A"},
                    {"label": "Option B", "description": "Description B"}
                ]
            },
            {
                "question": "Same question",  # 重复的问题文本
                "header": "Header 2",
                "options": [
                    {"label": "Option C", "description": "Description C"},
                    {"label": "Option D", "description": "Description D"}
                ]
            }
        ]
        
        result = ask_user_question(json.dumps(duplicate_questions))
        data = json.loads(result)
        
        assert "error" in data
        assert "must be unique" in data["error"].lower()
    
    def test_ask_user_question_duplicate_option_labels(self):
        """测试重复的选项标签"""
        invalid_question = [
            {
                "question": "Test question",
                "header": "Test header",
                "options": [
                    {"label": "Same label", "description": "Description A"},
                    {"label": "Same label", "description": "Description B"}  # 重复的标签
                ]
            }
        ]
        
        result = ask_user_question(json.dumps(invalid_question))
        data = json.loads(result)
        
        assert "error" in data
        assert "must be unique" in data["error"].lower() or "duplicate" in data["error"].lower()
    
    def test_ask_user_question_insufficient_options(self):
        """测试选项数量不足"""
        invalid_question = [
            {
                "question": "Test question",
                "header": "Test header",
                "options": [
                    {"label": "Only one option", "description": "Description"}  # 只有1个选项，需要2-4个
                ]
            }
        ]
        
        result = ask_user_question(json.dumps(invalid_question))
        data = json.loads(result)
        
        assert "error" in data
        assert "must have 2-4 options" in data["error"].lower()
    
    def test_ask_user_question_too_many_options(self):
        """测试选项数量过多"""
        invalid_question = [
            {
                "question": "Test question",
                "header": "Test header",
                "options": [
                    {"label": f"Option {i}", "description": f"Description {i}"}
                    for i in range(5)  # 5个选项，超出2-4的限制
                ]
            }
        ]
        
        result = ask_user_question(json.dumps(invalid_question))
        data = json.loads(result)
        
        assert "error" in data
        assert "must have 2-4 options" in data["error"].lower()
    
    def test_ask_user_question_claude_code_compatibility(self):
        """测试Claude Code兼容性"""
        questions_json = self._create_sample_questions_json()
        result = ask_user_question(questions_json)
        data = json.loads(result)
        
        # 检查必需字段
        assert "questions" in data
        assert "answers" in data
        assert "annotations" in data
        assert "durationMs" in data
        
        # 检查数据类型
        assert isinstance(data["questions"], list)
        assert isinstance(data["answers"], dict)
        assert isinstance(data["annotations"], dict)
        assert isinstance(data["durationMs"], int)
        
        # 检查问题结构
        for question in data["questions"]:
            assert "question" in question
            assert "header" in question
            assert "options" in question
            assert "multiSelect" in question
            assert isinstance(question["multiSelect"], bool)
            
            # 检查选项结构
            for option in question["options"]:
                assert "label" in option
                assert "description" in option
                # preview是可选的
    
    def test_parse_questions_input_valid(self):
        """测试_parse_questions_input函数（有效输入）"""
        valid_json = self._create_sample_questions_json()
        parsed = _parse_questions_input(valid_json)
        
        assert len(parsed) == 2
        assert parsed[0]["question"] == "Which library should we use for date formatting?"
        assert parsed[0]["header"] == "Library Choice"
        assert len(parsed[0]["options"]) == 3
        assert parsed[0]["multiSelect"] is False
        
        assert parsed[1]["question"] == "Which features do you want to enable?"
        assert parsed[1]["header"] == "Features"
        assert len(parsed[1]["options"]) == 4
        assert parsed[1]["multiSelect"] is True
    
    def test_parse_questions_input_invalid(self):
        """测试_parse_questions_input函数（无效输入）"""
        # 无效JSON
        try:
            _parse_questions_input("invalid")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
        
        # 非列表JSON
        try:
            _parse_questions_input('{"not": "a list"}')
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
    
    def test_parse_optional_json(self):
        """测试_parse_optional_json函数"""
        # 有效JSON
        result = _parse_optional_json('{"key": "value"}', "test")
        assert result == {"key": "value"}
        
        # None或空字符串
        assert _parse_optional_json(None, "test") is None
        assert _parse_optional_json("", "test") is None
        assert _parse_optional_json("  ", "test") is None
        
        # 无效JSON
        try:
            _parse_optional_json("invalid", "test")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
    
    def test_ask_user_question_config_from_env(self):
        """测试AskUserQuestionConfig从环境变量加载"""
        # 设置环境变量
        os.environ["ASK_USER_QUESTION_INTERACTIVE"] = "false"
        os.environ["ASK_USER_QUESTION_NON_INTERACTIVE_MODE"] = "random"
        os.environ["ASK_USER_QUESTION_ALLOW_SKIP"] = "true"
        os.environ["ASK_USER_QUESTION_SKIP_ANSWER"] = "user_skipped"
        
        config = AskUserQuestionConfig.from_env()
        
        assert config.interactive_mode is False
        assert config.non_interactive_mode == "random"
        assert config.allow_skip is True
        assert config.skip_answer == "user_skipped"
        
        # 测试默认值
        del os.environ["ASK_USER_QUESTION_INTERACTIVE"]
        del os.environ["ASK_USER_QUESTION_NON_INTERACTIVE_MODE"]
        del os.environ["ASK_USER_QUESTION_ALLOW_SKIP"]
        del os.environ["ASK_USER_QUESTION_SKIP_ANSWER"]
        
        config = AskUserQuestionConfig.from_env()
        assert config.interactive_mode is True  # 默认True
        assert config.non_interactive_mode == "simulate"
        assert config.allow_skip is True
        assert config.skip_answer == "skipped"
    
    @patch('interaction.ask_user_question_tool._get_user_answer_interactive')
    @patch('interaction.ask_user_question_tool._display_question')
    def test_ask_user_question_interactive_mode_mocked(self, mock_display, mock_get_answer):
        """测试交互模式（使用mock）"""
        # 设置交互模式
        os.environ["ASK_USER_QUESTION_INTERACTIVE"] = "true"
        
        # 设置mock返回值
        mock_get_answer.side_effect = ["Moment.js", "Dark mode, Analytics"]
        
        questions_json = self._create_sample_questions_json()
        result = ask_user_question(questions_json)
        data = json.loads(result)
        
        # 验证mock被调用
        assert mock_display.call_count == 2
        assert mock_get_answer.call_count == 2
        
        # 验证结果
        answers = data["answers"]
        assert answers["Which library should we use for date formatting?"] == "Moment.js"
        assert answers["Which features do you want to enable?"] == "Dark mode, Analytics"
        
        # 验证注释
        annotations = data["annotations"]
        assert len(annotations) == 2
        for question_text in answers.keys():
            assert question_text in annotations
            assert "notes" in annotations[question_text]
            assert "interactive" in annotations[question_text]["notes"].lower()
    
    def test_ask_user_question_single_question(self):
        """测试单个问题的情况"""
        single_question = [
            {
                "question": "Do you agree to the terms?",
                "header": "Agreement",
                "options": [
                    {"label": "Yes", "description": "I agree to the terms"},
                    {"label": "No", "description": "I do not agree"}
                ],
                "multiSelect": False
            }
        ]
        
        result = ask_user_question(json.dumps(single_question))
        data = json.loads(result)
        
        assert len(data["questions"]) == 1
        assert len(data["answers"]) == 1
        assert "Do you agree to the terms?" in data["answers"]
        
        # 在first_option模式下，应该选择"Yes"
        assert data["answers"]["Do you agree to the terms?"] == "Yes"
    
    def test_ask_user_question_minimum_options(self):
        """测试最小选项数量（2个选项）"""
        min_options_question = [
            {
                "question": "Binary choice",
                "header": "Choice",
                "options": [
                    {"label": "Option A", "description": "First option"},
                    {"label": "Option B", "description": "Second option"}
                ],
                "multiSelect": False
            }
        ]
        
        result = ask_user_question(json.dumps(min_options_question))
        data = json.loads(result)
        
        # 应该成功解析
        assert "error" not in data
        assert len(data["questions"]) == 1
        assert len(data["questions"][0]["options"]) == 2

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])