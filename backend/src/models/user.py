"""
User Model - Authentication and User Management
Compatible with Python 3.10 and SQLAlchemy 2.0
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    """User model for authentication and user management"""
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # User information
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role and status
    role = db.Column(db.String(20), nullable=False, default='team')  # 'admin' or 'team'
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Performance tracking
    total_tasks_assigned = db.Column(db.Integer, default=0)
    total_tasks_completed = db.Column(db.Integer, default=0)
    average_completion_time = db.Column(db.Float, default=0.0)  # in hours
    performance_score = db.Column(db.Float, default=0.0)  # 0-100 scale
    
    def __init__(self, username, email, role='team'):
        """Initialize user"""
        self.username = username
        self.email = email
        self.role = role
        self.is_active = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_team_member(self):
        """Check if user is team member"""
        return self.role == 'team'
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def calculate_performance_score(self):
        """Calculate performance score based on task completion"""
        if self.total_tasks_assigned == 0:
            return 0.0
        
        completion_rate = (self.total_tasks_completed / self.total_tasks_assigned) * 100
        
        # Factor in average completion time (lower is better)
        time_factor = 1.0
        if self.average_completion_time > 0:
            # Normalize time factor (assuming 24 hours is baseline)
            time_factor = max(0.1, min(1.0, 24 / self.average_completion_time))
        
        # Calculate final score (0-100)
        score = completion_rate * time_factor
        self.performance_score = min(100.0, max(0.0, score))
        
        return self.performance_score
    
    def update_task_stats(self, task_completed=False, completion_time_hours=None):
        """Update task statistics"""
        if task_completed:
            self.total_tasks_completed += 1
            
            if completion_time_hours is not None:
                # Update average completion time
                if self.total_tasks_completed == 1:
                    self.average_completion_time = completion_time_hours
                else:
                    # Calculate weighted average
                    total_time = (self.average_completion_time * (self.total_tasks_completed - 1)) + completion_time_hours
                    self.average_completion_time = total_time / self.total_tasks_completed
        
        # Recalculate performance score
        self.calculate_performance_score()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'total_tasks_assigned': self.total_tasks_assigned,
            'total_tasks_completed': self.total_tasks_completed,
            'average_completion_time': self.average_completion_time,
            'performance_score': self.performance_score
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    def __repr__(self):
        """String representation"""
        return f'<User {self.username} ({self.role})>'

