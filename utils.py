"""
Author: your name
Date: 2021-02-23 10:02:01
LastEditTime: 2021-03-27 14:35:40
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /MiniProgramGather/utils.py
"""
import logging
import os
import random
import sys
import time
import requests
from urllib import parse
import datetime
#   忽略证书警告
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
#   log配置
logging.basicConfig(filename='_debug-log.log',
                    level=logging.ERROR,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


#   随机间隔
def randomSleep(limit_t: float = 0.8, max_t: float = 2.6):
    ret = random.uniform(limit_t, max_t)
    time.sleep(ret)


#   获取开始结束日期
def timeLag(daylag: int = 5, timetype: str = 'uix'):  # 日期间隔  类型 uix时间戳 day日期
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
    return int(start.timestamp()), int(end.timestamp())


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
def moreGet(url, para, appid, signal=None, max_try: int = 5):
    if signal:
        signal.log_info.emit(random.choice(['-', '+', '@', '#', '$', '%', '&', '*', '^', '~', '/', '?', '<', '>']))
    temp_time = max_try
    res = None
    while temp_time >= 0:
        randomSleep()
        res = _subGet(url, para)
        temp_time -= 1
        if res.get('errcode') == 0:
            break
    #   循环之后还报错才算错
    if res.get('errcode') != 0:
        errorinfo = {
            'session_id': para.get('session_id', ''),
            'appid': appid,
            'error_info': str(res)
        }
        if signal:
            signal.log_info.emit(str(errorinfo))
    return res


#   _get子方法
def _subGet(url, para):
    res = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'}
    proxy = enumProxyPool()
    proxies = {
        "http": "http://%(proxy)s/" % {'proxy': proxy}
    }
    try:
        r = requests.get(url, params=para, headers=headers, verify=False, proxies=proxies)
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
    # path = os.path.dirname(os.path.abspath(__file__))  # 获取当前路径
    path = os.path.dirname(os.path.realpath(sys.executable))
    file = os.path.join(path, file_name)
    return file


#   获取一个代理
def enumProxyPool():
    #   ProxyPool（https://github.com/Python3WebSpider/ProxyPool.git）项目本地地址
    url = 'http://120.55.100.149/random'
    req = None
    while not req:
        req = requests.get(url)
    return req.text


#   数组按指定长度切割
def listSpiltAsSize(list_data: list, size: int):
    temp = []
    for i in range(0, len(list_data) + 1, size):
        part_list = list_data[i:i + size]
        temp.append(part_list)
    collection_list = [x for x in temp if x]
    return collection_list


#   报错日志
def logError(error_info: str):
    logging.error(error_info)


if __name__ == '__main__':
    pass
