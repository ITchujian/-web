"""
@File: token.py
@Author: 秦宇
@Created: 2023/11/2 18:50
@Description: Created in backend.
"""
import hashlib
import time

import jwt


class Password:
    @staticmethod
    def encrypt_password(password: str) -> str:
        md5_hash = hashlib.md5()
        md5_hash.update(password.encode('utf-8'))
        encrypted_password = md5_hash.hexdigest()
        return encrypted_password


class Token:
    @staticmethod
    def generate(uid: int, uname: str, upwd: str, secret_key: str) -> str:
        payload = {
            'uid': uid,
            'uname': uname,
            'upwd': upwd,
            'exp': int(time.time()) + 3600,
        }
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    @staticmethod
    def unravel(token: str, secret_key: str) -> dict:
        """
        解析token
        :param token:
        :param secret_key:
        :return: uid, uname, upwd, exp
        """
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            return payload
        except Exception as e:
            return {
                'uid': None,
                'uname': None,
                'upwd': None,
                'exp': None,
                'error': e
            }

    @staticmethod
    def is_valid(token: str, secret_key: str) -> bool:
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            if payload['exp'] > int(time.time()):
                return True
            else:
                return False
        except jwt.InvalidTokenError:
            return False
        except Exception:
            return False
