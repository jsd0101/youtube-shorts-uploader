import os
from flask import Flask
from app.extensions import db, oauth
from flask_cors import CORS

def create_app(config_name=None):
    """Flask 앱 팩토리"""
    
    # 설정 이름 결정
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Flask 앱 생성
    app = Flask(__name__)
    
    # 설정 로드
    from app.config import config
    app.config.from_object(config[config_name])
    
    # 확장 초기화
    db.init_app(app)
    oauth.init_app(app)
    CORS(app)
    
    # Google OAuth 설정
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    # 앱 컨텍스트 내에서 초기화
    with app.app_context():
        # 데이터베이스 테이블 생성
        db.create_all()
        
        # Blueprint 등록
        from app.routes import auth_bp, upload_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(upload_bp)
    
    return app
