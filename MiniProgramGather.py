'''
Author: Demoon
Date: 2021-02-23 10:06:02
LastEditTime: 2021-02-25 15:48:35
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
    def __init__(self, session_id: str, dates: tuple, app_info: dict):
        self.session_id = session_id
        self.date_tuple = dates
        self.app_info = app_info

    #   获取wx_weixin_app_advertisement表数据
    # 主要为日收入、点击、报告、点击率，其他数据没有，所以舍弃
    def advertisement(self):
        filter_config = [{
            "filter_list":
            None,
            'field_name_list':
            ['income', 'show_times', 'click_times', 'click_ratio']
        }, {
            "filter_list": {
                "name": "激励视频广告",
                "field_id": 2,
                "value": "1030436212907001"
            },
            'field_name_list': [
                'video_income', 'video_show_times', 'video_click_times',
                'video_ratio'
            ]
        }, {
            "filter_list": {
                "name": "banner广告",
                "field_id": 2,
                "value": "8040321819858439"
            },
            'field_name_list': [
                'banner_income', 'banner_show_times', 'banner_click_times',
                'banner_ratio'
            ]
        }]
        res_collect = []
        for conf in filter_config:
            temp_list = []
            if conf['filter_list']:
                temp_list.append(conf['filter_list'])
            res_collect += self._advertisementSub(temp_list,
                                                  conf['field_name_list'])
        return res_collect

    #   advertisement  子程序
    def _advertisementSub(self, filter_list: list, field_list: list):
        start_uix, end_uix = mytools.dateToStamps(self.date_tuple)
        duration = end_uix - start_uix
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagbdatawap/getwxagstat"
        data = {
            "need_app_info":
            False,
            "appid":
            self.app_info['appid'],
            "sequence_index_list": [
                {
                    "size_type": 24,
                    "stat_type": 1000020,
                    "data_field_id": 3,
                    "filter_list": filter_list,
                    "time_period": {
                        "start_time": start_uix,  # 起始时间戳
                        "duration_seconds": duration  # 到结束时间差
                    }
                },
                {
                    "size_type": 24,
                    "stat_type": 1000020,
                    "data_field_id": 6,
                    "filter_list": filter_list,
                    "time_period": {
                        "start_time": start_uix,
                        "duration_seconds": duration
                    }
                },
                {
                    "size_type": 24,
                    "stat_type": 1000020,
                    "data_field_id": 5,
                    "filter_list": filter_list,
                    "time_period": {
                        "start_time": start_uix,
                        "duration_seconds": duration
                    }
                },
                {
                    "size_type": 24,
                    "stat_type": 1000020,
                    "data_field_id": 8,
                    "filter_list": filter_list,
                    "time_period": {
                        "start_time": start_uix,
                        "duration_seconds": duration
                    }
                }
            ],
            "group_index_list": [],
            "rank_index_list": [],
            "version":
            2
        }
        reqs = warpGet(url, self.session_id, data)
        #   返回数据处理
        res = []
        sequence_data_list = reqs.get('data', {}).get('sequence_data_list')
        if sequence_data_list:
            for i in range(0, len(field_list)):
                field_name = field_list[i]
                point_list = sequence_data_list[i]['point_list']
                for item in point_list:
                    temp = {}
                    temp[field_name] = item.get('value', 0)
                    temp['day'] = item['label']
                    temp['app_id'] = self.app_info['app_id']
                    res.append(temp)
        return res

    #   获取wx_weixin_app_data表数据
    def appData(self):
        au = self._appDataAu()
        au_ratio = self._appDataAuRatio()

    #   获取活跃用户相关数据，appData子程序之一
    def _appDataAu(self):
        start_uix, end_uix = mytools.dateToStamps(self.date_tuple)
        duration = end_uix - start_uix
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagbdatawap/getwxagstat"
        data = {
            "need_app_info":
            False,
            "appid":
            self.app_info['appid'],
            "sequence_index_list": [{
                "size_type":
                24,
                "stat_type":
                1000001,
                "data_field_id":
                5,
                "filter_list": [{
                    "name": "全部平台",
                    "field_id": 9,
                    "value": "-9999"
                }],
                "time_period": {
                    "start_time": start_uix,
                    "duration_seconds": duration
                }
            }, {
                "size_type":
                24,
                "stat_type":
                1000001,
                "data_field_id":
                6,
                "filter_list": [{
                    "name": "全部平台",
                    "field_id": 9,
                    "value": "-9999"
                }],
                "time_period": {
                    "start_time": start_uix,
                    "duration_seconds": duration
                }
            }, {
                "size_type":
                24,
                "stat_type":
                1000001,
                "data_field_id":
                8,
                "filter_list": [{
                    "name": "全部平台",
                    "field_id": 9,
                    "value": "-9999"
                }],
                "time_period": {
                    "start_time": start_uix,
                    "duration_seconds": duration
                }
            }, {
                "size_type":
                24,
                "stat_type":
                1000001,
                "data_field_id":
                7,
                "filter_list": [{
                    "name": "全部平台",
                    "field_id": 9,
                    "value": "-9999"
                }],
                "time_period": {
                    "start_time": start_uix,
                    "duration_seconds": duration
                }
            }],
            "group_index_list": [],
            "rank_index_list": [],
            "version":
            2
        }
        reqs = warpGet(url, self.session_id, data)
        #   返回数据处理
        res = []
        field_list = [
            'active_user', 'access_times', 'avg_access_times', 'avg_delay'
        ]
        sequence_data_list = reqs.get('data', {}).get('sequence_data_list')
        if sequence_data_list:
            for i in range(0, len(field_list)):
                field_name = field_list[i]
                point_list = sequence_data_list[i]['point_list']
                for item in point_list:
                    temp = {}
                    temp[field_name] = item.get('value', 0)
                    temp['day'] = item['label']
                    temp['app_id'] = self.app_info['app_id']
                    res.append(temp)
        return res

    #   活跃用户留存数据
    def _appDataAuRatio(self):
        data = {
            "need_app_info":
            False,
            "appid":
            self.app_info['appid'],
            "sequence_index_list": [{
                "size_type":
                24,
                "stat_type":
                1000010,
                "data_field_id":
                3,
                "filter_list": [{
                    "name": "全部平台",
                    "field_id": 8,
                    "value": "-9999"
                }],
                "time_period": {
                    "start_time": 1613664000,
                    "duration_seconds": 518400
                }
            }, {
                "size_type":
                24,
                "stat_type":
                1000010,
                "data_field_id":
                4,
                "filter_list": [{
                    "name": "全部平台",
                    "field_id": 8,
                    "value": "-9999"
                }],
                "time_period": {
                    "start_time": 1613664000,
                    "duration_seconds": 518400
                }
            }, {
                "size_type":
                24,
                "stat_type":
                1000010,
                "data_field_id":
                5,
                "filter_list": [{
                    "name": "全部平台",
                    "field_id": 8,
                    "value": "-9999"
                }],
                "time_period": {
                    "start_time": 1613664000,
                    "duration_seconds": 518400
                }
            }],
            "group_index_list": [],
            "rank_index_list": [],
            "version":
            2
        }
