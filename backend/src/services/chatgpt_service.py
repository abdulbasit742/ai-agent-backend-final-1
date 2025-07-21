"""
ChatGPT Service - OpenAI API Integration
Compatible with Python 3.10 and openai==1.14.3
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatGPTService:
    """Service for OpenAI GPT integration"""
    
    def __init__(self):
        """Initialize ChatGPT service"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OpenAI API key not found. AI features will be disabled.")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("ChatGPT service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
    
    def is_available(self) -> bool:
        """Check if ChatGPT service is available"""
        return self.client is not None
    
    def generate_task_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered task suggestions"""
        if not self.is_available():
            return self._get_fallback_tasks()
        
        try:
            # Prepare context for AI
            team_info = context.get('team_info', {})
            project_context = context.get('project_context', 'General software development')
            current_tasks = context.get('current_tasks', [])
            performance_data = context.get('performance_data', {})
            
            # Create prompt
            prompt = self._create_task_generation_prompt(
                team_info, project_context, current_tasks, performance_data
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI project manager that generates relevant, actionable tasks for software development teams."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse response
            content = response.choices[0].message.content
            tasks = self._parse_task_response(content)
            
            logger.info(f"Generated {len(tasks)} AI tasks successfully")
            return tasks
            
        except Exception as e:
            logger.error(f"Error generating AI tasks: {e}")
            return self._get_fallback_tasks()
    
    def analyze_team_performance(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze team performance using AI"""
        if not self.is_available():
            return self._get_fallback_performance_analysis(team_data)
        
        try:
            # Prepare performance data
            members = team_data.get('members', [])
            tasks = team_data.get('tasks', [])
            timeframe = team_data.get('timeframe', '30 days')
            
            # Create analysis prompt
            prompt = self._create_performance_analysis_prompt(members, tasks, timeframe)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI performance analyst that provides insights on team productivity and recommendations for improvement."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.5
            )
            
            # Parse response
            content = response.choices[0].message.content
            analysis = self._parse_performance_response(content)
            
            logger.info("Generated AI performance analysis successfully")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return self._get_fallback_performance_analysis(team_data)
    
    def suggest_task_assignment(self, task_info: Dict[str, Any], team_members: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Suggest optimal task assignment using AI"""
        if not self.is_available():
            return self._get_fallback_assignment(task_info, team_members)
        
        try:
            # Create assignment prompt
            prompt = self._create_assignment_prompt(task_info, team_members)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI task assignment specialist that matches tasks to team members based on skills, workload, and performance."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            
            # Parse response
            content = response.choices[0].message.content
            assignment = self._parse_assignment_response(content, team_members)
            
            logger.info("Generated AI task assignment successfully")
            return assignment
            
        except Exception as e:
            logger.error(f"Error suggesting assignment: {e}")
            return self._get_fallback_assignment(task_info, team_members)
    
    def _create_task_generation_prompt(self, team_info: Dict, project_context: str, 
                                     current_tasks: List, performance_data: Dict) -> str:
        """Create prompt for task generation"""
        prompt = f"""
Generate 3-5 relevant software development tasks for a team working on: {project_context}

Team Information:
- Team size: {len(team_info.get('members', []))}
- Current active tasks: {len(current_tasks)}
- Average performance score: {performance_data.get('average_score', 75)}%

Current tasks in progress:
{self._format_current_tasks(current_tasks)}

Please generate tasks that are:
1. Specific and actionable
2. Appropriately scoped (1-3 days of work)
3. Complement existing work
4. Include clear acceptance criteria

Format your response as JSON array with this structure:
[
  {{
    "title": "Task title",
    "description": "Detailed description with acceptance criteria",
    "priority": "high|medium|low",
    "estimated_hours": 8,
    "difficulty_rating": 3,
    "skills_required": ["skill1", "skill2"],
    "reasoning": "Why this task is important now"
  }}
]
"""
        return prompt
    
    def _create_performance_analysis_prompt(self, members: List, tasks: List, timeframe: str) -> str:
        """Create prompt for performance analysis"""
        prompt = f"""
Analyze team performance over the last {timeframe} based on the following data:

Team Members:
{self._format_team_members(members)}

Recent Tasks:
{self._format_recent_tasks(tasks)}

Provide analysis in the following areas:
1. Overall team productivity
2. Individual performance highlights
3. Areas for improvement
4. Specific recommendations
5. Workload distribution

Format your response as JSON with this structure:
{{
  "overall_score": 85,
  "productivity_trend": "improving|stable|declining",
  "key_insights": ["insight1", "insight2"],
  "individual_highlights": [
    {{"member": "username", "achievement": "description"}}
  ],
  "recommendations": ["recommendation1", "recommendation2"],
  "workload_balance": "balanced|uneven",
  "summary": "Brief overall summary"
}}
"""
        return prompt
    
    def _create_assignment_prompt(self, task_info: Dict, team_members: List) -> str:
        """Create prompt for task assignment"""
        prompt = f"""
Suggest the best team member to assign this task to:

Task Details:
- Title: {task_info.get('title', 'Unknown')}
- Description: {task_info.get('description', 'No description')}
- Priority: {task_info.get('priority', 'medium')}
- Estimated Hours: {task_info.get('estimated_hours', 8)}
- Skills Required: {task_info.get('skills_required', [])}

Available Team Members:
{self._format_team_members_for_assignment(team_members)}

Consider:
1. Current workload
2. Relevant skills/experience
3. Performance history
4. Task priority and urgency

Format response as JSON:
{{
  "recommended_member": "username",
  "confidence": 85,
  "reasoning": "Why this member is the best choice",
  "alternative": "backup_username",
  "workload_impact": "low|medium|high"
}}
"""
        return prompt
    
    def _format_current_tasks(self, tasks: List) -> str:
        """Format current tasks for prompt"""
        if not tasks:
            return "No current tasks"
        
        formatted = []
        for task in tasks[:5]:  # Limit to 5 tasks
            formatted.append(f"- {task.get('title', 'Unknown')}: {task.get('status', 'unknown')} ({task.get('priority', 'medium')} priority)")
        
        return "\n".join(formatted)
    
    def _format_team_members(self, members: List) -> str:
        """Format team members for prompt"""
        if not members:
            return "No team members"
        
        formatted = []
        for member in members:
            formatted.append(
                f"- {member.get('username', 'Unknown')}: "
                f"{member.get('total_tasks_completed', 0)} tasks completed, "
                f"{member.get('performance_score', 0):.1f}% performance score"
            )
        
        return "\n".join(formatted)
    
    def _format_recent_tasks(self, tasks: List) -> str:
        """Format recent tasks for prompt"""
        if not tasks:
            return "No recent tasks"
        
        formatted = []
        for task in tasks[:10]:  # Limit to 10 tasks
            status = task.get('status', 'unknown')
            assignee = task.get('assignee_info', {}).get('username', 'Unassigned')
            formatted.append(f"- {task.get('title', 'Unknown')}: {status} (assigned to {assignee})")
        
        return "\n".join(formatted)
    
    def _format_team_members_for_assignment(self, members: List) -> str:
        """Format team members for assignment prompt"""
        if not members:
            return "No team members available"
        
        formatted = []
        for member in members:
            workload = member.get('total_tasks_assigned', 0) - member.get('total_tasks_completed', 0)
            formatted.append(
                f"- {member.get('username', 'Unknown')}: "
                f"Current workload: {workload} tasks, "
                f"Performance: {member.get('performance_score', 0):.1f}%, "
                f"Avg completion time: {member.get('average_completion_time', 0):.1f}h"
            )
        
        return "\n".join(formatted)
    
    def _parse_task_response(self, content: str) -> List[Dict[str, Any]]:
        """Parse AI task generation response"""
        try:
            # Try to extract JSON from response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                tasks = json.loads(json_str)
                
                # Validate and clean tasks
                cleaned_tasks = []
                for task in tasks:
                    if isinstance(task, dict) and 'title' in task:
                        cleaned_task = {
                            'title': task.get('title', 'AI Generated Task'),
                            'description': task.get('description', 'No description provided'),
                            'priority': task.get('priority', 'medium'),
                            'estimated_hours': float(task.get('estimated_hours', 8)),
                            'difficulty_rating': int(task.get('difficulty_rating', 3)),
                            'ai_context': task.get('reasoning', 'AI generated task'),
                            'is_ai_generated': True
                        }
                        cleaned_tasks.append(cleaned_task)
                
                return cleaned_tasks
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing AI task response: {e}")
        
        return self._get_fallback_tasks()
    
    def _parse_performance_response(self, content: str) -> Dict[str, Any]:
        """Parse AI performance analysis response"""
        try:
            # Try to extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                analysis = json.loads(json_str)
                return analysis
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing AI performance response: {e}")
        
        return self._get_fallback_performance_analysis({})
    
    def _parse_assignment_response(self, content: str, team_members: List) -> Dict[str, Any]:
        """Parse AI assignment response"""
        try:
            # Try to extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                assignment = json.loads(json_str)
                
                # Validate recommended member exists
                recommended = assignment.get('recommended_member')
                if recommended and any(m.get('username') == recommended for m in team_members):
                    return assignment
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Error parsing AI assignment response: {e}")
        
        return self._get_fallback_assignment({}, team_members)
    
    def _get_fallback_tasks(self) -> List[Dict[str, Any]]:
        """Get fallback tasks when AI is unavailable"""
        return [
            {
                'title': 'Code Review and Optimization',
                'description': 'Review existing codebase for performance improvements and best practices',
                'priority': 'medium',
                'estimated_hours': 4.0,
                'difficulty_rating': 3,
                'ai_context': 'Fallback task - AI service unavailable',
                'is_ai_generated': False
            },
            {
                'title': 'Update Documentation',
                'description': 'Update project documentation and README files',
                'priority': 'low',
                'estimated_hours': 2.0,
                'difficulty_rating': 2,
                'ai_context': 'Fallback task - AI service unavailable',
                'is_ai_generated': False
            },
            {
                'title': 'Bug Investigation',
                'description': 'Investigate and fix reported bugs in the system',
                'priority': 'high',
                'estimated_hours': 6.0,
                'difficulty_rating': 4,
                'ai_context': 'Fallback task - AI service unavailable',
                'is_ai_generated': False
            }
        ]
    
    def _get_fallback_performance_analysis(self, team_data: Dict) -> Dict[str, Any]:
        """Get fallback performance analysis"""
        return {
            'overall_score': 75,
            'productivity_trend': 'stable',
            'key_insights': [
                'AI analysis unavailable - using basic metrics',
                'Team performance appears stable based on completion rates'
            ],
            'individual_highlights': [],
            'recommendations': [
                'Enable AI analysis by configuring OpenAI API key',
                'Continue monitoring task completion rates'
            ],
            'workload_balance': 'unknown',
            'summary': 'Basic analysis - AI service unavailable. Configure OpenAI API key for detailed insights.'
        }
    
    def _get_fallback_assignment(self, task_info: Dict, team_members: List) -> Dict[str, Any]:
        """Get fallback assignment suggestion"""
        if not team_members:
            return {
                'recommended_member': None,
                'confidence': 0,
                'reasoning': 'No team members available',
                'alternative': None,
                'workload_impact': 'unknown'
            }
        
        # Simple fallback: assign to member with lowest current workload
        best_member = min(team_members, key=lambda m: m.get('total_tasks_assigned', 0) - m.get('total_tasks_completed', 0))
        
        return {
            'recommended_member': best_member.get('username'),
            'confidence': 50,
            'reasoning': 'Assigned to member with lowest current workload (AI analysis unavailable)',
            'alternative': team_members[1].get('username') if len(team_members) > 1 else None,
            'workload_impact': 'medium'
        }

