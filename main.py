'''
@Description:

@Version: 1.0
@Autor: Demoon
@Date: 1970-01-01 08:00:00
LastEditors: Please set LastEditors
LastEditTime: 2021-03-27 15:01:06
'''
#  基础模块
import sys
import time
import datetime
import logging
import threading
#   引入浏览器线程类#   引入api类
from HouyiApi import HouyiApi as Api
from MyDB import MyDB
#   工具集
import utils as myTools
#   引入采集类
import MiniProgramGather as MPGModel
from MiniProgramGather import MiniProgramGather as MPG

logging.basicConfig(filename='./_debug-log.log', level=logging.ERROR,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


#   分装fuc方便进程调用
def oneProcess(proinfo: tuple, houyiApi: object):
    info_id, session, recent_days = proinfo
    #   线程限制信号量
    thread_max = threading.BoundedSemaphore(8)
    #   根据日期构建采集时间数据
    date_today = datetime.date.today()
    end_datetime = datetime.datetime(date_today.year, date_today.month, date_today.day, 0, 0, 0)
    start_datetime = end_datetime - datetime.timedelta(days=int(recent_days))
    dates = (start_datetime, end_datetime)
    #   线程池
    thread_pool = []
    #   本地db
    mydb = MyDB()
    #   处理appid与app_id数据
    app_infos = houyiApi.pageData('list_apps', None)
    app_list = app_infos.get('Result', {}).get('List', [])
    app_dict = {}
    for app in app_list:
        app_dict[app['appid']] = app['id']
    #   抓取数据
    gl_info = MPGModel.listGames(session)
    if gl_info['errcode'] != 0:     # 不为0 说明接口返回错误，默认是session的问题
        logging.info('END - not find game list')
        houyiApi.up('notifyMpgConf', {'run_res': 0, 'id': info_id})
    else:
        gl = gl_info['game_list']
        if len(app_dict) > 0 and len(gl) > 0:
            for g in gl:
                app_id = app_dict.get(g['appid'])
                appid = g.get('appid')
                if not app_id or not appid:
                    continue
                app_info = {'appid': appid, 'app_id': app_id}
                thread_max.acquire()
                gather = GatherThread(session, dates, app_info, houyiApi, mydb, thread_max)
                thread_pool.append(gather)
                gather.start()
                # break
        #   线程统一等待完成
        #   所有完成才可继续主进程
        for t in thread_pool:
            t.join()
        houyiApi.up('notifyMpgConf', {'run_res': 1, 'id': info_id})


# 采集线程
class GatherThread(threading.Thread):
    def __init__(self, session_id: str, date_tuple: tuple, app_info: dict, api: object, db: object, thread_max: object):
        super().__init__()
        self.session_id = session_id
        self.date_tuple = date_tuple
        self.app_info = app_info
        self.api = api
        self.db = db
        self.thread_max = thread_max

    def run(self):
        #   数据采集
        mpg = MPG(self.session_id, self.date_tuple, self.app_info, self.api, self.db)
        mpg.runGatherer()
        self.thread_max.release()


if __name__ == '__main__':
    #   运行类型    区分手动和自动运行 1自动 2手动
    global RUN_TYPE
    # 登录界面的url
    try:
        RUN_TYPE = int(sys.argv[1])
    except Exception:
        RUN_TYPE = 1
    #   后台api
    houyiApi = Api()
    # #   测试
    # info = (4338, 'BgAAt3bl2gUxf97laJ8Nxpzbr75fBjZG5xZDnZqLm4ZgWDo', 3)
    # oneProcess(info, houyiApi)
    #   获取后台配置
    confs = houyiApi.up('getMpgConf', '')
    for conf in confs.get('Result', {}).get('session_conf', []):
        if RUN_TYPE == 2 and 1 != int(conf.get('runing', 0)):   # 手动运行
            continue
        conf_id = conf.get('id')
        session = conf.get('session_id')
        recent_days = conf.get('recent_days')
        if session and recent_days:
            info = (int(conf_id), session, int(recent_days))
            oneProcess(info, houyiApi)
        else:
            logging.error('后台配置异常，conf:{0}'.format(str(conf)))
    print("Run End!\n")
