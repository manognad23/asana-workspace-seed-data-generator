"""
Project generation with realistic project structures.
"""
import uuid
from datetime import datetime
import random
from typing import List, Dict

from src.scrapers.templates import (
    get_project_name,
    get_project_type_distribution,
    get_section_names
)
from src.utils.dates import generate_created_at
from src.utils.distributions import get_project_tasks_count


PROJECT_COLORS = [
    "blue", "green", "orange", "red", "purple", "pink",
    "yellow", "teal", "brown", "gray"
]


def generate_project(
    team_id: str,
    project_type: str,
    name: str,
    start_date: datetime,
    end_date: datetime,
    llm_generator=None
) -> Dict:
    """
    Generate a realistic project.
    
    Methodology:
    - Names: From templates (Asana, GitHub patterns)
    - Descriptions: LLM-generated based on project type
    - Types: Sprint, bug tracking, marketing, launch, ongoing
    - Colors: Random but consistent
    - Archived: ~10% of older projects
    """
    created_at = generate_created_at(start_date, end_date)
    
    # Generate description (70% have descriptions)
    description = None
    if random.random() < 0.7 and llm_generator:
        try:
            description = llm_generator.generate_project_description(name, project_type)
        except:
            description = f"Project focused on {project_type.replace('_', ' ')} initiatives."
    
    # Archive status: older projects more likely archived
    days_old = (end_date - created_at).days
    archived = False
    if days_old > 90 and random.random() < 0.3:
        archived = True
    
    return {
        "project_id": str(uuid.uuid4()),
        "team_id": team_id,
        "name": name,
        "description": description,
        "project_type": project_type,
        "created_at": created_at,
        "archived": archived,
        "color": random.choice(PROJECT_COLORS)
    }


def generate_projects(
    teams: List[Dict],
    projects_per_team: int,
    start_date: datetime,
    end_date: datetime,
    llm_generator=None
) -> List[Dict]:
    """Generate projects for teams."""
    projects = []
    
    for team in teams:
        # Number of projects per team varies (1 to projects_per_team)
        # Create dynamic weights based on projects_per_team
        max_projects = projects_per_team
        if max_projects == 1:
            weights = [100]
        elif max_projects == 2:
            weights = [30, 70]  # Prefer 2 projects
        elif max_projects == 3:
            weights = [15, 25, 60]  # Prefer 2-3 projects
        elif max_projects == 4:
            weights = [10, 20, 40, 30]  # Prefer 3 projects
        else:  # 5 or more
            weights = [15, 25, 30, 20, 10]  # Weighted toward 2-3 projects
            # Extend weights if projects_per_team > 5
            if max_projects > 5:
                additional = max_projects - 5
                weights.extend([5] * additional)
        
        # Ensure weights match population size
        weights = weights[:max_projects]
        if len(weights) < max_projects:
            weights.extend([5] * (max_projects - len(weights)))
        
        num_projects = random.choices(
            range(1, max_projects + 1),
            weights=weights,
            k=1
        )[0]
        
        for _ in range(num_projects):
            project_type = get_project_type_distribution()
            name = get_project_name(project_type)
            
            project = generate_project(
                team["team_id"],
                project_type,
                name,
                start_date,
                end_date,
                llm_generator
            )
            projects.append(project)
    
    return projects


def generate_sections(project: Dict) -> List[Dict]:
    """
    Generate sections for a project.
    
    Sections vary by project type (Kanban/Scrum patterns).
    """
    section_names = get_section_names(project["project_type"])
    sections = []
    
    for position, name in enumerate(section_names):
        sections.append({
            "section_id": str(uuid.uuid4()),
            "project_id": project["project_id"],
            "name": name,
            "position": position,
            "created_at": project["created_at"]
        })
    
    return sections
