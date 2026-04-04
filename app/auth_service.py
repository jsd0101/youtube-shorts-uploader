from flask import session

class AuthService:
    """Google OAuth 인증 서비스"""
    
    @staticmethod
    def save_user_session(user_data, token_data):
        """사용자 정보를 세션에 저장"""
        session['user'] = user_data
        session['token'] = token_data
        return True
    
    @staticmethod
    def get_user_session():
        """세션에서 사용자 정보 조회"""
        return session.get('user')
    
    @staticmethod
    def clear_user_session():
        """세션에서 사용자 정보 삭제"""
        session.pop('user', None)
        session.pop('token', None)
        return True
    
    @staticmethod
    def is_logged_in():
        """로그인 상태 확인"""
        return 'user' in session
