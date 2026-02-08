"""
Skill management module for AITools.

This module provides skill discovery, loading, and management operations.
Skills are stored in .agents/skills directory with SKILL.md files containing
YAML frontmatter and markdown content.
"""

__version__ = "1.0.0"
__author__ = "AITools Team"
__description__ = "Skill management operations module"

# Import skill operation functions
from .skill import (
    scan_skills,
    get_skills_list,
    get_skill_by_name,
    load_skill_by_name,
    get_skill_summary,
    ai_get_available_skills,
    ai_load_skill,
    ai_get_skill_summary,
    ai_recommend_skills,
    clear_skill_cache,
)

# Import tool definitions
from .skill import tools, TOOL_CALL_MAP

# List of all exported functions
__all__ = [
    'scan_skills',
    'get_skills_list',
    'get_skill_by_name',
    'load_skill_by_name',
    'get_skill_summary',
    'ai_get_available_skills',
    'ai_load_skill',
    'ai_get_skill_summary',
    'ai_recommend_skills',
    'clear_skill_cache',
    'tools',
    'TOOL_CALL_MAP',
]