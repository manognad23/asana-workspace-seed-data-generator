"""
Main orchestration script for generating Asana simulation seed data.
"""
import os
import sys
import random
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.database import Database
from src.utils.dates import get_historical_date_range
from src.utils.llm import LLMGenerator
from src.scrapers.companies import get_realistic_company_data
from src.generators.users import generate_users
from src.generators.teams import generate_teams, generate_team_membership
from src.generators.projects import generate_projects, generate_sections
from src.generators.tasks import generate_tasks_for_project
from src.generators.comments import generate_comments_for_task
from src.generators.metadata import (
    generate_tags,
    generate_custom_field_definitions,
    generate_custom_field_value,
    generate_task_tags,
    generate_attachments
)

load_dotenv()


# Configuration
CONFIG = {
    'organization_size': 7000,  # Target company size (5000-10000 range)
    'num_teams': 50,            # Number of teams
    'projects_per_team': 3,     # Average projects per team
    'date_range_months': 6,     # Historical data range (months)
    'num_tags': 30,             # Workspace tags
    'use_llm': True,            # Use OpenAI API for text generation (set to False to skip LLM)
}


def generate_organization(db: Database, start_date: datetime, end_date: datetime):
    """Generate organization/workspace."""
    print("Generating organization...")
    company_data = get_realistic_company_data()
    
    organization_id = "org_123456789"  # Simple ID format
    domain = company_data["name"].lower().replace(" ", "").replace("inc", "").replace("systems", "").replace("solutions", "").replace("technologies", "").replace("tech", "").strip() + ".com"
    
    db.execute(
        """INSERT INTO organizations (organization_id, name, domain, created_at, is_enterprise)
           VALUES (?, ?, ?, ?, ?)""",
        (organization_id, company_data["name"], domain, start_date, True)
    )
    
    print(f"[OK] Created organization: {company_data['name']} ({domain})")
    return organization_id, domain


def generate_users_data(db: Database, organization_id: str, domain: str, start_date: datetime, end_date: datetime):
    """Generate users."""
    print(f"\nGenerating {CONFIG['organization_size']} users...")
    users = generate_users(organization_id, CONFIG['organization_size'], start_date, end_date)
    
    # Insert users with email domain
    user_records = []
    emails_seen = set()
    duplicate_count = 0
    
    # #region agent log
    import json
    with open(r'c:\Users\manog\OneDrive\Desktop\Scalar Assignment\.scalar\debug.log', 'a') as f:
        f.write(json.dumps({"location": "main.py:68", "message": "Starting email domain combination", "data": {"user_count": len(users), "domain": domain}, "timestamp": int(datetime.now().timestamp() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
    # #endregion
    
    for idx, user in enumerate(users):
        email = f"{user['email_local']}@{domain}"
        
        # #region agent log
        if email in emails_seen:
            with open(r'c:\Users\manog\OneDrive\Desktop\Scalar Assignment\.scalar\debug.log', 'a') as f:
                f.write(json.dumps({"location": "main.py:75", "message": "Duplicate email detected", "data": {"email": email, "index": idx}, "timestamp": int(datetime.now().timestamp() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
        # #endregion
        
        if email in emails_seen:
            duplicate_count += 1
            # Add unique suffix
            email = f"{user['email_local']}{idx}@{domain}"
            # #region agent log
            with open(r'c:\Users\manog\OneDrive\Desktop\Scalar Assignment\.scalar\debug.log', 'a') as f:
                f.write(json.dumps({"location": "main.py:83", "message": "Fixed duplicate email", "data": {"new_email": email}, "timestamp": int(datetime.now().timestamp() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
            # #endregion
        
        emails_seen.add(email)
        user_records.append((
            user['user_id'],
            user['organization_id'],
            email,
            user['name'],
            user['title'],
            user['department'],
            user['created_at'],
            user['is_admin']
        ))
    
    # #region agent log
    with open(r'c:\Users\manog\OneDrive\Desktop\Scalar Assignment\.scalar\debug.log', 'a') as f:
        f.write(json.dumps({"location": "main.py:101", "message": "Before database insert", "data": {"records_count": len(user_records), "unique_emails": len(emails_seen), "duplicates_found": duplicate_count}, "timestamp": int(datetime.now().timestamp() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "B"}) + "\n")
    # #endregion
    
    db.executemany(
        """INSERT INTO users (user_id, organization_id, email, name, title, department, created_at, is_admin)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        user_records
    )
    
    db.commit()
    print(f"[OK] Generated {len(users)} users")
    return users


def generate_teams_data(db: Database, organization_id: str, users: list, start_date: datetime, end_date: datetime):
    """Generate teams and memberships."""
    print(f"\nGenerating {CONFIG['num_teams']} teams...")
    teams = generate_teams(organization_id, CONFIG['num_teams'], start_date, end_date)
    
    # Insert teams
    team_records = []
    for team in teams:
        team_records.append((
            team['team_id'],
            team['organization_id'],
            team['name'],
            team['description'],
            team['created_at']
        ))
    
    db.executemany(
        """INSERT INTO teams (team_id, organization_id, name, description, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        team_records
    )
    
    # Generate team memberships
    print("Generating team memberships...")
    memberships = []
    
    # Import get_team_size_distribution
    from src.utils.distributions import get_team_size_distribution
    
    # Track which users are already in teams
    users_in_teams = set()
    
    for team in teams:
        team_size = get_team_size_distribution()
        selected_users = set()
        
        # Select users for this team (prefer users not yet in teams)
        available_users = [u for u in users if u['user_id'] not in users_in_teams]
        if not available_users:
            available_users = users  # Fall back to all users if needed
        
        for _ in range(min(team_size, len(available_users))):
            user = random.choice(available_users)
            user_id = user['user_id']
            if user_id not in selected_users:
                selected_users.add(user_id)
                users_in_teams.add(user_id)
                
                # Joined_at: team creation or later (when user joined company)
                joined_at = max(team['created_at'], user['created_at'])
                membership = generate_team_membership(team['team_id'], user_id, joined_at)
                memberships.append(membership)
                available_users.remove(user)
                if not available_users:
                    break
    
    # Ensure all remaining users are in at least one team
    remaining_users = [u for u in users if u['user_id'] not in users_in_teams]
    for user in remaining_users:
        team = random.choice(teams)
        joined_at = max(team['created_at'], user['created_at'])
        membership = generate_team_membership(team['team_id'], user['user_id'], joined_at)
        memberships.append(membership)
        users_in_teams.add(user['user_id'])
    
    # Insert memberships
    membership_records = []
    for mem in memberships:
        membership_records.append((
            mem['membership_id'],
            mem['team_id'],
            mem['user_id'],
            mem['role'],
            mem['joined_at']
        ))
    
    db.executemany(
        """INSERT INTO team_memberships (membership_id, team_id, user_id, role, joined_at)
           VALUES (?, ?, ?, ?, ?)""",
        membership_records
    )
    
    db.commit()
    print(f"[OK] Generated {len(teams)} teams with {len(memberships)} memberships")
    return teams, memberships


def generate_projects_data(db: Database, teams: list, users: list, memberships: list, start_date: datetime, end_date: datetime, llm_generator):
    """Generate projects and sections."""
    print(f"\nGenerating projects...")
    projects = generate_projects(teams, CONFIG['projects_per_team'], start_date, end_date, llm_generator)
    
    # Insert projects
    project_records = []
    for project in projects:
        project_records.append((
            project['project_id'],
            project['team_id'],
            project['name'],
            project['description'],
            project['project_type'],
            project['created_at'],
            project['archived'],
            project['color']
        ))
    
    db.executemany(
        """INSERT INTO projects (project_id, team_id, name, description, project_type, created_at, archived, color)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        project_records
    )
    
    # Generate sections for each project
    print("Generating sections...")
    all_sections = []
    for project in projects:
        sections = generate_sections(project)
        all_sections.extend(sections)
    
    # Insert sections
    section_records = []
    for section in all_sections:
        section_records.append((
            section['section_id'],
            section['project_id'],
            section['name'],
            section['position'],
            section['created_at']
        ))
    
    db.executemany(
        """INSERT INTO sections (section_id, project_id, name, position, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        section_records
    )
    
    db.commit()
    print(f"[OK] Generated {len(projects)} projects with {len(all_sections)} sections")
    return projects, all_sections


def generate_tasks_data(db: Database, projects: list, sections: list, users: list, memberships: list, start_date: datetime, end_date: datetime, llm_generator):
    """Generate tasks and subtasks."""
    print(f"\nGenerating tasks...")
    
    # Build team members lookup
    team_members_map = {}
    for membership in memberships:
        team_id = membership['team_id']
        user_id = membership['user_id']
        if team_id not in team_members_map:
            team_members_map[team_id] = []
        team_members_map[team_id].append(user_id)
    
    # Group sections by project
    sections_by_project = {}
    for section in sections:
        if section['project_id'] not in sections_by_project:
            sections_by_project[section['project_id']] = []
        sections_by_project[section['project_id']].append(section)
    
    all_tasks = []
    task_count = 0
    
    for project in projects:
        project_sections = sections_by_project.get(project['project_id'], [])
        team_members = team_members_map.get(project['team_id'], [])
        
        tasks = generate_tasks_for_project(
            project,
            project_sections,
            team_members,
            start_date,
            end_date,
            llm_generator
        )
        
        all_tasks.extend(tasks)
        task_count += len(tasks)
        
        if task_count % 100 == 0:
            print(f"  Generated {task_count} tasks...")
    
    # Insert tasks
    task_records = []
    for task in all_tasks:
        task_records.append((
            task['task_id'],
            task['project_id'],
            task['section_id'],
            task['parent_task_id'],
            task['assignee_id'],
            task['name'],
            task['description'],
            task['due_date'],
            task['start_date'],
            task['created_at'],
            task['completed'],
            task['completed_at'],
            task['likes_count'],
            task['num_subtasks'],
            task['num_subtasks_completed']
        ))
    
    db.executemany(
        """INSERT INTO tasks (task_id, project_id, section_id, parent_task_id, assignee_id, name, description,
           due_date, start_date, created_at, completed, completed_at, likes_count, num_subtasks, num_subtasks_completed)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        task_records
    )
    
    db.commit()
    print(f"[OK] Generated {len(all_tasks)} tasks")
    return all_tasks


def generate_metadata(db: Database, organization_id: str, projects: list, tasks: list, users: list, start_date: datetime, llm_generator=None):
    """Generate tags, custom fields, comments, and attachments."""
    print(f"\nGenerating metadata...")
    
    # Generate tags
    tags = generate_tags(organization_id, CONFIG['num_tags'], start_date)
    tag_records = []
    for tag in tags:
        tag_records.append((
            tag['tag_id'],
            tag['organization_id'],
            tag['name'],
            tag['color'],
            tag['created_at']
        ))
    
    db.executemany(
        """INSERT INTO tags (tag_id, organization_id, name, color, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        tag_records
    )
    
    # Generate custom fields
    all_custom_fields = []
    for project in projects:
        fields = generate_custom_field_definitions(project)
        all_custom_fields.extend(fields)
    
    field_records = []
    for field in all_custom_fields:
        field_records.append((
            field['field_id'],
            field['project_id'],
            field['name'],
            field['field_type'],
            field['enum_options'],
            field['created_at']
        ))
    
    db.executemany(
        """INSERT INTO custom_field_definitions (field_id, project_id, name, field_type, enum_options, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        field_records
    )
    
    # Generate custom field values
    all_field_values = []
    for field in all_custom_fields:
        project_tasks = [t for t in tasks if t['project_id'] == field['project_id']]
        for task in project_tasks:
            value = generate_custom_field_value(task, field)
            if value:
                all_field_values.append(value)
    
    value_records = []
    for value in all_field_values:
        value_records.append((
            value['value_id'],
            value['task_id'],
            value['field_id'],
            value['value_text'],
            value['value_number'],
            value['value_date'],
            value['value_boolean']
        ))
    
    if value_records:
        db.executemany(
            """INSERT INTO custom_field_values (value_id, task_id, field_id, value_text, value_number, value_date, value_boolean)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            value_records
        )
    
    # Generate task-tag associations
    task_tags = []
    for task in tasks:
        associations = generate_task_tags(task, tags, None)
        task_tags.extend(associations)
    
    tag_assoc_records = [(ta['task_id'], ta['tag_id']) for ta in task_tags]
    if tag_assoc_records:
        db.executemany(
            """INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)""",
            tag_assoc_records
        )
    
    # Generate comments
    print("Generating comments...")
    user_ids = [u['user_id'] for u in users]
    all_comments = []
    
    comment_count = 0
    for task in tasks:
        comments = generate_comments_for_task(task, user_ids, llm_generator)
        all_comments.extend(comments)
        comment_count += len(comments)
        if comment_count % 100 == 0:
            print(f"  Generated {comment_count} comments...")
    
    comment_records = []
    for comment in all_comments:
        comment_records.append((
            comment['comment_id'],
            comment['task_id'],
            comment['user_id'],
            comment['text'],
            comment['created_at'],
            comment['is_pinned']
        ))
    
    if comment_records:
        db.executemany(
            """INSERT INTO comments (comment_id, task_id, user_id, text, created_at, is_pinned)
               VALUES (?, ?, ?, ?, ?, ?)""",
            comment_records
        )
    
    # Generate attachments
    print("Generating attachments...")
    all_attachments = []
    for task in tasks:
        attachments = generate_attachments(task, user_ids)
        all_attachments.extend(attachments)
    
    attachment_records = []
    for att in all_attachments:
        attachment_records.append((
            att['attachment_id'],
            att['task_id'],
            att['user_id'],
            att['filename'],
            att['file_type'],
            att['file_size'],
            att['created_at']
        ))
    
    if attachment_records:
        db.executemany(
            """INSERT INTO attachments (attachment_id, task_id, user_id, filename, file_type, file_size, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            attachment_records
        )
    
    db.commit()
    print(f"[OK] Generated {len(tags)} tags, {len(all_custom_fields)} custom fields, {len(all_comments)} comments, {len(all_attachments)} attachments")
    
    return tags, all_custom_fields, all_comments, all_attachments


def main():
    """Main orchestration function."""
    print("=" * 60)
    print("Asana Simulation Seed Data Generator")
    print("=" * 60)
    
    # Initialize database (recreate if exists)
    db = Database()
    db.connect(recreate=True)
    db.initialize_schema()
    
    # Initialize LLM generator (optional)
    llm_generator = None
    if CONFIG['use_llm']:
        try:
            llm_generator = LLMGenerator()
            print("[OK] LLM generator initialized")
        except Exception as e:
            print(f"[WARN] LLM generator unavailable: {e}. Continuing without LLM.")
            print("[WARN] Note: Task names and descriptions will use fallback templates (less realistic).")
            llm_generator = None
    
    # Get date range
    start_date, end_date = get_historical_date_range(CONFIG['date_range_months'])
    print(f"\nGenerating data for period: {start_date.date()} to {end_date.date()}")
    
    # Generate data in order
    organization_id, domain = generate_organization(db, start_date, end_date)
    users = generate_users_data(db, organization_id, domain, start_date, end_date)
    teams, memberships = generate_teams_data(db, organization_id, users, start_date, end_date)
    projects, sections = generate_projects_data(db, teams, users, memberships, start_date, end_date, llm_generator)
    tasks = generate_tasks_data(db, projects, sections, users, memberships, start_date, end_date, llm_generator)
    generate_metadata(db, organization_id, projects, tasks, users, start_date)
    
    # Final statistics
    print("\n" + "=" * 60)
    print("Generation Complete!")
    print("=" * 60)
    
    stats = db.execute("""
        SELECT 
            (SELECT COUNT(*) FROM organizations) as orgs,
            (SELECT COUNT(*) FROM teams) as teams,
            (SELECT COUNT(*) FROM users) as users,
            (SELECT COUNT(*) FROM projects) as projects,
            (SELECT COUNT(*) FROM tasks) as tasks,
            (SELECT COUNT(*) FROM comments) as comments,
            (SELECT COUNT(*) FROM tags) as tags
    """).fetchone()
    
    print(f"Organizations: {stats[0]}")
    print(f"Teams: {stats[1]}")
    print(f"Users: {stats[2]}")
    print(f"Projects: {stats[3]}")
    print(f"Tasks: {stats[4]}")
    print(f"Comments: {stats[5]}")
    print(f"Tags: {stats[6]}")
    print(f"\nDatabase saved to: {db.db_path}")
    
    db.close()
    print("\n[OK] Done!")


if __name__ == "__main__":
    main()
