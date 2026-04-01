import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth

db = SQLAlchemy()
oauth = OAuth()

def create_app(config_name='development'):
    """Flask 앱 팩토리"""
    app = Flask(__name__)
    
    # 환경변수에서 설정 이름 가져오기
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # config.py에서 설정 가져오기
    from app.config import config
    app.config.from_object(config[config_name])
    
    # 데이터베이스 초기화
    db.init_app(app)
    
    # OAuth 초기화
    oauth.init_app(app)
    
    # CORS 초기화
    CORS(app)
    
    # SECRET_KEY 설정
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Google OAuth 설정
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    # 데이터베이스 테이블 생성
    with app.app_context():
        db.create_all()
    
    # 블루프린트 등록
    from app.routes import auth_bp, upload_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    
    # 라우트 정보 출력
    print("\n=== Registered Routes ===")
    for rule in app.url_map.iter_rules():
        print(f"{rule.rule} -> {rule.endpoint} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
    print("========================\n")
    
    return app
