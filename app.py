import os
import json
from pathlib import Path
from flask import Flask, redirect, request, jsonify, session
from google.auth.oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

CLIENT_SECRET_JSON = os.getenv('CLIENT_SECRET_JSON')
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_redirect_uri():
    env = os.getenv('FLASK_ENV', 'development')
    if env == 'production':
        return 'https://youtube-shorts-uploader-production-0a35.up.railway.app/auth/callback'
    else:
        return 'http://localhost:5000/auth/callback'

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "ok", "message": "YouTube Shorts Uploader API is running!"})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": str(Path.cwd())})

@app.route('/auth/login', methods=['GET'])
def auth_login():
    if not CLIENT_SECRET_JSON:
        return jsonify({"error": "CLIENT_SECRET_JSON not configured in Railway"}), 500
    client_secret_file = '/tmp/client_secret.json'
    with open(client_secret_file, 'w') as f:
        f.write(CLIENT_SECRET_JSON)
    flow = Flow.from_client_secrets_file(client_secret_file, scopes=SCOPES, redirect_uri=get_redirect_uri())
    auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    return redirect(auth_url)

@app.route('/auth/callback', methods=['GET'])
def auth_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "No authorization code received"}), 400
    client_secret_file = '/tmp/client_secret.json'
    with open(client_secret_file, 'w') as f:
        f.write(CLIENT_SECRET_JSON)
    flow = Flow.from_client_secrets_file(client_secret_file, scopes=SCOPES, redirect_uri=get_redirect_uri())
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    return jsonify({"status": "success", "message": "OAuth authentication successful"})

@app.route('/auth/logout', methods=['GET'])
def logout():
    return jsonify({"status": "success", "message": "로그아웃 완료"})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running", "flask_env": os.getenv('FLASK_ENV', 'development'), "redirect_uri": get_redirect_uri()})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
