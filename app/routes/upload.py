# app/routes/upload.py
from flask import Blueprint, request, jsonify, session
from app.utils import FileHandler
from app.models import Upload
from app import db
from datetime import datetime

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')
file_handler = FileHandler()

@upload_bp.route('/', methods=['GET', 'POST'])
def upload_video():
    """파일 업로드 처리"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    if request.method == 'GET':
        return jsonify({'status': 'ready', 'message': 'Upload endpoint active'}), 200
    
    # POST: 파일 업로드
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    
    file = request.files['file']
    user_id = session['user_id']
    
    # 파일 검증
    is_valid, errors = file_handler.validate_file(file)
    if not is_valid:
        return jsonify({'status': 'error', 'message': errors}), 400
    
    # 파일 저장
    try:
        filename, filepath, size = file_handler.save_file(file, user_id)
        
        # DB에 Upload 레코드 생성
        upload_record = Upload(
            user_id=user_id,
            filename=filename,
            file_path=filepath,
            file_size=size,
            status='pending',
            created_at=datetime.utcnow()
        )
        db.session.add(upload_record)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'File uploaded successfully',
            'upload_id': upload_record.id,
            'filename': filename,
            'size': size
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@upload_bp.route('/history', methods=['GET'])
def upload_history():
    """사용자 업로드 기록 조회"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    uploads = Upload.query.filter_by(user_id=user_id).order_by(Upload.created_at.desc()).all()
    
    return jsonify({
        'status': 'success',
        'uploads': [
            {
                'id': u.id,
                'filename': u.filename,
                'file_size': u.file_size,
                'status': u.status,
                'created_at': u.created_at.isoformat() if u.created_at else None
            } for u in uploads
        ]
    }), 200
