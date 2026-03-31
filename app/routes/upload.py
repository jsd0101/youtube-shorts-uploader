from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import os
from app.models import Upload, db
from app.utils.file_handler import FileHandler
from app.services.youtube_service import YouTubeService

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'GET':
        return jsonify({'message': 'Upload endpoint ready'}), 200
    
    # POST 요청 처리
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    
    # 파일 검증
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: mp4, mov, avi, mkv'}), 400
    
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        return jsonify({'error': f'File too large. Max: {MAX_FILE_SIZE / 1024 / 1024}MB'}), 400
    
    # 파일 저장
    filename = secure_filename(file.filename)
    upload_dir = '/tmp/uploads'
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    
    # 메타데이터 가져오기
    title = request.form.get('title', filename)
    description = request.form.get('description', '')
    tags = request.form.get('tags', '').split(',')
    tags = [tag.strip() for tag in tags if tag.strip()]
    
    # YouTube 업로드 시도
    try:
        # 사용자의 access_token 가져오기
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user or not user.access_token:
            return jsonify({'error': 'YouTube access token not available'}), 401
        
        # YouTubeService 초기화
        yt_service = YouTubeService(
            access_token=user.access_token,
            refresh_token=user.refresh_token
        )
        
        # YouTube에 업로드
        result = yt_service.upload_video(filepath, title, description, tags)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        # DB에 업로드 기록 저장
        upload_record = Upload(
            user_id=user_id,
            filename=filename,
            filepath=filepath,
            youtube_video_id=result.get('video_id'),
            youtube_url=result.get('url'),
            status='completed',
            title=title,
            description=description,
            tags=','.join(tags)
        )
        db.session.add(upload_record)
        db.session.commit()
        
        # 파일 삭제 (선택사항)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': 'Video uploaded to YouTube successfully',
            'video_id': result.get('video_id'),
            'youtube_url': result.get('url')
        }), 200
    
    except Exception as e:
        # DB에 실패 기록 저장
        upload_record = Upload(
            user_id=user_id,
            filename=filename,
            filepath=filepath,
            status='failed',
            error_message=str(e),
            title=title,
            description=description,
            tags=','.join(tags)
        )
        db.session.add(upload_record)
        db.session.commit()
        
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@upload_bp.route('/history', methods=['GET'])
def upload_history():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session['user_id']
    uploads = Upload.query.filter_by(user_id=user_id).all()
    
    history = [{
        'id': u.id,
        'filename': u.filename,
        'youtube_video_id': u.youtube_video_id,
        'youtube_url': u.youtube_url,
        'status': u.status,
        'title': u.title,
        'description': u.description,
        'tags': u.tags,
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in uploads]
    
    return jsonify(history), 200
