import os
import pickle
import json
import base64
from flask import Flask, jsonify, request
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests
import tempfile

app = Flask(__name__)

API_KEY = "youtube-shorts-api-key-2026"
CHANNEL_ID = "UCn4-Z_7ixsnNaGKsPWGUe2A"

def get_oauth_credentials():
    """OAuth 토큰 로드 (유일한 인증 방법)"""
    oauth_token_b64 = os.getenv('OAUTH_TOKEN_B64')
    
    if not oauth_token_b64:
        raise Exception("❌ OAUTH_TOKEN_B64 환경변수가 없습니다!")
    
    try:
        token_data = base64.b64decode(oauth_token_b64)
        creds = pickle.loads(token_data)
        
        # 토큰 갱신
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        print("✅ OAuth 토큰 로드 성공")
        return creds
    except Exception as e:
        raise Exception(f"❌ OAuth 토큰 로드 실패: {str(e)}")

def get_youtube_service():
    """YouTube API 초기화"""
    creds = get_oauth_credentials()
    service = build('youtube', 'v3', credentials=creds)
    print("✅ YouTube 서비스 생성 완료")
    return service

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'YouTube Shorts Automation',
        'version': '4.0',
        'auth': 'OAuth 2.0 only'
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'OK'})

@app.route('/test-auth', methods=['GET'])
def test_auth():
    """인증 확인"""
    try:
        # API Key 검증
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({'error': 'Invalid API Key'}), 401
        
        # YouTube 서비스 생성 및 채널 정보 확인
        service = get_youtube_service()
        channels = service.channels().list(part='snippet', mine=True).execute()
        
        if not channels.get('items'):
            return jsonify({'error': 'No channel found'}), 400
        
        channel = channels['items'][0]
        
        return jsonify({
            'success': True,
            'auth_method': 'OAuth 2.0',
            'message': '✅ OAuth 인증 성공',
            'channel_name': channel['snippet']['title'],
            'channel_id': channel['id']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'❌ 인증 실패: {str(e)}'
        }), 500

@app.route('/upload-shorts', methods=['POST'])
def upload_shorts():
    """YouTube Shorts 업로드"""
    try:
        # API Key 검증
        api_key = request.headers.get('X-API-Key')
        if api_key != API_KEY:
            return jsonify({'error': 'Invalid API Key'}), 401
        
        # 요청 데이터
        data = request.get_json()
        title = data.get('title', 'YouTube Shorts')
        description = data.get('description', '')
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({'error': 'video_url 필수'}), 400
        
        print(f"📥 업로드 시작: {title}")
        
        # 동영상 다운로드
        print(f"📥 {video_url} 다운로드 중...")
        response = requests.get(video_url, stream=True, timeout=30)
        response.raise_for_status()
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        temp_file.close()
        
        print(f"✅ 다운로드 완료: {temp_file.name}")
        
        # YouTube에 업로드
        service = get_youtube_service()
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'categoryId': '22'
            },
            'status': {
                'privacyStatus': 'public'
            }
        }
        
        media = MediaFileUpload(temp_file.name, mimetype='video/mp4', resumable=True)
        
        print("📤 YouTube에 업로드 중...")
        insert_request = service.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = insert_request.execute()
        
        # 임시 파일 삭제
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
        
        print(f"✅ 업로드 성공! Video ID: {response['id']}")
        
        return jsonify({
            'success': True,
            'message': '✅ 업로드 성공',
            'video_id': response['id'],
            'channel_id': CHANNEL_ID,
            'url': f"https://youtube.com/watch?v={response['id']}"
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'❌ 업로드 실패: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
