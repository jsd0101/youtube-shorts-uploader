# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS  # 추가
from app.config import config

db = SQLAlchemy()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    CORS(app)  # 추가: 모든 라우트에 CORS 활성화
    
    with app.app_context():
        db.create_all()
    
    from app.routes import auth_bp, upload_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    
    return app
