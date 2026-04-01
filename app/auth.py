from flask import jsonify, session, url_for
from app.routes import auth_bp
from app import oauth

@auth_bp.route('/login')
def login():
    """Google OAuth 로그인"""
    redirect_uri = url_for('auth.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/authorize')
def authorize():
    """Google OAuth 콜백"""
    try:
        token = oauth.google.authorize_access_token()
        user = oauth.google.parse_id_token(token)
        session['user'] = user
        return jsonify({'message': 'Login successful', 'user': user}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/logout')
def logout():
    """로그아웃"""
    session.pop('user', None)
    return jsonify({'message': 'Logged out'}), 200
