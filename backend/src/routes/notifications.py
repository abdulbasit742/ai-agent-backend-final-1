"""
Notification Routes - Telegram Integration and Messaging
Handles Telegram notifications, bot status, and manual notification sending
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from ..models.user import User, db
from ..models.task import Task
from ..models.team_member import TeamMember
from ..services.telegram_service import telegram_service

notifications_bp = Blueprint('notifications', __name__)

def check_admin_access():
    """Check if current user is admin"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    return user and user.is_admin()

def get_current_user():
    """Get current user object"""
    user_id = get_jwt_identity()
    return User.query.get(user_id)

@notifications_bp.route('/telegram/status', methods=['GET'])
@jwt_required()
def get_telegram_status():
    """Get Telegram bot status and configuration"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Test bot connection
        is_connected = telegram_service.test_connection()
        bot_info = telegram_service.get_bot_info()
        
        status_data = {
            'connected': is_connected,
            'bot_token_configured': bool(telegram_service.bot_token),
            'default_chat_id_configured': bool(telegram_service.default_chat_id),
            'bot_info': bot_info,
            'last_check': datetime.utcnow().isoformat()
        }
        
        return jsonify(status_data), 200
        
    except Exception as e:
        print(f"❌ Get Telegram status error: {e}")
        return jsonify({'error': 'Failed to get Telegram status'}), 500

@notifications_bp.route('/telegram/test', methods=['POST'])
@jwt_required()
def test_telegram_notification():
    """Send a test Telegram notification"""
    try:
        current_user = get_current_user()
        if not current_user or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        chat_id = data.get('chat_id') or telegram_service.default_chat_id
        custom_message = data.get('message')
        
        if not chat_id:
            return jsonify({'error': 'No chat ID provided'}), 400
        
        # Create test message
        test_message = custom_message or f"""
🤖 *AI Agent System Test*

✅ *Connection Status:* Working
📅 *Test Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 *Tested by:* {current_user.username}

This is a test notification from your AI Agent System!
"""
        
        # Send notification
        success = telegram_service.send_message(chat_id, test_message.strip())
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Test notification sent successfully',
                'chat_id': chat_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send test notification'
            }), 500
        
    except Exception as e:
        print(f"❌ Test Telegram notification error: {e}")
        return jsonify({'error': 'Failed to send test notification'}), 500

@notifications_bp.route('/telegram/send-task-notification', methods=['POST'])
@jwt_required()
def send_task_notification():
    """Manually send task notification"""
    try:
        current_user = get_current_user()
        if not current_user or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        task_id = data.get('task_id')
        
        if not task_id:
            return jsonify({'error': 'Task ID is required'}), 400
        
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        if not task.assigned_member:
            return jsonify({'error': 'Task is not assigned to any team member'}), 400
        
        # Send notification
        success = telegram_service.send_task_assignment_notification(
            task.to_dict(),
            task.assigned_member.to_dict()
        )
        
        if success:
            task.telegram_notified = True
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Task notification sent successfully',
                'task_id': task_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send task notification'
            }), 500
        
    except Exception as e:
        print(f"❌ Send task notification error: {e}")
        return jsonify({'error': 'Failed to send task notification'}), 500

@notifications_bp.route('/telegram/send-performance-summary', methods=['POST'])
@jwt_required()
def send_performance_summary():
    """Send performance summary to team member"""
    try:
        current_user = get_current_user()
        if not current_user or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        team_member_id = data.get('team_member_id')
        
        if not team_member_id:
            return jsonify({'error': 'Team member ID is required'}), 400
        
        team_member = TeamMember.query.get(team_member_id)
        if not team_member:
            return jsonify({'error': 'Team member not found'}), 404
        
        # Update performance metrics
        team_member.update_performance_metrics()
        
        # Send performance summary
        success = telegram_service.send_performance_summary(
            team_member.to_dict(),
            team_member.get_performance_summary()
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Performance summary sent successfully',
                'team_member_id': team_member_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send performance summary'
            }), 500
        
    except Exception as e:
        print(f"❌ Send performance summary error: {e}")
        return jsonify({'error': 'Failed to send performance summary'}), 500

@notifications_bp.route('/telegram/send-daily-summary', methods=['POST'])
@jwt_required()
def send_daily_summary():
    """Send daily team summary"""
    try:
        current_user = get_current_user()
        if not current_user or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        # Gather daily statistics
        total_tasks = Task.query.count()
        completed_tasks = Task.query.filter_by(status='done').count()
        pending_tasks = Task.query.filter_by(status='pending').count()
        team_member_count = TeamMember.query.count()
        
        summary_data = {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'team_member_count': team_member_count
        }
        
        # Send daily summary
        success = telegram_service.send_daily_summary(summary_data)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Daily summary sent successfully',
                'summary': summary_data
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send daily summary'
            }), 500
        
    except Exception as e:
        print(f"❌ Send daily summary error: {e}")
        return jsonify({'error': 'Failed to send daily summary'}), 500

@notifications_bp.route('/telegram/send-urgent-alert', methods=['POST'])
@jwt_required()
def send_urgent_alert():
    """Send urgent task alert"""
    try:
        current_user = get_current_user()
        if not current_user or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        task_id = data.get('task_id')
        
        if not task_id:
            return jsonify({'error': 'Task ID is required'}), 400
        
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        if not task.assigned_member:
            return jsonify({'error': 'Task is not assigned to any team member'}), 400
        
        # Send urgent alert
        success = telegram_service.send_urgent_task_alert(
            task.to_dict(),
            task.assigned_member.to_dict()
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Urgent alert sent successfully',
                'task_id': task_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send urgent alert'
            }), 500
        
    except Exception as e:
        print(f"❌ Send urgent alert error: {e}")
        return jsonify({'error': 'Failed to send urgent alert'}), 500

@notifications_bp.route('/telegram/send-custom', methods=['POST'])
@jwt_required()
def send_custom_notification():
    """Send custom Telegram notification"""
    try:
        current_user = get_current_user()
        if not current_user or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        message = data.get('message', '').strip()
        chat_id = data.get('chat_id') or telegram_service.default_chat_id
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not chat_id:
            return jsonify({'error': 'Chat ID is required'}), 400
        
        # Add header to custom message
        formatted_message = f"""
📢 *Custom Notification*

{message}

📅 *Sent at:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
👤 *Sent by:* {current_user.username}
"""
        
        # Send notification
        success = telegram_service.send_message(chat_id, formatted_message.strip())
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Custom notification sent successfully',
                'chat_id': chat_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send custom notification'
            }), 500
        
    except Exception as e:
        print(f"❌ Send custom notification error: {e}")
        return jsonify({'error': 'Failed to send custom notification'}), 500

@notifications_bp.route('/telegram/update-chat-id', methods=['POST'])
@jwt_required()
def update_telegram_chat_id():
    """Update Telegram chat ID for team member"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        chat_id = data.get('chat_id', '').strip()
        
        if not chat_id:
            return jsonify({'error': 'Chat ID is required'}), 400
        
        # Update current user's team member profile
        if current_user.team_member:
            current_user.team_member.telegram_user_id = chat_id
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Telegram chat ID updated successfully',
                'chat_id': chat_id
            }), 200
        else:
            return jsonify({'error': 'No team member profile found'}), 404
        
    except Exception as e:
        print(f"❌ Update chat ID error: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update chat ID'}), 500

@notifications_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_notification_settings():
    """Get notification settings for current user"""
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        settings = {
            'telegram_configured': bool(telegram_service.bot_token),
            'user_chat_id': None,
            'notifications_enabled': False
        }
        
        if current_user.team_member:
            settings['user_chat_id'] = current_user.team_member.telegram_user_id
            settings['notifications_enabled'] = bool(current_user.team_member.telegram_user_id)
        
        return jsonify(settings), 200
        
    except Exception as e:
        print(f"❌ Get notification settings error: {e}")
        return jsonify({'error': 'Failed to get notification settings'}), 500

@notifications_bp.route('/history', methods=['GET'])
@jwt_required()
def get_notification_history():
    """Get notification history (placeholder for future implementation)"""
    try:
        current_user = get_current_user()
        if not current_user or not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        # This would typically query a notification_history table
        # For now, return placeholder data
        history = {
            'notifications': [],
            'total': 0,
            'message': 'Notification history feature coming soon'
        }
        
        return jsonify(history), 200
        
    except Exception as e:
        print(f"❌ Get notification history error: {e}")
        return jsonify({'error': 'Failed to get notification history'}), 500

