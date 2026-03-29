import os
import json
from pathlib import Path
from flask import Flask, redirect, request, jsonify
from google.auth.oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# CLIENT_SECRET_JSON 환경 변수에서 클라이언트 설정 읽기
CLIENT_SECRET_JSON = os.getenv('CLIENT_SECRET_JSON')
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_redirect_uri():
    """동적으로 redirect_uri를 반환하는 함수"""
    env = os.getenv('FLASK_ENV', 'development')
    print(f"🔍 DEBUG: FLASK_ENV={env}")
    if env == 'production':
        uri = 'https://youtube-shorts-uploader-production-0a35.up.railway.app/auth/callback'
    else:
        uri = 'http://localhost:5000/auth/callback'
    print(f"🔍 DEBUG: redirect_uri={uri}")
    return uri

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "ok", "message": "YouTube Shorts Uploader API is running!"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": str(Path.cwd())})

@app.route('/auth/login', methods=['GET'])
def auth_login():
    """OAuth 로그인 시작"""
    if not CLIENT_SECRET_JSON:
        return jsonify({"error": "CLIENT_SECRET_JSON not configured in Railway"}), 500
    
    try:
        # 클라이언트 설정 파일 생성
        client_secret_file = '/tmp/client_secret.json'
        with open(client_secret_file, 'w') as f:
            f.write(CLIENT_SECRET_JSON)
        
        # OAuth Flow 설정
        flow = Flow.from_client_secrets_file(
            client_secret_file,
            scopes=SCOPES,
            redirect_uri=get_redirect_uri()
        )
        
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return redirect(auth_url)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/auth/callback', methods=['GET'])
def auth_callback():
    """OAuth 콜백"""
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "No authorization code received"}), 400
    
    try:
        client_secret_file = '/tmp/client_secret.json'
        with open(client_secret_file, 'w') as f:
            f.write(CLIENT_SECRET_JSON)
        
        flow = Flow.from_client_secrets_file(
            client_secret_file,
            scopes=SCOPES,
            redirect_uri=get_redirect_uri()
        )
        
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        return jsonify({
            "status": "success",
            "message": "OAuth authentication successful"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/auth/logout', methods=['GET'])
def logout():
    """로그아웃"""
    return jsonify({"status": "success", "message": "로그아웃 완료"})

@app.route('/status', methods=['GET'])
def status():
    """앱 상태 확인"""
    return jsonify({
        "status": "running",
        "flask_env": os.getenv('FLASK_ENV', 'development'),
        "authenticated": "has_token" in session if 'has_token' in locals() else False,
        "redirect_uri": get_redirect_uri()
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f"🚀 Flask 앱 시작: PORT={port}, FLASK_ENV={os.getenv('FLASK_ENV', 'development')}")
    app.run(host='0.0.0.0', port=port, debug=False)

    
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
