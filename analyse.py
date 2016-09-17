#-*- coding:utf-8 -*-
# 2016.09.12 22:07:32 ÖÐ¹ú±ê×¼Ê±¼ä
#Embedded file name: analyse.pyo
from collections import namedtuple, OrderedDict
from common import *
from component import *
from export import ExportWidget
from glahf import glahf, faceutil
from itertools import chain
from operator import itemgetter
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
import clb
import heapq
import json
import logging
import re
import threading
import math
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


TEMPLATE_HTML = '''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="template.css" charset="utf-8">
</head>
<body>
<div class="header">
<h2 align="center">{hosp_name}</h2>
<h2 align="center">面区色部自动分析仪检测报告</h2>
</div>
<div class="patient-info">
<table>
<tbody>
<tr>
<td style="padding-right: {header_padding}px;">住院号: {hospitalized}</td>
<td style="padding-right: {header_padding}px;">门诊号: {outpatient}</td>
<td>检测时间: {datetime}</td>
</tr>
<tr>
<td style="padding-right: {header_padding}px;">姓名: {name}</td>
<td style="padding-right: {header_padding}px;">性别: {sex}</td>
<td>婚姻: {marriage}</td>
</tr>
<tr>
<td>出生年月: {born}</td>
<td>身高: {height}</td>
<td>体重: {weight}</td>
</tr>
</tbody>
</table>
</div>
<div class="diagnosis-info">
<b>主诉</b>
<p style="text-indent:10px;">{chief_complaint}</p>
<b>初步诊断</b>
<p style="text-indent:10px;">{diagnose}</p>
<table>
<tbody>
<tr>
<td>
<img src="mydata://nm.jpg" class="ir" height={img_width} width={img_width} />
</td>
<td>
<img src="mydata://ir.jpg" class="nm" height={img_width} width={img_width} style="margin-left:{img_width}px;" />
</td>
</tr>
</tbody>
</table>
</div>
<div class="data-info" style="clear: both;">
<table>
<tbody align="center">
<tr class="table-head">
<th></th>
<th width="250px">区域</th>
<th>灰度值</th>
<th>颜色</th>
<th>普通均值</th>
<th>颜色</th>
<th>普通差值</th>
<th>红外灰度</th>
<th>颜色</th>
<th>红外均值</th>
<th>颜色</th>
<th>红外差值</th>
</tr>
{grid_html}
</tbody>
</table>
<table>
{sec_grid_html}
<table>
</div>
<h4>异常数据</h4>
<table>
<tr>
<td>普通</td>
<td>红外</td>
</tr>
<tr>
<td>
<ul>
{exp_html}
</ul>
</td>
<td>
<ul>
{ir_exp_html}
</ul>
</td>
</tr>
</table>
<h4 align="right" style="margin-right: 180px;">检测人签字</h4><br/>
<h4 align="right" style="padding-right: 150px;">年&nbsp;&nbsp;&nbsp;&nbsp;月&nbsp;&nbsp;&nbsp;&nbsp;日</h4>
</body>
</html>
'''

TEMPLATE_CSS = '''
body {
font-size: 12px;
}
h4 {
font-size: 12px;
}
.data-info {
margin-top: 5px;
}
.data-info table {
border: 1px solid black;
border-collapse: collapse;
}
.data-info td {
border: 1px solid black;
padding: 0 0px;
}
.data-info th {
border: 1px solid black;
padding: 0 0px;
}
.table-head {
background-color: rgb(217, 217, 217);
}
'''

_region = namedtuple('region', ['start',
 'end',
 'intro',
 'verbose'])
FACE_REGION = OrderedDict(sorted({'left_11': _region('15L2', '22L8', '左胸、乳', '211'),
 'left_12': _region('22L3', '26L8', '左上腹区', '212'),
 'left_13': _region('26L4', '29L14', '左上腹区2', '213'),
 'left_14': _region('29L5', '32L14', '左中腹区', '214'),
 'left_15': _region('32L6', '35L14', '左中腹区2', '215'),
 'left_16': _region('35L8', '37L14', '左小腹区', '216'),
 'left_17': _region('37L8', '43L14', '外生殖器区(左)', '217'),
 'left_21': _region('26L14', '30L20', '左肩区', '421'),
 'left_22': _region('30L14', '34L20', '左背区', '422'),
 'left_23': _region('34L14', '38L20', '左腰区', '423'),
 'left_24': _region('38L14', '42L20', '左股里(臀)', '424'),
 'left_25': _region('42L14', '46L20', '左膝膑(腘)', '425'),
 'left_26': _region('46L14', '50L20', '左足区', '426'),
 'mid_1': _region('1R2', '8L2', '首面', '11'),
 'mid_2': _region('8R2', '15L2', '咽喉(颈)', '12'),
 'mid_3': _region('15R2', '18L2', '肺', '13'),
 'mid_4': _region('18R2', '22L2', '心', '14'),
 'mid_5': _region('22R3', '26L3', '肝胆', '15'),
 'mid_6': _region('26R4', '29L4', '脾胃', '16'),
 'mid_7': _region('29R2', '32L2', '大肠', '17'),
 'mid_8': _region('29R5', '32R2', '右肾', '18'),
 'mid_9': _region('29L2', '32L5', '左肾', '19'),
 'mid_10': _region('32R6', '35L6', '小肠区', '110'),
 'mid_11': _region('35R8', '37L8', '膀胱-子处', '111'),
 'right_11': _region('15R8', '22R2', '右胸、乳区', '311'),
 'right_12': _region('22R8', '26R3', '右上腹区', '312'),
 'right_13': _region('26R14', '29R4', '右上腹区2', '313'),
 'right_14': _region('29R14', '32L5', '右中腹区', '314'),
 'right_15': _region('32R14', '35R6', '右中腹区2', '315'),
 'right_16': _region('35R14', '37R8', '右小腹区', '316'),
 'right_17': _region('37R14', '43R8', '外生殖器区(右)', '317'),
 'right_21': _region('26R20', '30R14', '右肩区', '521'),
 'right_22': _region('30R20', '34R14', '右背区', '522'),
 'right_23': _region('34R20', '38R14', '右腰区', '523'),
 'right_24': _region('38R20', '42R14', '右股里(臀)', '524'),
 'right_25': _region('42R20', '46R14', '右膝膑(腘)区', '525'),
 'right_26': _region('46R20', '50R14', '右足区', '526')}.items(), key=lambda item: int(item[1].verbose)))

class LinesList(list):

    def get(self, label):
        for line in self:
            if line.info == label:
                return line


class AnalyseWindow(QtGui.QMainWindow):

    class RegionWidget(QtGui.QTableWidget):

        def __init__(self, parent = None):
            QtGui.QTableWidget.__init__(self)
            self.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.index = 0
            self.parent = parent
            header = self.horizontalHeader()
            self.setColumnCount(11)
            size = 49
            self.setRowCount(size)
            self.setColumnWidth(0, 160)
            self.setColumnWidth(1, 90)
            self.setColumnWidth(2, 70)
            self.setColumnWidth(3, 110)
            self.setColumnWidth(4, 70)
            self.setColumnWidth(5, 120)
            self.setColumnWidth(6, 110)
            self.setColumnWidth(7, 70)
            self.setColumnWidth(8, 110)
            self.setColumnWidth(9, 70)
            self.setColumnWidth(10, 110)
            self.region_list = [None] * size
            self.compare_list = [None] * size
            self.ir_compare_list = [None] * size
            str_list = QtCore.QStringList()
            str_list.append(self.tr('\xe5\x8c\xba\xe5\x9f\x9f'))
            str_list.append(self.tr('\xe7\x81\xb0\xe5\xba\xa6\xe5\x80\xbc'))
            str_list.append(self.tr('\xe9\xa2\x9c\xe8\x89\xb2'))
            str_list.append(self.tr('\xe6\x99\xae\xe9\x80\x9a\xe5\x9d\x87\xe5\x80\xbc'))
            str_list.append(self.tr('\xe9\xa2\x9c\xe8\x89\xb2'))
            str_list.append(self.tr('\xe6\x99\xae\xe9\x80\x9a\xe5\xb7\xae\xe5\x80\xbc'))
            str_list.append(self.tr('\xe7\xba\xa2\xe5\xa4\x96\xe7\x81\xb0\xe5\xba\xa6'))
            str_list.append(self.tr('\xe9\xa2\x9c\xe8\x89\xb2'))
            str_list.append(self.tr('\xe7\xba\xa2\xe5\xa4\x96\xe5\x9d\x87\xe5\x80\xbc'))
            str_list.append(self.tr('\xe9\xa2\x9c\xe8\x89\xb2'))
            str_list.append(self.tr('\xe7\xba\xa2\xe5\xa4\x96\xe5\xb7\xae\xe5\x80\xbc'))
            self.setHorizontalHeaderLabels(str_list)
            self.setSelectionBehavior(QtGui.QTableView.SelectRows)
            self.itemClicked.connect(self.onTableClicked)

        @classmethod
        def make_compare_value(cls, gv, exp_gv):
            return round(float(gv) - float(exp_gv), 2)

        @classmethod
        def make_compare_string(cls, gv, exp_gv):
            val = cls.make_compare_value(gv, exp_gv)
            if val > 0:
                return '\xe2\x86\x91 %s' % str(val)
            elif val < 0:
                return '\xe2\x86\x93 %s' % str(val)
            else:
                return '0.0'

        def append(self, index, region, gv, ir_gv):
            if math.isnan(gv):
                gv = 0
            if math.isnan(ir_gv):
                ir_gv = 0
            self.region_list[index] = [region.intro,
             str(gv),
             str(glahf.gray_to_pseudo(int(gv))),
             str(self.parent.all_gv),
             str(glahf.gray_to_pseudo(int(self.parent.all_gv))),
             self.make_compare_string(gv, self.parent.all_gv),
             str(ir_gv),
             str(glahf.gray_to_pseudo(int(ir_gv))),
             str(self.parent.all_ir_gv),
             str(glahf.gray_to_pseudo(int(self.parent.all_ir_gv))),
             self.make_compare_string(ir_gv, self.parent.all_ir_gv)]
            self.setItem(index, 0, QtGui.QTableWidgetItem(_translate('MainWindow', region.intro, None)))
            self.compare_list[index] = (region.intro, self.make_compare_value(gv, self.parent.all_gv))
            self.ir_compare_list[index] = (region.intro, self.make_compare_value(ir_gv, self.parent.all_ir_gv))
            self.setItem(index, 1, QtGui.QTableWidgetItem(_translate('MainWindow', str(gv), None)))
            self.setItem(index, 2, QtGui.QTableWidgetItem())
            self.item(index, 2).setBackground(QtGui.QColor(*glahf.gray_to_pseudo(int(gv))))
            self.setItem(index, 3, QtGui.QTableWidgetItem(_translate('MainWindow', str(self.parent.all_gv), None)))
            self.setItem(index, 4, QtGui.QTableWidgetItem())
            self.item(index, 4).setBackground(QtGui.QColor(*glahf.gray_to_pseudo(int(self.parent.all_gv))))
            self.setItem(index, 5, QtGui.QTableWidgetItem(_translate('MainWindow', self.make_compare_string(gv, self.parent.all_gv), None)))
            self.setItem(index, 6, QtGui.QTableWidgetItem(_translate('MainWindow', str(ir_gv), None)))
            self.setItem(index, 7, QtGui.QTableWidgetItem())
            self.item(index, 7).setBackground(QtGui.QColor(*glahf.gray_to_pseudo(int(ir_gv))))
            self.setItem(index, 8, QtGui.QTableWidgetItem(_translate('MainWindow', str(self.parent.all_ir_gv), None)))
            self.setItem(index, 9, QtGui.QTableWidgetItem())
            self.item(index, 9).setBackground(QtGui.QColor(*glahf.gray_to_pseudo(int(self.parent.all_ir_gv))))
            self.setItem(index, 10, QtGui.QTableWidgetItem(_translate('MainWindow', self.make_compare_string(ir_gv, self.parent.all_ir_gv), None)))

        def onTableClicked(self, item, *args, **kws):
            row = item.row()
            intro = self.item(row, 0).text()
            nm_gv = self.item(row, 1).text()
            nm_exp = self.item(row, 5).text()
            ir_gv = self.item(row, 6).text()
            ir_exp = self.item(row, 10).text()
            self.parent.area_sp_Color.setStyleSheet('margin:0px 30px;background-color:rgb%s;' % str(glahf.gray_to_pseudo(int(float(nm_gv)))))
            self.parent.result_Label.setText(_translate('MainWindow', '\xe6\x99\xae\xe9\x80\x9a\xe5\x8c\xba\xe5\x9f\x9f\xe5\x80\xbc\xef\xbc\x9a%s' % nm_gv, None))
            self.parent.ir_area_sp_Color.setStyleSheet('margin:0px 30px;background-color:rgb%s;' % str(glahf.gray_to_pseudo(int(float(ir_gv)))))
            self.parent.ir_result_Label.setText(_translate('MainWindow', '\xe7\xba\xa2\xe5\xa4\x96\xe5\x8c\xba\xe5\x9f\x9f\xe5\x80\xbc\xef\xbc\x9a%s' % ir_gv, None))
            self.parent.area_text.setText(_translate('MainWindow', intro, None))
            self.parent.nm_exp_text.setText(_translate('MainWindow', '\xe6\xad\xa3\xe5\xb8\xb8\xe5\xb7\xae\xe5\x80\xbc:\n%s' % nm_exp, None))
            self.parent.ir_exp_text.setText(_translate('MainWindow', '\xe7\xba\xa2\xe5\xa4\x96\xe5\xb7\xae\xe5\x80\xbc:\n%s' % ir_exp, None))

        def get_exp_areas(self):
            lowers = heapq.nsmallest(3, self.compare_list, key=lambda tup: tup[1])
            highers = heapq.nlargest(3, self.compare_list, key=lambda tup: tup[1])
            return (lowers, highers)

        def get_ir_exp_areas(self):
            lowers = heapq.nsmallest(3, self.ir_compare_list, key=lambda tup: tup[1])
            highers = heapq.nlargest(3, self.ir_compare_list, key=lambda tup: tup[1])
            return (lowers, highers)

        def __call__(self):
            self.show()

    class _Status(object):
        __slots__ = ()
        FOCUS = 'START'
        CURRENT_MODE = 'NORMAL'

    class InputEdit(QtGui.QLineEdit):

        def __init__(self, parent):
            QtGui.QLineEdit.__init__(self, parent)

        @property
        def key(self):
            return self._key

        @key.setter
        def key(self, value):
            self._key = value

        def mousePressEvent(self, ev):
            AnalyseWindow._Status.FOCUS = self._key

    @property
    def mode(self):
        return self._Status.CURRENT_MODE

    @mode.setter
    def mode(self, value):
        if value in ('NORMAL', 'IR'):
            self._Status.CURRENT_MODE = value
        else:
            raise ValueError('unexpected value')

    @property
    def focus(self):
        return self._Status.FOCUS

    @focus.setter
    def focus(self, value):
        if value in ('START', 'END'):
            self._Status.FOCUS = value
        else:
            raise ValueError('unexpected value')

    def __init__(self, parent = None, datas = None, config = None, info = None):
        super(AnalyseWindow, self).__init__(parent)
        self.focus = 'START'
        self.active_gray_img = None
        self.img_path = None
        self.spliced_img = None
        self.vis = None
        self.clb_gv = 0
        self.clb_os = 0
        self.info = info
        self.__linesArr = datas.get('linesArr', [])
        self.__vDraglines = LinesList()
        self.__hDraglines = LinesList()
        self.datas = datas
        self.reset_datas = dict(datas)
        self.region = self.RegionWidget(self)
        self.MAP = None
        if config is not None:
            self.config = config
        else:
            self.config = util.load_config()
        self.setupUi(self)
        self.retranslateUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.set_paths(None, None, None)

    class PreviewLabel(QtGui.QLabel):
        QLE_BGSTYLE = 'QLineEdit{background: %s;}'

        def __init__(self, parent, *arg, **kw):
            QtGui.QLabel.__init__(self, parent)
            self.parent = parent
            self.voffset = self.hoffset = None
            self.set_offset()

        def set_offset(self):
            self.voffset = (self.parent.datas['down'] - self.parent.datas['up']) * self.parent.PREVIEW_H / 60.0
            self.hoffset = (self.parent.datas['right'] - self.parent.datas['left']) * self.parent.PREVIEW_W / 80.0

        def get_offset(self):
            return (self.hoffset, self.voffset)

        def mousePressEvent(self, ev):
            self.set_offset()
            x = ev.x()
            y = ev.y()
            l_offset = self.parent.datas['left'] * self.parent.PREVIEW_W
            u_offset = self.parent.datas['up'] * self.parent.PREVIEW_H
            hpos = int(round((x - l_offset) / float(self.hoffset)))
            vpos = int(round((y - u_offset) / float(self.voffset)))
            if hpos < 0 or hpos > 80 or vpos < 0 or vpos > 60:
                return
            pos = str(vpos) + self.parent.MAP[hpos].strip()
            if self.parent.focus:
                self.parent.setCursor(Qt.CrossCursor)
                color = 'red'
                if self.parent.focus == 'START':
                    self.parent.startpoint_input.setText(pos)
                    self.parent.startpoint_input.setStyleSheet(self.QLE_BGSTYLE % color)
                else:
                    self.parent.endpoint_input.setText(pos)
                    self.parent.endpoint_input.setStyleSheet(self.QLE_BGSTYLE % color)
                if self.parent.startpoint_input.text() and self.parent.endpoint_input.text():
                    self.parent.retrieve()

        def mouseReleaseEvent(self, ev):
            if self.parent.focus:
                self.parent.setCursor(Qt.ArrowCursor)
                color = 'white'
                if self.parent.focus == 'START':
                    self.parent.startpoint_input.setStyleSheet(self.QLE_BGSTYLE % color)
                else:
                    self.parent.endpoint_input.setStyleSheet(self.QLE_BGSTYLE % color)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8('MainWindow'))
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        screen = QtGui.QDesktopWidget().screenGeometry()
        GLOBAL_WIDTH = screen.width()
        GLOBAL_HEIGHT = screen.height()
        self.resize(GLOBAL_WIDTH, GLOBAL_HEIGHT)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8('centralwidget'))
        font = QtGui.QFont()
        try:
            font.setFamily(_fromUtf8('Microsoft YaHei'))
        except Exception as e:
            font.setFamily(_fromUtf8('Arial'))

        self.setStyleSheet('QLineEdit{margin-left:20%;margin-right:30%;height:50%;font-size:18px;}')
        self.PREVIEW_W = GLOBAL_WIDTH * 0.6
        stretch_factor = self.datas['stretch_factor']
        if stretch_factor is not None:
            self.PREVIEW_H = int(self.PREVIEW_W / stretch_factor)
            self.PREVIEW_TOTOP = (GLOBAL_HEIGHT - self.PREVIEW_H) / 2
            if self.PREVIEW_TOTOP < 20:
                self.PREVIEW_H = GLOBAL_HEIGHT * 0.95
                self.PREVIEW_TOTOP = 20
        else:
            self.PREVIEW_H = GLOBAL_HEIGHT * 0.95
            self.PREVIEW_TOTOP = 20
        self.PREVIEW_TOLEFT = GLOBAL_WIDTH * 0.03
        self.LINE_WEIGHT = 8
        self.bottom_layout_ctn = QtGui.QWidget(self.centralwidget)
        self.bottom_layout_ctn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.65, 0, GLOBAL_WIDTH * 0.35, GLOBAL_HEIGHT))
        self.bottom_layout_ctn.setObjectName(_fromUtf8('bottom_layout_ctn'))
        self.bottom_layout = QtGui.QVBoxLayout(self.bottom_layout_ctn)
        self.bottom_layout.setObjectName(_fromUtf8('bottom_layout'))
        self.preview = self.PreviewLabel(self)
        self.preview.setGeometry(QtCore.QRect(self.PREVIEW_TOLEFT, self.PREVIEW_TOTOP, self.PREVIEW_W, self.PREVIEW_H))
        self.preview.setScaledContents(True)
        self.preview.setObjectName(_fromUtf8('label'))
        self._loc = []
        self.redraw_loc(80, 60)
        self.autoget_text = QtGui.QLabel(self.centralwidget)
        font.setPointSize(18)
        self.autoget_text.setFont(font)
        self.area_12af_Label = QtGui.QLabel(self.centralwidget)
        self.area_12af_Color = QtGui.QLabel(self.centralwidget)
        self.area_34ef_Label = QtGui.QLabel(self.centralwidget)
        self.area_34ef_Color = QtGui.QLabel(self.centralwidget)
        self.area_45bc_Label = QtGui.QLabel(self.centralwidget)
        self.area_45bc_Color = QtGui.QLabel(self.centralwidget)
        self.area_45de_Label = QtGui.QLabel(self.centralwidget)
        self.area_45de_Color = QtGui.QLabel(self.centralwidget)
        self.area_45ef_Label = QtGui.QLabel(self.centralwidget)
        self.area_45ef_Color = QtGui.QLabel(self.centralwidget)
        self.left_avg_Label = QtGui.QLabel(self.centralwidget)
        self.left_avg_Color = QtGui.QLabel(self.centralwidget)
        self.frontal_avg_Label = QtGui.QLabel(self.centralwidget)
        self.frontal_avg_Color = QtGui.QLabel(self.centralwidget)
        self.right_avg_Label = QtGui.QLabel(self.centralwidget)
        self.right_avg_Color = QtGui.QLabel(self.centralwidget)
        self.all_avg_Label = QtGui.QLabel(self.centralwidget)
        font.setPointSize(13)
        self.all_avg_Label.setFont(font)
        self.all_avg_Color = QtGui.QLabel(self.centralwidget)
        self.left_avg_ir_Label = QtGui.QLabel(self.centralwidget)
        self.left_avg_ir_Color = QtGui.QLabel(self.centralwidget)
        self.frontal_avg_ir_Label = QtGui.QLabel(self.centralwidget)
        self.frontal_avg_ir_Color = QtGui.QLabel(self.centralwidget)
        self.right_avg_ir_Label = QtGui.QLabel(self.centralwidget)
        self.right_avg_ir_Color = QtGui.QLabel(self.centralwidget)
        self.all_avg_ir_Label = QtGui.QLabel(self.centralwidget)
        self.all_avg_ir_Color = QtGui.QLabel(self.centralwidget)
        frameStyle = 'border:1px solid lightgray;border-radius:5px;opacity:0.5;'
        self.frame_ = QtGui.QWidget(self.centralwidget)
        self.frame_.setStyleSheet(frameStyle)
        self.area_text = QtGui.QLabel(self.centralwidget)
        font.setPointSize(13)
        self.area_text.setFont(font)
        font.setPointSize(12)
        self.area_text.setObjectName(_fromUtf8('area_text'))
        self.nm_exp_text = QtGui.QLabel(self.centralwidget)
        self.nm_exp_text.setFont(font)
        self.ir_exp_text = QtGui.QLabel(self.centralwidget)
        self.ir_exp_text.setFont(font)
        self.result_Label = QtGui.QLabel(self.centralwidget)
        font.setPointSize(12)
        self.result_Label.setFont(font)
        self.result_Label.setText(_fromUtf8(''))
        self.result_Label.setObjectName(_fromUtf8('result_Label'))
        self.area_sp_Color = QtGui.QLabel(self.centralwidget)
        self.area_avg_Color = QtGui.QLabel(self.centralwidget)
        self.position_text = QtGui.QLabel(self.centralwidget)
        font.setPointSize(18)
        self.position_text.setFont(font)
        self.position_text.setObjectName(_fromUtf8('position_text'))
        self.startpoint = QtGui.QLabel(self.centralwidget)
        font.setPointSize(12)
        self.startpoint.setFont(font)
        self.startpoint.setObjectName(_fromUtf8('startpoint'))
        self.endpoint = QtGui.QLabel(self.centralwidget)
        self.endpoint.setFont(font)
        self.endpoint.setObjectName(_fromUtf8('endpoint'))
        self.startpoint_input = self.InputEdit(self.centralwidget)
        self.startpoint_input.setObjectName(_fromUtf8('startpoint_input'))
        self.startpoint_input.key = 'START'
        self.endpoint_input = self.InputEdit(self.centralwidget)
        self.endpoint_input.setObjectName(_fromUtf8('endpoint_input'))
        self.endpoint_input.key = 'END'
        font.setPointSize(9)
        self.tip_text = QtGui.QLabel(self.centralwidget)
        self.tip_text.setFont(font)
        self.tip_text.setText(_fromUtf8(''))
        self.tip_text.setObjectName(_fromUtf8('tip_text'))
        self.center_layout = QtGui.QGridLayout()
        self.center_layout.setObjectName(_fromUtf8('center_layout'))
        self.center_layout.setSpacing(10)
        self.position_text.setMargin(10)
        self.startpoint.setMargin(10)
        self.endpoint.setMargin(10)
        self.center_layout.addWidget(self.frame_, 0, 0, 5, 3)
        self.bottom_layout.addWidget(self.region)
        self.center_layout.addWidget(self.position_text, 0, 0, 2, 1)
        self.center_layout.addWidget(self.tip_text, 0, 1, 2, 2)
        self.center_layout.addWidget(self.startpoint, 1, 0, 1, 1)
        self.center_layout.addWidget(self.endpoint, 2, 0, 1, 1)
        self.center_layout.addWidget(self.startpoint_input, 1, 1, 1, 2)
        self.center_layout.addWidget(self.endpoint_input, 2, 1, 1, 2)
        self.quit_btn = QtGui.QPushButton(self.centralwidget)
        font.setPointSize(14)
        self.quit_btn.setFont(font)
        self.quit_btn.setObjectName(_fromUtf8('quit_btn'))
        self.result_layout = QtGui.QVBoxLayout()
        self.result_layout.addWidget(self.area_sp_Color)
        self.result_layout.addWidget(self.result_Label)
        self.avg_layout = QtGui.QVBoxLayout()
        self.avg_layout.addWidget(self.area_avg_Color)
        self.avg_layout.addWidget(self.all_avg_Label)
        self.ir_area_sp_Color = QtGui.QLabel(self.centralwidget)
        self.ir_area_avg_Color = QtGui.QLabel(self.centralwidget)
        self.ir_result_Label = QtGui.QLabel(self.centralwidget)
        font.setPointSize(12)
        self.ir_result_Label.setFont(font)
        self.ir_result_Label.setText(_fromUtf8(''))
        self.ir_result_Label.setObjectName(_fromUtf8('ir_result_Label'))
        self.ir_all_avg_Label = QtGui.QLabel(self.centralwidget)
        self.ir_all_avg_Label.setFont(font)
        self.ir_all_avg_Label.setText(_fromUtf8(''))
        self.ir_all_avg_Label.setObjectName(_fromUtf8('ir_all_avg_Label'))
        self.ir_result_layout = QtGui.QVBoxLayout()
        self.ir_result_layout.addWidget(self.ir_area_sp_Color)
        self.ir_result_layout.addWidget(self.ir_result_Label)
        self.ir_avg_layout = QtGui.QVBoxLayout()
        self.ir_avg_layout.addWidget(self.ir_area_avg_Color)
        self.ir_avg_layout.addWidget(self.ir_all_avg_Label)
        self.illu_layout = QtGui.QVBoxLayout()
        self.illu_layout.addWidget(self.area_text)
        self.illu_layout.addWidget(self.nm_exp_text)
        self.illu_layout.addWidget(self.ir_exp_text)
        self.center_layout.addLayout(self.illu_layout, 3, 0, 2, 1)
        self.center_layout.addLayout(self.result_layout, 3, 1, 1, 1)
        self.center_layout.addLayout(self.avg_layout, 3, 2, 1, 1)
        self.center_layout.addLayout(self.ir_result_layout, 4, 1, 1, 1)
        self.center_layout.addLayout(self.ir_avg_layout, 4, 2, 1, 1)
        self.bottom_layout.addLayout(self.center_layout)
        self.bottom_layout.setStretch(0, 1)
        self.bottom_layout.setStretch(1, 1)
        self.bottom_layout.setStretch(2, 1)
        font.setPointSize(15)
        self.R_Label = QtGui.QLabel(self.centralwidget)
        self.R_Label.setText('R')
        self.R_Label.setFont(font)
        self.R_Label.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.01, self.PREVIEW_TOTOP, GLOBAL_WIDTH * 0.03, GLOBAL_HEIGHT * 0.03))
        self.L_Label = QtGui.QLabel(self.centralwidget)
        self.L_Label.setText('L')
        self.L_Label.setFont(font)
        self.L_Label.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.64, self.PREVIEW_TOTOP, GLOBAL_WIDTH * 0.03, GLOBAL_HEIGHT * 0.03))
        font.setPointSize(10)
        self.choose_left_btn = QtGui.QPushButton(self.centralwidget)
        self.choose_left_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.0, GLOBAL_HEIGHT * 0.9, GLOBAL_WIDTH * 0.03, GLOBAL_HEIGHT * 0.08))
        self.choose_left_btn.setObjectName(_fromUtf8('choose_left_btn'))
        self.choose_left_btn.setText(_translate('MainWindow', '\xe9\x80\x89\xe6\x8b\xa9\xe5\xb7\xa6\xe8\x84\xb8', None))
        self.choose_left_btn.clicked.connect(self.choose_face('left'))
        self.choose_left_btn.setFont(font)
        self.choose_frontal_btn = QtGui.QPushButton(self.centralwidget)
        self.choose_frontal_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.0, GLOBAL_HEIGHT * 0.9, GLOBAL_WIDTH * 0.03, GLOBAL_HEIGHT * 0.08))
        self.choose_frontal_btn.setObjectName(_fromUtf8('choose_frontal_btn'))
        self.choose_frontal_btn.setText(_translate('MainWindow', '\xe9\x80\x89\xe6\x8b\xa9\xe6\xad\xa3\xe8\x84\xb8', None))
        self.choose_frontal_btn.clicked.connect(self.choose_face('frontal'))
        self.choose_frontal_btn.setFont(font)
        self.choose_right_btn = QtGui.QPushButton(self.centralwidget)
        self.choose_right_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.0, GLOBAL_HEIGHT * 0.9, GLOBAL_WIDTH * 0.03, GLOBAL_HEIGHT * 0.08))
        self.choose_right_btn.setObjectName(_fromUtf8('choose_right_btn'))
        self.choose_right_btn.setText(_translate('MainWindow', '\xe9\x80\x89\xe6\x8b\xa9\xe5\x8f\xb3\xe8\x84\xb8', None))
        self.choose_right_btn.clicked.connect(self.choose_face('right'))
        self.choose_right_btn.setFont(font)
        self.choose_left_ir_btn = QtGui.QPushButton(self.centralwidget)
        self.choose_left_ir_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.0, GLOBAL_HEIGHT * 0.9, GLOBAL_WIDTH * 0.03, GLOBAL_HEIGHT * 0.08))
        self.choose_left_ir_btn.setObjectName(_fromUtf8('choose_left_ir_btn'))
        self.choose_left_ir_btn.setText(_translate('MainWindow', '\xe9\x80\x89\xe6\x8b\xa9\xe7\xba\xa2\xe5\xa4\x96\xe5\xb7\xa6\xe8\x84\xb8', None))
        self.choose_left_ir_btn.clicked.connect(self.choose_face('ir_left'))
        self.choose_left_ir_btn.setFont(font)
        self.choose_frontal_ir_btn = QtGui.QPushButton(self.centralwidget)
        self.choose_frontal_ir_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.0, GLOBAL_HEIGHT * 0.9, GLOBAL_WIDTH * 0.03, GLOBAL_HEIGHT * 0.08))
        self.choose_frontal_ir_btn.setObjectName(_fromUtf8('choose_frontal_ir_btn'))
        self.choose_frontal_ir_btn.setText(_translate('MainWindow', '\xe9\x80\x89\xe6\x8b\xa9\xe7\xba\xa2\xe5\xa4\x96\xe6\xad\xa3\xe8\x84\xb8', None))
        self.choose_frontal_ir_btn.clicked.connect(self.choose_face('ir_frontal'))
        self.choose_frontal_ir_btn.setFont(font)
        self.choose_right_ir_btn = QtGui.QPushButton(self.centralwidget)
        self.choose_right_ir_btn.setGeometry(QtCore.QRect(GLOBAL_WIDTH * 0.0, GLOBAL_HEIGHT * 0.9, GLOBAL_WIDTH * 0.03, GLOBAL_HEIGHT * 0.08))
        self.choose_right_ir_btn.setObjectName(_fromUtf8('choose_right_ir_btn'))
        self.choose_right_ir_btn.setText(_translate('MainWindow', '\xe9\x80\x89\xe6\x8b\xa9\xe7\xba\xa2\xe5\xa4\x96\xe5\x8f\xb3\xe8\x84\xb8', None))
        self.choose_right_ir_btn.clicked.connect(self.choose_face('ir_right'))
        self.choose_right_ir_btn.setFont(font)
        self.export_report_btn = QtGui.QPushButton(self.centralwidget)
        self.export_report_btn.setObjectName(_fromUtf8('export_report_btn'))
        self.export_report_btn.setText(_translate('MainWindow', '\xe7\x94\x9f\xe6\x88\x90\xe6\x8a\xa5\xe5\x91\x8a', None))
        self.export_report_btn.clicked.connect(self.export_report)
        self.export_report_btn.setFont(font)
        self.reset_btn = QtGui.QPushButton(self.centralwidget)
        self.reset_btn.setObjectName(_fromUtf8('reset_btn'))
        self.reset_btn.setText(_translate('MainWindow', '\xe5\x9b\x9e\xe5\x88\xb0\xe6\x9c\x80\xe5\x88\x9d', None))
        self.reset_btn.clicked.connect(self.reset)
        self.reset_btn.setFont(font)
        self.toggle_clb_btn = QtGui.QPushButton(self.centralwidget)
        self.toggle_clb_btn.setObjectName(_fromUtf8('toggle_clb_btn'))
        self.toggle_clb_btn.setText(_translate('MainWindow', '\xe6\x89\x93\xe5\xbc\x80\xe7\x99\xbd\xe6\x9d\xbf', None))
        self.toggle_clb_btn.clicked.connect(self.toggle_clb())
        self.toggle_clb_btn.setFont(font)
        self.clb_status = False
        font.setPointSize(18)
        self.advance_layout = QtGui.QGridLayout()
        self.advance_layout.setObjectName(_fromUtf8('advance_layout'))
        self.advance_layout.addWidget(self.choose_left_btn, 0, 0, 1, 1)
        self.advance_layout.addWidget(self.choose_frontal_btn, 0, 1, 1, 1)
        self.advance_layout.addWidget(self.choose_right_btn, 0, 2, 1, 1)
        self.advance_layout.addWidget(self.choose_left_ir_btn, 1, 0, 1, 1)
        self.advance_layout.addWidget(self.choose_frontal_ir_btn, 1, 1, 1, 1)
        self.advance_layout.addWidget(self.choose_right_ir_btn, 1, 2, 1, 1)
        self.advance_layout.addWidget(self.export_report_btn, 2, 0, 1, 1)
        self.advance_layout.addWidget(self.reset_btn, 2, 1, 1, 1)
        self.advance_layout.addWidget(self.toggle_clb_btn, 2, 2, 1, 1)
        self.advance_layout.setRowStretch(0, 3)
        self.llayout = QtGui.QGridLayout()
        self.llayout.addWidget(self.quit_btn)
        self.bottom_layout.addLayout(self.advance_layout)
        self.bottom_layout.addLayout(self.llayout)
        self.advances = [self.reset_btn,
         self.toggle_clb_btn,
         self.choose_left_btn,
         self.choose_frontal_btn,
         self.choose_right_btn,
         self.choose_left_ir_btn,
         self.choose_frontal_ir_btn,
         self.choose_right_ir_btn,
         self.export_report_btn,
         self.quit_btn]
        for btn in self.advances:
            btn.setStyleSheet('QPushButton{border:1px solid lightgray;background:rgb(220,230,230);}QPushButton:hover{border-color:green;background:transparent}')

        MainWindow.setCentralWidget(self.centralwidget)
        self.connect(self.quit_btn, QtCore.SIGNAL('clicked()'), self.return_to)
        self.setAcceptDrops(True)
        self.green_lines = LinesList()
        for key in ['f', 'ir_f']:
            pos = self.datas['up'] * self.PREVIEW_H + self.PREVIEW_TOTOP
            up_line = DragLine('', self, 'H')
            up_line.info = key + 'a'
            up_line.ypos = round((pos - self.PREVIEW_TOTOP + self.LINE_WEIGHT / 2) / float(self.PREVIEW_H), 3)
            up_line.setGeometry(self.PREVIEW_TOLEFT, pos, self.PREVIEW_W, self.LINE_WEIGHT)
            up_line.setStyleSheet('background-color:green;color:white;')
            pos = self.datas['right'] * self.PREVIEW_W + self.PREVIEW_TOLEFT
            right_line = DragLine('', self, 'V')
            right_line.info = key + '2'
            right_line.xpos = round((pos - self.PREVIEW_TOLEFT + self.LINE_WEIGHT / 2) / float(self.PREVIEW_W), 3)
            right_line.setGeometry(pos, self.PREVIEW_TOTOP, self.LINE_WEIGHT, self.PREVIEW_H)
            right_line.setStyleSheet('background-color:green;color:white;')
            pos = self.datas['down'] * self.PREVIEW_H + self.PREVIEW_TOTOP
            down_line = DragLine('', self, 'H')
            down_line.info = key + 'b'
            down_line.ypos = round((pos - self.PREVIEW_TOTOP + self.LINE_WEIGHT / 2) / float(self.PREVIEW_H), 3)
            down_line.setGeometry(self.PREVIEW_TOLEFT, pos, self.PREVIEW_W, self.LINE_WEIGHT)
            down_line.setStyleSheet('background-color:green;color:white;')
            pos = self.datas['left'] * self.PREVIEW_W + self.PREVIEW_TOLEFT
            left_line = DragLine('', self, 'V')
            left_line.info = key + '1'
            left_line.xpos = round((pos - self.PREVIEW_TOLEFT + self.LINE_WEIGHT / 2) / float(self.PREVIEW_W), 3)
            left_line.setGeometry(pos, self.PREVIEW_TOTOP, self.LINE_WEIGHT, self.PREVIEW_H)
            left_line.setStyleSheet('background-color:green;color:white;')
            self.green_lines.extend([up_line,
             right_line,
             down_line,
             left_line])

        if self.__linesArr:
            VLines = [ line for line in self.__linesArr if line['y'] == 0 ]
            HLines = [ line for line in self.__linesArr if line['x'] == 0 ]
            VLines.sort(cmp=lambda l1, l2: ord(l1['label']) > ord(l2['label']))
            HLines.sort(cmp=lambda l1, l2: ord(l1['label']) > ord(l2['label']))
            for line in VLines:
                for key in ['', 'ir']:
                    pos = line.get('x') * self.PREVIEW_W + self.PREVIEW_TOLEFT
                    dragline = DragLine('', self, 'V')
                    dragline.info = key + line['label']
                    dragline.xpos = round((pos - self.PREVIEW_TOLEFT + self.LINE_WEIGHT / 2) / float(self.PREVIEW_W), 3)
                    dragline.setGeometry(pos, self.PREVIEW_TOTOP, self.LINE_WEIGHT, self.PREVIEW_H)
                    dragline.setStyleSheet('background-color:red;color:white;')
                    self.__vDraglines.append(dragline)

            for line in HLines:
                for key in ['l',
                 'r',
                 'ir_l',
                 'ir_r']:
                    pos = line.get('y') * self.PREVIEW_H + self.PREVIEW_TOTOP
                    dragline = DragLine('', self, 'H')
                    dragline.info = key + line['label']
                    dragline.ypos = round((pos - self.PREVIEW_TOTOP + self.LINE_WEIGHT / 2) / float(self.PREVIEW_H), 3)
                    dragline.setGeometry(self.PREVIEW_TOLEFT, pos, self.PREVIEW_W, self.LINE_WEIGHT)
                    dragline.setStyleSheet('background-color:red;color:white;')
                    self.__hDraglines.append(dragline)

        self.display_red_lines(False)
        self.area_sp_Color.setStyleSheet('margin:0px 30px;background-color:rgb%s;' % str(glahf.gray_to_pseudo(0)))
        self.result_Label.setText(_translate('MainWindow', '\xe6\x99\xae\xe9\x80\x9a\xe5\x8c\xba\xe5\x9f\x9f\xe5\x80\xbc\xef\xbc\x9a\xe6\x9a\x82\xe6\x97\xa0', None))
        self.ir_area_sp_Color.setStyleSheet('margin:0px 30px;background-color:rgb%s;' % str(glahf.gray_to_pseudo(0)))
        self.ir_result_Label.setText(_translate('MainWindow', '\xe7\xba\xa2\xe5\xa4\x96\xe5\x8c\xba\xe5\x9f\x9f\xe5\x80\xbc\xef\xbc\x9a\xe6\x9a\x82\xe6\x97\xa0', None))
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def __closeline_callback(self, key):

        def deal_with_line(linesArr):
            __finded = False
            __last_key = None
            __deleted_line = None
            for line in linesArr:
                if __finded is True:
                    line.info = __last_key
                    line.setText(__last_key)
                    __last_key = chr(ord(__last_key) + 1)
                if line.info == key and __finded is False:
                    __finded = True
                    __last_key = key
                    __deleted_line = line
            else:
                if __deleted_line in linesArr:
                    linesArr.remove(__deleted_line)
                    return

        deal_with_line(self.__vDraglines)
        deal_with_line(self.__hDraglines)

    def set_paths(self, l_path, f_path, r_path):
        self.l_path = l_path
        self.f_path = f_path
        self.r_path = r_path

    def get_left_results(self):
        f = self.get_auto_grayvalue
        v_l1 = f('1', '2', 'la', 'lb', img=self.left_face)
        v_l2 = f('1', '2', 'lb', 'lc', img=self.left_face)
        v_l3 = f('1', '2', 'lc', 'ld', img=self.left_face)
        v_l4 = f('1', '2', 'ld', 'le', img=self.left_face)
        v_l5 = f('1', '2', 'le', 'lf', img=self.left_face)
        v_l6 = f('1', '2', 'lf', 'lg', img=self.left_face)
        v_ir_l1 = f('ir1', 'ir2', 'ir_la', 'ir_lb', img=self.left_ir_face)
        v_ir_l2 = f('ir1', 'ir2', 'ir_lb', 'ir_lc', img=self.left_ir_face)
        v_ir_l3 = f('ir1', 'ir2', 'ir_lc', 'ir_ld', img=self.left_ir_face)
        v_ir_l4 = f('ir1', 'ir2', 'ir_ld', 'ir_le', img=self.left_ir_face)
        v_ir_l5 = f('ir1', 'ir2', 'ir_le', 'ir_lf', img=self.left_ir_face)
        v_ir_l6 = f('ir1', 'ir2', 'ir_lf', 'ir_lg', img=self.left_ir_face)
        self.region.append(37, _region('1a', '2b', '左臂区', ''), gv=v_l1, ir_gv=v_ir_l1)
        self.region.append(38, _region('1b', '2c', '左肘区', ''), gv=v_l2, ir_gv=v_ir_l2)
        self.region.append(39, _region('1c', '2d', '左手区', ''), gv=v_l3, ir_gv=v_ir_l3)
        self.region.append(40, _region('1d', '2e', '左股(股骨关节)区', ''), gv=v_l4, ir_gv=v_ir_l4)
        self.region.append(41, _region('1e', '2f', '左膝(大腿)区', ''), gv=v_l5, ir_gv=v_ir_l5)
        self.region.append(42, _region('1f', '2g', '左胫区(小腿)区', ''), gv=v_l6, ir_gv=v_ir_l6)

    def get_right_results(self):
        f = self.get_auto_grayvalue
        v_r1 = f('3', '4', 'ra', 'rb', img=self.right_face)
        v_r2 = f('3', '4', 'rb', 'rc', img=self.right_face)
        v_r3 = f('3', '4', 'rc', 'rd', img=self.right_face)
        v_r4 = f('3', '4', 'rd', 're', img=self.right_face)
        v_r5 = f('3', '4', 're', 'rf', img=self.right_face)
        v_r6 = f('3', '4', 'rf', 'rg', img=self.right_face)
        v_ir_r1 = f('ir3', 'ir4', 'ir_ra', 'ir_rb', img=self.right_ir_face)
        v_ir_r2 = f('ir3', 'ir4', 'ir_rb', 'ir_rc', img=self.right_ir_face)
        v_ir_r3 = f('ir3', 'ir4', 'ir_rc', 'ir_rd', img=self.right_ir_face)
        v_ir_r4 = f('ir3', 'ir4', 'ir_rd', 'ir_re', img=self.right_ir_face)
        v_ir_r5 = f('ir3', 'ir4', 'ir_re', 'ir_rf', img=self.right_ir_face)
        v_ir_r6 = f('ir3', 'ir4', 'ir_rf', 'ir_rg', img=self.right_ir_face)
        self.region.append(43, _region('3a', '4b', '右臂区', ''), gv=v_r1, ir_gv=v_ir_r1)
        self.region.append(44, _region('3b', '4c', '右肘区', ''), gv=v_r2, ir_gv=v_ir_r2)
        self.region.append(45, _region('3c', '4d', '右手区', ''), gv=v_r3, ir_gv=v_ir_r3)
        self.region.append(46, _region('3d', '4e', '右股(股骨关节)区', ''), gv=v_r4, ir_gv=v_ir_r4)
        self.region.append(47, _region('3e', '4f', '右膝(大腿)区', ''), gv=v_r5, ir_gv=v_ir_r5)
        self.region.append(48, _region('3f', '4g', '右胫区(小腿)区', ''), gv=v_r6, ir_gv=v_ir_r6)

    def get_auto_results(self):
        f = self.get_auto_grayvalue
        self.v_left = f('1', '2', 'up', 'down', img=self.left_face, useskin=True)
        self.v_ir_left = f('ir1', 'ir2', 'up', 'down', img=self.left_ir_face)
        self.v_frontal = f('f1', 'f2', 'fa', 'fb', img=self.frontal_face, useskin=True)
        self.v_ir_frontal = f('ir_f1', 'ir_f2', 'ir_fa', 'ir_fb', img=self.frontal_ir_face)
        self.v_right = f('3', '4', 'up', 'down', img=self.right_face, useskin=True)
        self.v_ir_right = f('ir3', 'ir4', 'up', 'down', img=self.right_ir_face)
        all_gv = round((self.v_left + self.v_right + self.v_frontal) / 3, 2)
        all_ir_gv = round((self.v_ir_left + self.v_ir_right + self.v_ir_frontal) / 3, 2)
        self.all_gv, self.all_ir_gv = self.get_clb_gv(all_gv, all_ir_gv)
        self.get_left_results()
        self.get_right_results()
        self.area_avg_Color.setStyleSheet('margin:0px 30px;background-color:rgb%s;' % str(glahf.gray_to_pseudo(int(self.all_gv))))
        self.all_avg_Label.setText(_translate('MainWindow', '\xe6\x99\xae\xe9\x80\x9a\xe5\x9d\x87\xe5\x80\xbc\xef\xbc\x9a%s' % str(self.all_gv), None))
        self.ir_area_avg_Color.setStyleSheet('margin:0px 30px;background-color:rgb%s;' % str(glahf.gray_to_pseudo(int(self.all_ir_gv))))
        self.ir_all_avg_Label.setText(_translate('MainWindow', '\xe7\xba\xa2\xe5\xa4\x96\xe5\x9d\x87\xe5\x80\xbc\xef\xbc\x9a%s' % str(self.all_ir_gv), None))

    def get_auto_grayvalue(self, l_line, r_line, up_line, dn_line, img = None, useskin = False, skinMask = None):
        v_left = v_right = h_up = h_down = None
        for line in chain(self.__vDraglines, self.__hDraglines, self.green_lines):
            key = str(line)
            if key == l_line:
                v_left = line
            elif key == r_line:
                v_right = line
            if key == up_line:
                h_up = line
            elif key == dn_line:
                h_down = line

        start_x = v_left.xpos
        end_x = v_right.xpos
        if up_line == 'up':
            start_y = 0
        else:
            start_y = h_up.ypos
        if dn_line == 'down':
            end_y = 1
        else:
            end_y = h_down.ypos
        face = glahf.cut_img(img, start_x, end_x, start_y, end_y)
        if useskin:
            if skinMask is None:
                skin, skinMask = faceutil.skin(face)
            else:
                skin = faceutil.skin(face, skinMask=skinMask)
            gv = glahf.gray_value_filter(skin, 30, 220)
            gv = self.get_clb_gv(gv)
        else:
            gv = glahf.roi_grayvalue(face, start_x, end_x, start_y, end_y)
        if math.isnan(gv):
            gv = 0
        return round(gv, 2)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        dragline = e.source()
        position = e.pos()
        if position.x() < self.PREVIEW_TOLEFT:
            position.setX(self.PREVIEW_TOLEFT)
        elif position.x() > self.PREVIEW_W + self.PREVIEW_TOLEFT:
            position.setX(self.PREVIEW_W + self.PREVIEW_TOLEFT)
        if position.y() < self.PREVIEW_TOTOP:
            position.setY(self.PREVIEW_TOTOP)
        elif position.y() > self.PREVIEW_H + self.PREVIEW_TOTOP:
            position.setY(self.PREVIEW_H + self.PREVIEW_TOTOP)
        if dragline.TYPE == 'V':
            position.setY(self.PREVIEW_TOTOP)
            pos = (2 * position.x() + self.LINE_WEIGHT) / 2 - self.PREVIEW_TOLEFT
            dragline.xpos = pos / float(self.PREVIEW_W)
            if dragline.info == 'f1':
                self.datas['left'] = dragline.xpos
                self.save_vis(self.o_orig_img, self.o_ir_img)
                self.redraw_loc(80, 60)
                self.update_vis(False)
            elif dragline.info == 'f2':
                self.datas['right'] = dragline.xpos
                self.save_vis(self.o_orig_img, self.o_ir_img)
                self.redraw_loc(80, 60)
                self.update_vis(False)
            if dragline.info == 'ir_f1':
                self.datas['ir_left'] = dragline.xpos
                self.save_vis(self.o_orig_img, self.o_ir_img)
                self.redraw_loc(80, 60)
                self.update_vis(False)
            elif dragline.info == 'ir_f2':
                self.datas['ir_right'] = dragline.xpos
                self.save_vis(self.o_orig_img, self.o_ir_img)
                self.redraw_loc(80, 60)
                self.update_vis(False)
        elif dragline.TYPE == 'H':
            position.setX(self.PREVIEW_TOLEFT)
            pos = (2 * position.y() + self.LINE_WEIGHT) / 2 - self.PREVIEW_TOTOP
            dragline.ypos = pos / float(self.PREVIEW_H)
            if dragline.info in ('la', 'lg', 'ra', 'rg', 'ir_la', 'ir_lg', 'ir_ra', 'ir_rg'):
                index = dragline.info[:-1]
                start_idx = index + 'a'
                end_idx = index + 'g'
                start = self.__hDraglines.get(start_idx)
                end = self.__hDraglines.get(end_idx)
                offset = abs(end.ypos - start.ypos) / 6.0
                idx = 0
                for line in self.__hDraglines:
                    if line.info != dragline.info and line.info.startswith(index) and line.info not in (start_idx, end_idx):
                        idx += 1
                        line.ypos = start.ypos + idx * offset
                        line.move(self.PREVIEW_TOLEFT, line.ypos * self.PREVIEW_H + self.PREVIEW_TOTOP)

            if dragline.info == 'fa':
                self.datas['up'] = dragline.ypos
                self.save_vis(self.o_orig_img, self.o_ir_img)
                self.redraw_loc(80, 60)
                self.update_vis(False)
            elif dragline.info == 'fb':
                self.datas['down'] = dragline.ypos
                self.save_vis(self.o_orig_img, self.o_ir_img)
                self.redraw_loc(80, 60)
                self.update_vis(False)
            if dragline.info == 'ir_fa':
                self.datas['ir_up'] = dragline.ypos
                self.save_vis(self.o_orig_img, self.o_ir_img)
                self.redraw_loc(80, 60)
                self.update_vis(False)
            elif dragline.info == 'ir_fb':
                self.datas['ir_down'] = dragline.ypos
                self.save_vis(self.o_orig_img, self.o_ir_img)
                self.redraw_loc(80, 60)
                self.update_vis(False)
        else:
            return
        items = self.region.selectedItems()
        if items:
            self.region.onTableClicked(items[0])
        dragline.move(position)
        self.get_auto_results()
        self.get_regions_value()
        e.setDropAction(QtCore.Qt.MoveAction)
        e.accept()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate('MainWindow', '\xe7\x81\xb0\xe5\xba\xa6\xe5\x80\xbc\xe5\x88\x86\xe6\x9e\x90', None))
        self.preview.setText(_translate('MainWindow', '', None))
        self.position_text.setText(_translate('MainWindow', '\xe5\x9d\x90\xe6\xa0\x87\xe8\xbe\x93\xe5\x85\xa5', None))
        self.startpoint.setText(_translate('MainWindow', '\xe5\xbc\x80\xe5\xa7\x8b\xe5\x9d\x90\xe6\xa0\x87', None))
        self.endpoint.setText(_translate('MainWindow', '\xe7\xbb\x93\xe6\x9d\x9f\xe5\x9d\x90\xe6\xa0\x87', None))
        self.quit_btn.setText(_translate('MainWindow', '\xe8\xbf\x94\xe5\x9b\x9e', None))
        self.tip_text.setText(_translate('MainWindow', '', None))
        self.area_text.setStyleSheet('QLabel{margin-left:5%;}')
        self.nm_exp_text.setStyleSheet('QLabel{margin-left:5%;}')
        self.ir_exp_text.setStyleSheet('QLabel{margin-left:5%;}')
        self.result_Label.setStyleSheet('QLabel{margin-left:10%;}')
        self.ir_result_Label.setStyleSheet('QLabel{margin-left:10%;}')
        self.all_avg_Label.setStyleSheet('QLabel{margin-left:10%;}')
        self.ir_all_avg_Label.setStyleSheet('QLabel{margin-left:10%;}')

    @staticmethod
    def select_left(face):
        return glahf.cut_img(face, 0.0, 1 / 3.0, 0, 1)

    @staticmethod
    def select_frontal(face):
        return glahf.cut_img(face, 1 / 3.0, 2 / 3.0, 0, 1)

    @staticmethod
    def select_right(face):
        return glahf.cut_img(face, 2 / 3.0, 1.0, 0, 1)

    def choose_face(self, pos):
        d = {'left': 'self.left_face',
         'frontal': 'self.frontal_face',
         'right': 'self.right_face',
         'ir_left': 'self.left_ir_face',
         'ir_frontal': 'self.frontal_ir_face',
         'ir_right': 'self.right_ir_face'}

        def _choose():
            face = eval(d[pos])
            if pos.startswith('ir'):
                self.mode = 'IR'
            else:
                self.mode = 'NORMAL'
            if 'left' == pos:
                self.display_red_lines(True)
                self.display_green_lines(False)
                for line in self.__vDraglines:
                    line.hide()

                self.__vDraglines.get('1').show()
                self.__vDraglines.get('2').show()
                for line in self.__hDraglines:
                    if line.info.startswith('l'):
                        line.show()
                    else:
                        line.hide()

            elif 'ir_left' == pos:
                self.display_red_lines(True)
                self.display_green_lines(False)
                for line in self.__vDraglines:
                    line.hide()

                self.__vDraglines.get('ir1').show()
                self.__vDraglines.get('ir2').show()
                for line in self.__hDraglines:
                    if line.info.startswith('ir_l'):
                        line.show()
                    else:
                        line.hide()

            elif 'right' == pos:
                self.display_red_lines(True)
                self.display_green_lines(False)
                for line in self.__vDraglines:
                    line.hide()

                self.__vDraglines.get('3').show()
                self.__vDraglines.get('4').show()
                for line in self.__hDraglines:
                    if line.info.startswith('r'):
                        line.show()
                    else:
                        line.hide()

            elif 'ir_right' == pos:
                self.display_red_lines(True)
                self.display_green_lines(False)
                for line in self.__vDraglines:
                    line.hide()

                self.__vDraglines.get('ir3').show()
                self.__vDraglines.get('ir4').show()
                for line in self.__hDraglines:
                    if line.info.startswith('ir_r'):
                        line.show()
                    else:
                        line.hide()

            else:
                if 'frontal' == pos:
                    for line in self.green_lines:
                        if line.info.startswith('f'):
                            line.show()
                        else:
                            line.hide()

                elif 'ir_frontal' == pos:
                    for line in self.green_lines:
                        if line.info.startswith('ir_f'):
                            line.show()
                        else:
                            line.hide()

                self.display_red_lines(False)
            self.face_now = face
            self.active_gray_img = glahf.convert(face)
            if not 'ir_frontal' == pos:
                self.save_vis(face, None, pos)
                self.preview.setPixmap(QtGui.QPixmap('' + LINE_TEMP_PATH))
            else:
                self.save_vis(None, face)
                self.preview.setPixmap(QtGui.QPixmap('' + LINE_TEMP_IR_PATH))

        return _choose

    def set_preview(self, data):
        logging.info('\xe5\xbc\x80\xe5\xa7\x8b\xe6\x9b\xb4\xe6\x96\xb0\xe9\xa2\x84\xe8\xa7\x88\xe7\xaa\x97\xe5\x8f\xa3...')
        self.init_data = data
        self.startpoint_input.setPlaceholderText('1L2')
        self.endpoint_input.setPlaceholderText('3R2')
        self.img_path = data.get('path', None)
        self.ir_gray_img_path = data.get('ir_path', None)
        self.orig_img = glahf.read(self.img_path)
        self.ir_img = glahf.read(self.ir_gray_img_path)
        self.left_face = self.select_left(self.orig_img)
        self.frontal_face = self.select_frontal(self.orig_img)
        self.right_face = self.select_right(self.orig_img)
        self.left_ir_face = self.select_left(self.ir_img)
        self.frontal_ir_face = self.select_frontal(self.ir_img)
        self.right_ir_face = self.select_right(self.ir_img)
        self.face_now = self.frontal_face
        self.orig_img = self.frontal_face
        self.ir_img = self.frontal_ir_face
        self.o_orig_img = self.orig_img.copy()
        self.o_ir_img = self.ir_img.copy()
        self.orig_gray_img = glahf.convert(self.orig_img)
        self.ir_gray_img = glahf.convert(self.ir_img)
        self.save_vis(self.orig_img, self.ir_img)
        self.active_gray_img = self.orig_gray_img
        self.mode = 'NORMAL'
        self.qt_face = QtGui.QPixmap('' + LINE_TEMP_PATH)
        self.qt_ir_face = QtGui.QPixmap('' + LINE_TEMP_IR_PATH)
        self.preview.setPixmap(self.qt_face)
        if self.clb_status is True:
            clb = util.clb_array()
            self.clb_gv, self.clb_os = self.get_clb()
            logging.info(u'\u5b9a\u6807\u767d\u677f\u7684\u7070\u5ea6\u503c\u4e3a\uff1a{clb_gv}\uff0c\u5bf9\u5e94\u7684\u8bef\u5dee\u503c\u4e3a\uff1a{clb_os}'.format(clb_gv=round(self.clb_gv, 2), clb_os=round(self.clb_os, 2)))
        self.get_auto_results()
        self.get_regions_value()
        self.choose_face('frontal')()
        self.retrieve()

    def redraw_loc(self, H, V):
        for p in self._loc:
            p.close()
            p = None

        self._loc = []
        self.MAP = [ 'R%s' % str(num) for num in xrange(40, 0, -1) ]
        extras = [ 'L%s' % str(num) for num in xrange(1, 41) ]
        self.MAP.append(' 0')
        self.MAP.extend(extras)
        font = QtGui.QFont()
        try:
            font.setFamily(_fromUtf8('Microsoft YaHei'))
        except Exception as e:
            font.setFamily(_fromUtf8('Arial'))

        font.setPointSize(6)
        hoffset, voffset = self.preview.get_offset()
        vbegin = self.datas['up'] * self.PREVIEW_H
        hbegin = self.datas['left'] * self.PREVIEW_W
        for i in xrange(0, V + 1):
            if i % 2 == 0:
                continue
            label = LocationLabel()
            label.set_parent(self)
            label.style = 'y'
            label.setFont(font)
            label.setGeometry(QtCore.QRect(self.PREVIEW_TOLEFT - 25, vbegin + self.PREVIEW_TOTOP + i * voffset, 15, 10))
            label.setText(str(i))
            self.layout().addWidget(label)
            self._loc.append(label)
        else:
            self.X_VAXIS = str(i)

        for i in xrange(0, H + 1):
            if i % 2 == 0 and str(self.MAP[i]) != ' 0':
                continue
            label = LocationLabel()
            label.set_parent(self)
            label.style = 'x'
            label.setFont(font)
            label.setGeometry(QtCore.QRect(hbegin + self.PREVIEW_TOLEFT + i * hoffset, self.PREVIEW_TOTOP - 20, 15, 15))
            text = str(self.MAP[i])
            label.setText(text[1:])
            self.layout().addWidget(label)
            self._loc.append(label)
        else:
            self.X_HAXIS = str(self.MAP[i])

        self.preview.set_offset()

    def save_vis(self, orig_img, ir_img, pos = 'frontal'):
        try:
            if pos.endswith('frontal'):
                if orig_img is not None:
                    glahf.write(LINE_TEMP_PATH, glahf.drawlines(orig_img, 80, 60, datas=self.datas, px=1, img_type='nm'))
                if ir_img is not None:
                    glahf.write(LINE_TEMP_IR_PATH, glahf.drawlines(ir_img, 80, 60, datas=self.datas, px=1, img_type='ir'))
            else:
                if orig_img is not None:
                    glahf.write(LINE_TEMP_PATH, orig_img)
                if ir_img is not None:
                    glahf.write(LINE_TEMP_IR_PATH, ir_img)
        except IOError as e:
            pass

    def show_match_vis(self):
        height, width = self.orig_gray_img.shape[:2]
        img = self.frontal_face
        faceutil.show_detection(img)

    def show_skin(self):
        skin_img, _ = faceutil.skin(self.face_now)
        skin_img = glahf.resize(skin_img, int(self.PREVIEW_H), int(self.PREVIEW_W))
        glahf.show(skin_img)

    def update_base_lines(self, widget):

        def _op():
            if widget == self.red_v_line_btn:
                self.config['vposcount'] -= 1
            elif widget == self.add_h_line_btn:
                self.config['hposcount'] += 1
            elif widget == self.add_v_line_btn:
                self.config['vposcount'] += 1
            elif widget == self.red_h_line_btn:
                self.config['hposcount'] -= 1
            else:
                raise AssertionError()
            self.redraw_loc(80, 60)
            self.save_vis(self.o_orig_img, self.o_ir_img)
            self.update_vis(switch=False)

        return _op

    def display_green_lines(self, option):
        if option == True:
            for line in self.green_lines:
                line.show()

        elif option == False:
            for line in self.green_lines:
                line.hide()

    def display_red_lines(self, option):
        if option == True:
            for line in chain(self.__hDraglines, self.__vDraglines):
                line.show()

        elif option == False:
            for line in chain(self.__hDraglines, self.__vDraglines):
                line.hide()

    def toggle_lines(self):
        d = {'show': True}

        def _toggle_lines():
            if d['show'] == False:
                self.display_red_lines(True)
                self.hide_lines_btn.setText(_translate('MainWindow', '\xe9\x9a\x90\xe8\x97\x8f\xe7\xba\xa2\xe7\xba\xbf', None))
                d['show'] = True
            elif d['show'] == True or option == False:
                self.display_red_lines(False)
                self.hide_lines_btn.setText(_translate('MainWindow', '\xe6\x98\xbe\xe7\xa4\xba\xe7\xba\xa2\xe7\xba\xbf', None))
                d['show'] = False

        return _toggle_lines

    def toggle_advance(self):
        d = {'show': True}

        def _toggle_advance():
            if d['show'] == False:
                for comp in self.advances:
                    comp.show()

                d['show'] = True
            else:
                for comp in self.advances:
                    comp.hide()

                d['show'] = False

        return _toggle_advance

    def do_offset(self):
        if not (glahf.array_equal(self.face_now, self.frontal_face) or glahf.array_equal(self.face_now, self.frontal_ir_face)):
            util.warn_dialog(text='\xe5\x8f\xaa\xe6\x9c\x89\xe6\xad\xa3\xe8\x84\xb8\xe5\x8f\xaf\xe4\xbb\xa5\xe7\xa7\xbb\xe5\x8a\xa8')
            return False
        x_offset = self.pos_left_click_num - self.pos_right_click_num
        y_offset = self.pos_up_click_num - self.pos_down_click_num
        self.o_orig_img = faceutil.get_offset_img(self.orig_img, x_offset=x_offset, y_offset=y_offset)
        self.o_ir_img = faceutil.get_offset_img(self.ir_img, x_offset=x_offset, y_offset=y_offset)
        self.orig_gray_img = glahf.convert(self.o_orig_img)
        self.ir_gray_img = glahf.convert(self.o_ir_img)
        self.active_gray_img = self.orig_gray_img
        self.save_vis(self.o_orig_img, self.o_ir_img)
        self.update_vis(switch=False)
        self.get_regions_value()
        return True

    def l_offset(self):
        self.pos_left_click_num += 1
        if self.do_offset() is False:
            self.pos_left_click_num -= 1

    def u_offset(self):
        self.pos_up_click_num += 1
        if self.do_offset() is False:
            self.pos_up_click_num -= 1

    def r_offset(self):
        self.pos_right_click_num += 1
        if self.do_offset() is False:
            self.pos_right_click_num -= 1

    def d_offset(self):
        self.pos_down_click_num += 1
        if self.do_offset() is False:
            self.pos_down_click_num -= 1

    def handle_input(self, string):
        if string.isdigit() is True:
            l_index = string[:-1]
            r_index = self.MAP.index(' 0')
        else:
            l_index = re.split('[LR]', string)[0]
            r_index = self.MAP.index(string.replace(l_index, '', 1))
        if l_index == '' or r_index == '':
            raise ValueError()
        return (str(r_index), str(l_index))

    def get_region_value(self, start=None, end=None):
        if start is None or end is None:
            return None
        startpoint = self.handle_input(start)
        endpoint = self.handle_input(end)
        _, gv = faceutil.get_avg_gray_value(self.orig_gray_img, startpoint, endpoint, config=self.config, datas=self.datas, img_type='nm')
        _, ir_gv = faceutil.get_avg_gray_value(self.ir_gray_img, startpoint, endpoint, config=self.config, datas=self.datas, img_type='ir')
        gv, ir_gv = self.get_clb_gv(gv, ir_gv)
        if math.isnan(gv):
            gv = 0
        if math.isnan(ir_gv):
            ir_gv = 0
        gv_color = glahf.gray_to_pseudo(int(gv))
        ir_gv_color = glahf.gray_to_pseudo(int(ir_gv))
        return [round(gv, 2), gv_color, round(ir_gv, 2), ir_gv_color]

    def get_regions_value(self):
        for index, (key, region) in enumerate(FACE_REGION.items()):
            try:
                startpoint = self.handle_input(region.start)
                endpoint = self.handle_input(region.end)
            except (ValueError, KeyError):
                import traceback
                traceback.print_exc()
                continue

            _, gv = faceutil.get_avg_gray_value(self.orig_gray_img, startpoint, endpoint, config=self.config, datas=self.datas, img_type='nm')
            _, ir_gv = faceutil.get_avg_gray_value(self.ir_gray_img, startpoint, endpoint, config=self.config, datas=self.datas, img_type='ir')
            gv, ir_gv = self.get_clb_gv(gv, ir_gv)
            self.region.append(index, region, gv=round(gv, 2), ir_gv=round(ir_gv, 2))

    def retrieve(self, starttext = None, endtext = None, output = True):
        if not (glahf.array_equal(self.face_now, self.frontal_face) or glahf.array_equal(self.face_now, self.frontal_ir_face)):
            util.warn_dialog(text='\xe5\x8f\xaa\xe6\x9c\x89\xe6\xad\xa3\xe8\x84\xb8\xe5\x8f\xaf\xe4\xbb\xa5\xe6\xa3\x80\xe6\xb5\x8b')
            return
        if starttext is None and endtext is None:
            starttext = unicode(self.startpoint_input.text()).upper()
            endtext = unicode(self.endpoint_input.text()).upper()
            if not starttext and not endtext:
                return
        try:
            startpoint = self.handle_input(starttext)
            endpoint = self.handle_input(endtext)
        except (ValueError, KeyError):
            tip = '输入格式有误,格式:[纵坐标+横坐标],如5L2,28R3'
            self.tip_text.setText(_translate('MainWindow', tip, None))
            return

        if int(startpoint[0]) < int(endpoint[0]) <= int(self.config['hposcount']) and int(startpoint[1]) < int(endpoint[1]) <= int(self.config['vposcount']):
            pass
        else:
            tip = '\xe8\xaf\xb7\xe8\xbe\x93\xe5\x85\xa5\xe5\x90\x88\xe7\x90\x86\xe8\x8c\x83\xe5\x9b\xb4,\xe6\xa8\xaa\xe5\x9d\x90\xe6\xa0\x87(L20~R20),\xe7\xba\xb5\xe5\x9d\x90\xe6\xa0\x87(0~60)'
            self.tip_text.setText(_translate('MainWindow', tip, None))
            return
        self.spliced_img, gv = faceutil.get_avg_gray_value(self.orig_gray_img, startpoint, endpoint, config=self.config, datas=self.datas, img_type='nm')
        _, ir_gv = faceutil.get_avg_gray_value(self.ir_gray_img, startpoint, endpoint, config=self.config, datas=self.datas, img_type='ir')
        gv, ir_gv = self.get_clb_gv(gv, ir_gv)
        if output:
            self.result_Label.setText(_translate('MainWindow', '\xe5\x8c\xba\xe5\x9f\x9f\xe7\x81\xb0\xe5\xba\xa6\xe5\x80\xbc\xef\xbc\x9a%s' % str(gv), None))
            self.area_sp_Color.setStyleSheet('margin:0px 30px;background-color:rgb%s;' % str(glahf.gray_to_pseudo(int(gv))))
            self.result_Label.setStyleSheet('text-align:center;')
            self.ir_result_Label.setText(_translate('MainWindow', '\xe7\xba\xa2\xe5\xa4\x96\xe7\x81\xb0\xe5\xba\xa6\xe5\x80\xbc\xef\xbc\x9a%s' % str(ir_gv), None))
            self.ir_area_sp_Color.setStyleSheet('margin:0px 30px;background-color:rgb%s;' % str(glahf.gray_to_pseudo(int(ir_gv))))
            self.ir_result_Label.setStyleSheet('text-align:center;')
            self.tip_text.setText('')
            self.area_text.setText('')
            self.nm_exp_text.setText('')
            self.ir_exp_text.setText('')
        return (round(gv, 2), round(ir_gv, 2))

    def update_vis(self, switch = True):
        if self.mode == 'NORMAL':
            if switch:
                self.mode = 'IR'
                self.active_gray_img = self.ir_gray_img
                self.preview.setPixmap(QtGui.QPixmap('' + LINE_TEMP_IR_PATH))
            else:
                self.preview.setPixmap(QtGui.QPixmap('' + LINE_TEMP_PATH))
            self.get_auto_results()
            self.retrieve()
        elif self.mode == 'IR':
            if switch:
                self.mode = 'NORMAL'
                self.active_gray_img = self.orig_gray_img
                self.preview.setPixmap(QtGui.QPixmap('' + LINE_TEMP_PATH))
            else:
                self.preview.setPixmap(QtGui.QPixmap('' + LINE_TEMP_IR_PATH))
            self.get_auto_results()
            self.retrieve()
        else:
            raise AssertionError()

    def get_analyse(self):
        if self.spliced_img is not None:
            faceutil.showplt(self.spliced_img)

    def return_to(self):
        self.datas = None
        self.close()
        self = None

    def reset(self):
        new_window = AnalyseWindow(datas=self.reset_datas, config=self.config, info=self.info)
        new_window.set_paths(self.l_path, self.f_path, self.r_path)
        new_window.set_preview(self.init_data)
        new_window.show()
        self.return_to()

    def show_log(self):
        col_str = "<font color='{color}'>{text}</font>"
        text = []
        with open('log.txt', 'r') as f:
            for line in f:
                if line.find('INFO') != -1:
                    text.append(col_str.format(color='green', text=line))
                elif line.find('ERROR') != -1:
                    text.append(col_str.format(color='red', text=line))
                elif line.find('WARNING') != -1:
                    text.append(col_str.format(color='#CD9B1D', text=line))

        log = '<br>'.join(text) or ''
        util.about_dialog(window='AnalyseWindow', title='Log', text=log)

    def get_clb(self):
        clb_arr = util.clb_array()
        if clb_arr:
            if clb_arr['start_x'] == 0 and clb_arr['end_x'] == 0 and clb_arr['start_y'] == 0 and clb_arr['end_y'] == 0:
                return (255, 0)
            height, width = self.frontal_face.shape[:2]
            s_x = int(clb_arr['start_x'] * width)
            e_x = int(clb_arr['end_x'] * width)
            s_y = int(clb_arr['start_y'] * height)
            e_y = int(clb_arr['end_y'] * height)
            clb_area = self.frontal_face[s_y:e_y, s_x:e_x]
            clb_gv = glahf.gray_value(clb_area)
            clb_os = 255 - clb_gv
            if clb_os < 0 or clb_os > 255:
                return (255, 0)
            return (clb_gv, clb_os)
        return (255, 0)

    def get_clb_gv(self, gv, ir_gv = None):
        if self.clb_status is True:
            gv += self.clb_os
            if gv > 255:
                gv = 255
            if ir_gv is not None:
                ir_gv += self.clb_os
                if ir_gv > 255:
                    ir_gv = 255
                return (round(gv, 2), round(ir_gv, 2))
            return round(gv, 2)
        if ir_gv is None:
            return round(gv, 2)
        return (round(gv, 2), round(ir_gv, 2))

    def toggle_clb(self):
        d = {'status': False}

        def _toggle_clb():
            if d['status'] is False:
                util.about_dialog(self, window='AnalyseWindow', title='\xe6\xb6\x88\xe6\x81\xaf', text='\xe8\xaf\xb7\xe6\x8b\x96\xe6\x8b\xbd\xe9\xbc\xa0\xe6\xa0\x87\xe9\x80\x89\xe6\x8b\xa9\xe5\xae\x9a\xe6\xa0\x87\xe5\x8c\xba\xe5\x9f\x9f\xef\xbc\x8c\xe6\x8c\x89esc\xe6\x88\x96q\xe9\x80\x80\xe5\x87\xba')
                position = []
                img = self.active_gray_img
                calibration = clb.Calibration(img=img.copy())
                position = calibration.get_position()
                calibration = None
                if position:
                    with open(CLB_FILE, 'wb') as fp:
                        json.dump(position, fp, indent=4)
                else:
                    util.about_dialog(self, window='AnalyseWindow', title='\xe6\xb6\x88\xe6\x81\xaf', text='\xe4\xbf\xae\xe6\x94\xb9\xe5\xa4\xb1\xe8\xb4\xa5\xef\xbc\x8c\xe8\xaf\xb7\xe9\x87\x8d\xe8\xaf\x95')
                self.clb_gv, self.clb_os = self.get_clb()
                logging.info(u'\u66f4\u65b0\u5b9a\u6807\u767d\u677f\uff0c\u5f53\u524d\u767d\u677f\u7070\u5ea6\u503c\u4e3a\uff1a{clb_gv}\uff0c\u5bf9\u5e94\u7684\u8bef\u5dee\u503c\u4e3a\uff1a{clb_os}'.format(clb_gv=round(self.clb_gv, 2), clb_os=round(self.clb_os, 2)))
                self.clb_status = True
                try:
                    self.get_auto_results()
                    self.get_regions_value()
                finally:
                    self.toggle_clb_btn.setText(_translate('AnalyseWindow', '\xe5\x85\xb3\xe9\x97\xad\xe7\x99\xbd\xe6\x9d\xbf', None))
                    d['status'] = True

            else:
                self.clb_gv, self.clb_os = (255, 0)
                self.clb_status = False
                try:
                    self.get_auto_results()
                    self.get_regions_value()
                finally:
                    self.toggle_clb_btn.setText(_translate('AnalyseWindow', '\xe6\x89\x93\xe5\xbc\x80\xe7\x99\xbd\xe6\x9d\xbf', None))
                    d['status'] = False

        return _toggle_clb

    def export_report(self):
        screen_height, screen_width = util.screen_size()
        self.save_vis(self.o_orig_img, self.o_ir_img)
        self.qt_face = QtGui.QPixmap('' + LINE_TEMP_PATH)
        self.qt_ir_face = QtGui.QPixmap('' + LINE_TEMP_IR_PATH)
        exps = self.region.get_exp_areas()
        ir_exps = self.region.get_ir_exp_areas()
        exps_list = []
        ir_exps_list = []
        for exp in exps[0]:
            exps_list.append(u'<li>%s: 比平均值低%.2f</li>' % (exp[0], abs(exp[1])))
        for exp in exps[1]:
            exps_list.append(u'<li>%s: 比平均值高%.2f</li>' % (exp[0], abs(exp[1])))

        for exp in ir_exps[0]:
            exps_list.append(u'<li>%s: 比平均值低%.2f</li>' % (exp[0], abs(exp[1])))

        for exp in ir_exps[1]:
            ir_exps_list.append(u'<li>%s: 比平均值高%.2f</li>' % (exp[0], abs(exp[1])))

        grid_list = []
        for idx, r in enumerate(self.region.region_list):
            grid_list.append('''
                <tr>
                    <td style="padding-right:10px;padding-left:10px;">{index}</td>
                    <td style="padding-right:10px;padding-left:10px;">{intro}</td>
                    <td style="padding-right:10px;padding-left:10px;">{nm_gv}</td>
                    <td style="background-color: rgb{nm_color}"></td>
                    <td style="padding-right:10px;padding-left:10px;">{avg_gv}</td>
                    <td style="background-color: rgb{avg_color}"></td>
                    <td style="padding-right:10px;padding-left:10px;">{nm_cz}</td>
                    <td style="padding-right:10px;padding-left:10px;">{ir_gv}</td>
                    <td style="background-color: rgb{ir_color}"></td>
                    <td style="padding-right:10px;padding-left:10px;">{avg_ir_gv}</td>
                    <td style="background-color: rgb{avg_ir_color}"></td>
                    <td style="padding-right:10px;padding-left:10px;">{ir_cz}</td>
                </tr>
                '''.format(index=str(idx + 1), 
                    intro=r[0], 
                    nm_gv=str(r[1]), 
                    nm_color=r[2], 
                    avg_gv=str(r[3]), 
                    avg_color=r[4], 
                    nm_cz=r[5], 
                    ir_gv=r[6], 
                    ir_color=r[7], 
                    avg_ir_gv=r[8], 
                    avg_ir_color=r[9], 
                    ir_cz=r[10]
                )
            )
        
        f = self.get_auto_grayvalue
        v_l31 = f('1', '2', 'la', 'lb', img=self.left_face)
        v_l32 = f('1', '2', 'lb', 'lc', img=self.left_face)
        v_l33 = f('1', '2', 'lc', 'ld', img=self.left_face)
        v_l34 = f('1', '2', 'ld', 'le', img=self.left_face)
        v_l35 = f('1', '2', 'le', 'lf', img=self.left_face)
        v_l36 = f('1', '2', 'lf', 'lg', img=self.left_face)
        v_ir_l31 = f('ir1', 'ir2', 'ir_la', 'ir_lb', img=self.left_ir_face)
        v_ir_l32 = f('ir1', 'ir2', 'ir_lb', 'ir_lc', img=self.left_ir_face)
        v_ir_l33 = f('ir1', 'ir2', 'ir_lc', 'ir_ld', img=self.left_ir_face)
        v_ir_l34 = f('ir1', 'ir2', 'ir_ld', 'ir_le', img=self.left_ir_face)
        v_ir_l35 = f('ir1', 'ir2', 'ir_le', 'ir_lf', img=self.left_ir_face)
        v_ir_l36 = f('ir1', 'ir2', 'ir_lf', 'ir_lg', img=self.left_ir_face)
        v_r31 = f('3', '4', 'ra', 'rb', img=self.right_face)
        v_r32 = f('3', '4', 'rb', 'rc', img=self.right_face)
        v_r33 = f('3', '4', 'rc', 'rd', img=self.right_face)
        v_r34 = f('3', '4', 'rd', 're', img=self.right_face)
        v_r35 = f('3', '4', 're', 'rf', img=self.right_face)
        v_r36 = f('3', '4', 'rf', 'rg', img=self.right_face)
        v_ir_r31 = f('ir3', 'ir4', 'ir_ra', 'ir_rb', img=self.right_ir_face)
        v_ir_r32 = f('ir3', 'ir4', 'ir_rb', 'ir_rc', img=self.right_ir_face)
        v_ir_r33 = f('ir3', 'ir4', 'ir_rc', 'ir_rd', img=self.right_ir_face)
        v_ir_r34 = f('ir3', 'ir4', 'ir_rd', 'ir_re', img=self.right_ir_face)
        v_ir_r35 = f('ir3', 'ir4', 'ir_re', 'ir_rf', img=self.right_ir_face)
        v_ir_r36 = f('ir3', 'ir4', 'ir_rf', 'ir_rg', img=self.right_ir_face)
        sec_grid_list = []
        values = [
         [self.get_region_value('1R2', '8L2') + ['中1', '1R2,8L2'], #
         self.get_region_value('8R2', '15L2') + ['中2', '8R2,15L2'], #中2
         self.get_region_value('15R2', '18L2') + ['中3', '15R2,18L2'], #中3
         self.get_region_value('18R2', '22L2') + ['中4', '18R2,22L2'], #中4
         self.get_region_value('22R3', '26L3') + ['中5', '22R3,26L3'], #中5
         self.get_region_value('26R4', '29L4') + ['中6', '26R4,29L4'], #中6
         self.get_region_value('29R2', '32L2') + ['中7', '29R2,32L2'], #中7
         self.get_region_value('29R5', '32R2') + ['中8', '29R5,32R2'], #中8
         self.get_region_value('29L2', '32L5') + ['中9', '29L2,32L5 '], #中9
         self.get_region_value('32R6', '35L6') + ['中10', '32R6,35L6'], #中10
         self.get_region_value('35R8', '37L8') + ['中11', '35R8,37L8']
         ], #中11
         [self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value('15L2', '22L8') + ['左11', '15L2,22L8'], #左11
         self.get_region_value('22L3', '26L8') + ['左12', '22L3,26L8'], #左12
         self.get_region_value('26L4', '29L14') + ['左13', '26L4,29L14'], #左13
         self.get_region_value('29L5', '32L14') + ['左14', '29L5,32L14'], #左14
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value('32L6', '35L14') + ['左15', '32L6,35L14'], #左15
         self.get_region_value('35L8', '37L14') + ['左16', '35L8,37L14'], #左16
         self.get_region_value('37L8', '43L14') + ['左17', '37L8,43L14'],
         ], #左17
         [self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value('15R8', '22R2') + ['右11', '15R8,22R2'], #右11
         self.get_region_value('22R8', '26R3') + ['右12', '22R8,26R3'], #右12
         self.get_region_value('26R14', '29R4') + ['右13', '26R14,29R4'], #右13
         self.get_region_value('29R14', '29R4') + ['右14', '29R14,32L5'], #右14
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value('32R14', '35R6') + ['右15', '32R14,35R6'], #右15
         self.get_region_value('35R14', '37R8') + ['右16', '35R14,37R8'], #右16
         self.get_region_value('37R14', '43R8') + ['右17', '37R14,43R8']
         ], #右17
         [self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value('26L14', '30L20') + ['左21', '26L14,30L20'], #左21
         self.get_region_value('30L14', '34L20') + ['左22', '30L14,34L20'], #左22
         self.get_region_value(), #?
         self.get_region_value('34L14', '38L20') + ['左23', '34L14,38L20'], #左23
         self.get_region_value(), #?
         self.get_region_value('38L14', '42L20') + ['左24', '38L14,42L20'], #左24
         self.get_region_value('42L14', '46L20') + ['左25', '42L14,46L20'], #左25
         self.get_region_value('46L14', '50L20') + ['左25', '46L14,50L20']
         ], #左26
         [self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value('26R20', '30R14') + ['右21', '26R20,30R14'], #右21
         self.get_region_value('30R20', '34R14') + ['右22', '30R20,34R14'], #右22
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value('34R20', '38R14') + ['右23', '34R20,38R14'], #右23
         self.get_region_value('38R20', '42R14') + ['右24', '38R20,42R14'], #右24
         self.get_region_value('42R20', '46R14') + ['右25', '42R20,46R14'], #右25
         self.get_region_value('46R20', '50R14') + ['右26', '46R20,50R14']
         ], #右26
         [self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         (
            v_l31,
            glahf.gray_to_pseudo(int(v_l31)),
            v_ir_l31,
            glahf.gray_to_pseudo(int(v_ir_l31)),
            '左31',
            '26L20,30L38'
         ), #左31
         (
            v_l32,
            glahf.gray_to_pseudo(int(v_l32)),
            v_ir_l32,
            glahf.gray_to_pseudo(int(v_ir_l32)),
            '左32',
            '30L20,34L38'
         ), #左32
         self.get_region_value(), #?
         self.get_region_value(), #?
         (
            v_l33,
            glahf.gray_to_pseudo(int(v_l33)),
            v_ir_l33,
            glahf.gray_to_pseudo(int(v_ir_l33)),
            '左33',
            '34L20,38L38'
         ), #左33
         (
            v_l34,
            glahf.gray_to_pseudo(int(v_l34)),
            v_ir_l34,
            glahf.gray_to_pseudo(int(v_ir_l34)),
            '左34',
            '38L20,42L38'
         ), #左34
         (
            v_l35,
            glahf.gray_to_pseudo(int(v_l35)),
            v_ir_l35,
            glahf.gray_to_pseudo(int(v_ir_l35)),
            '左35',
            '42L20,46L38'
         ), #左35
         (
            v_l36,
            glahf.gray_to_pseudo(int(v_l36)),
            v_ir_l36,
            glahf.gray_to_pseudo(int(v_ir_l36)),
            '左36',
            '46L20,50L38'
         ) #左36
         ], #左36
         [self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         self.get_region_value(), #?
         (
            v_r31,
            glahf.gray_to_pseudo(int(v_r31)),
            v_ir_r31,
            glahf.gray_to_pseudo(int(v_ir_r31)),
            '右31',
            '26R38,30R20'
         ), #右31
         (
            v_r32,
            glahf.gray_to_pseudo(int(v_r32)),
            v_ir_r32,
            glahf.gray_to_pseudo(int(v_ir_r32)),
            '右32',
            '30R38,34R20'
         ), #右32
         self.get_region_value(), #?
         self.get_region_value(), #?
         (
            v_r33,
            glahf.gray_to_pseudo(int(v_r33)),
            v_ir_r33,
            glahf.gray_to_pseudo(int(v_ir_r33)),
            '右33',
            '34R38,38R20'
         ), #右33
         (
            v_r34,
            glahf.gray_to_pseudo(int(v_r34)),
            v_ir_r34,
            glahf.gray_to_pseudo(int(v_ir_r34)),
            '右34',
            '38R38,42R20'
         ), #右34
         (
            v_r35,
            glahf.gray_to_pseudo(int(v_r35)),
            v_ir_r35,
            glahf.gray_to_pseudo(int(v_ir_r35)),
            '右35',
            '42R38,46R20'
         ), #右35
         (
            v_r36,
            glahf.gray_to_pseudo(int(v_r36)),
            v_ir_r36,
            glahf.gray_to_pseudo(int(v_ir_r36)),
            '右36',
            '46R38,50R20'
         ) #右36
         ]
        ] #右36
        for row in values:
            sec_grid_list.append('<tr>')
            for data in row:
                if data is None:
                    sec_grid_list.append('<td></td>')
                else:    
                    sec_grid_list.append(
                        '<td style="background-color: rgb{nm_color}"></td>'.format(nm_color=str(data[1]))
                    )
            sec_grid_list.append('</tr>')
            sec_grid_list.append('<tr>')
            for data in row:
                if data is None:
                    sec_grid_list.append('<td></td>')
                else:
                    sec_grid_list.append(
                        '<td>{pos}</td>'.format(pos=data[4])
                    )
            sec_grid_list.append('</tr>')
            sec_grid_list.append('<tr>')
            for data in row:
                if data is None:
                    sec_grid_list.append('<td></td>')
                else:
                    sec_grid_list.append(
                        '<td style="background-color: rgb{ir_color}"></td>'.format(ir_color=str(data[3]))
                    )
            sec_grid_list.append('</tr>')
            sec_grid_list.append('<tr>')
            for data in row:
                if data is None:
                    sec_grid_list.append('<td></td>')
                else:
                    sec_grid_list.append(
                        '<td>{index}</td>'.format(index=data[5])
                    )
            sec_grid_list.append('</tr>')

        for row in values:
            sec_grid_list.append('<tr>')
            for data in row:
                if data is None:
                    sec_grid_list.append('<td></td>')
                else:    
                    sec_grid_list.append(
                        '<td>{gv}</td>'.format(gv=data[0])
                    )
            sec_grid_list.append('</tr>')
            sec_grid_list.append('<tr>')
            for data in row:
                if data is None:
                    sec_grid_list.append('<td></td>')
                else:
                    sec_grid_list.append(
                        '<td>{ir_gv}</td>'.format(ir_gv=data[2])
                    )
            sec_grid_list.append('</tr>')

        grid_html = ''.join(grid_list)
        exp_html = ''.join(exps_list)
        ir_exp_html = ''.join(ir_exps_list)
        sec_grid_html = ''.join(sec_grid_list)
        doc = QtGui.QTextDocument()
        doc.addResource(QtGui.QTextDocument.ImageResource, QtCore.QUrl('mydata://nm.jpg'), QtCore.QVariant(self.qt_face))
        doc.addResource(QtGui.QTextDocument.ImageResource, QtCore.QUrl('mydata://ir.jpg'), QtCore.QVariant(self.qt_ir_face))
        html = TEMPLATE_HTML.format(hosp_name=HOSP_NAME, grid_html=grid_html, sec_grid_html=sec_grid_html, exp_html=exp_html, ir_exp_html=ir_exp_html, img_width=str(screen_width / 6), header_padding=str(screen_width / 12), **self.info)
        css = TEMPLATE_CSS
        doc.setHtml(_fromUtf8(html))
        doc.setDefaultStyleSheet(css)
        printer = QPrinter()
        printer.setOutputFileName(os.path.join(self.datas['tardir'], 'export.pdf'))
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        doc.print_(printer)
        try:
            os.startfile(os.path.join(self.datas['tardir'], 'export.pdf'))
        except:
            util.warn_dialog(text='\xe5\xbd\x93\xe5\x89\x8d\xe7\x94\xb5\xe8\x84\x91\xe6\xb2\xa1\xe5\xae\x89\xe8\xa3\x85pdf\xef\xbc\x8c\xe8\xaf\xb7\xe5\xae\x89\xe8\xa3\x85\xe5\x90\x8e\xe9\x87\x8d\xe8\xaf\x95')

    @pyqtSlot()
    def showMax(self):
        if not self.isMaximized():
            self.showMaximized()
        else:
            self.showNormal()
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.12 22:07:39 ÖÐ¹ú±ê×¼Ê±¼ä
