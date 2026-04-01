import os
from dotenv import load_dotenv
from app import create_app

# .env 파일 로드
load_dotenv()

# 설정 이름 가져오기 (기본값: development)
config_name = os.getenv('FLASK_ENV', 'development')

# Flask 앱 생성
app = create_app(config_name)

if __name__ == '__main__':
    # 환경 정보 출력
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = config_name == 'development'
    
    print('=' * 60)
    print('INFO: Flask 서버 시작')
    print(f'HOST={host}, PORT={port}, DEBUG={debug}')
    print(f'FLASK_ENV={config_name}')
    print('=' * 60)
    
    # Flask 실행
    app.run(host=host, port=port, debug=debug)
