[国家企业信用信息公示系统](http://www.gsxt.gov.cn)使用GeeTest滑块验证码。主站使用online验证模式，难破解。部分分站使用offline验证模式，易破解但多次HTTP请求应答往复，查询效率低。  
[国家工商总局](http://www.saic.gov.cn/)提供了Android，iOS App，这次就来尝试分析一下App的情况。  

总局网站有2套：

+ 新版 http://www.saic.gov.cn/
+ 旧版 http://old.saic.gov.cn/

于是App下载说明页面也有2套：

+ 新版 http://gzhd.saic.gov.cn/gszj/index/telephone/android2.html
+ 旧版 http://gzhd.saic.gov.cn/gszj/index/telephone/android.html

还好App只有1套。

国家工商行政管理总局移动版客户端：

+ Android版 http://gzhd.saic.gov.cn/gszj/saicwap.apk  
+ iOS版 https://itunes.apple.com/cn/app/gong-shang-zong-ju/id725956822?mt=8  

国家企业信用信息公示系统：

+ Android版 http://gzhd.saic.gov.cn/gszj/gongshi.apk  
+ iOS版 https://itunes.apple.com/cn/app/%E5%9B%BD%E5%AE%B6%E4%BC%81%E4%B8%9A%E4%BF%A1%E7%94%A8%E4%BF%A1%E6%81%AF%E5%85%AC%E7%A4%BA%E7%B3%BB%E7%BB%9F/id1048375712?mt=8  
  
### 分析

**saicwap.apk，看这个名称，好像已经明白了什么。**  
安装&运行&解包查看`国家企业信用信息公示系统Android APK`文件。  
UI交互体验基本上就是一个网页。  
dex很小，assets文件很多。  
根据名称搜索加猜测，直接得出结论，WebView外壳，JQuery+AJAX实现网页。  
使用Fiddler抓包，仅有一条简单的HTTP Request & Response。  
Response是标准JSON文本。  

随手写个实现

### 填写Android Mobile HTTP Header参数

```Python
URL = 'http://yd.gsxt.gov.cn/QuerySummary'
MOBILE_ACTION = 'entSearch'
TOPIC = 1
PAGE_NUM = 1
PAGE_SIZE = 10
USER_ID = 'id001'
USER_IP = '192.168.0.1'
USER_AGENT = 'Mozilla/5.0 (Linux; Android 4.4.2; vivo Y28L Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36 Html5Plus/1.0'
ACCEPT_LANGUAGE = 'zh-CN,en-US;q=0.8'
XRW = 'com.zongjucredit'
ORIGIN = 'file://'
CHARSET = 'application/x-www-form-urlencoded; charset=UTF-8'
```

### 使用requests库

```Python
def query(keyword):
    _data = [('mobileAction', MOBILE_ACTION),
             ('keywords', keyword),
             ('topic', TOPIC),
             ('pageNum', PAGE_NUM),
             ('pageSize', PAGE_SIZE),
             ('userID', USER_ID),
             ('userIP', USER_IP)]
    _headers = {'User-Agent': USER_AGENT,
                'Accept-Language': ACCEPT_LANGUAGE,
                'X-Requested-With': XRW,
                'Origin': ORIGIN,
                'Content-Type': CHARSET}

    _response = requests.post(URL, data=_data, headers=_headers)
    print(_response.status_code)
    if _response.status_code == 200:
        _content = _response.json()
        print(json.dumps(_content, indent=2, sort_keys=True, ensure_ascii=False))
```

### 测试运行

搜索关键字`腾讯科技`，得到[50条数据](https://github.com/9468305/python-script/blob/master/gsxt_mobile/%E8%85%BE%E8%AE%AF%E7%A7%91%E6%8A%8050.txt)。格式示例：  

```JSON
{
"BUSEXCEPTCOUNT": "0",
"CAT18": "10",
"CAT2NAME": "法定代表人",
"ENTNAME": "<font color=red>腾讯科技</font>(成都)有限公司",
"ENTTYPE": "6150",
"ESTDATE": "2008年07月10日",
"NAME": "奚丹",
"PRIPID": "BFA63C5493A3045829033A5B114CE66AFD1B796865F63020C39130E7149AE9152BAC6972D71F0C3A65B342A32972C4439717E803CD7E66773D486FDD9FCBAEC8",
"REGNO": "510100400024413",
"REGSTATE_CN": "存续（在营、开业、在册）",
"S_EXT_NODENUM": "510000",
"UNISCID": "915101006771521538"
}
```

**实测，有时会封IP，24小时解禁，一旦封禁，爬虫和官方App一概屏蔽。**  
