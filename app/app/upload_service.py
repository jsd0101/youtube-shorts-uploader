import os
from werkzeug.utils import secure_filename

class UploadService:
    """파일 업로드 서비스"""
    
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'flv', 'webm'}
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')
    
    @staticmethod
    def allowed_file(filename):
        """파일 확장자 검증"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in UploadService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def save_upload(file, title, description):
        """파일 저장"""
        if not file:
            return {'error': 'No file provided'}, 400
        
        if not UploadService.allowed_file(file.filename):
            return {'error': 'File type not allowed'}, 400
        
        filename = secure_filename(file.filename)
        os.makedirs(UploadService.UPLOAD_FOLDER, exist_ok=True)
        filepath = os.path.join(UploadService.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        return {
            'message': 'File uploaded successfully',
            'filename': filename,
            'title': title,
            'description': description,
            'filepath': filepath
        }, 200
    
    @staticmethod
    def get_uploads():
        """업로드된 파일 목록 조회"""
        uploads = []
        if os.path.exists(UploadService.UPLOAD_FOLDER):
            for filename in os.listdir(UploadService.UPLOAD_FOLDER):
                uploads.append({
                    'filename': filename,
                    'path': os.path.join(UploadService.UPLOAD_FOLDER, filename)
                })
        return {'uploads': uploads}, 200
