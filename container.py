#-*- coding:utf-8 -*-
# 2016.09.16 17:25:45 ÖÐ¹ú±ê×¼Ê±¼ä
#Embedded file name: c:\Users\hp\Desktop\backup\container.py
from cap import Capture
from common import *
from glahf import glahf, faceutil
from facepp import facepp
from export import InfoDialog
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
import analyse
import configdialog
import cv2
import json
import dbdialog
import logging
import net
import threading
import os
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


class MainWindow(QtGui.QWidget):
    loadingSig = QtCore.pyqtSignal()

    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.parent = parent
        self.loadingSig.connect(self.set_img)
        self.linesArr = None
        self.FSCALE = None
        self.LSCALE = None
        self.RSCALE = None
        self.FRONTAL_PATH = None
        self.LEFT_PATH = None
        self.RIGHT_PATH = None
        self.LEFT_IR_PATH = None
        self.FRONTAL_IR_PATH = None
        self.RIGHT_IR_PATH = None
        self.config = util.load_config()
        self.scale = None
        self.stretch_factor = None
        self.info = None
        self.last_path = None
        self.from_db = False
        self.db_datas = {}
        self.datas = None
        self.capture = None

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8('MainWindow'))
        GLOBAL_HEIGHT, GLOBAL_WIDTH = util.screen_size()
        self.resize(GLOBAL_WIDTH, GLOBAL_HEIGHT)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8('Microsoft YaHei'))
        self.movie = QtGui.QMovie(LOADING_GIF, QtCore.QByteArray(), self)
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.movie.setSpeed(100)
        self.settingsdialog = configdialog.Ui_Dialog()
        png = QtGui.QPixmap(self)
        png.load(BG_IMG)
        palette = QtGui.QPalette(self)
        palette.setBrush(self.backgroundRole(), QtGui.QBrush(png))
        MainWindow.setPalette(palette)
        MainWindow.setAutoFillBackground(True)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8('centralwidget'))
        font.setPointSize(12)
        self.rightBGLabel = QtGui.QLabel(self.centralwidget)
        self.rightBGLabel.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.76, 0, GLOBAL_WIDTH * 0.3, GLOBAL_HEIGHT))
        self.rightBGLabel.setStyleSheet('QLabel{background:rgb(13, 25, 38)}')
        self.analyse_btn = QtGui.QPushButton(self.centralwidget)
        self.analyse_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.76, GLOBAL_HEIGHT * 0.1, GLOBAL_WIDTH * 0.27, GLOBAL_HEIGHT * 0.17))
        self.analyse_btn.setObjectName(_fromUtf8('analyse_btn'))
        self.analyse_btn.setFont(font)
        self.db_btn = QtGui.QPushButton(self.centralwidget)
        self.db_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.76, GLOBAL_HEIGHT * 0.3, GLOBAL_WIDTH * 0.27, GLOBAL_HEIGHT * 0.17))
        self.db_btn.setObjectName(_fromUtf8('db_btn'))
        self.db_btn.setFont(font)
        self.setting_btn = QtGui.QPushButton(self.centralwidget)
        self.setting_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.76, GLOBAL_HEIGHT * 0.5, GLOBAL_WIDTH * 0.27, GLOBAL_HEIGHT * 0.17))
        self.setting_btn.setObjectName(_fromUtf8('setting_btn'))
        self.setting_btn.setFont(font)
        self.quit_btn = QtGui.QPushButton(self.centralwidget)
        self.quit_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.76, GLOBAL_HEIGHT * 0.7, GLOBAL_WIDTH * 0.27, GLOBAL_HEIGHT * 0.17))
        self.quit_btn.setObjectName(_fromUtf8('quit_btn'))
        self.quit_btn.setFont(font)
        MainWindow.setCentralWidget(self.centralwidget)
        self.left_preview = QtGui.QLabel(self.centralwidget)
        self.left_preview.setScaledContents(True)
        self.left_preview.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.05, GLOBAL_HEIGHT * 0.07, GLOBAL_WIDTH * 0.18, GLOBAL_HEIGHT * 0.35))
        self.left_preview.setObjectName(_fromUtf8('left_preview'))
        self.frontal_preview = QtGui.QLabel(self.centralwidget)
        self.frontal_preview.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.3, GLOBAL_HEIGHT * 0.07, GLOBAL_WIDTH * 0.18, GLOBAL_HEIGHT * 0.35))
        self.frontal_preview.setObjectName(_fromUtf8('frontal_preview'))
        self.frontal_preview.setScaledContents(True)
        self.frontal_line = QtGui.QLabel(self.centralwidget)
        self.frontal_line.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.39, GLOBAL_HEIGHT * 0.07, GLOBAL_WIDTH * 0.002, GLOBAL_HEIGHT * 0.35))
        self.frontal_line.setObjectName(_fromUtf8('frontal_line'))
        self.frontal_line.setStyleSheet('QLabel{ background-color:red}')
        self.frontal_line.hide()
        self.right_preview = QtGui.QLabel(self.centralwidget)
        self.right_preview.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.55, GLOBAL_HEIGHT * 0.07, GLOBAL_WIDTH * 0.18, GLOBAL_HEIGHT * 0.35))
        self.right_preview.setObjectName(_fromUtf8('right_preview'))
        self.right_preview.setScaledContents(True)
        self.left_ir_preview = QtGui.QLabel(self.centralwidget)
        self.left_ir_preview.setScaledContents(True)
        self.left_ir_preview.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.05, GLOBAL_HEIGHT * 0.5, GLOBAL_WIDTH * 0.18, GLOBAL_HEIGHT * 0.35))
        self.left_ir_preview.setObjectName(_fromUtf8('left_ir_preview'))
        self.frontal_ir_preview = QtGui.QLabel(self.centralwidget)
        self.frontal_ir_preview.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.3, GLOBAL_HEIGHT * 0.5, GLOBAL_WIDTH * 0.18, GLOBAL_HEIGHT * 0.35))
        self.frontal_ir_preview.setObjectName(_fromUtf8('frontal_ir_preview'))
        self.frontal_ir_preview.setScaledContents(True)
        self.right_ir_preview = QtGui.QLabel(self.centralwidget)
        self.right_ir_preview.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.55, GLOBAL_HEIGHT * 0.5, GLOBAL_WIDTH * 0.18, GLOBAL_HEIGHT * 0.35))
        self.right_ir_preview.setObjectName(_fromUtf8('rightLIRabel'))
        self.right_ir_preview.setScaledContents(True)
        self.preview_height = GLOBAL_HEIGHT * 0.35
        self.focus_preview = None
        self.choose_left = QtGui.QPushButton(self.centralwidget)
        self.choose_left.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.02, GLOBAL_HEIGHT * 0.43, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.1))
        self.choose_left.setObjectName(_fromUtf8('choose_left'))
        self.choose_left_ir = QtGui.QPushButton(self.centralwidget)
        self.choose_left_ir.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.43, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.1))
        self.choose_left_ir.setObjectName(_fromUtf8('choose_left_ir'))
        self.choose_left_cap = QtGui.QPushButton(self.centralwidget)
        self.choose_left_cap.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.18, GLOBAL_HEIGHT * 0.43, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.1))
        self.choose_left_cap.setObjectName(_fromUtf8('choose_left_cap'))
        self.choose_frontal = QtGui.QPushButton(self.centralwidget)
        self.choose_frontal.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.27, GLOBAL_HEIGHT * 0.43, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.1))
        self.choose_frontal.setObjectName(_fromUtf8('choose_frontal'))
        self.choose_frontal_ir = QtGui.QPushButton(self.centralwidget)
        self.choose_frontal_ir.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.35, GLOBAL_HEIGHT * 0.43, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.1))
        self.choose_frontal_ir.setObjectName(_fromUtf8('choose_frontal_ir'))
        self.choose_frontal_cap = QtGui.QPushButton(self.centralwidget)
        self.choose_frontal_cap.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.43, GLOBAL_HEIGHT * 0.43, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.1))
        self.choose_frontal_cap.setObjectName(_fromUtf8('choose_frontal_cap'))
        self.choose_right = QtGui.QPushButton(self.centralwidget)
        self.choose_right.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.52, GLOBAL_HEIGHT * 0.43, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.1))
        self.choose_right.setObjectName(_fromUtf8('choose_right'))
        self.choose_right_ir = QtGui.QPushButton(self.centralwidget)
        self.choose_right_ir.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.6, GLOBAL_HEIGHT * 0.43, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.1))
        self.choose_right_ir.setObjectName(_fromUtf8('choose_right_ir'))
        self.choose_right_cap = QtGui.QPushButton(self.centralwidget)
        self.choose_right_cap.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.68, GLOBAL_HEIGHT * 0.43, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.1))
        self.choose_right_cap.setObjectName(_fromUtf8('choose_right_cap'))
        self.left_scale = QtGui.QSlider(MainWindow)
        self.left_scale.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.08, GLOBAL_HEIGHT * 0.89, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.05))
        self.left_scale.setOrientation(QtCore.Qt.Horizontal)
        self.left_scale.setObjectName(_fromUtf8('left_scale'))
        self.left_scale.setRange(0, 3)
        self.left_scale_text = QtGui.QLabel(MainWindow)
        self.left_scale_text.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.02, GLOBAL_HEIGHT * 0.9, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.02))
        self.left_scale_text.setObjectName(_fromUtf8('left_scale_text'))
        self.left_lcd = QtGui.QLCDNumber(MainWindow)
        self.left_lcd.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.19, GLOBAL_HEIGHT * 0.895, GLOBAL_WIDTH * 0.05, 23))
        self.left_lcd.setObjectName(_fromUtf8('left_lcd'))
        self.right_scale = QtGui.QSlider(MainWindow)
        self.right_scale.setRange(0, 3)
        self.right_scale.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.59, GLOBAL_HEIGHT * 0.89, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.05))
        self.right_scale.setOrientation(QtCore.Qt.Horizontal)
        self.right_scale.setObjectName(_fromUtf8('right_scale'))
        self.right_scale_text = QtGui.QLabel(MainWindow)
        self.right_scale_text.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.53, GLOBAL_HEIGHT * 0.9, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.02))
        self.right_scale_text.setObjectName(_fromUtf8('right_scale_text'))
        self.right_lcd = QtGui.QLCDNumber(MainWindow)
        self.right_lcd.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.7, GLOBAL_HEIGHT * 0.895, GLOBAL_WIDTH * 0.05, 23))
        self.right_lcd.setObjectName(_fromUtf8('right_lcd'))
        self.frontal_scale = QtGui.QSlider(MainWindow)
        self.frontal_scale.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.34, GLOBAL_HEIGHT * 0.89, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.05))
        self.frontal_scale.setOrientation(QtCore.Qt.Horizontal)
        self.frontal_scale.setObjectName(_fromUtf8('left_scale'))
        self.frontal_scale.setRange(0, 3)
        self.frontal_scale_text = QtGui.QLabel(MainWindow)
        self.frontal_scale_text.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.28, GLOBAL_HEIGHT * 0.9, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.02))
        self.frontal_scale_text.setObjectName(_fromUtf8('right_scale_text'))
        self.frontal_lcd = QtGui.QLCDNumber(MainWindow)
        self.frontal_lcd.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.45, GLOBAL_HEIGHT * 0.895, GLOBAL_WIDTH * 0.05, 23))
        self.frontal_lcd.setObjectName(_fromUtf8('right_lcd'))
        font.setPointSize(10)
        self.frontal_scale_text.setFont(font)
        self.left_scale_text.setFont(font)
        self.right_scale_text.setFont(font)
        self.choose_left.setFont(font)
        self.choose_frontal.setFont(font)
        self.choose_right.setFont(font)
        self.choose_left_ir.setFont(font)
        self.choose_frontal_ir.setFont(font)
        self.choose_right_ir.setFont(font)
        self.choose_left_cap.setFont(font)
        self.choose_frontal_cap.setFont(font)
        self.choose_right_cap.setFont(font)
        self.left_lcd.display(1.0)
        self.frontal_lcd.display(1.0)
        self.right_lcd.display(1.0)
        self.switch_cam_btn = QtGui.QPushButton(self.centralwidget)
        self.switch_cam_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.78, GLOBAL_HEIGHT * 0.91, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.08))
        self.switch_cam_btn.setObjectName(_fromUtf8('switch_cam_btn'))
        font.setPointSize(20)
        self.switch_cam_btn.setFont(font)
        self.switch_cam_btn.setStyleSheet('QPushButton{background-color:#333333;border:none;color:#ffffff;}QPushButton:hover{background-color:rgb(238,64,0);}')
        self.switch_cam_btn.setText(_translate('MainWindow', '\xe5\x88\x87\xe6\x8d\xa2\xe6\x91\x84\xe5\x83\x8f\xe5\xa4\xb4', None))
        self.switch_cam_btn.setCursor(Qt.PointingHandCursor)
        self.switch_cam_btn.clicked.connect(self.switch_cam)
        self.set_info_btn = QtGui.QPushButton(self.centralwidget)
        self.set_info_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.9, GLOBAL_HEIGHT * 0.91, GLOBAL_WIDTH * 0.1, GLOBAL_HEIGHT * 0.08))
        self.set_info_btn.setObjectName(_fromUtf8('set_info_btn'))
        font.setPointSize(20)
        self.set_info_btn.setFont(font)
        self.set_info_btn.setStyleSheet('QPushButton{background-color:#333333;border:none;color:#ffffff;}QPushButton:hover{background-color:rgb(238,64,0);}')
        self.set_info_btn.setText(_translate('MainWindow', '\xe8\xbe\x93\xe5\x85\xa5\xe4\xbf\xa1\xe6\x81\xaf', None))
        self.set_info_btn.setCursor(Qt.PointingHandCursor)
        self.set_info_btn.clicked.connect(self.set_info)
        self.connect(self.frontal_scale, QtCore.SIGNAL('valueChanged(int)'), lambda : self.slider_change('frontal'))
        self.connect(self.left_scale, QtCore.SIGNAL('valueChanged(int)'), lambda : self.slider_change('left'))
        self.connect(self.right_scale, QtCore.SIGNAL('valueChanged(int)'), lambda : self.slider_change('right'))
        self.connect(self.choose_left, QtCore.SIGNAL('clicked()'), lambda : self.get_face('left', 'normal'))
        self.connect(self.choose_frontal, QtCore.SIGNAL('clicked()'), lambda : self.get_face('frontal', 'normal'))
        self.connect(self.choose_right, QtCore.SIGNAL('clicked()'), lambda : self.get_face('right', 'normal'))
        self.connect(self.choose_left_ir, QtCore.SIGNAL('clicked()'), lambda : self.get_face('left', 'ir'))
        self.connect(self.choose_frontal_ir, QtCore.SIGNAL('clicked()'), lambda : self.get_face('frontal', 'ir'))
        self.connect(self.choose_right_ir, QtCore.SIGNAL('clicked()'), lambda : self.get_face('right', 'ir'))
        self.connect(self.analyse_btn, QtCore.SIGNAL('clicked()'), self.openAnalyse)
        self.connect(self.db_btn, QtCore.SIGNAL('clicked()'), self.select_entry)
        self.connect(self.setting_btn, QtCore.SIGNAL('clicked()'), self.settingsdialog.show)
        self.quit_btn.clicked.connect(self.quit)
        self.choose_left_cap.clicked.connect(self.toggle_cam('left'))
        self.choose_frontal_cap.clicked.connect(self.toggle_cam('frontal'))
        self.choose_right_cap.clicked.connect(self.toggle_cam('right'))
        util.clickable(self.left_preview).connect(lambda : self.preview_on_click(self.left_preview))
        util.clickable(self.frontal_preview).connect(lambda : self.preview_on_click(self.frontal_preview))
        util.clickable(self.right_preview).connect(lambda : self.preview_on_click(self.right_preview))
        util.clickable(self.left_ir_preview).connect(lambda : self.preview_on_click(self.left_ir_preview))
        util.clickable(self.frontal_ir_preview).connect(lambda : self.preview_on_click(self.frontal_ir_preview))
        util.clickable(self.right_ir_preview).connect(lambda : self.preview_on_click(self.right_ir_preview))
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate('MainWindow', '\xe4\xba\xba\xe8\x84\xb8\xe7\x81\xb0\xe5\xba\xa6\xe5\x80\xbc\xe5\xae\x9a\xe4\xbd\x8d', None))
        self.frontal_preview.setText(_translate('MainWindow', '\xe6\xad\xa3\xe8\x84\xb8', None))
        self.frontal_scale_text.setText(_translate('Dialog', '\xe7\xbc\xa9\xe6\x94\xbe\xe6\xaf\x94\xe4\xbe\x8b', None))
        self.choose_left.setText(_translate('MainWindow', '\xe9\x80\x89\xe6\x8b\xa9\xe5\xb7\xa6\xe8\x84\xb8', None))
        self.choose_frontal.setText(_translate('MainWindow', '\xe9\x80\x89\xe6\x8b\xa9\xe6\xad\xa3\xe8\x84\xb8', None))
        self.choose_right.setText(_translate('MainWindow', '\xe9\x80\x89\xe6\x8b\xa9\xe5\x8f\xb3\xe8\x84\xb8', None))
        self.choose_left_ir.setText(_translate('MainWindow', '\xe7\xba\xa2\xe5\xa4\x96\xe5\x9b\xbe\xe5\x83\x8f', None))
        self.choose_frontal_ir.setText(_translate('MainWindow', '\xe7\xba\xa2\xe5\xa4\x96\xe5\x9b\xbe\xe5\x83\x8f', None))
        self.choose_right_ir.setText(_translate('MainWindow', '\xe7\xba\xa2\xe5\xa4\x96\xe5\x9b\xbe\xe5\x83\x8f', None))
        self.choose_left_cap.setText(_translate('MainWindow', '\xe6\x89\x93\xe5\xbc\x80\xe6\x91\x84\xe5\x83\x8f\xe5\xa4\xb4', None))
        self.choose_frontal_cap.setText(_translate('MainWindow', '\xe6\x89\x93\xe5\xbc\x80\xe6\x91\x84\xe5\x83\x8f\xe5\xa4\xb4', None))
        self.choose_right_cap.setText(_translate('MainWindow', '\xe6\x89\x93\xe5\xbc\x80\xe6\x91\x84\xe5\x83\x8f\xe5\xa4\xb4', None))
        self.left_scale_text.setText(_translate('MainWindow', '\xe5\xb7\xa6\xe8\x84\xb8\xe7\xbc\xa9\xe6\x94\xbe\xe6\xaf\x94\xe4\xbe\x8b', None))
        self.right_scale_text.setText(_translate('MainWindow', '\xe5\x8f\xb3\xe8\x84\xb8\xe7\xbc\xa9\xe6\x94\xbe\xe6\xaf\x94\xe4\xbe\x8b', None))
        self.frontal_scale_text.setText(_translate('MainWindow', '\xe6\xad\xa3\xe8\x84\xb8\xe7\xbc\xa9\xe6\x94\xbe\xe6\xaf\x94\xe4\xbe\x8b', None))
        pixmap = QtGui.QPixmap(SEARCH_IMG)
        for btn in (self.choose_left, self.choose_frontal, self.choose_right):
            btn.setIcon(QtGui.QIcon(pixmap))
            btn.setIconSize(pixmap.size())
            btn.setFixedSize(100, 35)
            btn.setStyleSheet('QPushButton{border-radius:5px;background:rgb(110, 190, 10);color:white}QPushButton:hover{background:rgb(140, 220, 35)}')

        for btn in (self.choose_left_ir, self.choose_frontal_ir, self.choose_right_ir):
            btn.setIcon(QtGui.QIcon(pixmap))
            btn.setIconSize(pixmap.size())
            btn.setFixedSize(100, 35)
            btn.setStyleSheet('QPushButton{border-radius:5px;background:rgb(255, 48, 48);color:white}QPushButton:hover{background:rgb(205, 38, 38)}')

        for btn in (self.choose_left_cap, self.choose_frontal_cap, self.choose_right_cap):
            btn.setIconSize(pixmap.size())
            btn.setFixedSize(100, 35)
            btn.setStyleSheet('QPushButton{border-radius:5px;background:#EE4000;color:white}QPushButton:hover{background:#EE4000}')

        self.left_preview.setPixmap(QtGui.QPixmap(INIT_LEFTIMG))
        self.frontal_preview.setPixmap(QtGui.QPixmap(INIT_FRONTALIMG))
        self.right_preview.setPixmap(QtGui.QPixmap(INIT_RIGHTIMG))
        self.left_ir_preview.setPixmap(QtGui.QPixmap(INIT_LEFTIMG))
        self.frontal_ir_preview.setPixmap(QtGui.QPixmap(INIT_FRONTALIMG))
        self.right_ir_preview.setPixmap(QtGui.QPixmap(INIT_RIGHTIMG))
        self.analyse_btn.setStyleSheet("QPushButton{border-image:url('sys/img/analyse_dark.png')}QPushButton:hover{border-image:url('sys/img/analyse_light.png')}")
        self.db_btn.setStyleSheet("QPushButton{border-image:url('sys/img/db_dark.png')}QPushButton:hover{border-image:url('sys/img/db_light.png')}")
        self.setting_btn.setStyleSheet("QPushButton{border-image:url('sys/img/setting_dark.png')}QPushButton:hover{border-image:url('sys/img/setting_light.png')}")
        self.quit_btn.setStyleSheet("QPushButton{border-image:url('sys/img/exit_dark.png')}QPushButton:hover{border-image:url('sys/img/exit_light.png')}")

    def loading(self):
        self.frontal_preview.setMovie(self.movie)
        self.movie.start()

    def hide_scales(self):
        self.left_scale_text.hide()
        self.left_lcd.hide()
        self.left_scale.hide()
        self.frontal_scale_text.hide()
        self.frontal_lcd.hide()
        self.frontal_scale.hide()
        self.right_scale_text.hide()
        self.right_scale.hide()
        self.right_lcd.hide()

    def load_info(self, info):
        self.info = info
        return self.beginAnalyse()

    def set_info(self):            
        self.parent.hide()
        info_dialog = InfoDialog(self.parent)
        info_dialog.setCallbackAfterSave(self.load_info)
        if self.info:
            info_dialog.outpatient.setText(_translate('MainWindow', self.info['outpatient'], None))
            info_dialog.hospitalized.setText(_translate('MainWindow', self.info['hospitalized'], None))
            info_dialog.name.setText(_translate('MainWindow', self.info['name'], None))
            info_dialog.sex.setCurrentIndex(0 if self.info['sex'] == u'男' else 1)
            info_dialog.height.setCurrentIndex(info_dialog.height.findText(self.info['height']))
            info_dialog.weight.setCurrentIndex(info_dialog.height.findText(self.info['weight']))
            info_dialog.chief_complaint.setText(_translate('MainWindow', self.info['chief_complaint'], None))
            info_dialog.diagnose.setText(_translate('MainWindow', self.info['diagnose'], None))
            info_dialog.born.setDate(QtCore.QDate.fromString(self.info['born'], 'yyyyMd'))
        info_dialog.show()

    def switch_cam(self):
        if self.capture.is_running():
            if not self.capture.next_group():
                util.warn_dialog(text='\xe6\xb2\xa1\xe6\x9c\x89\xe6\xa3\x80\xe6\xb5\x8b\xe5\x88\xb0\xe6\x9b\xb4\xe5\xa4\x9a\xe7\x9a\x84\xe6\x91\x84\xe5\x83\x8f\xe5\xa4\xb4\xe4\xba\x86\xe3\x80\x82')
        else:
            util.warn_dialog(text='\xe5\x85\x88\xe7\x82\xb9\xe5\x87\xbb\xe3\x80\x90\xe6\x89\x93\xe5\xbc\x80\xe6\x91\x84\xe5\x83\x8f\xe5\xa4\xb4\xe3\x80\x91,\xe7\x84\xb6\xe5\x90\x8e\xe5\x86\x8d\xe5\x88\x87\xe6\x8d\xa2\xe6\x91\x84\xe5\x83\x8f\xe5\xa4\xb4')

    def toggle_cam(self, pos):
        d = {'status': False}
        btn = getattr(self, 'choose_%s_cap' % pos)

        def _close_cam():
            self.frontal_line.hide()
            d['status'] = False
            btn.setText(_translate('MainWindow', '\xe6\x89\x93\xe5\xbc\x80\xe6\x91\x84\xe5\x83\x8f\xe5\xa4\xb4', None))
            util.warn_dialog(title='\xe9\x94\x99\xe8\xaf\xaf', text='\xe6\x9c\xaa\xe9\x85\x8d\xe7\xbd\xae\xe6\x91\x84\xe5\x83\x8f\xe5\xa4\xb4\xef\xbc\x8c\xe8\xaf\xb7\xe8\xbf\x9e\xe6\x8e\xa5\xe5\xa5\xbd\xe5\x90\x8e\xe9\x87\x8d\xe5\x90\xaf')

        def _toggle_cam():
            if self.capture is None:
                self.capture = Capture()
            if d['status'] is False:
                d['status'] = True
                if self.capture.useable is True and self.capture.is_open():
                    self.frontal_line.show()
                    self.hide_scales()
                    btn.setText(_translate('MainWindow', '\xe6\x8b\x8d\xe6\x91\x84', None))
                    try:
                        self.capture.start(getattr(self, '_%s_cam_callback' % pos))
                    except:
                        import traceback
                        traceback.print_exc()
                        _close_cam()

                else:
                    _close_cam()
            else:
                btn.setText(_translate('MainWindow', '\xe6\x89\x93\xe5\xbc\x80\xe6\x91\x84\xe5\x83\x8f\xe5\xa4\xb4', None))
                d['status'] = False
                self.capture.end()
                nm_frame, ir_frame = self.capture.get_frames()
                if nm_frame is not None and ir_frame is not None:
                    getattr(self, '_capture_%s' % pos)(nm_frame, ir_frame)
                else:
                    print 'NONEONEONE'

        return _toggle_cam

    def _get_cam_pixmap(self, nm_frame, ir_frame):
        self.from_db = False
        height, width = nm_frame.shape[:2]
        scale = float(width) / height
        image = QtGui.QImage(nm_frame.tostring(), width, height, QtGui.QImage.Format_RGB888).rgbSwapped()
        nm_img = QtGui.QPixmap.fromImage(image)
        image = QtGui.QImage(ir_frame.tostring(), width, height, QtGui.QImage.Format_RGB888).rgbSwapped()
        ir_img = QtGui.QPixmap.fromImage(image)
        return (nm_img, ir_img, scale)

    def stretch_height(self, scale, *labels):
        for label in labels:
            orig_height = label.height()
            height = int(label.width() / scale)
            if height > self.preview_height:
                height = self.preview_height
            if orig_height != height:
                label.resize(label.width(), height)
                pos = label.pos()
                label.setGeometry(pos.x(), pos.y() + (orig_height - height) / 2, label.width(), height)

    def _left_cam_callback(self, nm_frame, ir_frame):
        nm_img, ir_img, scale = self._get_cam_pixmap(nm_frame, ir_frame)
        self.stretch_height(scale, self.left_preview, self.left_ir_preview)
        self.left_preview.setPixmap(nm_img)
        self.left_ir_preview.setPixmap(ir_img)

    def _frontal_cam_callback(self, nm_frame, ir_frame):
        nm_img, ir_img, scale = self._get_cam_pixmap(nm_frame, ir_frame)
        self.stretch_height(scale, self.frontal_preview, self.frontal_ir_preview)
        pos = self.frontal_preview.pos()
        red_line = self.frontal_line
        if red_line.pos().y() != pos.y():
            self.frontal_line.setGeometry(red_line.pos().x(), pos.y(), red_line.width(), self.frontal_preview.height())
        self.frontal_preview.setPixmap(nm_img)
        self.frontal_ir_preview.setPixmap(ir_img)

    def _right_cam_callback(self, nm_frame, ir_frame):
        nm_img, ir_img, scale = self._get_cam_pixmap(nm_frame, ir_frame)
        self.stretch_height(scale, self.right_preview, self.right_ir_preview)
        self.right_preview.setPixmap(nm_img)
        self.right_ir_preview.setPixmap(ir_img)

    def _capture_left(self, nm_frame, ir_frame):
        nm_img, ir_img, scale = self._get_cam_pixmap(nm_frame, ir_frame)
        self.left_preview.setPixmap(nm_img)
        self.left_ir_preview.setPixmap(ir_img)
        nm_img.save(LEFT_TEMP_PATH)
        self.get_face('left', 'normal', LEFT_TEMP_PATH)
        ir_img.save(LEFT_TEMP_IR_PATH)
        self.get_face('left', 'ir', LEFT_TEMP_IR_PATH)

    def _capture_frontal(self, nm_frame, ir_frame):
        self.frontal_line.hide()
        nm_img, ir_img, self.stretch_factor = self._get_cam_pixmap(nm_frame, ir_frame)
        self.frontal_preview.setPixmap(nm_img)
        self.frontal_ir_preview.setPixmap(ir_img)
        nm_img.save(FACE_TEMP_PATH)
        self.get_face('frontal', 'normal', FACE_TEMP_PATH)
        ir_img.save(FACE_TEMP_IR_PATH)
        self.get_face('frontal', 'ir', FACE_TEMP_IR_PATH)

    def _capture_right(self, nm_frame, ir_frame):
        nm_img, ir_img, scale = self._get_cam_pixmap(nm_frame, ir_frame)
        self.right_preview.setPixmap(nm_img)
        self.right_preview.setPixmap(ir_img)
        nm_img.save(RIGHT_TEMP_PATH)
        self.get_face('right', 'normal', RIGHT_TEMP_PATH)
        ir_img.save(RIGHT_TEMP_IR_PATH)
        self.get_face('right', 'ir', RIGHT_TEMP_IR_PATH)

    def pos_move(self, pos):
        if self.focus_preview is None:
            util.warn_dialog(text=u'\u8bf7\u5148\u7528\u9f20\u6807\u9009\u62e9\u56fe\u7247')
        widget = self.focus_preview
        if widget:
            if widget == self.left_preview or widget == self.left_ir_preview:
                if self.LEFT_PATH:
                    LEFT_ORIG = glahf.read(self.LEFT_PATH)
                    glahf.write(LEFT_TEMP_PATH, glahf.enlargeimage(LEFT_ORIG, self.LSCALE, position=pos, tag=LEFT_TAG))
                    self.left_preview.setPixmap(QtGui.QPixmap('' + LEFT_TEMP_PATH))
                if self.LEFT_IR_PATH:
                    LEFT_IR_ORIG = glahf.read(self.LEFT_IR_PATH)
                    glahf.write(LEFT_TEMP_IR_PATH, glahf.enlargeimage(LEFT_IR_ORIG, self.LSCALE, position=pos, tag=LEFT_IR_TAG))
                    self.left_ir_preview.setPixmap(QtGui.QPixmap('' + LEFT_TEMP_IR_PATH))
            elif widget == self.right_preview or widget == self.right_ir_preview:
                if self.RIGHT_PATH:
                    RIGHT_ORIG = glahf.read(self.RIGHT_PATH)
                    glahf.write(RIGHT_TEMP_PATH, glahf.enlargeimage(RIGHT_ORIG, self.RSCALE, position=pos, tag=RIGHT_TAG))
                    self.right_preview.setPixmap(QtGui.QPixmap(RIGHT_TEMP_PATH))
                if self.RIGHT_IR_PATH:
                    RIGHT_IR_ORIG = glahf.read(self.RIGHT_IR_PATH)
                    glahf.write(RIGHT_TEMP_IR_PATH, glahf.enlargeimage(RIGHT_IR_ORIG, self.RSCALE, position=pos, tag=RIGHT_IR_TAG))
                    self.right_ir_preview.setPixmap(QtGui.QPixmap('' + RIGHT_TEMP_IR_PATH))
            elif widget == self.frontal_preview or widget == self.frontal_ir_preview:
                if self.FRONTAL_PATH:
                    FACE_ORIG = glahf.read(self.FRONTAL_PATH)
                    temp = glahf.enlargeimage(FACE_ORIG, self.FSCALE)
                    if self.scale:
                        glahf.write(FACE_TEMP_PATH, glahf.enlargeimage(temp, self.scale, position=pos, tag=FRONTAL_TAG))
                if self.FRONTAL_IR_PATH:
                    FACE_IR_ORIG = glahf.read(self.FRONTAL_IR_PATH)
                    temp_ir = glahf.enlargeimage(FACE_IR_ORIG, self.FSCALE)
                    if self.scale:
                        glahf.write(FACE_TEMP_IR_PATH, glahf.enlargeimage(temp_ir, self.scale, position=pos, tag=FRONTAL_IR_TAG))
                self.frontal_preview.setPixmap(QtGui.QPixmap('' + FACE_TEMP_PATH))
                self.frontal_ir_preview.setPixmap(QtGui.QPixmap('' + FACE_TEMP_IR_PATH))
            else:
                raise ValueError()

    def preview_on_click(self, widget):
        if self.focus_preview is not None:
            self.focus_preview.setStyleSheet('QLabel{border:0px;}')
        if 'border' not in vars(widget):
            widget.setStyleSheet('QLabel{border:3px solid red;}')
            widget.border = True
            self.focus_preview = widget
        else:
            widget.setStyleSheet('QLabel{border:0px;}')
            del widget.border
            self.focus_preview = None

    def set_img(self):
        height, width = self.face.shape[:2]
        lr_distance = self.keyPoints['right_bound']['x'] - self.keyPoints['left_bound']['x']
        ud_distance = self.keyPoints['down_bound']['y'] - self.keyPoints['up_bound']['y']
        lr_offset = lr_distance / LR_LINES
        ud_offset = ud_distance / UD_LINES
        if 0 < int(width / lr_offset) < 200:
            self.config['hposcount'] = int(width / lr_offset)
        else:
            self.config['hposcount'] = 80
        if 0 < int(height / ud_offset) < 200:
            self.config['vposcount'] = int(height / ud_offset)
        else:
            self.config['vposcount'] = 160
        if self.status == False:
            logging.warning(u'\u8bc6\u522b\u72b6\u6001\u5931\u8d25\uff0c\u5f00\u59cb\u4f7f\u7528\u8bb0\u5fc6...')
            m = util.get_memory()
            if m is not None and isinstance(m, list):
                self.linesArr = m
        glahf.write(FACE_ORIG_PATH, self.face)
        glahf.write(FACE_TEMP_PATH, self.face)
        if self.FSCALE is not None and self.FSCALE > 0:
            self.slider_change('frontal')
        else:
            self.frontal_preview.setPixmap(QtGui.QPixmap('' + FACE_TEMP_PATH))
        if self.FRONTAL_IR_PATH:
            IR_IMG = glahf.read(self.FRONTAL_IR_PATH)
            glahf.write(FACE_TEMP_IR_PATH, IR_IMG)
            self.frontal_ir_preview.setPixmap(QtGui.QPixmap('' + FACE_TEMP_IR_PATH))

    def get_face(self, part, mode, spec_path = None):
        self.info = None
        PATH = None
        if spec_path is not None:
            PATH = spec_path.decode('gbk')
        else:
            self.from_db = False
            PATH = unicode(self.showFileDialog())
        if PATH:
            if part == 'left':
                if mode == 'normal':
                    logging.info(u'\u6b63\u5728\u5f00\u59cb\u8bfb\u53d6\u5de6\u8138...')
                    glahf._remove_tag(LEFT_TAG)
                    self.LEFT_PATH = PATH.encode('gbk')
                    IMG = glahf.read(self.LEFT_PATH)
                    height, width = IMG.shape[:2]
                    self.stretch_height(float(width) / height, self.left_preview)
                    glahf.write(LEFT_ORIG_PATH, IMG)
                    glahf.write(LEFT_TEMP_PATH, IMG)
                    self.left_preview.setPixmap(QtGui.QPixmap('' + LEFT_ORIG_PATH))
                    if self.LSCALE is not None and self.LSCALE > 0:
                        self.slider_change('left')
                else:
                    logging.info(u'\u6b63\u5728\u5f00\u59cb\u8bfb\u53d6\u5de6\u8138\u3010IR\u3011...')
                    glahf._remove_tag(LEFT_IR_TAG)
                    self.LEFT_IR_PATH = PATH.encode('gbk')
                    if self.LSCALE is not None and self.LSCALE > 0:
                        self.slider_change('left')
                    else:
                        IR_IMG = glahf.read(self.LEFT_IR_PATH)
                        height, width = IR_IMG.shape[:2]
                        self.stretch_height(float(width) / height, self.left_ir_preview)
                        glahf.write(LEFT_TEMP_IR_PATH, IR_IMG)
                        self.left_ir_preview.setPixmap(QtGui.QPixmap('' + LEFT_TEMP_IR_PATH))
            elif part == 'frontal':
                if mode == 'normal':
                    logging.info(u'\u6b63\u5728\u5f00\u59cb\u8bfb\u53d6\u6b63\u8138...')
                    glahf._remove_tag(FRONTAL_TAG)
                    self.FRONTAL_PATH = PATH.encode('gbk')
                    self.face = glahf.read(self.FRONTAL_PATH)
                    if self.face is None:
                        util.warn_dialog(text='\xe8\xaf\xbb\xe5\x8f\x96\xe5\x9b\xbe\xe7\x89\x87\xe5\xa4\xb1\xe8\xb4\xa5\xef\xbc\x8c\xe6\xa3\x80\xe6\x9f\xa5\xe5\x9b\xbe\xe7\x89\x87\xe8\xb7\xaf\xe5\xbe\x84')
                        return
                    height, width = self.face.shape[:2]
                    self.stretch_height(float(width) / height, self.frontal_preview)
                    self.stretch_factor = float(width) / height

                    def _start():
                        self.linesArr, self.keyPoints, self.status = glahf.markdetect(self.face, face_path=self.FRONTAL_PATH)
                        self.loadingSig.emit()

                    self.loading()
                    t = threading.Thread(target=_start)
                    t.setDaemon(True)
                    t.start()
                else:
                    logging.info(u'\u6b63\u5728\u5f00\u59cb\u8bfb\u53d6\u6b63\u8138\u3010IR\u3011...')
                    glahf._remove_tag(FRONTAL_IR_TAG)
                    self.FRONTAL_IR_PATH = PATH.encode('gbk')
                    if self.FSCALE is not None and self.FSCALE > 0:
                        self.slider_change('frontal')
                    else:
                        IR_IMG = glahf.read(self.FRONTAL_IR_PATH)
                        height, width = IR_IMG.shape[:2]
                        self.stretch_height(float(width) / height, self.frontal_ir_preview)
                        glahf.write(FACE_TEMP_IR_PATH, IR_IMG)
                        self.frontal_ir_preview.setPixmap(QtGui.QPixmap('' + FACE_TEMP_IR_PATH))
            elif part == 'right':
                if mode == 'normal':
                    logging.info(u'\u6b63\u5728\u5f00\u59cb\u8bfb\u53d6\u53f3\u8138...')
                    glahf._remove_tag(RIGHT_TAG)
                    self.RIGHT_PATH = PATH.encode('gbk')
                    IMG = glahf.read(self.RIGHT_PATH)
                    height, width = IMG.shape[:2]
                    self.stretch_height(float(width) / height, self.right_preview)
                    glahf.write(RIGHT_ORIG_PATH, IMG)
                    glahf.write(RIGHT_TEMP_PATH, IMG)
                    self.right_preview.setPixmap(QtGui.QPixmap('' + RIGHT_ORIG_PATH))
                    if self.RSCALE is not None and self.RSCALE > 0:
                        self.slider_change('right')
                else:
                    logging.info(u'\u6b63\u5728\u5f00\u59cb\u8bfb\u53d6\u53f3\u8138\u3010IR\u3011...')
                    glahf._remove_tag(RIGHT_IR_TAG)
                    self.RIGHT_IR_PATH = PATH.encode('gbk')
                    if self.RSCALE is not None and self.RSCALE > 0:
                        self.slider_change('right')
                    else:
                        IR_IMG = glahf.read(self.RIGHT_IR_PATH)
                        height, width = IR_IMG.shape[:2]
                        self.stretch_height(float(width) / height, self.right_ir_preview)
                        glahf.write(RIGHT_TEMP_IR_PATH, IR_IMG)
                        self.right_ir_preview.setPixmap(QtGui.QPixmap('' + RIGHT_TEMP_IR_PATH))
            else:
                logging.warning(u'\u8def\u5f84\u89e3\u6790\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u8def\u5f84\u662f\u5426\u4e3a\u7a7a...')
                raise RuntimeError()

    def slider_change(self, part):
        value = None
        if part == 'left':
            value = self.left_scale.value()
            value = float(value) / 10
            self.LSCALE = value / 2
            self.left_lcd.display(value + 1)
            if self.LEFT_PATH:
                LEFT_ORIG = glahf.read(self.LEFT_PATH)
                glahf.write(LEFT_TEMP_PATH, glahf.enlargeimage(LEFT_ORIG, self.LSCALE))
                self.left_preview.setPixmap(QtGui.QPixmap('' + LEFT_TEMP_PATH))
            if self.LEFT_IR_PATH:
                LEFT_IR_ORIG = glahf.read(self.LEFT_IR_PATH)
                glahf.write(LEFT_TEMP_IR_PATH, glahf.enlargeimage(LEFT_IR_ORIG, self.LSCALE))
                self.left_ir_preview.setPixmap(QtGui.QPixmap('' + LEFT_TEMP_IR_PATH))
        elif part == 'frontal':
            FACE_ORIG = FACE_IR_ORIG = None
            temp = temp_ir = None
            value = self.frontal_scale.value()
            value = float(value) / 10
            self.FSCALE = value / 2
            self.frontal_lcd.display(value + 1)
            if self.FRONTAL_PATH:
                FACE_ORIG = glahf.read(self.FRONTAL_PATH)
                temp = glahf.enlargeimage(FACE_ORIG, self.FSCALE)
                if self.scale:
                    temp = glahf.enlargeimage(temp, self.scale)
                glahf.write(FACE_TEMP_PATH, temp)
                self.frontal_preview.setPixmap(QtGui.QPixmap('' + FACE_TEMP_PATH))
            if self.FRONTAL_IR_PATH:
                FACE_IR_ORIG = glahf.read(self.FRONTAL_IR_PATH)
                temp_ir = glahf.enlargeimage(FACE_IR_ORIG, self.FSCALE)
                if self.scale:
                    temp_ir = glahf.enlargeimage(temp_ir, self.scale)
                glahf.write(FACE_TEMP_IR_PATH, temp_ir)
                self.frontal_ir_preview.setPixmap(QtGui.QPixmap('' + FACE_TEMP_IR_PATH))
            self.linesArr, self.keyPoints, _ = glahf.markdetect(temp, face_path=FACE_TEMP_PATH)
        elif part == 'right':
            value = self.right_scale.value()
            value = float(value) / 10
            self.RSCALE = value / 2
            self.right_lcd.display(value + 1)
            if self.RIGHT_PATH:
                RIGHT_ORIG = glahf.read(self.RIGHT_PATH)
                glahf.write(RIGHT_TEMP_PATH, glahf.enlargeimage(RIGHT_ORIG, self.RSCALE))
                self.right_preview.setPixmap(QtGui.QPixmap(RIGHT_TEMP_PATH))
            if self.RIGHT_IR_PATH:
                RIGHT_IR_ORIG = glahf.read(self.RIGHT_IR_PATH)
                glahf.write(RIGHT_TEMP_IR_PATH, glahf.enlargeimage(RIGHT_IR_ORIG, self.RSCALE))
                self.right_ir_preview.setPixmap(QtGui.QPixmap('' + RIGHT_TEMP_IR_PATH))
        else:
            raise RuntimeError()

    def showFileDialog(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, u'\u6253\u5f00\u56fe\u7247', './images')
        if len(filename) != 0:
            return filename
        return ''

    def select_entry(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, u'\u9009\u62e9\u8bb0\u5f55\u6240\u5728\u6587\u4ef6\u5939', './images')
        directory = os.path.abspath(os.path.dirname(unicode(filename).encode('gbk')))
        if directory:
            if not os.path.exists(os.path.join(directory, INFO_FILE)):
                util.warn_dialog(self, text='\xe9\x80\x89\xe6\x8b\xa9\xe8\xae\xb0\xe5\xbd\x95\xe6\x89\x80\xe5\x9c\xa8\xe6\x96\x87\xe4\xbb\xb6\xe5\xa4\xb9')
            else:
                info = {}
                datas = {}
                with open(os.path.join(directory, INFO_FILE), 'rb') as js:
                    info = json.load(js)
                with open(os.path.join(directory, DATAS_FILE), 'rb') as js:
                    datas = json.load(js)
                if info and datas:
                    self.get_face('left', 'normal', spec_path=os.path.join(directory, 'nm_left.jpg'))
                    self.get_face('frontal', 'normal', spec_path=os.path.join(directory, 'nm_front.jpg'))
                    self.get_face('right', 'normal', spec_path=os.path.join(directory, 'nm_right.jpg'))
                    self.get_face('left', 'ir', spec_path=os.path.join(directory, 'ir_left.jpg'))
                    self.get_face('frontal', 'ir', spec_path=os.path.join(directory, 'ir_front.jpg'))
                    self.get_face('right', 'ir', spec_path=os.path.join(directory, 'ir_right.jpg'))
                    self.info = info
                    self.db_datas = datas
                    self.from_db = True
                else:
                    util.warn_dialog(self, text='\xe6\x96\x87\xe4\xbb\xb6\xe6\x8d\x9f\xe5\x9d\x8f')

    def calc_bounds(self, img, h_lines, v_lines):
        v_beg = (v_lines - 60) / 2
        v_end = v_beg + 60
        h_beg = (h_lines - 40) / 2
        h_end = h_beg + 40
        v_beg_loc = None
        v_end_loc = None
        h_beg_loc = None
        h_end_loc = None
        height, width = img.shape[:2]
        offheight, offwidth = float(height) / v_lines, float(width) / h_lines
        v_beg_loc = int(v_beg * offwidth)
        v_end_loc = int(v_end * offwidth)
        h_beg_loc = int(h_beg * offheight)
        h_end_loc = int(h_end * offheight)
        logging.info(u'\u5f00\u59cb\u8ba1\u7b97\u754c\u9650...')
        return {'v_beg_loc': v_beg_loc,
         'v_end_loc': v_end_loc,
         'h_beg_loc': h_beg_loc,
         'h_end_loc': h_end_loc}

    @util.optional_debug(debug=BEGIN_ANALYSE_DEBUG)
    def beginAnalyse(self):
        if self.info is None:
            return False
        if not self.LEFT_PATH or not self.RIGHT_PATH or not self.FRONTAL_PATH:
            return False
        d = faceutil.handle_images(FACE_TEMP_PATH, LEFT_TEMP_PATH, RIGHT_TEMP_PATH, f_ir_face=FACE_TEMP_IR_PATH, l_ir_face=LEFT_TEMP_IR_PATH, r_ir_face=RIGHT_TEMP_IR_PATH, info=self.info, config=self.config, path=self.config['savedir'])
        if not d:
            return False
        self.db_datas['tardir'] = d['tardir']
        f_img = glahf.read(FACE_TEMP_PATH)
        height, width = f_img.shape[:2]
        d['up'] = round(self.keyPoints['up_bound']['y'] / float(height), 3)
        d['right'] = round(self.keyPoints['right_bound']['x'] / float(width), 3)
        d['down'] = round(self.keyPoints['down_bound']['y'] / float(height), 3)
        d['left'] = round(self.keyPoints['left_bound']['x'] / float(width), 3)
        d['ir_up'] = round(self.keyPoints['up_bound']['y'] / float(height), 3)
        d['ir_right'] = round(self.keyPoints['right_bound']['x'] / float(width), 3)
        d['ir_down'] = round(self.keyPoints['down_bound']['y'] / float(height), 3)
        d['ir_left'] = round(self.keyPoints['left_bound']['x'] / float(width), 3)
        d['stretch_factor'] = self.stretch_factor
        d['linesArr'] = self.linesArr
        with open(os.path.join(d['tardir'], DATAS_FILE), 'w') as fp:
            json.dump(d, fp)
        self.datas = d
        return True

    def openAnalyse(self):
        if self.from_db is True:
            analyseWindow = analyse.AnalyseWindow(datas=self.db_datas, info=self.info)
            analyseWindow.show()
            analyseWindow.set_preview(self.db_datas)
        else:
            if not self.datas or not self.info:
                util.warn_dialog(text='\xe4\xbf\xa1\xe6\x81\xaf\xe4\xb8\x8d\xe5\xae\x8c\xe6\x95\xb4')
            self.analysewindow = analyse.AnalyseWindow(datas=self.datas, config=self.config, info=self.info)
            p = self.datas['up']
            if p != self.last_path and self.last_path is not None:
                self.info = None
            self.latest = p
            logging.info(u'\u5f00\u59cb\u521b\u5efa\u5206\u6790\u7a97\u53e3...')
            self.analysewindow.set_paths(self.LEFT_PATH, self.FRONTAL_PATH, self.RIGHT_PATH)
            self.analysewindow.show()
            self.analysewindow.set_preview(self.datas)

    def quit(self, event):
        try:
            cv2.destroyAllWindows()
            self.close()
            self.parent.close()
            self.capture.quit()
        except:
            pass
        finally:
            QtGui.QApplication.quit()
            QtCore.QCoreApplication.quit()
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:25:48 ÖÐ¹ú±ê×¼Ê±¼ä
