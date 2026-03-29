from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask 서버 정상 실행!"

@app.route("/status")
def status():
    return jsonify({
        "status": "running",
        "flask_env": os.getenv('FLASK_ENV', 'development'),
        "port": os.getenv('PORT', '5000')
    })

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    print(f"INFO: Flask 시작! PORT={port}")
    app.run(host="0.0.0.0", port=port, debug=False)

