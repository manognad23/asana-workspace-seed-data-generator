"""
Date and time generation utilities with realistic distributions.
"""
from datetime import datetime, timedelta, date
import random
import numpy as np
from scipy.stats import lognorm


def generate_created_at(
    start_date: datetime,
    end_date: datetime,
    higher_weekdays: bool = True
) -> datetime:
    """
    Generate a realistic creation timestamp.
    
    Research-based: Asana data shows higher activity Mon-Wed, lower Thu-Fri.
    """
    # Generate random time within range
    time_delta = end_date - start_date
    random_days = random.randint(0, time_delta.days)
    base_date = start_date + timedelta(days=random_days)
    
    if higher_weekdays:
        # Weight weekdays more heavily (Mon-Wed higher, Thu-Fri lower)
        weekday = base_date.weekday()
        if weekday in [0, 1, 2]:  # Mon, Tue, Wed
            # Already in high-activity days
            pass
        elif weekday in [3, 4]:  # Thu, Fri
            # 30% chance to move to earlier in week
            if random.random() < 0.3:
                base_date -= timedelta(days=random.randint(1, 3))
        elif weekday == 6:  # Sunday
            # Move to Monday
            base_date += timedelta(days=1)
        elif weekday == 5:  # Saturday
            # Move to Friday or Monday
            base_date += timedelta(days=2 if random.random() < 0.5 else -1)
    
    # Generate time of day (9 AM - 6 PM bias, with some outliers)
    hour = random.choices(
        range(24),
        weights=[0.5]*9 + [2]*8 + [1.5]*3 + [0.5]*4,  # 0-8 low, 9-16 high, 17-19 medium, 20-23 low
        k=1
    )[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    return base_date.replace(hour=hour, minute=minute, second=second)


def generate_due_date(
    created_at: datetime,
    project_type: str = "general"
) -> datetime | None:
    """
    Generate a realistic due date based on task creation time and project type.
    
    Distribution research:
    - 25% within 1 week
    - 40% within 1 month  
    - 20% 1-3 months out
    - 10% no due date
    - 5% overdue (created but not due)
    
    Sprint projects cluster around sprint boundaries.
    """
    # 10% have no due date
    if random.random() < 0.10:
        return None
    
    rand = random.random()
    
    if project_type == "sprint":
        # Sprint tasks: cluster around 2-week sprint boundaries
        sprint_length = 14
        days_from_start = (created_at.date() - date(2024, 1, 1)).days
        sprint_end = ((days_from_start // sprint_length) + 1) * sprint_length
        days_until_due = sprint_end - days_from_start
        # Add some variance: 70% on sprint boundary, 30% distributed
        if random.random() < 0.7:
            due_in_days = max(1, days_until_due + random.randint(-2, 2))
        else:
            due_in_days = random.randint(1, 21)
    elif rand < 0.25:  # 25% within 1 week
        due_in_days = random.randint(1, 7)
    elif rand < 0.65:  # 40% within 1 month (total 40% of remaining)
        due_in_days = random.randint(8, 30)
    elif rand < 0.85:  # 20% 1-3 months
        due_in_days = random.randint(31, 90)
    else:  # 15% longer term
        due_in_days = random.randint(91, 180)
    
    # Avoid weekends for 85% of tasks (move to Friday if falls on weekend)
    due_date = created_at + timedelta(days=due_in_days)
    if due_date.weekday() >= 5 and random.random() < 0.85:  # Saturday or Sunday
        # Move to Friday
        days_to_friday = (4 - due_date.weekday()) % 7
        due_date = due_date + timedelta(days=days_to_friday - 7)
    
    # 5% chance of overdue (due date in the past relative to creation)
    if random.random() < 0.05:
        due_date = created_at - timedelta(days=random.randint(1, 30))
    
    return due_date.date()


def generate_completed_at(
    created_at: datetime,
    due_date: date | None = None,
    completion_rate: float = 0.65
) -> datetime | None:
    """
    Generate completion timestamp if task is completed.
    
    Based on cycle time research:
    - Completed tasks typically finished 1-14 days after creation
    - Follows log-normal distribution
    - Always after created_at and before now (or before due_date if specified)
    """
    if random.random() > completion_rate:
        return None
    
    # Log-normal distribution for cycle time (mean ~5 days, std ~3 days)
    # Convert to normal parameters
    mu = np.log(5)  # Mean of underlying normal
    sigma = 0.6  # Std of underlying normal
    
    cycle_days = max(1, int(lognorm.rvs(s=sigma, scale=np.exp(mu), size=1)[0]))
    cycle_days = min(cycle_days, 60)  # Cap at 60 days
    
    completed_at = created_at + timedelta(days=cycle_days)
    
    # If due_date exists, completed_at should be before it (for most tasks)
    if due_date and random.random() < 0.80:
        due_datetime = datetime.combine(due_date, datetime.min.time())
        if completed_at > due_datetime:
            # Complete before due date (sometimes)
            completed_at = due_datetime - timedelta(days=random.randint(0, 5))
    
    # Ensure completed_at is after created_at
    if completed_at <= created_at:
        completed_at = created_at + timedelta(days=1)
    
    return completed_at


def get_historical_date_range(months_back: int = 6) -> tuple[datetime, datetime]:
    """Get start and end dates for historical data generation."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months_back * 30)
    return start_date, end_date
