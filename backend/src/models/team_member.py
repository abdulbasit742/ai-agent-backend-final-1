"""
Team Member Model - Performance Tracking and Management
Handles team member profiles, performance metrics, and efficiency calculations
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class TeamMember(db.Model):
    """Team member model for performance tracking"""
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    telegram_user_id = db.Column(db.String(50))  # Telegram user ID for notifications
    
    # Performance metrics
    efficiency_rating = db.Column(db.Float, default=0.0)  # Percentage (0-100)
    tasks_completed = db.Column(db.Integer, default=0)
    tasks_assigned = db.Column(db.Integer, default=0)
    total_work_hours = db.Column(db.Float, default=0.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_task_completed = db.Column(db.DateTime)
    
    # Relationships
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assigned_to', backref='assigned_member', lazy='dynamic')
    
    def __init__(self, user_id, name, telegram_user_id=None):
        self.user_id = user_id
        self.name = name
        self.telegram_user_id = telegram_user_id
    
    def calculate_efficiency(self):
        """Calculate efficiency rating based on completed tasks"""
        if self.tasks_assigned == 0:
            return 0.0
        
        completion_rate = (self.tasks_completed / self.tasks_assigned) * 100
        
        # Factor in overdue tasks (penalty)
        overdue_tasks = self.get_overdue_tasks_count()
        overdue_penalty = min(overdue_tasks * 5, 20)  # Max 20% penalty
        
        # Factor in recent activity (bonus)
        recent_bonus = self.get_recent_activity_bonus()
        
        efficiency = max(0, min(100, completion_rate - overdue_penalty + recent_bonus))
        return round(efficiency, 1)
    
    def get_overdue_tasks_count(self):
        """Get count of overdue tasks for this team member"""
        from .task import Task
        return Task.query.filter(
            Task.assigned_to == self.id,
            Task.due_date < datetime.utcnow(),
            Task.status != 'done'
        ).count()
    
    def get_recent_activity_bonus(self):
        """Get bonus points for recent task completion"""
        if not self.last_task_completed:
            return 0
        
        days_since_last = (datetime.utcnow() - self.last_task_completed).days
        if days_since_last <= 1:
            return 10  # 10% bonus for completing task within 24 hours
        elif days_since_last <= 3:
            return 5   # 5% bonus for completing task within 3 days
        return 0
    
    def update_performance_metrics(self):
        """Update all performance metrics"""
        # Count tasks
        self.tasks_assigned = self.assigned_tasks.count()
        self.tasks_completed = self.assigned_tasks.filter_by(status='done').count()
        
        # Update efficiency
        self.efficiency_rating = self.calculate_efficiency()
        
        # Update last task completed
        last_completed_task = self.assigned_tasks.filter_by(status='done').order_by(
            'completed_at desc'
        ).first()
        if last_completed_task and last_completed_task.completed_at:
            self.last_task_completed = last_completed_task.completed_at
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def get_workload_score(self):
        """Get current workload score for intelligent task assignment"""
        pending_tasks = self.assigned_tasks.filter_by(status='pending').count()
        in_progress_tasks = self.assigned_tasks.filter_by(status='in_progress').count()
        
        # Weight in-progress tasks more heavily
        workload_score = pending_tasks + (in_progress_tasks * 1.5)
        
        # Factor in efficiency (higher efficiency = can handle more tasks)
        efficiency_factor = self.efficiency_rating / 100
        adjusted_score = workload_score / max(efficiency_factor, 0.1)  # Avoid division by zero
        
        return round(adjusted_score, 2)
    
    def get_task_completion_rate(self):
        """Get task completion rate as percentage"""
        if self.tasks_assigned == 0:
            return 0.0
        return round((self.tasks_completed / self.tasks_assigned) * 100, 1)
    
    def get_performance_summary(self):
        """Get comprehensive performance summary"""
        return {
            'efficiency_rating': self.efficiency_rating,
            'completion_rate': self.get_task_completion_rate(),
            'tasks_completed': self.tasks_completed,
            'tasks_assigned': self.tasks_assigned,
            'overdue_tasks': self.get_overdue_tasks_count(),
            'workload_score': self.get_workload_score(),
            'last_activity': self.last_task_completed.isoformat() if self.last_task_completed else None
        }
    
    def to_dict(self):
        """Convert team member to dictionary for JSON response"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'username': self.user.username if self.user else None,
            'telegram_user_id': self.telegram_user_id,
            'efficiency_rating': self.efficiency_rating,
            'tasks_completed': self.tasks_completed,
            'tasks_assigned': self.tasks_assigned,
            'completion_rate': self.get_task_completion_rate(),
            'workload_score': self.get_workload_score(),
            'overdue_tasks': self.get_overdue_tasks_count(),
            'total_work_hours': self.total_work_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_task_completed': self.last_task_completed.isoformat() if self.last_task_completed else None,
            'performance_summary': self.get_performance_summary()
        }
    
    @staticmethod
    def get_best_assignee_for_task(task_priority='medium'):
        """Get the best team member to assign a task to based on workload and efficiency"""
        team_members = TeamMember.query.all()
        
        if not team_members:
            return None
        
        # Score each team member
        scored_members = []
        for member in team_members:
            # Update metrics first
            member.update_performance_metrics()
            
            # Calculate assignment score (lower is better)
            workload_score = member.get_workload_score()
            efficiency_bonus = member.efficiency_rating / 10  # Convert to 0-10 scale
            
            # Priority factor (urgent tasks go to high-efficiency members)
            priority_factor = 1.0
            if task_priority == 'urgent' and member.efficiency_rating < 70:
                priority_factor = 2.0  # Penalty for low-efficiency members on urgent tasks
            
            final_score = (workload_score * priority_factor) - efficiency_bonus
            
            scored_members.append((member, final_score))
        
        # Sort by score (lowest first) and return best candidate
        scored_members.sort(key=lambda x: x[1])
        return scored_members[0][0] if scored_members else None
    
    def __repr__(self):
        return f'<TeamMember {self.name}>'

