'''
Author: your name
Date: 2021-02-23 09:59:37
LastEditTime: 2021-03-12 10:42:20
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: /MiniProgramGather/pyinstall.py
'''
if __name__ == '__main__':
    from PyInstaller.__main__ import run
    opts = ['main.py',
            'utils.py',
            'MiniProgramGather.py',
            'HouyiApi.py',
            'MyDb.py',
            '-F',
            '-w',
            # '-D',
            '--icon=Dig Dug.ico']
    run(opts)
