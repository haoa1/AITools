#!/usr/bin/env python3
"""
Tests for SkillSearchTool (Claude Code compatible version).
"""

import os
import sys
import json
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skill.skill_search_tool import (
    skill_search, 
    _parse_skills_result,
    _extract_skill_categories,
    _calculate_search_score,
    _get_content_snippet
)


class TestSkillSearchToolHelpers(unittest.TestCase):
    """Test helper functions for SkillSearchTool."""
    
    def test_parse_skills_result_valid(self):
        """Test parsing valid skills result."""
        skills_data = "[{'name': 'test_skill', 'description': 'A test skill'}]"
        result = _parse_skills_result(skills_data)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'test_skill')
        self.assertEqual(result[0]['description'], 'A test skill')
    
    def test_parse_skills_result_empty(self):
        """Test parsing empty skills result."""
        result = _parse_skills_result("")
        self.assertEqual(result, [])
    
    def test_parse_skills_result_error(self):
        """Test parsing error result."""
        result = _parse_skills_result("Error: No skills found")
        self.assertEqual(result, [])
    
    def test_parse_skills_result_invalid(self):
        """Test parsing invalid skills result."""
        result = _parse_skills_result("Not a valid skills list")
        self.assertEqual(result, [])
    
    def test_extract_skill_categories_from_name(self):
        """Test extracting categories from skill name."""
        categories = _extract_skill_categories("file_reader", "# File Reader Skill")
        
        self.assertIn('file', categories)
        self.assertNotIn('git', categories)
    
    def test_extract_skill_categories_git(self):
        """Test extracting git categories."""
        categories = _extract_skill_categories("git_commit", "# Git Commit Skill")
        
        self.assertIn('git', categories)
    
    def test_extract_skill_categories_web(self):
        """Test extracting web categories."""
        categories = _extract_skill_categories("web_fetcher", "# Web Fetcher Skill")
        
        self.assertIn('web', categories)
    
    def test_extract_skill_categories_system(self):
        """Test extracting system categories."""
        categories = _extract_skill_categories("bash_runner", "# Bash Runner Skill")
        
        self.assertIn('system', categories)
    
    def test_extract_skill_categories_from_frontmatter(self):
        """Test extracting categories from frontmatter."""
        content = """---
name: test_skill
categories: [file, analysis]
---
# Test Skill"""
        
        categories = _extract_skill_categories("test_skill", content)
        
        self.assertIn('file', categories)
        self.assertIn('analysis', categories)
    
    def test_extract_skill_categories_multiple_sources(self):
        """Test extracting categories from both name and frontmatter."""
        content = """---
name: git_file_manager
category: hybrid
---
# Git File Manager"""
        
        categories = _extract_skill_categories("git_file_manager", content)
        
        self.assertIn('git', categories)  # From name
        self.assertIn('file', categories)  # From name
        self.assertIn('hybrid', categories)  # From frontmatter
    
    def test_calculate_search_score_name_match(self):
        """Test search score calculation with name match."""
        skill = {
            'name': 'file_reader',
            'description': 'Reads files'
        }
        
        score, reasons = _calculate_search_score(skill, "file")
        
        self.assertGreater(score, 0)
        self.assertIn('Name contains:', ';'.join(reasons))
    
    def test_calculate_search_score_exact_match(self):
        """Test search score calculation with exact match."""
        skill = {
            'name': 'file',
            'description': 'File operations'
        }
        
        score, reasons = _calculate_search_score(skill, "file", exact_match=True)
        
        self.assertGreater(score, 0)
        # In exact mode, "file" matches "file" exactly
        self.assertTrue(any('Exact name match' in reason for reason in reasons) or
                       any('Name contains' in reason for reason in reasons))
    
    def test_calculate_search_score_category_match(self):
        """Test search score calculation with category match."""
        skill = {
            'name': 'file_reader',
            'description': 'Reads files',
            'categories': ['file', 'io']
        }
        
        score, reasons = _calculate_search_score(skill, "test", target_category="file")
        
        self.assertGreater(score, 0)
        self.assertIn('Category matches', ';'.join(reasons))
    
    def test_calculate_search_score_no_match(self):
        """Test search score calculation with no match."""
        skill = {
            'name': 'file_reader',
            'description': 'Reads files'
        }
        
        score, reasons = _calculate_search_score(skill, "nonexistent")
        
        self.assertEqual(score, 0)
    
    def test_calculate_search_score_description_match(self):
        """Test search score calculation with description match."""
        skill = {
            'name': 'data_processor',
            'description': 'Processes file data'
        }
        
        score, reasons = _calculate_search_score(skill, "file")
        
        self.assertGreater(score, 0)
        self.assertIn('Description contains:', ';'.join(reasons))
    
    def test_get_content_snippet_success(self):
        """Test getting content snippet."""
        with patch('skill.skill_search_tool.load_skill_by_name') as mock_load:
            mock_load.return_value = """---
name: test_skill
---
# Test Skill

This is the content of the test skill with some details."""
            
            snippet = _get_content_snippet("test_skill", max_length=50)
            
            self.assertIsNotNone(snippet)
            self.assertLessEqual(len(snippet), 53)  # 50 + possible "..."
            mock_load.assert_called_once_with(skill_name="test_skill", max_sections=1)
    
    def test_get_content_snippet_no_content(self):
        """Test getting content snippet when no content."""
        with patch('skill.skill_search_tool.load_skill_by_name') as mock_load:
            mock_load.return_value = ""
            
            snippet = _get_content_snippet("test_skill")
            
            self.assertIsNone(snippet)
    
    def test_get_content_snippet_error(self):
        """Test getting content snippet when error occurs."""
        with patch('skill.skill_search_tool.load_skill_by_name') as mock_load:
            mock_load.side_effect = Exception("Load failed")
            
            snippet = _get_content_snippet("test_skill")
            
            self.assertIsNone(snippet)


class TestSkillSearchToolMain(unittest.TestCase):
    """Test main skill_search function."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for tests
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def _parse_result(self, result_str):
        """Parse JSON result from skill_search function."""
        return json.loads(result_str)
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_empty_query(self, mock_get_skills):
        """Test search with empty query."""
        result = skill_search("")
        data = self._parse_result(result)
        
        self.assertIn("error", data)
        self.assertFalse(data.get("success", True))
        self.assertIn("non-empty string", data["error"])
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_invalid_limit(self, mock_get_skills):
        """Test search with invalid limit."""
        result = skill_search("test", limit=0)
        data = self._parse_result(result)
        
        self.assertIn("error", data)
        self.assertFalse(data.get("success", True))
        self.assertIn("must be positive", data["error"])
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_no_skills_available(self, mock_get_skills):
        """Test search when no skills are available."""
        mock_get_skills.return_value = ""
        
        result = skill_search("test")
        data = self._parse_result(result)
        
        self.assertTrue(data.get("success", False))
        self.assertEqual(data["results_count"], 0)
        self.assertEqual(data["results"], [])
        self.assertIn("No skills available", data["message"])
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_successful_search(self, mock_get_skills):
        """Test successful skill search."""
        # Mock skills data
        mock_skills = "[{'name': 'file_reader', 'description': 'Reads files from disk'}, " \
                      "{'name': 'web_fetcher', 'description': 'Fetches web content'}]"
        mock_get_skills.return_value = mock_skills
        
        # Mock load_skill_by_name for content snippets
        with patch('skill.skill_search_tool.load_skill_by_name') as mock_load:
            mock_load.return_value = "# Skill content\n\nThis skill does something useful."
            
            result = skill_search("file")
            data = self._parse_result(result)
            
            self.assertTrue(data.get("success", False))
            self.assertEqual(data["operation"], "skill_search")
            self.assertEqual(data["query"], "file")
            self.assertEqual(data["results_count"], 1)
            self.assertEqual(len(data["results"]), 1)
            
            # Check first result
            first_result = data["results"][0]
            self.assertEqual(first_result["name"], "file_reader")
            self.assertGreater(first_result["score"], 0)
            self.assertIn("reasons", first_result)
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_search_with_category_filter(self, mock_get_skills):
        """Test search with category filter."""
        # Mock skills data with categories in content
        mock_skills = "[{'name': 'file_reader', 'description': 'Reads files', 'content': '---\\nname: file_reader\\ncategories: [file]\\n---\\n# Content'}, " \
                      "{'name': 'git_commit', 'description': 'Git commit', 'content': '---\\nname: git_commit\\ncategories: [git]\\n---\\n# Content'}]"
        mock_get_skills.return_value = mock_skills
        
        result = skill_search("test", category="file")
        data = self._parse_result(result)
        
        self.assertTrue(data.get("success", False))
        self.assertEqual(data["category"], "file")
        
        # Should have at least one result
        self.assertGreaterEqual(data["results_count"], 1)
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_search_exact_match(self, mock_get_skills):
        """Test search with exact match."""
        mock_skills = "[{'name': 'file', 'description': 'File operations'}, " \
                      "{'name': 'file_reader', 'description': 'Reads files'}]"
        mock_get_skills.return_value = mock_skills
        
        result = skill_search("file", exact_match=True)
        data = self._parse_result(result)
        
        self.assertTrue(data.get("success", False))
        self.assertEqual(data["_metadata"]["search_mode"], "exact")
        
        # "file" should match "file" exactly better than "file_reader"
        if data["results_count"] > 0:
            first_result = data["results"][0]
            # The exact match "file" should have higher score
            self.assertEqual(first_result["name"], "file")
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_search_include_content(self, mock_get_skills):
        """Test search with content snippets."""
        mock_skills = "[{'name': 'file_reader', 'description': 'Reads files'}]"
        mock_get_skills.return_value = mock_skills
        
        with patch('skill.skill_search_tool.load_skill_by_name') as mock_load:
            mock_load.return_value = "# File Reader\n\nThis skill reads files from disk."
            
            result = skill_search("file", include_content=True, max_content_length=100)
            data = self._parse_result(result)
            
            self.assertTrue(data.get("success", False))
            self.assertTrue(data["_metadata"]["include_content"])
            self.assertEqual(data["_metadata"]["max_content_length"], 100)
            
            if data["results_count"] > 0:
                first_result = data["results"][0]
                self.assertIn("content_snippet", first_result)
                self.assertLessEqual(len(first_result["content_snippet"]), 103)  # 100 + "..."
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_search_limit(self, mock_get_skills):
        """Test search with limit."""
        # Create more skills than limit
        mock_skills = "[" + ", ".join(
            [f"{{'name': 'skill_{i}', 'description': 'Skill {i}'}}" 
             for i in range(15)]
        ) + "]"
        mock_get_skills.return_value = mock_skills
        
        result = skill_search("skill", limit=5)
        data = self._parse_result(result)
        
        self.assertTrue(data.get("success", False))
        self.assertEqual(data["results_count"], 5)
        self.assertEqual(len(data["results"]), 5)
        self.assertEqual(data["_metadata"]["limit_applied"], 5)
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_search_no_matches(self, mock_get_skills):
        """Test search with no matches."""
        mock_skills = "[{'name': 'file_reader', 'description': 'Reads files'}, " \
                      "{'name': 'web_fetcher', 'description': 'Fetches web content'}]"
        mock_get_skills.return_value = mock_skills
        
        result = skill_search("nonexistent_term")
        data = self._parse_result(result)
        
        self.assertTrue(data.get("success", False))
        # In fuzzy mode with no matches, should return all skills
        self.assertGreater(data["results_count"], 0)
        # But scores should be 0
        for result_item in data["results"]:
            self.assertEqual(result_item["score"], 0)
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_search_exact_match_no_matches(self, mock_get_skills):
        """Test exact match search with no matches."""
        mock_skills = "[{'name': 'file_reader', 'description': 'Reads files'}]"
        mock_get_skills.return_value = mock_skills
        
        result = skill_search("nonexistent", exact_match=True)
        data = self._parse_result(result)
        
        self.assertTrue(data.get("success", False))
        # In exact mode with no matches, should return empty results
        self.assertEqual(data["results_count"], 0)
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_search_error_handling(self, mock_get_skills):
        """Test error handling during search."""
        mock_get_skills.side_effect = Exception("Skills fetch failed")
        
        result = skill_search("test")
        data = self._parse_result(result)
        
        self.assertFalse(data.get("success", True))
        self.assertIn("error", data)
        self.assertIn("Skill search failed", data["error"])
    
    @patch('skill.skill_search_tool.get_skills_list')
    def test_search_json_structure(self, mock_get_skills):
        """Test JSON response structure."""
        mock_skills = "[{'name': 'test_skill', 'description': 'A test skill'}]"
        mock_get_skills.return_value = mock_skills
        
        result = skill_search("test")
        data = self._parse_result(result)
        
        # Check required fields
        required_fields = ["success", "operation", "query", "results_count", "results", "_metadata"]
        for field in required_fields:
            self.assertIn(field, data)
        
        # Check field types
        self.assertIsInstance(data["success"], bool)
        self.assertIsInstance(data["operation"], str)
        self.assertIsInstance(data["query"], str)
        self.assertIsInstance(data["results_count"], int)
        self.assertIsInstance(data["results"], list)
        self.assertIsInstance(data["_metadata"], dict)


class TestSkillSearchToolIntegration(unittest.TestCase):
    """Integration tests for SkillSearchTool module."""
    
    def test_module_exports(self):
        """Test module exports."""
        from skill.skill_search_tool import tools, TOOL_CALL_MAP
        
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        self.assertIsInstance(TOOL_CALL_MAP, dict)
        self.assertIn("skill_search", TOOL_CALL_MAP)
    
    def test_function_ai_decorator_presence(self):
        """Test that function_ai decorator is properly applied."""
        from skill.skill_search_tool import __SKILL_SEARCH_FUNCTION__
        
        # Check that the decorator was applied
        self.assertIsNotNone(__SKILL_SEARCH_FUNCTION__)
        self.assertIn("function", __SKILL_SEARCH_FUNCTION__)
        self.assertIn("name", __SKILL_SEARCH_FUNCTION__["function"])
        self.assertEqual(__SKILL_SEARCH_FUNCTION__["function"]["name"], "skill_search")
    
    def test_default_parameters(self):
        """Test function parameter defaults."""
        import inspect
        from skill.skill_search_tool import skill_search
        
        sig = inspect.signature(skill_search)
        params = sig.parameters
        
        self.assertIn('query', params)
        self.assertEqual(params['query'].default, inspect.Parameter.empty)  # Required
        
        self.assertIn('category', params)
        self.assertEqual(params['category'].default, None)
        
        self.assertIn('limit', params)
        self.assertEqual(params['limit'].default, 10)
        
        self.assertIn('exact_match', params)
        self.assertEqual(params['exact_match'].default, False)
        
        self.assertIn('include_content', params)
        self.assertEqual(params['include_content'].default, False)
        
        self.assertIn('max_content_length', params)
        self.assertEqual(params['max_content_length'].default, 200)


if __name__ == "__main__":
    unittest.main()