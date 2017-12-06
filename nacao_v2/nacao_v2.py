#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''
全国组织机构代码管理中心
http://www.nacao.org.cn/
全国统一社会信用代码信息校核结果公示系统
http://www.dmedu.org.cn/query.do
'''

import json
import logging
from logging import NullHandler
import requests
import constants

logging.getLogger(__name__).addHandler(NullHandler())
logging.basicConfig(level=logging.INFO)

HOST = 'http://www.dmedu.org.cn'

# 有时响应很慢，需要随时调整超时阈值
TIMEOUT = 20

def post_query(session, keyword, current_page):
    '''分页获取keyword json数据'''
    _url = HOST + '/query.do'
    logging.debug('POST ' + _url)
    _headers = {'Accept': constants.ACCEPT_ANY,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                #'Referer': referer,
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': HOST}
    _params = [('pageSize', 100),
               ('searchText', keyword),
               ('searchType', 3),
               ('DJBMBM', ''),
               ('sortField', ''),
               ('currentPage', current_page if current_page > 1 else '')]
    _response = session.post(_url, headers=_headers, data=_params, timeout=TIMEOUT)
    logging.debug('response code: ' + str(_response.status_code))
    logging.debug('response text: ' + _response.text)
    return _response.json() if _response.status_code == 200 else None


def query_keyword(session, keyword):
    '''查询关键字'''
    _current_page = 0
    _total_page = 5 # Max
    while _current_page < _total_page:
        _current_page += 1
        _json_obj = post_query(session, keyword, _current_page)
        if _json_obj:
            _total_page = _json_obj['totalPage']
            print(json.dumps(_json_obj, indent=2, sort_keys=True, ensure_ascii=False))
        else:
            break


def query():
    '''query entry'''
    try:
        with requests.Session() as session:
            # * 就是通配符, 可替换成任意公司名称, 该接口可能存在SQL注入漏洞, 未深入验证。
            query_keyword(session, '*')
    except requests.RequestException as _e:
        logging.error(_e)


if __name__ == "__main__":
    query()
