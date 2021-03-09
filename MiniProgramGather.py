'''
Author: Demoon
Date: 2021-02-23 10:06:02
LastEditTime: 2021-03-09 15:42:34
LastEditors: Please set LastEditors
Description: 微信小游戏数据助手爬取类
FilePath: /MiniProgramGather/MiniProgram.py
'''
import requests
import json
import time
import os
import utils as mytools
import logging
# import datetime


def warpGet(url, session_id, data):
    data = json.dumps(data)
    params = {"session_id": session_id, "data": data}
    res = mytools.moreGet(url, params)
    return res


#   获取游戏列表
def listGames(session_id):
    res = {
        'errcode': '',
        'game_list': []
    }
    url = "https://game.weixin.qq.com/cgi-bin/gamewxagdatawap/getwxagapplist"
    data = {"offset": "0", "limit": 20}
    while True:
        #   请求数据
        reqs = warpGet(url, session_id, data)
        res['errcode'] = reqs.get('errcode', 0)
        #   处理数据
        get_data = reqs.get('data', {})
        res['game_list'] += map(lambda x: {
                "appid": x['appid'],
                "appname": x['appname']
            }, get_data.get('app_list', []))
        if get_data.get('has_next'):
            #   请求数据
            data['offset'] = get_data.get('next_offset')
        else:
            break
    return res


#   单个游戏采集类
class MiniProgramGather:
    def __init__(self, session_id: str, dates: tuple, app_info: dict,
                 houyiApi: object, mydb: object):
        self.session_id = session_id
        self.date_tuple = dates
        self.app_info = app_info
        self.api = houyiApi
        self.db = mydb

    #   运行采集
    #   遍历 reqdata 下配置文件依次获取数据并发送
    #   仅适用于无依赖接口
    def runGatherer(self):
        #   基础采集
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
                    data = self._formatRes(reqs, req_conf['field_name_list'], req_conf['api_interface'])
                    self.api.up(req_conf['api_interface'], data)
        #   渠道相关特殊采集
        self.channelData()
        #   微信广告收入采集
        self.advIncome()
        #   实时数据
        self.realTime()

    #   实时数据采集 - 访问数据  访问人数、注册、访问次数
    def realTime(self):
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagbdatawap/getwxagstat"
        dayuix_list = mytools.dateList(self.date_tuple)
        duration = 24 * 60 * 60  # 86400
        request_data = {
                "need_app_info": True,
                "appid": "wx544d1855bb3963d5",
                "sequence_index_list": [
                    {
                        "size_type": 60,
                        "stat_type": 1000122,
                        "data_field_id": 5,
                        "filter_list": [],
                        "time_period": {
                            "start_time": 1615132800,
                            "duration_seconds": 86400
                        }
                    },
                    {
                        "size_type": 60,
                        "stat_type": 1000123,
                        "data_field_id": 4,
                        "filter_list": [],
                        "time_period": {
                            "start_time": 1615132800,
                            "duration_seconds": 86400
                        }
                    },
                    {
                        "size_type": 60,
                        "stat_type": 1000122,
                        "data_field_id": 4,
                        "filter_list": [],
                        "time_period": {
                            "start_time": 1615132800,
                            "duration_seconds": 86400
                        }
                    }
                ],
                "group_index_list": [],
                "rank_index_list": [],
                "version": 2
            }
        for suix in dayuix_list:
            reqdata = self._buildReqdata(request_data, (suix, duration))
            reqs = warpGet(url, self.session_id, reqdata)
            data = self._formatRes(reqs, ['visit_user', 'reg_user', 'visit_times'], "addTimeData")
            self.api.up('addTimeData', data)

    #   微信广告收入采集
    def advIncome(self):
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagbdatawap/getwxagstat"
        dayuix_list = mytools.dateList(self.date_tuple)
        duration = 24 * 60 * 60  # 86400
        request_data = {
            "need_app_info": False,
            "appid": "wx544d1855bb3963d5",
            "sequence_index_list": [],
            "group_index_list": [
                {
                    "size_type": 24,
                    "stat_type": 1000121,
                    "data_field_id": 5,
                    "filter_list": [
                        {
                            "field_id": 4,
                            "value": "ad"
                        }
                    ],
                    "time_period": {
                        "start_time": 1614787200,
                        "duration_seconds": 86400
                    },
                    "group_id": 3,
                    "limit": 50,
                    "is_stat_order_asc": False
                }
            ],
            "rank_index_list": [],
            "version": 2
        }
        for suix in dayuix_list:
            reqdata = self._buildReqdata(request_data, (suix, duration))
            reqs = warpGet(url, self.session_id, reqdata)
            data = self._formatResAdvIncome(reqs, ['income'])
            self.api.up('addStatement', data)

    #   特殊处理获取渠道数据接口
    def channelData(self):
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagbdatawap/getwxagstat"
        dayuix_list = mytools.dateList(self.date_tuple)
        duration = 24 * 60 * 60  # 86400
        #   获取自定义渠道
        #   该接口 duration_seconds 只支持 86400
        request_data = {
            "need_app_info": False,
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
            self.saveToDb('channel_group', data)
        #   获取该 app_id 下分组
        group_list = self.db.findAll("SELECT * FROM channel_group WHERE app_id={0}".format(self.app_info['app_id']))
        for group in group_list:
            self._channel(group)
        #   获取该 分组下渠道
        for group in group_list:
            channel_list = self.db.findAll("SELECT * FROM channel WHERE app_id={0} AND group_id={1}".format(self.app_info['app_id'], group[0]))
            if len(channel_list) > 0:
                self._channelData(channel_list, group)
        # 上传渠道 渠道分组
        self._upChannel()

    #   获取渠道
    def _channel(self, group_info: tuple):
        filter_list = [{
            "name": group_info[2],
            "field_id": 4,
            "value": group_info[1]
        }]
        #   活跃渠道相关配置
        request_data_act = {
            "need_app_info": False,
            "appid": "wxf846ea330ed135d7",
            "rank_index_list": [{
                "size_type": 24,
                "main_index": {
                    "name": "来源",
                    "stat_type": 1000088,
                    "size_type": 24,
                    "data_field_id": 6,
                    "key_field_id": 5,
                    "filter_list": filter_list
                },
                "join_index_list": [{
                    "name": "来源",
                    "stat_type": 1000088,
                    "size_type": 24,
                    "data_field_id": 6,
                    "key_field_id": 5,
                    "filter_list": filter_list
                }],
                "cur_page": 0,
                "per_page": 20,
                "time_period": {
                    "start_time": 1614528000,
                    "duration_seconds": 86400
                }
            }],
            "version": 2
        }
        #   注册渠道相关配置
        request_data_reg = {
                "need_app_info": False,
                "appid": "wxf846ea330ed135d7",
                "rank_index_list": [
                    {
                        "size_type": 24,
                        "main_index": {
                            "name": "来源",
                            "stat_type": 1000091,
                            "data_field_id": 6,
                            "size_type": 24,
                            "key_field_id": 5,
                            "filter_list": filter_list
                        },
                        "join_index_list": [
                            {
                                "name": "来源",
                                "stat_type": 1000091,
                                "data_field_id": 6,
                                "size_type": 24,
                                "key_field_id": 5,
                                "filter_list": filter_list
                            }
                        ],
                        "cur_page": 0,
                        "per_page": 20,
                        "time_period": {
                            "start_time": 1614614400,
                            "duration_seconds": 86400
                        }
                    }
                ],
                "version": 2
            }
        self._channelSub(request_data_act)
        self._channelSub(request_data_reg)

    #   _channel 的子程序 因为有活跃和注册区分
    def _channelSub(self, request_data: dict):
        #   变量处理
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagbdatawap/getwxagstat"
        start_uix, end_uix = mytools.dateToStamps(self.date_tuple)
        end_uix = end_uix - 24 * 60 * 60
        duration = 24 * 60 * 60  # 86400
        data = []
        #   请求阶段
        while True:
            reqdata = self._buildReqdata(request_data, (end_uix, duration))
            reqs = warpGet(url, self.session_id, reqdata)
            next_page = reqs.get('data', {}).get('rank_data_list', [{}])[0].get("next_page")
            has_next = reqs.get('data', {}).get('rank_data_list', [{}])[0].get("has_next", False)
            data += self._formatResChannel(reqs)
            if has_next and next_page:
                request_data['rank_index_list'][0]['cur_page'] = next_page
            else:
                break
        self.saveToDb('channel', data)

    #   获取渠道数据
    def _channelData(self, channel_list: list, group_info: dict):
        url = "https://game.weixin.qq.com/cgi-bin/gamewxagbdatawap/getwxagstat"
        start_uix, end_uix = mytools.dateToStamps(self.date_tuple)
        duration = end_uix - start_uix
        field_list = [
            "act_user",
            "access_times",
            "act_next_ratio",
            "avg_delay",
            "reg_user",
            "reg_next_ratio",
            "reg_total",
        ]
        #   field_list 和 sequence_item_conf 顺序是对应的
        sequence_item_conf = [{
            "stat_type": 1000088,
            "data_field_id": 6,     # 活跃用户数
        }, {
            "stat_type": 1000088,
            "data_field_id": 7,     # 访问次数
        }, {
            "stat_type": 1000089,   # 活跃用户次日留存率
            "data_field_id": 6,
        }, {
            "stat_type": 1000088,   # 人均在线时长
            "data_field_id": 9,
        }, {
            "stat_type": 1000091,   # 注册用户数
            "data_field_id": 6,
        }, {
            "stat_type": 1000093,   # 注册用户次日留存率
            "data_field_id": 6,
        }, {
            "stat_type": 1000094,   # 累计注册用户
            "data_field_id": 6,
        }]
        #   下面两个配置的数据用不着 不要了
        # {
        #     "stat_type": 1000092,   # 新增付费用户数
        #     "data_field_id": 6,
        # }, {
        #     "stat_type": 1000092,   # 新增付费金额
        #     "data_field_id": 7,
        # }
        
        #   构建发送的数据
        sequence_index_list = []
        for channel in channel_list:
            for item in sequence_item_conf:
                temp = {
                    "size_type": 24,
                    "stat_type": item['stat_type'],
                    "data_field_id": item['data_field_id'],
                    "filter_list": [
                        {
                            "field_id": 4,
                            "value": group_info[1]
                        },
                        {
                            "name": channel[3],
                            "value": channel[2],
                            "field_id": 5,
                            "checked": True
                        }
                    ],
                    "time_period": {
                        "start_time": 1614096000,
                        "duration_seconds": 604800
                    }
                }
                sequence_index_list.append(temp)
        request_data = {
            "need_app_info": False,
            "appid": "wxf846ea330ed135d7",
            "sequence_index_list": sequence_index_list,
            "group_index_list": [],
            "rank_index_list": [],
            "version": 2
        }
        reqdata = self._buildReqdata(request_data, (start_uix, duration))
        reqs = warpGet(url, self.session_id, reqdata)
        data = self._formatResChannelData(reqs, field_list)
        self.api.up('addWeixinChannelData', data)

    #   处理请求数据
    def _buildReqdata(self, request_data: dict, time_period: tuple):
        start_uix, duration = time_period
        request_data['appid'] = self.app_info['appid']
        index_list = [
            'sequence_index_list', 'group_index_list', 'rank_index_list'
        ]
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
    def _formatRes(self, reqs_json_dict: dict, field_list: list, data_type: str):
        res = []
        sequence_data_list = reqs_json_dict.get('data', {}).get('sequence_data_list')
        if len(sequence_data_list) > 0:
            for i in range(0, len(field_list)):
                field_name = field_list[i]
                point_list = sequence_data_list[i]['point_list']
                for item in point_list:
                    temp = {}
                    #   根据数据类型区分处理方式
                    if data_type == "addSourceDistribution":
                        temp['value'] = item.get('value', 0)
                        temp['value_type'] = i + 1    # i=0 active_user i=1 new_user 配合后台
                        temp['day'] = item['label']
                        temp['label_value'] = 33
                        temp['label'] = "微信广告"
                        temp['appId'] = self.app_info['appid']
                    elif data_type == "addTimeData":
                        temp[field_name] = item.get('value', 0)
                        temp['time'] = item['label_value']
                        temp['app_id'] = self.app_info['app_id']
                    else:
                        temp[field_name] = item.get('value', 0)
                        temp['day'] = item['label']
                        temp['app_id'] = self.app_info['app_id']
                    res.append(temp)
        return res

    #   处理渠道分组数据
    def _formatResChannelGroup(self, reqs_json_dict: dict):
        res = []
        group_data_list = reqs_json_dict.get('data', {}).get('group_data_list', [])
        if len(group_data_list) > 0:
            point_list = group_data_list[0]['point_list']
            for item in point_list:
                # temp = {}
                # temp['req_value'] = item['label_value']
                # temp['name'] = item['label']
                # temp['group_id'] = 0  # 这个字段修改了后台，用不上了
                # temp['app_id'] = self.app_info['app_id']
                temp = (item['label_value'], item['label'],
                        self.app_info['app_id'])
                res.append(temp)
        return res

    #   处理渠道数据
    def _formatResChannel(self, reqs_json_dict: dict):
        res = []
        rank_data_list = reqs_json_dict.get('data', {}).get('rank_data_list', [])
        if len(rank_data_list) > 0:
            stat_list = rank_data_list[0]['stat_list']
            filter_list = rank_data_list[0].get('index', {}).get('main_index', {}).get('filter_list', [])
            group_req_value = filter_list[0].get('value') if len(filter_list) > 0 else ""
            for item in stat_list:
                # temp = {}
                # temp['req_value'] = item['label_value']
                # temp['name'] = item['label']
                # temp['group_id'] = 0  # 这个字段修改了后台，用不上了
                # temp['app_id'] = self.app_info['app_id']
                temp = (self.app_info['app_id'], item['key_field_value'], item['key_field_label'], group_req_value)
                res.append(temp)
        return res

    #   处理渠道数据
    #   对应渠道的 活跃 注册 等
    def _formatResChannelData(self, reqs_json_dict: dict, field_list: list):
        res = []
        sequence_data_list = reqs_json_dict.get('data', {}).get('sequence_data_list')
        if len(sequence_data_list) > 0:
            for i in range(0, len(sequence_data_list)):
                sequence = sequence_data_list[i]
                #   获取渠道的 wxgamecid
                wxgamecid = sequence.get('index', {}).get('filter_list', [{}, {}])[1].get('value', '')
                point_list = sequence.get('point_list', [])
                #   获取争取的字段名
                field_name = field_list[i % len(field_list)]
                for item in point_list:
                    temp = {}
                    temp[field_name] = item.get('value', 0)
                    temp['day'] = item['label']
                    temp['wxgamecid'] = wxgamecid
                    temp['app_id'] = self.app_info['app_id']
                    res.append(temp)
        return res

    #   处理微信广告收入数据
    def _formatResAdvIncome(self, reqs_json_dict: dict, filter_list: list):
        res = []
        group_data_list = reqs_json_dict.get('data', {}).get('group_data_list')
        if len(group_data_list) > 0:
            for i in range(0, len(group_data_list)):
                point_list = group_data_list[i].get('point_list', [])
                day_uix = group_data_list[i].get('index', {}).get('time_period', {}).get('start_time')
                #   获取争取的字段名
                field_name = filter_list[i]
                for item in point_list:
                    if int(item.get('label_value', 0)) == 33:    # 只取微信广告，其他没用
                        temp = {}
                        temp[field_name] = item.get('value', 0)
                        temp['day'] = mytools.unixTimeDate(int(day_uix))
                        temp['group_value'] = 4    # 之前认定场景值 微信广告
                        temp['appId'] = self.app_info['appid']
                        res.append(temp)
        return res

    #   数据存储
    def saveToDb(self, tbl_name: str, data: list):
        filter_data = []
        if tbl_name == 'channel_group':
            i = 0
            while i < len(data):
                item = data[i]
                find_sql = "SELECT * FROM channel_group WHERE req_value='{0}' AND name='{1}' AND app_id={2}".format(
                    item[0], item[1], item[2])
                if not self.db.find(find_sql):
                    filter_data.append(item)
                i += 1
        elif tbl_name == 'channel':
            i = 0
            while i < len(data):
                item = data[i]
                find_sql = "SELECT * FROM channel WHERE app_id={0} AND out_channel_id='{1}' AND name='{2}'".format(
                    item[0], item[1], item[2])
                if not self.db.find(find_sql):
                    find_sql = "SELECT * FROM channel_group WHERE app_id={0} AND req_value='{1}'".format(item[0], item[3])
                    group = self.db.find(find_sql)
                    if group:
                        filter_data.append((item[0], item[1], item[2], group[0], group[2]))
                    else:
                        logging.error("Not find group.Info:{0}".format(str(item)))
                i += 1
        self.db.save(tbl_name, filter_data)

    #   上传channel 和 group数据
    def _upChannel(self):
        #   该游戏的渠道分组上传
        group_list = self.db.findAll("SELECT * FROM channel_group WHERE app_id={0}".format(self.app_info['app_id']))
        data = list(map(lambda x: {
            'group_id': x[0],
            'req_value': x[1],
            'name': x[2],
            'app_id': x[3],
            }, group_list))
        self.api.up('addWeixinChannelGroup', data)
        #   该游戏的渠道上传
        channel_list = self.db.findAll("SELECT * FROM channel WHERE app_id={0}".format(self.app_info['app_id']))
        data = list(map(lambda x: {
            'app_id': x[1],
            'out_channel_id': x[2],
            'name': x[3],
            'group_id': x[4],
            'group_name': x[5],
            }, channel_list))
        self.api.up('addWeixinChannel', data)
