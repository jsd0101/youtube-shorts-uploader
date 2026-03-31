# app/routes/upload.py
from flask import Blueprint, jsonify, session, request
from app import db
from app.models import Upload, User
import os

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

@upload_bp.route('/', methods=['GET', 'POST'])
def upload():
    """YouTube 업로드 준비"""
    if 'user' not in session:
        return jsonify({
            "status": "error",
            "message": "인증이 필요합니다. /auth/login으로 이동해주세요."
        }), 401
    
    return jsonify({
        "status": "ready",
        "message": "YouTube 업로드 준비 완료",
        "authenticated": True,
        "user": session.get('user', {})
    })

@upload_bp.route('/status', methods=['GET'])
def upload_status():
    """업로드 상태 조회"""
    if 'user' not in session:
        return jsonify({"status": "error", "message": "인증 필요"}), 401
    
    user_id = session['user']['id']
    uploads = Upload.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "status": "success",
        "uploads": [
            {
                "id": u.id,
                "title": u.title,
                "video_type": u.video_type,
                "status": u.status,
                "youtube_video_id": u.youtube_video_id,
                "created_at": u.created_at.isoformat()
            }
            for u in uploads
        ]
    })
