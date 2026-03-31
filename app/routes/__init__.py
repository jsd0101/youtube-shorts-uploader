# app/routes/__init__.py
from flask import Blueprint
from app.routes.auth import auth_bp
from app.routes.upload import upload_bp

__all__ = ['auth_bp', 'upload_bp']
