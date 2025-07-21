"""
Models Package - Database Models
Fixes circular import issues
Compatible with Python 3.10
"""

from flask_sqlalchemy import SQLAlchemy

# Initialize database instance
db = SQLAlchemy()

