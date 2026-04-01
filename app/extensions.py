from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth

# 확장 객체를 먼저 생성 (앱 없이)
db = SQLAlchemy()
oauth = OAuth()
