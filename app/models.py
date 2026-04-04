from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    picture = db.Column(db.String(500))
    access_token = db.Column(db.Text)
    refresh_token = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    uploads = db.relationship('Upload', backref='user', lazy=True)
    tokens = db.relationship('Token', backref='user', lazy=True)

class Upload(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500))
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    tags = db.Column(db.String(500))
    youtube_video_id = db.Column(db.String(255))
    youtube_url = db.Column(db.String(500))
    status = db.Column(db.String(50), default='pending')
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.Text, unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

