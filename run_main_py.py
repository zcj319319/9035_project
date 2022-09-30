#!/usr/bin/env python 
# -*- coding: utf-8 -*-
'''
Time    : 2022/9/29 15:14
Author  : zhuchunjin
Email   : chunjin.zhu@taurentech.net
File    : run_main_py.py
Software: PyCharm
'''

import sys

from PyQt5 import QtWidgets

from run_project.loadPanel import LoadingPanel

app = QtWidgets.QApplication(sys.argv)

if __name__ == '__main__':
    try:
        ex = LoadingPanel()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        raise e