#-*- coding:utf-8 -*-
# 2016.09.12 22:10:38 中国标准时间
#Embedded file name: glahf\glahf.pyo
from facepp import facepp
from functools import partial, wraps
import cv2
import faceutil
import logging
import math
import net
import numpy as np
import os
try:
    import cPickle as pickle
except ImportError:
    import pickle

face_cascade = cv2.CascadeClassifier('./cascades/haarcascade_frontalface_alt.xml')
eye_cascade = cv2.CascadeClassifier('./cascades/haarcascade_eye_tree_eyeglasses.xml')
nose_cascade = cv2.CascadeClassifier('./cascades/haarcascade_mcs_nose.xml')
mouth_cascade = cv2.CascadeClassifier('./cascades/haarcascade_mcs_mouth.xml')

class _const(object):

    class ConstError(TypeError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError, "Can't rebind const(%s)" % name
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            raise self.ConstError, "Can't unbind const(%s)" % name
        raise NameError, name


class ReadException(IOError):
    pass


class ImageNotFound(IOError):
    pass


class DetectExcepetion(Exception):
    pass


class UnExpectedValueException(ValueError):
    pass


def _mid_x(arr):
    return (2 * arr[0] + arr[2]) / 2


def _mid_y(arr):
    return (2 * arr[1] + arr[3]) / 2


class EInfo:
    TAG = None
    LEFT = 0
    RIGHT = 0
    UP = 0
    DOWN = 0


e_list = []

def _remove_tag(tag):
    for info in e_list:
        if info.TAG == tag:
            e_list.remove(info)


def array_equal(A, B):
    return np.array_equal(A, B)


def enlargeimage(img, scale, step = 0.01, position = None, tag = None):
    height, width = img.shape[:2]
    beginH = int(round(height * scale))
    endH = int(round(height - beginH))
    beginW = int(round(width * scale))
    endW = int(round(width - beginW))
    if scale > 0:
        if position:
            INFO = None
            for info in e_list:
                if info.TAG == tag:
                    INFO = info
                    break

            if INFO is None:
                INFO = EInfo()
                INFO.TAG = tag
                e_list.append(INFO)
            if position == 'up':
                INFO.UP += 1
            elif position == 'down':
                INFO.DOWN += 1
            elif position == 'left':
                INFO.LEFT += 1
            elif position == 'right':
                INFO.RIGHT += 1
            else:
                raise UnExpectedValueException()
            h_offset = INFO.UP - INFO.DOWN
            h_step = step * h_offset
            v_offset = INFO.LEFT - INFO.RIGHT
            v_step = step * v_offset
            beginH = beginH + height * h_step
            endH = endH + height * h_step
            if beginH < 0:
                beginH = 0
            if endH > height:
                endH = height
            if beginW < 0:
                beginW = 0
            if endW > width:
                endW = width
            beginW = beginW + width * v_step
            endW = endW + width * v_step
    if beginH < endH and beginW < endW:
        new_img = img[beginH:endH, beginW:endW]
    else:
        new_img = img[endH:beginH, endW:beginW]
    return new_img


def resize(img, h, w):
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)


def clahe(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(img)
    return cl


def shape(img):
    height, width = img.shape[:2]
    return (height, width)


def drawlines(img, h_lines, v_lines, datas, color = (0, 0, 0), px = 1, img_type = 'nm'):
    vis = img.copy()
    height, width = vis.shape[:2]
    font = cv2.FONT_HERSHEY_PLAIN
    if img_type == 'ir':
        offheight = float(datas['ir_down'] - datas['ir_up']) * height / v_lines
        offwidth = float(datas['ir_right'] - datas['ir_left']) * width / h_lines
        up = int(datas['ir_up'] * height)
        right = int(datas['ir_right'] * width)
        down = int(datas['ir_down'] * height)
        left = int(datas['ir_left'] * width)
    else:
        offheight = float(datas['down'] - datas['up']) * height / v_lines
        offwidth = float(datas['right'] - datas['left']) * width / h_lines
        up = int(datas['up'] * height)
        right = int(datas['right'] * width)
        down = int(datas['down'] * height)
        left = int(datas['left'] * width)
    for i in range(1, v_lines + 1):
        cv2.line(vis, (left, int(up + i * offheight)), (right, int(up + i * offheight)), color, px)

    for i in range(1, h_lines + 1):
        cv2.line(vis, (int(left + i * offwidth), up), (int(left + i * offwidth), down), color, px)

    return vis


def merge_image(imglist):
    first = imglist[0]
    h, w = first.shape[:2]
    for img in imglist:
        img = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)

    vis = np.concatenate(tuple(imglist), axis=1)
    return vis


def move_to_center(face, center_x):
    height, width = face.shape[:2]
    target = width / 2
    logging.info(u'\u5f00\u59cb\u8c03\u6574\u5230\u4e2d\u95f4\uff0c\u8ddd\u79bb\u4e3a%s...' % abs(target - center_x))
    if target > center_x:
        face = cv2.copyMakeBorder(face, 0, 0, target - center_x, 0, cv2.BORDER_REFLECT)
        height, width = face.shape[:2]
        return (face[0:height, 0:width - target + center_x], target - center_x)
    elif target < center_x:
        face = cv2.copyMakeBorder(face, 0, 0, 0, center_x - target, cv2.BORDER_REFLECT)
        height, width = face.shape[:2]
        return (face[0:height, center_x - target:width], target - center_x)
    else:
        return (face, 0)


def cut_img(face, start_x, end_x, start_y, end_y):
    height, width = face.shape[:2]
    start_x = int(start_x * width)
    end_x = int(end_x * width)
    start_y = int(start_y * height)
    end_y = int(end_y * height)
    cut_img = face[start_y:end_y, start_x:end_x]
    return cut_img


def roi_grayvalue(face, start_x, end_x, start_y, end_y, rounds = None):
    roi_img = cut_img(face, start_x, end_x, start_y, end_y)
    value = gray_value(roi_img)
    if not rounds:
        return value
    return round(value, 2)


def showplt(img):
    from matplotlib.font_manager import FontProperties
    font = FontProperties(fname='c:\\windows\\fonts\\simsun.ttc', size=14)
    hist_full = cv2.calcHist([img], [0], None, [256], [0, 256])
    (plt.subplot(211), plt.imshow(img, 'gray'), plt.title(u'\u7ed3\u679c', fontproperties=font))
    (plt.subplot(212), plt.plot(hist_full, 'gray'), plt.xlim([0, 256]))
    plt.xlabel(u'\u7070\u5ea6\u8303\u56f4', fontproperties=font)
    plt.ylabel(u'\u50cf\u7d20\u6570\u91cf', fontproperties=font)
    plt.show()


def affine_transform(img, ori_loc, dst_loc):
    new_img = img.copy()
    h, w = new_img.shape[:2]
    pts1 = np.float32(ori_loc)
    pts2 = np.float32(dst_loc)
    M = cv2.getPerspectiveTransform(pts1, pts2)
    new_img = cv2.warpPerspective(new_img, M, (w, h))
    return new_img


def find_eyes(face):
    eyepos = []
    height, width = face.shape[:2]
    eyes = get_organs(face).get_eyes()
    if len(eyes) != 0:
        for ex, ey, ew, eh in eyes:
            eyepos.append((ex + ew / 2, ey + eh / 2))

    if len(eyepos) == 2:
        eyepos = sorted(eyepos, key=lambda eye: eye[0])
        leye = eyepos[0]
        reye = eyepos[1]
        pos_tuple = (leye, reye)
        return pos_tuple


def adjustface(face, find = False, zoom_factor = 0):
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    height, width = face.shape[:2]
    if find == True:
        face_ = face_cascade.detectMultiScale(face)
        if len(face_) != 0:
            face_ = sorted(face_, key=lambda item: item[2])[-1]
            face = face[face_[0]:face_[0] + face_[2], face_[1]:face_[1] + face_[2]]
    eyepos = find_eyes(face)
    if eyepos:
        logging.info(u'\u5f00\u59cb\u77b3\u5b54\u9501\u5b9a...')
        leye = eyepos[0]
        reye = eyepos[1]
        yy = math.fabs(leye[1] - reye[1])
        xx = math.fabs(leye[0] - reye[0])
        degree = math.degrees(math.atan(yy / xx))
        if degree > 5:
            degree = degree if reye[1] > leye[1] else -degree
            M = cv2.getRotationMatrix2D((width / 2, height / 2), degree, 1)
        else:
            M = cv2.getRotationMatrix2D((width / 2, height / 2), 0, 1)
        face = cv2.warpAffine(face, M, (width, height))
        scale = 0.0
        if zoom_factor > 0:
            distance = leye[0] - reye[0] if leye[0] > reye[0] else reye[0] - leye[0]
            proportion = float(distance) / width
            scale = (width - distance / zoom_factor) / (2 * width)
            face = enlargeimage(face, scale)
            logging.info(u'\u7f29\u653e\u56e0\u5b50\u4e3a\uff1a{}'.format(zoom_factor))
            logging.info(u'\u8c03\u6574\u56fe\u7247\u89d2\u5ea6...')
        logging.info(u'\u8c03\u6574\u56fe\u7247\u6210\u529f\uff01')
        return (face, scale)
    else:
        return (face, None)


def gray_to_pseudo(gray_val):
    if gray_val > 255 or gray_val < 0:
        logging.error(u'\u9519\u8bef\u7684\u7070\u5ea6\u503c\u8303\u56f4\uff0c\u65e0\u6cd5\u8f6c\u6362\u5bf9\u5e94\u4f2a\u5f69\u8272')
        raise UnExpectedValueException('\xe9\x94\x99\xe8\xaf\xaf\xe7\x9a\x84\xe7\x81\xb0\xe5\xba\xa6\xe8\x8c\x83\xe5\x9b\xb4')
    R = G = B = None
    c = gray_val / 64
    if c == 0:
        R = 0
        G = gray_val * 4
        B = 255
    elif c == 1:
        R = 0
        G = 255
        B = 511 - gray_val * 4
    elif c == 2:
        R = gray_val * 4 - 511
        G = 255
        B = 0
    elif c == 3:
        R = 255
        G = 1023 - gray_val * 4
        B = 0
    if R is not None and G is not None and B is not None:
        return (R, G, B)


def pick_skin(face, skinMask = None):
    if skinMask is None:
        lower = np.array([0, 48, 80], dtype='uint8')
        upper = np.array([20, 255, 255], dtype='uint8')
        converted = cv2.cvtColor(face, cv2.COLOR_BGR2HSV)
        skinMask = cv2.inRange(converted, lower, upper)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        skinMask = cv2.erode(skinMask, kernel, iterations=2)
        skinMask = cv2.dilate(skinMask, kernel, iterations=2)
        skinMask = cv2.GaussianBlur(skinMask, (3, 3), 0)
    skin = cv2.bitwise_and(face, face, mask=skinMask)
    return (skin, skinMask)


def read(path, gray = False):
    if isinstance(path, unicode):
        path = path.encode('gbk')
    if gray:
        img = cv2.imread(path, 0)
    else:
        img = cv2.imread(path)
    if img is None:
        raise ImageNotFound('\xe5\x9b\xbe\xe7\x89\x87\xe4\xb8\x8d\xe5\xad\x98\xe5\x9c\xa8')
    return img


def write(dst, img):
    cv2.imwrite(dst, img)


def convert(img, mode = cv2.COLOR_BGR2GRAY):
    vis = cv2.cvtColor(img, mode)
    if vis is not None:
        return vis
    else:
        return img


def show(img, title = 'img', size = (500, 400)):
    while True:
        img = resize(img, size[0], size[1])
        cv2.imshow(title, img)
        if cv2.waitKey(0) & 255 in (-1, 27, 255):
            break

    cv2.destroyAllWindows()


def gray_value(gray, extract = False):
    if extract:
        gray = gray[gray != 0]
    return gray.mean()


def gray_value_filter(gray, low_bound, up_bound):
    gray = gray[(gray > low_bound) & (gray < up_bound)]
    return gray.mean()


def grab_cut(face):
    height, width = face.shape[:2]
    mask = np.zeros(face.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    rect = get_organs(face).get_face()
    cv2.grabCut(face, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
    face = face * mask2[:, :, np.newaxis]
    _, face = cv2.threshold(face, 50, 255, cv2.THRESH_TOZERO)
    face = np.ma.masked_equal(face, 0)
    return face


def _memory_study(function):

    @wraps(function)
    def __memory_study(*args, **kw):
        result = function(*args, **kw)
        linesArr, _, status = result
        if status is False:
            return result
        try:
            STUDY_FILE = 'memory.pkl'
            if os.path.exists(STUDY_FILE) == False:
                with open(STUDY_FILE, 'wb') as pkl:
                    pickle.dump((linesArr, 1), pkl)
            else:
                with open(STUDY_FILE, 'rb') as memory_file:
                    m_linesArr, count = pickle.load(memory_file)
                    VLines = sorted([ line for line in linesArr if line['y'] == 0 ], key=lambda x: x['x'])
                    HLines = sorted([ line for line in linesArr if line['x'] == 0 ], key=lambda x: x['y'])
                    m_VLines = sorted([ line for line in m_linesArr if line['y'] == 0 ], key=lambda x: x['x'])
                    m_HLines = sorted([ line for line in m_linesArr if line['x'] == 0 ], key=lambda x: x['y'])
                for now, memory in zip(VLines, m_VLines):
                    memory['x'] = (now['x'] + memory['x'] * count) / (count + 1)

                for now, memory in zip(HLines, m_HLines):
                    memory['y'] = (now['y'] + memory['y'] * count) / (count + 1)

                m_linesArr = m_VLines + m_HLines
                with open(STUDY_FILE, 'wb') as memory_file:
                    pickle.dump((m_linesArr, count + 1), memory_file)
        finally:
            return result

    return __memory_study


def get_organs(face):
    height, width = face.shape[:2]

    def _f():
        pass

    def get_face():
        face_ = face_cascade.detectMultiScale(face, 1.3, 5)
        face = [ f for f in faces if f[2] > width / 3 and f[3] > height / 3 ]
        if len(face) == 1:
            for x, y, w, h in faces:
                rect = (x,
                 y,
                 w,
                 h)

        else:
            rect = (width / 4,
             height / 4,
             width * 3 / width,
             height * 3 / 4)
        return rect

    def get_mouths():
        mouths = []
        mouths = mouth_cascade.detectMultiScale(face)
        mouths = [ mouth for mouth in mouths if width / 3 < _mid_x(mouth) < width * 2 / 3 and _mid_y(mouth) > height * 3 / 5 ]
        mouths = sorted(mouths, key=lambda mouth: mouth[1])[:1]
        return mouths

    def get_noses():
        noses = []
        noses = nose_cascade.detectMultiScale(face)
        noses = [ nose for nose in noses if width * 2 / 3 > _mid_x(nose) > width * 1 / 3 and width / 3 > nose[2] > width / 8 and height / 4 < _mid_y(nose) < height * 3 / 4 ]
        return noses

    def get_eyes():
        eyes = []
        eyes = eye_cascade.detectMultiScale(face)
        eyes = [ eye for eye in eyes if eye[1] > height / 4 and height / 4 < _mid_y(eye) < height * 2 / 3 ]
        eyes = sorted(eyes, key=lambda eye: eye[1])[:2]
        eyes = sorted(eyes, key=lambda eye: eye[0])
        return eyes

    _f.get_face = get_face
    _f.get_mouths = get_mouths
    _f.get_noses = get_noses
    _f.get_eyes = get_eyes
    return _f


@_memory_study
def markdetect(face, face_path = None):
    C = _const()
    C.BROW_UP = 0.3
    C.BROW_DN = 0.35
    C.EYE_UP = 0.4
    C.EYE_DN = 0.45
    C.EYE_RT = 0.65
    C.EYE_CT = 0.6
    C.EYE_LT = 0.57
    C.NOSE_CT = 0.6
    C.NOSE_DN = 0.66
    C.NOSE_CL = 0.45
    C.NOSE_CR = 0.52
    C.MOUTH_UP = 0.62
    C.MOUTH_DN = 0.7
    DARWEIGHT = 1
    detect_status = True
    linesArr = []
    height, width = face.shape[:2]
    keyPoints = {'left_bound': {'x': int(width * 0.3)},
     'right_bound': {'x': int(width * 0.7)},
     'up_bound': {'y': int(height * 0.18)},
     'down_bound': {'y': int(height * 0.78)},
     'center': int(width / 2.0)}
    eye_left = eye_right = nose = mouth_left = mouth_right = None
    round3 = partial(round, ndigits=3)
    data = net.get_facepp_data(face_path)
    face_pos = faceutil.get_facepp_pos(data)
    if data is not None and face_pos is not None:
        logging.info(u'\u542f\u7528\u4e91\u7aefAPI\u5206\u6790\u7ed3\u679c...')
        eye_left, eye_right, nose, mouth_left, mouth_right = face_pos
        right_bound_x = int((eye_right['x'] + 0.05) * width)
        keyPoints['right_bound']['x'] = right_bound_x if right_bound_x < width else width - 10
        keyPoints['right_bound']['y'] = int(eye_right['y'] * height)
        left_bound_x = int((eye_left['x'] - 0.05) * width)
        keyPoints['left_bound']['x'] = left_bound_x if left_bound_x > 0 else 10
        keyPoints['left_bound']['y'] = int(eye_left['y'] * height)
        keyPoints['up_bound']['x'] = int((eye_left['x'] + eye_right['x']) / 2 * width)
        up_bound_y = int((eye_right['y'] - 0.25) * height)
        keyPoints['up_bound']['y'] = up_bound_y if up_bound_y > 0 else 10
        keyPoints['down_bound']['x'] = int((mouth_left['x'] + mouth_right['x']) / 2 * width)
        down_bound_y = int((mouth_right['y'] + 0.13) * height)
        keyPoints['down_bound']['y'] = down_bound_y if down_bound_y < height else height - 10
        keyPoints['center'] = int(nose['x'] * width)
        begin = round(eye_right['y'], 3)
        end = round(mouth_right['y'], 3) + 0.13
        step = (end - begin) / 6.0
        l_begin = round(eye_left['x'], 3) - 0.05
        l_end = 0.55
        r_begin = 0.65
        r_end = 0.85
        linesArr.append({'x': 0,
         'y': begin,
         'label': 'a'})
        linesArr.append({'x': 0,
         'y': begin + step,
         'label': 'b'})
        linesArr.append({'x': 0,
         'y': begin + step * 2,
         'label': 'c'})
        linesArr.append({'x': 0,
         'y': begin + step * 3,
         'label': 'd'})
        linesArr.append({'x': 0,
         'y': begin + step * 4,
         'label': 'e'})
        linesArr.append({'x': 0,
         'y': begin + step * 5,
         'label': 'f'})
        linesArr.append({'x': 0,
         'y': end,
         'label': 'g'})
        linesArr.append({'x': l_begin,
         'y': 0,
         'label': '1'})
        linesArr.append({'x': l_end,
         'y': 0,
         'label': '2'})
        linesArr.append({'x': r_begin,
         'y': 0,
         'label': '3'})
        linesArr.append({'x': r_end,
         'y': 0,
         'label': '4'})
    else:
        begin = 0.45
        end = 0.75
        step = (end - begin) / 6.0
        l_begin = 0.3
        l_end = 0.55
        r_begin = 0.65
        r_end = 0.8
        linesArr.append({'x': 0,
         'y': begin,
         'label': 'a'})
        linesArr.append({'x': 0,
         'y': begin + step,
         'label': 'b'})
        linesArr.append({'x': 0,
         'y': begin + step * 2,
         'label': 'c'})
        linesArr.append({'x': 0,
         'y': begin + step * 3,
         'label': 'd'})
        linesArr.append({'x': 0,
         'y': begin + step * 4,
         'label': 'e'})
        linesArr.append({'x': 0,
         'y': begin + step * 5,
         'label': 'f'})
        linesArr.append({'x': 0,
         'y': end,
         'label': 'g'})
        linesArr.append({'x': l_begin,
         'y': 0,
         'label': '1'})
        linesArr.append({'x': l_end,
         'y': 0,
         'label': '2'})
        linesArr.append({'x': r_begin,
         'y': 0,
         'label': '3'})
        linesArr.append({'x': r_end,
         'y': 0,
         'label': '4'})
    return (linesArr, keyPoints, detect_status)
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.12 22:10:40 中国标准时间
