'''
@Description:

@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
LastEditors: Please set LastEditors
LastEditTime: 2021-02-25 18:08:09
'''
#  基础模块
import sys
import time
import logging
import threading
#   qt5
from PyQt5 import QtWidgets
from PyQt5.Qt import QThread
from PyQt5.QtCore import QDate, Qt, QDateTime
from PyQt5.QtGui import QColor
#   引入ui文件
from home import Ui_MainWindow as Ui
#   引入浏览器线程类#   引入api类
from HouyiApi import HouyiApi as Api
#   工具集
import utils as myTools
#   引入采集类
import MiniProgramGather as MPGModel
from MiniProgramGather import MiniProgramGather as MPG

logging.basicConfig(filename='_debug-log.log', level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class MyApp(QtWidgets.QMainWindow, Ui):
    def __init__(self):
        #   UI
        QtWidgets.QMainWindow.__init__(self)
        Ui.__init__(self)
        self.setupUi(self)
        self.api = Api()
        self.bar_note = None
        self.browser = None
        self.run_urls = []  # 要采集的url集合
        self.thread_pools = []   # 线程池
        # 方法
        self._initdata()
        self.DateEdit.dateChanged.connect(self._timeInit)
        self.pushButton.clicked.connect(self.start_run)

    #   数据初始化
    def _initdata(self):
        today = QDate.currentDate()
        self.DateEdit.setDate(today)
        self.DateEdit.setCalendarPopup(True)
        self.DateEdit_2.setDate(today.addDays(-5))
        self.DateEdit_2.setEnabled(False)
        #   处理appid与app_id数据
        app_infos = self.api.pageData('list_apps', None)
        app_list = app_infos.get('Result', {}).get('List', [])
        app_dict = map(lambda x: {
            str(x['appid']): str(x['id']),
            }, app_list)
        myTools.writeToFile('appinfos.tmp', str(list(app_dict)))

    #   时间处理
    def _timeInit(self):
        endDate = self.DateEdit.date()
        self.DateEdit_2.setDate(endDate.addDays(-5))

    #   按钮触发
    def start_run(self):
        session = 'BgAAIS2RR62FKL7-tzSc-5swJfvK7Inb62nAWuL5JvyqPVg'
        dates = (self.DateEdit_2.date(), self.DateEdit.date())
        gl = MPGModel.listGames(session)
        for g in gl:
            gather = GatherThread(session, dates, g['appid'], self.api)
            self.thread_pools.append(gather)
            # self.threadPools.append(gather)
            # gather.sig.completed.connect(self._completedListener)
            gather.start()
            break


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
        mpg.appData()


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
    session = 'BgAAOZ7VdTGC1Lj1D8Gfdl2Xs5arxanYFAonOpWJhRVdLkU'
    dates = (QDate(2021, 2, 20), QDate(2021, 2, 25))
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
