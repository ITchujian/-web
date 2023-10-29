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
from xhsAPI import Login
from flask import Blueprint, request, jsonify

spider_bp = Blueprint('spider', __name__)
cookies = "abRequestId=b3a24d97-e349-553f-866c-7fba9239ccaa; a1=18b287fe0af9atg98uvl7aoprycn0jsa7sc9ov2z750000374905; webId=037a83ee1baebf147894c93a32bf9802; gid=yYDJYWifdKWdyYDJYWid8MhJ0ij09kjY7h1WSuW0lUFvSj28I8VM0l888qW4j8280q00WSKf; webBuild=3.12.0; xsecappid=xhs-pc-web; websectiga=9730ffafd96f2d09dc024760e253af6ab1feb0002827740b95a255ddf6847fc8; sec_poison_id=517a5527-5edc-45f1-bb2d-69585c4a63a4; web_session=040069b4593d2bf8c047e6fa06374b761c5547; unread={%22ub%22:%22650a6a2f000000001f03a3d4%22%2C%22ue%22:%2265325bae00000000200032e2%22%2C%22uc%22:28}"

spiders_fields = ['sid', 'state', 'createTime', 'isMultiKey', 'searchKey', 'selectedFilter',
                  'selectedCategory', 'taskCount', 'isCyclicMode', 'waitTime', 'isToLike',
                  'isToCollect', 'isToFollow', 'isComment', 'commentMode', 'isRandomRareWords',
                  'rareWordsCount', 'isCheckFailure', 'isRetryAfterFailure', 'retryTimes', 'isRandomIntervalTime',
                  'intervalTime', 'run', 'showQrCode', 'showQrCodeState', 'qrCodeState', 'secureSession', 'session',
                  'userId',
                  'comments']

config_fields = ('id', 'isMultiKey', 'searchKey', 'selectedFilter',
                 'selectedCategory', 'taskCount', 'isCyclicMode', 'waitTime', 'isToLike',
                 'isToCollect', 'isToFollow', 'isComment', 'commentMode', 'isRandomRareWords',
                 'rareWordsCount', 'isCheckFailure', 'isRetryAfterFailure', 'retryTimes', 'isRandomIntervalTime',
                 'intervalTime', 'comments')

config_limit = {
    'taskCount': (1, 1000),
    'waitTime': (1, 10080),
    'rareWordsCount': (0, 50),
    'retryTimes': (0, 5),
    'intervalTime': (1, 300),
}


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
    login = Login(cookies)
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
    login = Login(cookies)
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
    new_s = Spider(**data)
    mysql.insert('spiders', new_s.__dict__)
    return jsonify({
        'success': True,
        'msg': '机器爬虫创建成功',
        'data': new_s.to_dict(),
    })


@spider_bp.route('/load', methods=['GET'])
@handle_exceptions
def load():
    spiders = []
    for db_spider in mysql.select('spiders'):
        spiders.append(dict(zip(spiders_fields, db_spider)))
    return jsonify({
        'success': True,
        'msg': '机器爬虫列表获取成功',
        'data': spiders,
    })


@spider_bp.route('/delete', methods=["GET"])
@handle_exceptions
def delete():
    sid = request.args.get('sid')
    mysql.delete('spiders', f'sid={sid!r}')
    return load()


@spider_bp.route('/set_state', methods=['POST'])
@handle_exceptions
def set_state():
    sid = request.form.get('sid')
    run = request.form.get('run')
    data = dict(zip(spiders_fields, mysql.select('spiders', condition=f'sid={sid!r}')[0]))
    spider = spiderModels.get(sid) if spiderModels.get(sid) else Spider(**data)
    if run == 'false':
        mysql.update('spiders', {'run': 0}, f'sid={sid!r}')
        run = False
        spider.run = 0
    elif run == 'true':
        mysql.update('spiders', {'run': 1}, f'sid={sid!r}')
        run = True
        spider.run = 1
        if not spiderModels.get(spider.sid):
            spiderModels[spider.sid] = spider
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
            'data': dict(zip(config_fields, config_record[0])),
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
        if region := config_limit.get(key):
            if float(value) > region[1]:
                data[key] = str(region[1])
            elif float(value) < region[0]:
                data[key] = str(region[0])
    mysql.update('config', condition='id=1', data=data)
    config_record = mysql.select('config', condition='id=1')
    return jsonify({
        'success': True,
        'msg': '保存配置成功',
        'data': dict(zip(config_fields, config_record[0])),
    })
