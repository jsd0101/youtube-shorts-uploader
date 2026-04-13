import os
from flask import Flask
from flask_session import Session
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix

oauth = OAuth()

def create_app():
    app = Flask(__name__)
    
    # ===== 보안 설정 =====
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # ===== 세션 설정 =====
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    Session(app)
    
    # ===== ProxyFix (Railway 배포용, x_prefix 제거) =====
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1
    )
    
    # ===== Google OAuth 등록 =====
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
        token_url='https://oauth2.googleapis.com/token',
        userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
        client_kwargs={
            'scope': 'openid email profile https://www.googleapis.com/auth/youtube.upload'
        },
        authorize_params={
            'access_type': 'offline',
            'prompt': 'select_account'
        }
    )
    
    # ===== 블루프린트 등록 =====
    from app.auth import auth_bp
    from app.upload import upload_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    
    # ===== 기본 라우트 =====
    @app.route('/')
    def index():
        return '''
        <h1>YouTube Shorts 업로더</h1>
        <p><a href="/auth/login">Google로 로그인</a></p>
        '''
    
    @app.route('/health')
    def health():
        return {'status': 'ok'}, 200
    
    return app
