from flask import Blueprint

# Blueprint 정의
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
upload_bp = Blueprint('upload', __name__, url_prefix='/upload')

# 라우트 임포트 (순환 import 방지)
from app.routes.auth import *
from app.routes.upload import *
