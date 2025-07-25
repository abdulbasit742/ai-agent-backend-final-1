"""Task Model - Task Management and Tracking
Compatible with Python 3.10+ and SQLAlchemy 2.0
"""

from datetime import datetime, timedelta, timezone
from . import db

class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), nullable=False, default='medium')
    status = db.Column(db.String(20), nullable=False, default='pending')

    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    due_date = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    is_ai_generated = db.Column(db.Boolean, default=False, nullable=False)
    ai_context = db.Column(db.Text)

    estimated_hours = db.Column(db.Float, default=0.0)
    actual_hours = db.Column(db.Float, default=0.0)
    difficulty_rating = db.Column(db.Integer, default=3)

    def __init__(self, title, description=None, priority='medium', status='pending',
                 assigned_to=None, created_by=None, due_date=None, is_ai_generated=False,
                 ai_context=None, estimated_hours=0.0, difficulty_rating=3,
                 started_at=None, completed_at=None, actual_hours=0.0):
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.assigned_to = assigned_to
        self.created_by = created_by
        self.due_date = due_date
        self.is_ai_generated = is_ai_generated
        self.ai_context = ai_context
        self.estimated_hours = estimated_hours
        self.difficulty_rating = difficulty_rating
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.started_at = started_at
        self.completed_at = completed_at
        self.actual_hours = actual_hours

    @property
    def priority_emoji(self):
        return {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'urgent': '🔴'
        }.get(self.priority, '🟡')

    @property
    def status_emoji(self):
        return {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅'
        }.get(self.status, '⏳')

    @property
    def is_overdue(self):
        if not self.due_date or self.status == 'completed':
            return False
        return datetime.now(timezone.utc) > self.due_date

    @property
    def days_until_due(self):
        if not self.due_date:
            return None
        delta = self.due_date - datetime.now(timezone.utc)
        return delta.days

    @property
    def duration_hours(self):
        if not self.started_at:
            return 0.0
        end_time = self.completed_at or datetime.now(timezone.utc)
        delta = end_time - self.started_at
        return round(delta.total_seconds() / 3600, 2)

    def start_task(self):
        if self.status == 'pending':
            self.status = 'in_progress'
            self.started_at = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False

    def complete_task(self):
        if self.status in ['pending', 'in_progress']:
            if self.status == 'pending':
                self.started_at = datetime.now(timezone.utc)
            self.status = 'completed'
            self.completed_at = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)
            if self.started_at:
                self.actual_hours = self.duration_hours
            return True
        return False

    def update_status(self, new_status):
        old_status = self.status
        if new_status == 'in_progress' and old_status == 'pending':
            self.start_task()
        elif new_status == 'completed' and old_status in ['pending', 'in_progress']:
            self.complete_task()
        elif new_status == 'pending' and old_status in ['in_progress', 'completed']:
            self.status = 'pending'
            self.started_at = None
            self.completed_at = None
            self.actual_hours = 0.0
            self.updated_at = datetime.now(timezone.utc)
        else:
            self.status = new_status
            self.updated_at = datetime.now(timezone.utc)
        return old_status != new_status

    def assign_to_user(self, user_id):
        self.assigned_to = user_id
        self.updated_at = datetime.now(timezone.utc)

    def get_assignee_info(self):
        if not self.assigned_to:
            return None
        from .user import User
        user = User.query.get(self.assigned_to)
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        } if user else None

    def get_creator_info(self):
        if not self.created_by:
            return None
        from .user import User
        user = User.query.get(self.created_by)
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        } if user else None

    def calculate_completion_score(self):
        score = 0.0
        if self.status == 'completed':
            score += 50.0
            if not self.is_overdue:
                score += 20.0
            if self.estimated_hours > 0 and self.actual_hours > 0:
                efficiency = self.estimated_hours / self.actual_hours
                if efficiency >= 1.0:
                    score += min(20.0, efficiency * 10.0)
            score += self.difficulty_rating * 2.0
        elif self.status == 'in_progress':
            score += 25.0
            if self.is_overdue:
                score -= 10.0
        return min(100.0, max(0.0, score))

    def to_dict(self, include_relations=True):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'priority_emoji': self.priority_emoji,
            'status': self.status,
            'status_emoji': self.status_emoji,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'is_ai_generated': self.is_ai_generated,
            'ai_context': self.ai_context,
            'estimated_hours': self.estimated_hours,
            'actual_hours': self.actual_hours,
            'duration_hours': self.duration_hours,
            'difficulty_rating': self.difficulty_rating,
            'is_overdue': self.is_overdue,
            'days_until_due': self.days_until_due,
            'completion_score': self.calculate_completion_score()
        }

        if include_relations:
            data['assignee_info'] = self.get_assignee_info()
            data['creator_info'] = self.get_creator_info()

        return data

    @staticmethod
    def get_priority_order():
        return ['urgent', 'high', 'medium', 'low']

    @staticmethod
    def get_status_order():
        return ['pending', 'in_progress', 'completed']

    def __repr__(self):
        return f'<Task {self.id}: {self.title} ({self.status})>'
