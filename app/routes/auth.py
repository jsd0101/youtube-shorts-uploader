# app/routes/auth.py
from flask import Blueprint, jsonify, redirect, request, session, send_from_directory
from app import oauth, db
from app.models import User, Token
from app.services.auth_service import AuthService
from datetime import datetime
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
auth_service = AuthService()

@auth_bp.route('/')
def home():
    """홈페이지"""
    return send_from_directory('.', 'index.html')

@auth_bp.route('/status')
def status():
    """서버 상태"""
    return jsonify({
        "status": "running",
        "flask_env": os.getenv('FLASK_ENV', 'development'),
        "port": os.getenv('PORT', '5000'),
        "authenticated": 'user' in session
    })

@auth_bp.route('/login')
def login():
    """Google OAuth 로그인 시작"""
    redirect_uri = (
        'https://youtube-shorts-uploader-production-0a35.up.railway.app/auth/callback'
        if os.getenv('FLASK_ENV') == 'production'
        else 'http://localhost:5000/auth/callback'
    )
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback')
def callback():
    """Google OAuth 콜백"""
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo') or token
        
        # 데이터베이스에 사용자 저장/업데이트
        user = auth_service.save_or_update_user(user_info)
        
        # 토큰 저장
        auth_service.save_token(user.id, token)
        
        # 세션 저장
        session['user'] = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'picture_url': user.picture_url
        }
        session['access_token'] = token.get('access_token', '')
        
        return jsonify({
            "status": "success",
            "message": f"✅ {user.email} 인증 완료!",
            "authenticated": True,
            "user": session['user']
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"인증 실패: {str(e)}"
        }), 400

@auth_bp.route('/logout')
def logout():
    """로그아웃"""
    session.pop('user', None)
    session.pop('access_token', None)
    return jsonify({
        "status": "success",
        "message": "로그아웃 완료",
        "authenticated": False
    })
