#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''
geetest offline 5.9.0 - 6.0.0 spider for nm.gsxt.gov.cn
HTTP协议与其他站点略有不同
'''

import time
import random
import logging
from logging import NullHandler
import requests
import execjs
from bs4 import BeautifulSoup
import constants
import util

logging.getLogger(__name__).addHandler(NullHandler())
logging.basicConfig(level=logging.DEBUG)

HOST = ''
INDEX = ''

JSRUNTIME = execjs.get(execjs.runtime_names.Node)

CAPTCHA_JSON = []

USERRESPONSE_JSCONTEXT = JSRUNTIME.compile(util.USERRESPONSE_JS)

TIMEOUT = 10

GSXT_HOST_NM = 'http://nm.gsxt.gov.cn:58888'
GSXT_INDEX_NM = GSXT_HOST_NM + '/'

def config(host, index):
    '''设置 host and index URL'''
    global HOST, INDEX
    HOST, INDEX = host, index


def calc_userresponse(distance, challenge):
    '''根据滑动距离distance和challenge，计算userresponse值'''
    return USERRESPONSE_JSCONTEXT.call('userresponse', distance, challenge)


def calc_validate(challenge):
    '''计算validate值'''
    _r = random.randint(0, len(util.OFFLINE_SAMPLE)-1)
    distance, rand0, rand1 = util.OFFLINE_SAMPLE[_r]
    distance_r = calc_userresponse(distance, challenge)
    rand0_r = calc_userresponse(rand0, challenge)
    rand1_r = calc_userresponse(rand1, challenge)
    validate = distance_r + '_' + rand0_r + '_' + rand1_r
    logging.debug(validate)
    return validate


def parse_code(html_doc):
    '''使用BeautifulSoup解析HTML页面,查找统一社会信用代码,查找代码总数(下一页)'''
    _soup = BeautifulSoup(html_doc, 'html.parser')
    # find result number
    _span = _soup.find('span', attrs={'style': 'color: red'})
    _number = int(''.join(_span.get_text().split())) if _span else 0
    logging.debug('page number = ' + str(_number))
    if not _number:
        logging.error('Number Not Found')
        return None, 0

    _div_all = _soup.find_all('div', class_='clickStyle', attrs={'onclick': 'details(this)'})
    _result = []
    if _div_all:
        for _div in _div_all:
            _a = _div.find('a', class_='font16', attrs={'target': '_blank'})
            _a_str = _a.get_text()
            _td = _div.find('td', attrs={'style': 'width: 35%'})
            _span = _td.find('span', class_='dataTextStyle')
            _span_str = ''.join(_span.get_text().split())
            _result.append((_a_str.encode('utf-8'), _span_str.encode('utf-8')))
    else:
        logging.info('Code Not Found')
        logging.info(html_doc)
    return _result, _number


def get_main(session):
    '''Get gsxt 首页'''
    _url = INDEX
    logging.debug('GET ' + _url)
    _headers = {'Accept': constants.ACCEPT_HTML,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT}
    _response = session.get(_url, headers=_headers, timeout=TIMEOUT)
    logging.debug('response code:' + str(_response.status_code))
    return _response.status_code == 200


def get_verify_start(session):
    '''
    {"success": 0,
	 "gt": "39134c54afef1e0b19228627406614e9",
	 "challenge": "fc490ca45c00b1249bbe3554a4fdf6fb35"}
    '''
    _url = INDEX + '/verify/start.html'
    logging.debug('GET ' + _url)
    _headers = {'Accept': constants.ACCEPT_JSON,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': INDEX,
                'X-Requested-With': 'XMLHttpRequest'}
    _params = {'v': str(int(time.time() * 1000))}
    _response = session.get(_url, headers=_headers, params=_params, timeout=TIMEOUT)
    logging.debug('response code: ' + str(_response.status_code))
    logging.debug('response text: ' + _response.text)
    if _response.status_code != 200:
        return False
    global CAPTCHA_JSON
    CAPTCHA_JSON = _response.json()
    return True


def post_verify_sec(session, validate, keyword):
    '''	POST /verify/sec.html'''
    _url = INDEX + 'verify/sec.html'
    logging.debug('POST ' + _url)
    _headers = {'Accept': constants.ACCEPT_JSON,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': INDEX,
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': HOST}
    _params = [('textfield', keyword),
               ('geetest_challenge', CAPTCHA_JSON['challenge']),
               ('geetest_validate', validate),
               ('geetest_seccode', validate + '|jordan')]
    _response = session.post(_url, headers=_headers, data=_params, timeout=TIMEOUT)
    logging.debug('response code: ' + str(_response.status_code))
    logging.debug('response text: ' + _response.text)
    if _response.status_code != 200:
        return None
    _json_obj = _response.json()
    logging.debug(_json_obj)
    return _json_obj['textfield'] if _json_obj['status'] == 'success' else None


def post_search(session, textfield, page):
    '''	POST /CheckEntContext/showCheck.html'''
    _url = INDEX + 'CheckEntContext/showCheck.html'
    logging.debug('POST ' + _url)
    _headers = {'Accept': constants.ACCEPT_HTML,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': INDEX,
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': HOST}
    _params = [('textfield', textfield),
               ('type', 'nomal')]
    if page > 1:
        _params.append(('total', ''))
        _params.append(('pageNo', page))

    _response = session.post(_url, headers=_headers, data=_params, timeout=TIMEOUT)
    logging.debug('response code: ' + str(_response.status_code))
    #logger.debug('response text: ' + _response.text)
    if _response.status_code != 200:
        return None, None
    return parse_code(_response.text)


def get_validate(session, keyword):
    '''循环进行validate验证'''
    for _ in range(10):
        if not get_verify_start(session):
            return None

        validate = calc_validate(CAPTCHA_JSON['challenge'])
        textfield = post_verify_sec(session, validate, keyword)
        if textfield:
            return textfield
    return None


def query_keyword(session, keyword):
    '''使用session, 查询keyword, 更新session.token'''
    if not get_main(session):
        return None

    textfield = get_validate(session, keyword)
    if not textfield:
        return None

    _code_all = []
    _number = 50 # max result number
    _page = 0 # start page number
    while _page * 10 < _number:
        _page += 1
        _code, _number = post_search(session, textfield, _page)
        if _code:
            _code_all.extend(_code)
        else:
            break

    return _code_all


def query_leveldb(query_db, save_db, queryed_db):
    '''query by leveldb'''
    try:
        with requests.Session() as session:
            for _name, _code in query_db.RangeIter():
                if not util.has_key(save_db, _name) and not util.has_key(queryed_db, _name):
                    # 模糊查询
                    _subname = _name[0: 18] if len(_name) > 18 else _name
                    logging.info(_name + ' -> ' + _subname)
                    _code_all = query_keyword(session, _subname)
                    if _code_all:
                        for _c in _code_all:
                            logging.info(_c[0] + ' : ' + _c[1])
                            save_db.Put(_c[0], _c[1], sync=True)
                    queryed_db.Put(_name, '', sync=True)
        return True
    except requests.RequestException as _e:
        logging.error(_e)
        return False


def query_keyword_helper(keyword):
    '''根据keyword查询一次'''
    try:
        with requests.Session() as session:
            _code_all = query_keyword(session, keyword)
            if _code_all:
                logging.info(len(_code_all))
                for _r in _code_all:
                    logging.info(_r[0].decode() + ' : ' + _r[1].decode())
    except requests.RequestException as _e:
        logging.error(_e)


if __name__ == "__main__":
    config(GSXT_HOST_NM, GSXT_INDEX_NM)
    query_keyword_helper('百度')
