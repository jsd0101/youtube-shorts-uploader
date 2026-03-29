from flask import Flask, redirect, request, session, jsonify
import os
import json
from google.auth.oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import requests

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# OAuth 2.0 설정
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_redirect_uri():
    env = os.getenv('FLASK_ENV', 'development')
    print(f"?? DEBUG: FLASK_ENV={env}")
    if env == 'production':
        uri = 'https://youtube-shorts-uploader-production-0a35.up.railway.app/auth/callback'
    else:
        uri = 'http://localhost:5000/auth/callback'
    print(f"?? DEBUG: redirect_uri={uri}")
    return uri

def get_flow():
    """OAuth Flow 생성"""
    client_secret_json = os.getenv('CLIENT_SECRET_JSON')
    if not client_secret_json:
        raise ValueError("CLIENT_SECRET_JSON 환경변수가 필요합니다!")
    
    print(f"?? DEBUG: CLIENT_SECRET_JSON 길이={len(client_secret_json)}")
    
    try:
        client_config = json.loads(client_secret_json)
    except json.JSONDecodeError as e:
        print(f"??JSON 파싱 오류: {e}")
        raise
    
    print(f"?? DEBUG: client_config={json.dumps(client_config, indent=2)[:200]}...")
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=get_redirect_uri()
    )
    
    print(f"?? DEBUG: Flow 생성 완료, client_id={client_config.get('installed', {}).get('client_id', 'N/A')}")
    return flow

# =============== OAuth 2.0 요청? 뭐??===============
@app.route('/', methods=['GET'])
def health():
    """상태 확인"""
    return jsonify({
        "status": "ok",
        "message": "YouTube Shorts Uploader - OAuth 2.0",
        "flask_env": os.getenv('FLASK_ENV', 'development')
    })

@app.route('/auth/login', methods=['GET'])
def login():
    """Google OAuth 로그인"""
    print("?? /auth/login 요청됨")
    
    try:
        flow = get_flow()
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        print(f"?? DEBUG: authorization_url={authorization_url}")
        print(f"?? DEBUG: state={state}")
        
        # state를 세션에 저장
        session['oauth_state'] = state
        
        print("?? /auth/login 요청됨, Google 로그인 페이지로 리다이렉트")
        return redirect(authorization_url)
    except Exception as e:
        print(f"?? /auth/login 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/auth/callback', methods=['GET'])
def callback():
    """Google OAuth 콜백"""
    print("?? Google OAuth 콜백 수신??")
    
    try:
        # ?앗음 오류처리
        error = request.args.get('error')
        if error:
            print(f"?? OAuth 오류: {error}")
            return jsonify({"status": "error", "message": f"OAuth error: {error}"}), 400
        
        # authorization_code 받기
        code = request.args.get('code')
        print(f"?? DEBUG: authorization_code={code}")
        
        if not code:
            print("?? authorization_code 없음")
            return jsonify({"status": "error", "message": "No authorization code"}), 400
        
        # Flow ?갱신?토큰 획득
        flow = get_flow()
        flow.fetch_token(authorization_response=request.url)
        
        credentials = flow.credentials
        print(f"?? Token 획득 완료")
        print(f"?? DEBUG: access_token={credentials.token[:20]}...")
        print(f"?? DEBUG: refresh_token={credentials.refresh_token is not None}...")
        
        # ?갱신?token 저장
        session['access_token'] = credentials.token
        
        return jsonify({
            "status": "success",
            "message": "Google OAuth 2.0 인증 완료!",
            "access_token": credentials.token[:50] + "...",
            "has_refresh_token": credentials.refresh_token is not None
        })
        
    except Exception as e:
        print(f"?? /auth/callback 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/auth/logout', methods=['GET'])
def logout():
    """로그아웃"""
    session.clear()
    return jsonify({"status": "success", "message": "로그아웃 완료!!"})

# =============== 상태? 뭐??? ===============
@app.route('/status', methods=['GET'])
def status():
    """상태 확인"""
    has_token = 'access_token' in session
    return jsonify({
        "status": "running",
        "flask_env": os.getenv('FLASK_ENV', 'development'),
        "authenticated": has_token,
        "redirect_uri": get_redirect_uri()
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    print(f"?? Flask ?????앗!! PORT={port}, FLASK_ENV={os.getenv('FLASK_ENV', 'development')}")
    app.run(host='0.0.0.0', port=port, debug=False)

