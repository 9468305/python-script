这次的爬虫换个目标，不仅仅抓取统一社会信用代码（税号），还要抓取企业基础信息。目标网站设定为 http://gd.gsxt.gov.cn 国家企业信用信息公示系统（广东）。

首页依然是采用GeeTest滑块验证码Offline模式验证，校验过程内容省略。以搜索关键字“腾讯科技”为例，第一步获得如下数据。

```python
[
  ('广州腾讯科技有限公司',
   'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_nPNw57QPCnL961TNeXO4Gqc/FgBy7ESTwWPrP4zJe5g=-FBrJ/suNwXMupXtmIUvNKg=='),
  ('深圳兴腾讯科技有限公司',
   'https://www.szcredit.org.cn/GJQYCredit/GSZJGSPTS/QYGS.aspx?rid=6B553DC2860F51DD8179F9821CA72F8094E73CE96BD2D49EC7C4690757FA61D9'),
  ('腾讯科技（深圳）有限公司',
   'https://www.szcredit.org.cn/GJQYCredit/GSZJGSPTS/QYGS.aspx?rid=B0819DEB6219A8B1'),
  ('深圳市联腾讯科技有限公司', 
   'https://www.szcredit.org.cn/GJQYCredit/GSZJGSPTS/QYGS.aspx?rid=DB80B6DEA7F44F35C9A10E5985D4FAA2D4F342323238AB811179ADA6138BD8D4'),
  ('惠州云达腾讯科技有限公司', 
   'http://gd.gsxt.gov.cn/aiccips/CheckEntContext/../GSpublicity/GSpublicityList.html?service=entInfo_SesJBXGCYofnRPu6PUIM/1lSj0vJHOw5gTgVbtsLB1BTAOYLpc4gxgb5a3wjX8k3-dA+Hj5oOjXjQTgAhKSP1lA=='),
  ('深圳市华腾讯科技有限公司', 
   'https://www.szcredit.org.cn/GJQYCredit/GSZJGSPTS/QYGS.aspx?rid=6B553DC2860F51DD8179F9821CA72F80820C9FD043746B01E89676307B6B60EF'),
  ('中山腾讯科技电子有限公司', 
   'http://gd.gsxt.gov.cn/aiccips/CheckEntContext/../GSpublicity/GSpublicityList.html?service=entInfo_ZECp7scr3rINuX8+ial6uIv57yGPPUCA1RAvDHoM0tBrXZJ9+1otoDp51Oi7UabK-7kW54gFL28iQmsO8Qn3cTA=='),
  ('深圳市安腾讯科技电子有限公司', 
   'https://www.szcredit.org.cn/GJQYCredit/GSZJGSPTS/QYGS.aspx?rid=6B553DC2860F51DD8179F9821CA72F808CC6A55FD01EE165A1560ECF17B3E73C'),
  ('中山市纸箱总厂腾讯科技亚太电子厂', 
   'http://gd.gsxt.gov.cn/aiccips/CheckEntContext/../GSpublicity/GSpublicityList.html?service=entInfo_M+Q/CD12sdYKPqPXAzRChoB2xhauTJBsWbk/xaaA92MJ4dcDV+KRZ71QUWHSpwQ+-7kW54gFL28iQmsO8Qn3cTA=='),
  ('深圳龙腾讯威科技有限公司', 
   'https://www.szcredit.org.cn/GJQYCredit/GSZJGSPTS/QYGS.aspx?rid=6B553DC2860F51DD7501B40D8BFA3C22E27771C25B8DF96FD1F35DF7C350F5A9')
]
```

**吐槽：企业详细信息页面分3种。每种网站又有不同的网页模板，因此解析HTML页面元素需要分别处理。深圳的网页模板是一套，广州和其他的是另一套。所以需要区分2种DOM树进行解析。**

+ 深圳 https://www.szcredit.org.cn
+ 广州 http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html
+ 其他 http://gd.gsxt.gov.cn/aiccips/CheckEntContext/../GSpublicity/GSpublicityList.html

使用 BeautifulSoup 解析搜索结果页面后，需要判断URL：  

```Python
 _url = _company['href']
if _url.startswith('../'):
    _url = INDEX + '/aiccips/CheckEntContext/' + _url
```

最终整理得到数据：  

```python
{
  '注册号/统一社会信用代码': '91440101327598294H',
  '注册资本': '0',
  '企业名称': '广州腾讯科技有限公司',
  '类型': '有限责任公司(外商投资企业法人独资)',
  '成立日期': '2014年12月31日',
  '营业期限自': '2014年12月31日',
  '营业期限至': '2018年07月15日',
  '登记机关': '广州市海珠区工商行政管理局',
  '核准日期': '2016年12月23日',
  '登记状态': '存续',
  '经营范围': '电子、通信与自动控制技术研究、开发;网络技术的研究、开发;计算机技术开发、技术服务;软件服务;软件测试服务;软件批发;软件零售;软件开发;游戏软件设计制作;信息技术咨询服务;数据处理和存储服务;(依法须经批准的项目，经相关部门批准后方可开展经营活动)〓'
}
```

**吐槽+1：〓是什么鬼？**

由于这些网站性能极差，默认的15秒超时经常失败，因此在每次网络请求之上添加保护，对于可以多次重试的请求，添加循环等待。

```Python
def safe_query_detail(url):
    '''Safe query url, handle network timeout and retry multi times.'''
    for _ in range(5):
        try:
            with requests.Session() as session:
                return query_detail(session, url)
        except requests.RequestException as _e:
            logging.error(_e)
            time.sleep(5)
    return None
```

**吐槽+2：降低网站性能也是一种非常有效的反爬技术。**

2017.12.05 更新

从 http://gd.gsxt.gov.cn 查询“深圳兴腾讯科技有限公司”，跳转链接失败，服务器500错误。  
> https://www.szcredit.org.cn/GJQYCredit/GSZJGSPTS/QYGS.aspx?rid=6B553DC2860F51DD8179F9821CA72F8094E73CE96BD2D49EC7C4690757FA61D9  

从 https://www.szcredit.org.cn ，查询和跳转正常。  
> https://www.szcredit.org.cn/web/gspt/newGSPTDetail3.aspx?ID=2e82a6a7aaec419884738d2421e7a838  

**吐槽+3：这都是什么运维水平？**
