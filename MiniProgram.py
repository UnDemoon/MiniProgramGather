'''
Author: Demoon
Date: 2021-02-23 10:06:02
LastEditTime: 2021-02-24 11:54:59
LastEditors: Please set LastEditors
Description: 微信小游戏数据助手爬取类
FilePath: /MiniProgramGather/MiniProgram.py
'''
import requests
import json
import time
from urllib.request import quote
import utils as mytools
from PyQt5.QtCore import QDate, Qt, QDateTime
# import datetime


def warpGet(url, session_id, data):
    data = json.dumps(data)
    params = {"session_id": session_id, "data": data}
    res = mytools.moreGet(url, params)
    return res


#   单个游戏采集类
class OneGameData:
    def __init__(self, session_id: str, dates: tuple, appid: str):
        self.session_id = session_id
        self.date_tuple = dates
        self.appid = appid

    #   获取 wx_weixin_app_advertisement 表数据
    def advertisement(self):
        start_uix, end_uix = mytools.dateToStamps(self.date_tuple)
        duration = end_uix - start_uix
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagbdatawap/getwxagstat"
        data = {
            "need_app_info": True,
            "appid": self.appid,
            "sequence_index_list": [{
                "size_type": 24,
                "stat_type": 1000020,
                "data_field_id": 3,
                "filter_list": [],
                "time_period": {
                    "start_time": start_uix,   # 起始时间戳
                    "duration_seconds": duration  # 到结束时间差
                }
            }, {
                "size_type": 24,
                "stat_type": 1000020,
                "data_field_id": 6,
                "filter_list": [],
                "time_period": {
                    "start_time": start_uix,
                    "duration_seconds": duration
                }
            }, {
                "size_type": 24,
                "stat_type": 1000020,
                "data_field_id": 5,
                "filter_list": [],
                "time_period": {
                    "start_time": start_uix,
                    "duration_seconds": duration
                }
            }, {
                "size_type": 24,
                "stat_type": 1000020,
                "data_field_id": 8,
                "filter_list": [],
                "time_period": {
                    "start_time": start_uix,
                    "duration_seconds": duration
                }
            }],
            "group_index_list": [],
            "rank_index_list": [],
            "version": 2
        }
        res = warpGet(url, self.session_id, data)
        print(res)


#   小程序采集类
class MiniProgram:
    def __init__(self, session_id: str):
        self.session_id = session_id

    #   获取游戏列表信息
    def listGames(self):
        game_list = []
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagdatawap/getwxagapplist"
        data = {"offset": "0", "limit": 20}
        while True:
            #   请求数据
            res = warpGet(url, self.session_id, data)
            #   处理数据
            get_data = res.get('data', {})
            game_list += map(
                lambda x: {
                    "appid": x['appid'],
                    "appname": x['appname']
                }, get_data.get('app_list', []))
            if get_data.get('has_next'):
                #   请求数据
                data['offset'] = get_data.get('next_offset')
                res = warpGet(url, self.session_id, data)
                #   处理数据
                get_data = res.get('data', {})
                game_list += map(
                    lambda x: {
                        "appid": x['appid'],
                        "appname": x['appname']
                    }, get_data.get('app_list', []))
            else:
                break
        return game_list
