"""
@File: spider.py
@Author: 秦宇
@Created: 2023/10/25 20:41
@Description: Created in backend.
"""
import functools

from ..models.task import runTask, spiderModels
from ..models.spider import Spider
from ..utils.dbtool import mysql
from ..config.settings import Config
from xhsAPI import Login
from flask import Blueprint, request, jsonify

spider_bp = Blueprint('spider', __name__)


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


@spider_bp.route('/qrcode', methods=['GET'])
@handle_exceptions
def qrcode():
    login = Login(Config.DEFAULT_COOKIES)
    qrcode_data = login.createQrcode()['data']

    return jsonify({
        'success': True,
        'msg': '获取二维码成功',
        'data': qrcode_data,
    })


@spider_bp.route('/qrcode/state', methods=['GET'])
@handle_exceptions
def qrcodeState():
    qr_id = request.args.get('qrId')
    code = request.args.get('code')
    login = Login(Config.DEFAULT_COOKIES)
    data = login.qrcodeStatus(qr_id, code)['data']
    if not data or data.get('code_status', -1) == 0 or data.get('code_status', -1) == 1:
        return jsonify({
            'success': True,
            'msg': '等待扫码',
            'data': data.get('login_info'),
        })
    elif data.get('code_status', -1) == 2:
        return jsonify({
            'success': True,
            'msg': '登录成功',
            'data': data.get('login_info'),
        })
    elif data.get('code_status', -1) == 3:
        return jsonify({
            'success': True,
            'msg': '二维码已过期',
            'data': {},
        })
    else:
        return jsonify({
            'success': True,
            'msg': '未知错误呀',
            'data': {},
        })


@spider_bp.route('/create', methods=['POST'])
@handle_exceptions
def create():
    data = request.form.to_dict()
    new_spider = Spider(**data)
    mysql.insert('spiders', new_spider.__dict__)
    return jsonify({
        'success': True,
        'msg': '机器爬虫创建成功',
        'data': new_spider.to_dict(),
    })


@spider_bp.route('/load', methods=['GET'])
@handle_exceptions
def load():
    spiders = []
    for db_spider in mysql.select('spiders'):
        spiders.append(dict(zip(Config.SPIDER_FIELDS, db_spider)))
    return jsonify({
        'success': True,
        'msg': '机器爬虫列表获取成功',
        'data': spiders,
    })


@spider_bp.route('/delete', methods=["GET"])
@handle_exceptions
def delete():
    userId = request.args.get('userId')
    mysql.delete('spiders', f'userId={userId!r}')
    return load()


@spider_bp.route('/set_state', methods=['POST'])
@handle_exceptions
def set_state():
    userId = request.form.get('userId')
    run = request.form.get('run')
    data = dict(zip(Config.SPIDER_FIELDS, mysql.select('spiders', condition=f'userId={userId!r}')[0]))
    spider = spiderModels.get(userId) if spiderModels.get(userId) else Spider(**data)
    if run == 'false':
        mysql.update('spiders', {'run': 0}, f'userId={userId!r}')
        run = False
        spider.run = 0
    elif run == 'true':
        mysql.update('spiders', {'run': 1}, f'userId={userId!r}')
        run = True
        spider.run = 1
        if not spiderModels.get(spider.userId):
            spiderModels[spider.userId] = spider
            runTask(spider)
    if run:
        return jsonify({
            'success': True,
            'msg': '已激活',
            'data': {}
        })
    else:
        return jsonify({
            'success': True,
            'msg': '已暂停',
            'data': {}
        })


@spider_bp.route('/sensitive_words', methods=['GET'])
@handle_exceptions
def getSensitiveWords():
    return jsonify({
        'success': True,
        'msg': '获取敏感词成功',
        'data': ['已经被屏蔽', '失败'],
    })


@spider_bp.route('/configure/get', methods=['GET'])
@handle_exceptions
def getConfigure():
    config_record = mysql.select('config', condition='id=1')
    if config_record:
        return jsonify({
            'success': True,
            'msg': '获取配置成功',
            'data': dict(zip(Config.CONFIG_FIELDS, config_record[0])),
        })
    else:
        return jsonify({
            'success': False,
            'msg': '获取配置失败',
            'data': {},
        })


@spider_bp.route('/configure/set', methods=['POST'])
def saveConfigure():
    data = request.form.to_dict()
    for key, value in data.items():
        if region := Config.CONFIG_LIMIT.get(key):
            if float(value) > region[1]:
                data[key] = str(region[1])
            elif float(value) < region[0]:
                data[key] = str(region[0])
    if config_record := mysql.select('config', condition='id=1'):
        mysql.update('config', condition='id=1', data=data)
    else:
        mysql.insert('config', data=data)
    return jsonify({
        'success': True,
        'msg': '保存配置成功',
        'data': config_record,
    })
