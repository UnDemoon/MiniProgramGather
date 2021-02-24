'''
@Description: 
@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
@LastEditors: Demoon
@LastEditTime: 2020-06-12 10:24:36
'''
import requests
import json
import time
# import datetime


class HouyiApi:
    def __init__(
        self,
        account='caiji',
        pwd='caiji@20200107',
        secret_key='cd283176e1e2c2a69a00e76a52742d42a4ae0b3780eec48fae289977008e9a3b',
        platform_type='WeixinData',
    ):
        with open("./config-default.json", encoding='utf-8') as defcfg:
            cfg = json.load(defcfg)
        self.host = cfg['upload_host']
        self.secret_key = secret_key
        self.urls = {
            'token':
            self.host + '/api/'+platform_type+'/accessToken.html',
            'list_apps':
            self.host + '/api/WeixinData/listAppInfo.html',
            'adv_apps':
            self.host + '/api/WeixinData/listAdvApp.html',
            'add_gamedata':
            self.host + '/api/WeixinData/addGameChannelData.html',
        }
        self.token = self._getToken(account, pwd)

    def _getToken(self, acc, pwd):
        data = {
            'account': acc,
            'password': pwd,
            'secret_key': self.secret_key,
            'timestamp': time.time()
        }
        res = self.post(self.urls['token'], data)
        return res['Result']['token']

    #   post 方法
    def post(self, url, data):
        res = {}
        try:
            r = requests.post(url=url, data=data)
            res = r.json()
        except BaseException as e:
            print(str(e))
        return res

    def up(self, data_type: str, post_data: dict):
        #   转换为字符串
        post_data = json.JSONEncoder().encode(post_data)
        #   构建数据
        data = {'token': self.token, 'data': post_data}
        #   发送
        res = self._subUp(self.urls[data_type], data)
        return res

    #   上传数据重传机制
    def _subUp(self, url, data, time_count=3):
        count = time_count
        if count > 0:
            res = self.post(url, data)
            if res.get('Status') != 200:
                time.sleep(2)
                res = self._subUp(url, data, count - 1)
        return res

    #   多页数据获取
    def pageData(self, data_type: str, pageindex: int = 1, pagesize: int = 2000):
        #   构建数据
        data = {'token': self.token, 'pageindex': pageindex, 'pagesize': pagesize}
        #   发送
        res = self._subUp(self.urls[data_type], data)
        return res
