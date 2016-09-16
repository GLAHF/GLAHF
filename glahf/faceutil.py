#-*- coding:utf-8 -*-
# 2016.09.16 17:27:00 中国标准时间
#Embedded file name: c:\Users\hp\Desktop\backup\glahf\faceutil.py
from common import *
from datetime import datetime
from functools import wraps
from matplotlib import pyplot as plt
import copy
import cv2
import json
import math
import numpy as np
import os
import sys
import time
import util
reload(sys)
sys.setdefaultencoding('utf-8')
import glahf

def splice_image(img, startpoint, endpoint, config, datas, img_type = 'nm'):
    if config is None:
        config = util.load_config()
    beginX = int(startpoint[0])
    beginY = int(startpoint[1])
    endX = int(endpoint[0])
    endY = int(endpoint[1])
    height, width = img.shape[:2]
    if img_type == 'ir':
        l_beg = int(datas['ir_left'] * width)
        u_beg = int(datas['ir_up'] * height)
        offheight = (datas['ir_down'] - datas['ir_up']) * height / 60
        offwidth = (datas['ir_right'] - datas['ir_left']) * width / 40
    else:
        l_beg = int(datas['left'] * width)
        u_beg = int(datas['up'] * height)
        offheight = (datas['down'] - datas['up']) * height / 60
        offwidth = (datas['right'] - datas['left']) * width / 40
    spliced_img = img[int(u_beg + beginY * offheight):int(u_beg + endY * offheight), int(l_beg + beginX * offwidth):int(l_beg + endX * offwidth)]
    return spliced_img


def handle_images(f_face, l_face, r_face, f_ir_face, l_ir_face, r_ir_face, info, config = {}, path = './', save = True):
    if not (f_ir_face and l_ir_face and r_ir_face and f_ir_face and l_ir_face and r_ir_face):
        util.warn_dialog(text='\xe8\xb7\xaf\xe5\xbe\x84\xe4\xb8\x8d\xe8\x83\xbd\xe4\xb8\xba\xe7\xa9\xba')
        raise AttributeError('\xe8\xb7\xaf\xe5\xbe\x84\xe4\xb8\x8d\xe8\x83\xbd\xe4\xb8\xba\xe7\xa9\xba')
    try:
        f_img = glahf.read(f_face)
        l_img = glahf.read(l_face)
        r_img = glahf.read(r_face)
    except IOError as e:
        util.warn_dialog(text='\xe5\x9b\xbe\xe7\x89\x87\xe8\xaf\xbb\xe5\x8f\x96\xe5\xa4\xb1\xe8\xb4\xa5')
        return

    h, w = f_img.shape[:2]
    l_img = cv2.resize(l_img, (w, h), interpolation=cv2.INTER_LINEAR)
    r_img = cv2.resize(r_img, (w, h), interpolation=cv2.INTER_LINEAR)
    vis = glahf.merge_image([l_img, f_img, r_img])
    join = os.path.join
    now_t = datetime.now()
    today = str(time.strftime('%Y-%m-%d', time.localtime()))
    date = str(time.strftime('%Y-%m-%d %H:%M %p', time.localtime()))
    f_ir_img = glahf.read(f_ir_face)
    l_ir_img = glahf.read(l_ir_face)
    r_ir_img = glahf.read(r_ir_face)
    if f_ir_img is None or l_ir_img is None or r_ir_img is None:
        util.warn_dialog(text='\xe8\xaf\xbb\xe5\x8f\x96\xe5\xa4\xb1\xe8\xb4\xa5')
        raise glahf.ReadException('\xe8\xaf\xbb\xe5\x8f\x96\xe5\xa4\xb1\xe8\xb4\xa5')
    h, w = f_ir_img.shape[:2]
    l_ir_img = cv2.resize(l_ir_img, (w, h), interpolation=cv2.INTER_LINEAR)
    r_ir_img = cv2.resize(r_ir_img, (w, h), interpolation=cv2.INTER_LINEAR)
    ir_vis = glahf.merge_image([l_ir_img, f_ir_img, r_ir_img])
    name = info['name'] if info['name'] else '\xe6\x9c\xaa\xe5\x91\xbd\xe5\x90\x8d'
    tardir = join(path, today, name + '(%s-%s)' % (now_t.hour, now_t.minute))
    if os.path.exists(tardir) is False:
        try:
            os.makedirs(tardir)
        except:
            util.warn_dialog(text='\xe6\x9d\x83\xe9\x99\x90\xe4\xb8\x8d\xe8\xb6\xb3')
            return

    savepath = join(tardir, 'nomarl.jpg')
    ir_savepath = join(tardir, 'ir.jpg')
    lines_savepath = join(tardir, '_lines.jpg')
    glahf.write(savepath.encode('gbk'), vis)
    glahf.write(ir_savepath.encode('gbk'), ir_vis)
    glahf.write(join(tardir, 'nm_left.jpg').encode('gbk'), l_img)
    glahf.write(join(tardir, 'nm_front.jpg').encode('gbk'), f_img)
    glahf.write(join(tardir, 'nm_right.jpg').encode('gbk'), r_img)
    glahf.write(join(tardir, 'ir_left.jpg').encode('gbk'), l_ir_img)
    glahf.write(join(tardir, 'ir_front.jpg').encode('gbk'), f_ir_img)
    glahf.write(join(tardir, 'ir_right.jpg').encode('gbk'), r_ir_img)
    with open(join(tardir, INFO_FILE), 'w') as fp:
        json.dump(info, fp)
    with open(join(tardir, '\xe5\xa4\x87\xe4\xbb\xbd'), 'w'):
        pass
    arr = util.db_array()
    id = len(arr)
    return {'id': str(id + 1),
     'tardir': tardir,
     'date': date,
     'path': savepath,
     'ir_path': ir_savepath}


def get_offset_img(img, x_offset = 0, y_offset = 0, dist = 0.005):
    height, width = img.shape[:2]
    blank_image = np.zeros((height, width, 3), np.uint8)
    x_dist = int(width * dist)
    y_dist = int(height * dist)
    if x_offset >= 0 and y_offset >= 0:
        blank_image[0:height - y_offset * y_dist, 0:width - x_offset * x_dist] = img[y_offset * y_dist:height, x_offset * x_dist:width]
    elif x_offset <= 0 and y_offset >= 0:
        blank_image[0:height - y_offset * y_dist, abs(x_offset) * x_dist:width] = img[y_offset * y_dist:height, 0:width - abs(x_offset) * x_dist]
    elif x_offset >= 0 and y_offset <= 0:
        blank_image[abs(y_offset) * y_dist:height, 0:width - x_offset * x_dist] = img[0:height - abs(y_offset) * y_dist, x_offset * x_dist:width]
    elif x_offset <= 0 and y_offset <= 0:
        blank_image[abs(y_offset) * y_dist:height, abs(x_offset) * x_dist:width] = img[0:height - abs(y_offset) * y_dist, 0:width - abs(x_offset) * x_dist]
    return blank_image


def get_avg_gray_value(vis, startpoint, endpoint, config, datas, img_type = 'nm'):
    if vis is None:
        return
    spliced_img = splice_image(vis, startpoint, endpoint, config, datas, img_type)
    return (spliced_img, round(spliced_img.mean(), 2))


def skin(face, mode = 'f', skinMask = None):
    h, w = face.shape[:2]
    if mode == 'l':
        face = face[0:h, 0:w * 3 / 4]
    elif mode == 'r':
        face = face[0:h, w / 4:w]
    elif mode != 'f':
        raise TypeError('invalid argument type')
    if skinMask is not None:
        skin, skinMask = glahf.pick_skin(face, skinMask)
        return skin
    else:
        skin, skinMask = glahf.pick_skin(face)
        return (skin, skinMask)


def showplt(img):
    from matplotlib.font_manager import FontProperties
    font = FontProperties(fname='c:\\windows\\fonts\\simsun.ttc', size=14)
    hist_full = cv2.calcHist([img], [0], None, [256], [0, 256])
    (plt.subplot(211), plt.imshow(img, 'gray'), plt.title(u'\u7ed3\u679c', fontproperties=font))
    (plt.subplot(212), plt.plot(hist_full, 'gray'), plt.xlim([0, 256]))
    plt.xlabel(u'\u7070\u5ea6\u8303\u56f4', fontproperties=font)
    plt.ylabel(u'\u50cf\u7d20\u6570\u91cf', fontproperties=font)
    plt.show()


def show_detection(face):
    organs = glahf.get_organs(face)
    eyes = organs.get_eyes()
    noses = organs.get_noses()
    mouths = organs.get_mouths()
    face_dup = None
    if eyes or noses or mouths:
        face_dup = face.copy()
        for ex, ey, ew, eh in eyes:
            cv2.putText(face_dup, u'eye', (ex, ey), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 1)
            cv2.rectangle(face_dup, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 1)

        for nx, ny, nw, nh in noses:
            cv2.putText(face_dup, u'nose', (nx, ny), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 1)
            cv2.rectangle(face_dup, (nx, ny), (nx + nw, ny + nh), (0, 255, 0), 1)

        for mx, my, mw, mh in mouths:
            cv2.putText(face_dup, u'mouth', (mx, my), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 1)
            cv2.rectangle(face_dup, (mx, my), (mx + mw, my + mh), (0, 255, 0), 1)

    if face_dup is not None:
        face_dup = glahf.resize(face_dup, 600, 400)
        glahf.show(face_dup)


def get_facepp_pos(facepp_data):
    if facepp_data is None:
        return
    try:
        face_data = facepp_data['face'][0]
    except:
        return

    pos = face_data['position']
    for key in pos.keys():
        if key in ('height', 'width'):
            continue
        pos[key]['x'] = pos[key]['x'] / 100.0
        pos[key]['y'] = pos[key]['y'] / 100.0

    return (pos['eye_left'],
     pos['eye_right'],
     pos['nose'],
     pos['mouth_left'],
     pos['mouth_right'])


def stretch(img, l_offset, r_offset):
    new_img = copy.deepcopy(img)
    if l_offset < 0 and r_offset < 0:
        new_img = cv2.copyMakeBorder(new_img, 0, 0, -l_offset, -r_offset, cv2.BORDER_REFLECT)
    elif l_offset < 0:
        new_img = cv2.copyMakeBorder(new_img, 0, 0, -l_offset, 0, cv2.BORDER_REFLECT)
        l_offset = 0
    elif r_offset < 0:
        new_img = cv2.copyMakeBorder(new_img, 0, 0, 0, -r_offset, cv2.BORDER_REFLECT)
        r_offset = 0
    else:
        new_img = new_img[0:h, l_offset * 2:w - r_offset * 2]
        new_img = cv2.resize(new_img, (w, h), interpolation=cv2.INTER_LINEAR)
    return new_img
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:27:01 中国标准时间
