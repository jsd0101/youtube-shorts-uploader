from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Flask 서버 정상 실행!"

if __name__ == "__main__":
    print("INFO: Flask 시작!")
    app.run(host="0.0.0.0", port=5000)
