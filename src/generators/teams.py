"""
Team generation with realistic team structures.
"""
import uuid
from datetime import datetime, timedelta
from faker import Faker
import random
from typing import List, Dict

fake = Faker()


# Team name patterns by function
TEAM_PATTERNS = {
    "engineering": [
        "Backend Engineering", "Frontend Engineering", "Platform Team",
        "Infrastructure", "DevOps", "Security Engineering", "QA Engineering",
        "Mobile Engineering", "API Team", "Data Engineering"
    ],
    "product": [
        "Product Management", "Product Design", "User Experience",
        "Product Strategy", "Platform Product"
    ],
    "business": [
        "Enterprise Sales", "SMB Sales", "Sales Engineering",
        "Business Development", "Partnerships", "Revenue Operations"
    ],
    "marketing": [
        "Growth Marketing", "Content Marketing", "Product Marketing",
        "Brand Marketing", "Demand Generation", "Field Marketing"
    ],
    "operations": [
        "Customer Success", "Support", "Operations",
        "People Operations", "Legal & Compliance", "Finance"
    ]
}


def generate_team(organization_id: str, team_type: str, created_at: datetime) -> Dict:
    """
    Generate a realistic team.
    
    Methodology:
    - Team names: Based on common enterprise team structures
    - Descriptions: ~60% have descriptions (brief team purpose)
    """
    patterns = TEAM_PATTERNS.get(team_type, ["General Team"])
    name = random.choice(patterns)
    
    # Add team identifier sometimes (e.g., "Backend Engineering - Core")
    if random.random() < 0.2:
        suffixes = [" - Core", " - Platform", " - Services", " Team", ""]
        name += random.choice(suffixes)
    
    # 60% have descriptions
    description = None
    if random.random() < 0.6:
        description = f"Responsible for {name.lower()} initiatives and operations."
    
    return {
        "team_id": str(uuid.uuid4()),
        "organization_id": organization_id,
        "name": name,
        "description": description,
        "created_at": created_at
    }


def generate_teams(organization_id: str, count: int, start_date: datetime, end_date: datetime) -> List[Dict]:
    """Generate multiple teams."""
    teams = []
    
    # Team type distribution
    team_types = random.choices(
        ["engineering", "product", "business", "marketing", "operations"],
        weights=[40, 15, 20, 15, 10],  # Engineering-heavy for SaaS
        k=count
    )
    
    for team_type in team_types:
        # Teams created over time (more earlier, some recent)
        days_ago = random.betavariate(2, 1.5) * (end_date - start_date).days
        created_at = end_date - timedelta(days=int(days_ago))
        
        team = generate_team(organization_id, team_type, created_at)
        teams.append(team)
    
    return teams


def generate_team_membership(team_id: str, user_id: str, joined_at: datetime) -> Dict:
    """
    Generate team membership.
    
    Roles:
    - member: 85%
    - admin: 12% (team leads, managers)
    - limited_member: 3% (external, contractors)
    """
    role = random.choices(
        ["member", "admin", "limited_member"],
        weights=[85, 12, 3],
        k=1
    )[0]
    
    return {
        "membership_id": str(uuid.uuid4()),
        "team_id": team_id,
        "user_id": user_id,
        "role": role,
        "joined_at": joined_at
    }
