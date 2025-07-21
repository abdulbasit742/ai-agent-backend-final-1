"""
Authentication Routes - JWT Authentication System
Compatible with Python 3.10 and Flask-JWT-Extended
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from werkzeug.security import check_password_hash
from ..models import db
from ..models.user import User

# Create blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'status': 'error',
                'message': 'Username and password are required'
            }), 400
        
        # Find user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'status': 'error',
                'message': 'Invalid username or password'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'status': 'error',
                'message': 'Account is deactivated'
            }), 401
        
        # Update last login
        user.update_last_login()
        
        # Create tokens with additional claims
        additional_claims = {
            'username': user.username,
            'role': user.role,
            'email': user.email
        }
        
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 86400,  # 24 hours in seconds
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Login failed',
            'details': str(e)
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'status': 'error',
                'message': 'User not found or inactive'
            }), 401
        
        # Create new access token
        additional_claims = {
            'username': user.username,
            'role': user.role,
            'email': user.email
        }
        
        new_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims
        )
        
        return jsonify({
            'status': 'success',
            'access_token': new_token,
            'expires_in': 86400
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Token refresh failed',
            'details': str(e)
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    try:
        # In a production app, you might want to blacklist the token
        # For now, we'll just return a success message
        return jsonify({
            'status': 'success',
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Logout failed',
            'details': str(e)
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get user info',
            'details': str(e)
        }), 500

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        role_filter = request.args.get('role')
        
        # Build query
        query = User.query
        
        if role_filter:
            query = query.filter_by(role=role_filter)
        
        # Paginate results
        users = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'status': 'success',
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get users',
            'details': str(e)
        }), 500

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get specific user information"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Users can view their own info, admins can view any user
        if current_user_id != user_id and not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'status': 'success',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get user',
            'details': str(e)
        }), 500

@auth_bp.route('/users/<int:user_id>/activate', methods=['PUT'])
@jwt_required()
def activate_user(user_id):
    """Activate/deactivate user (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        data = request.get_json()
        is_active = data.get('is_active', True)
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        user.is_active = is_active
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        action = 'activated' if is_active else 'deactivated'
        return jsonify({
            'status': 'success',
            'message': f'User {action} successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to update user status',
            'details': str(e)
        }), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """User registration endpoint (for demo purposes)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'No data provided'
            }), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'team')
        
        if not username or not email or not password:
            return jsonify({
                'status': 'error',
                'message': 'Username, email, and password are required'
            }), 400
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({
                'status': 'error',
                'message': 'Username already exists'
            }), 409
        
        if User.query.filter_by(email=email).first():
            return jsonify({
                'status': 'error',
                'message': 'Email already exists'
            }), 409
        
        # Validate role
        if role not in ['admin', 'team']:
            role = 'team'
        
        # Create new user
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Registration failed',
            'details': str(e)
        }), 500

@auth_bp.route('/change-password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            }), 404
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'status': 'error',
                'message': 'Current and new passwords are required'
            }), 400
        
        # Verify current password
        if not user.check_password(current_password):
            return jsonify({
                'status': 'error',
                'message': 'Current password is incorrect'
            }), 401
        
        # Update password
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to change password',
            'details': str(e)
        }), 500

@auth_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_auth_stats():
    """Get authentication statistics (Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or not current_user.is_admin():
            return jsonify({
                'status': 'error',
                'message': 'Admin access required'
            }), 403
        
        # Get user statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(role='admin').count()
        team_users = User.query.filter_by(role='team').count()
        
        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = User.query.filter(
            User.created_at >= thirty_days_ago
        ).count()
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'admin_users': admin_users,
                'team_users': team_users,
                'recent_registrations': recent_registrations
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'Failed to get auth stats',
            'details': str(e)
        }), 500

