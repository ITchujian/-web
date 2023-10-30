"""
@File: config.py
@Author: 秦宇
@Created: 2023/10/25 13:55
@Description: Created in backend.
"""
import pymysql


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
