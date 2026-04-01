import os
import sys
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

try:
    from app import create_app
    
    config_name = os.getenv('FLASK_ENV', 'development')
    print(f"[INFO] Creating app with config: {config_name}", file=sys.stderr)
    
    app = create_app(config_name)
    
    print(f"[INFO] App created successfully", file=sys.stderr)
    print(f"[INFO] Registered routes:", file=sys.stderr)
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}", file=sys.stderr)
    
except Exception as e:
    print(f"[ERROR] Failed to create app: {str(e)}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Gunicorn WSGI 진입점
if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = config_name == 'development'
    
    print(f"[INFO] Starting Flask server: {host}:{port}, DEBUG={debug}", file=sys.stderr)
    app.run(host=host, port=port, debug=debug)
