"""
LLM utilities for generating realistic text content using OpenAI API.
"""
import os
import random
from typing import List, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMGenerator:
    """Generates realistic text content using OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY in .env file.")
        self.client = OpenAI(api_key=self.api_key)
        
    def generate_text(
        self,
        prompt: str,
        temperature: float = 0.9,
        max_tokens: int = 200,
        model: str = "gpt-3.5-turbo"
    ) -> str:
        """Generate text using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates realistic, professional content for business applications."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Warning: LLM generation failed: {e}. Using fallback.")
            return self._fallback_generation(prompt)
    
    def _fallback_generation(self, prompt: str) -> str:
        """Fallback generation when API fails."""
        # Simple heuristics-based fallback
        if "task name" in prompt.lower():
            return "Implement feature authentication"
        elif "description" in prompt.lower():
            return "This task involves implementing the requested functionality with proper error handling and testing."
        else:
            return "Generated content"
    
    def generate_task_name(
        self,
        project_type: str,
        component: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """
        Generate realistic task names based on project type.
        
        Engineering tasks: "[Component] - [Action] - [Detail]"
        Marketing tasks: "[Campaign] - [Deliverable]"
        Bug tracking: "[Component] - Fix [Issue]"
        """
        prompt_templates = {
            "sprint": f"""Generate a realistic software engineering task name in the format "[Component] - [Action] - [Detail]". 
Examples: "API Gateway - Implement rate limiting - Add Redis cache", "Frontend - Add user authentication UI - Login modal component"
Component: {component or 'System'}
Context: {context or 'General development'}
Generate one task name only, no quotes or numbering:""",
            
            "bug_tracking": f"""Generate a realistic bug fix task name in the format "[Component] - Fix [Issue Description]".
Examples: "Database - Fix connection pool timeout", "UI - Fix button alignment on mobile", "API - Fix null pointer exception in user endpoint"
Component: {component or 'System'}
Generate one bug fix task name only:""",
            
            "marketing_campaign": f"""Generate a realistic marketing task name in the format "[Campaign/Deliverable] - [Action]".
Examples: "Q4 Product Launch - Create social media content", "Website Redesign - Design landing page mockups", "Email Campaign - Write newsletter copy"
Context: {context or 'Marketing campaign'}
Generate one marketing task name only:""",
            
            "launch": f"""Generate a realistic product launch task name.
Examples: "Prepare launch announcement blog post", "Set up analytics tracking", "Create demo video script", "Coordinate beta tester feedback"
Context: {context or 'Product launch'}
Generate one launch task name only:""",
            
            "ongoing": f"""Generate a realistic ongoing operations task name.
Examples: "Review monthly performance metrics", "Update documentation", "Customer support ticket triage", "Infrastructure monitoring review"
Context: {context or 'Ongoing operations'}
Generate one task name only:"""
        }
        
        template = prompt_templates.get(project_type, prompt_templates["ongoing"])
        return self.generate_text(template, temperature=0.9, max_tokens=50)
    
    def generate_task_description(
        self,
        task_name: str,
        project_context: str,
        include_bullets: bool = False
    ) -> str:
        """
        Generate realistic task descriptions with varying formats.
        
        Distribution:
        - 20% empty descriptions
        - 50% 1-3 sentences
        - 30% detailed with formatting (bullets, links, etc.)
        """
        rand = random.random()
        
        if rand < 0.20:
            return ""  # 20% empty
        
        elif rand < 0.70:  # 50% simple descriptions
            prompt = f"""Write a brief 1-3 sentence description for this task: "{task_name}"
Project context: {project_context}
Keep it concise and professional:"""
            return self.generate_text(prompt, temperature=0.8, max_tokens=100)
        
        else:  # 30% detailed descriptions
            format_hint = "Include bullet points or numbered list" if include_bullets else "Use clear formatting"
            prompt = f"""Write a detailed task description (3-6 sentences) for: "{task_name}"
Project context: {project_context}
{format_hint}. Include relevant context, requirements, and acceptance criteria if appropriate:"""
            return self.generate_text(prompt, temperature=0.85, max_tokens=200)
    
    def generate_comment(
        self,
        task_name: str,
        comment_type: str = "general"
    ) -> str:
        """
        Generate realistic task comments.
        
        Comment types: general, question, update, approval
        """
        prompts = {
            "general": f"""Write a brief, realistic comment on this task: "{task_name}"
Examples: "Looks good to me!", "Can we add error handling here?", "I'll start working on this tomorrow"
Write one comment only:""",
            
            "question": f"""Write a question or clarification comment about this task: "{task_name}"
Examples: "What should we do if the API returns an error?", "Should this include mobile support?"
Write one question comment:""",
            
            "update": f"""Write an update or status comment on this task: "{task_name}"
Examples: "Just finished the first draft, ready for review", "Blocked on API access, waiting for credentials"
Write one update comment:""",
            
            "approval": f"""Write an approval or acknowledgment comment on this task: "{task_name}"
Examples: "Approved! Looks great.", "This works for me, thanks!", "LGTM"
Write one approval comment:"""
        }
        
        prompt = prompts.get(comment_type, prompts["general"])
        return self.generate_text(prompt, temperature=0.9, max_tokens=100)
    
    def generate_project_description(self, project_name: str, project_type: str) -> str:
        """Generate realistic project descriptions."""
        prompt = f"""Write a 2-4 sentence project description for: "{project_name}"
Project type: {project_type}
Keep it professional and realistic. Include goals and scope:"""
        return self.generate_text(prompt, temperature=0.8, max_tokens=150)
