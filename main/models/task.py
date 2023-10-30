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
from ..utils.helper import convert_timestamp, check_comment, generate_rare_chars
from ..utils.dbtool import mysql
from ..models.spider import Spider
from ..models.cookie import Cookie

SpiderStatus = (
    '生成中', '搜索中', '取消收藏中', '跳过收藏中', '评论中', '检查评论中', '重试中', '收藏', '点赞', '关注', '暂停中',
    '异常')

threads = []

spiderModels = {}

cookies = "abRequestId=b3a24d97-e349-553f-866c-7fba9239ccaa; a1=18b287fe0af9atg98uvl7aoprycn0jsa7sc9ov2z750000374905; webId=037a83ee1baebf147894c93a32bf9802; gid=yYDJYWifdKWdyYDJYWid8MhJ0ij09kjY7h1WSuW0lUFvSj28I8VM0l888qW4j8280q00WSKf; xsecappid=xhs-pc-web; webBuild=3.11.3; unread={%22ub%22:%22652a5407000000001f037069%22%2C%22ue%22:%2265097e06000000001e00c840%22%2C%22uc%22:32}; acw_tc=9d80a54070b7c90daedd0f4b70fd95c56e7e134e9fc26bcb71dc90a8707a2b7a; web_session=040069b2f4a6242ffbaf7cfd06374b044e8a7e; websectiga=29098a4cf41f76ee3f8db19051aaa60c0fc7c5e305572fec762da32d457d76ae; sec_poison_id=b48d3561-4e32-47b9-9759-6e6181be3518"

noteType = {
    '混合采集': 0,
    '采集视频': 1,
    '采集图文': 2,
    '先图文后视频': 3,
}

sortType = {
    "综合": "general",
    "最热": "popularity_descending",
    "最新": "time_descending",
}

noteBaseUrl = "https://www.xiaohongshu.com/explore/"


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
                fixed_monitors[self.spider.sid].work_time = f"{int(hours)}时{int(minutes)}分{int(seconds)}秒"
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
                fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
                DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '责任链状态',
                                            '责任链发生异常']
            finally:
                if not mysql.select('spiders', ['sid'], condition=f'sid={spider.sid!r}'):
                    self.next = None
                    user = Login(fixed_monitors[spider.sid].cookies)
                    user.logout()
                    del spiderModels[spider.sid]
                if self.next:  # 如果存在下一个处理器，则执行下一个处理器
                    self.timer(spider)
                    self.next.handle(spider, tasks)
                else:  # 否则，停止定时线程，并设置停止事件
                    del spiderModels[spider.sid]
                    del fixed_monitors[spider.sid]
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
        # 如果 spider 未运行，则暂停
        while not spider.run:
            # 如果是第一次，则记录暂停时间
            if i == 0:
                fixed_monitors[spider.sid].pause_time = convert_timestamp(time.time() * 1000)
                spider.state = -2
                fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
            time.sleep(1)
            i += 1


class SearchHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks: dict):
        if not self.timer_thread.spider:
            self.timer_thread.setSpider(spider)
            self.timer_thread.start()
        spider.state = 0
        fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
        self.pause(spider)

        if len(tasks) == 0 or (spider.isCyclicMode and sum(tasks.values()) >= spider.taskCount):
            self.search = Search(fixed_monitors[spider.sid].cookies)
            time.sleep(1)
            spider.state = 1
            fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
            self.pause(spider)
            # is_multi_key = spider.isMultiKey
            task_count = spider.taskCount
            search_count = task_count // 20 + 1
            search_keys = spider.searchKey.split("|")
            selected_filter = sortType.get(spider.selectedFilter)
            fixed_monitors[spider.sid].task_count = len(search_keys) * task_count
            fixed_monitors[spider.sid].fetch_progress = 0
            fixed_monitors[spider.sid].task_progress = 0
            for search_key in search_keys:
                current_key_list = []
                if spider.selectedCategory == '先图文后视频':
                    is_search1 = True
                    is_search2 = True
                    for i in range(search_count // 2):
                        if is_search1:
                            result1 = self.search.notes(search_key, i + 1, 20, selected_filter,
                                                        noteType.get('采集图文'))
                            if not self.getSearchNotes(result1, current_key_list, spider, limit=10):
                                break
                            if not result1['data'].get('has_more', True):
                                is_search1 = False
                        if not is_search1:
                            if len(current_key_list) >= task_count:
                                break
                    for i in range(int(search_count - search_count // 2)):
                        if is_search2:
                            result2 = self.search.notes(search_key, i + 1, 20, selected_filter,
                                                        noteType.get('采集视频'))
                            if not self.getSearchNotes(result2, current_key_list, spider, limit=10):
                                break
                            if not result2['data'].get('has_more', True):
                                is_search2 = False
                        if not is_search2:
                            if len(current_key_list) >= task_count:
                                break
                        time.sleep(0.1)
                else:
                    selected_category = noteType.get(spider.selectedCategory)
                    for i in range(search_count):
                        result = self.search.notes(search_key, i + 1, 20, selected_filter, selected_category)
                        if not self.getSearchNotes(result, current_key_list, spider):
                            break
                        if not result['data'].get('has_more', True):
                            break
                        time.sleep(0.1)

                for i in range(min(len(current_key_list), task_count)):
                    tasks.setdefault(current_key_list[i]['id'], False)
                    fixed_monitors[spider.sid].fetch_progress += 1

    def getSearchNotes(self, result, temp_list, spider, limit=20):
        if result['code'] == 0:
            temp_list.extend(result['data']['items'][:limit])
            return True
        else:
            DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '登录状态',
                                        '未登录，请重新登录']
            spider.state = -1
            fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
            self.next = None
            return False


class UncollectHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 2
        fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
        self.pause(spider)
        if spider.isComment:
            self.note = Note(fixed_monitors[spider.sid].cookies)
            if spider.commentMode == '再评论再收藏':
                for note_id, state in tasks.items():
                    if not state:
                        self.note.uncollect(note_id)
                        break


class SkipCollectHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 3
        fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
        self.pause(spider)
        if spider.isComment:
            self.note = Note(fixed_monitors[spider.sid].cookies)
            comment_mode = spider.commentMode
            if comment_mode == '跳过已收藏':
                for note_id, state in tasks.items():
                    if not state:
                        interact_info = self.note.feed(note_id)['data']['items'][0]['note_card']['interact_info']
                        if interact_info['collected']:
                            self.next = self.next.next
                        break


class CommentHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 4
        fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
        self.pause(spider)
        if spider.isComment:
            self.comment = Comment(fixed_monitors[spider.sid].cookies)
            comments = spider.comments.split('|')
            for note_id, state in tasks.items():
                comment = random.choice(comments)  # 随机出评
                comment = check_comment(comment)  # 检测敏感
                if spider.isRandomRareWords:  # 生僻字追加
                    comment = f"{comment}{generate_rare_chars(spider.rareWordsCount)}"
                fixed_monitors[spider.sid].task_url = f"{noteBaseUrl}{note_id}"
                fixed_monitors[spider.sid].task_comment = comment
                if not state:
                    response = self.comment.post(note_id, comment)
                    if response['code'] == -10000:
                        DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '评论状态',
                                                    '该账户违反小红书社区规范已经被封号']
                        self.next = None
                        fixed_monitors[spider.sid].failure_comment += 1
                    elif response['code'] != 0:
                        DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '评论状态',
                                                    '未知原因导致评论失败']
                        fixed_monitors[spider.sid].failure_comment += 1
                    elif response['code'] == 0:
                        fixed_monitors[spider.sid].success_comment += 1
                    break


class RetryHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 5
        fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
        self.pause(spider)
        if spider.isComment:
            self.comment = Comment(fixed_monitors[spider.sid].cookies)
            if spider.isCheckFailure:
                for note_id, state in tasks.items():
                    if not state:
                        comments = self.comment.showAll(note_id)['data']['comments']
                        for comment in comments:
                            if comment['content'] == fixed_monitors[spider.sid].task_comment and \
                                    comment['user_info']['user_id'] == spider.userId:
                                if comment['status'] != 0:
                                    self.retry_comment(note_id, spider)
                                    comment['status'] = 0
                                    continue
                                break
                        else:
                            self.retry_comment(note_id, spider)
                    break

    def retry_comment(self, note_id, spider):
        fixed_monitors[spider.sid].failure_comment += 1
        fixed_monitors[spider.sid].success_comment -= 1
        DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '评论状态',
                                    f'该评论已经被屏蔽，地址是 {noteBaseUrl}{note_id}']
        if spider.isRetryAfterFailure:
            time.sleep(1)
            spider.state = 6
            fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
            for i in range(spider.retryTimes):
                self.timer(spider)
                response = self.comment.post(note_id, fixed_monitors[spider.sid].task_comment)
                if response['code'] == 0:
                    DynamicMonitor().message = [convert_timestamp(time.time() * 1000),
                                                '重评状态',
                                                f'第 {i + 1} 次评论成功']
                    fixed_monitors[spider.sid].failure_comment -= 1
                    fixed_monitors[spider.sid].success_comment += 1
                    break
                else:
                    DynamicMonitor().message = [convert_timestamp(time.time() * 1000),
                                                '重评状态',
                                                f'第 {i + 1} 次评论失败']
            self.pause(spider)


class CollectHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 7
        fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
        self.pause(spider)
        if spider.isToCollect or (spider.isComment and spider.commentMode == '再评论再收藏'):
            self.note = Note(fixed_monitors[spider.sid].cookies)
            for note_id, state in tasks.items():
                if not state:
                    response = self.note.collect(note_id)
                    if response['code'] != 0:
                        DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '收藏状态',
                                                    '收藏失败']
                    break


class LikeHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks):
        spider.state = 8
        fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
        self.pause(spider)
        if spider.isToLike:
            self.note = Note(fixed_monitors[spider.sid].cookies)
            for note_id, state in tasks.items():
                if not state:
                    response = self.note.like(note_id)
                    if response['code'] != 0:
                        DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '点赞状态',
                                                    '点赞失败']
                    break


class FollowHandler(Handler):
    @Handler.trace
    def handle(self, spider, tasks: dict):
        spider.state = 9
        fixed_monitors[spider.sid].state = SpiderStatus[spider.state]
        self.pause(spider)
        if spider.isToFollow:
            self.note = Note(fixed_monitors[spider.sid].cookies)
            self.user = User(fixed_monitors[spider.sid].cookies)
            for note_id, state in tasks.items():
                if not state:
                    user_id = self.note.feed(note_id)['data']['items'][0]['note_card']['user']['user_id']
                    response = self.user.follow(user_id)
                    if response['code'] != 0:
                        DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '关注状态',
                                                    '关注失败']
                    break
        # 当前任务标记完成
        for index, (note_id, state) in enumerate(tasks.items()):
            if not state:
                tasks[note_id] = True
                fixed_monitors[spider.sid].task_progress += 1
                DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '任务状态',
                                            f'第{index + 1}任务 {noteBaseUrl}{note_id} 已完成']
                break
        # 非循环模式下 检测总任务是否完成
        if not spider.isCyclicMode and sum(tasks.values()) == spider.taskCount:
            self.next = None
            DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '任务状态', f'总任务已完成']
        # 循环模式下 并且第一次总任务完成了情况 进入大循环前
        if spider.isCyclicMode and sum(tasks.values()) >= spider.taskCount:
            time.sleep(60 * spider.waitTime)


def runTask(spider: Spider):
    if fixed_monitors.get(spider.sid):
        return
    # 构建责任链
    DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '构建责任链', f'配置责任链中，请等待']
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
    DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '构建责任链', f'配置责任链关系已完成']
    # Cookies更换
    user_cookie = Cookie(cookies)
    user_cookie.set_cookie("web_session", spider.session)
    # 固定监控屏启动!!原神启动！！摸下鱼
    fixed_monitor = FixedMonitor()
    fixed_monitor.sid = spider.sid
    fixed_monitor.create_time = convert_timestamp(int(spider.createTime))
    fixed_monitor.task_count = spider.taskCount
    fixed_monitor.cookies = user_cookie.get_cookie_string()
    fixed_monitors[spider.sid] = fixed_monitor
    DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '监控启动', f'{spider.sid}已载入监控屏模型']
    tasks = {}
    # 线程启动，开始执行任务
    thread = Thread(target=search_handler.handle, kwargs={'spider': spider, 'tasks': tasks}, daemon=True)
    threads.append(thread)
    thread.start()
    DynamicMonitor().message = [convert_timestamp(time.time() * 1000), '线程启动',
                                f'{spider.sid}已附加线程并且已经启动']
