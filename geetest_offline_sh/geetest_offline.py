#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
against geetest offline 5.9.0
for gsxt 上海 河北
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


def parse_token(html_doc):
    '''使用BeautifulSoup解析HTML页面, 查找session.token'''
    soup = BeautifulSoup(html_doc, 'html.parser')
    _find = soup.find('input', attrs={'name': 'session.token'})
    return _find['value'] if _find else None


def parse_code(html_doc):
    '''使用BeautifulSoup解析HTML页面，查找统一社会信用代码'''
    _soup = BeautifulSoup(html_doc, 'html.parser')
    _findall = _soup.find_all('div', class_='tableContent page-item')
    _result = []
    if _findall:
        for _a in _findall:
            _td = _a.find('td')
            _td_str = ''.join(_td.get_text().split())
            _i = _a.find('i')
            _i_str = ''.join(_i.get_text().split())
            _td_str = _td_str[0: -len(_i_str)]
            _th = _a.find('th', class_='icon1')
            _em = _th.find('em')
            _result.append((_td_str.encode('utf-8'), _em.get_text().encode('utf-8')))
    else:
        logging.info('Code Not Found')
    return _result


def get_main(session):
    '''Get gsxt 首页'''
    _url = INDEX
    logging.debug('GET ' + _url)
    _headers = {'Accept': constants.ACCEPT_HTML,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT}
    _response = session.get(_url, headers=_headers, timeout=TIMEOUT)
    logging.debug('response code:' + str(_response.status_code))
    return parse_token(_response.text) if _response.status_code == 200 else None


def get_register(session):
    '''
    {"success": 0,
	 "gt": "39134c54afef1e0b19228627406614e9",
	 "challenge": "fc490ca45c00b1249bbe3554a4fdf6fb35"}
    '''
    _url = INDEX + 'pc-geetest/register'
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


def post_verify_ip(session):
    '''	POST /notice/security/verify_ip'''
    _url = INDEX + 'security/verify_ip'
    logging.debug('POST ' + _url)
    _headers = {'Accept': constants.ACCEPT_TEXT,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': INDEX,
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': HOST}
    _response = session.post(_url, headers=_headers, timeout=TIMEOUT)
    logging.debug('response code: ' + str(_response.status_code))
    logging.debug('response text: ' + _response.text)
    return _response.status_code == 200


def post_verify_keyword(session, keyword):
    '''	POST /notice/security/verify_keyword HTTP/1.1'''
    _url = INDEX + 'security/verify_keyword'
    logging.debug('POST ' + _url)
    _headers = {'Accept': constants.ACCEPT_TEXT,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': INDEX,
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': HOST}
    _params = {'keyword': keyword}
    _response = session.post(_url, headers=_headers, data=_params, timeout=TIMEOUT)
    logging.debug('response code: ' + str(_response.status_code))
    logging.debug('response text: ' + _response.text)
    return _response.status_code == 200


def post_validate(session, validate):
    '''	POST /notice/pc-geetest/validate'''
    _url = INDEX + 'pc-geetest/validate'
    logging.debug('POST ' + _url)
    _headers = {'Accept': constants.ACCEPT_JSON,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': INDEX,
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': HOST}
    _params = [('geetest_challenge', CAPTCHA_JSON['challenge']),
               ('geetest_validate', validate),
               ('geetest_seccode', validate + '|jordan')]
    _response = session.post(_url, headers=_headers, data=_params, timeout=TIMEOUT)
    logging.debug('response code: ' + str(_response.status_code))
    logging.debug('response text: ' + _response.text)
    if _response.status_code != 200:
        return False
    _json_obj = _response.json() # {"status":"success","version":"3.3.0"}
    logging.debug(_json_obj)
    return _json_obj['status'] == 'success'


def post_search(session, validate, keyword, token):
    '''	POST /notice/search/ent_info_list HTTP/1.1'''
    _url = INDEX + 'search/ent_info_list'
    logging.debug('POST ' + _url)
    _headers = {'Accept': constants.ACCEPT_HTML,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': INDEX,
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': HOST}
    _params = [('condition.searchType', 1),
               ('captcha', ''),
               ('geetest_challenge', CAPTCHA_JSON['challenge']),
               ('geetest_validate', validate),
               ('geetest_seccode', validate + '|jordan'),
               ('session.token', token),
               ('condition.keyword', keyword)]
    _response = session.post(_url, headers=_headers, data=_params, timeout=TIMEOUT)
    logging.debug('response code: ' + str(_response.status_code))
    #logger.debug('response text: ' + _response.text)
    if _response.status_code != 200:
        return None, None
    return parse_code(_response.text), parse_token(_response.text)


def get_validate(session, keyword):
    '''循环进行validate验证'''
    for _ in range(10):
        if not get_register(session):
            return None

        if not post_verify_ip(session):
            return None

        if not post_verify_keyword(session, keyword):
            return None

        validate = calc_validate(CAPTCHA_JSON['challenge'])
        if post_validate(session, validate):
            return validate
    return None


def query_keyword(session, keyword, token):
    '''使用session, 查询keyword, 更新session.token'''
    if not token:
        token = get_main(session)
        if not token:
            return None

    validate = get_validate(session, keyword)
    if not validate:
        return None

    return post_search(session, validate, keyword, token)


def query(query_db, save_db, queryed_db):
    '''query by leveldb'''
    try:
        with requests.Session() as session:
            _token = ''
            for _name, _code in query_db.RangeIter():
                if not util.has_key(save_db, _name) and not util.has_key(queryed_db, _name):
                    # 模糊查询
                    _subname = _name[0: 18] if len(_name) > 18 else _name
                    logging.info(_name + ' -> ' + _subname)
                    _query_code, _token = query_keyword(session, _subname, _token)
                    if _query_code:
                        for _r in _query_code:
                            logging.info(_r[0] + ' : ' + _r[1])
                            save_db.Put(_r[0], _r[1], sync=True)
                    queryed_db.Put(_name, '', sync=True)
        return True
    except requests.RequestException as _e:
        logging.error(_e)
        return False


if __name__ == "__main__":
    logging.info('call query()')
