# app/models/token.py
from app import db
from datetime import datetime

class Token(db.Model):
    __tablename__ = 'tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)
    id_token = db.Column(db.Text)
    expires_at = db.Column(db.DateTime)
    token_type = db.Column(db.String(50), default='Bearer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Token user_id={self.user_id}>'
