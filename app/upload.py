from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
import os
import requests
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import tempfile
import subprocess

upload_bp = Blueprint('upload', __name__, url_prefix='')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@upload_bp.route('/dashboard')
@login_required
def dashboard():
    """업로드 폼 페이지"""
    user_info = session.get('user_info', {})
    return render_template('dashboard.html', user=user_info)

@upload_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """YouTube에 영상 업로드"""
    video_url = request.form.get('video_url')
    title = request.form.get('title', 'Untitled')
    description = request.form.get('description', '')
    
    if not video_url:
        return jsonify({'error': 'Video URL required'}), 400
    
    try:
        # YouTube API 초기화
        token = session.get('token')
        youtube = build(
            'youtube',
            'v3',
            credentials=oauth.google.fetch_token(token)
        )
        
        # 비디오 다운로드
        with tempfile.TemporaryDirectory() as tmp_dir:
            video_path = os.path.join(tmp_dir, 'video.mp4')
            
            # yt-dlp 사용 (간단한 버전)
            subprocess.run([
                'yt-dlp',
                '-f', 'best[ext=mp4]',
                '-o', video_path,
                video_url
            ], check=True)
            
            # YouTube에 업로드
            request_body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': ['shorts'],
                    'categoryId': '22'
                },
                'status': {
                    'privacyStatus': 'public'
                }
            }
            
            media = MediaFileUpload(video_path, mimetype='video/mp4')
            response = youtube.videos().insert(
                part='snippet,status',
                body=request_body,
                media_body=media
            ).execute()
            
            video_id = response['id']
            return render_template(
                'success.html',
                video_id=video_id,
                title=title
            )
    
    except Exception as e:
        return render_template(
            'error.html',
            error=str(e)
        ), 500
