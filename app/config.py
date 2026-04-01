import os
from datetime import timedelta

class Config:
    """공통 설정"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

class DevelopmentConfig(Config):
    """개발 환경"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///youtube_shorts.db')
    SESSION_COOKIE_SECURE = False

class ProductionConfig(Config):
    """프로덕션 환경 (Railway)"""
    DEBUG = False
    # Railway에서 DATABASE_URL이 없으면 SQLite 사용 (fallback)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///youtube_shorts.db')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': DevelopmentConfig
}

