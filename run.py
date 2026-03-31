# run.py
import os
from dotenv import load_dotenv
from app import create_app

load_dotenv()

if __name__ == '__main__':
    config_name = os.getenv('FLASK_ENV', 'development')
    app = create_app(config_name)
    
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = config_name == 'development'
    
    print('='*60)
    print('INFO: Flask 시작!')
    print(f'HOST={host}, PORT={port}, FLASK_ENV={config_name}')
    print('='*60)
    
    app.run(host=host, port=port, debug=debug)
