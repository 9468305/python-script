#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''
geetest常用公共方法
'''

SPLIT_ARRAY_JS = '''
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
        var g = Math.round(a) + c; b = b.slice(0, 32);
        var h, i = [ [], [], [], [], [] ], j = {}, k = 0; e = 0;
        for (var l = b.length; e < l; e++)
            h = b.charAt(e), j[h] || (j[h] = 1, i[k].push(h), k++, k = 5 == k ? 0 : k);
        for (var m, n = g, o = 4, p = "", q = [1, 2, 5, 10, 50]; n > 0;)
            n - q[o] >= 0 ? (m = parseInt(Math.random() * i[o].length, 10), p += i[o][m], n -= q[o]) : (i.splice(o, 1), q.splice(o, 1), o -= 1);
        return p
    }
'''

OFFLINE_SAMPLE = ((186, 1, 98),
                  (82, 0, 136),
                  (61, 5, 108),
                  (128, 2, 7),
                  (130, 4, 99),
                  (189, 3, 65),
                  (108, 5, 285),
                  (136, 0, 36),
                  (41, 0, 263),
                  (124, 3, 185))


TRACE_JS = '''
var tracer = function () {
    c = function (traceArray) {
        for (var b, c, d, e = [], f = 0, g = [], h = 0, i = traceArray.length - 1; h < i; h++) {
            b = Math.round(traceArray[h + 1][0] - traceArray[h][0]),
            c = Math.round(traceArray[h + 1][1] - traceArray[h][1]),
            d = Math.round(traceArray[h + 1][2] - traceArray[h][2]),
            g.push([b, c, d]), 0 == b && 0 == c && 0 == d || (0 == b && 0 == c ? f += d : (e.push([b, c, d + f]), f = 0));
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

def has_key(database, key):
    '''安全的检查leveldb是否存在key'''
    try:
        database.Get(key)
        return True
    except KeyError:
        return False
