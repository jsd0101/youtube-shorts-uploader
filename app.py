from flask import Flask, jsonify, redirect, request, session, send_from_directory
import os
import json
from google.auth.oauthlib.flow import Flow
import google.auth.transport.requests
from google.oauth2.credentials import Credentials

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_redirect_uri():
    """동적으로 redirect URI 결정"""
    if os.getenv('FLASK_ENV') == 'production':
        return 'https://youtube-shorts-uploader-production-0a35.up.railway.app/auth/callback'
    else:
        return 'http://localhost:5000/auth/callback'

def get_flow():
    """CLIENT_SECRET_JSON 환경변수에서 OAuth Flow 생성"""
    client_secret_json = os.getenv('CLIENT_SECRET_JSON')
    if not client_secret_json:
        print('⚠️ WARNING: CLIENT_SECRET_JSON 환경변수가 설정되지 않음')
        return None
    
    try:
        client_config = json.loads(client_secret_json)
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=get_redirect_uri()
        )
        print("✅ OAuth Flow 생성 완료")
        return flow
    except Exception as e:
        print(f'❌ ERROR in get_flow(): {e}')
        return None

@app.route('/')
def home():
    """홈 페이지 - index.html 반환"""
    return send_from_directory('.', 'index.html')

@app.route('/status')
def status():
    """서버 상태 확인"""
    return jsonify({
        "status": "running",
        "flask_env": os.getenv('FLASK_ENV', 'development'),
        "port": os.getenv('PORT', '5000'),
        "authenticated": 'access_token' in session
    })

@app.route('/auth/login')
def login():
    """Google OAuth 로그인 시작"""
    flow = get_flow()
    if not flow:
        return jsonify({
            "status": "error",
            "message": "OAuth가 구성되지 않았습니다"
        }), 500
    
    try:
        auth_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        session['oauth_state'] = state
        print(f"✅ 로그인 URL 생성: {auth_url[:50]}...")
        print(f"✅ State 저장: {state[:20]}...")
        return redirect(auth_url)
    except Exception as e:
        print(f'❌ ERROR in /auth/login: {e}')
        return jsonify({
            "status": "error",
            "message": f"로그인 실패: {str(e)}"
        }), 500

@app.route('/auth/callback')
def callback():
    """Google OAuth 콜백"""
    # 에러 확인
    error = request.args.get('error')
    if error:
        print(f"❌ OAuth 에러: {error}")
        return jsonify({
            "status": "error",
            "message": f"인증 실패: {error}"
        }), 400
    
    # ✅ State 검증 (CSRF 방지)
    request_state = request.args.get('state')
    session_state = session.get('oauth_state')
    
    if not request_state or request_state != session_state:
        print(f"❌ State 검증 실패: request={request_state[:20] if request_state else None}..., session={session_state[:20] if session_state else None}...")
        return jsonify({
            "status": "error",
            "message": "State 검증 실패 - 보안 오류"
        }), 400
    
    # State 검증 성공 후 세션에서 제거 (일회용)
    session.pop('oauth_state', None)
    print("✅ State 검증 성공 & 제거")
    
    flow = get_flow()
    if not flow:
        return jsonify({
            "status": "error",
            "message": "OAuth가 구성되지 않았습니다"
        }), 500
    
    try:
        # authorization_response를 받아 토큰 교환
        flow.fetch_token(authorization_response=request.url)
        creds = flow.credentials
        
        # 세션에 토큰 저장
        session['access_token'] = creds.token
        session['refresh_token'] = creds.refresh_token or ""
        session['token_expiry'] = creds.expiry.isoformat() if creds.expiry else None
        
        print("✅ Google 인증 완료!")
        print(f"   - Access Token: {creds.token[:20]}...")
        print(f"   - Refresh Token: {'있음' if creds.refresh_token else '없음'}")
        
        # JSON 응답 반환
        return jsonify({
            "status": "success",
            "message": "✅ Google 인증 완료!",
            "access_token": creds.token[:20] + "..." if creds.token else None,
            "authenticated": True
        })
    except Exception as e:
        print(f'❌ ERROR in /auth/callback: {e}')
        return jsonify({
            "status": "error",
            "message": f"Token 획득 실패: {str(e)}"
        }), 400

@app.route('/auth/logout')
def logout():
    """로그아웃"""
    session.pop('access_token', None)
    session.pop('refresh_token', None)
    session.pop('token_expiry', None)
    session.pop('oauth_state', None)
    
    print("✅ 로그아웃 완료")
    return jsonify({
        "status": "success",
        "message": "로그아웃 완료",
        "authenticated": False
    })

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """YouTube 업로드 준비 확인"""
    if 'access_token' not in session:
        return jsonify({
            "status": "error",
            "message": "Google 인증이 필요합니다. /auth/login으로 이동해주세요."
        }), 401
    
    if request.method == 'POST':
        # 나중에 업로드 로직 추가
        return jsonify({
            "status": "pending",
            "message": "YouTube 업로드 기능 준비 중입니다."
        })
    
    return jsonify({
        "status": "ready",
        "message": "YouTube 업로드 준비 완료",
        "authenticated": True,
        "methods": ["GET", "POST"]
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    flask_env = os.getenv('FLASK_ENV', 'development')
    print(f"{'='*50}")
    print(f"INFO: Flask 시작!")
    print(f"PORT={port}, FLASK_ENV={flask_env}")
    print(f"Redirect URI: {get_redirect_uri()}")
    print(f"{'='*50}")
    app.run(host='0.0.0.0', port=port, debug=False)
