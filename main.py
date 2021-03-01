'''
@Description:

@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
LastEditors: Please set LastEditors
LastEditTime: 2021-03-01 16:45:38
'''
#  基础模块
import sys
import time
import datetime
import logging
import threading
#   qt5
from PyQt5.QtCore import QDate
#   引入浏览器线程类#   引入api类
from HouyiApi import HouyiApi as Api
#   工具集
import utils as myTools
#   引入采集类
import MiniProgramGather as MPGModel
from MiniProgramGather import MiniProgramGather as MPG

logging.basicConfig(filename='_debug-log.log', level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


# 采集线程
class GatherThread(threading.Thread):
    def __init__(self, session_id: str, date_tuple: tuple, app_info: dict, api: object):
        super().__init__()
        self.session_id = session_id
        self.date_tuple = date_tuple
        self.app_info = app_info
        self.api = api

    def run(self):
        # api = Api()
        #   数据采集
        mpg = MPG(self.session_id, self.date_tuple, self.app_info, self.api)
        mpg.runGatherer()


# if __name__ == '__main__':
#     # 定义为全局变量，方便其他模块使用
#     global RUN_EVN
#     try:
#         RUN_EVN = sys.argv[1]
#     except Exception:
#         pass
#     app = QtWidgets.QApplication(sys.argv)
#     window = MyApp()
#     window.show()
#     sys.exit(app.exec_())

if __name__ == '__main__':
    houyiApi = Api()
    session = 'BgAApXptU9UVT6FKYY_dPdYIFxBwDuM3vau5vjvFJvOM-dk'
    date_today = datetime.date.today()
    dates = (datetime.datetime(2021, 2, 25, 0, 0, 0), datetime.datetime(date_today.year, date_today.month, date_today.day, 0, 0, 0))
    #   处理appid与app_id数据
    app_infos = houyiApi.pageData('list_apps', None)
    app_list = app_infos.get('Result', {}).get('List', [])
    app_dict = {}
    for app in app_list:
        app_dict[app['appid']] = app['id']
    #   抓取数据
    gl = MPGModel.listGames(session)
    if len(app_dict) > 0 and len(gl) > 0:
        for g in gl:
            app_id = app_dict.get(g['appid'])
            appid = g.get('appid')
            if not app_id or not appid:
                break
            app_info = {'appid': appid, 'app_id': app_id}
            gather = GatherThread(session, dates, app_info, houyiApi)
            gather.start()
            # break
