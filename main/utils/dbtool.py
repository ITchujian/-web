"""
@File: dbtool.py
@Author: 秦宇
@Created: 2023/10/25 22:32
@Description: Created in backend.
"""
from dbutils.pooled_db import PooledDB
from ..config.settings import Config


class MySQL:
    def __init__(self):
        self.pool = PooledDB(**Config.DBPOOL_PARAMS())

    @staticmethod
    def dbing(func):
        def inner(self, *args, **kwargs):
            conn = self.pool.connection()
            cursor = conn.cursor()
            result = func(self, *args, **kwargs, conn=conn, cursor=cursor)
            cursor.close()
            conn.close()
            return result

        return inner

    @dbing
    def create(self, table_name: str, columns: list | tuple, conn=None, cursor=None):
        try:
            if table_name.__contains__(' '):
                return []
            sql = f'CREATE TABLE IF NOT EXISTS {table_name} ('
            sql += ', '.join(columns)
            sql += ')'
            cursor.execute(sql)
            conn.commit()
            print(f" * Table {table_name} created successfully")
        except Exception as e:
            conn.rollback()
            print(f" * Failed to create table {table_name}. Error: {e}")

    @dbing
    def show(self, sql: str = None, conn=None, cursor=None):
        try:
            sql = sql or 'SHOW TABLES'
            cursor.execute(sql)
            tables = cursor.fetchall()
            print(" * Tables in the current database:")
            for table in tables:
                print(f"\t{table[0]}")
        except Exception as e:
            print(f" * Failed to fetch tables. Error: {e}")

    @dbing
    def insert(self, table: str, data: dict, conn=None, cursor=None):
        try:
            if table.__contains__(' '):
                return []
            keys = ','.join(data.keys())
            values = ','.join(['%s'] * len(data))
            insert_values = []
            for value in data.values():
                if isinstance(value, str) and value == 'false':
                    value = 0
                elif isinstance(value, str) and value == 'true':
                    value = 1
                insert_values.append(value)
            sql = f'INSERT INTO {table} ({keys}) VALUES ({values})'
            cursor.execute(sql, tuple(insert_values))
            conn.commit()
            print(' * Insert success')
        except Exception as e:
            conn.rollback()
            print(f' * Insert failed. Error: {e}')

    @dbing
    def delete(self, table: str, condition: str, conn=None, cursor=None):
        try:
            if table.__contains__(' '):
                return []
            sql = f'DELETE FROM {table} WHERE {condition}'
            cursor.execute(sql)
            conn.commit()
            print(' * Delete success')
        except Exception as e:
            conn.rollback()
            print(f' * Delete failed. Error: {e}')

    @dbing
    def update(self, table: str, data: dict, condition: str, conn=None, cursor=None):
        try:
            if table.__contains__(' '):
                return []
            update_data = ','.join([f'{key}=%s' for key in data.keys()])
            update_values = []
            for value in data.values():
                if isinstance(value, str) and value == 'false':
                    value = 0
                elif isinstance(value, str) and value == 'true':
                    value = 1
                update_values.append(value)
            sql = f'UPDATE {table} SET {update_data} WHERE {condition}'
            cursor.execute(sql, tuple(update_values))
            conn.commit()
            print(' * Update success')
        except Exception as e:
            conn.rollback()
            print(f' * Update failed. Error: {e}')

    @dbing
    def select(self, table: str, fields: list = None, condition: str = '', conn=None, cursor=None):
        if fields is None:
            fields = []
        try:
            if table.__contains__(' '):
                return []
            if not fields:
                sql = f'SELECT * FROM {table}'
            else:
                select_fields = ','.join(fields)
                sql = f'SELECT {select_fields} FROM {table}'
            if condition:
                sql += f' WHERE {condition}'
            cursor.execute(sql)
            result = cursor.fetchall()
            print(f' * Select success. Result: {result}')
            return result
        except Exception as e:
            print(f' * Select failed. Error: {e}')


mysql = MySQL()

if __name__ == '__main__':
    # mysql.create('spiders', (
    #     'sid VARCHAR(255) PRIMARY KEY',
    #     'state VARCHAR(255)',
    #     'createTime VARCHAR(255)',
    #     'isMultiKey BOOLEAN',
    #     'searchKey VARCHAR(255)',
    #     'selectedFilter VARCHAR(255)',
    #     'selectedCategory VARCHAR(255)',
    #     'taskCount INT',
    #     'isCyclicMode BOOLEAN',
    #     'waitTime INT',
    #     'isToLike BOOLEAN',
    #     'isToCollect BOOLEAN',
    #     'isToFollow BOOLEAN',
    #     'isComment BOOLEAN',
    #     'commentMode VARCHAR(255)',
    #     'isRandomRareWords BOOLEAN',
    #     'rareWordsCount INT',
    #     'isCheckFailure BOOLEAN',
    #     'isRetryAfterFailure BOOLEAN',
    #     'retryTimes INT',
    #     'isRandomIntervalTime BOOLEAN',
    #     'intervalTime INT',
    #     'run BOOLEAN',
    # ))
    # sid,createTime
    mysql.create('config', [
        '`id` int(11) PRIMARY KEY AUTO_INCREMENT',
        '`isMultiKey` tinyint(1) DEFAULT 0 NULL',
        '`searchKey` varchar(255) DEFAULT NULL',
        '`selectedFilter` varchar(255) DEFAULT "最新" NULL',
        '`selectedCategory` varchar(255) DEFAULT "先图文后视频" NULL',
        '`taskCount` int(11) DEFAULT 200 NULL',
        '`isCyclicMode` tinyint(1) DEFAULT 1 NULL',
        '`waitTime` int(11) DEFAULT 5 NULL',
        '`isToLike` tinyint(1) DEFAULT 0 NULL',
        '`isToCollect` tinyint(1) DEFAULT 1 NULL',
        '`isToFollow` tinyint(1) DEFAULT 0 NULL',
        '`isComment` tinyint(1) DEFAULT 1 NULL',
        '`commentMode` varchar(255) DEFAULT "跳过已收藏" NULL',
        '`isRandomRareWords` tinyint(1) DEFAULT 0 NULL',
        '`rareWordsCount` int(11) DEFAULT 3 NULL',
        '`isCheckFailure` tinyint(1) DEFAULT 1 NULL',
        '`isRetryAfterFailure` tinyint(1) DEFAULT 0 NULL',
        '`retryTimes` int(11) DEFAULT 3 NULL',
        '`isRandomIntervalTime` tinyint(1) DEFAULT 1 NULL',
        '`intervalTime` int(11) DEFAULT 5 NULL',
        '`comments` text',
    ])
