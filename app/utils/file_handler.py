# app/utils/file_handler.py
import os
import mimetypes
from werkzeug.utils import secure_filename
from datetime import datetime

class FileHandler:
    """동영상 파일 처리 유틸"""
    
    # 설정
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm', 'flv'}
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..', 'uploads')
    
    @classmethod
    def init_upload_folder(cls):
        """업로드 폴더 생성"""
        os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)
    
    @classmethod
    def validate_file(cls, file):
        """파일 검증 (확장자, 크기, MIME 타입)"""
        errors = []
        
        if not file or file.filename == '':
            errors.append('파일을 선택해주세요')
            return False, errors
        
        # 1. 파일명 검증
        filename = secure_filename(file.filename)
        if not filename:
            errors.append('유효하지 않은 파일명입니다')
            return False, errors
        
        # 2. 확장자 검증
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if ext not in cls.ALLOWED_EXTENSIONS:
            errors.append(f'지원하지 않는 형식입니다. (지원: {", ".join(cls.ALLOWED_EXTENSIONS)})')
            return False, errors
        
        # 3. MIME 타입 검증
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type or not mime_type.startswith('video'):
            errors.append('동영상 파일만 업로드 가능합니다')
            return False, errors
        
        # 4. 파일 크기 검증
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > cls.MAX_FILE_SIZE:
            errors.append(f'파일이 너무 큽니다 (최대: 500MB, 현재: {file_size / 1024 / 1024:.2f}MB)')
            return False, errors
        
        if file_size == 0:
            errors.append('빈 파일입니다')
            return False, errors
        
        return True, []
    
    @classmethod
    def save_file(cls, file, user_id):
        """파일을 서버에 저장하고 경로 반환"""
        cls.init_upload_folder()
        
        # 파일명 생성: timestamp_userid_originalname
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(file.filename)
        new_filename = f"{timestamp}_user{user_id}_{filename}"
        filepath = os.path.join(cls.UPLOAD_FOLDER, new_filename)
        
        # 파일 저장
        file.save(filepath)
        
        return {
            'filename': new_filename,
            'filepath': filepath,
            'file_size': os.path.getsize(filepath)
        }
    
    @classmethod
    def get_file_info(cls, filepath):
        """파일 정보 조회"""
        if not os.path.exists(filepath):
            return None
        
        return {
            'size': os.path.getsize(filepath),
            'created': os.path.getctime(filepath),
            'modified': os.path.getmtime(filepath)
        }
