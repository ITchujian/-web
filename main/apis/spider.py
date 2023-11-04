"""
@File: spider.py
@Author: 秦宇
@Created: 2023/10/25 20:41
@Description: Created in backend.
"""
from .base import *
from ..models.task import runTask, spiderModels
from ..models.spider import Spider
from xhsAPI import Login

spider_bp = Blueprint('spider', __name__)


@spider_bp.route('/qrcode', methods=['GET'])
@handle_exceptions
@auth
def qrcode(user):
    login = Login(Config.DEFAULT_COOKIES)
    qrcode_data = login.createQrcode()['data']

    return jsonify({
        'success': True,
        'msg': '获取成功',
        'data': qrcode_data,
    })


@spider_bp.route('/qrcode/state', methods=['GET'])
@handle_exceptions
@auth
def qrcodeState(user):
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
            'success': False,
            'msg': '二维码已过期',
            'data': {},
        })
    else:
        return jsonify({
            'success': False,
            'msg': '未知错误',
            'data': data.get('code_status', -1),
        })


@spider_bp.route('/verify', methods=['GET'])
@handle_exceptions
@auth
def verify(user):
    if verify_limit(user):
        return jsonify({
            'success': True,
            'msg': '限制通过',
        }), 201
    return jsonify({
        'success': False,
        'msg': '限制拒绝',
    }), 403


@spider_bp.route('/create', methods=['POST'])
@handle_exceptions
@auth
def create(user):
    if verify_limit(user):
        data = request.form.to_dict()
        new_spider = Spider(**data)
        db_new = new_spider.__dict__
        db_new.pop('tokenId')
        mysql.insert('spiders', new_spider.__dict__)
        relation = {
            "uid": user["uid"],
            "userId": new_spider.__dict__.get('userId')
        }
        mysql.insert('users_spiders', relation)
        return jsonify({
            'success': True,
            'msg': '创建成功',
            'data': new_spider.to_dict(),
        }), 201
    return jsonify({
        'success': False,
        'msg': '创建失败',
    }), 403


@spider_bp.route('/load', methods=['GET'])
@handle_exceptions
@auth
def load(user):
    spiders = []
    userIds = mysql.select('users_spiders', fields=['userId'], condition=f'uid={user["uid"]!r}')
    if userIds:
        userIds = map(lambda x: x[0], userIds)
        for userId in userIds:
            db_spider = mysql.select('spiders', condition=f'userId={userId!r}')
            if db_spider:
                spiders.append(dict(zip(Config.SPIDER_FIELDS, db_spider[0])))
    return jsonify({
        'success': True,
        'msg': '获取成功',
        'data': spiders,
    })


@spider_bp.route('/delete', methods=["GET"])
@handle_exceptions
@auth
def delete(user):
    userId = request.args.get('userId')
    userIds = mysql.select('users_spiders', fields=['userId'], condition=f'uid={user["uid"]!r}')
    if userIds:
        userIds = map(lambda x: x[0], userIds)
    if userId in userIds:
        mysql.delete('spiders', f'userId={userId!r}')
    return load()


@spider_bp.route('/set_state', methods=['POST'])
@handle_exceptions
@auth
def set_state(user):
    userId = request.form.get('userId')
    run = request.form.get('run')
    userIds = mysql.select('users_spiders', fields=['userId'], condition=f'uid={user["uid"]!r}')
    if userIds:
        userIds = map(lambda x: x[0], userIds)
    if userId in userIds:
        data = dict(zip(Config.SPIDER_FIELDS, mysql.select('spiders', condition=f'userId={userId!r}')[0]))
        spider = spiderModels.get(userId) if spiderModels.get(userId) else Spider(**data)
        spider.tokenId = user['tokenId']
        if run == 'false':
            mysql.update('spiders', {'run': 0}, f'userId={userId!r}')
            spider.run = 0
            return jsonify({
                'success': True,
                'msg': '已暂停',
            })
        elif run == 'true':
            mysql.update('spiders', {'run': 1}, f'userId={userId!r}')
            spider.run = 1
            if not spiderModels.get(spider.userId):
                spiderModels[spider.userId] = spider
                runTask(spider)
            return jsonify({
                'success': True,
                'msg': '已激活',
            })
    else:
        return jsonify({
            'success': False,
            'msg': 'No permission'
        })


@spider_bp.route('/sensitive_words', methods=['GET'])
@handle_exceptions
@auth
def getSensitiveWords(user):
    return jsonify({
        'success': True,
        'msg': '获取敏感词成功',
        'data': ['已经被屏蔽', '失败'],
    })


@spider_bp.route('/configure/get', methods=['GET'])
@handle_exceptions
@auth
def getConfigure(user):
    config_id = mysql.select('users_config', fields=['id'], condition=f'uid={user["uid"]!r}')
    if config_id and config_id[0]:
        config_id = config_id[0][0]
    config_record = mysql.select('config', condition=f'id={config_id!r}')
    if config_record:
        return jsonify({
            'success': True,
            'msg': '获取成功',
            'data': dict(zip(Config.CONFIG_FIELDS, config_record[0])),
        })
    else:
        return jsonify({
            'success': False,
            'msg': '获取失败',
            'data': None,
        })


@spider_bp.route('/configure/set', methods=['POST'])
@handle_exceptions
@auth
def saveConfigure(user):
    data = request.form.to_dict()
    for key, value in data.items():
        if region := Config.CONFIG_LIMIT.get(key):
            if float(value) > region[1]:
                data[key] = str(region[1])
            elif float(value) < region[0]:
                data[key] = str(region[0])
    config_id = mysql.select('users_config', fields=['id'], condition=f'uid={user["uid"]!r}')
    if config_id and config_id[0]:
        config_id = config_id[0][0]
        config_record = mysql.select('config', condition=f'id={config_id!r}')
        if config_record:
            mysql.update('config', condition=f'id={config_id!r}', data=data)
            return jsonify({
                'success': True,
                'msg': '保存成功',
            })
        else:
            data['id'] = config_id
            mysql.insert('config', data=data)
    return jsonify({
        'success': False,
        'msg': '保存失败',
    })
