import os
from flask import Flask, jsonify
from app.extensions import db, oauth
from flask_cors import CORS

def create_app(config_name=None):
    """Flask app factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    app = Flask(__name__)
    from app.config import config
    app.config.from_object(config[config_name])
    db.init_app(app)
    oauth.init_app(app)
    CORS(app)
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )
    
    @app.route('/')
    def home():
        """홈 페이지"""
        return jsonify({
            'message': 'YouTube Shorts Uploader API',
            'version': '1.0',
            'endpoints': {
                'auth': {
                    'login': '/auth/login',
                    'logout': '/auth/logout',
                    'status': '/auth/status'
                },
                'upload': {
                    'upload': '/upload/',
                    'list': '/upload/list'
                }
            }
        }), 200
    
    with app.app_context():
        db.create_all()
        from app.routes import auth_bp, upload_bp
        app.register_blueprint(auth_bp)
        app.register_blueprint(upload_bp)
    return app
