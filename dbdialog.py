#-*- coding:utf-8 -*-
# 2016.09.16 17:25:56 中国标准时间
#Embedded file name: c:\Users\hp\Desktop\backup\dbdialog.py
from common import *
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import *
from PyQt4.QtCore import QTextCodec
import os
import json
import sys
import util
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:

    def _fromUtf8(s):
        return s


try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)


except AttributeError:

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


QTextCodec.setCodecForTr(QTextCodec.codecForName('utf8'))

class Ui_Table(QtGui.QTableWidget):

    def __init__(self, parent = None):
        super(Ui_Table, self).__init__(parent)
        self.shadow = QtGui.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(5)
        self.shadow.setOffset(15, 15)
        self.setGraphicsEffect(self.shadow)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowTitle(self.tr('\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93'))
        self.resize(700, 350)
        count = len(util.db_array())
        self.setColumnCount(4)
        self.setRowCount(count)
        strList = QtCore.QStringList()
        strList.append(self.tr('\xe6\x97\xa5\xe6\x9c\x9f'))
        strList.append(self.tr('\xe8\xb7\xaf\xe5\xbe\x84'))
        strList.append(self.tr('\xe6\x9f\xa5\xe7\x9c\x8b'))
        strList.append(self.tr('\xe5\x88\xa0\xe9\x99\xa4'))
        self.setHorizontalHeaderLabels(strList)
        try:
            with open(DATA_FILE, 'rb') as js:
                arr = json.load(js)
                for idx, d in enumerate(arr):
                    if os.path.exists(d.get('path')):
                        self.setRowData(idx, d)
                    else:
                        self.setRowData(idx, d.get('date'), '\xe6\x96\x87\xe4\xbb\xb6\xe5\xb7\xb2\xe8\xa2\xab\xe5\x88\xa0\xe9\x99\xa4')

        except IOError:
            print '\xe6\x96\x87\xe4\xbb\xb6\xe6\x89\x93\xe5\xbc\x80\xe5\xa4\xb1\xe8\xb4\xa5'

    def setRowData(self, row, info):
        dateLabel = QtGui.QLabel()
        dateLabel.setText(info['date'])
        self.setCellWidget(row, 0, dateLabel)
        self.setColumnWidth(0, 130)
        pathLabel = QtGui.QLabel()
        pathLabel.setText(_translate('Ui_Table', info['path'], None))
        self.setCellWidget(row, 1, pathLabel)
        self.setColumnWidth(1, 350)
        BtnStyle = 'QPushButton{border:1px solid lightgray;background:rgb(230,230,230)}QPushButton:hover{border-color:green;background:transparent}'
        analyseButton = QtGui.QPushButton()
        analyseButton.setText(_translate('Ui_Table', '\xe6\x9f\xa5\xe7\x9c\x8b\xe5\x88\x86\xe6\x9e\x90', None))
        analyseButton.setStyleSheet(BtnStyle)
        self.setCellWidget(row, 2, analyseButton)
        deleteButton = QtGui.QPushButton()
        deleteButton.setText(_translate('Ui_Table', '\xe5\x88\xa0\xe9\x99\xa4', None))
        deleteButton.setStyleSheet(BtnStyle)
        self.setCellWidget(row, 3, deleteButton)
        deleteButton.clicked.connect(lambda : self.remove_button(row))
        analyseButton.clicked.connect(lambda : self.on_button(info))

    def on_button(self, info):
        import analyse
        self.analyseWindow = analyse.AnalyseWindow(datas=info)
        self.analyseWindow.show()
        self.close()
        self.analyseWindow.set_preview(info)

    def remove_button(self, row):
        arr = util.db_array()
        with open(DATA_FILE, 'rb') as pkl:
            try:
                d = arr.pop(int(row))
                path = d.get('path')
                if os.path.exists(path):
                    try:
                        os.remove(d.get('path'))
                        os.remove(d.get('ir_path'))
                        os.remove(d.get('lines_path'))
                    except:
                        pass

                self.clearContents()
            except:
                pass

        util.direct_write_db(arr)
        arr = util.db_array()
        try:
            for idx, d in enumerate(arr):
                if os.path.exists(d.get('path')):
                    self.setRowData(idx, d)

        except:
            pass
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:25:57 中国标准时间
