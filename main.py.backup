import os
import pickle
import base64
from flask import Flask, jsonify, request
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests
import tempfile

app = Flask(__name__)

API_KEY = os.getenv('API_KEY', 'youtube-shorts-api-key-2026')
CHANNEL_ID = 'UCn4-Z_7ixsnNaGKsPWGUe2A'
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def load_oauth_token():
    oauth_token_b64 = os.getenv('OAUTH_TOKEN_B64')
    if not oauth_token_b64:
        raise Exception("OAUTH_TOKEN_B64 not found")
    creds = pickle.loads(base64.b64decode(oauth_token_b64))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

def get_youtube_service():
    creds = load_oauth_token()
    return build('youtube', 'v3', credentials=creds)

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status':'YouTube Shorts API','auth':'OAuth 2.0'})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status':'healthy'})

@app.route('/test-auth', methods=['GET'])
def test_auth():
    if request.headers.get('X-API-Key') != API_KEY:
        return jsonify({'error':'Invalid API Key'}), 401
    try:
        yt = get_youtube_service()
        info = yt.channels().list(part='snippet', mine=True).execute()
        ch = info['items'][0]
        return jsonify({'success':True,'auth_method':'OAuth 2.0','message':'✅ OAuth 인증 성공','channel_name':ch['snippet']['title'],'channel_id':ch['id']})
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}), 401

@app.route('/upload-shorts', methods=['POST'])
def upload_shorts():
    if request.headers.get('X-API-Key') != API_KEY:
        return jsonify({'error':'Invalid API Key'}), 401
    try:
        data = request.get_json()
        yt = get_youtube_service()
        resp = requests.get(data['video_url'], timeout=30, stream=True)
        tmp = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk: tmp.write(chunk)
        tmp.close()
        body = {'snippet':{'title':data['title'],'description':data.get('description',''),'categoryId':'22'},'status':{'privacyStatus':'public'}}
        media = MediaFileUpload(tmp.name, mimetype='video/mp4', resumable=True)
        result = yt.videos().insert(part='snippet,status', body=body, media_body=media).execute()
        if os.path.exists(tmp.name): os.remove(tmp.name)
        return jsonify({'success':True,'message':'✅ 업로드 성공','video_id':result['id'],'channel_id':CHANNEL_ID})
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
