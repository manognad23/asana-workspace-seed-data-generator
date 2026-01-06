"""
Generate tags, custom fields, and other metadata.
"""
import uuid
from datetime import datetime
import random
from typing import List, Dict


# Common tag patterns from real Asana workspaces
TAG_PATTERNS = [
    "urgent", "blocked", "needs-review", "high-priority", "low-priority",
    "bug", "feature", "enhancement", "documentation", "technical-debt",
    "customer-request", "internal", "external", "launch-blocker",
    "security", "performance", "accessibility", "mobile", "web",
    "backend", "frontend", "api", "database", "infrastructure",
    "q1", "q2", "q3", "q4", "2024", "2025",
    "design", "engineering", "product", "marketing", "sales"
]

TAG_COLORS = [
    "red", "orange", "yellow", "green", "blue",
    "purple", "pink", "brown", "gray", "black"
]


def generate_tags(organization_id: str, count: int, created_at: datetime) -> List[Dict]:
    """
    Generate workspace-level tags.
    
    Methodology:
    - Names: Common patterns from real Asana workspaces
    - Colors: Random assignment
    - Usage: Tags are applied to tasks based on relevance
    """
    tags = []
    selected_patterns = random.sample(TAG_PATTERNS, min(count, len(TAG_PATTERNS)))
    
    for pattern in selected_patterns:
        tags.append({
            "tag_id": str(uuid.uuid4()),
            "organization_id": organization_id,
            "name": pattern,
            "color": random.choice(TAG_COLORS),
            "created_at": created_at
        })
    
    return tags


def generate_custom_field_definitions(project: Dict) -> List[Dict]:
    """
    Generate custom field definitions for a project.
    
    Methodology:
    - Custom fields vary by project type
    - Not all projects have custom fields (~60% do)
    - Field types: text, number, enum, date, boolean
    """
    if random.random() > 0.60:  # 40% have no custom fields
        return []
    
    fields = []
    
    # Field definitions by project type
    field_templates = {
        "sprint": [
            {"name": "Priority", "type": "enum", "options": ["P0", "P1", "P2", "P3"]},
            {"name": "Story Points", "type": "number"},
            {"name": "Epic", "type": "text"},
        ],
        "bug_tracking": [
            {"name": "Severity", "type": "enum", "options": ["Critical", "High", "Medium", "Low"]},
            {"name": "Environment", "type": "enum", "options": ["Production", "Staging", "Development"]},
            {"name": "Reporter", "type": "text"},
        ],
        "marketing_campaign": [
            {"name": "Channel", "type": "enum", "options": ["Email", "Social", "Web", "Paid Ads"]},
            {"name": "Target Audience", "type": "text"},
            {"name": "Budget", "type": "number"},
        ],
        "launch": [
            {"name": "Launch Blocking", "type": "boolean"},
            {"name": "Launch Readiness", "type": "enum", "options": ["Not Ready", "Ready", "Blocked"]},
        ],
        "ongoing": [
            {"name": "Status", "type": "enum", "options": ["Active", "On Hold", "Completed"]},
        ]
    }
    
    templates = field_templates.get(project["project_type"], [])
    
    # Select 1-3 fields
    num_fields = random.randint(1, min(3, len(templates)))
    selected_templates = random.sample(templates, num_fields)
    
    for template in selected_templates:
        field = {
            "field_id": str(uuid.uuid4()),
            "project_id": project["project_id"],
            "name": template["name"],
            "field_type": template["type"],
            "enum_options": None,
            "created_at": project["created_at"]
        }
        
        if template["type"] == "enum":
            field["enum_options"] = ",".join(template["options"])
        
        fields.append(field)
    
    return fields


def generate_custom_field_value(task: Dict, field: Dict) -> Dict:
    """
    Generate a value for a custom field on a task.
    Not all tasks have values for all fields (~80% coverage).
    """
    if random.random() > 0.80:
        return None
    
    value = {
        "value_id": str(uuid.uuid4()),
        "task_id": task["task_id"],
        "field_id": field["field_id"],
        "value_text": None,
        "value_number": None,
        "value_date": None,
        "value_boolean": None
    }
    
    if field["field_type"] == "enum":
        options = field["enum_options"].split(",")
        value["value_text"] = random.choice(options)
    elif field["field_type"] == "text":
        value["value_text"] = f"Sample {field['name']}"
    elif field["field_type"] == "number":
        value["value_number"] = random.randint(1, 20)
    elif field["field_type"] == "date":
        # Date in future or past relative to task
        if task.get("due_date"):
            value["value_date"] = task["due_date"]
        else:
            from datetime import timedelta
            value["value_date"] = (task["created_at"] + timedelta(days=random.randint(-30, 60))).date().isoformat()
    elif field["field_type"] == "boolean":
        value["value_boolean"] = random.choice([True, False])
    
    return value


def generate_task_tags(task: Dict, available_tags: List[Dict], project_type: str) -> List[Dict]:
    """
    Generate tag associations for a task.
    
    Distribution:
    - 30% of tasks have no tags
    - 50% have 1-2 tags
    - 15% have 3-4 tags
    - 5% have 5+ tags
    """
    rand = random.random()
    
    if rand < 0.30:
        num_tags = 0
    elif rand < 0.80:
        num_tags = random.randint(1, 2)
    elif rand < 0.95:
        num_tags = random.randint(3, 4)
    else:
        num_tags = random.randint(5, 8)
    
    associations = []
    if num_tags > 0 and available_tags:
        selected_tags = random.sample(available_tags, min(num_tags, len(available_tags)))
        for tag in selected_tags:
            associations.append({
                "task_id": task["task_id"],
                "tag_id": tag["tag_id"]
            })
    
    return associations


def generate_attachments(task: Dict, potential_users: List[str]) -> List[Dict]:
    """
    Generate file attachments for tasks.
    
    Distribution:
    - 70% of tasks have no attachments
    - 25% have 1 attachment
    - 5% have 2-4 attachments
    """
    rand = random.random()
    
    if rand < 0.70:
        num_attachments = 0
    elif rand < 0.95:
        num_attachments = 1
    else:
        num_attachments = random.randint(2, 4)
    
    attachments = []
    if num_attachments > 0 and potential_users:
        file_types = [
            ("document.pdf", "application/pdf", 1024 * 500),  # 500KB
            ("image.png", "image/png", 1024 * 200),  # 200KB
            ("spreadsheet.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 1024 * 300),
            ("presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation", 1024 * 800),
            ("screenshot.jpg", "image/jpeg", 1024 * 150),
        ]
        
        for _ in range(num_attachments):
            filename, file_type, file_size = random.choice(file_types)
            
            attachments.append({
                "attachment_id": str(uuid.uuid4()),
                "task_id": task["task_id"],
                "user_id": random.choice(potential_users),
                "filename": filename,
                "file_type": file_type,
                "file_size": file_size,
                "created_at": task["created_at"]
            })
    
    return attachments
