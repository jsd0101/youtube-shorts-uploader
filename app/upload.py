from flask import jsonify, request
from app.routes import upload_bp

@upload_bp.route('/', methods=['GET', 'POST'])
def upload():
    """파일 업로드"""
    if request.method == 'POST':
        try:
            file = request.files.get('file')
            title = request.form.get('title', 'Untitled')
            description = request.form.get('description', '')
            
            if not file:
                return jsonify({'error': 'No file provided'}), 400
            
            # 파일 처리 로직 (추후 구현)
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': file.filename,
                'title': title
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'message': 'Upload endpoint'}), 200

@upload_bp.route('/list', methods=['GET'])
def list_uploads():
    """업로드된 파일 목록"""
    try:
        return jsonify({'uploads': []}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
