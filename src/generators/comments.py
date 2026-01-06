"""
Comment/Story generation for tasks.
"""
import uuid
from datetime import datetime, timedelta
import random
from typing import List, Dict, Optional

from src.utils.llm import LLMGenerator


COMMENT_TYPES = ["general", "question", "update", "approval"]


def generate_comment(
    task_id: str,
    user_id: str,
    task_name: str,
    created_at: datetime,
    llm_generator: Optional[LLMGenerator] = None
) -> Dict:
    """
    Generate a realistic task comment.
    
    Methodology:
    - Text: LLM-generated with different types (general, question, update, approval)
    - Timing: Comments created after task creation, clustered in first few days
    - Pinned: ~2% of comments are pinned
    """
    # Comment timing: most comments within first week, some later
    days_after_task = random.choices(
        range(30),
        weights=[15, 12, 10, 8, 6, 5, 4] + [2] * 23,  # More comments early
        k=1
    )[0]
    
    comment_created_at = created_at + timedelta(days=days_after_task)
    
    # Generate comment text
    comment_type = random.choice(COMMENT_TYPES)
    text = "Looks good!"
    
    if llm_generator:
        try:
            text = llm_generator.generate_comment(task_name, comment_type)
        except:
            # Fallback comments
            fallbacks = {
                "general": ["Looks good!", "Thanks for the update.", "This makes sense."],
                "question": ["Can you clarify this?", "What's the timeline?", "Any blockers?"],
                "update": ["Working on this now.", "Just finished the first pass.", "Ready for review."],
                "approval": ["Approved!", "LGTM", "This works for me."]
            }
            text = random.choice(fallbacks.get(comment_type, ["Comment"]))
    
    # Pinned comments: rare
    is_pinned = random.random() < 0.02
    
    return {
        "comment_id": str(uuid.uuid4()),
        "task_id": task_id,
        "user_id": user_id,
        "text": text,
        "created_at": comment_created_at,
        "is_pinned": is_pinned
    }


def generate_comments_for_task(
    task: Dict,
    potential_commenters: List[str],
    llm_generator: Optional[LLMGenerator] = None
) -> List[Dict]:
    """
    Generate comments for a task.
    
    Distribution:
    - 40% of tasks have no comments
    - 40% have 1-3 comments
    - 15% have 4-8 comments
    - 5% have 9+ comments (active discussions)
    """
    rand = random.random()
    
    if rand < 0.40:
        num_comments = 0
    elif rand < 0.80:
        num_comments = random.randint(1, 3)
    elif rand < 0.95:
        num_comments = random.randint(4, 8)
    else:
        num_comments = random.randint(9, 15)
    
    comments = []
    if num_comments > 0 and potential_commenters:
        for _ in range(num_comments):
            commenter = random.choice(potential_commenters)
            comment = generate_comment(
                task["task_id"],
                commenter,
                task["name"],
                task["created_at"],
                llm_generator
            )
            comments.append(comment)
    
    return comments
