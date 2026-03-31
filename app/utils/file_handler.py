# app/utils/file_handler.py
import os
from werkzeug.utils import secure_filename
from datetime import datetime

class FileHandler:
    """파일 업로드 검증 및 저장 클래스"""
    
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'}
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    
    def __init__(self):
        # Railway 임시 저장소 사용
        self.UPLOAD_FOLDER = '/tmp/uploads'
        self.init_upload_folder()
    
    def init_upload_folder(self):
        """업로드 폴더 생성"""
        if not os.path.exists(self.UPLOAD_FOLDER):
            os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
            print(f"✅ Upload folder created: {self.UPLOAD_FOLDER}")
    
    def validate_file(self, file):
        """파일 검증"""
        errors = []
        
        # 1. 파일 존재 확인
        if not file or file.filename == '':
            return False, "파일을 선택하세요"
        
        # 2. 파일명 보안 검증
        filename = secure_filename(file.filename)
        if not filename:
            return False, "잘못된 파일명입니다"
        
        # 3. 확장자 검증
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if ext not in self.ALLOWED_EXTENSIONS:
            return False, f"지원하지 않는 형식입니다. 허용: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        # 4. MIME 타입 검증
        if not file.content_type or not file.content_type.startswith('video/'):
            return False, "영상 파일만 업로드 가능합니다"
        
        # 5. 파일 크기 검증
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size == 0:
            return False, "빈 파일입니다"
        if size > self.MAX_FILE_SIZE:
            return False, f"파일 크기가 너무 큽니다 (최대 500MB)"
        
        return True, None
    
    def save_file(self, file, user_id):
        """파일 저장 및 정보 반환"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        original_ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{timestamp}_user{user_id}_{secure_filename(file.filename)}"
        filepath = os.path.join(self.UPLOAD_FOLDER, filename)
        
        try:
            file.save(filepath)
            size = os.path.getsize(filepath)
            print(f"✅ File saved: {filename} ({size} bytes)")
            return filename, filepath, size
        except Exception as e:
            print(f"❌ File save error: {str(e)}")
            raise Exception(f"파일 저장 실패: {str(e)}")
    
    def get_file_info(self, filepath):
        """파일 정보 조회"""
        if not os.path.exists(filepath):
            return None
        
        return {
            'size': os.path.getsize(filepath),
            'created': os.path.getctime(filepath),
            'modified': os.path.getmtime(filepath)
        }
