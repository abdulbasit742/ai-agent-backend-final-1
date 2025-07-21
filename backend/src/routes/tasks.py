"""
Task Routes - CRUD Task Management
Compatible with Python 3.10 and Flask-JWT-Extended
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, desc, asc
from ..models import db
from ..models.user import User
from ..models.task import Task
from ..services.telegram_service import TelegramService

# Create blueprint
tasks_bp = Blueprint('tasks', __name__)

# Initialize services
telegram_service = TelegramService()

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get tasks with filtering and pagination"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status')
        priority_filter = request.args.get('priority')
        assigned_to_filter = request.args.get('assigned_to', type=int)
        created_by_filter = request.args.get('created_by', type=int)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
        query = Task.query
        
        # Apply filters based on user role
        if not current_user.is_admin():
            # Team members can only see tasks assigned to them or created by them
            query = query.filter(
                (Task.assigned_to == current_user_id) | 
                (Task.created_by == current_user_id)
            )
        
        # Apply additional filters
        if status_filter:
            query = query.filter(Task.status == status_filter)
        
        if priority_filter:
            query = query.filter(Task.priority == priority_filter)
        
        if assigned_to_filter:
            query = query.filter(Task.assigned_to == assigned_to_filter)
        
        if created_by_filter:
            query = query.filter(Task.created_by == created_by_filter)
        
        # Apply sorting
        if hasattr(Task, sort_by):
            sort_column = getattr(Task, sort_by)
            if sort_order == 'asc':
                query = query.order_by(asc(sort_column))
            else:
                query = query.order_by(desc(sort_column))
        
        # Paginate results
        tasks = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'tasks': [task.to_dict() for task in tasks.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': tasks.total,
                'pages': tasks.pages,
                'has_next': tasks.has_next,
                'has_prev': tasks.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get tasks',
            'details': str(e)
        }), 500

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get specific task"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        task = Task.query.get(task_id)
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        # Check access permissions
        if not current_user.is_admin():
            if task.assigned_to != current_user_id and task.created_by != current_user_id:
                return jsonify({
                    'status': 'error',
                    'message': 'Access denied'
                }), 403
        
        return jsonify({
            'status': 'success',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get task',
            'details': str(e)
        }), 500

@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create new task"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        title = data.get('title')
        if not title:
            return jsonify({
                'status': 'error',
                'message': 'Task title is required'
            }), 400
        
        # Parse due date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid due date format'
                }), 400
        
        # Create task
        task = Task(
            title=title,
            description=data.get('description', ''),
            priority=data.get('priority', 'medium'),
            status=data.get('status', 'pending'),
            assigned_to=data.get('assigned_to'),
            created_by=current_user_id,
            due_date=due_date,
            estimated_hours=float(data.get('estimated_hours', 0)),
            difficulty_rating=int(data.get('difficulty_rating', 3)),
            is_ai_generated=data.get('is_ai_generated', False),
            ai_context=data.get('ai_context')
        )
        
        db.session.add(task)
        db.session.flush()  # Get task ID
        
        # Update assignee task count
        if task.assigned_to:
            assignee = User.query.get(task.assigned_to)
            if assignee:
                assignee.total_tasks_assigned += 1
                assignee.updated_at = datetime.utcnow()
                
                # Send Telegram notification
                if telegram_service.is_available():
                    try:
                        telegram_service.send_task_assignment_notification(
                            task.to_dict(),
                            assignee.to_dict()
                        )
                    except Exception as e:
                        print(f"Failed to send Telegram notification: {e}")
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create task',
            'details': str(e)
        }), 500

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update task"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        task = Task.query.get(task_id)
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        # Check permissions
        can_edit = (
            current_user.is_admin() or 
            task.created_by == current_user_id or 
            task.assigned_to == current_user_id
        )
        
        if not can_edit:
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        # Store old values for notifications
        old_status = task.status
        old_assigned_to = task.assigned_to
        
        # Update fields
        if 'title' in data:
            task.title = data['title']
        
        if 'description' in data:
            task.description = data['description']
        
        if 'priority' in data:
            task.priority = data['priority']
        
        if 'status' in data:
            new_status = data['status']
            if task.update_status(new_status):
                # Status changed, handle completion tracking
                if new_status == 'completed' and old_status != 'completed':
                    # Task completed
                    if task.assigned_to:
                        assignee = User.query.get(task.assigned_to)
                        if assignee:
                            completion_time = task.duration_hours
                            assignee.update_task_stats(
                                task_completed=True,
                                completion_time_hours=completion_time
                            )
                            
                            # Send completion notification
                            if telegram_service.is_available():
                                try:
                                    telegram_service.send_task_completion_notification(
                                        task.to_dict(),
                                        assignee.to_dict()
                                    )
                                except Exception as e:
                                    print(f"Failed to send completion notification: {e}")
                
                elif old_status == 'completed' and new_status != 'completed':
                    # Task uncompleted
                    if task.assigned_to:
                        assignee = User.query.get(task.assigned_to)
                        if assignee and assignee.total_tasks_completed > 0:
                            assignee.total_tasks_completed -= 1
                            assignee.calculate_performance_score()
                            assignee.updated_at = datetime.utcnow()
        
        if 'assigned_to' in data:
            new_assigned_to = data['assigned_to']
            if new_assigned_to != old_assigned_to:
                # Update old assignee stats
                if old_assigned_to:
                    old_assignee = User.query.get(old_assigned_to)
                    if old_assignee and old_assignee.total_tasks_assigned > 0:
                        old_assignee.total_tasks_assigned -= 1
                        old_assignee.updated_at = datetime.utcnow()
                
                # Update new assignee stats
                if new_assigned_to:
                    new_assignee = User.query.get(new_assigned_to)
                    if new_assignee:
                        new_assignee.total_tasks_assigned += 1
                        new_assignee.updated_at = datetime.utcnow()
                        
                        # Send assignment notification
                        if telegram_service.is_available():
                            try:
                                telegram_service.send_task_assignment_notification(
                                    task.to_dict(),
                                    new_assignee.to_dict()
                                )
                            except Exception as e:
                                print(f"Failed to send assignment notification: {e}")
                
                task.assigned_to = new_assigned_to
        
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({
                        'status': 'error',
                        'message': 'Invalid due date format'
                    }), 400
            else:
                task.due_date = None
        
        if 'estimated_hours' in data:
            task.estimated_hours = float(data['estimated_hours'])
        
        if 'difficulty_rating' in data:
            task.difficulty_rating = int(data['difficulty_rating'])
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Send status update notification if status changed
        if old_status != task.status and task.assigned_to:
            assignee = User.query.get(task.assigned_to)
            if assignee and telegram_service.is_available():
                try:
                    telegram_service.send_task_status_update(
                        task.to_dict(),
                        old_status,
                        task.status,
                        assignee.to_dict()
                    )
                except Exception as e:
                    print(f"Failed to send status update notification: {e}")
        
        return jsonify({
            'status': 'success',
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update task',
            'details': str(e)
        }), 500

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete task"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        task = Task.query.get(task_id)
        if not task:
            return jsonify({
                'status': 'error',
                'message': 'Task not found'
            }), 404
        
        # Check permissions (only admin or creator can delete)
        if not current_user.is_admin() and task.created_by != current_user_id:
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        # Update assignee stats
        if task.assigned_to:
            assignee = User.query.get(task.assigned_to)
            if assignee:
                if assignee.total_tasks_assigned > 0:
                    assignee.total_tasks_assigned -= 1
                
                if task.status == 'completed' and assignee.total_tasks_completed > 0:
                    assignee.total_tasks_completed -= 1
                
                assignee.calculate_performance_score()
                assignee.updated_at = datetime.utcnow()
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Task deleted successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete task',
            'details': str(e)
        }), 500

@tasks_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """Get task statistics"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Base query
        base_query = Task.query
        
        # Filter for team members
        if not current_user.is_admin():
            base_query = base_query.filter(
                (Task.assigned_to == current_user_id) | 
                (Task.created_by == current_user_id)
            )
        
        # Get basic counts
        total_tasks = base_query.count()
        pending_tasks = base_query.filter(Task.status == 'pending').count()
        in_progress_tasks = base_query.filter(Task.status == 'in_progress').count()
        completed_tasks = base_query.filter(Task.status == 'completed').count()
        
        # Priority breakdown
        urgent_tasks = base_query.filter(Task.priority == 'urgent').count()
        high_tasks = base_query.filter(Task.priority == 'high').count()
        medium_tasks = base_query.filter(Task.priority == 'medium').count()
        low_tasks = base_query.filter(Task.priority == 'low').count()
        
        # Overdue tasks
        overdue_tasks = base_query.filter(
            Task.due_date < datetime.utcnow(),
            Task.status != 'completed'
        ).count()
        
        # AI generated tasks
        ai_tasks = base_query.filter(Task.is_ai_generated == True).count()
        
        # Recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_tasks = base_query.filter(Task.created_at >= week_ago).count()
        recent_completed = base_query.filter(
            Task.completed_at >= week_ago,
            Task.status == 'completed'
        ).count()
        
        # Calculate completion rate
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Average completion time
        completed_with_time = base_query.filter(
            Task.status == 'completed',
            Task.actual_hours > 0
        ).all()
        
        avg_completion_time = 0
        if completed_with_time:
            total_time = sum(task.actual_hours for task in completed_with_time)
            avg_completion_time = total_time / len(completed_with_time)
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'in_progress_tasks': in_progress_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': round(completion_rate, 1),
                'overdue_tasks': overdue_tasks,
                'priority_breakdown': {
                    'urgent': urgent_tasks,
                    'high': high_tasks,
                    'medium': medium_tasks,
                    'low': low_tasks
                },
                'ai_generated_tasks': ai_tasks,
                'recent_activity': {
                    'new_tasks': recent_tasks,
                    'completed_tasks': recent_completed
                },
                'average_completion_time': round(avg_completion_time, 2)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get task stats',
            'details': str(e)
        }), 500

@tasks_bp.route('/kanban', methods=['GET'])
@jwt_required()
def get_kanban_data():
    """Get tasks organized for Kanban board"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Base query
        query = Task.query
        
        # Filter for team members
        if not current_user.is_admin():
            query = query.filter(
                (Task.assigned_to == current_user_id) | 
                (Task.created_by == current_user_id)
            )
        
        # Get tasks by status
        pending_tasks = query.filter(Task.status == 'pending').order_by(Task.priority.desc(), Task.created_at.desc()).all()
        in_progress_tasks = query.filter(Task.status == 'in_progress').order_by(Task.priority.desc(), Task.started_at.desc()).all()
        completed_tasks = query.filter(Task.status == 'completed').order_by(Task.completed_at.desc()).limit(20).all()
        
        return jsonify({
            'status': 'success',
            'kanban': {
                'pending': [task.to_dict() for task in pending_tasks],
                'in_progress': [task.to_dict() for task in in_progress_tasks],
                'completed': [task.to_dict() for task in completed_tasks]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get Kanban data',
            'details': str(e)
        }), 500

@tasks_bp.route('/bulk-update', methods=['PUT'])
@jwt_required()
def bulk_update_tasks():
    """Bulk update multiple tasks"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        data = request.get_json()
        if not data or 'task_ids' not in data or 'updates' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Task IDs and updates are required'
            }), 400
        
        task_ids = data['task_ids']
        updates = data['updates']
        
        if not task_ids:
            return jsonify({
                'status': 'error',
                'message': 'No task IDs provided'
            }), 400
        
        # Get tasks
        tasks = Task.query.filter(Task.id.in_(task_ids)).all()
        
        updated_count = 0
        for task in tasks:
            # Check permissions
            can_edit = (
                current_user.is_admin() or 
                task.created_by == current_user_id or 
                task.assigned_to == current_user_id
            )
            
            if not can_edit:
                continue
            
            # Apply updates
            if 'status' in updates:
                task.update_status(updates['status'])
            
            if 'priority' in updates:
                task.priority = updates['priority']
            
            if 'assigned_to' in updates:
                old_assigned_to = task.assigned_to
                new_assigned_to = updates['assigned_to']
                
                if old_assigned_to != new_assigned_to:
                    # Update assignee stats
                    if old_assigned_to:
                        old_assignee = User.query.get(old_assigned_to)
                        if old_assignee and old_assignee.total_tasks_assigned > 0:
                            old_assignee.total_tasks_assigned -= 1
                    
                    if new_assigned_to:
                        new_assignee = User.query.get(new_assigned_to)
                        if new_assignee:
                            new_assignee.total_tasks_assigned += 1
                    
                    task.assigned_to = new_assigned_to
            
            task.updated_at = datetime.utcnow()
            updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Updated {updated_count} tasks successfully',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to bulk update tasks',
            'details': str(e)
        }), 500

