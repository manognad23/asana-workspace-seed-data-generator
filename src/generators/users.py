"""
User generation with realistic names, emails, and profiles.
Uses US Census data patterns via Faker.
"""
import uuid
from datetime import datetime, timedelta
from faker import Faker
import random
from typing import List, Dict

fake = Faker('en_US')


# Department distribution for B2B SaaS company (5000-10000 employees)
DEPARTMENTS = [
    "Engineering", "Product", "Design", "Marketing", "Sales",
    "Customer Success", "Support", "Operations", "HR", "Finance",
    "Legal", "Security", "Data & Analytics", "IT", "Business Development"
]

# Title patterns by department
TITLES_BY_DEPARTMENT = {
    "Engineering": ["Software Engineer", "Senior Software Engineer", "Staff Engineer", "Engineering Manager", "Principal Engineer", "DevOps Engineer", "QA Engineer"],
    "Product": ["Product Manager", "Senior Product Manager", "Product Owner", "VP of Product", "Product Designer"],
    "Design": ["UX Designer", "UI Designer", "Senior Designer", "Design Manager", "Design Lead"],
    "Marketing": ["Marketing Manager", "Content Manager", "Growth Manager", "Brand Manager", "Marketing Director"],
    "Sales": ["Account Executive", "Sales Manager", "Sales Director", "Sales Engineer", "VP of Sales"],
    "Customer Success": ["Customer Success Manager", "CS Lead", "Account Manager", "Customer Success Director"],
    "Support": ["Support Engineer", "Support Manager", "Technical Support Specialist"],
    "Operations": ["Operations Manager", "Operations Analyst", "Operations Director"],
    "HR": ["HR Manager", "Recruiter", "HR Business Partner", "Talent Acquisition"],
    "Finance": ["Financial Analyst", "Finance Manager", "Controller", "CFO"],
    "Legal": ["Legal Counsel", "Legal Assistant", "General Counsel"],
    "Security": ["Security Engineer", "Security Analyst", "CISO", "Security Manager"],
    "Data & Analytics": ["Data Analyst", "Data Scientist", "Analytics Engineer", "BI Analyst"],
    "IT": ["IT Administrator", "IT Manager", "Systems Administrator"],
    "Business Development": ["Business Development Manager", "BD Director", "Partnership Manager"]
}


def generate_user(organization_id: str, created_at: datetime) -> Dict:
    """
    Generate a realistic user profile.
    
    Methodology:
    - Names: US Census data via Faker (realistic demographic distribution)
    - Emails: Based on name + company domain
    - Titles: Realistic job titles by department
    - Departments: Weighted by typical SaaS company distribution
    - Admin status: ~5% are admins
    """
    department = random.choices(
        DEPARTMENTS,
        weights=[25, 8, 5, 12, 15, 8, 5, 4, 3, 3, 2, 3, 4, 2, 1],  # Engineering-heavy
        k=1
    )[0]
    
    titles = TITLES_BY_DEPARTMENT.get(department, ["Manager", "Specialist"])
    title = random.choice(titles)
    
    # Generate name (realistic US demographic distribution)
    name = fake.name()
    
    # Generate email (first.last format, with variations)
    email_format = random.choices(
        ["{first}.{last}", "{first}{last}", "{first}{last_initial}", "{first_initial}{last}"],
        weights=[50, 25, 15, 10],
        k=1
    )[0]
    
    name_parts = name.lower().split()
    first = name_parts[0] if name_parts else "user"
    last = name_parts[1] if len(name_parts) > 1 else "user"
    
    # Generate unique email by adding random number if needed (will be handled in calling function)
    email_local = email_format.format(
        first=first,
        last=last,
        first_initial=first[0],
        last_initial=last[0] if last else ""
    ).replace(" ", "").replace("'", "").replace(".", "")
    
    # Email domain will be set when we know the organization domain
    
    # Admin status: ~5% are admins (higher in certain departments)
    is_admin = False
    if department in ["Engineering", "Operations", "Security"]:
        is_admin = random.random() < 0.08  # 8% in technical roles
    else:
        is_admin = random.random() < 0.03  # 3% in other roles
    
    return {
        "user_id": str(uuid.uuid4()),
        "organization_id": organization_id,
        "name": name,
        "title": title,
        "department": department,
        "email_local": email_local,  # Will combine with domain later
        "is_admin": is_admin,
        "created_at": created_at
    }


def generate_users(organization_id: str, count: int, start_date: datetime, end_date: datetime) -> List[Dict]:
    """Generate multiple users with temporal distribution."""
    users = []
    email_locals_seen = set()  # Track emails to ensure uniqueness
    
    # #region agent log
    with open(r'c:\Users\manog\OneDrive\Desktop\Scalar Assignment\.scalar\debug.log', 'a') as f:
        import json
        f.write(json.dumps({"location": "users.py:105", "message": "Starting user generation", "data": {"count": count}, "timestamp": int(datetime.now().timestamp() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
    # #endregion
    
    # Temporal distribution: more users created earlier (company growth curve)
    # Early days: high hiring rate
    # Recent: lower rate (company more established)
    
    for i in range(count):
        # Bias toward earlier dates (company was smaller, growing)
        days_ago = random.betavariate(2, 1) * (end_date - start_date).days
        created_at = end_date - timedelta(days=int(days_ago))
        
        # #region agent log
        with open(r'c:\Users\manog\OneDrive\Desktop\Scalar Assignment\.scalar\debug.log', 'a') as f:
            import json
            f.write(json.dumps({"location": "users.py:120", "message": "Generating user", "data": {"i": i, "total": count}, "timestamp": int(datetime.now().timestamp() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
        # #endregion
        
        # Generate user and ensure unique email
        max_attempts = 10
        email_local = None
        for attempt in range(max_attempts):
            user = generate_user(organization_id, created_at)
            email_local = user['email_local']
            
            # #region agent log
            with open(r'c:\Users\manog\OneDrive\Desktop\Scalar Assignment\.scalar\debug.log', 'a') as f:
                import json
                f.write(json.dumps({"location": "users.py:128", "message": "Generated email_local", "data": {"email_local": email_local, "attempt": attempt, "in_set": email_local in email_locals_seen, "set_size": len(email_locals_seen)}, "timestamp": int(datetime.now().timestamp() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
            # #endregion
            
            if email_local not in email_locals_seen:
                email_locals_seen.add(email_local)
                break
            else:
                # Add random suffix to make unique
                email_local = f"{user['email_local']}{random.randint(100, 999)}"
                # #region agent log
                with open(r'c:\Users\manog\OneDrive\Desktop\Scalar Assignment\.scalar\debug.log', 'a') as f:
                    import json
                    f.write(json.dumps({"location": "users.py:138", "message": "Added suffix for uniqueness", "data": {"new_email_local": email_local}, "timestamp": int(datetime.now().timestamp() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
                # #endregion
                if email_local not in email_locals_seen:
                    email_locals_seen.add(email_local)
                    user['email_local'] = email_local
                    break
        
        # Final fallback if still duplicate
        if email_local in email_locals_seen or email_local is None:
            email_local = f"user{i}{random.randint(10000, 99999)}"
            user['email_local'] = email_local
            email_locals_seen.add(email_local)
            # #region agent log
            with open(r'c:\Users\manog\OneDrive\Desktop\Scalar Assignment\.scalar\debug.log', 'a') as f:
                import json
                f.write(json.dumps({"location": "users.py:151", "message": "Using fallback email", "data": {"email_local": email_local}, "timestamp": int(datetime.now().timestamp() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
            # #endregion
        
        users.append(user)
        
        # #region agent log
        if (i + 1) % 1000 == 0:
            with open(r'c:\Users\manog\OneDrive\Desktop\Scalar Assignment\.scalar\debug.log', 'a') as f:
                import json
                f.write(json.dumps({"location": "users.py:157", "message": "Progress update", "data": {"generated": i + 1, "unique_emails": len(email_locals_seen)}, "timestamp": int(datetime.now().timestamp() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
        # #endregion
    
    # #region agent log
    with open(r'c:\Users\manog\OneDrive\Desktop\Scalar Assignment\.scalar\debug.log', 'a') as f:
        import json
        f.write(json.dumps({"location": "users.py:163", "message": "User generation complete", "data": {"total": len(users), "unique_emails": len(email_locals_seen)}, "timestamp": int(datetime.now().timestamp() * 1000), "sessionId": "debug-session", "runId": "run1", "hypothesisId": "A"}) + "\n")
    # #endregion
    
    return users
