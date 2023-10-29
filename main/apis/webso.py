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
def handle_message(sid):
    # Check if the session ID is valid
    if sid:
        # Get the fixed monitor info
        info = get_fixed_monitor_info(sid)
        # Emit the info to the client
        emit('updateFixed', {"fixedMonitorInfo": info})


@socketio.on('updateDynamic')
def handle_message(sid):
    # Check if the session ID is valid
    if sid:
        # Get the dynamic monitor info
        info = get_dynamic_monitor_info()
        # Emit the info to the client
        emit('updateDynamic', {"dynamicMonitorInfo": info})


def get_fixed_monitor_info(sid):
    # Return the fixed monitor info from the fixed_monitors dictionary
    return fixed_monitors.get(sid, FixedMonitor()).__dict__


def get_dynamic_monitor_info():
    # Return the dynamic monitor info from the DynamicMonitor class
    return DynamicMonitor().message
