from flask import jsonify, session, url_for
from app.routes import auth_bp
from app import oauth
from app.services.auth_service import AuthService

@auth_bp.route('/login', methods=['GET'])
def login():
    """Google OAuth 로그인 시작"""
    redirect_uri = url_for('auth.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/authorize', methods=['GET'])
def authorize():
    """Google OAuth 콜백"""
    try:
        token = oauth.google.authorize_access_token()
        user = oauth.google.parse_id_token(token)
        AuthService.save_user_session(user, token)
        return jsonify({
            'message': 'Login successful',
            'user': user
        }), 200
    except Exception as e:
        return jsonify({'error': f'Authorization failed: {str(e)}'}), 400

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """로그아웃"""
    AuthService.clear_user_session()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/status', methods=['GET'])
def status():
    """로그인 상태 확인"""
    user = AuthService.get_user_session()
    if user:
        return jsonify({'logged_in': True, 'user': user}), 200
    return jsonify({'logged_in': False}), 200
