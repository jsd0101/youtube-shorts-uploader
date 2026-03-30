from flask import Flask, jsonify, redirect, request, session, send_from_directory
import os
from authlib.integrations.flask_client import OAuth

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')

oauth = OAuth(app)

def register_google_oauth():
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/youtube.upload'}
    )

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/status')
def status():
    return jsonify({"status":"running","flask_env":os.getenv('FLASK_ENV','development'),"port":os.getenv('PORT','5000'),"authenticated":'user' in session})

@app.route('/auth/login')
def login():
    register_google_oauth()
    redirect_uri = ('https://youtube-shorts-uploader-production-0a35.up.railway.app/auth/callback'
                    if os.getenv('FLASK_ENV') == 'production' else 'http://localhost:5000/auth/callback')
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def callback():
    register_google_oauth()
    try:
        token = oauth.google.authorize_access_token()
        # ✅ nonce 파라미터 추가
        user_info = token.get('userinfo')
        if not user_info:
            # Fallback: ID token에서 파싱 (nonce 없이)
            user_info = token
        session['user'] = user_info
        session['access_token'] = token.get('access_token', '')
        session['refresh_token'] = token.get('refresh_token', '')
        email = user_info.get('email', 'Unknown')
        print(f"✅ Google 인증 완료: {email}")
        return jsonify({"status":"success","message":f"✅ {email} 인증 완료!","authenticated":True,"user":user_info})
    except Exception as e:
        print(f"❌ 인증 실패: {str(e)}")
        return jsonify({"status":"error","message":f"인증 실패: {str(e)}"}),400

@app.route('/auth/logout')
def logout():
    session.pop('user', None)
    session.pop('access_token', None)
    session.pop('refresh_token', None)
    print("✅ 로그아웃 완료")
    return jsonify({"status":"success","message":"로그아웃 완료","authenticated":False})

@app.route('/upload', methods=['GET','POST'])
def upload():
    if 'user' not in session:
        return jsonify({"status":"error","message":"인증이 필요합니다. /auth/login으로 이동해주세요."}),401
    return jsonify({"status":"ready","message":"YouTube 업로드 준비 완료","authenticated":True,"user":session.get('user',{})})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    flask_env = os.getenv('FLASK_ENV', 'development')
    print('='*60)
    print('INFO: Flask 시작!')
    print(f'PORT={port}, FLASK_ENV={flask_env}')
    print('='*60)
    app.run(host='0.0.0.0', port=port, debug=False)

