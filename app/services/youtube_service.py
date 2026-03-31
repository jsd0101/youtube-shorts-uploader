import requests
import os


class YouTubeService:
    """YouTube Data API v3 - Simple HTTP Implementation"""
    
    def __init__(self, access_token=None, refresh_token=None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.upload_url = "https://www.googleapis.com/upload/youtube/v3/videos"
        self.api_url = "https://www.googleapis.com/youtube/v3"
    
    def upload_video(self, file_path, title, description="", tags=None):
        """Upload video to YouTube"""
        if not self.access_token:
            return {'error': 'No access token'}
        
        if not os.path.exists(file_path):
            return {'error': 'File not found'}
        
        try:
            # Prepare metadata
            metadata = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags if tags else [],
                    'categoryId': '22'
                },
                'status': {'privacyStatus': 'public'}
            }
            
            # Step 1: Start resumable upload
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Goog-Upload-Protocol': 'resumable',
                'X-Goog-Upload-Command': 'start',
                'Content-Type': 'application/json'
            }
            
            file_size = os.path.getsize(file_path)
            headers['X-Goog-Upload-Header-Content-Length'] = str(file_size)
            headers['X-Goog-Upload-Header-Content-Type'] = 'video/mp4'
            
            params = {'part': 'snippet,status', 'uploadType': 'resumable'}
            
            response = requests.post(
                self.upload_url,
                json=metadata,
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code not in [200, 201]:
                return {'error': f'Failed to start upload: {response.text}'}
            
            upload_uri = response.headers.get('Location')
            if not upload_uri:
                return {'error': 'No upload URI'}
            
            # Step 2: Upload file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            upload_headers = {
                'X-Goog-Upload-Command': 'upload, finalize',
                'X-Goog-Upload-Offset': '0',
                'Content-Type': 'video/mp4'
            }
            
            upload_response = requests.put(
                upload_uri,
                data=file_data,
                headers=upload_headers,
                timeout=300
            )
            
            if upload_response.status_code not in [200, 201]:
                return {'error': f'Upload failed: {upload_response.text}'}
            
            result = upload_response.json()
            video_id = result.get('id')
            
            if not video_id:
                return {'error': 'No video ID'}
            
            return {
                'success': True,
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}'
            }
        
        except Exception as e:
            return {'error': f'Exception: {str(e)}'}
    
    def get_channel_info(self):
        """Get YouTube channel info"""
        if not self.access_token:
            return {'error': 'No access token'}
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            params = {'part': 'snippet,statistics', 'mine': 'true'}
            
            response = requests.get(
                f'{self.api_url}/channels',
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                return {'error': 'Failed to get channel'}
            
            data = response.json()
            if not data.get('items'):
                return {'error': 'No channel'}
            
            channel = data['items'][0]
            return {
                'channel_id': channel['id'],
                'title': channel['snippet']['title'],
                'subscribers': channel['statistics'].get('subscriberCount', 0)
            }
        
        except Exception as e:
            return {'error': f'Exception: {str(e)}'}
