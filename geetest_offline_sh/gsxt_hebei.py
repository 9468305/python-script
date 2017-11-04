#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
国家企业信用信息公示系统(河北)
http://he.gsxt.gov.cn/notice/
'''
import os
import traceback
import requests
import geetest_offline

GSXT_HOST = 'http://he.gsxt.gov.cn'
GSXT_INDEX = GSXT_HOST + '/notice/'

def query_keyword(keyword):
    '''根据keyword查询一次'''
    geetest_offline.config(GSXT_HOST, GSXT_INDEX)
    try:
        with requests.Session() as session:
            _token = ''
            print keyword
            _query_code, _token = geetest_offline.query_keyword(session, keyword, _token)
            if _query_code:
                for _r in _query_code:
                    print _r[0] + ':' + _r[1]
        return True
    except requests.RequestException as _e:
        traceback.print_exc()
        return False


def query():
    '''查询该省db中所有数据'''
    import leveldb
    geetest_offline.config(GSXT_HOST, GSXT_INDEX)

    query_db_file = os.path.join(os.getcwd(), 'data', 'hebei.db')
    query_db = leveldb.LevelDB(query_db_file)

    save_db_file = os.path.join(os.getcwd(), 'data', 'hebei_code.db')
    save_db = leveldb.LevelDB(save_db_file)

    queryed_db_file = os.path.join(os.getcwd(), 'data', 'hebei_queryed.db')
    queryed_db = leveldb.LevelDB(queryed_db_file)

    _loop = True
    while _loop:
        _loop = not geetest_offline.query(query_db, save_db, queryed_db)


if __name__ == "__main__":
    #query()
    query_keyword('百度')
