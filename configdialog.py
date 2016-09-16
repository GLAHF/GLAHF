#-*- coding:utf-8 -*-
# 2016.09.16 17:25:37 中国标准时间
#Embedded file name: c:\Users\hp\Desktop\backup\configdialog.py
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from glahf import glahf
from push_button import PushButton
from common import *
import clb
import json
import util
try:
    import cPickle as pickle
except ImportError:
    import pickle

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


class Ui_Dialog(QtGui.QDialog):

    def __init__(self, parent = None):
        super(Ui_Dialog, self).__init__(parent)
        self.config = util.load_config()
        self.setupUi(self)
        self.retranslateUi(self)
        self.mouse_press = False
        self.is_change = False
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.initTitle()

    def initTitle(self):
        self.title_label = QLabel(self)
        self.title_icon_label = QLabel(self)
        self.close_button = PushButton(self)
        self.close_button.loadPixmap('./sys/img/close_button.png')
        self.title_label.setFixedHeight(30)
        self.title_layout = QHBoxLayout()
        self.title_layout.addWidget(self.title_icon_label, 0, Qt.AlignVCenter)
        self.title_layout.addWidget(self.title_label, 0, Qt.AlignVCenter)
        self.title_layout.addStretch()
        self.title_layout.addWidget(self.close_button, 0, Qt.AlignTop)
        self.title_layout.setSpacing(5)
        self.title_layout.setContentsMargins(10, 0, 5, 0)
        self.initTitle
        self.title_label.setStyleSheet('color:white')
        self.connect(self.close_button, SIGNAL('clicked()'), SLOT('close()'))

    def paintEvent(self, event):
        if ~self.is_change:
            pass
        self.skin_name = QString(BG_IMG)
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), QPixmap(self.skin_name))
        painter2 = QPainter(self)
        linear2 = QLinearGradient(QPointF(self.rect().topLeft()), QPointF(self.rect().bottomLeft()))
        linear2.setColorAt(0, Qt.white)
        linear2.setColorAt(0.5, Qt.white)
        linear2.setColorAt(1, Qt.white)
        painter2.setPen(Qt.white)
        painter2.setBrush(linear2)
        painter2.drawRect(QRect(0, 30, self.width(), self.height() - 30))
        painter3 = QPainter(self)
        painter3.setPen(Qt.gray)
        painter3.drawPolyline(QPointF(0, 30), QPointF(0, self.height() - 1), QPointF(self.width() - 1, self.height() - 1), QPointF(self.width() - 1, 30))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_press = True
        self.move_point = event.globalPos() - self.pos()

    def mouseReleaseEvent(self, event):
        self.mouse_press = False

    def mouseMoveEvent(self, event):
        if self.mouse_press:
            self.move_pos = event.globalPos()
            self.move(self.move_pos - self.move_point)

    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8('Dialog'))
        Dialog.resize(400, 300)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(30, 250, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel | QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8('buttonBox'))
        self.savedirLabel = QtGui.QLabel(Dialog)
        self.savedirLabel.setGeometry(QtCore.QRect(10, 40, 71, 16))
        self.savedirLabel.setObjectName(_fromUtf8('savedirLabel'))
        self.savedir = QtGui.QLineEdit(Dialog)
        self.savedir.setGeometry(QtCore.QRect(90, 40, 221, 20))
        self.savedir.setObjectName(_fromUtf8('savedir'))
        self.choose_savedir = QtGui.QPushButton(Dialog)
        self.choose_savedir.setGeometry(QtCore.QRect(320, 40, 75, 23))
        self.choose_savedir.setObjectName(_fromUtf8('choose_savedir'))
        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8('accepted()')), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8('rejected()')), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        self.connect(self.choose_savedir, QtCore.SIGNAL('clicked()'), self.choose_dir)
        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.ok)
        self.connect(self.buttonBox, QtCore.SIGNAL('rejected()'), self.cancel)
        self.refresh_value()

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate('Dialog', '\xe8\xae\xbe\xe7\xbd\xae', None))
        self.savedirLabel.setText(_translate('Dialog', '\xe5\x9b\xbe\xe7\x89\x87\xe5\xad\x98\xe6\x94\xbe\xe8\xb7\xaf\xe5\xbe\x84', None))
        self.choose_savedir.setText(_translate('Dialog', '\xe9\x80\x89\xe6\x8b\xa9\xe8\xb7\xaf\xe5\xbe\x84', None))

    def ok(self):
        if str(self.savedir.text()):
            self.config['savedir'] = str(self.savedir.text())
            with open(SETTING_FILE, 'w') as settings:
                json.dump(self.config, settings)
            with open(SETTING_FILE) as jsonfile:
                self.config = json.load(jsonfile)

    def cancel(self):
        self.refresh_value()

    def choose_dir(self):
        dirname = unicode(self.show_file_dialog())
        self.savedir.setText(dirname)

    def show_file_dialog(self):
        savedir = QtGui.QFileDialog.getExistingDirectory(self, u'\u9009\u62e9\u56fe\u7247\u4fdd\u5b58\u76ee\u5f55', './')
        return savedir

    def hori_count_change(self):
        value = self.hori_count.value()
        self.hori_count_lcd.setText(str(value))

    def vert_count_change(self):
        value = self.vert_count.value()
        self.vert_count_lcd.setText(str(value))

    def refresh_value(self):
        self.savedir.setText(self.config['savedir'])
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:25:38 中国标准时间
