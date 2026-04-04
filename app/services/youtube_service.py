from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import logging

logger = logging.getLogger(__name__)


class YouTubeService:
    """YouTube Data API v3 - Official Library Implementation"""
    
    def __init__(self, access_token, refresh_token=None):
        """Initialize with OAuth tokens"""
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id='YOUR_CLIENT_ID',
            client_secret='YOUR_CLIENT_SECRET'
        )
        self.access_token = access_token
    
    def upload_video(self, file_path, title, description='', tags=None):
        """Upload video to YouTube"""
        if not self.access_token:
            logger.error("No access token")
            return {'error': 'Access token not available'}
        
        try:
            logger.info(f"Starting upload: {title}")
            
            # Build YouTube API client
            youtube = build('youtube', 'v3', credentials=self.credentials)
            
            # Prepare request body
            request_body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags if tags else [],
                    'categoryId': '22',
                    'defaultLanguage': 'ko',
                    'defaultAudioLanguage': 'ko'
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create media upload
            media = MediaFileUpload(
                file_path,
                mimetype='video/mp4',
                resumable=True,
                chunksize=10 * 1024 * 1024  # 10MB chunks
            )
            
            # Insert video
            request = youtube.videos().insert(
                part='snippet,status',
                body=request_body,
                media_body=media
            )
            
            logger.info("Uploading to YouTube...")
            response = None
            while response is None:
                try:
                    status, response = request.next_chunk()
                    if status:
                        logger.info(f"Upload progress: {int(status.progress() * 100)}%")
                except Exception as e:
                    logger.error(f"Upload chunk error: {str(e)}")
                    return {'error': f'Chunk upload failed: {str(e)}'}
            
            video_id = response.get('id')
            if not video_id:
                logger.error("No video ID in response")
                return {'error': 'No video ID in response'}
            
            logger.info(f"Upload successful: {video_id}")
            return {
                'success': True,
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            }
        
        except Exception as e:
            logger.error(f"Upload exception: {str(e)}")
            return {'error': f'Upload failed: {str(e)}'}
    
    def get_channel_info(self):
        """Get YouTube channel information"""
        if not self.access_token:
            logger.error("No access token")
            return {'error': 'Access token not available'}
        
        try:
            youtube = build('youtube', 'v3', credentials=self.credentials)
            
            request = youtube.channels().list(
                part='snippet,statistics',
                mine=True
            )
            
            response = request.execute()
            
            if not response.get('items'):
                logger.error("No channel found")
                return {'error': 'No channel found'}
            
            channel = response['items'][0]
            return {
                'channel_id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet']['description'],
                'subscriber_count': channel['statistics'].get('subscriberCount', 0),
                'video_count': channel['statistics'].get('videoCount', 0)
            }
        
        except Exception as e:
            logger.error(f"Channel info error: {str(e)}")
            return {'error': f'Failed to get channel info: {str(e)}'}
