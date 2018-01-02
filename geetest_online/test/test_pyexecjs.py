#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''Unit Test for PyExecJS.'''
import execjs

JSRUNTIME = execjs.get(execjs.runtime_names.Node)

TOKEN_JS = '''
function check_browser(data){
    location_info = data.value ^ 536870911
}
location_info = 4995595067;
'''


def test_context():
    '''Test JSRuntime Context functions.'''
    _context = JSRUNTIME.compile(TOKEN_JS)
    print(_context.eval('location_info'))
    print(_context.call('check_browser', '{ value: 499382950}'))
    print(_context.eval('location_info'))


if __name__ == "__main__":
    test_context()
