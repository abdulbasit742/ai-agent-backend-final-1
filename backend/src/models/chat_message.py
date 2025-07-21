"""
Chat Message Model - AI Interaction Tracking
Handles ChatGPT interactions, task generation requests, and AI reasoning storage
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .user import db

class ChatMessage(db.Model):
    """Chat message model for AI interaction tracking"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_type = db.Column(db.String(50), nullable=False)  # 'task_generation', 'query', 'system'
    
    # Message content
    user_message = db.Column(db.Text)  # User's input/request
    ai_response = db.Column(db.Text)   # AI's response
    context = db.Column(db.Text)       # Additional context (JSON string)
    
    # AI model information
    model_used = db.Column(db.String(50), default='gpt-3.5-turbo')
    tokens_used = db.Column(db.Integer, default=0)
    
    # Task generation specific
    generated_tasks_count = db.Column(db.Integer, default=0)
    task_ids = db.Column(db.Text)  # JSON array of generated task IDs
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    # Status tracking
    status = db.Column(db.String(20), default='pending')  # 'pending', 'processed', 'failed'
    error_message = db.Column(db.Text)
    
    def __init__(self, user_id, message_type, user_message=None, context=None):
        self.user_id = user_id
        self.message_type = message_type
        self.user_message = user_message
        self.context = context
    
    def mark_processed(self, ai_response, tokens_used=0, generated_tasks_count=0, task_ids=None):
        """Mark message as processed with AI response"""
        self.ai_response = ai_response
        self.tokens_used = tokens_used
        self.generated_tasks_count = generated_tasks_count
        self.task_ids = task_ids
        self.status = 'processed'
        self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def mark_failed(self, error_message):
        """Mark message as failed with error"""
        self.status = 'failed'
        self.error_message = error_message
        self.processed_at = datetime.utcnow()
        db.session.commit()
    
    def get_processing_time(self):
        """Get processing time in seconds"""
        if self.processed_at and self.created_at:
            delta = self.processed_at - self.created_at
            return delta.total_seconds()
        return None
    
    def to_dict(self):
        """Convert chat message to dictionary for JSON response"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'message_type': self.message_type,
            'user_message': self.user_message,
            'ai_response': self.ai_response,
            'context': self.context,
            'model_used': self.model_used,
            'tokens_used': self.tokens_used,
            'generated_tasks_count': self.generated_tasks_count,
            'task_ids': self.task_ids,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'processing_time': self.get_processing_time()
        }
    
    @staticmethod
    def get_recent_task_generations(limit=10):
        """Get recent task generation messages"""
        return ChatMessage.query.filter_by(
            message_type='task_generation'
        ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_ai_usage_stats():
        """Get AI usage statistics"""
        total_messages = ChatMessage.query.count()
        successful_messages = ChatMessage.query.filter_by(status='processed').count()
        failed_messages = ChatMessage.query.filter_by(status='failed').count()
        total_tokens = db.session.query(db.func.sum(ChatMessage.tokens_used)).scalar() or 0
        total_tasks_generated = db.session.query(db.func.sum(ChatMessage.generated_tasks_count)).scalar() or 0
        
        return {
            'total_messages': total_messages,
            'successful_messages': successful_messages,
            'failed_messages': failed_messages,
            'success_rate': round((successful_messages / total_messages) * 100, 1) if total_messages > 0 else 0,
            'total_tokens_used': total_tokens,
            'total_tasks_generated': total_tasks_generated,
            'average_tokens_per_message': round(total_tokens / successful_messages, 1) if successful_messages > 0 else 0
        }
    
    def __repr__(self):
        return f'<ChatMessage {self.message_type} by User {self.user_id}>'

