import os
from datetime import timedelta

class Config:
    """기본 설정"""
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
    """프로덕션 환경"""
    DEBUG = False
    # Railway 환경에서는 DATABASE_URL이 자동으로 설정됨
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///youtube_shorts.db')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': DevelopmentConfig
}

