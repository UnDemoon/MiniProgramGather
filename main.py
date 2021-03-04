'''
@Description:

@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
LastEditors: Please set LastEditors
LastEditTime: 2021-03-04 15:52:33
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
from MyDB import MyDB
#   工具集
import utils as myTools
#   引入采集类
import MiniProgramGather as MPGModel
from MiniProgramGather import MiniProgramGather as MPG

logging.basicConfig(filename='_debug-log.log', level=logging.ERROR,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

#   线程限制信号量
thread_max = threading.BoundedSemaphore(12)


# 采集线程
class GatherThread(threading.Thread):
    def __init__(self, session_id: str, date_tuple: tuple, app_info: dict, api: object, db: object):
        super().__init__()
        self.session_id = session_id
        self.date_tuple = date_tuple
        self.app_info = app_info
        self.api = api
        self.db = db

    def run(self):
        # api = Api()
        #   数据采集
        mpg = MPG(self.session_id, self.date_tuple, self.app_info, self.api, self.db)
        mpg.runGatherer()
        thread_max.release()


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
    session = 'BgAAeqaaPxS6Ru3jahK0qaaUKLQJsBNmoDCxKjLQgfzbU9U'
    date_today = datetime.date.today()
    dates = (datetime.datetime(2021, 2, 25, 0, 0, 0), datetime.datetime(date_today.year, date_today.month, date_today.day, 0, 0, 0))
    #   线程池
    thread_pool = []
    #   上传api
    houyiApi = Api()
    #   本地db
    mydb = MyDB()
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
            thread_max.acquire()
            gather = GatherThread(session, dates, app_info, houyiApi, mydb)
            thread_pool.append(gather)
            gather.start()
            # break
    #   线程统一等待完成
    #   所有完成才可继续主进程
    for t in thread_pool:
        t.join()
    print('END!')
