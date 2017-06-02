# -*- coding: utf-8 -*-
'''Query Uniform-Social-Credit-Code from National-Enterprise-Credit-Information-Publicity-System.'''

import json
import requests

if __name__ == "__main__":
    URL = 'http://yd.gsxt.gov.cn/QuerySummary'
    MOBILE_ACTION = 'entSearch'
    KEY_WORDS = '腾讯科技'
    TOPIC = 1
    PAGE_NUM = 1
    PAGE_SIZE = 10
    USER_ID = 'id001'
    USER_IP = '192.168.0.1'
    DATA = [('mobileAction', MOBILE_ACTION),
            ('keywords', KEY_WORDS),
            ('topic', TOPIC),
            ('pageNum', PAGE_NUM),
            ('pageSize', PAGE_SIZE),
            ('userID', USER_ID),
            ('userIP', USER_IP)]

    USER_AGENT = 'Mozilla/5.0 (Linux; Android 4.4.2; vivo Y28L Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36 Html5Plus/1.0'
    ACCEPT_LANGUAGE = 'zh-CN,en-US;q=0.8'
    XRW = 'com.zongjucredit'
    ORIGIN = 'file://'
    CHARSET = 'application/x-www-form-urlencoded; charset=UTF-8'

    HEADERS = {'User-Agent': USER_AGENT,
               'Accept-Language': ACCEPT_LANGUAGE,
               'X-Requested-With': XRW,
               'Origin': ORIGIN,
               'Content-Type': CHARSET}

    RESPONSE = requests.post(URL, data=DATA, headers=HEADERS)
    print RESPONSE.status_code
    if RESPONSE.status_code == 200:
        CONTENT = RESPONSE.json()
        print json.dumps(CONTENT, indent=2, sort_keys=True, ensure_ascii=False)
    else:
        print 'request fail'
