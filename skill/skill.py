"""
Skill management module for AITools.

This module provides skill discovery, loading, and management operations.
Skills are stored in .agents/skills directory with SKILL.md files containing
YAML frontmatter and markdown content.
"""

from base import function_ai, parameters_func, property_param
import os
import yaml
import re
from typing import List, Dict, Optional, Tuple

# Global cache for loaded skills to avoid repeated file reads
_SKILL_CACHE = {}
_CONTENT_CACHE = {}

# Property definitions for skill parameters
__SKILLS_DIR_PROPERTY__ = property_param(
    name="skills_dir",
    description="Path to the skills directory (default: '.agents/skills').",
    t="string",
    required=False
)

__SKILL_NAME_PROPERTY__ = property_param(
    name="skill_name",
    description="Name of the skill to operate on.",
    t="string",
    required=True
)

__MAX_SECTIONS_PROPERTY__ = property_param(
    name="max_sections",
    description="Maximum number of sections to load (None for all).",
    t="integer",
    required=False
)

__SECTION_FILTER_PROPERTY__ = property_param(
    name="section_filter",
    description="String to filter sections by title.",
    t="string",
    required=False
)

__MAX_LENGTH_PROPERTY__ = property_param(
    name="max_length",
    description="Maximum length of summary in characters.",
    t="integer",
    required=False
)

__CLEAR_CACHE_PROPERTY__ = property_param(
    name="force",
    description="Force cache clearing (true/false).",
    t="boolean",
    required=False
)

__USER_QUERY_PROPERTY__ = property_param(
    name="user_query",
    description="User's request or question to match against skills.",
    t="string",
    required=True
)

__TOP_N_PROPERTY__ = property_param(
    name="top_n",
    description="Number of top recommendations to return (default: 3).",
    t="integer",
    required=False
)
# Parameters definitions
SCAN_SKILLS_PARAMS = parameters_func([__SKILLS_DIR_PROPERTY__])

GET_SKILLS_LIST_PARAMS = parameters_func([__SKILLS_DIR_PROPERTY__])

GET_SKILL_BY_NAME_PARAMS = parameters_func([
    __SKILL_NAME_PROPERTY__,
    __SKILLS_DIR_PROPERTY__
])

LOAD_SKILL_CONTENT_PARAMS = parameters_func([
    __SKILL_NAME_PROPERTY__,
    __MAX_SECTIONS_PROPERTY__,
    __SECTION_FILTER_PROPERTY__,
    __SKILLS_DIR_PROPERTY__
])

GET_SKILL_SUMMARY_PARAMS = parameters_func([
    __SKILL_NAME_PROPERTY__,
    __MAX_LENGTH_PROPERTY__,
    __SKILLS_DIR_PROPERTY__
])

AI_GET_AVAILABLE_SKILLS_PARAMS = parameters_func([])

AI_LOAD_SKILL_PARAMS = parameters_func([
    __SKILL_NAME_PROPERTY__,
    __MAX_SECTIONS_PROPERTY__,
    __SECTION_FILTER_PROPERTY__
])

AI_GET_SKILL_SUMMARY_PARAMS = parameters_func([__SKILL_NAME_PROPERTY__])

CLEAR_CACHE_PARAMS = parameters_func([__CLEAR_CACHE_PROPERTY__])
AI_RECOMMEND_SKILLS_PARAMS = parameters_func([__USER_QUERY_PROPERTY__, __TOP_N_PROPERTY__])

# Internal helper functions
def _get_skills_base_path(skills_dir=".agents/skills"):
    """Get absolute path to skills directory."""
    # Use current working directory as base for skills directory
    # This allows the skill module to work regardless of where AITools is installed
    return os.path.join(os.getcwd(), skills_dir)

def _parse_markdown_sections(content: str) -> List[Tuple[str, str]]:
    """
    Parse markdown content into sections.
    
    Args:
        content: Markdown content with frontmatter
        
    Returns:
        List of (title, content) tuples
    """
    # Remove YAML frontmatter if present
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    # Split by headers (starting with #)
    pattern = r'^(#+)\s+(.+)$'
    lines = content.split('\n')
    
    sections = []
    current_title = "Introduction"
    current_content = []
    
    for line in lines:
        # Check if line is a header
        match = re.match(pattern, line.strip())
        if match:
            # Save previous section if any content
            if current_content:
                sections.append((current_title, '\n'.join(current_content)))
                current_content = []
            
            # Start new section
            current_title = match.group(2).strip()
        else:
            current_content.append(line)
    
    # Add last section
    if current_content:
        sections.append((current_title, '\n'.join(current_content)))
    
    # If no sections found, return whole content as one section
    if not sections and content.strip():
        sections = [("Full Content", content)]
    
    return sections

# Public API functions
def scan_skills(skills_dir=".agents/skills") -> str:
    """
    Scan the skills directory and return a list of available skills.
    
    Args:
        skills_dir: Path to the skills directory (default: '.agents/skills')
        
    Returns:
        JSON string with list of skills or error message
    """
    try:
        # Check cache first
        cache_key = f"scan_{skills_dir}"
        if cache_key in _SKILL_CACHE:
            skills = _SKILL_CACHE[cache_key]
        else:
            skills = []
            skills_base = _get_skills_base_path(skills_dir)
            
            if not os.path.exists(skills_base):
                return f"Error: Skills directory not found: {skills_base}"
            
            # Walk through skills directory
            for root, dirs, files in os.walk(skills_base):
                # Look for SKILL.md files
                if "SKILL.md" in files:
                    skill_path = os.path.join(root, "SKILL.md")
                    skill_dir = os.path.relpath(root, skills_base)
                    
                    try:
                        with open(skill_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Parse YAML frontmatter
                        if content.startswith('---'):
                            parts = content.split('---', 2)
                            if len(parts) >= 3:
                                yaml_content = parts[1].strip()
                                frontmatter = yaml.safe_load(yaml_content)
                                skill_name = frontmatter.get('name', '')
                                skill_description = frontmatter.get('description', '')
                                
                                skills.append({
                                    'name': skill_name,
                                    'description': skill_description,
                                    'path': skill_path,
                                    'directory': skill_dir,
                                    'full_path': os.path.abspath(skill_path)
                                })
                    except Exception as e:
                        return f"Error reading skill {skill_path}: {e}"
            
            # Update cache
            _SKILL_CACHE[cache_key] = skills
        
        return str(skills)
        
    except Exception as e:
        return f"Error scanning skills: {e}"

def get_skills_list(skills_dir=".agents/skills") -> str:
    """
    Get formatted list of skills for AI consumption.
    
    Args:
        skills_dir: Path to the skills directory (default: '.agents/skills')
        
    Returns:
        Formatted string with skills list
    """
    try:
        skills_result = scan_skills(skills_dir)
        if skills_result.startswith("Error:"):
            return skills_result
        
        # Parse skills from string
        import ast
        skills = ast.literal_eval(skills_result)
        
        if not skills:
            return "No skills found. Skills directory may be empty or not configured correctly."
        
        formatted = "## Available Skills\n\n"
        for i, skill in enumerate(skills, 1):
            formatted += f"{i}. **{skill['name']}**\n"
            formatted += f"   - Description: {skill['description']}\n"
            formatted += f"   - Directory: {skill['directory']}\n\n"
        
        formatted += f"\nTotal: {len(skills)} skills available."
        return formatted
        
    except Exception as e:
        return f"Error getting skills list: {e}"

def get_skill_by_name(skill_name: str, skills_dir=".agents/skills") -> str:
    """
    Find a skill by name and return its information.
    
    Args:
        skill_name: Name of the skill to find
        skills_dir: Path to the skills directory (default: '.agents/skills')
        
    Returns:
        JSON string with skill info or error message
    """
    try:
        skills_result = scan_skills(skills_dir)
        if skills_result.startswith("Error:"):
            return skills_result
        
        import ast
        skills = ast.literal_eval(skills_result)
        
        for skill in skills:
            if skill['name'] == skill_name:
                return str(skill)
        
        return f"Error: Skill '{skill_name}' not found."
        
    except Exception as e:
        return f"Error finding skill: {e}"

def load_skill_by_name(skill_name: str, max_sections: Optional[int] = None,
                      section_filter: Optional[str] = None, 
                      skills_dir=".agents/skills") -> str:
    """
    Load skill content by skill name with caching.
    
    Args:
        skill_name: Name of the skill to load
        max_sections: Maximum number of sections to load (None for all)
        section_filter: String to filter sections by title
        skills_dir: Path to skills directory (default: '.agents/skills')
        
    Returns:
        Skill content as string, or error message if skill not found
    """
    try:
        # Check cache first
        cache_key = f"content_{skill_name}_{max_sections}_{section_filter}_{skills_dir}"
        if cache_key in _CONTENT_CACHE:
            return _CONTENT_CACHE[cache_key]
        
        # Find skill by name
        skill_result = get_skill_by_name(skill_name, skills_dir)
        if skill_result.startswith("Error:"):
            return skill_result
        
        import ast
        skill = ast.literal_eval(skill_result)
        skill_path = skill['full_path']
        
        if not os.path.exists(skill_path):
            return f"Error: Skill file not found: {skill_path}"
        
        # Load and parse content
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = _parse_markdown_sections(content)
        
        # Apply filtering if requested
        if section_filter:
            sections = [(title, section_content) for title, section_content in sections 
                       if section_filter.lower() in title.lower()]
        
        # Apply max sections limit
        if max_sections and max_sections > 0:
            sections = sections[:max_sections]
        
        # Combine selected sections
        result_parts = []
        for i, (title, section_content) in enumerate(sections):
            if i == 0 and title == "Introduction":
                result_parts.append(section_content.strip())
            else:
                result_parts.append(f"## {title}\n{section_content.strip()}")
        
        result = '\n\n'.join(result_parts)
        
        # Update cache
        _CONTENT_CACHE[cache_key] = result
        return result
        
    except Exception as e:
        return f"Error loading skill content: {e}"

def get_skill_summary(skill_name: str, max_length: int = 500, 
                     skills_dir=".agents/skills") -> str:
    """
    Get a summary of a skill (first section or truncated content).
    
    Args:
        skill_name: Name of the skill
        max_length: Maximum length of summary in characters
        skills_dir: Path to skills directory (default: '.agents/skills')
        
    Returns:
        Skill summary
    """
    try:
        # Load only first section for summary
        content = load_skill_by_name(skill_name, max_sections=1, skills_dir=skills_dir)
        
        if content.startswith("Error:"):
            return content
        
        # Truncate if too long
        if len(content) > max_length:
            content = content[:max_length].rsplit(' ', 1)[0] + "..."
        
        return content
        
    except Exception as e:
        return f"Error getting skill summary: {e}"

def ai_get_available_skills() -> str:
    """
    Interface for AI to get available skills.
    
    Returns:
        Formatted list of skills
    """
    return get_skills_list()

def ai_load_skill(skill_name: str, max_sections: Optional[int] = None, 
                 section_filter: Optional[str] = None) -> str:
    """
    Interface for AI to load a specific skill.
    
    Args:
        skill_name: Name of skill to load
        max_sections: Number of sections to load (None for all)
        section_filter: Filter sections containing this string
        
    Returns:
        Skill content
    """
    return load_skill_by_name(skill_name, max_sections=max_sections, 
                             section_filter=section_filter)

def ai_get_skill_summary(skill_name: str) -> str:
    """
    Interface for AI to get a skill summary.
    
    Args:
        skill_name: Name of skill
        
    Returns:
        Skill summary
    """
    return get_skill_summary(skill_name)

def clear_skill_cache(force: bool = False) -> str:
    """
    Clear all skill caches.
    
    Args:
        force: Force cache clearing (required for safety)
        
    Returns:
        Status message
    """
    if not force:
        return "Error: Force parameter must be True to clear cache. Use force=True."
    
    global _SKILL_CACHE, _CONTENT_CACHE
    _SKILL_CACHE.clear()
    _CONTENT_CACHE.clear()
    return "Skill cache cleared successfully."
def ai_recommend_skills(user_query: str, top_n: int = 3) -> str:
    """
    Interface for AI to get skill recommendations based on user query.

    Args:
        user_query: User's request or question
        top_n: Number of top recommendations to return (default: 3)

    Returns:
        Formatted recommendations string
    """
    skills_result = scan_skills()
    if not skills_result:
        return "No skills available."
    
    # Handle error response
    if skills_result.startswith("Error:"):
        return f"Cannot recommend skills: {skills_result}"
    
    # Parse skills from string representation
    import ast
    try:
        skills = ast.literal_eval(skills_result)
    except Exception as e:
        return f"Error parsing skills data: {e}"

    # Tokenize user query
    import re
    words = re.findall(r'\b\w+\b', user_query.lower())
    
    recommendations = []
    for skill in skills:
        score = 0
        reasons = []
        
        # Check skill name
        skill_name_lower = skill['name'].lower()
        for word in words:
            if word in skill_name_lower:
                score += 3
                reasons.append(f"Keyword '{word}' matches skill name")
        
        # Check description
        desc_lower = skill['description'].lower()
        for word in words:
            if word in desc_lower:
                score += 2
                reasons.append(f"Keyword '{word}' matches description")
        
        if score > 0:
            recommendations.append({
                'name': skill['name'],
                'description': skill['description'],
                'score': score,
                'reason': '; '.join(reasons[:3])  # Limit reasons
            })
    
    # If no matches, return all skills with zero score
    if not recommendations:
        for skill in skills:
            recommendations.append({
                'name': skill['name'],
                'description': skill['description'],
                'score': 0,
                'reason': 'No keyword matches found'
            })
    
    # Sort by score descending
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    # Format output
    formatted = "## Skill Recommendations\n\n"
    for i, rec in enumerate(recommendations[:top_n], 1):
        formatted += f"{i}. **{rec['name']}** (score: {rec['score']})\n"
        formatted += f"   - Description: {rec['description']}\n"
        formatted += f"   - Reason: {rec['reason']}\n\n"
    
    formatted += f"\nBased on your query: \"{user_query}\""
    return formatted
# AI Tool definitions
tools = [
    function_ai(
        name="scan_skills",
        parameters=SCAN_SKILLS_PARAMS,
        description="Scan the skills directory and return a list of available skills."
    ),
    function_ai(
        name="get_skills_list",
        parameters=GET_SKILLS_LIST_PARAMS,
        description="Get formatted list of skills for AI consumption."
    ),
    function_ai(
        name="get_skill_by_name",
        parameters=GET_SKILL_BY_NAME_PARAMS,
        description="Find a skill by name and return its information."
    ),
    function_ai(
        name="load_skill_by_name",
        parameters=LOAD_SKILL_CONTENT_PARAMS,
        description="Load skill content by skill name with caching and optional section filtering."
    ),
    function_ai(
        name="get_skill_summary",
        parameters=GET_SKILL_SUMMARY_PARAMS,
        description="Get a summary of a skill (first section or truncated content)."
    ),
    function_ai(
        name="ai_get_available_skills",
        parameters=AI_GET_AVAILABLE_SKILLS_PARAMS,
        description="Interface for AI to get available skills."
    ),
    function_ai(
        name="ai_load_skill",
        parameters=AI_LOAD_SKILL_PARAMS,
        description="Interface for AI to load a specific skill with optional section filtering."
    ),
    function_ai(
        name="ai_get_skill_summary",
        parameters=AI_GET_SKILL_SUMMARY_PARAMS,
        description="Interface for AI to get a skill summary."
    ),
    function_ai(
        name="ai_recommend_skills",
        parameters=AI_RECOMMEND_SKILLS_PARAMS,
        description="Interface for AI to get skill recommendations based on user query."
    ),
    function_ai(
        name="clear_skill_cache",
        parameters=CLEAR_CACHE_PARAMS,
        description="Clear all skill caches. Requires force=True for safety."
    ),
]

# Tool call mapping
TOOL_CALL_MAP = {
    "scan_skills": scan_skills,
    "get_skills_list": get_skills_list,
    "get_skill_by_name": get_skill_by_name,
    "load_skill_by_name": load_skill_by_name,
    "get_skill_summary": get_skill_summary,
    "ai_get_available_skills": ai_get_available_skills,
    "ai_load_skill": ai_load_skill,
    "ai_get_skill_summary": ai_get_skill_summary,
    "ai_recommend_skills": ai_recommend_skills,
    "clear_skill_cache": clear_skill_cache,
}