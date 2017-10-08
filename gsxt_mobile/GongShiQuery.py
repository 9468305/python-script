#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''通过国家企业信用信息公示系统(www.gsxt.gov.cn) Mobile App HTTP API 查询统一社会信用代码'''

import json
import requests

URL = 'http://yd.gsxt.gov.cn/QuerySummary'
MOBILE_ACTION = 'entSearch'
TOPIC = 1
PAGE_NUM = 1
PAGE_SIZE = 10
USER_ID = 'id001'
USER_IP = '192.168.0.1'
USER_AGENT = 'Mozilla/5.0 (Linux; Android 4.4.2; vivo Y28L Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36 Html5Plus/1.0'
ACCEPT_LANGUAGE = 'zh-CN,en-US;q=0.8'
XRW = 'com.zongjucredit'
ORIGIN = 'file://'
CHARSET = 'application/x-www-form-urlencoded; charset=UTF-8'


def main(keyword):
    '''main entry'''
    _data = [('mobileAction', MOBILE_ACTION),
             ('keywords', keyword),
             ('topic', TOPIC),
             ('pageNum', PAGE_NUM),
             ('pageSize', PAGE_SIZE),
             ('userID', USER_ID),
             ('userIP', USER_IP)]

    _headers = {'User-Agent': USER_AGENT,
                'Accept-Language': ACCEPT_LANGUAGE,
                'X-Requested-With': XRW,
                'Origin': ORIGIN,
                'Content-Type': CHARSET}

    _response = requests.post(URL, data=_data, headers=_headers)
    print(_response.status_code)
    if _response.status_code == 200:
        _content = _response.json()
        print(json.dumps(_content, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print('request fail')

if __name__ == "__main__":
    KEY_WORD = '腾讯科技'
    main(KEY_WORD)
