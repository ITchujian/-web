"""
@File: __init__.py.py
@Author: 秦宇
@Created: 2023/10/25 20:34
@Description: Created in backend.
"""
from flask import Flask
from flask_cors import *
from .apis.user import user_bp, SECRET_KEY
from .apis.spider import spider_bp
from .apis.webso import websocket_bp, socketio


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(spider_bp, url_prefix='/api/spider')
    app.register_blueprint(websocket_bp, url_prefix='/monitor')
    socketio.init_app(app, cors_allowed_origins='*')
    CORS(app)
    return app, socketio
