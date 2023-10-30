"""
@File: test.py
@Author: 秦宇
@Created: 2023/10/30 14:12
@Description: Created in backend.
"""
import requests

res = requests.get('http://127.0.0.1:5000/api/spider/load')

print(res.json())