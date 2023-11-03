"""
@File: config.py
@Author: 秦宇
@Created: 2023/10/25 13:55
@Description: Created in backend.
"""
import pymysql
from enum import Enum

SECRET_KEY = 'd0fb963ff976f9c37fc81fe03c21ea7b'


class SpiderState(Enum):
    生成中 = 0
    搜索中 = 1
    取消收藏中 = 2
    跳过收藏中 = 3
    评论中 = 4
    检查评论中 = 5
    重试中 = 6
    收藏 = 7
    点赞 = 8
    关注 = 9
    循环等待 = 10

    异常 = -1
    暂停 = -2
    待补登 = -3


class NoteType(Enum):
    混合采集 = 0
    采集视频 = 1
    采集图文 = 2
    先图文后视频 = 3


class SortType(Enum):
    综合 = "general"
    最热 = "popularity_descending"
    最新 = "time_descending"


class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_HOST = 'localhost'
    DATABASE_USER = 'normal'
    DATABASE_PASSWORD = '20010908xygGYX'
    DATABASE_NAME = 'redbook'
    DATABASE_CHARSET = 'utf8'
    DATABASE_POOL_MINCACHED = 2
    DATABASE_POOL_MAXCONNECTIONS = 8
    DATABASE_POOL_BLOCKING = True
    DATABASE_POOL_PING = 0

    NOTE_BASE_URL = "https://www.xiaohongshu.com/explore/"
    COMMENT_FAILURE_REASON_BANNED = '该账户违反小红书社区规范已经被封号'
    COMMENT_FAILURE_REASON_UNKNOWN = '未知原因导致评论失败'
    DEFAULT_COOKIES = ("abRequestId=b3a24d97-e349-553f-866c-7fba9239ccaa; "
                       "a1=18b287fe0af9atg98uvl7aoprycn0jsa7sc9ov2z750000374905; "
                       "webId=037a83ee1baebf147894c93a32bf9802; "
                       "gid=yYDJYWifdKWdyYDJYWid8MhJ0ij09kjY7h1WSuW0lUFvSj28I8VM0l888qW4j8280q00WSKf; "
                       "webBuild=3.13.6; "
                       "acw_tc=3c07e4257dfae1f514f0a9f187905bff9ad44213b56f4642a68b85b2fefb1259; "
                       "xsecappid=xhs-pc-web; "
                       "websectiga=10f9a40ba454a07755a08f27ef8194c53637eba4551cf9751c009d9afb564467; "
                       "sec_poison_id=35ae2fea-e006-494c-b7cd-fc479d1a16f6; "
                       "web_session=040069b4589c75f8cc96b64d77374bf590e845; "
                       "unread={%22ub%22:%22651be29b000000001d038221%22%2C%22ue%22:%22653a31b7000000001e02ed04%22%2C"
                       "%22uc%22:15}")

    SPIDER_FIELDS = ('state', 'createTime', 'isMultiKey', 'searchKey', 'selectedFilter',
                     'selectedCategory', 'taskCount', 'isCyclicMode', 'waitTime', 'isToLike',
                     'isToCollect', 'isToFollow', 'isComment', 'commentMode', 'isRandomRareWords',
                     'rareWordsCount', 'isCheckFailure', 'isRetryAfterFailure', 'retryTimes', 'isRandomIntervalTime',
                     'intervalTime', 'run', 'showQrCode', 'showQrCodeState', 'qrCodeState', 'secureSession', 'session',
                     'userId', 'comments')
    CONFIG_FIELDS = ('id', 'isMultiKey', 'searchKey', 'selectedFilter',
                     'selectedCategory', 'taskCount', 'isCyclicMode', 'waitTime', 'isToLike',
                     'isToCollect', 'isToFollow', 'isComment', 'commentMode', 'isRandomRareWords',
                     'rareWordsCount', 'isCheckFailure', 'isRetryAfterFailure', 'retryTimes', 'isRandomIntervalTime',
                     'intervalTime', 'comments')
    CONFIG_LIMIT = {
        'taskCount': (1, 1000),
        'waitTime': (1, 10080),
        'rareWordsCount': (0, 50),
        'retryTimes': (0, 5),
        'intervalTime': (1, 300),
    }

    USER_FIELDS = ('uid', 'uname', 'max_limit')
    LOGIN_FAILURE_LIMIT = 3
    LOCK_TIME = 5

    @classmethod
    def DBPOOL_PARAMS(cls):
        return dict(
            creator=pymysql,
            mincached=cls.DATABASE_POOL_MINCACHED,
            maxconnections=cls.DATABASE_POOL_MAXCONNECTIONS,
            blocking=cls.DATABASE_POOL_BLOCKING,
            ping=cls.DATABASE_POOL_PING,
            host=cls.DATABASE_HOST,
            user=cls.DATABASE_USER,
            password=cls.DATABASE_PASSWORD,
            database=cls.DATABASE_NAME,
            charset=cls.DATABASE_CHARSET,
        )


try:
    from .localsettings import Config
except ImportError:
    pass
