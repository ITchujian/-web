"""
@File: task.py
@Author: 秦宇
@Created: 2023/10/26 12:28
@Description: Created in backend.
"""
import functools
import random
import time
from threading import Thread, Event
from xhsAPI import Search, User, Note, Comment, Login
from .monitor import fixed_monitors, FixedMonitor, DynamicMonitor
from ..utils.helper import convert_timestamp, check_comment, generate_rare_chars, cal_minute_time
from ..utils.dbtool import mysql
from ..models.spider import Spider
from ..models.cookie import Cookie
from ..config.settings import NoteType, SortType, Config, SpiderState

threads = []
spiderModels = {}


class TimerThread(Thread):
    def __init__(self, event):
        super().__init__()
        self.event = event
        self.spider = None
        self.daemon = True
        self.start_time = None  # 记录开始时间
        self.paused_time = None  # 记录暂停时间

    def setSpider(self, spider):
        self.spider = spider

    def run(self):
        self.start_time = time.time()  # 记录开始时间
        while not self.event.is_set():
            if self.spider.run:
                current_time = time.time()
                if self.paused_time:
                    duration = self.paused_time - self.start_time
                    self.paused_time = None
                    self.start_time = time.time() - duration
                else:
                    duration = current_time - self.start_time
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                fixed_monitors[self.spider.userId].work_time = f"{int(hours)}时{int(minutes)}分{int(seconds)}秒"
            else:
                if not self.paused_time:
                    self.paused_time = time.time()
            time.sleep(1)


class Handler:
    def __init__(self):
        self.stop_event = Event()
        self.timer_thread = TimerThread(self.stop_event)  # 创建一个定时线程

    @staticmethod
    def trace(func):
        @functools.wraps(func)
        def inner(self, spider, tasks: dict, *args, **kwargs):
            try:
                # 执行函数
                result = func(self, spider, tasks, *args, **kwargs)
                return result
            except Exception as e:
                # 打印异常信息
                print(f'{func.__name__}: {e}')
                spider.state = -1
                fixed_monitors[spider.userId].state = SpiderState(spider.state).name
                DynamicMonitor().message = [Handler.now(), '责任链状态', '责任链发生异常']
            finally:
                if not mysql.select('spiders', ['userId'], condition=f'userId={spider.userId!r}'):
                    self.next = None
                    user = Login(fixed_monitors[spider.userId].cookies)
                    user.logout()
                    del spiderModels[spider.userId]
                if self.next:  # 如果存在下一个处理器，则执行下一个处理器
                    self.timer(spider)
                    self.next.handle(spider, tasks)
                else:  # 否则，停止定时线程，并设置停止事件
                    del spiderModels[spider.userId]
                    del fixed_monitors[spider.userId]
                    self.stop_event.set()
                    self.timer_thread.join()

        return inner

    def setNext(self, next_):
        self.next: Handler = next_

    @trace
    def handle(self, spider: Spider):
        pass

    @staticmethod
    def timer(spider: Spider):
        # 如果采用随机间隔时间，则暂停随机秒数
        if spider.isRandomIntervalTime:
            time.sleep(random.uniform(1, spider.intervalTime))
        # 否则，暂停固定秒数
        else:
            time.sleep(spider.intervalTime)

    @staticmethod
    def pause(spider: Spider):
        i = 0
        while not spider.run:
            if i == 0:
                fixed_monitors[spider.userId].pause_time = Handler.now()
                spider.state = -2
                fixed_monitors[spider.userId].state = SpiderState(spider.state).name
            time.sleep(1)
            i += 1

    @staticmethod
    def now():
        return convert_timestamp(time.time() * 1000)


class SearchHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks: dict):
        if not self.timer_thread.spider:
            self.timer_thread.setSpider(spider)
            self.timer_thread.start()
        spider.state = 0
        fixed_monitors[spider.userId].state = SpiderState(spider.state).name
        self.pause(spider)

        if len(tasks) == 0 or (spider.isCyclicMode and all(tasks.values())):
            self.search = Search(fixed_monitors[spider.userId].cookies)
            time.sleep(1)
            spider.state = 1
            fixed_monitors[spider.userId].state = SpiderState(spider.state).name
            self.pause(spider)
            task_count = spider.taskCount
            search_count = task_count // 20 + (1 if task_count % 20 else 0)
            search_keys = spider.searchKey.split("|")
            sort_type = SortType[spider.selectedFilter].value
            fixed_monitors[spider.userId].task_count = len(search_keys) * task_count
            fixed_monitors[spider.userId].fetch_progress = 0
            fixed_monitors[spider.userId].task_progress = 0
            for search_key in search_keys:
                DynamicMonitor().message = [Handler.now(), '搜索状态', f'正在搜索关键字 {search_key}']
                i = 0
                half_upper_limit = search_count // 2 + search_count % 2
                self.pause(spider)
                while i < search_count:
                    # 判断是 先图文后视频
                    if spider.selectedCategory == '先图文后视频':
                        note_type = NoteType.采集图文.value if i < half_upper_limit else NoteType.采集视频.value
                        page = i % half_upper_limit + 1
                    else:
                        note_type = NoteType[spider.selectedCategory]
                        page = i + 1
                    result = self.search.notes(search_key, page, 20, sort_type, note_type)
                    if result['code'] == 0:
                        if not result['data']:  # 高频搜索导致验证码情况处理
                            DynamicMonitor().message = [Handler.now(), '搜索状态', '搜索为空，疑似验证码出现']
                            DynamicMonitor().message = [Handler.now(), '登录状态',
                                                        '请启动补登工具，输入用户ID并登录，然后重新激活本爬虫']
                            spider.state = -3
                            fixed_monitors[spider.userId].state = SpiderState(spider.state).name
                            mysql.update('spiders', {'run': 0}, f'userId={spider.userId!r}')
                            spider.run = 0
                            self.pause(spider)  # 恢复工作后从数据库获取新的 session 值
                            session = mysql.select('spiders', 'session', f'userId={spider.userId!r}')[0][0]
                            spider.session = session
                            user_cookie = Cookie(Config.DEFAULT_COOKIES)
                            user_cookie.set_cookie("web_session", spider.session)
                            fixed_monitors[spider.userId].cookies = user_cookie.get_cookie_string()
                            self.search = Search(fixed_monitors[spider.userId].cookies)
                            continue
                        if spider.selectedCategory == '先图文后视频':
                            if not result['data'].get('has_more', False):
                                i += 1
                                continue
                            items = result['data']['items']
                            if i + 1 == half_upper_limit:
                                items = items[:task_count // 2 % 20]
                            elif i + 1 == search_count:
                                items = items[:(task_count - task_count // 2) % 20]
                            for item in items:
                                tasks.setdefault(item['id'], False)
                            # 如果数量在20范围内，也就是只有一轮循环，需要处理好相应的一半图文与后另一半视频
                            if 0 < task_count <= 20:
                                result = self.search.notes(search_key, page, 20, sort_type, NoteType.采集视频.value)
                                items = result['data']['items'][:(task_count - task_count // 2) % 20]
                                for item in items:
                                    tasks.setdefault(item['id'], False)
                        else:  # 单选状态，仅图文 或者 仅视频
                            if not result['data'].get('has_more', False):
                                break
                            items = result['data']['items'][:(task_count % 20 or 20) if i + 1 == search_count else 20]
                            for item in items:
                                tasks.setdefault(item['id'], False)
                        fixed_monitors[spider.userId].fetch_progress = len(tasks)
                    else:  # 异常状态
                        spider.state = -1
                        fixed_monitors[spider.userId].state = SpiderState(spider.state).name
                        DynamicMonitor().message = [Handler.now(), '登录状态', '未登录，请重新登录']
                        self.next = None
                        break
                    i += 1
                    time.sleep(0.314)

        if spider.isCyclicMode:
            fixed_monitors[spider.userId].task_count = len(tasks)


class UncollectHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 2
        fixed_monitors[spider.userId].state = SpiderState(spider.state).name
        self.pause(spider)
        if spider.isComment:
            self.note = Note(fixed_monitors[spider.userId].cookies)
            if spider.commentMode == '再评论再收藏':
                note_id = next((note_id for note_id, state in tasks.items() if not state), None)
                if note_id:
                    self.note.uncollect(note_id)


class SkipCollectHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 3
        fixed_monitors[spider.userId].state = SpiderState(spider.state).name
        self.pause(spider)
        if spider.isComment:
            self.note = Note(fixed_monitors[spider.userId].cookies)
            comment_mode = spider.commentMode
            if comment_mode == '跳过已收藏':
                note_id = next((note_id for note_id, state in tasks.items() if not state), None)
                if note_id:
                    interact_info = self.note.feed(note_id)['data']['items'][0]['note_card']['interact_info']
                    if interact_info['collected']:
                        self.next = self.next.next


class CommentHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 4
        fixed_monitors[spider.userId].state = SpiderState(spider.state).name
        self.pause(spider)
        if spider.isComment:
            self.comment = Comment(fixed_monitors[spider.userId].cookies)
            item = next(((i + 1, note_id) for i, (note_id, state) in enumerate(tasks.items()) if not state), None)
            if item:
                serial_num, note_id = item
                DynamicMonitor().message = [Handler.now(), '评论状态', f'正在评论第{serial_num}条']
                comment = random.choice(spider.comments.split('|'))  # 随机出评
                comment = check_comment(comment)  # 检测敏感
                if spider.isRandomRareWords:  # 生僻字追加
                    comment = f"{comment}{generate_rare_chars(spider.rareWordsCount)}"
                fixed_monitors[spider.userId].task_url = f"{Config.NOTE_BASE_URL}{note_id}"
                fixed_monitors[spider.userId].task_comment = comment
                response = self.comment.post(note_id, comment)
                if response['code'] == -10000:
                    self.next = None
                    fixed_monitors[spider.userId].failure_comment += 1
                    DynamicMonitor().message = [Handler.now(), '评论状态', Config.COMMENT_FAILURE_REASON_BANNED]
                elif response['code'] != 0:
                    fixed_monitors[spider.userId].failure_comment += 1
                    DynamicMonitor().message = [Handler.now(), '评论状态', Config.COMMENT_FAILURE_REASON_UNKNOWN]
                elif response['code'] == 0:
                    fixed_monitors[spider.userId].success_comment += 1
                    DynamicMonitor().message = [Handler.now(), '评论状态', f'第{serial_num}条评论完成']


class RetryHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 5
        fixed_monitors[spider.userId].state = SpiderState(spider.state).name
        self.pause(spider)
        if spider.isComment:
            self.comment = Comment(fixed_monitors[spider.userId].cookies)
            if spider.isCheckFailure:
                note_id = next((note_id for note_id, state in tasks.items() if not state), None)
                if note_id:
                    comments = self.comment.showAll(note_id)['data']['comments']
                    for comment in comments:
                        if comment['content'] == fixed_monitors[spider.userId].task_comment and \
                                comment['user_info']['user_id'] == spider.userId:
                            if comment['status'] != 0:
                                self.retry_comment(note_id, spider)
                                break
                    else:
                        self.retry_comment(note_id, spider)

    def retry_comment(self, note_id, spider):
        fixed_monitors[spider.userId].failure_comment += 1
        fixed_monitors[spider.userId].success_comment -= 1
        DynamicMonitor().message = [Handler.now(), '评论状态',
                                    f'该评论已经被屏蔽，地址是 {Config.NOTE_BASE_URL}{note_id}']
        if spider.isRetryAfterFailure:
            time.sleep(0.314)
            spider.state = 6
            fixed_monitors[spider.userId].state = SpiderState(spider.state).name
            for i in range(spider.retryTimes):
                self.timer(spider)
                self.pause(spider)
                response = self.comment.post(note_id, fixed_monitors[spider.userId].task_comment)
                if response['code'] == 0:
                    comments = self.comment.showAll(note_id)['data']['comments']
                    for comment in comments:
                        if comment['content'] == fixed_monitors[spider.userId].task_comment and \
                                comment['user_info']['user_id'] == spider.userId:
                            if comment['status'] != 0:
                                DynamicMonitor().message = [Handler.now(), '重评状态', f'第 {i + 1} 次评论失败']
                            else:
                                DynamicMonitor().message = [Handler.now(), '重评状态', f'第 {i + 1} 次评论成功']
                                fixed_monitors[spider.userId].failure_comment -= 1
                                fixed_monitors[spider.userId].success_comment += 1
                                break
                else:
                    DynamicMonitor().message = [Handler.now(), '重评状态', f'第 {i + 1} 次评论失败']


class CollectHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 7
        fixed_monitors[spider.userId].state = SpiderState(spider.state).name
        self.pause(spider)
        if spider.isToCollect or (spider.isComment and spider.commentMode == '再评论再收藏'):
            self.note = Note(fixed_monitors[spider.userId].cookies)
            note_id = next((note_id for note_id, state in tasks.items() if not state), None)
            if note_id:
                response = self.note.collect(note_id)
                if response['code'] != 0:
                    DynamicMonitor().message = [Handler.now(), '收藏状态', '收藏失败']


class LikeHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 8
        fixed_monitors[spider.userId].state = SpiderState(spider.state).name
        self.pause(spider)
        if spider.isToLike:
            self.note = Note(fixed_monitors[spider.userId].cookies)
            note_id = next((note_id for note_id, state in tasks.items() if not state), None)
            if note_id:
                response = self.note.like(note_id)
                if response['code'] != 0:
                    DynamicMonitor().message = [Handler.now(), '点赞状态', '点赞失败']


class FollowHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks: dict):
        spider.state = 9
        fixed_monitors[spider.userId].state = SpiderState(spider.state).name
        self.pause(spider)
        if spider.isToFollow:
            self.note = Note(fixed_monitors[spider.userId].cookies)
            self.user = User(fixed_monitors[spider.userId].cookies)
            note_id = next((note_id for note_id, state in tasks.items() if not state), None)
            if note_id:
                user_id = self.note.feed(note_id)['data']['items'][0]['note_card']['user']['user_id']
                response = self.user.follow(user_id)
                if response['code'] != 0:
                    DynamicMonitor().message = [Handler.now(), '关注状态', '关注失败']
        # 当前任务标记完成
        item = next(((i + 1, note_id) for i, (note_id, state) in enumerate(tasks.items()) if not state), None)
        if item:
            serial_num, note_id = item
            tasks[note_id] = True
            fixed_monitors[spider.userId].task_progress += 1
            DynamicMonitor().message = [Handler.now(), '任务状态',
                                        f'第{serial_num}个任务 {Config.NOTE_BASE_URL}{note_id} 完成']
        else:
            self.next = None
            DynamicMonitor().message = [Handler.now(), '任务状态', f'该任务异常，请检查后台日志']
        # 非循环模式下 检测总任务是否完成
        if not spider.isCyclicMode and all(tasks.values()):
            self.next = None
            DynamicMonitor().message = [Handler.now(), '任务状态', f'总任务已完成']
        # 循环模式下 并且总任务完成
        if spider.isCyclicMode and all(tasks.values()):
            DynamicMonitor().message = [Handler.now(), '任务状态', f'循环直到{cal_minute_time(spider.waitTime)}后执行']
            spider.state = 10
            fixed_monitors[spider.userId].state = SpiderState(spider.state).name
            time.sleep(60 * spider.waitTime)


def runTask(spider: Spider):
    if fixed_monitors.get(spider.userId):
        return
    # 构建责任链
    DynamicMonitor().message = [Handler.now(), '构建责任链', f'配置责任链中，请等待']
    search_handler = SearchHandler()
    uncollect_handler = UncollectHandler()
    skip_collect_handler = SkipCollectHandler()
    comment_handler = CommentHandler()
    retry_handler = RetryHandler()
    collect_handler = CollectHandler()
    like_handler = LikeHandler()
    follow_handler = FollowHandler()
    # 设置责任链关系
    search_handler.setNext(uncollect_handler)
    uncollect_handler.setNext(skip_collect_handler)
    skip_collect_handler.setNext(comment_handler)
    comment_handler.setNext(retry_handler)
    retry_handler.setNext(collect_handler)
    collect_handler.setNext(like_handler)
    like_handler.setNext(follow_handler)
    follow_handler.setNext(search_handler)
    DynamicMonitor().message = [Handler.now(), '构建责任链', f'配置责任链关系已完成']
    # Cookies更换
    user_cookie = Cookie(Config.DEFAULT_COOKIES)
    user_cookie.set_cookie("web_session", spider.session)
    # 固定监控屏启动!!原神启动！！摸下鱼
    fixed_monitor = FixedMonitor()
    fixed_monitor.userId = spider.userId
    fixed_monitor.create_time = convert_timestamp(int(spider.createTime))
    fixed_monitor.task_count = spider.taskCount
    fixed_monitor.cookies = user_cookie.get_cookie_string()
    fixed_monitors[spider.userId] = fixed_monitor
    DynamicMonitor().message = [Handler.now(), '监控启动', f'{spider.userId[:6]}...已载入监控屏模型']
    tasks = {}
    # 线程启动，开始执行任务
    thread = Thread(target=search_handler.handle, kwargs={'spider': spider, 'tasks': tasks}, daemon=True)
    threads.append(thread)
    thread.start()
    DynamicMonitor().message = [Handler.now(), '线程启动', f'{spider.userId[:6]}...已附加线程并且已经启动']
