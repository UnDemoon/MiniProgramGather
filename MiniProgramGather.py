'''
Author: Demoon
Date: 2021-02-23 10:06:02
LastEditTime: 2021-03-01 17:10:52
LastEditors: Please set LastEditors
Description: 微信小游戏数据助手爬取类
FilePath: /MiniProgramGather/MiniProgram.py
'''
import requests
import json
import time
import os
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
    def __init__(self, session_id: str, dates: tuple, app_info: dict, houyiApi: object):
        self.session_id = session_id
        self.date_tuple = dates
        self.app_info = app_info
        self.api = houyiApi

    #   运行采集
    #   遍历 reqdata 下配置文件依次获取数据并发送
    #   仅适用于无依赖接口
    def runGatherer(self):
        self.channelData()
        return True
        start_uix, end_uix = mytools.dateToStamps(self.date_tuple)
        duration = end_uix - start_uix
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagbdatawap/getwxagstat"
        path = "./reqdata/"
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    req_conf = json.load(f)
                    reqdata = self._buildReqdata(req_conf['request_data'], (start_uix, duration))
                    reqs = warpGet(url, self.session_id, reqdata)
                    data = self._formatRes(reqs, req_conf['field_name_list'])
                    self.api.up(req_conf['api_interface'], data)

    #   特殊处理获取渠道数据接口
    def channelData(self):
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagbdatawap/getwxagstat"
        dayuix_list = mytools.dateList(self.date_tuple)
        duration = 24 * 60 * 60  # 86400
        #   获取自定义渠道
        #   该接口 duration_seconds 只支持 86400
        request_data = {
            "need_app_info": True,
            "appid": "wx544d1855bb3963d5",
            "sequence_index_list": [],
            "group_index_list": [{
                "size_type": 24,
                "requestType": "group",
                "time_period": {
                    "start_time": 1614441600,
                    "duration_seconds": 86400
                },
                "group_id": 4,
                "stat_type": 1000088,
                "data_field_id": 6
            }],
            "rank_index_list": [],
            "version": 2
        }
        for suix in dayuix_list:
            reqdata = self._buildReqdata(request_data, (suix, duration))
            reqs = warpGet(url, self.session_id, reqdata)
            data = self._formatResChannelGroup(reqs)
            self.api.up('addWeixinChannelGroup', data)

    #   处理请求数据
    def _buildReqdata(self, request_data: dict, time_period: tuple):
        start_uix, duration = time_period
        request_data['appid'] = self.app_info['appid']
        index_list = ['sequence_index_list', 'group_index_list', 'rank_index_list']
        for idx_name in index_list:
            if request_data.get(idx_name, None):
                for sequence in request_data[idx_name]:
                    if sequence.get('time_period', None):
                        sequence['time_period'] = {
                            "start_time": start_uix,
                            "duration_seconds": duration
                            }
        return request_data

    #   处理返回数据
    def _formatRes(self, reqs_json_dict: dict, field_list: list):
        res = []
        sequence_data_list = reqs_json_dict.get('data', {}).get('sequence_data_list')
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

    #   处理渠道分组数据
    def _formatResChannelGroup(self, reqs_json_dict: dict):
        res = []
        group_data_list = reqs_json_dict.get('data', {}).get('group_data_list')
        if group_data_list:
            point_list = group_data_list[0]['point_list']
            for item in point_list:
                temp = {}
                temp['req_value'] = item['label_value']
                temp['name'] = item['label']
                temp['group_id'] = 0  # 这个字段修改了后台，用不上了
                temp['app_id'] = self.app_info['app_id']
                res.append(temp)
        return res
