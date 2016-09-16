#-*- coding:utf-8 -*-
# 2016.09.16 17:25:01 中国标准时间
#Embedded file name: c:\Users\hp\Desktop\backup\cap.py
import cv2
import os
import numpy as np
from itertools import combinations, cycle, permutations
from threading import Lock
from PyQt4 import QtGui, QtCore

class Capture(object):
    LR_OFFSET = 60
    UD_OFFSET = 25
    SCAN_NUM = 10

    def __init__(self):
        caps = self.polling()
        if caps is None:
            self.useable = self.capturing = False
        else:
            self.useable = True
            self.groups = cycle(permutations(caps, min(2, len(caps))))
            self.normal_cap = self.ir_cap = None
            self._last_group = None
            self.next_group()
            self.capturing = False
            self.enable_switch = True if self.NM_NUM != self.IR_NUM else False
            self.blank = np.zeros((1, 1, 3), np.uint8)
            self.callback = None
            self.nm_frame = None
            self.ir_frame = None
            self.lower = np.array([0, 48, 80], dtype='uint8')
            self.upper = np.array([20, 255, 255], dtype='uint8')

    def next_group(self):
        group = next(self.groups)
        if group != self._last_group:
            self.NM_NUM, self.normal_cap = group[0]
            self.IR_NUM, self.ir_cap = group[1]
            self._last_group = group
            return True
        return False

    def polling(self):
        useable_cam = []
        for i in range(self.SCAN_NUM):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                useable_cam.append((i, cap))

        if len(useable_cam) == 1:
            useable_cam.append(useable_cam[0])
        elif len(useable_cam) == 0:
            return None
        return useable_cam

    def is_open(self):
        if self.normal_cap is None and self.ir_cap is None:
            return False
        return self.normal_cap.isOpened() and self.ir_cap.isOpened()

    def is_running(self):
        return self.capturing

    def get_frames(self):
        return (self.nm_frame, self.ir_frame)

    def start(self, callback):
        if self.useable == False:
            return
        self.callback = callback
        self.capturing = True
        while self.capturing:
            ret, self.nm_frame = self.normal_cap.read()
            ret2, self.ir_frame = self.ir_cap.read()
            hsv_nm = cv2.cvtColor(self.nm_frame, cv2.COLOR_BGR2HSV)
            hsv_ir = cv2.cvtColor(self.ir_frame, cv2.COLOR_BGR2HSV)
            mask_nm = cv2.inRange(hsv_nm, self.lower, self.upper)
            mask_ir = cv2.inRange(hsv_ir, self.lower, self.upper)
            cv2.imshow(u'\u4e0d\u8981\u5173\u95ed\u8be5\u7a97\u53e3', self.blank)
            callback(self.nm_frame, self.ir_frame)
            cv2.waitKey(5)

        cv2.destroyAllWindows()
        self.capturing = False

    def switch(self):
        self.end()
        self.normal_cap.release()
        self.ir_cap.release()
        self.NM_NUM, self.IR_NUM = self.IR_NUM, self.NM_NUM
        self.normal_cap = cv2.VideoCapture(self.NM_NUM)
        self.ir_cap = cv2.VideoCapture(self.IR_NUM)
        self.start(self.callback)

    def end(self):
        self.capturing = False

    def quit(self):
        self.end()
        cv2.destroyAllWindows()
        self.normal_cap.release()
        self.ir_cap.release()

    def fix_ir(self, frame):
        height, width = frame.shape[:2]
        lr_offset = np.zeros((height, self.LR_OFFSET, 3), np.uint8)
        ud_offset = np.zeros((self.UD_OFFSET, width, 3), np.uint8)
        frame[0:height, 0:width - self.LR_OFFSET] = frame[0:height, self.LR_OFFSET:width]
        frame[self.UD_OFFSET:height, 0:width] = frame[0:height - self.UD_OFFSET, 0:width]
        frame[0:height, width - self.LR_OFFSET:width] = lr_offset[:]
        frame[0:self.UD_OFFSET, 0:width] = ud_offset[:]
        return frame
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:25:01 中国标准时间
