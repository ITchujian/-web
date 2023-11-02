"""
@File: user.py
@Author: 秦宇
@Created: 2023/11/2 17:42
@Description: Created in backend.
"""
from .base import *

user_bp = Blueprint('user', __name__)


@user_bp.route('/login', methods=['POST'])
@handle_exceptions
def login():
    username = request.form.get('uname')
    password = request.form.get('upwd')
    if password:
        password = Password.encrypt_password(password)
    user = mysql.select('users', ['uid', 'uname', 'upwd'], f'uname={username!r}')
    if user and user[0] and user[0][2] == password:
        token = Token.generate(*user[0], secret_key=SECRET_KEY)
        return jsonify({'success': True, 'msg': '登录成功', 'token': token}), 200
    else:
        return jsonify({'success': False, 'msg': '登录失败', 'token': None}), 401


@user_bp.route('/login/state', methods=['GET'])
@handle_exceptions
@auth
def state(user):
    return jsonify({'success': True, 'msg': '已登录', 'user': user['uname']})
