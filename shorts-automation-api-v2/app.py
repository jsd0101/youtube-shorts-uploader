import os
from flask import Flask, redirect, request, session, url_for, jsonify
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')

# CLIENT_SECRET_JSON 환경 변수에서 클라이언트 정보 로드
def get_client_secrets():
    client_secret_json = os.environ.get('CLIENT_SECRET_JSON')
    if not client_secret_json:
        raise ValueError("CLIENT_SECRET_JSON 환경 변수가 설정되지 않았습니다.")
    return json.loads(client_secret_json)

# 환경에 따라 redirect_uri 동적 설정
def get_redirect_uri():
    if os.environ.get('FLASK_ENV') == 'production':
        return 'https://youtube-shorts-uploader-production-0a35.up.railway.app/auth/callback'
    else:
        return 'http://localhost:5000/auth/callback'

@app.route('/')
def home():
    return jsonify({"message": "YouTube Shorts Uploader API is running", "status": "ok"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": "/app"})

@app.route('/auth/login')
def auth_login():
    try:
        client_secrets = get_client_secrets()
        redirect_uri = get_redirect_uri()
        
        flow = Flow.from_client_config(
            client_secrets,
            scopes=['https://www.googleapis.com/auth/youtube.upload'],
            redirect_uri=redirect_uri
        )
        
        auth_url, state = flow.authorization_url(access_type='offline', prompt='consent')
        session['state'] = state
        return redirect(auth_url)
    except Exception as e:
        return jsonify({"error": f"OAuth login failed: {str(e)}"}), 500

@app.route('/auth/callback')
def auth_callback():
    try:
        state = session.get('state')
        client_secrets = get_client_secrets()
        redirect_uri = get_redirect_uri()
        
        flow = Flow.from_client_config(
            client_secrets,
            scopes=['https://www.googleapis.com/auth/youtube.upload'],
            state=state,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        session['credentials'] = credentials.to_json()
        
        return jsonify({"message": "OAuth 인증 완료!", "status": "success"})
    except Exception as e:
        return jsonify({"error": f"OAuth callback failed: {str(e)}"}), 500

@app.route('/upload-shorts', methods=['POST'])
def upload_shorts():
    return jsonify({"message": "Shorts upload endpoint", "status": "ok"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
