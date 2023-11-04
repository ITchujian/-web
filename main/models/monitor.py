"""
@File: monitor.py
@Author: 秦宇
@Created: 2023/10/26 12:09
@Description: Created in backend.
"""

fixed_monitors = {}

dynamic_monitors = {}


class FixedMonitor:
    def __init__(self):
        self.userId = ""
        self.state = ""
        self.create_time = ""
        self.pause_time = ""
        self.work_time = ""
        self.fetch_progress = 0
        self.task_progress = 0
        self.success_comment = 0
        self.failure_comment = 0
        self.task_url = ""
        self.task_comment = ""
        self.task_count = 0
        self.cookies = ''


class Log:
    """
    日志：时间 事件类型 详细描述
    """

    def __get__(self, instance, owner):
        temp = instance.__dict__.get('msg', '')
        instance.__dict__['msg'] = ""
        return temp

    def __set__(self, instance, value):
        if not (isinstance(value, list) or isinstance(value, tuple)):
            raise ValueError("Message must be a list or tuple")
        if len(value) != 3:
            raise ValueError("Detail: [timeType, class, describe]")
        instance.__dict__['msg'] = " | ".join(value)

    def __delete__(self, instance):
        del instance.__dict__['msg']


class DynamicMonitor:
    message = Log()


if __name__ == '__main__':
    monitor = DynamicMonitor()
    print('设置值前', monitor.message)
    monitor.message = ['2021-10-15 23:00:11', '吃饭', '吃出了黄金三千两']
    monitor2 = DynamicMonitor()
    print(monitor2.message)
    print('设置值后', monitor.message)
    print('访问值后', monitor.message)

