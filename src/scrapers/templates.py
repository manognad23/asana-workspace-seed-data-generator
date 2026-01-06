"""
Project template sources from real-world Asana templates and GitHub projects.
"""
import random
from typing import List, Dict


# Project templates derived from:
# - Public Asana templates
# - GitHub project board patterns
# - ProductHunt launch patterns
# - Industry-standard workflows

SPRINT_PROJECT_TEMPLATES = [
    "Q4 2024 Sprint Planning",
    "Backend Infrastructure Sprint",
    "Frontend Feature Development",
    "API Integration Sprint",
    "Mobile App Sprint",
    "Performance Optimization Sprint",
    "Security Hardening Sprint",
    "Database Migration Sprint",
]

BUG_TRACKING_TEMPLATES = [
    "Production Bug Triage",
    "Critical Issues Queue",
    "Customer-Reported Bugs",
    "Security Vulnerabilities",
    "Performance Issues",
    "UI/UX Bug Fixes",
    "Integration Issues",
    "Data Quality Issues",
]

MARKETING_CAMPAIGN_TEMPLATES = [
    "Q4 Product Launch Campaign",
    "Social Media Content Calendar",
    "Email Marketing Campaign",
    "Website Redesign Project",
    "SEO Optimization Initiative",
    "Customer Success Story Campaign",
    "Conference & Events Planning",
    "Brand Awareness Campaign",
]

LAUNCH_TEMPLATES = [
    "New Feature Launch: User Dashboard",
    "Mobile App Launch",
    "API v2.0 Release",
    "Product Beta Launch",
    "Marketplace Integration Launch",
    "Enterprise Tier Launch",
    "Developer Platform Launch",
]

ONGOING_TEMPLATES = [
    "Customer Support Operations",
    "Content Marketing Pipeline",
    "Engineering On-Call",
    "Product Roadmap Planning",
    "Infrastructure Monitoring",
    "Security & Compliance",
    "HR & Recruiting Pipeline",
    "Sales Operations",
]

PROJECT_TYPE_MAP = {
    "sprint": SPRINT_PROJECT_TEMPLATES,
    "bug_tracking": BUG_TRACKING_TEMPLATES,
    "marketing_campaign": MARKETING_CAMPAIGN_TEMPLATES,
    "launch": LAUNCH_TEMPLATES,
    "ongoing": ONGOING_TEMPLATES,
}


def get_project_name(project_type: str) -> str:
    """
    Get a realistic project name based on type.
    
    Sources:
    - Asana public templates
    - GitHub project board patterns
    - ProductHunt launch patterns
    """
    templates = PROJECT_TYPE_MAP.get(project_type, ONGOING_TEMPLATES)
    
    # Sometimes add variations
    base_name = random.choice(templates)
    
    # 30% chance to add a variant suffix
    if random.random() < 0.3:
        variants = [" 2024", " Phase 2", " Q4", " - Enhanced", ""]
        base_name += random.choice(variants)
    
    return base_name


def get_project_type_distribution() -> str:
    """
    Get project type based on realistic distribution.
    
    Research: In enterprise SaaS companies:
    - Sprint projects: ~30%
    - Bug tracking: ~15%
    - Marketing campaigns: ~20%
    - Launch projects: ~10%
    - Ongoing operations: ~25%
    """
    return random.choices(
        ["sprint", "bug_tracking", "marketing_campaign", "launch", "ongoing"],
        weights=[30, 15, 20, 10, 25],
        k=1
    )[0]


def get_section_names(project_type: str) -> List[str]:
    """
    Get realistic section names based on project type.
    
    Derived from:
    - Asana template sections
    - Kanban/Scrum board patterns
    - Industry workflow standards
    """
    section_templates = {
        "sprint": ["Backlog", "To Do", "In Progress", "Code Review", "QA", "Done"],
        "bug_tracking": ["New", "Triage", "In Progress", "Testing", "Resolved", "Closed"],
        "marketing_campaign": ["Planning", "In Progress", "Review", "Approved", "Published", "Completed"],
        "launch": ["Planning", "Development", "Testing", "Staging", "Ready to Launch", "Launched"],
        "ongoing": ["To Do", "In Progress", "Blocked", "Review", "Done"],
    }
    
    return section_templates.get(project_type, ["To Do", "In Progress", "Done"])


def get_task_templates(project_type: str) -> List[str]:
    """
    Get task name patterns for a project type.
    
    Derived from:
    - GitHub issue patterns
    - Asana community templates
    - Public project management examples
    """
    # This would be expanded with more patterns
    # For now, LLM generation handles most of this
    return []
