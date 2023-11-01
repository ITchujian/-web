"""
@File: webso.py
@Author: 秦宇
@Created: 2023/10/26 18:06
@Description: Created in backend.
"""
from flask import Blueprint
from flask_socketio import emit, SocketIO
from ..models.monitor import fixed_monitors, FixedMonitor, DynamicMonitor

websocket_bp = Blueprint('websocket', __name__)
socketio = SocketIO()


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('updateFixed')
def handle_message(userId):
    if userId:
        info = get_fixed_monitor_info(userId)
        emit('updateFixed', {"fixedMonitorInfo": info})


@socketio.on('updateDynamic')
def handle_message(userId):
    if userId:
        info = get_dynamic_monitor_info()
        emit('updateDynamic', {"dynamicMonitorInfo": info})


def get_fixed_monitor_info(userId):
    return fixed_monitors.get(userId, FixedMonitor()).__dict__


def get_dynamic_monitor_info():
    return DynamicMonitor().message
