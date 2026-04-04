# app/models/upload.py
from app import db
from datetime import datetime

class Upload(db.Model):
    __tablename__ = 'uploads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(500))
    video_type = db.Column(db.String(20), default='shorts')  # 'shorts' or 'longform'
    duration = db.Column(db.Integer)  # 초 단위
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    youtube_video_id = db.Column(db.String(255), unique=True, index=True)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Upload {self.title}>'
