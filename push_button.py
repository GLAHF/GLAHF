#-*- coding:utf-8 -*-
# 2016.09.16 17:26:20 中国标准时间
#Embedded file name: c:\Users\hp\Desktop\backup\push_button.py
from PyQt4.QtGui import *
from PyQt4.Qt import *

class PushButton(QPushButton):

    def __init__(self, parent = None):
        super(PushButton, self).__init__(parent)
        self.status = 0

    def loadPixmap(self, pic_name):
        self.pixmap = QPixmap(pic_name)
        self.btn_width = self.pixmap.width() / 4
        self.btn_height = self.pixmap.height()
        self.setFixedSize(self.btn_width, self.btn_height)

    def enterEvent(self, event):
        self.status = 1
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_press = True
            self.status = 2
            self.update()

    def mouseReleaseEvent(self, event):
        if self.mouse_press:
            self.mouse_press = False
            self.status = 3
            self.update()
            self.clicked.emit(True)

    def leaveEvent(self, event):
        self.status = 0
        self.update()

    def paintEvent(self, event):
        self.painter = QPainter()
        self.painter.begin(self)
        self.painter.drawPixmap(self.rect(), self.pixmap.copy(self.btn_width * self.status, 0, self.btn_width, self.btn_height))
        self.painter.end()
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:26:20 中国标准时间
