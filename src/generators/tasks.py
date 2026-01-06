"""
Task generation with realistic task structures and relationships.
"""
import uuid
from datetime import datetime, date
import random
from typing import List, Dict, Optional

from src.utils.dates import (
    generate_created_at,
    generate_due_date,
    generate_completed_at
)
from src.utils.distributions import (
    get_project_tasks_count,
    get_completion_rate,
    get_subtask_count
)
from src.utils.llm import LLMGenerator


def generate_task(
    project: Dict,
    section_id: Optional[str],
    parent_task_id: Optional[str],
    assignee_id: Optional[str],
    team_members: List[str],
    start_date: datetime,
    end_date: datetime,
    llm_generator: Optional[LLMGenerator] = None
) -> Dict:
    """
    Generate a realistic task.
    
    Methodology:
    - Names: LLM-generated with project-type-specific patterns
    - Descriptions: LLM-generated with varying formats (20% empty, 50% brief, 30% detailed)
    - Assignees: Based on team membership, 15% unassigned
    - Due dates: Realistic distribution with project-type patterns
    - Completion: Varies by project type
    - Subtasks: 60% have 0, 25% have 1-2, etc.
    """
    created_at = generate_created_at(start_date, end_date)
    
    # Generate task name with proper fallback
    task_name = f"{project['project_type'].replace('_', ' ').title()} Task"  # Default fallback
    if llm_generator:
        try:
            task_name = llm_generator.generate_task_name(
                project["project_type"],
                component=None,
                context=project.get("name")
            )
        except Exception as e:
            # Fallback to pattern-based generation (already set above)
            pass
    
    # Generate description
    description = None
    if llm_generator:
        include_bullets = random.random() < 0.3  # 30% have bullet points
        try:
            description = llm_generator.generate_task_description(
                task_name,
                project.get("name", ""),
                include_bullets
            )
        except:
            description = None
    
    # Assignee: 15% unassigned (per Asana benchmarks)
    assignee = assignee_id
    if not assignee and random.random() > 0.15:
        if team_members:
            assignee = random.choice(team_members)
    
    # Due date generation
    due_date = generate_due_date(created_at, project["project_type"])
    
    # Completion status and timestamp
    completion_rate = get_completion_rate(project["project_type"])
    completed = random.random() < completion_rate
    
    completed_at = None
    if completed:
        completed_at = generate_completed_at(
            created_at,
            due_date,
            completion_rate
        )
        # Ensure completed_at is not in the future (check if not None)
        if completed_at and completed_at > end_date:
            completed_at = end_date
    
    # Subtask count (will be set later when subtasks are generated)
    num_subtasks = 0
    if parent_task_id is None:  # Only count for parent tasks
        num_subtasks = get_subtask_count()
    
    # Likes count: most tasks have 0-2 likes, some have more
    likes_count = random.choices(
        range(6),
        weights=[60, 25, 10, 3, 1, 1],
        k=1
    )[0]
    
    return {
        "task_id": str(uuid.uuid4()),
        "project_id": project["project_id"],
        "section_id": section_id,
        "parent_task_id": parent_task_id,
        "assignee_id": assignee,
        "name": task_name,
        "description": description,
        "due_date": due_date.isoformat() if due_date else None,
        "start_date": None,  # Optional field, not always used
        "created_at": created_at,
        "completed": completed,
        "completed_at": completed_at,
        "likes_count": likes_count,
        "num_subtasks": 0,  # Will be updated when subtasks are created
        "num_subtasks_completed": 0  # Will be updated
    }


def generate_tasks_for_project(
    project: Dict,
    sections: List[Dict],
    team_members: List[str],
    start_date: datetime,
    end_date: datetime,
    llm_generator: Optional[LLMGenerator] = None
) -> List[Dict]:
    """
    Generate tasks for a project with realistic distribution.
    
    Tasks are distributed across sections based on project type.
    """
    num_tasks = get_project_tasks_count(project["project_type"])
    tasks = []
    
    # Section distribution (tasks move through sections)
    # Most tasks end up in later sections (progress over time)
    section_weights = {
        "sprint": [5, 15, 30, 20, 15, 15],  # Backlog, To Do, In Progress, Review, QA, Done
        "bug_tracking": [10, 10, 20, 15, 25, 20],  # New, Triage, In Progress, Testing, Resolved, Closed
        "marketing_campaign": [10, 25, 20, 15, 15, 15],
        "launch": [5, 20, 25, 20, 15, 15],
        "ongoing": [20, 30, 15, 15, 20]
    }
    
    weights = section_weights.get(project["project_type"], [30, 40, 30])
    # Pad or trim weights to match section count
    if len(weights) < len(sections):
        weights = weights + [weights[-1]] * (len(sections) - len(weights))
    elif len(weights) > len(sections):
        weights = weights[:len(sections)]
    
    # Generate parent tasks first
    parent_tasks = []
    for i in range(num_tasks):
        section_idx = random.choices(range(len(sections)), weights=weights, k=1)[0]
        section = sections[section_idx] if sections else None
        
        task = generate_task(
            project,
            section["section_id"] if section else None,
            None,  # Parent task
            None,  # Assignee will be set per task
            team_members,
            start_date,
            end_date,
            llm_generator
        )
        
        parent_tasks.append(task)
        tasks.append(task)
    
    # Generate subtasks for parent tasks that should have them
    for parent_task in parent_tasks:
        num_subtasks = get_subtask_count()
        if num_subtasks > 0:
            parent_task["num_subtasks"] = num_subtasks
            
            # Subtasks are usually in same or adjacent sections
            parent_section_idx = None
            if parent_task["section_id"]:
                parent_section_idx = next(
                    (i for i, s in enumerate(sections) if s["section_id"] == parent_task["section_id"]),
                    None
                )
            
            completed_subtasks = 0
            for _ in range(num_subtasks):
                # Subtask section: same or next section
                if parent_section_idx is not None:
                    subtask_section_idx = min(
                        parent_section_idx + random.randint(0, 1),
                        len(sections) - 1
                    )
                    subtask_section = sections[subtask_section_idx]
                else:
                    subtask_section = None
                
                subtask = generate_task(
                    project,
                    subtask_section["section_id"] if subtask_section else None,
                    parent_task["task_id"],
                    parent_task["assignee_id"],  # Often same assignee
                    team_members,
                    start_date,
                    end_date,
                    llm_generator
                )
                
                if subtask["completed"]:
                    completed_subtasks += 1
                
                tasks.append(subtask)
            
            parent_task["num_subtasks_completed"] = completed_subtasks
    
    return tasks
