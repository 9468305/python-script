#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''
Cross Search and Verification by Google Search Engine.
Thanks to https://so.ctool.cc/api/
'''

import base64
import json
import logging
from logging import NullHandler
import requests

logging.getLogger(__name__).addHandler(NullHandler())
logging.basicConfig(level=logging.DEBUG)

CTOOL_API = r'https://so.ctool.cc/api/api.php?ver=3&kw={}&page={}&num={}'
CTOOL_VER = 3
CTOOL_PAGE = 1
CTOOL_NUM = 20


def ctool(session, keyword, page, num, site):
    '''
    GET ctool by params
    '''
    kw = base64.b64encode(keyword.encode()).decode()
    _url = CTOOL_API.format(kw, page, num)
#    params = [('ver', CTOOL_VER),
#              ('kw', base64.b64encode(keyword.encode())),
#              ('page', page),
#              ('num', num)]
#    if site:
#        params.append(['site', site])
    _response = session.get(_url)
    logging.debug('Response code = ' + str(_response.status_code))
    if _response.status_code != 200:
        return None
    _json = base64.b64decode(_response.text).decode()
    logging.debug(_json)
    return _json


def cross_fetch(keyword, site):
    '''Fetch keyword by Search Engine.'''
    with requests.Session() as session:
        kw_string = ' '.join(keyword)
        _result = ctool(session, kw_string, CTOOL_PAGE, CTOOL_NUM, site)
        fetch = json.loads(_result, encoding='utf-8')
        logging.debug(fetch)

        keyword.reverse()
        kw_string = ' '.join(keyword)
        _result = ctool(session, kw_string, CTOOL_PAGE, CTOOL_NUM, site)
        cross = json.loads(_result, encoding='utf-8')
        logging.debug(cross)


if __name__ == "__main__":
    KEYWORD = ['腾讯科技（深圳）有限公司', '统一社会信用代码']
    SITE = ''
    cross_fetch(KEYWORD, SITE)
