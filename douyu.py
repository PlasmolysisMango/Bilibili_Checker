from spider_base import *
import datetime
import time
import re
import json

DEBUG = False

# 此处配置需要抢的页面id和对应时间
taskId_config = [
    # {
    #     "taskId": 217732,
    #     "name": "萌新-累播14天"
    # },
    # {
    #     "taskId": 217723,
    #     "name": "里程碑-累计开播18天"
    # },
    # {
    #     "taskId": 217724,
    #     "name": "里程碑-累计开播26天"
    # },
    # {
    #     "taskId": 217710,
    #     "name": "每日-被观看10min"
    # },
    # {
    #     "taskId": 217711,
    #     "name": "每日-收到6条弹幕"
    # },
    # {
    #     "taskId": 217724,
    #     "name": "里程碑-累计开播26天"
    # },
    # {
    #     "taskId": 230914,
    #     "name": "【萌新】180星琼"
    # },
    {
        "taskId": 230805,
        "name": "320星琼w1"
    },
]


def tick(period=0.5):
    time.sleep(period)


def getTaskIdList() -> list:
    res = []
    for eachTask in taskId_config:
        res.append(eachTask['taskId'])
    return res


class DouyuRequest:
    def getHeaders(self, path: str, cookies_path="douyu/cookies.txt") -> dict:
        with open(path, "r+", encoding="utf-8") as f:
            h = f.read()
        headers = get_headersDict(h)
        # 使用cookies文件
        with open(cookies_path, "r+", encoding="utf-8") as f:
            c = f.read()
        if 'Cookie' in headers.keys():
            headers['Cookie'] = c

        return headers


class GetStatus(DouyuRequest):
    def __init__(self, taskIdList: list[int]) -> None:
        super().__init__()
        self.url = "https://www.douyu.com/japi/carnival/nc/roomTask/getStatus"
        self.headers = self.getHeaders(r"douyu/get_price.txt")
        self.taskIdList = taskIdList

    def request(self) -> str:
        params = {
            "taskIds": self.taskIdList
        }
        r = requests.get(url=self.url, headers=self.headers,
                         params=params)
        r.encoding = r.apparent_encoding
        return r.text

    def update(self):
        while True:
            text = self.request()
            if not "频繁" in text and not "过快" in text:
                break
            else:
                tick()
        resJson = json.loads(text)['data']
        if DEBUG:
            print(resJson)
            with open("./douyu/debug.json", "w+", encoding="utf-8") as f:
                f.write(text)
        for eachBonus in resJson:
            print(eachBonus['condCompleteList'][0]['name'],
                  eachBonus['status'] == 4 and "已抢完" or (
                      eachBonus['status'] == 1 and "未完成" or (
                          eachBonus['status'] == 2 and "已完成"
                      )), end=' ')
            print(eachBonus['prizeInfo'][0]['remain']['remainDesc'], end=" ")
            print(f"共{eachBonus['prizeInfo'][0]['remain']['maxNumDesc']}")
    
    def buildConf(self):
        text = self.request()
        resJson = json.loads(text)['data']
        taskInfoList=[]
        for eachTask in resJson:
            taskInfoList.append(
                {
                    "taskId": eachTask['taskId'], 
                    "name": eachTask["prizeInfo"][0]['name']
                }
            )
        with open("douyu/res.json", "w+", encoding="utf-8") as f:
            f.write(json.dumps(taskInfoList, ensure_ascii=False))


class ReceiveBonus(DouyuRequest):
    def __init__(self, taskId: int) -> None:
        super().__init__()
        self.url = "https://www.douyu.com/japi/carnival/nc/roomTask/getPrize"
        self.headers = self.getHeaders(r"douyu/receive.txt")
        self.taskId = taskId

    def request(self) -> str:
        data = {
            "taskId": self.taskId
        }
        r = requests.post(url=self.url, headers=self.headers,
                          data=data)
        return r.text


class BonusRecord(DouyuRequest):
    def __init__(self) -> None:
        super().__init__()
        self.headers = self.getHeaders(r"douyu/myrecord.txt")
        self.url = "https://www.douyu.com/japi/carnival/nc/giftbag/myrecord"

    def request(self) -> str:
        params = {
            "pageSize":	10,
            "currentPage": 1,
            "actAlias": "20230807XFCUE",
        }
        r = requests.get(url=self.url, params=params, headers=self.headers)
        return r.text
    
    def update(self) -> None:
        text = self.request() 
        resJson = json.loads(text)['data']
        if DEBUG:
            print(resJson)
            with open("./douyu/debug.json", "w+", encoding="utf-8") as f:
                f.write(text)
        rawPriceList = resJson['bags']
        todayList = []
        for eachRawPrice in rawPriceList:
            dic = eachRawPrice['prizes'][0]
            t = datetime.datetime.fromtimestamp(float(dic['obtTime']))
            if (t.day == datetime.datetime.now().day):
                todayList.append(dic['ext'])
        for e in todayList:
            print(e)


def check_time(target_time):
    now = datetime.datetime.now()
    return now >= target_time


def just_receive_mode():
    # 目标时间
    target_time = datetime.datetime.strptime(
        "2023-09-04 18:00:00", r"%Y-%m-%d %H:%M:%S")
    target_time = target_time - datetime.timedelta(seconds=3)
    print(f"实际预定时间：{target_time}")
    # 检查cookies
    status = GetStatus(getTaskIdList())
    status.update()

    readyList = []

    for taskId in getTaskIdList():
        readyList.append(ReceiveBonus(taskId))

    while (True):
        if check_time(target_time):
            while (True):
                for receiveBonus in readyList:
                    r = receiveBonus.request()
                    print(r)
                tick(0.5)
                if ("频繁" in r or "过快" or "繁忙" in r):
                    tick(0.5)
        else:
            print("Waiting...", target_time - datetime.datetime.now())
            if (target_time - datetime.datetime.now() > datetime.timedelta(minutes=5)):
                time.sleep(60)
            elif (target_time - datetime.datetime.now() > datetime.timedelta(seconds=60)):
                time.sleep(10)
            elif (target_time - datetime.datetime.now() > datetime.timedelta(seconds=10)):
                time.sleep(1)

def bonus_record_mode():
    br = BonusRecord()
    br.update()

def build_res_mode():
    taskIds = [
        230911,230912,230913,230914,230915,
        230900,230901,230902,
        230797,230803,230804,230805,
        230906,230907,230908,230909,
        230810,230811,230812,230813,
        230814,230815,230816,230817,
        230818,230819,230820,230821,
        230822,230823,230824,230825,
    ]
    gs = GetStatus(taskIdList=taskIds)
    gs.buildConf()

def main_loop():
    # bonus_record_mode()
    just_receive_mode()
    # update_status()
    # build_res_mode()


if __name__ == "__main__":
    main_loop()
