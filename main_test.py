#!/usr/bin/env python3
# encoding: utf-8
"""
@Author  : Demoon
@Contact : liu_zun@foxmail.com
@Software: garner
@Site    : 
@File    : main_test.py.py
@Time    : 2021/5/21 14:13
@Desc    : 用于测试shell脚本的调用
"""
import time

if __name__ == '__main__':
    max_loop = 10000
    while max_loop > 0:
        max_loop -= 1
        time.sleep(3)
        print(max_loop)
