from flask import Blueprint, redirect, url_for, session, render_template
from app import oauth

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    """Google OAuth 로그인 페이지로 리다이렉트"""
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback')
def callback():
    """Google에서 돌아온 후 토큰 저장"""
    try:
        token = oauth.google.authorize_access_token()
        session['token'] = token
        session['user_info'] = token.get('userinfo')
        return redirect(url_for('upload.dashboard'))
    except Exception as e:
        return f'<h1>로그인 실패</h1><p>{str(e)}</p>', 400

@auth_bp.route('/logout')
def logout():
    """로그아웃"""
    session.clear()
    return redirect(url_for('index'))
