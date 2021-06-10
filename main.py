"""
@Description:
@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
LastEditors: Please set LastEditors
LastEditTime: 2021-02-19 09:31:08
"""
import datetime
import json
#  基础模块
import logging
import sys
import threading
import time
#   qt5
from PyQt5 import QtWidgets
from PyQt5.Qt import QThread
from PyQt5.QtCore import pyqtSignal, QObject, QDate, QDateTime, QTime
from PyQt5.QtWidgets import QMessageBox
#   引入ui文件
from home import Ui_MainWindow as Ui
#   引入采集类
import MiniProgramGather as MPGModel
#   引入db
from MyDB import MyDB
#   引入后裔api
from HouyiApi import HouyiApi
import utils as  mytools


class MyAppThread(QThread):
    def __init__(self, session_id: str, target_appid: str, date_tuple: tuple, houyi_api: object):
        super().__init__()
        self.session_id = session_id
        self.target_appid = target_appid
        self.date_tuple = date_tuple
        self.houyi_api = houyi_api
        self.signal = LogSignal()

    #   分装fuc方便进程调用
    def run(self):
        #   线程限制信号量
        thread_max = threading.BoundedSemaphore(8)
        #   根据日期构建采集时间数据
        dates = self.date_tuple
        #   线程池
        thread_pool = []
        #   本地db
        mydb = MyDB()
        #   处理appid与app_id数据
        app_infos = self.houyi_api.pageData('list_apps', None)
        app_list = app_infos.get('Result', {}).get('List', [])
        app_dict = {}
        for one_app in app_list:
            app_dict[one_app['appid']] = one_app['id']
        #   抓取数据
        gl_info = MPGModel.MiniProgramGather.listGames(self.session_id)
        if gl_info['errcode'] != 0:  # 不为0 说明接口返回错误，默认是session_id的问题
            self.signal.log_info.emit('session_id无效！')
        else:
            gl = gl_info['game_list']
            if len(app_dict) > 0 and len(gl) > 0:
                for g in gl:
                    app_id = app_dict.get(g['appid'])
                    appid = g.get('appid')
                    if not app_id or not appid:
                        continue
                    #   设置目标appid，没有则跳过
                    if self.target_appid:
                        if self.target_appid != appid:
                            continue
                    app_info = {'appid': appid, 'app_id': app_id}
                    thread_max.acquire()
                    gather = GatherThread(self.session_id, dates, app_info, self.houyi_api, mydb, thread_max, self.signal)
                    thread_pool.append(gather)
                    gather.start()
                    # break
            #   线程统一等待完成
            #   所有完成才可继续主进程
            for t in thread_pool:
                t.join()
            self.signal.log_info.emit('完成！')


#   自定义的信号  log信号
class LogSignal(QObject):
    log_info = pyqtSignal(str)


# 采集线程
class GatherThread(threading.Thread):
    def __init__(self, session_id: str, date_tuple: tuple, app_info: dict, api: object, db: object, thread_max: object, signal: QObject):
        super().__init__()
        self.session_id = session_id
        self.date_tuple = date_tuple
        self.app_info = app_info
        self.api = api
        self.db = db
        self.thread_max = thread_max
        self.signal = signal

    def run(self):
        #   数据采集
        mpg = MPGModel.MiniProgramGather(self.session_id, self.date_tuple, self.app_info, self.api, self.db, self.signal)
        mpg.runGatherer()
        self.thread_max.release()


#   程序
class MyApp(QtWidgets.QMainWindow, Ui):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.account_info = None
        self.browser = None
        self.threadPools = []
        Ui.__init__(self)
        self.setupUi(self)
        self._data_init()
        self.pushButton_run.clicked.connect(self._go_run)

    #   数据初始化
    def _data_init(self):
        end_day = QDate.currentDate()
        #   上月1号
        start_day = end_day.addDays(-3)
        self.DateEdit_end.setDate(end_day)
        self.DateEdit_start.setDate(start_day)
        self.DateEdit_end.setCalendarPopup(True)
        self.DateEdit_start.setCalendarPopup(True)

    #    输出信息
    def _log(self, text):
        self.plainTextEdit_log.appendPlainText(text)
        return True

    #   按钮触发
    def _go_run(self):
        start_day = self.DateEdit_start.date()
        end_day = self.DateEdit_end.date()
        appid = self.lineEdit_appid.text()
        session_id = self.lineEdit_session.text()
        api = HouyiApi()
        if start_day.daysTo(end_day) < 0 or start_day.daysTo(end_day) > 10:
            QMessageBox.warning(self, "日期错误", "间隔在0~10天内！", QMessageBox.Yes | QMessageBox.No)
        session_thread = MyAppThread(session_id, appid,
                                     (QDateTime(start_day, QTime(0, 0, 0)).toPyDateTime(),
                                      QDateTime(end_day, QTime(0, 0, 0)).toPyDateTime()), api)
        self.threadPools.append(session_thread)
        session_thread.signal.log_info.connect(self._log)
        session_thread.start()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
