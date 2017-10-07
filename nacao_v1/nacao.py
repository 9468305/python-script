#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
全国组织机构代码管理中心
http://www.nacao.org.cn/
全国统一社会信用代码信息校核结果公示系统
http://125.35.63.141:8080/PublicNotificationWeb/search.do
'''
import os
import logging
import requests
import constants

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        '''NullHandler'''
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
logging.basicConfig(level=logging.DEBUG)

HOST = 'http://125.35.63.141:8080'

# 该网站有时响应很慢，需要随时调整超时时间阈值
TIMEOUT = 20


def get_search(session, keyword):
    '''查询keyword'''
    _url = HOST + '/PublicNotificationWeb/search.do'
    logging.debug('GET ' + _url)
    _headers = {'Accept': constants.ACCEPT_HTML,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT}
    _params = [('searchText', keyword),
               ('searchType', 3)]
    _response = session.get(_url, headers=_headers, params=_params, timeout=TIMEOUT)
    logging.debug('response code:' + str(_response.status_code))
    return _response.url if _response.status_code == 200 else None


def post_query(session, keyword, referer, current_page):
    '''分页获取keyword json数据'''
    _url = HOST + '/PublicNotificationWeb/query.do'
    logging.debug('POST ' + _url)
    _headers = {'Accept': constants.ACCEPT_ANY,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': referer,
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
    '''使用session,查询keyword'''
    _referer = get_search(session, keyword)
    if not _referer:
        return None

    _code_all = []
    _current_page = 0
    _total_page = 5
    while _current_page < _total_page:
        _current_page += 1
        _json_obj = post_query(session, keyword, _referer, _current_page)
        if _json_obj:
            _total_page = _json_obj['totalPage']
            _found_count = _json_obj['foundCount']
            _data_list = _json_obj['dataList']
            if _found_count  and _data_list:
                for _i in _data_list:
                    _code_all.append((_i['JGMC'].encode('utf-8'), _i['TYSHXYDM'].encode('utf-8')))
        else:
            break

    return _code_all


def has_key(database, key):
    '''安全地检查leveldb是否存在key'''
    try:
        database.Get(key)
        return True
    except KeyError:
        return False


def query_leveldb(query_db, save_db, queryed_db):
    '''query by leveldb database'''
    try:
        with requests.Session() as session:
            for _name, _code in query_db.RangeIter():
                if not has_key(save_db, _name) and not has_key(queryed_db, _name):
                    # 模糊查询 取前6个中文字符(不精确)
                    _subname = _name[0: 18] if len(_name) > 18 else _name
                    logging.info(_name)
                    logging.info(_subname)
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


def query_once():
    '''query once'''
    try:
        with requests.Session() as session:
            # * 就是通配符, 可替换成任意公司名称, 该接口可能存在SQL注入漏洞, 未深入验证.
            _code_all = query_keyword(session, '*')
            if _code_all:
                logging.info(len(_code_all))
                for _r in _code_all:
                    logging.info(_r[0] + ' : ' + _r[1])
    except requests.RequestException as _e:
        logging.error(_e)


def query_batch():
    '''query batch by leveldb'''
    import leveldb
    query_db_file = os.path.join(os.getcwd(), 'data', 'query.db')
    query_db = leveldb.LevelDB(query_db_file)

    save_db_file = os.path.join(os.getcwd(), 'data', 'save.db')
    save_db = leveldb.LevelDB(save_db_file)

    queryed_db_file = os.path.join(os.getcwd(), 'data', 'queryed.db')
    queryed_db = leveldb.LevelDB(queryed_db_file)

    _loop = True
    while _loop:
        _loop = not query_leveldb(query_db, save_db, queryed_db)


if __name__ == "__main__":
    #query_batch()
    query_once()
