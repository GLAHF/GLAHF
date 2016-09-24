#-*- coding:utf-8 -*-
# 2016.09.16 17:25:18 ÖÐ¹ú±ê×¼Ê±¼ä
#Embedded file name: c:\Users\hp\Desktop\backup\common.py
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

LR_LINES = 40.0
UD_LINES = 60.0
SYS_PATH = './sys'
INIT_FRONTALIMG = SYS_PATH + '/img/frontal.jpg'
INIT_LEFTIMG = SYS_PATH + '/img/left.jpg'
INIT_RIGHTIMG = SYS_PATH + '/img/right.jpg'
CLB_IMG = SYS_PATH + '/img/calibration.jpg'
BG_IMG = SYS_PATH + '/img/mbg.png'
SUCCESS_STATUS_IMG = SYS_PATH + '/img/success.png'
FAIL_STATUS_IMG = SYS_PATH + '/img/fail.png'
SEARCH_IMG = SYS_PATH + '/img/power.png'
LOADING_GIF = SYS_PATH + '/img/loading.gif'
TEMP_PATH = './temp'
FACE_TEMP_PATH = TEMP_PATH + '/frontal_temp.jpg'
FACE_ORIG_PATH = TEMP_PATH + '/frontal_orig.jpg'
LEFT_TEMP_PATH = TEMP_PATH + '/left_temp.jpg'
LEFT_ORIG_PATH = TEMP_PATH + '/left_orig.jpg'
RIGHT_TEMP_PATH = TEMP_PATH + '/right_temp.jpg'
RIGHT_ORIG_PATH = TEMP_PATH + '/right_orig.jpg'
LEFT_TEMP_IR_PATH = TEMP_PATH + '/left_temp_ir.jpg'
FACE_TEMP_IR_PATH = TEMP_PATH + '/frontal_temp_ir.jpg'
RIGHT_TEMP_IR_PATH = TEMP_PATH + '/right_temp_ir.jpg'
LINE_TEMP_PATH = TEMP_PATH + '/lines.jpg'
LINE_TEMP_IR_PATH = TEMP_PATH + '/lines_ir.jpg'
LEFT_TAG = 'left'
LEFT_IR_TAG = 'left_ir'
FRONTAL_TAG = 'frontal'
FRONTAL_IR_TAG = 'frontal_ir'
RIGHT_TAG = 'right'
RIGHT_IR_TAG = 'right_ir'
SETTING_FILE = 'settings.json'
DATA_FILE = 'db.json'
STUDY_FILE = 'memory.pkl'
CLB_FILE = 'calibration.json'
INFO_FILE = 'info.json'
DATAS_FILE = 'datas.json'
BEGIN_ANALYSE_DEBUG = True
HOSP_NAME = '未注册'
try:
    tree = ET.ElementTree(file='./hosp.xml')
    text = tree.getroot().text
    if text is not None:
        HOSP_NAME = text
    del tree
    del text
except:
    pass

def open_all_debugs():
    BEGIN_ANALYSE_DEBUG = True


def close_all_debugs():
    BEGIN_ANALYSE_DEBUG = False
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:25:18 ÖÐ¹ú±ê×¼Ê±¼ä
