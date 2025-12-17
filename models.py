# FILE: models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# 1. USER TABLE
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default="Student")
    
    full_name = db.Column(db.String(150))
    college = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    qualification = db.Column(db.String(100))
    
    internships = db.relationship('Internship', backref='author', lazy=True)
    applications = db.relationship('Application', backref='applicant', lazy=True)

# 2. INTERNSHIP TABLE (Updated with 'description')
class Internship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(100))
    required_skills = db.Column(db.String(500))
    type = db.Column(db.String(50)) # Remote/Onsite
    
    # --- THIS WAS MISSING ---
    description = db.Column(db.Text) 
    # ------------------------

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    applications = db.relationship('Application', backref='internship', lazy=True)

# 3. APPLICATION TABLE
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    internship_id = db.Column(db.Integer, db.ForeignKey('internship.id'))
    generated_text = db.Column(db.Text) 
    resume_filename = db.Column(db.String(300))
    status = db.Column(db.String(50), default="Applied")