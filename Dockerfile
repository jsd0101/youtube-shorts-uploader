FROM python:3.12-slim

WORKDIR /app

# PostgreSQL 개발 라이브러리 설치 (핵심!)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 프로덕션 WSGI 서버
CMD ["gunicorn", "--workers=4", "--bind=0.0.0.0:8080", "run:app"]
