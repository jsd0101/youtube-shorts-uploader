from flask import jsonify, request
from app.routes import upload_bp
from app.services.upload_service import UploadService

@upload_bp.route('/', methods=['GET', 'POST'])
def upload():
    """파일 업로드"""
    if request.method == 'POST':
        try:
            file = request.files.get('file')
            title = request.form.get('title', 'Untitled')
            description = request.form.get('description', '')
            
            result, status_code = UploadService.save_upload(file, title, description)
            return jsonify(result), status_code
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return jsonify({'message': 'Upload endpoint'}), 200

@upload_bp.route('/list', methods=['GET'])
def list_uploads():
    """업로드된 파일 목록"""
    try:
        result, status_code = UploadService.get_uploads()
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

