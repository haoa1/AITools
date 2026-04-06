#!/usr/bin/env python3
"""
SkillSearchTool implementation for AITools (Claude Code compatible version).
Provides skill search and discovery functionality to complement SkillTool.
Based on Claude Code pattern with simplified implementation.
"""

import os
import json
import re
import yaml
from typing import Dict, List, Optional, Tuple, Any
from base import function_ai, parameters_func, property_param

# Import existing skill functions
from skill.skill import (
    scan_skills,
    get_skills_list,
    get_skill_by_name,
    load_skill_by_name,
    ai_recommend_skills
)

# ============================================================================
# PROPERTY DEFINITIONS
# ============================================================================

__SEARCH_QUERY_PROPERTY__ = property_param(
    name="query",
    description="Search query string to match against skill names, descriptions, and content.",
    t="string",
    required=True,
)

__SEARCH_CATEGORY_PROPERTY__ = property_param(
    name="category",
    description="Optional skill category filter (e.g., 'file', 'git', 'web', 'analysis').",
    t="string",
    required=False,
)

__SEARCH_LIMIT_PROPERTY__ = property_param(
    name="limit",
    description="Maximum number of results to return (default: 10).",
    t="number",
    required=False,
)

__SEARCH_EXACT_MATCH_PROPERTY__ = property_param(
    name="exact_match",
    description="Require exact match of search terms (default: false, uses fuzzy matching).",
    t="boolean",
    required=False,
)

__SEARCH_INCLUDE_CONTENT_PROPERTY__ = property_param(
    name="include_content",
    description="Include skill content snippets in results (default: false).",
    t="boolean",
    required=False,
)

__SEARCH_MAX_CONTENT_LENGTH_PROPERTY__ = property_param(
    name="max_content_length",
    description="Maximum length of content snippets to include (default: 200 characters).",
    t="number",
    required=False,
)

# ============================================================================
# TOOL FUNCTION DEFINITION
# ============================================================================

__SKILL_SEARCH_FUNCTION__ = function_ai(
    name="skill_search",
    description="Search and discover skills by query, category, or other criteria. Complement to SkillTool for skill discovery.",
    parameters=parameters_func([
        __SEARCH_QUERY_PROPERTY__,
        __SEARCH_CATEGORY_PROPERTY__,
        __SEARCH_LIMIT_PROPERTY__,
        __SEARCH_EXACT_MATCH_PROPERTY__,
        __SEARCH_INCLUDE_CONTENT_PROPERTY__,
        __SEARCH_MAX_CONTENT_LENGTH_PROPERTY__,
    ]),
)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _parse_skills_result(skills_result: str) -> List[Dict]:
    """
    Parse skills result string into list of skill dictionaries.
    """
    if not skills_result or skills_result.startswith("Error:"):
        return []
    
    try:
        import ast
        skills = ast.literal_eval(skills_result)
        if isinstance(skills, list):
            return skills
        else:
            return []
    except:
        # Try to parse as JSON if ast fails
        try:
            skills = json.loads(skills_result)
            if isinstance(skills, list):
                return skills
            else:
                return []
        except:
            return []

def _extract_skill_categories(skill_name: str, skill_content: str) -> List[str]:
    """
    Extract categories from skill content and name.
    """
    categories = []
    
    # Common categories based on skill name patterns
    name_lower = skill_name.lower()
    
    # File operations
    file_keywords = ['file', 'read', 'write', 'edit', 'copy', 'move', 'delete', 'search']
    if any(keyword in name_lower for keyword in file_keywords):
        categories.append('file')
    
    # Git operations
    if 'git' in name_lower or 'commit' in name_lower or 'branch' in name_lower:
        categories.append('git')
    
    # Web/network operations
    web_keywords = ['web', 'http', 'fetch', 'download', 'network', 'url']
    if any(keyword in name_lower for keyword in web_keywords):
        categories.append('web')
    
    # Analysis operations
    analysis_keywords = ['analyze', 'stats', 'statistics', 'report', 'summary', 'search']
    if any(keyword in name_lower for keyword in analysis_keywords):
        categories.append('analysis')
    
    # System operations
    system_keywords = ['bash', 'shell', 'powershell', 'command', 'exec', 'run']
    if any(keyword in name_lower for keyword in system_keywords):
        categories.append('system')
    
    # User interaction
    ui_keywords = ['ask', 'question', 'confirm', 'user', 'interaction']
    if any(keyword in name_lower for keyword in ui_keywords):
        categories.append('ui')
    
    # Try to extract from skill content frontmatter
    try:
        # Look for YAML frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?\n)---\s*\n', skill_content, re.DOTALL)
        if frontmatter_match:
            frontmatter_text = frontmatter_match.group(1)
            frontmatter = yaml.safe_load(frontmatter_text)
            if frontmatter:
                # Check for categories in frontmatter
                if 'categories' in frontmatter:
                    cats = frontmatter['categories']
                    if isinstance(cats, str):
                        categories.append(cats)
                    elif isinstance(cats, list):
                        categories.extend(cats)
                if 'category' in frontmatter:
                    cat = frontmatter['category']
                    if isinstance(cat, str):
                        categories.append(cat)
    except:
        pass
    
    # Remove duplicates and empty strings
    categories = [cat for cat in categories if cat and isinstance(cat, str)]
    categories = list(set(categories))
    
    return categories

def _calculate_search_score(
    skill: Dict,
    query: str,
    exact_match: bool = False,
    target_category: Optional[str] = None
) -> Tuple[float, List[str]]:
    """
    Calculate search score for a skill based on query and category.
    Returns (score, reasons)
    """
    score = 0.0
    reasons = []
    
    skill_name = skill.get('name', '').lower()
    skill_description = skill.get('description', '').lower()
    
    # Tokenize query
    query_terms = re.findall(r'\b\w+\b', query.lower())
    
    # Category match (if specified)
    if target_category:
        skill_categories = skill.get('categories', [])
        if isinstance(skill_categories, str):
            skill_categories = [skill_categories]
        
        target_category_lower = target_category.lower()
        for cat in skill_categories:
            if isinstance(cat, str) and target_category_lower in cat.lower():
                score += 5.0
                reasons.append(f"Category matches: '{cat}'")
                break
    
    # Name matches
    for term in query_terms:
        if exact_match:
            if term == skill_name:
                score += 10.0
                reasons.append(f"Exact name match: '{term}'")
            elif term in skill_name:
                score += 8.0
                reasons.append(f"Name contains: '{term}'")
        else:
            # Fuzzy matching
            if term in skill_name:
                score += 8.0
                reasons.append(f"Name contains: '{term}'")
            elif re.search(term, skill_name):
                score += 6.0
                reasons.append(f"Name fuzzy match: '{term}'")
    
    # Description matches
    for term in query_terms:
        if exact_match:
            if term == skill_description:
                score += 5.0
                reasons.append(f"Exact description match: '{term}'")
            elif term in skill_description:
                score += 3.0
                reasons.append(f"Description contains: '{term}'")
        else:
            if term in skill_description:
                score += 3.0
                reasons.append(f"Description contains: '{term}'")
            elif re.search(term, skill_description):
                score += 2.0
                reasons.append(f"Description fuzzy match: '{term}'")
    
    # Priority for skills with good descriptions
    if len(skill_description) > 20:
        score += 0.5
        reasons.append("Has detailed description")
    
    return score, reasons[:5]  # Limit to top 5 reasons

def _get_content_snippet(
    skill_name: str,
    max_length: int = 200
) -> Optional[str]:
    """
    Get a content snippet from a skill.
    """
    try:
        content = load_skill_by_name(skill_name=skill_name, max_sections=1)
        if content and isinstance(content, str):
            # Remove frontmatter if present
            content_no_fm = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
            # Get first non-empty lines
            lines = content_no_fm.strip().split('\n')
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    snippet = line.strip()
                    if len(snippet) > max_length:
                        snippet = snippet[:max_length] + '...'
                    return snippet
    except:
        pass
    
    return None

# ============================================================================
# MAIN TOOL FUNCTION
# ============================================================================

def skill_search(
    query: str,
    category: Optional[str] = None,
    limit: int = 10,
    exact_match: bool = False,
    include_content: bool = False,
    max_content_length: int = 200
) -> str:
    """
    Search and discover skills based on query and criteria.
    
    Args:
        query: Search query string to match against skills
        category: Optional category filter (e.g., 'file', 'git', 'web')
        limit: Maximum number of results to return (default: 10)
        exact_match: Require exact term matching (default: false)
        include_content: Include content snippets in results (default: false)
        max_content_length: Maximum length of content snippets (default: 200)
    
    Returns:
        JSON string with search results matching Claude Code tool format.
    """
    try:
        # Validate inputs
        if not query or not isinstance(query, str):
            return json.dumps({
                "error": "Search query must be a non-empty string",
                "success": False
            }, indent=2)
        
        if limit <= 0:
            return json.dumps({
                "error": f"Limit must be positive, got: {limit}",
                "success": False
            }, indent=2)
        
        # Get all available skills
        skills_result = get_skills_list()
        skills = _parse_skills_result(skills_result)
        
        if not skills:
            return json.dumps({
                "success": True,
                "operation": "skill_search",
                "query": query,
                "category": category,
                "results_count": 0,
                "results": [],
                "message": "No skills available for search",
                "_metadata": {
                    "search_mode": "exact" if exact_match else "fuzzy",
                    "include_content": include_content
                }
            }, indent=2)
        
        # Enrich skills with categories and calculate scores
        enriched_skills = []
        
        for skill in skills:
            # Extract categories
            skill_categories = []
            if 'content' in skill:
                skill_categories = _extract_skill_categories(
                    skill['name'], 
                    skill['content']
                )
            elif 'description' in skill:
                # Try to get content for category extraction
                try:
                    content = load_skill_by_name(skill_name=skill['name'], max_sections=1)
                    skill_categories = _extract_skill_categories(skill['name'], content)
                except:
                    pass
            
            # Add categories to skill dict
            skill_with_cats = skill.copy()
            if skill_categories:
                skill_with_cats['categories'] = skill_categories
            
            # Calculate search score
            score, reasons = _calculate_search_score(
                skill_with_cats,
                query,
                exact_match,
                category
            )
            
            skill_with_cats['_search_score'] = score
            skill_with_cats['_search_reasons'] = reasons
            
            # Add content snippet if requested
            if include_content and score > 0:
                snippet = _get_content_snippet(skill['name'], max_content_length)
                if snippet:
                    skill_with_cats['content_snippet'] = snippet
            
            enriched_skills.append(skill_with_cats)
        
        # Filter skills with positive score or keep all if no matches
        filtered_skills = [s for s in enriched_skills if s['_search_score'] > 0]
        if not filtered_skills and not exact_match:
            # If no matches in fuzzy mode, return all skills with zero score
            filtered_skills = enriched_skills
        
        # Sort by score descending
        filtered_skills.sort(key=lambda x: x['_search_score'], reverse=True)
        
        # Apply limit
        limited_skills = filtered_skills[:limit]
        
        # Prepare results in Claude Code compatible format
        results = []
        for skill in limited_skills:
            result_entry = {
                "name": skill.get('name'),
                "description": skill.get('description', 'No description available'),
                "score": round(skill['_search_score'], 2),
                "reasons": skill.get('_search_reasons', []),
            }
            
            # Add optional fields
            if skill.get('categories'):
                result_entry["categories"] = skill.get('categories')
            
            if skill.get('content_snippet'):
                result_entry["content_snippet"] = skill.get('content_snippet')
            
            results.append(result_entry)
        
        # Build final response
        response = {
            "success": True,
            "operation": "skill_search",
            "query": query,
            "category": category,
            "results_count": len(results),
            "total_skills": len(skills),
            "results": results,
            "_metadata": {
                "search_mode": "exact" if exact_match else "fuzzy",
                "include_content": include_content,
                "max_content_length": max_content_length if include_content else None,
                "limit_applied": limit,
                "scoring_explanation": "Scores: name match (8-10), description match (2-5), category match (5)"
            }
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "operation": "skill_search",
            "error": f"Skill search failed: {str(e)}",
            "query": query,
            "category": category
        }, indent=2)

# ============================================================================
# MODULE EXPORTS
# ============================================================================

# Tool list for module export
tools = [__SKILL_SEARCH_FUNCTION__]

# Tool call map
TOOL_CALL_MAP = {
    "skill_search": skill_search
}

__all__ = ['tools', 'TOOL_CALL_MAP', 'skill_search', '__SKILL_SEARCH_FUNCTION__']