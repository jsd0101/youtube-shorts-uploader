# app/services/youtube_service.py
import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

class YouTubeService:
    """YouTube Data API v3를 사용하여 동영상을 업로드합니다."""
    
    # YouTube API 스코프
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    
    def __init__(self, access_token=None, refresh_token=None):
        """
        YouTube 서비스 초기화
        
        Args:
            access_token: Google OAuth 액세스 토큰
            refresh_token: Google OAuth 리프레시 토큰
        """
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.youtube = None
        
        if access_token:
            self._build_service_from_token(access_token, refresh_token)
    
    def _build_service_from_token(self, access_token, refresh_token=None):
        """토큰으로 YouTube 서비스 빌드"""
        try:
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                scopes=self.SCOPES
            )
            self.youtube = build('youtube', 'v3', credentials=credentials)
        except Exception as e:
            print(f"YouTube 서비스 빌드 실패: {str(e)}")
            raise
    
    def upload_video(self, file_path, title, description='', tags=None):
        """
        YouTube에 동영상 업로드
        
        Args:
            file_path: 업로드할 동영상 파일 경로
            title: 동영상 제목
            description: 동영상 설명
            tags: 동영상 태그 리스트
        
        Returns:
            동영상 ID 또는 에러 메시지
        """
        if not self.youtube:
            return {'error': 'YouTube 서비스가 초기화되지 않았습니다.'}
        
        try:
            # 동영상 메타데이터 설정
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '22',  # 22 = Shorts/Short movies
                    'defaultLanguage': 'ko',
                    'defaultAudioLanguage': 'ko'
                },
                'status': {
                    'privacyStatus': 'public'  # public, unlisted, private
                }
            }
            
            # 파일 업로드 설정
            media = MediaFileUpload(
                file_path,
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024*1024  # 1MB chunks
            )
            
            # 업로드 요청
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            # 업로드 실행
            response = None
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        print(f'Upload progress: {progress}%')
                except HttpError as e:
                    print(f'An error occurred: {e}')
                    return {'error': str(e)}
            
            video_id = response['id']
            return {
                'success': True,
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            }
        
        except HttpError as e:
            error_msg = f'YouTube API 오류: {e}'
            print(error_msg)
            return {'error': error_msg}
        except Exception as e:
            error_msg = f'업로드 중 오류 발생: {str(e)}'
            print(error_msg)
            return {'error': error_msg}
    
    def get_channel_info(self):
        """현재 인증된 채널 정보 조회"""
        try:
            request = self.youtube.channels().list(
                part='snippet,contentDetails,statistics',
                mine=True
            )
            response = request.execute()
            
            if response['items']:
                channel = response['items'][0]
                return {
                    'channel_id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', 0),
                    'video_count': channel['statistics'].get('videoCount', 0)
                }
            return {'error': '채널 정보를 찾을 수 없습니다.'}
        
        except Exception as e:
            return {'error': str(e)}
