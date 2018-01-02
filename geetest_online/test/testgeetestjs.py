#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''Unit Test for geetest.js'''
import os
import random
import codecs
import json
import execjs
from PIL import Image
from bs4 import BeautifulSoup

JSRUNTIME = execjs.get(execjs.runtime_names.Node)

G_SPLIT_ARRAY_JS = '''
    function getSplitArray() {
        for (var a, b = "6_11_7_10_4_12_3_1_0_5_2_9_8".split("_"), c = [], d = 0, e = 52; d < e; d++)
            a = 2 * parseInt(b[parseInt(d % 26 / 2)]) + d % 2,
            parseInt(d / 2) % 2 || (a += d % 2 ? -1 : 1),
            a += d < 26 ? 26 : 0,
            c.push(a);
        return c
    }
'''

USERRESPONSE_JS = '''
    function userresponse(a, b) {
        for (var c = b.slice(32), d = [], e = 0; e < c.length; e++) {
            var f = c.charCodeAt(e);
            d[e] = f > 57 ? f - 87 : f - 48
        }
        c = 36 * d[0] + d[1];
        var g = Math.round(a) + c;
        b = b.slice(0, 32);
        var h, i = [
                [],
                [],
                [],
                [],
                []
            ],
            j = {},
            k = 0;
        e = 0;
        for (var l = b.length; e < l; e++) h = b.charAt(e), j[h] || (j[h] = 1, i[k].push(h), k++, k = 5 == k ? 0 : k);
        for (var m, n = g, o = 4, p = "", q = [1, 2, 5, 10, 50]; n > 0;) n - q[o] >= 0 ? (m = parseInt(Math.random() * i[o].length, 10), p += i[o][m], n -= q[o]) : (i.splice(o, 1), q.splice(o, 1), o -= 1);
        return p
    }
'''

USERRESPONSE_JSCONTEXT = JSRUNTIME.compile(USERRESPONSE_JS)

TRACE_JS = '''
var tracer = function () {
    c = function (traceArray) {
        for (var b, c, d, e = [], f = 0, g = [], h = 0, i = traceArray.length - 1; h < i; h++) {
            b = Math.round(traceArray[h + 1][0] - traceArray[h][0]), c = Math.round(traceArray[h + 1][1] - traceArray[h][1]), d = Math.round(traceArray[h + 1][2] - traceArray[h][2]), g.push([b, c, d]), 0 == b && 0 == c && 0 == d || (0 == b && 0 == c ? f += d : (e.push([b, c, d + f]), f = 0));
        }
        return 0 !== f && e.push([b, c, f]), e
    },
    d = function (a) {
        var b = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr",
        c = b.length,
        d = "",
        e = Math.abs(a),
        f = parseInt(e / c);
        f >= c && (f = c - 1), f && (d = b.charAt(f)), e %= c;
        var g = "";
        return a < 0 && (g += "!"), d && (g += "$"), g + d + b.charAt(e)
    },
    e = function (a) {
        for (var b = [
             [1, 0],
             [2, 0],
             [1, -1],
             [1, 1],
             [0, 1],
             [0, -1],
             [3, 0],
             [2, -1],
             [2, 1]
        ], c = "stuvwxyz~", d = 0, e = b.length; d < e; d++)
        if (a[0] == b[d][0] && a[1] == b[d][1]) return c[d];
            return 0
    },
    f = function (traceArray) {
        for (var b, f = c(traceArray), g = [], h = [], i = [], j = 0, k = f.length; j < k; j++) {
            b = e(f[j]), b ? h.push(b) : (g.push(d(f[j][0])), h.push(d(f[j][1]))), i.push(d(f[j][2]));
        }
        return g.join("") + "!!" + h.join("") + "!!" + i.join("")
    },
    g = function (traceArray) {
        var a = f(traceArray);
        return encodeURIComponent(a)
    };
    return {
        trace: g
    }
}();
exports.tracer = tracer;
'''

TRACE_JS_CONTEXT = JSRUNTIME.compile(TRACE_JS)


def load_filetext(filename):
    '''load text from file as utf-8 codecs'''
    text = ''
    with codecs.open(filename, 'r', 'utf-8') as _f:
        text = _f.read()
    return text


def test_load_geetest_js():
    '''load javascript text from file, compile, return context object'''
    jsfile = os.path.join(os.getcwd(), 'gsxt', 'geetest.5.10.10.js')
    print(jsfile)
    js_context = JSRUNTIME.compile(load_filetext(jsfile))
    print(js_context)


def test_get_splite_array():
    '''load split array data from call javascript'''
    context = JSRUNTIME.compile(G_SPLIT_ARRAY_JS)
    splite_array = context.call('getSplitArray')
    print('split array = ' + str(splite_array))
    return splite_array


def test_offset_position(height, split_array):
    '''parse offset position array from split array'''
    offset_array = []
    for i in split_array:
        _x = i % 26 * 12 + 1
        _y = height / 2 if i > 25 else 0
        offset_array.append([_x, _y])
    print('offset array = ' + str(offset_array))
    return offset_array


def test_rewrite_image(image_name, offset_array):
    '''load image from file, recombined to new image by offset array'''
    img = Image.open(os.path.join(os.getcwd(), 'temp', image_name))
    print(img.format, img.size, img.mode)

    rows, columns, offsetwidth, offsetheight = 2, 26, 10, 58
    img_new = Image.new('RGB', (columns*offsetwidth, rows*offsetheight))
    for row in range(rows):
        for column in range(columns):
            from_x, from_y = offset_array[row * columns + column]
            box = (from_x, from_y, from_x + offsetwidth, from_y + offsetheight)
            to_x, to_y = column*offsetwidth, row*offsetheight
            box_new = (to_x, to_y, to_x + offsetwidth, to_y + offsetheight)
            img_new.paste(img.crop(box), box_new)

    img_new.save(os.path.join(os.getcwd(), 'temp', image_name + '.jpg'), format='JPEG')
    print(img_new.format, img_new.size, img_new.mode)
    img.close()
    img_new.close()


def comparepixel(src, dst, threshold):
    '''compare two pixel value by threshold.'''
    return abs(src[0] - dst[0]) < threshold \
        and abs(src[1] - dst[1]) < threshold \
        and abs(src[2] - dst[2]) < threshold


def get_diff_xy(img1, img2, start_x, start_y, threshold):
    '''Calculate the difference between image1 and image2.'''
    width, height = img1.size
    img_diff = img2.copy()
    pixel_diff = []
    for _x in range(start_x, width):
        for _y in range(start_y, height):
            pixel1, pixel2 = img1.getpixel((_x, _y)), img2.getpixel((_x, _y))
            if not comparepixel(pixel1, pixel2, threshold):
                pixel_diff.append((_x, _y))

    min_xy, max_xy = min(pixel_diff), max(pixel_diff)
    for _y in range(height):
        img_diff.putpixel((min_xy[0], _y), (0, 0, 0))
        img_diff.putpixel((max_xy[0], _y), (0, 0, 0))

    name = 'diff_' + str(threshold) + '_' + str(min_xy[0]) + '_' + str(max_xy[0]) + '.jpg'
    img_diff.save(os.path.join(os.getcwd(), 'temp', name), format='JPEG')
    img_diff.close()
    print(threshold, min_xy[0], max_xy[0])
    return min_xy[0], max_xy[0]


def get_best_diff(img1, img2, start_x, start_y):
    '''Calculate the best different positon.'''
    _x, _y = 0, 0
    for threshold in range(5, 71, 5):
        _x, _y = get_diff_xy(img1, img2, start_x, start_y, threshold)
    return _x, _y


def test_diff_image(image1, image2, start_x, start_y):
    '''find different between two images'''
    image_path_src = os.path.join(os.getcwd(), 'temp', image1)
    image_path_dst = os.path.join(os.getcwd(), 'temp', image2)
    img1, img2 = Image.open(image_path_src), Image.open(image_path_dst)
    if img1.size != img2.size:
        print('2 images size is different')
        img1.close()
        img2.close()
        return
    _x, _y = get_best_diff(img1, img2, start_x, start_y)
    img1.close()
    img2.close()
    return _x, _y


def userresponse(distance, challenge):
    '''根据滑动距离distance和challenge，计算userresponse值'''
    return USERRESPONSE_JSCONTEXT.call('userresponse', distance, challenge)


def imgload():
    '''图片加载时间(毫秒)，用于统计，无验证功能。'''
    return random.randint(100, 200)


def adjust_distance(distance):
    '''滑块slice图片的尺寸：59*50，上下左右四周可能间隔6像素，因此实际尺寸：47*38。'''
    return distance - 6


def parsetrace(trace_file):
    '''parse trace distance'''
    with open(os.path.join(os.getcwd(), 'test', trace_file)) as tracedata:
        trace = json.load(tracedata)
    print('trace analyse:')
    for index in range(2, len(trace)):
        print(trace[index][0] - trace[index-1][0], trace[index][2] - trace[index-1][2])


def usertrace(distance):
    '''
    采集用户鼠标拖动轨迹，构造数组(x坐标, y坐标, 时间间隔毫秒)，加密。
    geetest.5.10.10.js的变量: Q.t("arr", a)
    输出加密前的明文数组: console.log(JSON.stringify(Q.t("arr", a)))
    轨迹样本见TraceSample.txt
    轨迹样本分析见TraceSampleParse.txt
    '''
    # 轨迹间隔数组
    trace = []
    # 根据距离distance，计算总共步数，范围采样50%-75%
    total_steps = int(distance * random.uniform(0.5, 0.75))
    # 滑动阶段1：慢速起步，按下鼠标时间间隔较长
    move_instance = random.randint(1, 4)
    trace.append((move_instance, 0, random.randint(200, 500)))
    # 滑动阶段2：中速运行，鼠标拖动速度中等
    for _i in range(total_steps):
        if move_instance < distance:
            step = random.randint(1, 3)
            move_instance = move_instance + step
            trace.append((step, 0, random.randint(8, 24)))
    # 滑动阶段3：慢速到达，鼠标接近目标位置时减速
    trace.append(((distance - move_instance), 0, random.randint(100, 800)))
    trace.append((0, 0, random.randint(100, 500)))
    print(trace)

    # 轨迹间隔数组转成轨迹坐标数组
    position = []
    # 鼠标点击坐标相对于滑块图片边缘的值
    position.append((-random.randint(14, 30), -random.randint(14, 30), 0))
    # 起始值
    current_position = (0, 0, 0)
    position.append(current_position)
    for _i in trace:
        next_positon = (current_position[0] + _i[0], _i[1], current_position[2] + _i[2])
        position.append(next_positon)
        current_position = next_positon

    passtime = position[-1][2]
    print(position)
    print(passtime)
    return position, passtime


def encrypttrace(trace):
    '''encrypt trace data by JSCall'''
    return TRACE_JS_CONTEXT.call('tracer.trace', trace)


def fun_c(param):
    '''reversed from geetest.js'''
    _b = 0
    _c = 0
    _d = 0
    _e = []
    _f = 0
    _g = []
    _h = 0
    for _h in range(0, len(param)-1):
        _b = round(param[_h + 1][0] - param[_h][0])
        _c = round(param[_h + 1][1] - param[_h][1])
        _d = round(param[_h + 1][2] - param[_h][2])
        _g.append([_b, _c, _d])
        if _b == 0 and _c == 0 and _d == 0:
            continue
        else:
            if _b == 0 and _c == 0:
                _f = _f + _d
            else:
                _e.append([_b, _c, _d + _f])
                _f = 0
    if _f != 0:
        _e.append([_b, _c, _f])
    return _e


def fun_d(param):
    '''reversed from geetest.js'''
    _b = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr"
    _c = len(_b)
    _d = ""
    _e = abs(param)
    _f = int(_e / _c)
    if _f >= _c:
        _f = _c - 1
    if _f:
        _d = chr(_f)
    _e = _e % _c
    _g = ''
    if param < 0:
        _g = _g + '!'
    if _d:
        _g = _g + '$'
    return _g + _d + _b[int(_e)]


def fun_e(param):
    '''reversed from geetest.js'''
    _b = [[1, 0], [2, 0], [1, -1], [1, 1], [0, 1], [0, -1], [3, 0], [2, -1], [2, 1]]
    _c = "stuvwxyz~"
    _d = 0
    _e = len(_b)
    for _d in range(0, len(_b)):
        if param[0] == _b[_d][0] and param[1] == _b[_d][1]:
            return _c[_d]
    return 0


def fun_f(param):
    '''reversed from geetest.js'''
    _b = None
    _f = fun_c(param)
    _g = []
    _h = []
    _i = []
    for j in _f:
        _b = fun_e(j)
        if _b:
            _h.append(_b)
        else:
            _g.append(fun_d(j[0]))
            _h.append(fun_d(j[1]))
        _i.append(fun_d(j[2]))

    return ''.join(j for j in _g) + '!!' + ''.join(j for j in _h) + '!!' + ''.join(j for j in _i)


def parse_html(html_doc, page):
    '''parse html webpage elements.'''
    soup = BeautifulSoup(html_doc, 'html.parser')
    _result = []
    _findall = soup.find_all('a', class_='search_list_item db')
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


def print_json_type():
    '''Dump json object type.'''
    json_text = '''{
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
        "type": "slide"
        }'''
    json_object = json.loads(json_text)
    for _k, _v in json_object.items():
        print(type(_k))
        print(type(_v))


def test_geetest():
    '''test geetest related functions.'''
    test_load_geetest_js()
    print(userresponse(100, '1196277ad0c2a2142efce133857c5c8bja'))
    print(userresponse(100, "1196277ad0c2a2142efce133857c5c8bja"))
    splites = test_get_splite_array()
    offsets = test_offset_position(116, splites)
    test_rewrite_image('fullbg', offsets)
    test_rewrite_image('bg', offsets)
    _x, _y = test_diff_image('fullbg.jpg', 'bg.jpg', 0, 12)
    print(imgload())
    parsetrace('TraceSample01.txt')
    parsetrace('TraceSample02.txt')
    parsetrace('TraceSample03.txt')
    parsetrace('TraceSample04.txt')
    trace, _passtime = usertrace(100)
    print(encrypttrace(trace))
    print(fun_f(trace))
    trace, _passtime = usertrace(200)
    print(encrypttrace(trace))
    print(fun_f(trace))
    print(parse_html(load_filetext(os.path.join(os.getcwd(), 'test', 'result.html')), 1))
    print(parse_html(load_filetext(os.path.join(os.getcwd(), 'test', 'result2.html')), 2))
    print_json_type()


if __name__ == "__main__":
    test_geetest()
