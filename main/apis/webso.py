"""
@File: webso.py
@Author: 秦宇
@Created: 2023/10/26 18:06
@Description: Created in backend.
"""
from .base import *
from flask import Blueprint, request
from flask_socketio import emit, SocketIO
from ..models.monitor import fixed_monitors, FixedMonitor, dynamic_monitors, DynamicMonitor

websocket_bp = Blueprint('websocket', __name__)
socketio = SocketIO()

USER = {}


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    token = request.args.get('token')
    token = Token.unravel(token, secret_key=SECRET_KEY)
    token_id = token['tokenId']
    if token_id in USER:
        print(f'{token_id} 已存在')
    else:
        USER[token_id] = {'sid': request.sid}
    dynamic_monitors[token_id] = DynamicMonitor()


@socketio.on('disconnect')
def handle_disconnect():
    del_token_id = None
    for token_id, dic in USER.items():
        if dic.get('sid') == request.sid:
            del_token_id = token_id
            break
    if del_token_id:
        USER.pop(del_token_id)
    print('Client disconnected')


@socketio.on('updateFixed')
def handle_message(userId):
    try:
        token = request.args.get('token')
        token = Token.unravel(token, secret_key=SECRET_KEY)
        token_id = token['tokenId']
        user_dic = USER.get(token_id)
        info = get_fixed_monitor_info(userId)
        emit('updateFixed', {"fixedMonitorInfo": info}, to=user_dic.get('sid'))
    except Exception as e:
        pass


@socketio.on('updateDynamic')
def handle_message(userId):
    try:
        token = request.args.get('token')
        token = Token.unravel(token, secret_key=SECRET_KEY)
        token_id = token['tokenId']

        user_dic = USER.get(token_id)
        info = get_dynamic_monitor_info(token_id)

        admins = mysql.select('users', ['uid'], 'is_admin=1')
        for admin in admins:
            admin_token = mysql.select('sessions', ['tokenId'], f"uid={admin[0]!r}")
            if admin_token[0][0] in USER and admin_token[0][0] != token_id:
                admin_dic = USER.get(admin_token[0][0])
                emit('updateDynamic', {"dynamicMonitorInfo": info, "user": token['uname']}, to=admin_dic.get('sid'))
        emit('updateDynamic', {"dynamicMonitorInfo": info, "user": token['uname']}, to=user_dic.get('sid'))
    except Exception as e:
        pass


def get_fixed_monitor_info(userId):
    return fixed_monitors.get(userId, FixedMonitor()).__dict__


def get_dynamic_monitor_info(token_id):
    return dynamic_monitors.get(token_id).message
