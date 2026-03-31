# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
import logging
import json
from pythonjsonlogger import jsonlogger
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# SQLAlchemy, Migrate, OAuth 초기화
db = SQLAlchemy()
migrate = Migrate()
oauth = OAuth()

def create_app(config_name=None):
    """Flask 애플리케이션 팩토리"""
    app = Flask(__name__)
    
    # 설정 로드
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    if config_name == 'production':
        from app.config import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from app.config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # 확장 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    oauth.init_app(app)
    
    # Google OAuth 등록
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile https://www.googleapis.com/auth/youtube.upload'}
    )
    
    # 로깅 설정
    setup_logging(app)
    
    # Blueprint 등록
    from app.routes import auth_bp, upload_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    
    # 전역 에러 핸들러
    @app.errorhandler(404)
    def not_found(error):
        return {"status": "error", "message": "엔드포인트를 찾을 수 없습니다"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"서버 오류: {str(error)}")
        return {"status": "error", "message": "서버 오류 발생"}, 500
    
    # 애플리케이션 컨텍스트에서 모델 import
    with app.app_context():
        from app.models import User, Upload, Token
        db.create_all()
    
    return app

def setup_logging(app):
    """구조화된 로깅 설정"""
    if not app.debug:
        # JSON 로거 설정
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter()
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)
