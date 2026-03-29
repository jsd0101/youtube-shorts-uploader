from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask 서버 정상 실행!"

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))  # Railway의 PORT 환경변수 사용
    print(f"INFO: Flask 시작! PORT={port}")
    app.run(host="0.0.0.0", port=port, debug=False)
