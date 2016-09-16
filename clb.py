#-*- coding:utf-8 -*-
# 2016.09.16 17:25:09 中国标准时间
#Embedded file name: c:\Users\hp\Desktop\backup\clb.py
from common import *
import numpy as np
import cv2

class Calibration(object):

    def __init__(self, img = None):
        super(Calibration, self).__init__()
        self.img = cv2.imread(CLB_IMG) if img is None else img
        self.drawing = False
        self.ending = False
        self.start_x = self.end_x = self.start_y = self.end_y = 0

    def draw_rect(self, event, x, y, flags, param):
        if event == cv2.EVENT_FLAG_LBUTTON:
            self.drawing = True
            self.ix, self.iy = x, y
        elif event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
            if self.drawing == True:
                cv2.rectangle(self.img, (self.ix, self.iy), (x, y), (0, 255, 0), -1)
        elif event == cv2.EVENT_LBUTTONUP and self.drawing == True:
            if self.ix < 0:
                self.ix = 0
            if self.iy < 0:
                self.iy = 0
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            if self.ix > x:
                self.ix, x = x, self.ix
            if self.iy > y:
                self.iy, y = y, self.iy
            height, width = self.img.shape[:2]
            self.drawing = False
            self.start_x = float(self.ix) / width
            self.end_x = float(x) / width
            self.start_y = float(self.iy) / height
            self.end_y = float(y) / height
            self.ending = True

    def get_position(self, *arg, **kw):
        cv2.namedWindow('image')
        cv2.setMouseCallback('image', self.draw_rect)
        while 1:
            cv2.imshow('image', self.img)
            k = cv2.waitKey(20) & 255
            if self.ending or k in (27, 113):
                break

        cv2.destroyAllWindows()
        d = {}
        d['start_x'] = self.start_x
        d['end_x'] = self.end_x
        d['start_y'] = self.start_y
        d['end_y'] = self.end_y
        self.ending = False
        return d
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:25:10 中国标准时间
