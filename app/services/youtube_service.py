import requests
import json
import os

class YouTubeService:
    """YouTube Data API v3 via raw HTTP requests"""
    YOUTUBE_UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
    YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, access_token=None, refresh_token=None):
        self.access_token = access_token
        self.refresh_token = refresh_token

    def upload_video(self, file_path, title, description='', tags=None):
        """Upload video to YouTube using resumable upload protocol"""
        if not self.access_token:
            return {'error': 'Access token not available'}
        
        try:
            # Prepare video metadata
            video_body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': '22',
                    'defaultLanguage': 'ko',
                    'defaultAudioLanguage': 'ko'
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Step 1: Initiate resumable upload
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Goog-Upload-Protocol': 'resumable',
                'X-Goog-Upload-Command': 'start',
                'X-Goog-Upload-Header-Content-Length': str(os.path.getsize(file_path)),
                'X-Goog-Upload-Header-Content-Type': 'video/mp4',
                'Content-Type': 'application/json'
            }
            params = {'part': 'snippet,status', 'uploadType': 'resumable'}
            
            response = requests.post(
                self.YOUTUBE_UPLOAD_URL,
                headers=headers,
                json=video_body,
                params=params,
                timeout=30
            )
            
            if response.status_code not in [200, 201]:
                return {'error': f'Failed to initiate upload: {response.text}'}
            
            upload_uri = response.headers.get('Location')
            if not upload_uri:
                return {'error': 'No upload URI received'}
            
            # Step 2: Upload video file
            with open(file_path, 'rb') as f:
                video_data = f.read()
            
            upload_headers = {
                'X-Goog-Upload-Command': 'upload, finalize',
                'X-Goog-Upload-Offset': '0',
                'Content-Type': 'video/mp4'
            }
            
            upload_response = requests.put(
                upload_uri,
                headers=upload_headers,
                data=video_data,
                timeout=300
            )
            
            if upload_response.status_code not in [200, 201]:
                return {'error': f'Upload failed: {upload_response.text}'}
            
            result = upload_response.json()
            video_id = result.get('id')
            
            if not video_id:
                return {'error': 'No video ID in response'}
            
            return {
                'success': True,
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            }
        
        except Exception as e:
            return {'error': f'Upload error: {str(e)}'}

    def get_channel_info(self):
        """Get YouTube channel information"""
        if not self.access_token:
            return {'error': 'Access token not available'}
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            params = {'part': 'snippet,contentDetails,statistics', 'mine': 'true'}
            
            response = requests.get(
                f'{self.YOUTUBE_API_URL}/channels',
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                return {'error': 'Failed to fetch channel info'}
            
            data = response.json()
            if not data.get('items'):
                return {'error': 'No channel found'}
            
            channel = data['items'][0]
            return {
                'channel_id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet']['description'],
                'subscriber_count': channel['statistics'].get('subscriberCount', 0),
                'video_count': channel['statistics'].get('videoCount', 0)
            }
        
        except Exception as e:
            return {'error': f'Error: {str(e)}'}
