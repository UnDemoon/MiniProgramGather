'''
Author: Demoon
Date: 2021-02-23 10:06:02
LastEditTime: 2021-02-24 18:09:26
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


#   获取游戏列表
def listGames(session_id):
    game_list = []
    url = "https://game.weixin.qq.com/cgi-bin/gamewxagdatawap/getwxagapplist"
    data = {"offset": "0", "limit": 20}
    while True:
        #   请求数据
        res = warpGet(url, session_id, data)
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
            res = warpGet(url, session_id, data)
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


#   单个游戏采集类
class MiniProgramGather:
    def __init__(self, session_id: str, dates: tuple, appid: str):
        self.session_id = session_id
        self.date_tuple = dates
        self.appid = appid

    def advertisement(self):
        filter_config = [
            {
                "filter_list": None,
                'field_name_list': ['income', 'show_times', 'click_times', 'click_ratio']
            },
            {
                "filter_list": {
                         "name": "激励视频广告",
                         "field_id": 2,
                         "value": "1030436212907001"
                    },
                'field_name_list': ['video_income', 'video_show_times', 'video_click_times', 'video_ratio']
            },
            {
                "filter_list": {
                         "name": "banner广告",
                         "field_id": 2,
                         "value": "8040321819858439"
                    },
                'field_name_list': ['banner_income', 'banner_show_times', 'banner_click_times', 'banner_ratio']
            }
        ]
        res_collect = []
        for conf in filter_config:
            temp_list = []
            temp_list.append(conf['filter_list'])
            res_collect += self._advertisement(temp_list, conf['field_name_list'])
        return res_collect

    #   获取 wx_weixin_app_advertisement 表数据
    def _advertisement(self, filter_list: list, field_list: list):
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
                "filter_list": filter_list,
                "time_period": {
                    "start_time": start_uix,   # 起始时间戳
                    "duration_seconds": duration  # 到结束时间差
                }
            }, {
                "size_type": 24,
                "stat_type": 1000020,
                "data_field_id": 6,
                "filter_list": filter_list,
                "time_period": {
                    "start_time": start_uix,
                    "duration_seconds": duration
                }
            }, {
                "size_type": 24,
                "stat_type": 1000020,
                "data_field_id": 5,
                "filter_list": filter_list,
                "time_period": {
                    "start_time": start_uix,
                    "duration_seconds": duration
                }
            }, {
                "size_type": 24,
                "stat_type": 1000020,
                "data_field_id": 8,
                "filter_list": filter_list,
                "time_period": {
                    "start_time": start_uix,
                    "duration_seconds": duration
                }
            }],
            "group_index_list": [],
            "rank_index_list": [],
            "version": 2
        }
        reqs = warpGet(url, self.session_id, data)
        #   返回数据处理
        res = []
        print(reqs)
        sequence_data_list = reqs['data']['sequence_data_list']
        for i in range(0, len(field_list)):
            field_name = field_list[i]
            point_list = sequence_data_list[i]['point_list']
            for item in point_list:
                temp = {}
                temp[field_name] = item['value']
                temp['day'] = item['label']
                temp['app_id'] = 1
                res.append(temp)
        return res
