# YouTube Shorts Uploader

YouTube Shorts 자동 업로드 도구 (Google OAuth 인증 포함)

## 기능

- Google OAuth 인증
- YouTube Shorts 자동 업로드
- REST API 제공

## 환경 변수 설정

Railway에 배포할 때 다음 환경 변수를 설정하세요:

- `CLIENT_SECRET_JSON` - Google Cloud OAuth Client Secret JSON 내용
- `SECRET_KEY` - Flask 애플리케이션 시크릿 키

## 사용법

```bash
pip install -r requirements.txt
python app.py
