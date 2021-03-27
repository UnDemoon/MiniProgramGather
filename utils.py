'''
Author: your name
Date: 2021-02-23 10:02:01
LastEditTime: 2021-03-27 14:35:40
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /MiniProgramGather/utils.py
'''
import os
import random
import time
import requests
from urllib import parse
import datetime
#   忽略证书警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


#   随机间隔
def randomSleep(limit_t: float = 0.5, max_t: float = 1.5):
    ret = random.uniform(limit_t, max_t)
    time.sleep(ret)


#   获取开始结束日期
def timeLag(daylag: int = 5, timetype: str = 'uix'):  # 日期间隔  类型 uix时间戳 day日期
    res = False
    endday = datetime.date.today()
    enduix = int(time.mktime(time.strptime(str(endday), '%Y-%m-%d')))
    startday = endday - datetime.timedelta(days=daylag)  # 默认最近几天
    startuix = int(time.mktime(time.strptime(str(startday), '%Y-%m-%d')))
    if timetype == 'uix':
        res = (startuix, enduix)
    else:
        res = (startday, endday)
    return res


#   生成最近n天日期
#   dateAry (datetime, datetime)
def dateList(dateAry: tuple):
    start, end = dateAry
    res = []
    cur_day = start
    while True:
        # res.append(cur_day)
        res.append(int(cur_day.timestamp()))
        cur_day = cur_day + datetime.timedelta(days=1)
        if cur_day >= end:
            break
    return res


#   datetime 转时间戳
#   dateAry (datetime, datetime)
def dateToStamps(dateAry: tuple):
    start, end = dateAry
    return (int(start.timestamp()), int(end.timestamp()))


#   时间戳转 date
def unixTimeDate(unix_time: int):
    timeArray = time.localtime(unix_time)
    date = time.strftime("%Y-%m-%d", timeArray)
    return date


#   拆解url参数
def urlParam(url: str):
    query = parse.urlparse(url).query
    return dict([(k, v[0]) for k, v in parse.parse_qs(query).items()])


#   _get 方法
def moreGet(url, para, time: int = 3):
    temp_time = time
    res = None
    while temp_time >= 0:
        randomSleep()
        res = _subGet(url, para)
        temp_time -= 1
        if res.get('errcode') == 0:
            break
    return res


#   _get子方法
def _subGet(url, para):
    res = {}
    try:
        r = requests.get(url, params=para, verify=False)
        res = r.json()
    except BaseException as e:
        print(str(e))
    return res


def logFile(strings: str, file='_ctm_debug-log.log'):
    """
    字符串写入文件
    """
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    with open(file, 'a+', encoding='utf-8') as f:
        f.write('\n')
        f.write(now)
        f.write('\n')
        f.write(strings)
        f.write('\n')


#   写入文件
def writeToFile(file_path: str, data_str: str):
    with open(file_path, 'a+', encoding='utf-8') as f:
        f.write(data_str)


#   文件的路径
def filePath(file_name: str):
    path = os.path.dirname(os.path.abspath(__file__))  # 获取当前路径
    file = os.path.join(path, file_name)
    return file


if __name__ == '__main__':
    pass
