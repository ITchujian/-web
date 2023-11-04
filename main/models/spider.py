"""
@File: spider.py
@Author: 秦宇
@Created: 2023/10/25 21:32
@Description: Created in backend.
"""
import time
import uuid

ExcludeKeys = {'qrCodeUrl', 'commentsFile', 'multiKeysFile', 'isPermission', 'generateRobotTitle', 'tokenId'}


class Spider:
    def __init__(self, **kwargs):
        self.tokenId = None
        self.waitTime = 3
        self.isToFollow = 0
        self.isToLike = 0
        self.isToCollect = 0
        self.retryTimes = 0
        self.isRetryAfterFailure = 0
        self.userId = ""
        self.isCheckFailure = 0
        self.rareWordsCount = 0
        self.isRandomRareWords = 0
        self.isComment = 0
        self.comments = ""
        self.commentMode = ""
        self.selectedCategory = "混合采集"
        self.selectedFilter = "综合"
        self.isMultiKey = 0
        self.searchKey = ""
        self.session = ""
        self.taskCount = 0
        self.run = 0
        self.isCyclicMode = True
        self.intervalTime = 3
        self.isRandomIntervalTime = None
        self.state = 0
        self.createTime = int(time.time() * 1000)
        for key, value in kwargs.items():
            if key in ExcludeKeys:
                continue
            setattr(self, key, value)

    def to_dict(self):
        return {
            'userId': self.userId,
            'state': self.state,
            'createTime': self.createTime
        }


if __name__ == '__main__':
    s = Spider()
    print(s.__dict__)
