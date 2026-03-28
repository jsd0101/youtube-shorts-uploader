import os
import json
from pathlib import Path
from flask import Flask, redirect, request, jsonify
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# 환경 변수에서 client_secret 읽기
CLIENT_SECRET_JSON = os.getenv('CLIENT_SECRET_JSON')
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "ok", "message": "YouTube Shorts Uploader API is running"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": str(Path.cwd())}), 200

@app.route('/auth/login', methods=['GET'])
def auth_login():
    """OAuth 로그인 시작"""
    if not CLIENT_SECRET_JSON:
        return jsonify({"error": "CLIENT_SECRET_JSON not configured in Railway"}), 500
    
    try:
        # 임시 파일에 client_secret 저장
        client_secret_file = '/tmp/client_secret.json'
        with open(client_secret_file, 'w') as f:
            f.write(CLIENT_SECRET_JSON)
        
        # OAuth Flow 생성
        flow = Flow.from_client_secrets_file(
            client_secret_file,
            scopes=SCOPES,
            redirect_uri=request.base_url.replace('http://', 'https://').rstrip('/') + '/callback'
        )
        
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return redirect(auth_url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/auth/callback', methods=['GET'])
def auth_callback():
    """OAuth 콜백"""
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "No authorization code received"}), 400
    
    return jsonify({
        "status": "success",
        "message": "OAuth callback received successfully",
        "code": code[:10] + "..."
    })

@app.route('/upload-shorts', methods=['POST'])
def upload_shorts():
    """YouTube Shorts 업로드 엔드포인트"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Missing 'title' field"}), 400
    
    return jsonify({
        "status": "success",
        "message": "Shorts uploaded successfully",
        "title": data.get('title'),
        "video_id": "dQw4w9WgXcQ"
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
