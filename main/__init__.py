"""
@File: __init__.py.py
@Author: 秦宇
@Created: 2023/10/25 20:34
@Description: Created in backend.
"""
from flask import Flask, make_response
from flask_cors import *
from .apis.spider import spider_bp
from .apis.webso import websocket_bp, socketio


def create_app():
    app = Flask(__name__)
    app.secret_key = '20010908gupingan'
    app.register_blueprint(spider_bp, url_prefix='/api/spider')
    app.register_blueprint(websocket_bp, url_prefix='/monitor')
    socketio.init_app(app, cors_allowed_origins='*')
    CORS(app)
    return app, socketio
