'''
Author: Demoon
Date: 2021-03-02 09:55:45
LastEditTime: 2021-03-12 17:51:56
LastEditors: Please set LastEditors
Description: 运营 sqlite3 的本地存储系统
FilePath: \\MiniProgramGather\\MyDB.py
'''
import sqlite3
import logging
import utils as myTools


class MyDB:
    def __init__(self, db_file='mpg.sqlite3.db'):
        file = myTools.filePath(db_file)
        self.conn = sqlite3.connect(file, check_same_thread=False)

    #   运行sql语句 无返回类
    def runSql(self, sql):
        # 获取游标对象用来操作数据库
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()
        cursor.close()
        return True

    #   查询多条数据，返回list[tuple]
    def findAll(self, sql):
        # 获取游标对象用来操作数据库
        cursor = self.conn.cursor()
        cursor.execute(sql)
        query_list = cursor.fetchall()
        cursor.close()
        return query_list

    #   查询多条数据，返回list[tuple]
    def find(self, sql):
        # 获取游标对象用来操作数据库
        cursor = self.conn.cursor()
        cursor.execute(sql)
        query = cursor.fetchone()
        cursor.close()
        return query

    #   保存数据 data 为元组list
    def save(self, tbl_name: str, data: list):
        res = True
        if len(data) > 0:
            try:
                #   先获取列名
                cursor = self.conn.cursor()
                cursor.execute("PRAGMA table_info({0})".format(tbl_name))
                querys = cursor.fetchall()
                fields = []
                for field in querys:
                    fields.append(field[1])
                fields_str = str(tuple(fields[1:]))
                data_str = ','.join(list(map(lambda x: str(x), data)))
                #   构建sql
                insert_sql = '''INSERT INTO {0} {1} VALUES {2};'''.format(tbl_name, fields_str, data_str)
                cursor.execute(insert_sql)
                self.conn.commit()
            except Exception as e:
                logging.error(e)
                res = False
        return res

    #   关闭数据库链接
    def close(self):
        self.conn.close()
        return True

# if __name__ == '__main__':
#     db = MyDB()
#     # db.save('channel_group', [('1','sss', '111'),('1','sss', '111')])
#     res = db.findAll('SELECT * FROM channel_group WHERE id!=100')
#     print(res)
