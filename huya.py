from spider_base import *
import datetime
import time
import re
import json

DEBUG = False

advancedLevelList = [
    {
        "level": 2,
        "actId": 446,
        "levelName": "开播3天",
        "levelExp": 30,
        "levelDesc": "",
        "prizeList": []
    },
]


class RequestParams:
    def __init__(self, dic: dict = None,level = None, actId = None) -> None:
        if dic:
            self.level = dic['level']
            self.actId = dic['actId']
        else:
            self.level = level
            self.actId = actId

    def getTimeStampStr(self) -> str:
        return str(int(datetime.datetime.now().timestamp()))

    def toGetUserLevelParams(self) -> dict:
        return {
            'callback': 'getUserLevel_matchComponent19',
            'actId': self.actId,
            'platform': '1',
            '_': self.getTimeStampStr()
        }

    def toReceivePrizeParams(self) -> dict:
        return {
            'callback': 'getLevelPrize_matchComponent19',
            'actId': self.actId,
            'level': self.level,
            'type': '0',
            'platform': '1',
            '_': self.getTimeStampStr()
        }

def tick(period = 0.5):
    time.sleep(period)
        
class HuyaRequest:
    def getHeaders(self, path: str, cookies_path = "huya/cookies.txt") -> dict:
        with open(path, "r+", encoding="utf-8") as f:
            h = f.read()
        headers = get_headersDict(h)
        # 使用cookies文件
        with open(cookies_path, "r+", encoding="utf-8") as f:
            c = f.read()
        if 'Cookie' in headers.keys():
            headers['Cookie'] = c
            
        return headers

class UserLevelStatus(HuyaRequest):
    def __init__(self, requestParams: RequestParams) -> None:
        super().__init__()
        self.url = "https://activityapi.huya.com/growthlevel/getUserLevel"
        self.requestParams = requestParams
        self.headers = self.getHeaders(r"huya/status_cookies.txt")
        self.res = None
    
    def request(self) -> str:
        r = requests.get(url = self.url, headers=self.headers, params=self.requestParams.toGetUserLevelParams())
        return r.text
    
    def explainText(self, text: str) -> dict:
        text = re.search("\(.+?\)", text).group(0)
        return json.loads(text[1:-1])
    
    def update(self):
        while True:
            text = self.request()
            if not "频繁" in text and not "过快" in text:
                break
            else:
                tick()
        resJson = self.explainText(text)
        if DEBUG:
            print(resJson)
            with open("./huya/debug.json", "w+", encoding="utf-8") as f:
                f.write(text)
        self.receiveStatus = resJson['data']['levelPrizeStatus']
        self.completeStatus = resJson['data']['advancedPrizeStatus']
        for eachDict in advancedLevelList:
            eachDict['receiveStatus'] = self.receiveStatus[str(eachDict['level'])]

class ReceiveBonus(HuyaRequest):
    def __init__(self, requestParams: RequestParams) -> None:
        super().__init__()
        self.url = "https://activityapi.huya.com/growthlevel/receivePrize"
        self.requestParams = requestParams
        self.headers = self.getHeaders(r"huya/receive_cookies.txt")
        self.res = None
    
    def request(self) -> str:
        r = requests.get(url = self.url, headers=self.headers, params=self.requestParams.toReceivePrizeParams())
        return r.text

# class BonusRecord(HuyaRequest):
#     def __init__(self) -> None:
#         super().__init__()
#         self.headers = self.getHeaders(r"huya/myrecord.txt")
#         self.url = "https://www.douyu.com/japi/carnival/nc/giftbag/myrecord"

#     def request(self) -> str:
#         params = {
#             "pageSize":	10,
#             "currentPage": 1,
#             "actAlias": "20230530TRHPG",
#         }
#         r = requests.get(url=self.url, params=params, headers=self.headers)
#         return r.text
    
#     def update(self) -> None:
#         text = self.request() 
#         resJson = json.loads(text)['data']
#         if DEBUG:
#             print(resJson)
#             with open("./douyu/debug.json", "w+", encoding="utf-8") as f:
#                 f.write(text)
#         rawPriceList = resJson['bags']
#         todayList = []
#         for eachRawPrice in rawPriceList:
#             dic = eachRawPrice['prizes'][0]
#             t = datetime.datetime.fromtimestamp(float(dic['obtTime']))
#             if (t.day == datetime.datetime.now().day):
#                 todayList.append(json.loads(dic['ext'])[0]['code'])
#         for e in todayList:
#             print(e)


def printAdvancedDict():
    for eachDict in advancedLevelList:
        if 'receiveStatus' in eachDict.keys():
            print(eachDict['levelName'], 
                  eachDict['receiveStatus'] == 1 and "已领取" or (eachDict['receiveStatus'] == 0 and "已完成" or "未完成")
                  )
        else:
            print(eachDict['levelName'])

def check_time(target_time):
    now = datetime.datetime.now()
    return now >= target_time

def just_receive_mode():
    requestParamsList = []
    for eachDict in advancedLevelList:
        requestParamsList.append(RequestParams(eachDict))
    # 目标时间
    target_time = datetime.datetime.strptime("2023-09-01 02:00:00", r"%Y-%m-%d %H:%M:%S")
    target_time = target_time - datetime.timedelta(seconds=2)
    print(f"预定时间{target_time}")
    
    # 检查cookies
    status = UserLevelStatus(requestParamsList[0])
    status.update()
    printAdvancedDict()
    
    # 需要抢的请求列表
    readyList = [
        ReceiveBonus(x) for x in requestParamsList
    ]
    
    while (True):
        if check_time(target_time):
            while (True):
                for receiveBonus in readyList:
                    r = receiveBonus.request()
                    print(r)
                # tick(0.5)
                if ("频繁" in r or "过快" in r):
                    tick(0.5)
        else:
            print("Waiting...", target_time - datetime.datetime.now())
            if (target_time - datetime.datetime.now()> datetime.timedelta(minutes=5)):
                time.sleep(60)
            elif (target_time - datetime.datetime.now()> datetime.timedelta(seconds=60)):
                time.sleep(10)
            elif (target_time - datetime.datetime.now()> datetime.timedelta(seconds=10)):
                time.sleep(1)

def main_loop():
    just_receive_mode()
    # update_status()

if __name__ == "__main__": 
    main_loop()


    