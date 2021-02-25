'''
Author: Demoon
Date: 2021-02-23 10:06:02
LastEditTime: 2021-02-25 17:56:11
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

    #   获取wx_weixin_app_data表数据
    def appData(self):
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagbdatawap/getwxagstat"
        path = "./reqdata/"
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    req_conf = json.load(f)
                    reqdata = self._buildReqdata(req_conf['request_data'])
                    reqs = warpGet(url, self.session_id, reqdata)
                    data = self._formatRes(reqs, req_conf['field_name_list'])
                    self.api.up(req_conf['api_interface'], data)

    #   处理请求数据
    def _buildReqdata(self, request_data: dict):
        start_uix, end_uix = mytools.dateToStamps(self.date_tuple)
        duration = end_uix - start_uix
        request_data['appid'] = self.app_info['appid']
        for sequence in request_data['sequence_index_list']:
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
