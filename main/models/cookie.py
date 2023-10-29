"""
@File: cookie.py
@Author: 秦宇
@Created: 2023/10/27 16:37
@Description: Created in backend.
"""


class Cookie:
    def __init__(self, cookie_string=''):
        self.cookies = {}
        self.parse_cookie_string(cookie_string)

    def parse_cookie_string(self, cookie_string):
        if not cookie_string:
            return

        cookie_list = cookie_string.split('; ')
        for cookie in cookie_list:
            name_value = cookie.split('=')
            if len(name_value) == 2:
                name = name_value[0].strip()
                value = name_value[1].strip()
                self.cookies[name] = value

    def get_cookie_string(self):
        cookie_list = []
        for name, value in self.cookies.items():
            cookie_list.append(f"{name}={value}")
        return '; '.join(cookie_list)

    def set_cookie(self, name, value):
        self.cookies[name] = value

    def delete_cookie(self, name):
        if name in self.cookies:
            del self.cookies[name]
