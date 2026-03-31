# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from app.config import config

db = SQLAlchemy()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # SECRET_KEY 설정 (세션용)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    db.init_app(app)
    CORS(app)
    
    with app.app_context():
        db.create_all()
    
    from app.routes import auth_bp, upload_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(upload_bp)
    
    return app
