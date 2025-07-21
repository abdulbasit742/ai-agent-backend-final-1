#!/usr/bin/env python3
"""
AI Agent System - Flask Backend Application
Main entry point for the AI Agent System backend
Compatible with Python 3.10 and Windows 10
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Configuration
app.config['SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_agent_system.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize database with app
from src.models import db
db.init_app(app)

# Initialize other extensions
jwt = JWTManager(app)
CORS(app, origins="*")

# Import models after db initialization
from src.models.user import User
from src.models.task import Task

# Import routes
from src.routes.auth import auth_bp
from src.routes.tasks import tasks_bp
from src.routes.chat import chat_bp
from src.routes.telegram import telegram_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(tasks_bp, url_prefix='/api/tasks')
app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(telegram_bp, url_prefix='/api/telegram')

# Health check endpoint
@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI Agent System Backend is running',
        'timestamp': datetime.utcnow().isoformat()
    })

# Serve React frontend
@app.route('/')
def serve_frontend():
    """Serve React frontend"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory(app.static_folder, path)

def initialize_database():
    """Initialize database with sample data"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            
            # Check if admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                # Create admin user
                admin_user = User(
                    username='admin',
                    email='admin@aiagent.com',
                    role='admin'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                
                # Create team members
                team_members = [
                    {'username': 'john_doe', 'email': 'john@aiagent.com'},
                    {'username': 'jane_smith', 'email': 'jane@aiagent.com'},
                    {'username': 'mike_wilson', 'email': 'mike@aiagent.com'}
                ]
                
                for member_data in team_members:
                    member = User(
                        username=member_data['username'],
                        email=member_data['email'],
                        role='team'
                    )
                    member.set_password('user123')
                    db.session.add(member)
                
                # Create sample tasks
                sample_tasks = [
                    {
                        'title': 'Setup Development Environment',
                        'description': 'Configure development tools and environment for the project',
                        'priority': 'high',
                        'status': 'completed',
                        'assigned_to': 2,  # john_doe
                        'created_by': 1,   # admin
                        'due_date': datetime.utcnow() - timedelta(days=1),
                        'completed_at': datetime.utcnow() - timedelta(hours=2)
                    },
                    {
                        'title': 'Design Database Schema',
                        'description': 'Create comprehensive database schema for the AI Agent System',
                        'priority': 'high',
                        'status': 'in_progress',
                        'assigned_to': 3,  # jane_smith
                        'created_by': 1,   # admin
                        'due_date': datetime.utcnow() + timedelta(days=2)
                    },
                    {
                        'title': 'Implement User Authentication',
                        'description': 'Build JWT-based authentication system with role management',
                        'priority': 'urgent',
                        'status': 'pending',
                        'assigned_to': 4,  # mike_wilson
                        'created_by': 1,   # admin
                        'due_date': datetime.utcnow() + timedelta(days=3)
                    },
                    {
                        'title': 'Create Task Management API',
                        'description': 'Develop RESTful API endpoints for task CRUD operations',
                        'priority': 'medium',
                        'status': 'pending',
                        'assigned_to': 2,  # john_doe
                        'created_by': 1,   # admin
                        'due_date': datetime.utcnow() + timedelta(days=5)
                    },
                    {
                        'title': 'Integrate OpenAI GPT',
                        'description': 'Implement AI-powered task generation using OpenAI API',
                        'priority': 'medium',
                        'status': 'pending',
                        'assigned_to': 3,  # jane_smith
                        'created_by': 1,   # admin
                        'due_date': datetime.utcnow() + timedelta(days=7),
                        'is_ai_generated': True,
                        'ai_context': 'Generated based on project requirements analysis'
                    }
                ]
                
                for task_data in sample_tasks:
                    task = Task(**task_data)
                    db.session.add(task)
                
                db.session.commit()
                
                print("✅ Database initialized with sample data")
                print("👤 Admin: admin / admin123")
                print("👥 Team Members: john_doe, jane_smith, mike_wilson / user123")
            else:
                print("✅ Database already initialized")
                
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    # Initialize database
    initialize_database()
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    print(f"🚀 Starting AI Agent System Backend")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📊 Health check: http://{host}:{port}/api/health")
    
    app.run(host=host, port=port, debug=debug)

