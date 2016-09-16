#-*- coding:utf-8 -*-
# 2016.09.16 17:26:12 中国标准时间
#Embedded file name: c:\Users\hp\Desktop\backup\net.py
from facepp import facepp
import requests
import json
import os
import util
API_KEY = '7a8d67c943a51cb72145b2a5eda4f596'
API_SECRET = '9bcs2h6WERlNngFl9BlR6Qrbw7BMg8vD'

def get_facepp_api():
    api = facepp.API(API_KEY, API_SECRET)
    return api


def get_facepp_data(path):
    data = None
    if os.path.getsize(path) > 1000000:
        util.warn_dialog(text='\xe5\x9b\xbe\xe7\x89\x87\xe5\xa4\xa7\xe5\xb0\x8f\xe8\xbf\x87\xe5\xa4\xa7\xef\xbc\x81\xe8\xaf\xb7\xe9\x80\x89\xe6\x8b\xa91M\xe4\xbb\xa5\xe4\xb8\x8b\xe7\x9a\x84\xe5\x9b\xbe\xe7\x89\x87')
        return
    files = {'img': open(path, 'rb')}
    url = 'http://api.cn.faceplusplus.com/detection/detect?api_secret=%s&api_key=%s&mode=oneface' % (API_SECRET, API_KEY)
    count = 2
    while 1:
        try:
            r = requests.post(url=url, files=files, timeout=5)
        except requests.exceptions.Timeout:
            count -= 1
            if count == 0:
                return
            continue
        except Exception:
            return

        break

    data = r.text
    if isinstance(data, unicode):
        data = data.encode('utf-8')
    data = json.loads(data)
    return data


def check_net():
    return requests.head('http://www.163.com').status_code == 200
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2016.09.16 17:26:12 中国标准时间
