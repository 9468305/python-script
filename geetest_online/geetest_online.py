#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''
geetest online 5.10.10 spider for www.gsxt.gov.cn
'''

import time
import os
import datetime
import random
import json
from io import BytesIO
from PIL import Image
import requests
import execjs
from bs4 import BeautifulSoup
import constants
import util

GSXT_HOST = 'http://www.gsxt.gov.cn'
GSXT_INDEX = GSXT_HOST + '/index.html'
GEETEST_API_HOST = 'http://api.geetest.com'
GEETEST_STATIC_HOST = 'http://static.geetest.com'

IMAGE_DEBUG = True

TOKEN_JS = None

TOKEN_JS_CONTEXT = None

VALIDATE_TOKEN_JS_CONTEXT = None

CAPTCHA_JSON = None

GETTYPE_JSON = None

CONFIG_JSON = None

JSRUNTIME = execjs.get()

SPLIT_ARRAY_JSCONTEXT = JSRUNTIME.compile(util.SPLIT_ARRAY_JS)

USERRESPONSE_JSCONTEXT = JSRUNTIME.compile(util.USERRESPONSE_JS)

TRACE_JS_CONTEXT = JSRUNTIME.compile(util.TRACE_JS)


def get_image(image_name):
    '''
    Download image file from url to memory.
    Then we can use Image.open(BytesIO(RawContent)) to parse it.
    '''
    _image_data = None
    _image = CONFIG_JSON[image_name].lower()
    if _image.endswith('.jpg'):
        _image = _image.replace('.jpg', '.webp')
    _url = GEETEST_STATIC_HOST + '/' + _image
    print('GET ' + _url)
    _headers = {'Accept': constants.ACCEPT_IMAGE,
                'Referer': GSXT_INDEX,
                'Origin': GSXT_HOST,
                'User-Agent': constants.USER_AGENT}
    _response = requests.get(_url, headers=_headers)
    if _response.status_code == 200:
        if IMAGE_DEBUG:
            _image_path = os.path.join(os.getcwd(), 'temp', image_name)
            with open(_image_path, 'wb') as _f:
                _f.write(bytearray(_response.content))
        _image_data = _response.content
    _response.close()
    return _image_data


def get_split_array():
    '''load split array data from call javascript'''
    return SPLIT_ARRAY_JSCONTEXT.call('getSplitArray')


def get_offset_array(height, split_array):
    '''parse offset position array from split array'''
    _offset_array = []
    for i in split_array:
        _x = i % 26 * 12 + 1
        _y = height / 2 if i > 25 else 0
        _offset_array.append([_x, _y])
    return _offset_array


ROWS, COLUMNS, OFFSET_WIDTH, OFFSET_HEIGHT = 2, 26, 10, 58

def recover_image(image_name, image_data, offset_array):
    '''load image from binary data, recombine to new image by offset array'''
    _img = Image.open(BytesIO(image_data))
    _img_new = Image.new('RGB', (COLUMNS*OFFSET_WIDTH, ROWS*OFFSET_HEIGHT))
    for _row in range(ROWS):
        for _column in range(COLUMNS):
            _from_x, _from_y = offset_array[_row * COLUMNS + _column]
            _box = (_from_x, _from_y, _from_x + OFFSET_WIDTH, _from_y + OFFSET_HEIGHT)
            _to_x, _to_y = _column * OFFSET_WIDTH, _row * OFFSET_HEIGHT
            _box_new = (_to_x, _to_y, _to_x + OFFSET_WIDTH, _to_y + OFFSET_HEIGHT)
            _img_new.paste(_img.crop(_box), _box_new)
    _img.close()
    if IMAGE_DEBUG:
        _img_new.save(os.path.join(os.getcwd(), 'temp', image_name + '.jpg'), format='JPEG')
    return _img_new


def comparepixel(pixel1, pixel2, threshold):
    '''compare two pixel is same or not, calculate by threshold'''
    return abs(pixel1[0] - pixel2[0]) < threshold and\
           abs(pixel1[1] - pixel2[1]) < threshold and\
           abs(pixel1[2] - pixel2[2]) < threshold


def calc_diff_position(img1, img2, startx, starty, threshold):
    '''calculate different between two images, by threshold'''
    if img1.size != img2.size:
        print('two images size are different, can not compare')
        return 0, 0

    diffpixel = []
    for _x in range(startx, img1.size[0]):
        for _y in range(starty, img1.size[1]):
            pixel1, pixel2 = img1.getpixel((_x, _y)), img2.getpixel((_x, _y))
            if not comparepixel(pixel1, pixel2, threshold):
                diffpixel.append((_x, _y))

    minxy, maxxy = min(diffpixel), max(diffpixel)
    if IMAGE_DEBUG:
        imgdiff = img2.copy()
        for _y in range(img1.size[1]):
            imgdiff.putpixel((minxy[0], _y), (0, 0, 0))
            imgdiff.putpixel((maxxy[0], _y), (0, 0, 0))

        diffname = 'diff_' + str(threshold) + '_' + str(minxy[0]) + '_' + str(maxxy[0]) + '.jpg'
        imgdiff.save(os.path.join(os.getcwd(), 'temp', diffname), format='JPEG')
        imgdiff.close()
    print(threshold, minxy[0], maxxy[0])
    return minxy[0], maxxy[0]


def calc_best_diff_position(image1, image2, start_x, start_y):
    '''calculate different between two images, find the best match'''
    return calc_diff_position(image1, image2, start_x, start_y, 50)


def calc_slice_target_position(fullbg_data, bg_data):
    '''recover image and calculate slice target position'''
    _offsets = get_offset_array(CONFIG_JSON['height'], get_split_array())
    _fullbg_img = recover_image('fullbg', fullbg_data, _offsets)
    _bg_img = recover_image('bg', bg_data, _offsets)
    _x, _y = calc_best_diff_position(_fullbg_img, _bg_img, CONFIG_JSON['xpos'], CONFIG_JSON['ypos'])
    _fullbg_img.close()
    _bg_img.close()
    '''
    滑块slice图片的尺寸：59*50，上下左右四周可能间隔6像素，因此实际尺寸：47*38。
    精确偏移 = 6
    偏移 = 0, 极大概率返回 fail
    微调 = 3,4 有一定概率 success
    '''
    _x -= 6
    return (_x, _y)


def calc_userresponse(distance, challenge):
    '''根据滑动距离distance和challenge，计算userresponse值'''
    return USERRESPONSE_JSCONTEXT.call('userresponse', distance, challenge)


def calc_imgload():
    '''图片加载时间(毫秒)，用于统计，无验证功能。'''
    return random.randint(100, 200)


def calc_usertrace(distance):
    '''
    采集用户鼠标拖动轨迹，构造数组(x坐标, y坐标, 时间间隔毫秒)，加密。
    geetest.5.10.10.js文件中轨迹数组变量：
        Q.t("arr", a)
    Chrome DevTools输出加密前的明文数组：
        console.log(JSON.stringify(Q.t("arr", a)))
    轨迹样本：TraceSample.txt
    轨迹样本分析：TraceSampleParse.txt
    '''
    # 轨迹间隔数组
    trace = []
    # 根据距离distance，计算总共步数，范围采样50%-75%
    total_steps = int(distance * random.uniform(0.75, 0.95))
    # 滑动阶段1：慢速起步，按下鼠标时间间隔较长
    move_instance = random.randint(1, 4)
    trace.append([move_instance, 0, random.randint(200, 400)])
    # 滑动阶段2：中速运行，鼠标拖动速度中等
    for _i in range(total_steps):
        if move_instance < distance - random.randint(5, 10):
            step = random.randint(1, 3)
            move_instance = move_instance + step
            trace.append([step, 0, random.randint(8, 24)])
    # 滑动阶段3：慢速到达，鼠标接近目标位置时减速
    trace.append([(distance - move_instance), -1, random.randint(100, 400)])
    trace.append((0, -1, random.randint(100, 400)))
    print(trace)

    # 轨迹间隔数组转成轨迹坐标数组
    position = []
    # 鼠标点击坐标相对于滑块图片边缘的值
    position.append([-random.randint(14, 30), -random.randint(14, 30), 0])
    # 起始值
    current_position = [0, 0, 0]
    position.append(current_position)
    for _i in trace:
        next_positon = [current_position[0] + _i[0], _i[1], current_position[2] + _i[2]]
        position.append(next_positon)
        current_position = next_positon

    print(position)
    return position


def calc_validate(position, challenge):
    '''calculate validate parameters'''
    _userresponse = calc_userresponse(position[0], challenge)
    _imgload = calc_imgload()
    _usertrace = calc_usertrace(position[0])
    _passtime = _usertrace[-1][2]
    return _userresponse, _passtime, _imgload, _usertrace


def encrypttrace(trace):
    '''encrypt user trace, by geetest.x.x.x.js'''
    return TRACE_JS_CONTEXT.call('tracer.trace', trace)


def get_main(session):
    '''get gsxt main webpage'''
    _url = GSXT_INDEX
    print('GET ' + _url)

    _headers = {'Accept': constants.ACCEPT_HTML,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT}

    response = session.get(_url, headers=_headers)
    print('response code:' + str(response.status_code))
    print(response.cookies)
    if response.status_code != 200:
        return False
    return True


def get_corp_query_custom_geetest_image(session):
    '''
    [102,117,110,99,116,105,111,110,32,99,104,101,99,107,95,98,114,111,119,115,
    101,114,40,100,97,116,97,41,123,32,10,32,32,32,32,32,108,111,99,97,
    116,105,111,110,95,105,110,102,111,32,61,32,100,97,116,97,46,118,97,108,
    117,101,32,94,32,53,51,54,56,55,48,57,49,49,10,125,32,10,108,111,
    99,97,116,105,111,110,95,105,110,102,111,32,61,32,53,48,48,49,56,49,
    49,48,48,51,59]
    function check_browser(data){
        location_info = data.value ^ 536870911
    }
    location_info = 5001811003;
    '''
    url = GSXT_HOST + '/corp-query-custom-geetest-image.gif'
    print('GET ' + url)
    _headers = {'Accept': constants.ACCEPT_JSON,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': GSXT_INDEX,
                'X-Requested-With': 'XMLHttpRequest'}
    now = datetime.datetime.now()
    timestamp = now.minute + now.second
    params = {'v': str(timestamp)}
    response = session.get(url, headers=_headers, params=params)
    print('response code: ' + str(response.status_code))
    print('response text: ' + response.text)
    if response.status_code != 200:
        return False
    _jsontext = response.json()
    global TOKEN_JS
    TOKEN_JS = ''.join(chr(i) for i in _jsontext)
    print(TOKEN_JS)
    global TOKEN_JS_CONTEXT
    TOKEN_JS_CONTEXT = JSRUNTIME.compile(TOKEN_JS)
    return True


def get_search_item_captcha(session):
    '''
    {"success":1,
     "gt":"1d2c042096e050f07cb35ff3df5afd92",
     "challenge":"a829158c2e2e17191b607ba42f09495c"}
    '''
    url = GSXT_HOST + '/SearchItemCaptcha'
    print('GET ' + url)
    _headers = {'Accept': constants.ACCEPT_JSON,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': GSXT_INDEX,
                'X-Requested-With': 'XMLHttpRequest'}
    params = {'v': str(int(time.time() * 1000))}
    response = session.get(url, headers=_headers, params=params)
    print('response code: ' + str(response.status_code))
    print('response text: ' + response.text)
    if response.status_code != 200:
        return False
    global CAPTCHA_JSON
    CAPTCHA_JSON = response.json()
    return True


def get_gettype(session):
    '''
    geetest_1497532445018({
        "status": "success",
        "data": {"type": "slide",
                 "path": "/static/js/geetest.5.10.10.js",
                 "static_servers": ["static.geetest.com",
                                    "dn-staticdown.qbox.me"]}})
    '''
    url = GEETEST_API_HOST + '/gettype.php'
    print('GET ' + url)
    _headers = {'Accept': constants.ACCEPT_ANY,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': GSXT_INDEX}
    callback = 'geetest_{}'.format(int(time.time() * 1000))
    params = [('gt', CAPTCHA_JSON['gt']), ('callback', callback)]
    response = session.get(url, headers=_headers, params=params)
    print('response code: ' + str(response.status_code))
    print('response text: ' + response.text)
    if response.status_code != 200:
        return False
    global GETTYPE_JSON
    GETTYPE_JSON = json.loads(response.text[len(callback)+1:-1])
    return True


def get_getphp(session):
    '''
    geetest_1496911691034({
        "xpos": 0,
        "version": "5.10.10",
        "fullpage": false,
        "ypos": 23,
        "api_server": "http://api.geetest.com/",
        "feedback": "",
        "bg": "pictures/gt/969ffa43c/bg/6d29bdf56.jpg",
        "link": "",
        "type": "slide",
        "slice": "pictures/gt/969ffa43c/slice/6d29bdf56.png",
        "https": false,
        "challenge": "a002618817f3a625056461f09188703fjy",
        "product": "popup",
        "logo": false,
        "static_servers": ["static.geetest.com/", "dn-staticdown.qbox.me/"],
        "gt": "1d2c042096e050f07cb35ff3df5afd92",
        "theme_version": "3.2.0",
        "id": "aa002618817f3a625056461f09188703f",
        "benchmark": false,
        "clean": true,
        "mobile": false,
        "theme": "golden",
        "fullbg": "pictures/gt/969ffa43c/969ffa43c.jpg",
        "hide_delay": 800,
        "show_delay": 250,
        "height": 116})
    '''
    url = GEETEST_API_HOST + '/get.php'
    print('GET ' + url)
    _headers = {'Accept': constants.ACCEPT_ANY,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': GSXT_INDEX}
    callback = 'geetest_{}'.format(int(time.time() * 1000))
    params = [('gt', CAPTCHA_JSON['gt']),
              ('challenge', CAPTCHA_JSON['challenge']),
              ('product', 'popup'),
              ('offline', 'false'),
              ('protocol', ''),
              ('path', '/static/js/geetest.5.10.10.js'),
              ('type', 'slide'),
              ('callback', callback)]
    response = session.get(url, headers=_headers, params=params)
    print('response code: ' + str(response.status_code))
    print('response text: ' + response.text)
    if response.status_code != 200:
        return False
    global CONFIG_JSON
    CONFIG_JSON = json.loads(response.text[len(callback)+1:-1])
    return True


def get_corp_query_geetest_validate_input(session):
    '''
    [105,102,40,33,104,97,115,86,97,108,105,100,41,123,98,114,111,119,115,101,
    114,95,118,101,114,115,105,111,110,40,123,32,118,97,108,117,101,58,32,53,
    48,48,49,56,49,48,56,53,125,41,59,104,97,115,86,97,108,105,100,61,
    116,114,117,101,59,125]
    if(!hasValid){browser_version({ value: 500181085});hasValid=true;}
    '''
    url = GSXT_HOST + '/corp-query-geetest-validate-input.html'
    print('GET ' + url)
    _headers = {'Accept': constants.ACCEPT_JSON,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': GSXT_INDEX,
                'X-Requested-With': 'XMLHttpRequest'}
    token = TOKEN_JS_CONTEXT.eval('location_info')
    params = {'token': token}
    response = session.get(url, headers=_headers, params=params)
    print('response code: ' + str(response.status_code))
    print('response text: ' + response.text)
    if response.status_code != 200:
        return False
    _jsontext = response.json()
    _browser_version_js = ''.join(chr(i) for i in _jsontext)
    print(_browser_version_js)
    # 合并4段JavaScript代码，生成一段完整的计算validate token的代码
    _validate_token_js = TOKEN_JS + \
        'browser_version=check_browser,hasValid=false;' + \
        _browser_version_js + \
        'location_info'

    global VALIDATE_TOKEN_JS_CONTEXT
    VALIDATE_TOKEN_JS_CONTEXT = JSRUNTIME.compile(_validate_token_js)
    print(VALIDATE_TOKEN_JS_CONTEXT.eval('location_info'))
    return True


def get_corp_query_search_test(session, searchword):
    '''response: true'''
    url = GSXT_HOST + '/corp-query-search-test.html'
    print('GET ' + url)
    _headers = {'Accept': constants.ACCEPT_JSON,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': GSXT_INDEX,
                'X-Requested-With': 'XMLHttpRequest'}
    params = {'searchword': searchword}
    response = session.get(url, headers=_headers, params=params)
    print('response code: ' + str(response.status_code))
    print('response text: ' + response.text)
    if response.status_code != 200:
        return False
    if not response.json():
        return False

    return True


def get_ajax(session, userresponse, passtime, imgload, usertrace):
    '''
    geetest_1497417450734({
        "score": "5",
        "message": "success",
        "validate": "6b07ff675b6dcc2d43f960b1a4a093a4",
        "success": 1})

    geetest_1497422319552({
        "success": 0,
        "message": "forbidden"})

    geetest_1497423471897({
        "success": 0,
        "message": "fail"})
    '''
    url = GEETEST_API_HOST + '/ajax.php'
    print('GET ' + url)
    _headers = {'Accept': constants.ACCEPT_ANY,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': GSXT_INDEX}
    callback = 'geetest_{}'.format(int(time.time() * 1000))
    params = [('gt', CONFIG_JSON['gt']),
              ('challenge', CONFIG_JSON['challenge']),
              ('userresponse', userresponse),
              ('passtime', passtime),
              ('imgload', imgload),
              ('a', encrypttrace(usertrace)),
              ('callback', callback)]
    params_str = "&".join("%s=%s" % (k, v) for k, v in params)
    response = session.get(url, headers=_headers, params=params_str)
    print('response code: ' + str(response.status_code))
    print('response text: ' + response.text)
    if response.status_code != 200:
        return None
    _ajax_json = json.loads(response.text[len(callback)+1:-1])
    return _ajax_json


def get_refresh(session):
    '''
    geetest_1497431212291({
        "bg": "pictures/gt/fc064fc73/bg/e1777734e.jpg",
        "link": "",
        "challenge": "0a80f1e4b0ff6381e26425b7fa3e71f4c2",
        "ypos": 24,
        "fullbg": "pictures/gt/fc064fc73/fc064fc73.jpg",
        "id": "",
        "xpos": 0,
        "feedback": "",
        "height": 116,
        "slice": "pictures/gt/fc064fc73/slice/e1777734e.png",
        "type": "slide"})

    geetest_1497530854449({
        "error": "refresh too much",
        "status": "error",
        "error_code": "error_00"})
    '''
    _url = GEETEST_API_HOST + '/refresh.php'
    print('GET ' + _url)
    _headers = {'Accept': constants.ACCEPT_ANY,
                'Accept-Language': constants.ACCEPT_LANGUAGE,
                'User-Agent': constants.USER_AGENT,
                'Referer': GSXT_INDEX}
    _callback = 'geetest_{}'.format(int(time.time() * 1000))
    _params = [('gt', CONFIG_JSON['gt']),
               ('challenge', CONFIG_JSON['challenge']),
               ('callback', _callback)]
    _response = session.get(_url, headers=_headers, params=_params)
    print('response code: ' + str(_response.status_code))
    print('response text: ' + _response.text)
    if _response.status_code != 200:
        return False
    _ajax_json = json.loads(_response.text[len(_callback)+1:-1])
    if _ajax_json.has_key('error'):
        return False
    for _k, _v in _ajax_json.items():
        CONFIG_JSON[_k] = _v
    return True


def get_validate(session, search_name):
    '''get geetest validate result by serial call'''
    if not get_corp_query_custom_geetest_image(session):
        return None

    if not get_search_item_captcha(session):
        return None

    if not get_gettype(session):
        return None

    if not get_getphp(session):
        return None

    if not get_corp_query_geetest_validate_input(session):
        return None

    if not get_corp_query_search_test(session, search_name):
        return None

    for _ in range(3):
        fullbg_data = get_image('fullbg')
        if not fullbg_data:
            return None

        bg_data = get_image('bg')
        if not bg_data:
            return None

        slice_data = get_image('slice')
        if not slice_data:
            return None

        _position = calc_slice_target_position(fullbg_data, bg_data)
        _userresponse, _passtime, _imgload, _usertrace = calc_validate(_position, CONFIG_JSON['challenge'])

        _ajax_json = get_ajax(session, _userresponse, _passtime, _imgload, _usertrace)
        if _ajax_json:
            _success = _ajax_json['success']
            #_message = _ajax_json['message']
            if _success == 1: # _message = 'success'
                return _ajax_json
            else:
                # 验证码失败 forbidden 时，等待3秒刷新
                # 验证码失败 fail 时，暂不处理，直接刷新。（因为我的滑块位置算法非常精确）
                time.sleep(3)
                if not get_refresh(session):
                    return None
    return None


def parse_html(html_doc, page):
    '''使用BeautifulSoup解析HTML页面, 查找统一社会信用代码,检查下一页.'''
    soup = BeautifulSoup(html_doc, 'html.parser')
    _result = []
    _findall = soup.find_all('a', class_='search_list_item db')
    if not _findall:
        return None, False
    for _a in _findall:
        _name = _a.find('h1', class_='f20')
        _name_str = ''.join(_name.get_text().split())
        _code = _a.find('div', class_='div-map2')
        _number = _code.find('span', class_='g3')
        _number_str = ''.join(_number.get_text().split())
        _result.append([_name_str, _number_str])
    print(json.dumps(_result, indent=2, sort_keys=True, ensure_ascii=False))
    _findall = soup.find_all('a', href='javascript:turnOverPage({})'.format(page + 1))
    return _result, True if _findall else False


def fetch_corp_query_search(session, search_name, validate_json):
    '''
    POST http://www.gsxt.gov.cn/corp-query-search-1.html
    GET http://www.gsxt.gov.cn/corp-query-search-2.html
    GET http://www.gsxt.gov.cn/corp-query-search-3.html
    GET http://www.gsxt.gov.cn/corp-query-search-4.html
    GET http://www.gsxt.gov.cn/corp-query-search-5.html
    '''
    _url_template = GSXT_HOST + '/corp-query-search-{}.html'
    _page = 1
    while True:
        _url = _url_template.format(_page)
        print('Fetch ' + _url)
        _headers = {'Accept': constants.ACCEPT_HTML,
                    'Accept-Language': constants.ACCEPT_LANGUAGE,
                    'User-Agent': constants.USER_AGENT}
        if _page == 1:
            _headers['Origin'] = GSXT_HOST
            _headers['Referer'] = GSXT_INDEX
        else:
            _headers['Referer'] = _url_template.format(_page - 1)

        _params = [('tab', 'ent_tab'),
                   ('token', VALIDATE_TOKEN_JS_CONTEXT.eval('location_info')),
                   ('searchword', search_name),
                   ('geetest_challenge', CONFIG_JSON['challenge']),
                   ('geetest_validate', validate_json['validate']),
                   ('geetest_seccode', validate_json['validate'] + '|jordan')]
        if _page > 1:
            _params.append(('page', _page))

        if _page == 1:
            response = session.post(_url, headers=_headers, data=_params)
        else:
            response = session.get(_url, headers=_headers, params=_params)

        print('response code: ' + str(response.status_code))
        print('response text: ' + response.text)
        if response.status_code != 200:
            return False
        _code, _more = parse_html(response.text, _page)
        if _more:
            _page += 1
        else:
            break

    return True


def query(queryname):
    '''Query by company name'''
    with requests.Session() as session:
        if not get_main(session):
            return False

        validate_json = get_validate(session, queryname)
        if not validate_json:
            return False

        if not fetch_corp_query_search(session, queryname, validate_json):
            return False

    return True


def set_image_debug(image_debug):
    '''设置是否dump验证码图片到本地缓存文件，以供分析'''
    global IMAGE_DEBUG
    IMAGE_DEBUG = image_debug
    if IMAGE_DEBUG:
        _path = os.path.join(os.getcwd(), 'temp')
        try:
            os.makedirs(_path)
        except OSError:
            if not os.path.isdir(_path):
                raise


if __name__ == "__main__":
    print('main begin')
    set_image_debug(True)
    query('腾讯科技')
    print('main end')
