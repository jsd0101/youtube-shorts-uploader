from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='.', static_url_path='')

@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

@app.route("/status")
def status():
    return jsonify({
        "status": "running",
        "flask_env": os.getenv('FLASK_ENV', 'development'),
        "port": os.getenv('PORT', '5000')
    })

@app.route("/auth/login")
def login():
    return jsonify({
        "status": "redirect",
        "message": "Google 로그인으로 이동",
        "redirect_url": "https://accounts.google.com/o/oauth2/v2/auth"
    })

@app.route("/auth/logout")
def logout():
    return jsonify({
        "status": "success",
        "message": "로그아웃 완료"
    })

@app.route("/upload")
def upload():
    return jsonify({
        "status": "ready",
        "message": "YouTube 업로드 준비 완료",
        "methods": ["GET", "POST"]
    })

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print(f"INFO: Flask 시작! PORT={port}")
    app.run(host="0.0.0.0", port=port, debug=False)
