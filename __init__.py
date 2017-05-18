#-*- coding:utf-8 -*-
import FileDialog
from export import InfoDialog, ExportWidget
import sys
import util
from PyQt4.Qt import *

util.init()

from PyQt4 import QtCore, QtGui

import container

class BtnTitlebar(QtGui.QPushButton):
    def __init__(self, *args, **kwargs):
        super(BtnTitlebar, self).__init__(*args, **kwargs)
        self.m_ishover = False
        
    def paintEvent(self, evt):
        super(BtnTitlebar, self).paintEvent(evt)
        
    def isHover(self):
        return self.m_ishover
        
    def enterEvent(self, evt):
        self.m_ishover = True
        
    def leaveEvent(self, evt):
        self.m_ishover = False

class BtnMinimize(BtnTitlebar):
    def __init__(self, *args, **kwargs):
        super(BtnMinimize, self).__init__(*args, **kwargs)
        
    def paintEvent(self, evt):
        super(BtnMinimize, self).paintEvent(evt)
        painter = QtGui.QPainter(self)
        if self.isDown() or self.isHover():
            painter.fillRect(QtCore.QRect(10,14,8,2), QtGui.QColor("#FFFFFF"))
        else:
            painter.fillRect(QtCore.QRect(10,14,8,2), QtGui.QColor("#282828"))

class BtnClose(BtnTitlebar):
    def __init__(self, *args, **kwargs):
        super(BtnClose, self).__init__(*args, **kwargs)
        
    def paintEvent(self, evt):
        super(BtnClose, self).paintEvent(evt)
        painter = QtGui.QPainter(self)
        if self.isDown() or self.isHover():
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor("#FFFFFF")), 1.42))
        else:
            painter.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor("#282828")), 1.42))
        
        painter.drawLine(15,10,20,15)
        painter.drawPoint(14,9)
        painter.drawPoint(21,15)
        
        painter.drawLine(20,10,15,15)
        painter.drawPoint(21,9)
        painter.drawPoint(14,15)

class Ui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Ui, self).__init__(parent)
        self.ui = container.MainWindow(self)
        self.setMouseTracking(True)
        self.ui.setupUi(self)
        self.showMax()

        self.m_DragPosition=self.pos()
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        
        # self.setWindowIcon(QtGui.QIcon("./sys/img/icon.ico"))

        font = QtGui.QFont()
        font.setFamily(util._fromUtf8("Microsoft YaHei"))

        qlbl_title = QtGui.QLabel(util._translate("MainWindow", "面区色部分析仪", None) , self)
        qlbl_title.setFont(font)
        GLOBAL_HEIGHT, GLOBAL_WIDTH = util.screen_size()
        TITLEBAR_HEIGHT = 30
        qlbl_title.setGeometry(0,0,GLOBAL_WIDTH,TITLEBAR_HEIGHT)
        qlbl_title.setStyleSheet("QLabel{background-color:#027FFE;"
                                        "border:none;"
                                        "color:#ffffff;"
                                        "font:bold;"
                                        "font-size:16px;"
                                        "qproperty-alignment:AlignCenter;}")
        
        self.qbtn_minimize=BtnMinimize(self)
        self.qbtn_minimize.setGeometry(GLOBAL_WIDTH*0.94,0,GLOBAL_WIDTH*0.05,TITLEBAR_HEIGHT)
        self.qbtn_minimize.setStyleSheet("QPushButton{background-color:#027FFE;"
                                                      "border:none;"
                                                      "font-size:12px;"
                                                      "font-family:Tahoma;}"
                                        "QPushButton:hover{background-color:#295e87;}"
                                        "QPushButton:pressed{background-color:#204a6a;}")
        
        self.qbtn_close=BtnClose(self)
        self.qbtn_close.setGeometry(GLOBAL_WIDTH*0.97,0,GLOBAL_WIDTH*0.05,TITLEBAR_HEIGHT)
        self.qbtn_close.setStyleSheet("QPushButton{background-color:#027FFE;"
                                                  "border:none;"
                                                  "font-size:12px;"
                                                  "font-family:Tahoma;}"
                                      "QPushButton:hover{background-color:#ea5e00;}"
                                      "QPushButton:pressed{background-color:#994005;}")

        self.qbtn_minimize.clicked.connect(self.btnClicked_minimize)
        self.qbtn_close.clicked.connect(self.btnClicked_close)


    def btnClicked_minimize(self):
        self.showMinimized()

    def btnClicked_close(self):
        self.close()

    def mouseDoubleClickEvent(self, e):
        pass
        # self.showMax()
        # self.emit(SIGNAL("showMax()"))

    @pyqtSlot()    
    def showMax(self):
        if not self.isMaximized():
            self.showMaximized()
        else:
            self.showNormal()

def _main():
    util.update_db()
    app = QtGui.QApplication(sys.argv)
    # if not util.verify():
    #     util.warn_dialog(text=u"注册码错误")
    #     return12
    
    # 启动界面
    w = QtGui.QWidget()
    w.setWindowFlags(Qt.FramelessWindowHint)
    label = QtGui.QLabel(w)
    start_pic = QtGui.QPixmap('./sys/img/start_pic.jpg')
    label.setScaledContents(True)
    screen_height, screen_width = util.screen_size()
    label.resize(screen_height/2, screen_width/3)
    label.setPixmap(start_pic)
    w.resize(screen_height/2, screen_width/3)
    w.show()

    window = None

    def callback(info):
        window = Ui()
        window.ui.load_info(info)
        window.show()

    def start():
        w.hide()
        w.setParent(None)
        window = Ui()
        window.show()
    QtCore.QTimer.singleShot(2000, start)
    sys.exit(app.exec_())
    
_main()
