from flask import Flask, jsonify, send_from_directory, redirect, request, session
import os
import json
from google.auth.oauthlib.flow import Flow

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_redirect_uri():
    if os.getenv('FLASK_ENV') == 'production':
        return 'https://youtube-shorts-uploader-production-0a35.up.railway.app/auth/callback'
    return 'http://localhost:5000/auth/callback'

def get_flow():
    client_secret_json = os.getenv('CLIENT_SECRET_JSON')
    if not client_secret_json:
        print("⚠️ WARNING: CLIENT_SECRET_JSON not set in environment")
        return None
    
    try:
        client_config = json.loads(client_secret_json)
        return Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=get_redirect_uri())
    except Exception as e:
        print(f"❌ ERROR: Failed to create Flow: {e}")
        return None

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/status')
def status():
    return jsonify({
        "status": "running",
        "flask_env": os.getenv('FLASK_ENV', 'development'),
        "port": os.getenv('PORT', '5000'),
        "authenticated": 'access_token' in session
    })

@app.route('/auth/login')
def login():
    flow = get_flow()
    if not flow:
        return jsonify({"error": "OAuth not configured", "status": "error"}), 500
    
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['oauth_state'] = state
    return redirect(auth_url)

@app.route('/auth/callback')
def callback():
    error = request.args.get('error')
    if error:
        return jsonify({
            "status": "error",
            "message": f"인증 실패: {error}"
        }), 400
    
    flow = get_flow()
    if not flow:
        return jsonify({"error": "OAuth not configured"}), 500
    
    try:
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        session['access_token'] = creds.token
        session['refresh_token'] = creds.refresh_token
        return jsonify({
            "status": "success",
            "message": "✅ Google 인증 완료!",
            "access_token": creds.token
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Token 획득 실패: {str(e)}"
        }), 400

@app.route('/auth/logout')
def logout():
    session.pop('access_token', None)
    session.pop('refresh_token', None)
    return jsonify({
        "status": "success",
        "message": "로그아웃 완료"
    })

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'access_token' not in session:
        return jsonify({
            "status": "error",
            "message": "Google 인증이 필요합니다. /auth/login으로 이동해주세요."
        }), 401
    
    return jsonify({
        "status": "ready",
        "message": "YouTube 업로드 준비 완료",
        "methods": ["GET", "POST"],
        "authenticated": True
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    flask_env = os.getenv('FLASK_ENV', 'development')
    print(f"INFO: Flask 시작! PORT={port}, FLASK_ENV={flask_env}")
    app.run(host='0.0.0.0', port=port, debug=False)
