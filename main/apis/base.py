"""
@File: base.py
@Author: 秦宇
@Created: 2023/11/2 17:44
@Description: Created in backend.
"""
import functools
from ..utils.auth import *
from ..utils.helper import cal_minute_time, get_current_time, convert_datetime
from ..utils.dbtool import mysql
from flask import Blueprint, jsonify, request
from ..config.settings import *


def handle_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            print(e)
            return jsonify({
                'success': False,
                'message': 'An error occurred.',
                'data': []
            }), 500

    return wrapper


def auth(func):
    @functools.wraps(func)
    def decorated(*args, **kwargs):
        authorization_header = request.headers.get('Authorization')

        if authorization_header and authorization_header.startswith("Bearer "):
            token = authorization_header.split(" ")[1]
            if Token.is_valid(token, SECRET_KEY):
                user = Token.unravel(token, SECRET_KEY)
                db_token = mysql.select('sessions', ['uid', 'tokenId'], f'uid={user["uid"]!r}')
                if not db_token or db_token[0][1] != user['tokenId']:
                    return jsonify({'success': False, 'msg': 'Invalid token', 'token': None}), 401
                return func(user, *args, **kwargs)
            else:
                return jsonify({'success': False, 'msg': '登录已过期', 'token': None}), 401
        return jsonify({'success': False, 'msg': '未登录', 'token': None}), 401

    return decorated


def verify_limit(user):
    user_max_limit = mysql.select('users', ['max_limit'], condition=f'uid={user["uid"]!r}')
    if user_max_limit and user_max_limit[0]:
        user_max_limit = user_max_limit[0][0]
    else:
        return False
    current_num = len(mysql.select('users_spiders', ['`order`'], condition=f'uid={user["uid"]!r}'))
    if current_num >= user_max_limit:
        return False
    return True
