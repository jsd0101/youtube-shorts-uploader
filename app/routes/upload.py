from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import logging
from app.models import Upload, db, User
from app.services.youtube_service import YouTubeService

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__, url_prefix='/upload')
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB

def allowed_file(fname):
    return '.' in fname and fname.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/', methods=['GET', 'POST'])
def upload_video():
    """Upload video to YouTube"""
    logger.info("=== Upload request started ===")
    
    if request.method == 'GET':
        logger.info("GET /upload/ - returning ready message")
        return jsonify({'message': 'Upload endpoint ready'}), 200
    
    # POST request
    logger.info("POST /upload/ - processing upload")
    
    if 'user_id' not in session:
        logger.error("Not authenticated - no user_id in session")
        return jsonify({'error': 'Not authenticated'}), 401
    
    logger.info(f"User ID: {session['user_id']}")
    
    if 'file' not in request.files:
        logger.error("No file provided in request")
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or not allowed_file(file.filename):
        logger.error(f"Invalid file: {file.filename}")
        return jsonify({'error': 'Invalid file type. Allowed: mp4, mov, avi, mkv'}), 400
    
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        logger.error(f"File too large: {file.content_length} bytes")
        return jsonify({'error': f'File too large. Max: {MAX_FILE_SIZE/1024/1024}MB'}), 400
    
    filename = secure_filename(file.filename)
    logger.info(f"File received: {filename}")
    
    # Save file temporarily
    upload_dir = '/tmp/uploads'
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    
    try:
        file.save(filepath)
        logger.info(f"File saved to: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        return jsonify({'error': f'Failed to save file: {str(e)}'}), 500
    
    # Get metadata
    title = request.form.get('title', filename)
    description = request.form.get('description', '')
    tags = [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()]
    
    logger.info(f"Metadata - Title: {title}, Tags: {tags}")
    
    try:
        # Get user from database
        user = db.session.query(User).filter_by(id=session['user_id']).first()
        
        if not user:
            logger.error(f"User not found: {session['user_id']}")
            return jsonify({'error': 'User not found'}), 401
        
        if not user.access_token:
            logger.error(f"No access token for user: {session['user_id']}")
            return jsonify({'error': 'YouTube access token not available'}), 401
        
        logger.info(f"User found: {user.email}, uploading to YouTube...")
        
        # Upload to YouTube
        yt = YouTubeService(access_token=user.access_token, refresh_token=user.refresh_token)
        logger.info("YouTubeService initialized, calling upload_video()...")
        
        result = yt.upload_video(filepath, title, description, tags)
        logger.info(f"YouTube upload result: {result}")
        
        if 'error' in result:
            logger.error(f"YouTube upload error: {result['error']}")
            
            # Save failed record
            error_rec = Upload(
                user_id=session['user_id'],
                filename=filename,
                filepath=filepath,
                status='failed',
                error_message=result['error'],
                title=title,
                description=description,
                tags=','.join(tags)
            )
            db.session.add(error_rec)
            db.session.commit()
            logger.info(f"Failed upload record saved: {error_rec.id}")
            
            return jsonify({'error': result['error']}), 500
        
        # Save successful record
        logger.info(f"Upload successful! Video ID: {result.get('video_id')}")
        
        record = Upload(
            user_id=session['user_id'],
            filename=filename,
            filepath=filepath,
            youtube_video_id=result.get('video_id'),
            youtube_url=result.get('url'),
            status='completed',
            title=title,
            description=description,
            tags=','.join(tags)
        )
        db.session.add(record)
        db.session.commit()
        logger.info(f"Upload record saved: {record.id}")
        
        # Clean up temporary file
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Temporary file deleted: {filepath}")
        
        logger.info("=== Upload completed successfully ===")
        
        return jsonify({
            'success': True,
            'message': 'Video uploaded to YouTube successfully',
            'video_id': result.get('video_id'),
            'youtube_url': result.get('url')
        }), 200
    
    except Exception as e:
        logger.error(f"Upload exception: {str(e)}", exc_info=True)
        
        # Save error record
        try:
            error_rec = Upload(
                user_id=session['user_id'],
                filename=filename,
                filepath=filepath,
                status='failed',
                error_message=str(e),
                title=title,
                description=description,
                tags=','.join(tags)
            )
            db.session.add(error_rec)
            db.session.commit()
            logger.info(f"Error upload record saved: {error_rec.id}")
        except Exception as db_error:
            logger.error(f"Failed to save error record: {str(db_error)}")
        
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@upload_bp.route('/history', methods=['GET'])
def upload_history():
    """Get upload history for current user"""
    logger.info("GET /upload/history - fetching upload history")
    
    if 'user_id' not in session:
        logger.error("Not authenticated")
        return jsonify({'error': 'Not authenticated'}), 401
    
    logger.info(f"Fetching history for user: {session['user_id']}")
    
    try:
        uploads = Upload.query.filter_by(user_id=session['user_id']).all()
        logger.info(f"Found {len(uploads)} uploads")
        
        history = [
            {
                'id': u.id,
                'filename': u.filename,
                'youtube_video_id': u.youtube_video_id,
                'youtube_url': u.youtube_url,
                'status': u.status,
                'title': u.title,
                'description': u.description,
                'tags': u.tags,
                'error_message': u.error_message,
                'created_at': u.created_at.isoformat() if u.created_at else None
            }
            for u in uploads
        ]
        
        logger.info(f"Returning {len(history)} upload records")
        return jsonify(history), 200
    
    except Exception as e:
        logger.error(f"History fetch error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to fetch history: {str(e)}'}), 500
