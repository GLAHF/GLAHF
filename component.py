#-*- coding:utf-8 -*-
# 2016.09.16 17:25:28 中国标准时间
#Embedded file name: c:\Users\hp\Desktop\backup\component.py
from PyQt4 import QtGui
from PyQt4 import QtCore
import util

class DragLine(QtGui.QLabel):

    def __init__(self, title, parent, TYPE = 'V'):
        super(DragLine, self).__init__(title, parent)
        self.TYPE = TYPE
        self._xpos = self._ypos = 0
        self._info = None
        self.__callback = None
        self.__close_callback = None

    @property
    def callback(self):
        return self.__callback

    @callback.setter
    def callback(self, function):
        if callable(function):
            self.__callback = function

    @property
    def close_callback(self):
        return self.__close_callback

    @close_callback.setter
    def close_callback(self, function):
        if callable(function):
            self.__close_callback = function

    @property
    def info(self):
        return self._info

    @info.setter
    def info(self, value):
        self._info = value

    @property
    def xpos(self):
        return self._xpos

    @xpos.setter
    def xpos(self, value):
        self._xpos = value

    @property
    def ypos(self):
        return self._ypos

    @ypos.setter
    def ypos(self, value):
        self._ypos = value

    def mouseMoveEvent(self, e):
        if e.buttons() != QtCore.Qt.LeftButton:
            return
        mimeData = QtCore.QMimeData()
        pixmap = QtGui.QPixmap.grabWidget(self)
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
        painter.end()
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(e.pos() - self.rect().topLeft())
        dropAction = drag.start(QtCore.Qt.MoveAction)

    def mouseReleaseEvent(self, e):
        pass

    def closeEvent(self, e):
        self.__close_callback(self._info)

    def __str__(self):
        return self.info

    __repr__ = __str__


class LocationLabel(QtGui.QLabel):

    def __init__(self, *arg, **kw):
        super(LocationLabel, self).__init__(*arg, **kw)
        self.parent = None
        self._style = None

    def set_parent(self, window):
        if isinstance(window, QtGui.QMainWindow):
            self.parent = window

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        if value in ('x', 'y'):
            self._style = value

    def mousePressEvent(self, e):
        if e.buttons() == QtCore.Qt.LeftButton:
            height, width = util.screen_size()
            self.label = QtGui.QLabel()
            if self.style == 'y':
                self.label.setGeometry(QtCore.QRect(0, self.y(), width, 3))
            else:
                self.label.setGeometry(QtCore.QRect(self.x(), 0, 3, height))
            self.label.setStyleSheet('background-color:blue;')
            self.parent.layout().addWidget(self.label)

    def mouseReleaseEvent(self, e):
        self.label.close()
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:25:28 中国标准时间
