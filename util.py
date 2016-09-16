#-*- coding:utf-8 -*-
# 2016.09.16 17:26:27 中国标准时间
#Embedded file name: c:\Users\hp\Desktop\backup\util.py
import os
import sys
import hashlib
import json
import logging
import shutil
import time
from PyQt4 import QtGui, QtCore
from common import *
from functools import wraps, partial
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


def warn_dialog(parent = None, window = 'MainWindow', title = u'\u6807\u9898', text = 'text'):
    QtGui.QMessageBox.warning(parent, _translate(window, title, None), _translate(window, text, None))


def about_dialog(parent = None, window = 'MainWindow', title = u'\u6807\u9898', text = 'text'):
    QtGui.QMessageBox.about(parent, _translate(window, title, None), _translate(window, text, None))


def verify():
    import wmi
    import md5
    w = wmi.WMI()
    nets = w.Win32_NetworkAdapterConfiguration()
    s = ''.join([ str(n.MACAddress) for n in nets ]) + 'glahf'
    secret_key = md5.new(s).hexdigest()[0:8]
    d = load_config()
    if d['code'] is False:
        pass
    elif d['code'].lower() == secret_key.lower():
        return True
    code = QtGui.QInputDialog.getText(None, u'\u6ce8\u518c\u7801', u'\u8f93\u5165\u6ce8\u518c\u7801:', QtGui.QLineEdit.Normal, '')[0]
    try:
        if secret_key.lower() == str(code).lower():
            if d:
                d['code'] = secret_key
                write_config(d)
                return True
            return False
        return False
    except:
        return True


def screen_size():
    screen = QtGui.QDesktopWidget().screenGeometry()
    return (screen.height(), screen.width())


def init():
    _init_config()
    _init_temp()


def _init_temp():
    try:
        if os.path.exists(TEMP_PATH) == True:
            shutil.rmtree(TEMP_PATH)
            os.mkdir(TEMP_PATH)
        else:
            os.mkdir(TEMP_PATH)
    except Exception:
        logging.error('\xe4\xb8\xb4\xe6\x97\xb6\xe6\x96\x87\xe4\xbb\xb6\xe5\xa4\xb9\xe5\x88\x9b\xe5\xbb\xba\xe5\xa4\xb1\xe8\xb4\xa5')


def _init_config():
    logging.basicConfig(filemode='w', filename='./log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')
    if os.path.exists(SETTING_FILE) == False:
        with open(SETTING_FILE, 'w') as setting:
            savedir = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'images')
            d = {}
            d['lockeyes'] = True
            d['savedir'] = savedir
            d['vposcount'] = 160
            d['hposcount'] = 120
            d['code'] = False
            json.dump(d, setting, indent=4)


def write_config(config):
    if isinstance(config, dict):
        try:
            with open(SETTING_FILE, 'w') as setting:
                json.dump(config, setting, indent=4)
        except:
            logging.error('\xe9\x85\x8d\xe7\xbd\xae\xe8\xaf\xbb\xe5\x8f\x96\xe5\xa4\xb1\xe8\xb4\xa5')


def load_config():
    config = {}
    try:
        with open(SETTING_FILE) as jsonfile:
            config = json.load(jsonfile)
    except:
        logging.error('\xe9\x85\x8d\xe7\xbd\xae\xe8\xaf\xbb\xe5\x8f\x96\xe5\xa4\xb1\xe8\xb4\xa5')
        return config

    return config


def clb_array():
    d = {}
    try:
        with open(CLB_FILE, 'rb') as clb:
            d = json.load(clb)
    except:
        logging.error('CLB\xe5\xbc\x82\xe5\xb8\xb8')

    return d


def db_array():
    arr = []
    try:
        with open(DATA_FILE, 'rb') as db:
            arr = json.load(db)
    except:
        logging.error('\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93\xe4\xb8\x8d\xe5\xad\x98\xe5\x9c\xa8')

    return arr


def direct_write_db(arr):
    try:
        with open(DATA_FILE, 'wb') as db:
            json.dump(arr, db)
    except IOError:
        logging.error('\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93\xe5\x86\x99\xe5\x85\xa5\xe5\xa4\xb1\xe8\xb4\xa5')


def insert_to_db(d):
    arr = db_array()
    arr.append(d)
    direct_write_db(arr)


def update_db():
    arr = []
    if os.path.exists(DATA_FILE) == False:
        try:
            with open(DATA_FILE, 'w') as db:
                json.dump([], db)
        except:
            logging.error('DB\xe6\x96\x87\xe4\xbb\xb6\xe5\x88\x9b\xe5\xbb\xba\xe5\xa4\xb1\xe8\xb4\xa5')

    else:
        arr = db_array()
    if arr is not None:
        for d in arr:
            if os.path.exists(d.get('path')) == False:
                arr.remove(d)

    direct_write_db(arr)


def get_memory():
    m_linesArr = None
    try:
        with open(STUDY_FILE, 'rb') as memory_file:
            m_linesArr = pickle.load(memory_file)[0]
    except:
        logging.ERROR('\xe8\xae\xb0\xe5\xbf\x86\xe8\xaf\xbb\xe5\x8f\x96\xe5\xa4\xb1\xe8\xb4\xa5')
    finally:
        return m_linesArr


def clickable(widget):

    class Filter(QtCore.QObject):
        clicked = QtCore.pyqtSignal()

        def eventFilter(self, obj, event):
            if obj == widget:
                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.clicked.emit()
                        return True
            return False

    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked


def _function():
    return sys._getframe(1).f_back.f_locals


def fn_timer(function):

    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print 'Total time running <%s>: %s seconds' % (function.func_name, str(t1 - t0))
        return result

    return function_timer


def optional_debug(func = None, debug = False):
    if func is None:
        return partial(optional_debug, debug=debug)

    @wraps(func)
    def wrapper(*args, **kw):
        return func(*args, **kw)

    wrapper.DEBUG = debug
    return wrapper


class Singleton(type):

    def __new__(cls, *arg, **kw):
        cls._instance = None
        return super(Singleton, cls).__new__(cls, *arg, **kw)

    def __call__(cls, *arg, **kw):
        if cls._instance is not None:
            return cls._instance
        else:
            cls._instance = super(Singleton, cls).__call__(*arg, **kw)
            return cls._instance


class DBHandler(object):

    def __init__(self):
        self.db = None

    def set(self, file):
        raise NotImplementedError

    def insert(self, data):
        raise NotImplementedError()

    def update(self, query, dict, multi = False):
        raise NotImplementedError()

    def remove(self, query):
        raise NotImplementedError()

    def query(self, query):
        raise NotImplementedError()


class JsonDBHandler(DBHandler):

    @staticmethod
    def insert(self, data):
        if isinstance(data, dict):
            self.db.append(data)
        else:
            print '\xe9\x94\x99\xe8\xaf\xaf\xe7\x9a\x84\xe6\x95\xb0\xe6\x8d\xae\xe7\xb1\xbb\xe5\x9e\x8b'

    def update(self, query, dict, multi = False):
        raise NotImplementedError()

    def remove(self, query):
        raise NotImplementedError()

    def query(self, query):
        raise NotImplementedError()

    def set(self, fp):
        try:
            self.db = json.load(fp)
        except:
            raise IOError('\xe9\x9d\x9ejson\xe7\xb1\xbb\xe5\x9e\x8b\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93')

    def save(self, fp):
        try:
            json.dump(self.db, fp)
        except:
            raise IOError('json\xe5\x86\x99\xe5\x85\xa5\xe5\xa4\xb1\xe8\xb4\xa5')


class DBManager:
    __metaclass__ = Singleton

    def __init__(self, data_file = DATA_FILE, hanlder = JsonDBHandler):
        self.file = data_file
        self.hanlder = hanlder()

    def __enter__(self):
        try:
            self.f = open(self.file, 'w')
            self.hanlder.set(self.f)
        except:
            import traceback
            traceback.print_exc()

        return self.hanlder

    def __exit__(self):
        print 'exit'
        try:
            self.hanlder.save(self.f)
            self.f.close()
        except:
            pass

    def db_array():
        arr = []
        try:
            with open(DATA_FILE, 'rb') as db:
                arr = pickle.load(db)
        except:
            logging.ERROR('\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93\xe4\xb8\x8d\xe5\xad\x98\xe5\x9c\xa8')

        return arr

    def direct_write_db(arr):
        try:
            with open(DATA_FILE, 'wb') as db:
                pickle.dump(arr, db)
        except IOError:
            logging.ERROR('\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93\xe5\x86\x99\xe5\x85\xa5\xe5\xa4\xb1\xe8\xb4\xa5')

    def insert_to_db(dict_):
        arr = db_array()
        arr.append(dict_)
        direct_write_db(arr)

    def update_db():
        arr = []
        if os.path.exists(DATA_FILE) == False:
            try:
                with open(DATA_FILE, 'w') as db:
                    pickle.dump([], db)
            except:
                logging.ERROR('DB\xe6\x96\x87\xe4\xbb\xb6\xe5\x88\x9b\xe5\xbb\xba\xe5\xa4\xb1\xe8\xb4\xa5')

        else:
            arr = db_array()
        if arr is not None:
            for d in arr:
                if os.path.exists(d.get('path')) == False:
                    arr.remove(d)

        direct_write_db(arr)


from pprint import pformat

def print_result(hint, result):

    def encode(obj):
        if type(obj) is unicode:
            return obj.encode('utf-8')
        if type(obj) is dict:
            return {encode(k):encode(v) for k, v in obj.iteritems()}
        if type(obj) is list:
            return [ encode(i) for i in obj ]
        return obj

    print hint
    result = encode(result)
    print '\n'.join([ '  ' + i for i in pformat(result, width=75).split('\n') ])
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:26:29 中国标准时间
