"""
Chat Routes - OpenAI API Integration
Compatible with Python 3.10 and openai==1.14.3
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db
from ..models.user import User
from ..models.task import Task
from ..services.chatgpt_service import ChatGPTService
from ..services.telegram_service import TelegramService

# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Initialize services
chatgpt_service = ChatGPTService()
telegram_service = TelegramService()

@chat_bp.route('/generate-tasks', methods=['POST'])
@jwt_required()
def generate_ai_tasks():
    """Generate AI-powered task suggestions"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        if not chatgpt_service.is_available():
            return jsonify({
                'status': 'error',
                'message': 'AI service not available. Please configure OpenAI API key.'
            }), 503
        
        data = request.get_json() or {}
        
        # Prepare context for AI
        context = {
            'project_context': data.get('project_context', 'General software development'),
            'team_info': _get_team_info(),
            'current_tasks': _get_current_tasks(),
            'performance_data': _get_performance_data()
        }
        
        # Generate tasks using AI
        ai_tasks = chatgpt_service.generate_task_suggestions(context)
        
        if not ai_tasks:
            return jsonify({
                'status': 'error',
                'message': 'Failed to generate AI tasks'
            }), 500
        
        # Optionally create tasks in database
        create_tasks = data.get('create_tasks', False)
        created_tasks = []
        
        if create_tasks:
            for ai_task in ai_tasks:
                # Get AI assignment suggestion
                team_members = User.query.filter_by(role='team', is_active=True).all()
                assignment_suggestion = chatgpt_service.suggest_task_assignment(
                    ai_task, 
                    [member.to_dict() for member in team_members]
                )
                
                # Create task
                task = Task(
                    title=ai_task['title'],
                    description=ai_task['description'],
                    priority=ai_task['priority'],
                    status='pending',
                    created_by=current_user_id,
                    estimated_hours=ai_task.get('estimated_hours', 8),
                    difficulty_rating=ai_task.get('difficulty_rating', 3),
                    is_ai_generated=True,
                    ai_context=ai_task.get('reasoning', 'AI generated task')
                )
                
                # Assign task if suggestion is confident enough
                if (assignment_suggestion.get('confidence', 0) > 70 and 
                    assignment_suggestion.get('recommended_member')):
                    
                    recommended_user = User.query.filter_by(
                        username=assignment_suggestion['recommended_member']
                    ).first()
                    
                    if recommended_user:
                        task.assigned_to = recommended_user.id
                        recommended_user.total_tasks_assigned += 1
                        recommended_user.updated_at = datetime.utcnow()
                
                db.session.add(task)
                db.session.flush()  # Get task ID
                created_tasks.append(task.to_dict())
                
                # Send assignment notification
                if task.assigned_to and telegram_service.is_available():
                    try:
                        assignee = User.query.get(task.assigned_to)
                        telegram_service.send_task_assignment_notification(
                            task.to_dict(),
                            assignee.to_dict()
                        )
                    except Exception as e:
                        print(f"Failed to send assignment notification: {e}")
            
            db.session.commit()
            
            # Send AI generation notification
            if telegram_service.is_available():
                try:
                    telegram_service.send_ai_task_generation_notification(
                        created_tasks,
                        context['project_context']
                    )
                except Exception as e:
                    print(f"Failed to send AI generation notification: {e}")
        
        return jsonify({
            'status': 'success',
            'message': f'Generated {len(ai_tasks)} AI task suggestions',
            'ai_tasks': ai_tasks,
            'created_tasks': created_tasks if create_tasks else [],
            'context_used': {
                'project_context': context['project_context'],
                'team_size': len(context['team_info'].get('members', [])),
                'current_tasks_count': len(context['current_tasks'])
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate AI tasks',
            'details': str(e)
        }), 500

@chat_bp.route('/analyze-performance', methods=['POST'])
@jwt_required()
def analyze_team_performance():
    """Analyze team performance using AI"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        if not chatgpt_service.is_available():
            return jsonify({
                'status': 'error',
                'message': 'AI service not available. Please configure OpenAI API key.'
            }), 503
        
        data = request.get_json() or {}
        timeframe = data.get('timeframe', '30 days')
        
        # Prepare team performance data
        team_data = {
            'members': _get_team_performance_data(timeframe),
            'tasks': _get_recent_tasks_data(timeframe),
            'timeframe': timeframe
        }
        
        # Analyze performance using AI
        analysis = chatgpt_service.analyze_team_performance(team_data)
        
        # Send performance report notification
        send_notification = data.get('send_notification', False)
        if send_notification and telegram_service.is_available():
            try:
                telegram_service.send_performance_report(analysis)
            except Exception as e:
                print(f"Failed to send performance report notification: {e}")
        
        return jsonify({
            'status': 'success',
            'message': 'Performance analysis completed',
            'analysis': analysis,
            'team_data_summary': {
                'members_analyzed': len(team_data['members']),
                'tasks_analyzed': len(team_data['tasks']),
                'timeframe': timeframe
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to analyze performance',
            'details': str(e)
        }), 500

@chat_bp.route('/suggest-assignment', methods=['POST'])
@jwt_required()
def suggest_task_assignment():
    """Get AI suggestion for task assignment"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        if not chatgpt_service.is_available():
            return jsonify({
                'status': 'error',
                'message': 'AI service not available. Please configure OpenAI API key.'
            }), 503
        
        data = request.get_json()
        if not data or 'task_info' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Task information is required'
            }), 400
        
        task_info = data['task_info']
        
        # Get team members
        team_members = User.query.filter_by(role='team', is_active=True).all()
        team_data = [member.to_dict() for member in team_members]
        
        # Get AI assignment suggestion
        suggestion = chatgpt_service.suggest_task_assignment(task_info, team_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Assignment suggestion generated',
            'suggestion': suggestion,
            'available_members': len(team_data)
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to suggest assignment',
            'details': str(e)
        }), 500

@chat_bp.route('/service-status', methods=['GET'])
@jwt_required()
def get_ai_service_status():
    """Get AI service status"""
    try:
        return jsonify({
            'status': 'success',
            'services': {
                'chatgpt': {
                    'available': chatgpt_service.is_available(),
                    'configured': bool(chatgpt_service.api_key)
                },
                'telegram': telegram_service.get_service_status()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get service status',
            'details': str(e)
        }), 500

@chat_bp.route('/test-services', methods=['POST'])
@jwt_required()
def test_ai_services():
    """Test AI services connectivity"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        results = {}
        
        # Test ChatGPT service
        if chatgpt_service.is_available():
            try:
                # Simple test generation
                test_context = {
                    'project_context': 'Test project',
                    'team_info': {'members': []},
                    'current_tasks': [],
                    'performance_data': {'average_score': 75}
                }
                test_tasks = chatgpt_service.generate_task_suggestions(test_context)
                results['chatgpt'] = {
                    'status': 'success',
                    'message': f'Generated {len(test_tasks)} test tasks',
                    'available': True
                }
            except Exception as e:
                results['chatgpt'] = {
                    'status': 'error',
                    'message': f'ChatGPT test failed: {str(e)}',
                    'available': False
                }
        else:
            results['chatgpt'] = {
                'status': 'error',
                'message': 'ChatGPT service not configured',
                'available': False
            }
        
        # Test Telegram service
        telegram_test = telegram_service.test_connection()
        results['telegram'] = telegram_test
        
        return jsonify({
            'status': 'success',
            'message': 'Service tests completed',
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to test services',
            'details': str(e)
        }), 500

# Helper functions
def _get_team_info():
    """Get team information for AI context"""
    team_members = User.query.filter_by(role='team', is_active=True).all()
    return {
        'members': [member.to_dict() for member in team_members]
    }

def _get_current_tasks():
    """Get current tasks for AI context"""
    current_tasks = Task.query.filter(
        Task.status.in_(['pending', 'in_progress'])
    ).order_by(Task.created_at.desc()).limit(10).all()
    
    return [task.to_dict() for task in current_tasks]

def _get_performance_data():
    """Get performance data for AI context"""
    team_members = User.query.filter_by(role='team', is_active=True).all()
    
    if not team_members:
        return {'average_score': 75}
    
    total_score = sum(member.performance_score for member in team_members)
    average_score = total_score / len(team_members)
    
    return {
        'average_score': round(average_score, 1),
        'team_size': len(team_members)
    }

def _get_team_performance_data(timeframe):
    """Get team performance data for analysis"""
    # Parse timeframe
    days = 30
    if 'day' in timeframe:
        days = int(timeframe.split()[0]) if timeframe.split()[0].isdigit() else 30
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    team_members = User.query.filter_by(role='team', is_active=True).all()
    performance_data = []
    
    for member in team_members:
        # Get recent tasks
        recent_tasks = Task.query.filter(
            Task.assigned_to == member.id,
            Task.created_at >= cutoff_date
        ).all()
        
        completed_tasks = [t for t in recent_tasks if t.status == 'completed']
        
        performance_data.append({
            'username': member.username,
            'total_tasks_assigned': len(recent_tasks),
            'total_tasks_completed': len(completed_tasks),
            'performance_score': member.performance_score,
            'average_completion_time': member.average_completion_time,
            'recent_activity': len(recent_tasks)
        })
    
    return performance_data

def _get_recent_tasks_data(timeframe):
    """Get recent tasks data for analysis"""
    # Parse timeframe
    days = 30
    if 'day' in timeframe:
        days = int(timeframe.split()[0]) if timeframe.split()[0].isdigit() else 30
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    recent_tasks = Task.query.filter(
        Task.created_at >= cutoff_date
    ).order_by(Task.created_at.desc()).all()
    
    tasks_data = []
    for task in recent_tasks:
        task_dict = task.to_dict()
        # Add assignee info
        if task.assigned_to:
            assignee = User.query.get(task.assigned_to)
            if assignee:
                task_dict['assignee_info'] = {
                    'username': assignee.username,
                    'performance_score': assignee.performance_score
                }
        tasks_data.append(task_dict)
    
    return tasks_data

