# 빌드 스테이지
FROM python:3.12-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 빌드 도구 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libffi-dev \
    libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# pip 업그레이드
RUN pip install --upgrade pip setuptools wheel

# 휠 파일 생성
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# 런타임 스테이지
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 빌더 스테이지에서 휠 복사
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# 휠에서 설치 (빌드 도구 필요 없음)
RUN pip install --no-cache /wheels/*

# 앱 코드 복사
COPY . .

# Flask 실행
CMD ["python", "app.py"]
