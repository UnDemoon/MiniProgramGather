if __name__ == '__main__':
    from PyInstaller.__main__ import run
    opts = ['main.py',
            'home.py',
            'MyBrowser.py',
            'utils.py',
            'GameweixinGather.py',
            'HouyiApi.py',
            'MyDb.py',
            '-F',
            '-w',
            # '-D',
            '--icon=icon.ico']
    run(opts)
