"""
@File: base.py
@Author: 秦宇
@Created: 2023/11/2 17:44
@Description: Created in backend.
"""
import functools
from ..utils.auth import *
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
                return func(user, *args, **kwargs)
            else:
                return jsonify({'success': False, 'msg': '登录已过期', 'token': None}), 401
        return jsonify({'success': False, 'msg': '未登录', 'token': None}), 401

    return decorated
