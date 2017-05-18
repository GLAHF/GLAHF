#-*- coding:utf-8 -*-
# 2016.09.16 17:26:05 ÖÐ¹ú±ê×¼Ê±¼ä
#Embedded file name: c:\Users\hp\Desktop\backup\export.py
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from common import *
from datetime import datetime, date
from util import warn_dialog
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


class InfoDialog(QtGui.QDialog):

    def __init__(self, parent = None):
        super(InfoDialog, self).__init__(parent)
        self.parent = parent
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(_translate('MainWindow', HOSP_NAME, None))
        layout = QtGui.QGridLayout(self)
        self.hospitalized_label = QtGui.QLabel(self)
        self.hospitalized_label.setText(_translate('MainWindow', '住院号', None))
        self.hospitalized = QtGui.QLineEdit(self)
        layout.addWidget(self.hospitalized_label, 0, 0, 1, 1)
        layout.addWidget(self.hospitalized, 0, 1, 1, 1)
        self.outpatient_label = QtGui.QLabel(self)
        self.outpatient_label.setText(_translate('MainWindow', '门诊号', None))
        self.outpatient = QtGui.QLineEdit(self)
        layout.addWidget(self.outpatient_label, 0, 2, 1, 1)
        layout.addWidget(self.outpatient, 0, 3, 1, 1)
        self.datetime_label = QtGui.QLabel(self)
        self.datetime_label.setText(_translate('MainWindow', '检测时间', None))
        self.datetime = QtGui.QDateTimeEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QtCore.QDateTime.currentDateTime())
        self.datetime.setDisplayFormat(u'yyyy\u5e74M\u6708d\u65e5 H:MM:s')
        layout.addWidget(self.datetime_label, 0, 4, 1, 1)
        layout.addWidget(self.datetime, 0, 5, 1, 1)
        self.name_label = QtGui.QLabel(self)
        self.name_label.setText(_translate('MainWindow', '姓名', None))
        self.name = QtGui.QLineEdit(self)
        layout.addWidget(self.name_label, 1, 0, 1, 1)
        layout.addWidget(self.name, 1, 1, 1, 1)
        self.sex_label = QtGui.QLabel(self)
        self.sex_label.setText(_translate('MainWindow', '性别', None))
        self.sex = QtGui.QComboBox()
        self.sex.addItems([u'\u7537', u'\u5973'])
        layout.addWidget(self.sex_label, 1, 2, 1, 1)
        layout.addWidget(self.sex, 1, 3, 1, 1)
        self.marriage_label = QtGui.QLabel(self)
        self.marriage_label.setText(_translate('MainWindow', '婚姻', None))
        self.marriage = QtGui.QComboBox()
        self.marriage.addItems([u'\u5df2\u5a5a', u'\u672a\u5a5a'])
        layout.addWidget(self.marriage_label, 1, 4, 1, 1)
        layout.addWidget(self.marriage, 1, 5, 1, 1)
        self.born_label = QtGui.QLabel(self)
        self.born_label.setText(_translate('MainWindow', '出生日期', None))
        self.born = QtGui.QDateEdit(self)
        self.born.setCalendarPopup(True)
        self.born.setDisplayFormat(u'yyyy\u5e74M\u6708d\u65e5')
        self.born.setDate(QtCore.QDate.fromString('19760616', 'yyyyMd'))
        layout.addWidget(self.born_label, 2, 0, 1, 1)
        layout.addWidget(self.born, 2, 1, 1, 1)
        self.height_label = QtGui.QLabel(self)
        self.height_label.setText(_translate('MainWindow', '身高', None))
        self.height = QtGui.QComboBox()
        self.height.addItems([ '%scm' % i for i in xrange(80, 200) ])
        layout.addWidget(self.height_label, 2, 2, 1, 1)
        layout.addWidget(self.height, 2, 3, 1, 1)
        self.weight_label = QtGui.QLabel(self)
        self.weight_label.setText(_translate('MainWindow', '体重', None))
        self.weight = QtGui.QComboBox()
        self.weight.addItems([ '%skg' % i for i in xrange(40, 150) ])
        layout.addWidget(self.weight_label, 2, 4, 1, 1)
        layout.addWidget(self.weight, 2, 5, 1, 1)
        self.chief_complaint_label = QtGui.QLabel(self)
        self.chief_complaint_label.setText(_translate('MainWindow', '主述', None))
        self.chief_complaint = QtGui.QLineEdit(self)
        layout.addWidget(self.chief_complaint_label, 3, 0, 1, 1)
        layout.addWidget(self.chief_complaint, 3, 1, 1, 1)
        self.diagnose_label = QtGui.QLabel(self)
        self.diagnose_label.setText(_translate('MainWindow', '初步诊断', None))
        self.diagnose = QtGui.QTextEdit(self)
        self.diagnose.setFixedHeight(80)
        layout.addWidget(self.diagnose_label, 4, 0, 1, 1)
        layout.addWidget(self.diagnose, 4, 1, 1, 2)
        self.buttons = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, Qt.Horizontal, self)
        layout.addWidget(self.buttons, 5, 5, 1, 1)
        self.buttons.accepted.connect(self.save)
        self.buttons.rejected.connect(self.exit)

    def setCallbackAfterSave(self, callback):
        self.callback = callback

    def exit(self):
        if self.parent is not None:
            self.parent.show()
        self.close()
        self.setParent(None)

    def save(self):
        if self.name.text() == '':
            warn_dialog(self, text='\xe5\xa7\x93\xe5\x90\x8d\xe4\xb8\x8d\xe8\x83\xbd\xe4\xb8\xba\xe7\xa9\xba')
            return
        info = {'name': str(self.name.text()),
         'marriage': str(self.marriage.itemText(self.marriage.currentIndex())),
         'born': self.born.date().toPyDate().strftime('%Y\xe5\xb9\xb4%m\xe6\x9c\x88'),
         'datetime': self.datetime.dateTime().toPyDateTime().strftime('%Y\xe5\xb9\xb4%m\xe6\x9c\x88%d\xe6\x97\xa5 %H:%M:%S'),
         'hospitalized': str(self.hospitalized.text()),
         'outpatient': str(self.outpatient.text()),
         'height': str(self.height.itemText(self.height.currentIndex())),
         'weight': str(self.weight.itemText(self.weight.currentIndex())),
         'sex': str(self.sex.itemText(self.sex.currentIndex())),
         'chief_complaint': str(self.chief_complaint.text()),
         'diagnose': str(self.diagnose.toPlainText())}
        flag = self.callback(info)
        if self.parent is not None:
            self.parent.show()
        self.close()
        self.setParent(None)
        if flag is True:
            warn_dialog(text='\xe8\xae\xb0\xe5\xbd\x95\xe5\xb7\xb2\xe5\xad\x98\xe7\x9b\x98')
        else:
            warn_dialog(text='\xe8\xaf\xb7\xe9\x80\x89\xe6\x8b\xa9\xe5\x9b\xbe\xe7\x89\x87')


class ExportWidget(QtGui.QWidget):

    def __init__(self, parent = None, info = None, img = None, ir_img = None, region = None, exps_areas = None):
        super(ExportWidget, self).__init__(parent)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8('Microsoft YaHei'))
        font.setPointSize(18)
        self.info = info
        layout = QtGui.QGridLayout(self)
        self.header = QtGui.QLabel(self)
        self.header.setText(_translate('MainWindow', '       ' + HOSP_NAME + '\n\xe9\x9d\xa2\xe5\x8c\xba\xe8\x89\xb2\xe9\x83\xa8\xe8\x87\xaa\xe5\x8a\xa8\xe5\x88\x86\xe6\x9e\x90\xe4\xbb\xaa\xe6\xa3\x80\xe6\xb5\x8b\xe6\x8a\xa5\xe5\x91\x8a\n', None))
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.header.setFont(font)
        layout.addWidget(self.header, 0, 0, 1, 5)
        font.setPointSize(14)
        self.hospitalized_label = QtGui.QLabel(self)
        self.hospitalized_label.setText(_translate('MainWindow', '\xe4\xbd\x8f\xe9\x99\xa2\xe5\x8f\xb7 %s' % info['hospitalized'], None))
        self.hospitalized_label.setFont(font)
        layout.addWidget(self.hospitalized_label, 1, 0, 1, 1)
        self.outpatient_label = QtGui.QLabel(self)
        self.outpatient_label.setText(_translate('MainWindow', '\xe9\x97\xa8\xe8\xaf\x8a\xe5\x8f\xb7 %s' % info['outpatient'], None))
        self.outpatient_label.setFont(font)
        layout.addWidget(self.outpatient_label, 1, 2, 1, 1)
        self.datetime_label = QtGui.QLabel(self)
        self.datetime_label.setText(_translate('MainWindow', '\xe6\xa3\x80\xe6\xb5\x8b\xe6\x97\xb6\xe9\x97\xb4 %s' % info['datetime'], None))
        self.datetime_label.setFont(font)
        layout.addWidget(self.datetime_label, 1, 4, 1, 1)
        self.name_label = QtGui.QLabel(self)
        self.name_label.setText(_translate('MainWindow', '\xe5\xa7\x93\xe5\x90\x8d %s' % info['name'], None))
        self.name_label.setFont(font)
        layout.addWidget(self.name_label, 2, 0, 1, 1)
        self.sex_label = QtGui.QLabel(self)
        self.sex_label.setText(_translate('MainWindow', '\xe6\x80\xa7\xe5\x88\xab %s' % info['sex'], None))
        self.sex_label.setFont(font)
        layout.addWidget(self.sex_label, 2, 2, 1, 1)
        self.marriage_label = QtGui.QLabel(self)
        self.marriage_label.setText(_translate('MainWindow', '\xe5\xa9\x9a\xe5\xa7\xbb %s' % info['marriage'], None))
        self.marriage_label.setFont(font)
        layout.addWidget(self.marriage_label, 2, 4, 1, 1)
        self.born_label = QtGui.QLabel(self)
        self.born_label.setText(_translate('MainWindow', '\xe5\x87\xba\xe7\x94\x9f\xe5\xb9\xb4\xe6\x9c\x88 %s' % info['born'], None))
        self.born_label.setFont(font)
        layout.addWidget(self.born_label, 3, 0, 1, 1)
        self.height_label = QtGui.QLabel(self)
        self.height_label.setText(_translate('MainWindow', '\xe8\xba\xab\xe9\xab\x98 %s' % info['height'], None))
        self.height_label.setFont(font)
        layout.addWidget(self.height_label, 3, 2, 1, 1)
        self.weight_label = QtGui.QLabel(self)
        self.weight_label.setText(_translate('MainWindow', '\xe4\xbd\x93\xe9\x87\x8d %s' % info['weight'], None))
        self.weight_label.setFont(font)
        layout.addWidget(self.weight_label, 3, 4, 1, 1)
        self.chief_complaint_label = QtGui.QLabel(self)
        self.chief_complaint_label.setText(_translate('MainWindow %s', '\xe4\xb8\xbb\xe8\xaf\x89\n  %s' % info['chief_complaint'], None))
        self.chief_complaint_label.setFont(font)
        layout.addWidget(self.chief_complaint_label, 4, 0, 1, 1)
        self.diagnose_label = QtGui.QLabel(self)
        self.diagnose_label.setText(_translate('MainWindow', '\xe5\x88\x9d\xe6\xad\xa5\xe8\xaf\x8a\xe6\x96\xad\n %s\n' % info['diagnose'], None))
        self.diagnose_label.setFont(font)
        layout.addWidget(self.diagnose_label, 5, 0, 1, 1)
        self.result_pic_label = QtGui.QLabel(self)
        self.result_pic_label.setText(_translate('MainWindow', '\xe6\xa3\x80\xe6\xb5\x8b\xe7\xbb\x93\xe6\x9e\x9c\xe5\x9b\xbe\xe7\x89\x87', None))
        self.result_pic_label.setFont(font)
        layout.addWidget(self.result_pic_label, 6, 0, 1, 1)
        qpm_lb = QtGui.QLabel(self)
        qpm_lb.setScaledContents(True)
        qpm_lb.setPixmap(img)
        qpm_lb.setFixedSize(500, 500)
        qpm_ir_lb = QtGui.QLabel(self)
        qpm_ir_lb.setScaledContents(True)
        qpm_ir_lb.setPixmap(ir_img)
        qpm_ir_lb.setFixedSize(500, 500)
        layout.addWidget(qpm_lb, 7, 0, 1, 2)
        layout.addWidget(qpm_ir_lb, 7, 2, 1, 2)
        font.setPointSize(11)
        self.result_table_label = QtGui.QLabel(self)
        self.result_table_label.setText(_translate('MainWindow', '\xe6\xa3\x80\xe6\xb5\x8b\xe6\x95\xb0\xe6\x8d\xae', None))
        self.result_table_label.setFont(font)
        layout.addWidget(self.result_table_label, 8, 0, 1, 1)
        layout.addWidget(region, 9, 0, 1, 4)
        exps = []
        lowers, highers = exps_areas[0], exps_areas[1]
        for exp in lowers:
            exps.append('%s: \xe6\xaf\x94\xe5\xb9\xb3\xe5\x9d\x87\xe5\x80\xbc\xe4\xbd\x8e%.2f' % (exp[0], abs(exp[1])))

        for exp in highers:
            exps.append('%s: \xe6\xaf\x94\xe5\xb9\xb3\xe5\x9d\x87\xe5\x80\xbc\xe9\xab\x98%.2f' % (exp[0], abs(exp[1])))

        self.exp_datas_label = QtGui.QLabel(self)
        self.exp_datas_label.setText(_translate('MainWindow', '\xe5\xbc\x82\xe5\xb8\xb8\xe6\x95\xb0\xe6\x8d\xae\xe6\x8a\xa5\xe5\x91\x8a\n%s' % '\n'.join(exps), None))
        self.exp_datas_label.setFont(font)
        layout.addWidget(self.exp_datas_label, 10, 0, 1, 1)
        font.setPointSize(14)
        self.sign_label = QtGui.QLabel(self)
        self.sign_label.setText(_translate('MainWindow', '\xe6\xa3\x80\xe6\xb5\x8b\xe4\xba\xba\xe7\xad\xbe\xe5\xad\x97', None))
        self.sign_label.setFont(font)
        layout.addWidget(self.sign_label, 11, 3, 1, 1)
        self.date_label = QtGui.QLabel(self)
        self.date_label.setText(_translate('MainWindow', '\xe5\xb9\xb4    \xe6\x9c\x88    \xe6\x97\xa5\n', None))
        self.date_label.setFont(font)
        layout.addWidget(self.date_label, 12, 4, 1, 1)
        self.setStyleSheet('background-color:white;')
        self.resize(1800, 2670)
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:26:06 ÖÐ¹ú±ê×¼Ê±¼ä
