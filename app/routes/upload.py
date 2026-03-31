# app/routes/upload.py
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from werkzeug.utils import secure_filename

def get_db_and_models():
    from app import db
    from app.models import Upload
    return db, Upload

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

_file_handler = None

def get_file_handler():
    global _file_handler
    if _file_handler is None:
        from app.utils import FileHandler
        _file_handler = FileHandler()
    return _file_handler

@upload_bp.route('/', methods=['GET', 'POST'])
def upload_video():
    """Handle file upload"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    if request.method == 'GET':
        return jsonify({'status': 'ready', 'message': 'Upload endpoint active'}), 200
    
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400
    
    file = request.files['file']
    user_id = session['user_id']
    file_handler = get_file_handler()
    
    is_valid, errors = file_handler.validate_file(file)
    if not is_valid:
        return jsonify({'status': 'error', 'message': errors}), 400
    
    try:
        filename, filepath, size = file_handler.save_file(file, user_id)
        db, Upload = get_db_and_models()
        
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
        db, Upload = get_db_and_models()
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@upload_bp.route('/history', methods=['GET'])
def upload_history():
    """Return a list of the user's upload records"""
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    db, Upload = get_db_and_models()
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
