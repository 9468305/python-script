#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
国家企业信用信息公示系统(内蒙古)
http://nm.gsxt.gov.cn/
'''
import os
import traceback
import requests
import geetest_offline_nm

GSXT_HOST = 'http://nm.gsxt.gov.cn'
GSXT_INDEX = GSXT_HOST + '/'

def query_keyword(keyword):
    '''根据keyword查询一次'''
    geetest_offline_nm.config(GSXT_HOST, GSXT_INDEX)
    try:
        with requests.Session() as session:
            print keyword
            _query_code = geetest_offline_nm.query_keyword(session, keyword)
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
    geetest_offline_nm.config(GSXT_HOST, GSXT_INDEX)

    query_db_file = os.path.join(os.getcwd(), 'data', 'neimenggu.db')
    query_db = leveldb.LevelDB(query_db_file)

    save_db_file = os.path.join(os.getcwd(), 'data', 'neimenggu_code.db')
    save_db = leveldb.LevelDB(save_db_file)

    queryed_db_file = os.path.join(os.getcwd(), 'data', 'neimenggu_queryed.db')
    queryed_db = leveldb.LevelDB(queryed_db_file)

    _loop = True
    while _loop:
        _loop = not geetest_offline_nm.query(query_db, save_db, queryed_db)


if __name__ == "__main__":
    #query()
    query_keyword('百度')
