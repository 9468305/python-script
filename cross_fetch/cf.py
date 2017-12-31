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

CTOOL_API = r'https://so.ctool.cc/api/api.php?ver=3&kw={}&page={}&num={}&site={}'
CTOOL_PAGE = 1
CTOOL_NUM = 20


def ctool(session, keyword, page, num, site):
    '''
    GET ctool url + params
    '''
    kw_string = ' '.join(keyword)
    kw_param = base64.b64encode(kw_string.encode()).decode()
    _url = CTOOL_API.format(kw_param, page, num, site)
    _response = session.get(_url)
    logging.debug('Response code = ' + str(_response.status_code))
    if _response.status_code != 200:
        return None
    _json_text = base64.b64decode(_response.text).decode()
    _json_obj = json.loads(_json_text)
    logging.debug(_json_obj)
    return _json_obj


def cross_fetch(keyword, site):
    '''Cross fetch keyword by Search Engine.'''
    with requests.Session() as session:
        fetch = ctool(session, keyword, CTOOL_PAGE, CTOOL_NUM, site)
        keyword.reverse()
        cross = ctool(session, keyword, CTOOL_PAGE, CTOOL_NUM, site)
        #TODO Add cross verify
        #TODO ctool API fail


if __name__ == "__main__":
    KEYWORD = ['腾讯科技（深圳）有限公司', '统一社会信用代码']
    SITE = ''
    cross_fetch(KEYWORD, SITE)
