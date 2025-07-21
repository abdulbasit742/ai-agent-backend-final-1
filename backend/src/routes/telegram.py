"""
Telegram Routes - Telegram Bot API Integration
Compatible with Python 3.10
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db
from ..models.user import User
from ..models.task import Task
from ..services.telegram_service import TelegramService

# Create blueprint
telegram_bp = Blueprint('telegram', __name__)

# Initialize service
telegram_service = TelegramService()

@telegram_bp.route('/status', methods=['GET'])
@jwt_required()
def get_telegram_status():
    """Get Telegram service status"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        service_status = telegram_service.get_service_status()
        
        return jsonify({
            'status': 'success',
            'telegram_service': service_status
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get Telegram status',
            'details': str(e)
        }), 500

@telegram_bp.route('/test', methods=['POST'])
@jwt_required()
def test_telegram_connection():
    """Test Telegram bot connection"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        if not telegram_service.is_available():
            return jsonify({
                'status': 'error',
                'message': 'Telegram service not configured'
            }), 503
        
        # Test connection
        test_result = telegram_service.test_connection()
        
        if test_result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Telegram connection successful',
                'bot_info': test_result.get('bot_info', {}),
                'test_result': test_result
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Telegram connection failed',
                'error': test_result.get('error'),
                'details': test_result.get('message')
            }), 503
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to test Telegram connection',
            'details': str(e)
        }), 500

@telegram_bp.route('/send-message', methods=['POST'])
@jwt_required()
def send_custom_message():
    """Send custom message via Telegram"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        if not telegram_service.is_available():
            return jsonify({
                'status': 'error',
                'message': 'Telegram service not configured'
            }), 503
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Message content is required'
            }), 400
        
        message = data['message']
        title = data.get('title', 'Custom Message')
        emoji = data.get('emoji', '📢')
        
        # Send message
        result = telegram_service.send_custom_message(title, message, emoji)
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Message sent successfully',
                'telegram_result': result
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send message',
                'error': result.get('error'),
                'details': result.get('details')
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to send custom message',
            'details': str(e)
        }), 500

@telegram_bp.route('/notify-task-assignment', methods=['POST'])
@jwt_required()
def notify_task_assignment():
    """Send task assignment notification"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        if not telegram_service.is_available():
            return jsonify({
                'status': 'error',
                'message': 'Telegram service not configured'
            }), 503
        
        data = request.get_json()
        if not data or 'task_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Task ID is required'
            }), 400
        
        task_id = data['task_id']
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        if not task.assigned_to:
            return jsonify({
                'status': 'error',
                'message': 'Task is not assigned to anyone'
            }), 400
        
        assignee = User.query.get(task.assigned_to)
        if not assignee:
            return jsonify({
                'status': 'error',
                'message': 'Assignee not found'
            }), 404
        
        # Send notification
        result = telegram_service.send_task_assignment_notification(
            task.to_dict(),
            assignee.to_dict()
        )
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Task assignment notification sent',
                'telegram_result': result
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send notification',
                'error': result.get('error'),
                'details': result.get('details')
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to send task assignment notification',
            'details': str(e)
        }), 500

@telegram_bp.route('/notify-task-completion', methods=['POST'])
@jwt_required()
def notify_task_completion():
    """Send task completion notification"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        data = request.get_json()
        if not data or 'task_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Task ID is required'
            }), 400
        
        task_id = data['task_id']
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        # Check permissions
        if not current_user.is_admin() and task.assigned_to != current_user_id:
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        if not telegram_service.is_available():
            return jsonify({
                'status': 'error',
                'message': 'Telegram service not configured'
            }), 503
        
        if not task.assigned_to:
            return jsonify({
                'status': 'error',
                'message': 'Task is not assigned to anyone'
            }), 400
        
        assignee = User.query.get(task.assigned_to)
        if not assignee:
            return jsonify({
                'status': 'error',
                'message': 'Assignee not found'
            }), 404
        
        # Send notification
        result = telegram_service.send_task_completion_notification(
            task.to_dict(),
            assignee.to_dict()
        )
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Task completion notification sent',
                'telegram_result': result
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send notification',
                'error': result.get('error'),
                'details': result.get('details')
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to send task completion notification',
            'details': str(e)
        }), 500

@telegram_bp.route('/send-performance-report', methods=['POST'])
@jwt_required()
def send_performance_report():
    """Send performance report via Telegram"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        if not telegram_service.is_available():
            return jsonify({
                'status': 'error',
                'message': 'Telegram service not configured'
            }), 503
        
        data = request.get_json() or {}
        timeframe = data.get('timeframe', '30 days')
        
        # Generate performance report data
        report_data = _generate_performance_report(timeframe)
        
        # Send report
        result = telegram_service.send_performance_report(report_data)
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': 'Performance report sent successfully',
                'report_data': report_data,
                'telegram_result': result
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send performance report',
                'error': result.get('error'),
                'details': result.get('details')
            }), 500
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to send performance report',
            'details': str(e)
        }), 500

@telegram_bp.route('/notifications/settings', methods=['GET', 'PUT'])
@jwt_required()
def notification_settings():
    """Get or update notification settings"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        if request.method == 'GET':
            # Return current settings (for now, just service status)
            return jsonify({
                'status': 'success',
                'settings': {
                    'telegram_enabled': telegram_service.is_available(),
                    'auto_assignment_notifications': True,
                    'auto_completion_notifications': True,
                    'performance_reports': True,
                    'ai_task_notifications': True
                }
            }), 200
        
        elif request.method == 'PUT':
            # Update settings (placeholder for future implementation)
            data = request.get_json() or {}
            
            return jsonify({
                'status': 'success',
                'message': 'Notification settings updated',
                'settings': data
            }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to handle notification settings',
            'details': str(e)
        }), 500

@telegram_bp.route('/history', methods=['GET'])
@jwt_required()
def get_notification_history():
    """Get notification history (placeholder)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        # Placeholder for notification history
        # In a real implementation, you'd store notification logs in the database
        history = [
            {
                'id': 1,
                'type': 'task_assignment',
                'message': 'Task assigned to john_doe',
                'timestamp': datetime.utcnow().isoformat(),
                'status': 'sent'
            },
            {
                'id': 2,
                'type': 'task_completion',
                'message': 'Task completed by jane_smith',
                'timestamp': (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                'status': 'sent'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'history': history,
            'total': len(history)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get notification history',
            'details': str(e)
        }), 500

# Helper functions
def _generate_performance_report(timeframe):
    """Generate performance report data"""
    # Parse timeframe
    days = 30
    if 'day' in timeframe:
        days = int(timeframe.split()[0]) if timeframe.split()[0].isdigit() else 30
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Get team statistics
    team_members = User.query.filter_by(role='team', is_active=True).all()
    total_tasks = Task.query.filter(Task.created_at >= cutoff_date).count()
    completed_tasks = Task.query.filter(
        Task.created_at >= cutoff_date,
        Task.status == 'completed'
    ).count()
    
    # Calculate overall performance
    overall_score = 0
    if team_members:
        total_score = sum(member.performance_score for member in team_members)
        overall_score = total_score / len(team_members)
    
    # Determine trend (simplified)
    productivity_trend = 'stable'
    if overall_score > 80:
        productivity_trend = 'improving'
    elif overall_score < 60:
        productivity_trend = 'declining'
    
    # Generate insights
    key_insights = []
    if completed_tasks > 0:
        completion_rate = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        key_insights.append(f"Task completion rate: {completion_rate:.1f}%")
    
    if team_members:
        key_insights.append(f"Team size: {len(team_members)} active members")
        
        # Find top performer
        top_performer = max(team_members, key=lambda m: m.performance_score)
        key_insights.append(f"Top performer: {top_performer.username} ({top_performer.performance_score:.1f}%)")
    
    return {
        'timeframe': timeframe,
        'overall_score': round(overall_score, 1),
        'productivity_trend': productivity_trend,
        'key_insights': key_insights,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'team_size': len(team_members)
    }

