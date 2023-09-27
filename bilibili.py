from spider_base import *
import json
import datetime
import time

DEBUG = False

# 此处配置需要抢的页面id和对应时间
id_config = [
    # {
    #    "t_id": "23268e79",
    #    "name": "开播60min",
    #    "time": "01:00:00", 
    # }, 
    # {
    #    "t_id": "401a8931",
    #    "name": "开播120min",
    #    "time": "02:00:00", 
    # }, 
    # {
    #    "t_id": "c96e7d04",
    #    "name": "观看10min",
    #    "time": "00:00:00", 
    # },
    # {
    #    "t_id": "9712397d",
    #    "name": "10电池",
    #    "time": "00:00:00", 
    # }, 
    # {
    #    "t_id": "e9a33442",
    #    "name": "弹幕6条",
    #    "time": "00:00:00", 
    # }, 
    # {
    #    "t_id": "a34107fd",
    #    "name": "牛蛙",
    #    "time": "00:00:00", 
    # }, 
    # {
    #    "t_id": "b0c28690",
    #    "name": "累积5天",
    #    "time": "00:00:00", 
    # }, 
    {
       "t_id": "673468a9",
       "name": "20tian",
       "time": "00:00:00", 
    }, 
]

# 此处配置抢兑换码页面的请求中带的csrf字段
csrf = "937b5b6151b53a8bedde6a658567b3ed"

with open("bilibili/cookies.txt", "r+", encoding="utf-8") as f:
    common_cookies = f.read()

class Config:
    def __init__(self) -> None:
        
        pass

def get_info(id: str):
    with open("bilibili/single_task_cookies.txt", "r+") as f:
        h = f.read()
    headers = get_headersDict_2(h)
    headers['Cookie'] = common_cookies
        
    url = "https://api.bilibili.com/x/activity/mission/single_task"
    p = "csrf=0363f50af50e6fe2fabc5a65ae598a0c&id=b1c26a25"
    params = getDict(p)
    params['id'] = id
    params['csrf'] = csrf
    # r = getHTMLText(url, headers=headers, params=params)
    # print(headers)
    r = requests.get(url, params=params, headers=headers)
    if DEBUG:
        print(r.text)
        with open("./bilibili/debug.json", "w+", encoding="utf-8") as f:
                f.write(r.text)
    res = json.loads(r.text)
    group_list = res['data']['task_info']['group_list'][0]
    task_id = group_list['task_id']
    act_id = group_list['act_id']
    group_id = group_list['group_id']
    receive_id = res['data']['task_info']['receive_id']
    act_name = res['data']['act_info']['act_name']
    task_name = res['data']['task_info']['task_name']
    reward_name = res['data']['task_info']['reward_info']['reward_name']
    receive_status = res['data']['task_info']['receive_status']
    
    return {
        "task_id": task_id, 
        "act_id": act_id, 
        "group_id": group_id, 
        "receive_id": receive_id, 
        "act_name": act_name, 
        "task_name": task_name, 
        "reward_name": reward_name, 
        "receive_status": receive_status, 
    }
    
def receive(info: dict):
    with open("bilibili/receive_cookies.txt", "r+") as f:
        h2 = f.read()
    headers2 = get_headersDict_2(h2)
    headers2['Cookie'] = common_cookies
    
    url2 = "https://api.bilibili.com/x/activity/mission/task/reward/receive"
    d = '''csrf: 0363f50af50e6fe2fabc5a65ae598a0c
    act_id: 727
    task_id: 2865
    group_id: 0
    receive_id: 0
    receive_from: missionPage
    act_name: 星穹铁道1.1版本任务【直播】
    task_name: 每日开播满60分钟
    reward_name: 提纯以太*5
    gaia_vtoken: '''
    data = get_headersDict(d)
    data['csrf'] = csrf

    data['act_id'] = info["act_id"]
    data['task_id'] = info["task_id"]
    data['group_id'] = info["group_id"]
    data['receive_id'] = info["receive_id"]
    data['act_name'] = info["act_name"]
    data['task_name'] = info["task_name"]
    data['reward_name'] = info["reward_name"]

    r = post_HTMLText(url2, headers=headers2, data=data)
    return r

def tick(period = 0.5):
    time.sleep(period)

info_dict = {}
def update_status():
    info_dict.clear()
    print('任务列表')
    for conf in id_config:
        t_id = conf['t_id']
        info = get_info(t_id)
        info_dict[t_id] = info
        print(info['task_name'], info['receive_status'] == 0 and "未完成" or (
            info['receive_status'] == 1 and "已完成" or info['receive_status']))
        tick(0.5)
        
def check_time(target_time):
    now = datetime.datetime.now()
    return now >= target_time
        
# 此为单次完整的任务
def single_task(check_status = True, enable_conf_time = True, just_receive = False):
    if just_receive:
        for t_id, info in info_dict.items():
            r = receive(info)
            print(r)
            tick()
        return
    if check_status:
        update_status()
        tick()
    for t_id, info in info_dict.items():
        if info['receive_status'] == 1:
            r = receive(info)
            print(r)
            tick()

def just_receive_mode():
    update_status()
    # 目标时间
    target_time = datetime.datetime.strptime("2023-09-29 00:00:00", r"%Y-%m-%d %H:%M:%S")
    target_time = target_time - datetime.timedelta(seconds=0)
    print(f"实际预定时间：{target_time}")
    while (True):
        if check_time(target_time):
            # update_status()
            while (True):
                for t_id, info in info_dict.items():
                    r = receive(info)
                    print(t_id, r)
                # tick(0.5)
                if ("频繁" in r):
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