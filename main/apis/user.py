"""
@File: user.py
@Author: 秦宇
@Created: 2023/11/2 17:42
@Description: Created in backend.
"""
import datetime

from .base import *

user_bp = Blueprint('user', __name__)


@user_bp.route('/login', methods=['POST'])
@handle_exceptions
def login():
    username = request.form.get('uname')
    password = request.form.get('upwd')
    if not username:
        return jsonify({'success': False, 'msg': '用户名不能为空', 'token': None}), 401
    if not password:
        return jsonify({'success': False, 'msg': '密码不能为空', 'token': None}), 401
    else:
        password = Password.encrypt(password)
    user = mysql.select('users', ['uid', 'uname', 'upwd', 'error', 'is_wait', 'wait_time'], f'uname={username!r}')
    if user and user[0]:
        if user[0][4]:
            if get_current_time() >= user[0][5]:
                mysql.update('users', {'error': 0, 'is_wait': 0, 'update_time': get_current_time()},
                             condition=f'uid={user[0][0]!r}')
                user = mysql.select('users', ['uid', 'uname', 'upwd', 'error', 'is_wait', 'wait_time'],
                                    f'uname={username!r}')
            else:
                remain_second = (user[0][5] - get_current_time()).seconds
                return jsonify({'success': False, 'msg': '登录失败', 'remain_second': remain_second}), 403

        if user[0][2] == password:
            token = Token.create(*user[0][:3], secret_key=SECRET_KEY)
            source = Token.unravel(token, secret_key=SECRET_KEY)
            mysql.update('users', {'error': 0, 'is_wait': 0, 'update_time': get_current_time()},
                         condition=f'uid={user[0][0]!r}')
            mysql.update('sessions', {'tokenId': source['tokenId']}, condition=f'uid={user[0][0]!r}')
            return jsonify({'success': True, 'msg': '登录成功', 'token': token}), 200
        else:
            if user[0][3] >= Config.LOGIN_FAILURE_LIMIT - 1:
                mysql.update('users',
                             {'is_wait': 1, 'wait_time': cal_minute_time(Config.LOCK_TIME),
                              'update_time': get_current_time()},
                             condition=f'uid={user[0][0]!r}')
            else:
                mysql.update('users', {'error': user[0][3] + 1, 'update_time': get_current_time()},
                             condition=f'uid={user[0][0]!r}')
            return jsonify({'success': False, 'msg': '登录失败', 'count': 3 - user[0][3] - 1}), 400
    else:
        return jsonify({'success': False, 'msg': '登录失败', 'token': None}), 401


@user_bp.route('/login/state', methods=['GET'])
@handle_exceptions
@auth
def state(user):
    return jsonify({'success': True, 'msg': '已登录', 'user': user['uname']})


@user_bp.route('/info', methods=['GET'])
@handle_exceptions
@auth
def info(user):
    user_info = mysql.select('users', fields=list(Config.USER_FIELDS), condition=f'uid={user["uid"]!r}')
    if user_info:
        user_info = dict(zip(Config.USER_FIELDS, user_info[0]))
    return jsonify({'success': True, 'msg': '获取成功', 'user': user_info})


@user_bp.route('/logout', methods=['GET'])
@handle_exceptions
@auth
def logout(user):
    mysql.update('sessions', data={'tokenId': ''}, condition=f'uid={user["uid"]!r}')
    return jsonify({'success': True, 'msg': '退出成功'})
